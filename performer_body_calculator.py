import re, sys, json

try:
    import stashapi.log as log
    from stashapi.stashapp import StashInterface
except ModuleNotFoundError:
    print("You need to install stashapp-tools. (https://pypi.org/project/stashapp-tools/)", file=sys.stderr)
    print("If you have pip (normally installed with python), run this command in a terminal (cmd): 'pip install stashapp-tools'", file=sys.stderr)
    sys.exit()

import body_tags
from body_tags import BodyShape, BodyType, BreastSize, ButtSize

TAG_CLASSES = [BodyShape, BodyType, BreastSize, ButtSize]
CM_TO_INCH = 2.54

def main(stash_in=None, mode_in=None):
    global stash

    if stash_in:
        stash = stash_in
        mode = mode_in
    else:
        fragment = json.loads(sys.stdin.read())
        stash = StashInterface(fragment["server_connection"])
        mode = fragment['args']['mode']

    if mode == "run_calculator":
        run_calculator()
    if mode == "destroy_managed_tags":
        destroy_managed_tags()

def destroy_managed_tags():
    tags = stash.find_tags(f={"description":{"value": "^\\[Managed By: PBC Plugin\\]","modifier": "MATCHES_REGEX"}}, fragment="id")
    log.info(f"Deleting {len(tags)} tags...")
    stash.destroy_tags([t["id"] for t in tags])

def run_calculator():

    all_tag_ids = []
    tag_updates = {}

    log.info("Finding Tags in Stash...")
    for enum_class in TAG_CLASSES:
        enumtag_stash_init(enum_class, all_tag_ids, tag_updates)

    # get performers with measurements
    performers = stash.find_performers({
        "measurements": {
            "value": "",
            "modifier": "NOT_NULL"
        }
    }, fragment="id name measurements weight height")
    
    log.info("Removing existing plugin tags...")
    stash.update_performers({
        "ids": [p["id"] for p in performers],
        "tag_ids":{
            "ids": all_tag_ids,
            "mode": "REMOVE"
        }
    })

    log.info("Parsing Performers...")
    for p in performers:
        p_id = f"{p['name']} ({p['id']})"
        try:
            p = StashPerformer(p)
            p.get_tag_updates(tag_updates)
        except DebugException as e:
            log.debug(f"{p_id:>30}: {e}")
        except WarningException as e:
            log.warning(f"{p_id:>30}: {e}")
        except Exception as e:
            log.error(f"{p_id:>30}: {e}")

    for enum, performer_ids in tag_updates.items():
        if not performer_ids:
            continue
        log.info(f"Adding {enum} tag to {len(performer_ids)} performer(s)...")
        stash.update_performers({
            "ids": performer_ids,
            "tag_ids":{
                "ids": [enum.tag_id],
                "mode": "ADD"
            }
        })

class StashPerformer:

    def __init__(self, resp) -> None:

        self.__dict__.update(resp)

        self.cupsize = ""
        self.band    = 0.0
        self.waist   = 0.0
        self.hips    = 0.0
        self.bust    = None
        
        self.bmi = 0
        self.body_shapes = []
        self.descriptor = None

        self.parse_measurements()
        self.calculate_bmi()

        self.set_breast_size()
        self.set_butt_size()

        self.match_body_shapes()
        self.set_type_descriptor()
         
    def parse_measurements(self):
        self.measurements = self.measurements.replace(" ", "")
        m = re.match(r'^(?P<band>\d+)(?P<cupsize>[a-zA-Z]+)\-(?P<waist>\d+)\-(?P<hips>\d+)$', self.measurements)
        if m:
            m = m.groupdict()
        else:
            raise DebugException(f"could not parse measurements: '{self.measurements}'")

        if not m.get("band"):
            raise DebugException(f"band size could not be parsed from measurements: '{self.measurements}'")
        if not m.get("cupsize"):
            raise DebugException(f"cupsize could not be parsed from measurements: '{self.measurements}'")
        if not m.get("waist"):
            raise DebugException(f"waist size could not be parsed from measurements: '{self.measurements}'")
        if not m.get("hips"):
            raise DebugException(f"hip size could not be parsed from measurements: '{self.measurements}'")

        self.cupsize = m.get("cupsize", "").upper()
        self.band    = float(m.get("band", 0))
        self.waist   = float(m.get("waist",0))
        self.hips    = float(m.get("hips", 0))

        # convert metric to imperial
        if self.band > 50 and self.waist > 50 and self.hips > 50:
            self.band  = self.band / CM_TO_INCH
            self.waist = self.waist / CM_TO_INCH
            self.hips  = self.hips / CM_TO_INCH
            log.debug(f"converted measurements from metric {self.measurements} -> {self.band}{self.cupsize}-{self.waist}-{self.hips}")

        for bust_diff, cup_list in enumerate(body_tags.BUST_DIFF_IDX):
            if self.cupsize in cup_list:
                self.bust = self.band + bust_diff
        if not self.bust:
            raise Exception(f"could not identify cupsize '{self.cupsize}' add to 'BUST_DIFF_IDX' list")

    def calculate_bmi(self):
        if not self.weight or not self.height:
            return
        self.weight = float(self.weight)
        self.height = float(self.height)
        self.bmi = (self.weight / (self.height*self.height)) * 10000

    def match_body_shapes(self):
        self.body_shapes = body_tags.calculate_shape(self)
        if not self.body_shapes:
            p_id = f"{self.name} ({self.id})"
            log.warning(f"{p_id:>30}: could not classify bodyshape bust={self.bust:.0f} waist={self.waist:.0f} hips={self.hips:.0f}")

    def set_type_descriptor(self):
        self.descriptor = None
        if not self.bmi or not self.body_shapes:
            return
        self.descriptor = body_tags.get_enum_for_threshold(self.bmi, BodyType)
        if self.descriptor == BodyType.AVERAGE and any(bs in self.body_shapes for bs in body_tags.CURVY_SHAPES):
            self.descriptor = BodyType.CURVY

    def set_breast_size(self):
        self.bust_band_diff = None
        self.breast_size = None
        if not self.cupsize or not self.bust:
            return
        self.breast_size = body_tags.get_enum_for_threshold(self.bust, BreastSize)

    def set_butt_size(self):
        self.butt_size = None
        if not self.hips:
            return
        self.butt_size = body_tags.get_enum_for_threshold(self.hips, ButtSize)

    def get_tag_updates(self, tag_updates={}):
        for body_shape in self.body_shapes:
            tag_updates[body_shape].append(self.id)
        if self.descriptor:
            tag_updates[self.descriptor].append(self.id)
        if self.breast_size:
            tag_updates[self.breast_size].append(self.id)
        if self.butt_size:
            tag_updates[self.butt_size].append(self.id)

    def __str__(self) -> str:
        body_shapes = ",".join([s.name for s in self.body_shapes])
        descriptor = "N/A"
        if self.descriptor:
            descriptor = self.descriptor.name
        p_id = f"{self.name} ({self.id})"
        return f"{p_id:>25} {self.bust:.0f}-{self.waist:.0f}-{self.hips:.0f} {self.bmi:5.2f} {descriptor:>7} {body_shapes:<17}"
    def __repr__(self) -> str:
        return str(self)

def enumtag_stash_init(enum_class, tag_id_list=[], enum_dict={}):
    for enum in enum_class:
        enum.tag_id = stash.find_tag(enum.value.tag_create_input(), create=True)["id"]
        tag_id_list.append(enum.tag_id)
        enum_dict[enum] = []
    return tag_id_list, enum_dict

class DebugException(Exception):
    pass
class WarningException(Exception):
    pass
class ErrorException(Exception):
    pass

if __name__ == '__main__':
    main()
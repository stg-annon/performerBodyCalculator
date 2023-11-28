import re, sys, json

try:
    import stashapi.log as log
    from stashapi.stashapp import StashInterface
except ModuleNotFoundError:
    print("You need to install stashapp-tools. (https://pypi.org/project/stashapp-tools/)", file=sys.stderr)
    print("If you have pip (normally installed with python), run this command in a terminal (cmd): 'pip install stashapp-tools'", file=sys.stderr)
    sys.exit()

import body_tags
from body_tags import BodyShape, HeightType, BodyType, BreastSize, ButtSize, BodyMassIndex, BreastCup, HipSize

#TAG_CLASSES = [BodyShape, BodyType, BreastSize, ButtSize, BodyMassIndex, BreastCup]
TAG_CLASSES = [BreastCup, HipSize]
CM_TO_INCH = 2.54

PERFORMER_FRAGMENT = """
id
name 
measurements
weight
height_cm
"""

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
    performers = stash.find_performers(fragment=PERFORMER_FRAGMENT)
    
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

        self.cupsize        = None
        self.band           = None
        self.waist          = None
        self.hips           = None
        self.bust           = None
        self.bust_band_diff = None
        self.breast_volume  = None

        self.breastcup      = None #enum
        self.hipsize        = None #enum
        
        self.bmi = 0
        self.body_shapes = []
        self.descriptor = None

        self.parse_measurements()
        self.calculate_bmi()

        self.set_breast_size()
        self.set_breast_cup()

        self.set_hip_size()

#        self.set_butt_size()

#        self.match_body_shapes()
#        self.set_type_descriptor()
         
    def parse_measurements(self):
        if self.weight:
            self.weight = float(self.weight)
        if self.height_cm:
            self.height_cm = float(self.height_cm)

        self.measurements = self.measurements.replace(" ", "")

        if self.measurements == "":
            log.debug(f"No measurements found for {str(self)}")
            return

        # Full Measurements | Band, Cup Size, Waist, Hips | Example: "32D-28-34"
        band_cup_waist_hips = re.match(r'^(?P<band>\d+)(?P<cupsize>[a-zA-Z]+)\-(?P<waist>\d+)\-(?P<hips>\d+)$', self.measurements)
        if band_cup_waist_hips:
            m = band_cup_waist_hips.groupdict()
        else:
            # Fashion Measurements | Bust, Waist, Hips | Example: "36-28-34"
            bust_waist_hips = re.match(r'^(?P<bust>\d+)\-(?P<waist>\d+)\-(?P<hips>\d+)$', self.measurements)
            if bust_waist_hips:
                m = bust_waist_hips.groupdict()
            else:
                # Bra Measurements | Band, Cup Size | Example: "32D" or "32D (81D)"
                band_cup = re.match(r'^(?P<band>\d+)(?P<cupsize>[a-zA-Z]+)(?: ?\(\d+[a-zA-Z]+\))?$', self.measurements)
                if band_cup:
                    m = band_cup.groupdict()
                else:
                    raise WarningException(f"could not parse measurements: '{self.measurements}'")

        if m.get("cupsize"):
            self.cupsize = m.get("cupsize", "").upper()
        if m.get("band"):
            self.band    = float(m.get("band", 0))
        if m.get("bust"):
            self.bust    = float(m.get("bust", 0))
        if m.get("waist"):
            self.waist   = float(m.get("waist",0))
        if m.get("hips"):
            self.hips    = float(m.get("hips", 0))

        # convert metric to imperial
        if self.band and self.band > 50 and self.waist and self.waist > 50 and self.hips and self.hips > 50:
            self.band  = self.band / CM_TO_INCH
            self.waist = self.waist / CM_TO_INCH
            self.hips  = self.hips / CM_TO_INCH
            log.debug(f"converted measurements from metric {self.measurements} -> {self.band}{self.cupsize}-{self.waist}-{self.hips}")
        elif self.bust and self.bust > 50 and self.waist and self.waist > 50 and self.hips and self.hips > 50:
            self.bust  = self.bust / CM_TO_INCH
            self.waist = self.waist / CM_TO_INCH
            self.hips  = self.hips / CM_TO_INCH
            log.debug(f"converted measurements from metric {self.measurements} -> {self.bust}-{self.waist}-{self.hips}")

        if self.band and self.cupsize:
            self.bust_band_diff = body_tags.get_bust_band_difference(self.cupsize)
            self.bust = self.band + self.bust_band_diff
            self.breast_volume = (self.band / 2.0) + self.bust_band_diff
            log.debug(f"Bra size {int(self.band)}{self.cupsize} converted to {(self.band / 2.0)} + {self.bust_band_diff} = {self.breast_volume} volume points")

    def calculate_bmi(self):
        if not self.weight or not self.height_cm:
            return
        breast_weight = body_tags.approximate_breast_weight(self.bust_band_diff)
        self.bmi = (self.weight-breast_weight) / (self.height_cm/100) ** 2

    def match_body_shapes(self):
        self.body_shapes = body_tags.calculate_shape(self)
        if not self.body_shapes:
            p_id = f"{self.name} ({self.id})"
            if not self.bust or not self.waist or not self.hips:
                log.debug(f"{p_id:>30}: could not classify bodyshape, missing required measurements")
            else:
                log.warning(f"{p_id:>30}: could not classify bodyshape bust={self.bust:.0f} waist={self.waist:.0f} hips={self.hips:.0f}")

    def set_type_descriptor(self):
        self.descriptor = None
        if not self.bmi:
            return
        self.descriptor = BodyType.match_threshold(self.bmi)
        
        if self.descriptor == BodyType.FIT and HeightType.SHORT.within_threshold(self.height_cm):
            self.descriptor = BodyType.PETITE
        if self.descriptor == BodyType.AVERAGE and self.body_shapes and any(bs in self.body_shapes for bs in body_tags.CURVY_SHAPES):
            self.descriptor = BodyType.CURVY

    def set_breast_size(self):
        self.breast_size = None
        if not self.breast_volume:
            return
        self.breast_size = BreastSize.match_threshold(self.breast_volume)

    def set_breast_cup(self):
        log.debug(f"self.cupsize={self.cupsize}")
        self.breastcup = body_tags.calculate_cup(self)
        log.debug(f"self.breastcup={self.breastcup}")

    def set_hip_size(self):
        self.hip_size = body_tags.calculate_hip_size(self)

    def set_butt_size(self):
        self.butt_size = None
        if not self.hips:
            return
        self.butt_size = ButtSize.match_threshold(self.hips)

    def get_tag_updates(self, tag_updates={}):
#        for body_shape in self.body_shapes:
#            tag_updates[body_shape].append(self.id)
#        if self.descriptor:
#            tag_updates[self.descriptor].append(self.id)
#        if self.breast_size:
#            tag_updates[self.breast_size].append(self.id)
#        if self.butt_size:
#            tag_updates[self.butt_size].append(self.id)
        if self.breastcup:
            log.debug(f"self.breastcup={self.breastcup}")
            tag_updates[self.breastcup].append(self.id)
        if self.hip_size:
            log.debug(f"self.hip_size={self.hip_size}")
            tag_updates[self.hip_size].append(self.id)

    def __str__(self) -> str:
        body_shapes = ",".join([s.name for s in self.body_shapes])
        descriptor = "N/A"
        if self.descriptor:
            descriptor = self.descriptor.name
        p_id = f"{self.name} ({self.id})"
        p_str = f"{p_id:>25}"
        if self.band and self.cupsize:
            p_str += f" {self.band:.0f}{self.cupsize}"
        elif self.bust:
            p_str += f" {self.bust:.0f}"
        if self.waist and self.hips:
            p_str += f"-{self.waist:.0f}-{self.hips:.0f}"
        p_str += f" {self.bmi:5.2f}bmi {descriptor:>7} {body_shapes:<17}"
        return p_str
    def __repr__(self) -> str:
        return str(self)

def enumtag_stash_init(enum_class, tag_id_list=[], enum_dict={}):
    for enum in enum_class:
        enum.tag_id = stash.find_tag(enum.value.tag_create_input(), create=True)["id"]
        log.debug(f"{enum.tag_id}")
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

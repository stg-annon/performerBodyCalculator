import operator
from enum import Enum

from dataclasses import dataclass

@dataclass
class StashTagDC:
    name: str
    threshold: float | None = None
    description :str | None = ""
    aliases: list[str] | None = None
    image: str | None = None

    def tag_create_input(self):
        create_input = {"name": self.name}
        create_input["description"] =  "[Managed By: PBC Plugin]\n"+self.description
        if self.aliases:
            create_input["aliases"] = self.aliases
        if self.image:
            create_input["image"] = self.image
        return create_input

class StashTagEnum(Enum):
    def __repr__(self) -> str:
        #  return f"{self.__class__.__name__}.{self.name}"
        return f"{self.name}"

class StashTagEnumComparable(StashTagEnum):
    def __new__(cls, *args):
        obj = object.__new__(cls)
        obj._order_ = len(cls.__members__)
        return obj

    def __gt__(self, other):
        try:
            return self._order_ > other._order_
        except:
            pass
        return NotImplemented

    def __lt__(self, other):
        try:
            return self._order_ < other._order_
        except:
            pass
        return NotImplemented
    
    def within_threshold(self, compare_value):
        if not self.value.threshold:
            return
        op, value = self.value.threshold
        return op(compare_value, value)

    @classmethod
    def match_threshold(cls, compare_value):
        for enum in cls:
            if enum.within_threshold(compare_value):
                return enum
    
# shape determined from calculate_shape()
class BodyShape(StashTagEnum):
    HOURGLASS = StashTagDC(
        "Figure: Hourglass",
        image="https://user-images.githubusercontent.com/14135675/225106804-d573bba1-7ca2-4c55-b1e1-d858c03040be.jpg",
        description='Hourglass:\nIf hips and bust are nearly equal in size with a well-defined waist that’s narrower than both.\n\nLegs and upper body are probably considered proportionate.\n\nShoulders may be slightly rounded, and most likely has a rounded buttocks.'
    )
    BOTTOM_HOURGLASS = StashTagDC(
        "Figure: Bottom Hourglass",
        image="https://user-images.githubusercontent.com/14135675/225106797-c818b1ab-d82d-4130-8184-b661c9fd7b44.jpg",
        description='Bottom hourglass:\nHas the general hourglass shape, but hip measurements are slightly larger than bust.'
    )
    TOP_HOURGLASS = StashTagDC(
        "Figure: Top Hourglass",
        image="https://user-images.githubusercontent.com/14135675/225106819-6462ac6a-8ca7-41ac-9cd5-467c9c80e7f1.jpg",
        description='Top hourglass:\nHas the general hourglass shape, but bust measurements are slightly larger than hips.'
    )
    SPOON = StashTagDC(
        "Figure: Spoon",
        image="https://user-images.githubusercontent.com/14135675/225106816-574eee46-d14c-4869-9137-6477bdedd2d5.jpg",
        description='Spoon:\nThe spoon body type is similar to the Triangle or “Pear” shape.\n\nHips are larger than bust or the rest of body and may have a “shelf”-like appearance.\n\nLikely has a defined waist. May also carry some weight in upper arms and upper thighs.'
    )
    TRIANGLE = StashTagDC(
        "Figure: Triangle",
        image="https://user-images.githubusercontent.com/14135675/225106820-6b8d71a7-3ba1-4aec-a763-a4e52e71363b.jpg",
        description='Triangle / “Pear”:\nShoulders and bust are narrower than hips.\n\nLikely to have slim arms and a fairly defined waist. waist most likely slopes out to hips.'
    )
    INVERTED_TRIANGLE = StashTagDC(
        "Figure: Inverted Triangle",
        image="https://user-images.githubusercontent.com/14135675/225106808-38ff54fa-a8cd-4f2e-b9b7-ae8ec6371357.jpg",
        description='Inverted triangle / “Apple”:\nShoulders and bust are larger than relatively narrow hips.'
    )
    RECTANGLE = StashTagDC(
        "Figure: Rectangle",
        image="https://user-images.githubusercontent.com/14135675/225106815-a4afdeda-835a-4888-b581-f382c18f3487.jpg",
        description='Rectangle / Straight / “Banana”:\nWaist measurements are about the same as hip or bust, and shoulders and hips are about the same width.'
    )
    DIAMOND = StashTagDC(
        "Figure: Diamond",
        image="https://user-images.githubusercontent.com/14135675/225106802-8cb88df8-7804-4f1f-a65c-c6e86a64698d.jpg",
        description='Diamond:\nBroader hips than shoulders, a narrow bust, and a fuller waistline.\n\nMay carry a little more weight in upper legs. May also have slender arms.'
    )
    OVAL = StashTagDC(
        "Figure: Oval",
        image="https://user-images.githubusercontent.com/14135675/225106814-e80f5cfe-c467-4b91-bd27-d9360dbb0894.jpg",
        description='Round / Oval:\nBust is larger than the rest of body, hips are narrow, and waist is fuller.'
    )

# threshold based off of performer.bmi
CURVY_SHAPES = [BodyShape.TOP_HOURGLASS, BodyShape.BOTTOM_HOURGLASS, BodyShape.HOURGLASS]
class BodyType(StashTagEnumComparable):
    PETITE  = StashTagDC("Petite Body", threshold=None)
    CURVY   = StashTagDC("Curvy Body",  threshold=None)
    SKINNY  = StashTagDC("Skinny Body", threshold=(operator.lt, 18))
    FIT     = StashTagDC("Fit Body",    threshold=(operator.lt, 23))
    AVERAGE = StashTagDC("Average Body",threshold=(operator.lt, 29))
    BBW     = StashTagDC("BBW Body",    threshold=(operator.lt, 55))
    SSBBW   = StashTagDC("SSBBW Body",  threshold=(operator.ge, 55))

# threshold based off of performer.height
class HeightType(StashTagEnumComparable):
    SHORT   = StashTagDC("Short",  threshold=(operator.le, 160))
    TALL    = StashTagDC("Tall",   threshold=(operator.ge, 180))

# threshold based off of performer.bust
class BreastSize(StashTagEnumComparable):
    TINY    = StashTagDC("Tiny Breasts",   threshold=(operator.lt, 27))
    SMALL   = StashTagDC("Small Breasts",  threshold=(operator.lt, 32))
    MEDIUM  = StashTagDC("Medium Breasts", threshold=(operator.lt, 37))
    LARGE   = StashTagDC("Large Breasts",  threshold=(operator.lt, 42))
    HUGE    = StashTagDC("Huge Breasts",   threshold=(operator.lt, 47))
    MASSIVE = StashTagDC("Massive Breasts",threshold=(operator.ge, 47))

# threshold based off of performer.hips 
class ButtSize(StashTagEnumComparable):
    TINY    = StashTagDC("Tiny Ass",   threshold=(operator.lt, 28))
    SMALL   = StashTagDC("Small Ass",  threshold=(operator.lt, 32))
    MEDIUM  = StashTagDC("Medium Ass", threshold=(operator.lt, 40))
    LARGE   = StashTagDC("Large Ass",  threshold=(operator.lt, 44))
    HUGE    = StashTagDC("Huge Ass",   threshold=(operator.lt, 48))
    MASSIVE = StashTagDC("Massive Ass",threshold=(operator.ge, 48))

# Shape Calculation References:
#  https://en.wikipedia.org/wiki/Female_body_shape#FFIT_for_Apparel_measurements
#  https://scholarsbank.uoregon.edu/xmlui/bitstream/handle/1794/25863/2022sokolowski.pdf?sequence=1&isAllowed=y
def calculate_shape(performer):

    shapes = []
    if performer.bust <= 0 and performer.waist <= 0 and performer.hips <= 0:
        return

    bust_hips = performer.bust - performer.hips
    bust_waist = performer.bust - performer.waist
    hips_bust = performer.hips - performer.bust
    hips_waist = performer.hips - performer.waist
    
    hips_over_waist = performer.hips/performer.waist # highip/waist

    # bust to waist ratio close to 1 with a small waist
    if bust_hips <= 1 and hips_bust < 3.6 and (9 <= bust_waist or 10 <= hips_waist):
        shapes.append(BodyShape.HOURGLASS)

    # If (hip-bust) ≥ 3.6 and (hip-bust) < 10, then if (hip-waist) ≥ 9, then if (high hip/waist) < 1.193 
    # hourglass with more defined waist
    if 3.6 <= hips_bust and hips_bust < 10 and 9 <= hips_waist and hips_over_waist < 1.193:
        shapes.append(BodyShape.BOTTOM_HOURGLASS)

    # hourglass with more defined bust
    if 1 < bust_hips and bust_hips < 10 and 9 <= bust_waist:
        shapes.append(BodyShape.TOP_HOURGLASS)

    # spoon: hips greater than bust, triangle with smaller waist
    if 2 < hips_bust and 7 <= hips_waist and 1.193 < hips_over_waist:
        shapes.append(BodyShape.SPOON)
    
    # triangle small bust large hips with larger/tapered waist
    if 3.6 <= hips_bust and 0 <= hips_waist < 9 or bust_waist < 0 and 0 <= hips_waist:
        shapes.append(BodyShape.TRIANGLE)

    if 3.6 <= bust_hips and bust_waist < 9:
        shapes.append(BodyShape.INVERTED_TRIANGLE)

    if hips_bust < 3.6 and bust_hips < 3.6 and 0 <= bust_waist < 9 and 0 <= hips_waist < 10:
        shapes.append(BodyShape.RECTANGLE)
    
    if hips_waist < 0 and bust_waist < 0:
        shapes.append(BodyShape.DIAMOND)
    
    if hips_waist < 0 and 0 <= bust_waist:
        shapes.append(BodyShape.OVAL)

    return shapes

# SEE: https://en.wikipedia.org/wiki/Bra_size#The_meaning_of_cup_sizes_varies
# "cup size approximates the difference between the Over-the-bust and band measurements in inches"
# index == bust band difference in inches
BUST_DIFF_IDX = [
    ['AA'],
    ['A'],
    ['B'],
    ['C'],
    ['D'],
    ['E','DD'],
    ['F','DDD','EE'],
    ['G','DDDD'],
    ['H','FF'],
    ['I'],
    ['J','GG'],
    ['K'],
    ['L','HH'],
    ['M'],
    ['N','JJ'],
    ['O'],
    ['P','KK'],
    ['Q'],
    ['R','LL'],
]
import operator
from enum import Enum

from dataclasses import dataclass

@dataclass
class StashTagDC:
    name: str
    threshold: tuple | None = None
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
        if op == operator.contains:
            return op(value, compare_value)
        return op(compare_value, value)

    @classmethod
    def match_threshold(cls, compare_value):
        for enum in cls:
            if enum.within_threshold(compare_value):
                return enum

# body mass index determined from calculate_bmi()
class BodyMassIndex(StashTagEnum):
    SEVERELY_UNDERWEIGHT = StashTagDC("BMI: Severely Underweight",image='',description='')
    UNDERWEIGHT = StashTagDC("BMI: Underweight",image='',description='')
    HEALTHY = StashTagDC("BMI: Healthy",image='',description='')
    OVERWEIGHT = StashTagDC("BMI: Overweight",image='',description='')
    OBESE_CLASS_1 = StashTagDC("BMI: Obese Class 1",image='',description='')
    OBESE_CLASS_2 = StashTagDC("BMI: Obese Class 2",image='',description='')
    SEVERELY_OBESE = StashTagDC("BMI: Extremely Obese",image='',description='')

class HipSize(StashTagEnum):
    WIDE = StashTagDC("Hips: Wide")
    MEDIUM = StashTagDC("Hips: Medium")
    SLIM = StashTagDC("Hips: Slim")

class BreastCup(StashTagEnumComparable):
    AA = StashTagDC("Cup: AA", threshold=(operator.contains, ['AA']))
    A  = StashTagDC("Cup: A",  threshold=(operator.contains, ['A']))
    B  = StashTagDC("Cup: B",  threshold=(operator.contains, ['B']))
    C  = StashTagDC("Cup: C",  threshold=(operator.contains, ['C']))
    D  = StashTagDC("Cup: D",  threshold=(operator.contains, ['D']))
    E  = StashTagDC("Cup: E",  threshold=(operator.contains, ['E','DD']))
    F  = StashTagDC("Cup: F",  threshold=(operator.contains, ['F','DDD','EE']))
    G  = StashTagDC("Cup: G",  threshold=(operator.contains, ['G','DDDD']))
    H  = StashTagDC("Cup: H",  threshold=(operator.contains, ['H','FF']))
    I  = StashTagDC("Cup: I",  threshold=(operator.contains, ['I']))
    J  = StashTagDC("Cup: J",  threshold=(operator.contains, ['J','GG']))
    K  = StashTagDC("Cup: K",  threshold=(operator.contains, ['K']))
    L  = StashTagDC("Cup: L",  threshold=(operator.contains, ['L','HH']))
    M  = StashTagDC("Cup: M",  threshold=(operator.contains, ['M']))
    N  = StashTagDC("Cup: N",  threshold=(operator.contains, ['N','JJ']))
    O  = StashTagDC("Cup: O",  threshold=(operator.contains, ['O']))
    P  = StashTagDC("Cup: P",  threshold=(operator.contains, ['P','KK']))
    Q  = StashTagDC("Cup: Q",  threshold=(operator.contains, ['Q']))
    R  = StashTagDC("Cup: R",  threshold=(operator.contains, ['R','LL']))

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

# threshold based off of performer.height_cm
# https://ourworldindata.org/human-height
# current implementation uses global average
# TODO - can further segment by country/continent factor, see:
# https://www.worlddata.info/average-bodyheight.php
# height means by ethnicity (US)
# https://thebonescience.com/blogs/journal/average-height-around-the-world
# height standard deviation (global)
# https://www.nber.org/system/files/working_papers/h0108/h0108.pdf
F_HEIGHT_MEAN = 164.7
F_HEIGHT_SD = 7.07
class HeightType(StashTagEnumComparable):
    SHORT   = StashTagDC("Short",  threshold=(operator.le, F_HEIGHT_MEAN - F_HEIGHT_SD))
    MEDIUM  = StashTagDC("Medium",  threshold=(operator.le, F_HEIGHT_MEAN - F_HEIGHT_SD))
    TALL    = StashTagDC("Tall",   threshold=(operator.ge, F_HEIGHT_MEAN + F_HEIGHT_SD))

# threshold based off of performer.breast_volume
class BreastSize(StashTagEnumComparable):
    TINY    = StashTagDC("Tiny Breasts",   threshold=(operator.lt, 16))
    SMALL   = StashTagDC("Small Breasts",  threshold=(operator.lt, 19))
    MEDIUM  = StashTagDC("Medium Breasts", threshold=(operator.lt, 23))
    LARGE   = StashTagDC("Large Breasts",  threshold=(operator.lt, 27))
    HUGE    = StashTagDC("Huge Breasts",   threshold=(operator.lt, 31))
    MASSIVE = StashTagDC("Massive Breasts",threshold=(operator.ge, 31))

# threshold based off of performer.hips 
class ButtSize(StashTagEnumComparable):
    TINY    = StashTagDC("Tiny Ass",   threshold=(operator.lt, 28))
    SMALL   = StashTagDC("Small Ass",  threshold=(operator.lt, 32))
    MEDIUM  = StashTagDC("Medium Ass", threshold=(operator.lt, 40))
    LARGE   = StashTagDC("Large Ass",  threshold=(operator.lt, 44))
    HUGE    = StashTagDC("Huge Ass",   threshold=(operator.lt, 48))
    MASSIVE = StashTagDC("Massive Ass",threshold=(operator.ge, 48))

def calculate_hip_size(performer):
    if not performer.waist or not performer.hips:
        return None

    whr = performer.waist / performer.hips

    if whr > 0.8:
        return HipSize.WIDE
    elif whr > 0.64:
        return HipSize.MEDIUM
    else:
        return HipSize.SLIM

def calculate_cup(performer):
    if not performer.cupsize:
        return None
    return BreastCup.match_threshold(performer.cupsize)
         
# https://www.ncbi.nlm.nih.gov/books/NBK541070/
def calculate_bmi(performer):
    if performer.bmi < 1:
        return None
    elif performer.ethnicity.title() == 'Asian':
        if performer.bmi < 16.5:
            return BodyMassIndex.SEVERELY_UNDERWEIGHT
        elif performer.bmi < 18.5:
            return BodyMassIndex.UNDERWEIGHT
        elif performer.bmi < 23:
            return BodyMassIndex.HEALTHY
        elif performer.bmi < 25:
            return BodyMassIndex.OVERWEIGHT
        elif performer.bmi < 30:
            return BodyMassIndex.OBESE_CLASS_1
        elif performer.bmi < 35:
            return BodyMassIndex.OBESE_CLASS_2
        else:
            return BodyMassIndex.SEVERELY_OBESE
    else:
        if performer.bmi < 16.5:
            return BodyMassIndex.SEVERELY_UNDERWEIGHT
        elif performer.bmi < 18.5:
            return BodyMassIndex.UNDERWEIGHT
        elif performer.bmi < 25:
            return BodyMassIndex.HEALTHY
        elif performer.bmi < 30:
            return BodyMassIndex.OVERWEIGHT
        elif performer.bmi < 35:
            return BodyMassIndex.OBESE_CLASS_1
        elif performer.bmi < 40:
            return BodyMassIndex.OBESE_CLASS_2
        else:
            return BodyMassIndex.SEVERELY_OBESE


# Shape Calculation References:
#  https://en.wikipedia.org/wiki/Female_body_shape#FFIT_for_Apparel_measurements
#  https://scholarsbank.uoregon.edu/xmlui/bitstream/handle/1794/25863/2022sokolowski.pdf?sequence=1&isAllowed=y
def calculate_shape(performer):

    shapes = []
    if not performer.bust or not performer.waist or not performer.hips:
        return shapes

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
def get_bust_band_difference(cupsize):
    for difference, cup_enum in enumerate(BreastCup):
        if cup_enum.within_threshold(cupsize):
            return difference    
    raise Exception(f"could not identify cupsize '{cupsize}' add to 'BreastCup' enum")

# Approximates breasts weight in kg, derived from this chart https://i.imgur.com/QZBhze8.png
def approximate_breast_weight(bust_band_diff):
    if not bust_band_diff:
        return 0
    bust_band_diff -= 1 
    # 3 Degree Polynomial Trendline
    weight_lb = 0.765 + 0.415 * bust_band_diff + -0.0168 * bust_band_diff ** 2 + 0.00247 * bust_band_diff ** 3
    return weight_lb * 0.453

from src.scan.scansion import *


class Meter:
    """ Represents a meter as a set of Scansion objects. Supports iterating over these objects. """

    METERS = {}  # dictionary of available meters.
    # Can also contain tuples of Meter objects: METERS["elegiacs"] = (HEXAMETER, PENTAMETER)

    def __init__(self, feet, name):
        """
        Initialize a new Meter object from a list of meter patterns of which it is composed.
        :param feet:    a list of meter feet, each of which is a list of possible feet scansions,
                        i.e. a feet of hexameter is (SPONDEE, DACTYL)
        """
        self.scansions = {EMPTY, }
        self.feet = feet
        self.name = name
        Meter.METERS[name] = self
        for foot in feet:
            tmp_scansions = set()
            for alternative in foot:
                for existing in self.scansions:
                    tmp_scansions.add(existing + alternative)
            self.scansions = tmp_scansions
        self.__solve_conflicts()

    def get_matching_scansions(self, scansion, precise=False):
        """
        Return all scansions in self.scansions that match the given scansion
        :param scansion: a Scansion object
        :param precise:  if True, will not use the UNK symbol for ancipites
        :return: a list of Scansion objects
        """
        result = []
        for meter_scansion in self:
            if not precise and meter_scansion.matches(scansion):
                result.append(meter_scansion)
            elif precise:
                for precise_meter_scansion in meter_scansion.precise_matchings():
                    if precise_meter_scansion.matches(scansion):
                        result.append(precise_meter_scansion)
        return result

    def decompose(self, scansion, turn_off_assertions=False):
        """
        Decompose a meter pattern into feet. E.g. this line of hexameter: "_^^___^^___^^_*"
        will be decomposed into ["_^^", "__", "_^^", "__", "_^^", "_*"]. There can be several
        possible decomposition, so the result is a list of lists of Scansion objects
        :param scansion:            a Scansion object
        :param turn_off_assertions  if True, do not assert that there is only one matching scansion
        :return:                    a list of lists of Scansion objects
        """
        pattern = self.get_matching_scansions(scansion)
        if len(pattern) == 0 and turn_off_assertions:
                return [[]]
        elif len(pattern) > 1 and turn_off_assertions:
            pattern = [pattern[0]]
        assert len(pattern) == 1
        scansion = scansion.apply_mask(pattern[0])
        return self.__recursively_decompose(scansion, 0)

    def __recursively_decompose(self, scansion, feet_id):
        """
        A recursive method that performs what is described in the docstirng of decompose()
        :param scansion: part of the scansion left to decompose
        :param feet_id:  number of feet already counted in decomposition
        :return:
        """
        results = []
        for alternative in self.feet[feet_id]:
            first, second = scansion.divide_by(alternative)
            if not first:
                continue
            if second and feet_id < len(self.feet) - 1:
                decompositions = self.__recursively_decompose(second, feet_id + 1)
                for decomposition in decompositions:
                    results.append([first] + decomposition)
            elif not second and feet_id == len(self.feet) - 1:
                results.append([first])
        return results

    def __solve_conflicts(self):
        """
        Check if any two scansions defining this meter match.
        If they do, replace them with precise scansions (i.e. without ancipites)
        :return: a boolean
        """
        new_scansions = set()
        while self.scansions:  # for every scansion
            scansion = self.scansions.pop()
            # check if this scansion matches any other scansion in the set
            matches = False
            for other_scansion in self.scansions:
                if scansion.matches(other_scansion):
                    matches = True
                    break
            # if match is not found, place the scansion back in the new set
            if not matches:
                new_scansions.add(scansion)
                continue
            # else replace the scansion with precise scansions
            self.scansions.remove(other_scansion)
            for precise in scansion.precise_matchings() + other_scansion.precise_matchings():
                new_scansions.add(precise)
        self.scansions = new_scansions

    def __iter__(self):
        return self.scansions.__iter__()

print("Loading meters...")
# disyllabics
IAMB = SHORT + LONG
SPONDEE = LONG + LONG
IAMB_OR_SPONDEE = UNK + LONG
# trisyllabics
TRIBRACH = SHORT + SHORT + SHORT
DACTYL = LONG + SHORT + SHORT
ANAPEST = SHORT + SHORT + LONG
TRIBRACH_OR_DACTYL = UNK + SHORT + SHORT
# tetrasyllabic(s)
PROCELEUSMATIC = SHORT + SHORT + SHORT + SHORT

# metrical feet
H_FOOT = (SPONDEE, DACTYL)  # hexameter
H_FINAL_FOOT = (LONG + UNK, )  # final hexameter foot
T_ODD_FOOT = (IAMB_OR_SPONDEE, TRIBRACH_OR_DACTYL, ANAPEST, PROCELEUSMATIC)  # odd foot of trimeter
T_EVEN_FOOT = (IAMB, TRIBRACH)  # even foot
T_FINAL_FOOT = (SHORT + UNK, )  # final foot

T_ODD_FOOT_CORRER = (IAMB_OR_SPONDEE, TRIBRACH_OR_DACTYL, ANAPEST)
T_EVEN_FOOT_CORRER = (IAMB, TRIBRACH, ANAPEST)  # even foot in Correr's trimeter
T_FINAL_FOOT_CORRER = (SHORT + UNK, SHORT + SHORT + UNK)  # final foot in Correr's trimeter

# meters
HEXAMETER = Meter((H_FOOT, H_FOOT, H_FOOT, H_FOOT, H_FOOT, H_FINAL_FOOT), "hexameter")
PENTAMETER = Meter((H_FOOT, H_FOOT, [LONG], H_FOOT, H_FOOT, [UNK]), "pentameter")
Meter((T_ODD_FOOT, T_EVEN_FOOT, T_ODD_FOOT, T_EVEN_FOOT, T_ODD_FOOT, T_FINAL_FOOT), "trimeter")
Meter((T_ODD_FOOT_CORRER, T_EVEN_FOOT_CORRER,
       T_ODD_FOOT_CORRER, T_EVEN_FOOT_CORRER,
       T_ODD_FOOT_CORRER, T_FINAL_FOOT_CORRER), "trimeterCORRER")
Meter((T_ODD_FOOT_CORRER, T_ODD_FOOT_CORRER, T_ODD_FOOT_CORRER,
       T_ODD_FOOT_CORRER, T_ODD_FOOT_CORRER, T_FINAL_FOOT_CORRER), "trimeterDATI")
Meter.METERS["elegiacs"] = (HEXAMETER, PENTAMETER)

if __name__ == "__main__":
    # assertions and checks:
    print(HEXAMETER.decompose(Scansion("A_rma^ vi^ru_mque^ ca^no_ "
                                       "Tro_j[ae] qui_ pri_mu^s a^b o_ri*s")))

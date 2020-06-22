import re


class Scansion:
    """ Represents a scansion of a piece of text (line, word, etc.)"""

    # throughout this code, "_" marks a long syllable, "^" - a short one,
    # and "*" - a syllable of unknown quantity.
    NON_QUANT_SYMBOLS = re.compile("[^\^_*]")
    DIPHTHONG = re.compile("\[[^\]]*\]")  # diphthongs are enclosed with brackets

    def __init__(self, scansion):
        """
        Initialize a Scansion object from a string.
        :param scansion: may only contain whitespaces, alphabetic characters,
        _, ^, and * symbols, [...] marking long diphthongs, or (...) marking elided parts of a word
        """
        self.scansion = scansion
        self.pattern = Scansion.DIPHTHONG.sub("_", self.scansion)  # replace [] with "long" symbol
        self.pattern = Scansion.NON_QUANT_SYMBOLS.sub("", self.pattern)  # remove non quant symbols

    def matches(self, scansion):
        """
        Check if two the scansions match (have the same number and quantity of syllables).
        An anceps syllable (*) matches a syllable of any length, much like regex's "."
        :param scansion:    another Scansion object
        :return:            a boolean
        """
        if len(self.pattern) != len(scansion.pattern):
            return False
        for i, syl in enumerate(self.pattern):
            if syl != scansion.pattern[i] and syl != "*" and scansion.pattern[i] != "*":
                return False
        return True

    def apply_mask(self, mask):
        """
        Take a different but matching scansion and return a new scansion with all the quantitity
        marks in self replaced with quantitu marks in mask
        :param mask:    another Scansion object
        :return:        a new Scansion object
        """
        assert self.matches(mask)
        syllable_id = 0
        new_scansion = self.scansion
        for i in range(len(new_scansion)):
            if new_scansion[i] in "*^_":
                new_scansion = new_scansion[:i] + mask.pattern[syllable_id] + new_scansion[i + 1:]
                syllable_id += 1
            elif new_scansion[i] == "[":  # diphthong
                syllable_id += 1
        return Scansion(new_scansion)

    def precise_matchings(self):
        """
        Returns a list of matching scansions that do not use the anceps quantity symbol (*)
        E.g.: Scansion("*_").precise_matchings() will return [Scansion("^_"), Scansion("__")]
        :return: a list of Scansion objects
        """
        return [Scansion(x) for x in self.__recursive_precise_matchings(self.pattern)]

    def __recursive_precise_matchings(self, string):
        """
        A recursive helper function for computing the result of precise_matchings()
        :param string: a string of quantity symbols
        :return:       a list of precise versions of that string
        """
        if len(string) == 0:
            return [string]
        rpm = self.__recursive_precise_matchings(string[1:])
        if string[0] != "*":
            return [string[0] + x for x in rpm]
        return ["_" + x for x in rpm] + ["^" + x for x in rpm]

    def begins_with(self, scansion):
        """
        Checks that this Scansion object begins with syllables matching the syllables in another
        Scansion object. Examples:
            Scansion("_^_").begins_with(Scansion("_^")) returns True
            Scansion("_^_").begins_with(Scansion("__")) returns False
            Scansion("_^_").begins_with(Scansion("_*")) returns True
        :param scansion:    another Scansion object
        :return:            a boolean
        """
        if len(self.pattern) >= len(scansion.pattern) and \
                Scansion(self.pattern[:len(scansion.pattern)]).matches(scansion):
            return True
        return False

    def divide_by(self, scansion):
        """
        Attempt to match the beginning of self with scansion.
        If match is unsuccessful, return None, None
        If match is successful, divide self in a tuple of two elements so that the first element in
        the tuple matches scansion. The second element is either None or another Scansion object.
        For example, Scansion("a_rma^ vi^ru_mque^ ca^no_...").divide_by(Scansion("_^^")) returns:
        (Scansion("a_rma^ vi^"), Scansion("ru_mque^ ca^no_..."))
        :param scansion: another Scansion object
        :return:         a tuple of two Scansion objects (can be None)
        """
        if not self.begins_with(scansion):
            return None, None
        if len(self.pattern) == len(scansion.pattern):  # scansions have equal number of syllables
            return self, None
        sylls = len(scansion.pattern)
        i = 0  # division point
        while sylls > 0:
            if self.scansion[i] in "]*_^":
                sylls -= 1
            i += 1
        # Division should happen at word boundary, if possible. If there is a single consonant
        # between the two vowels, the consonant goes with the second syllable. If there are
        # more than one, the first consonant goes with the first syllable. This is only a
        # heuristic for syllable division as there are other things at play, such as prefixes, etc.
        j = i
        while self.scansion[j] not in " [" and self.scansion[j+1] not in "_*^":
            j += 1
        if self.scansion[j] != " " and j - i > 1:
            i += 1
        elif self.scansion[j] == " ":
            i = j
        return Scansion(self.scansion[:i]), Scansion(self.scansion[i:])

    def count_elisions(self):
        """
        Count the number of elisions in this Scansion object
        :return: an integer
        """
        return self.scansion.count("(")

    def __str__(self):
        return self.scansion.__str__()

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return self.pattern.__hash__()

    def __eq__(self, other):
        return self.pattern == other.pattern

    def __add__(self, other):
        return Scansion(self.scansion + " " + other.scansion)

    def __radd__(self, other):
        if isinstance(other, int):
            return self
        elif isinstance(other, Scansion):
            return self + other

# These are used elswhere in the code, especially in meter.py
EMPTY = Scansion("")
LONG = Scansion("_")
SHORT = Scansion("^")
UNK = Scansion("*")

if __name__ == "__main__":
    # assertions and checks;
    patresque_l = Scansion("pa_tre_sque^")
    patresque_s = Scansion("pa^tre_sque^")
    patresque_u = Scansion("pa*tre_sque^")
    patres_l = Scansion("pa_tre_s")

    assert patres_l + Scansion("ne^") == patresque_l

    assert patresque_u.pattern == "*_^"  # check that pattern is constructed correctly
    assert patresque_u.matches(patresque_l)  # check matches()
    assert not patresque_l.matches(patresque_s)  # check matches()
    assert not patres_l.matches(patresque_l)   # check matches()
    assert patresque_l.apply_mask(patresque_u).scansion == patresque_u.scansion
    assert patresque_l in patresque_u.precise_matchings()
    assert patresque_s in patresque_u.precise_matchings()
    assert patresque_u.begins_with(patres_l)
    assert not patresque_s.begins_with(patres_l)

    assert Scansion("ca^no_").divide_by(Scansion("^"))[0].scansion == "ca^"
    assert Scansion("a^b o_ri*s").divide_by(Scansion("^"))[0].scansion == "a^b"
    assert Scansion("a_rma^").divide_by(Scansion("_"))[0].scansion == "a_r"

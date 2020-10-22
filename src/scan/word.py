from src.utils import *
import warnings
# import joblib
from tqdm import tqdm
from src.scan.scansion import Scansion
from src.mqdq.dictionary import MqDqDictionary
from collections import defaultdict


class Word:
    """ Represents a single word in a text """

    USE_DICTIONARY = True  # set False for debug purposes only
    # see scan.py command line arguments description for the following variables:
    DIPHTHONG = True
    TOTAL_COUNT = 10
    AUTHOR_COUNT = 3

    MORPHEUS_DICT = defaultdict(set)
    MQDQ_DICT = MqDqDictionary()

    def __init__(self, word, next_word):
        """
        Initialize a new word object from a string
        :param word:        a word, which may comprise of lowercase alphabetical characters only
        :param next_word:   next word in the line, which is used to detect elisions
        """
        if next_word:
            self.next_word_prefix = next_word.__get_prefix()
        else:
            self.next_word_prefix = None

        # checking if the word has a postfix like que
        self.word = word  # word - postfix like que, if there is one
        self.scansions = self.__look_up()
        self.__check_if_has_postfix(self.next_word_prefix)
        if self.postfix != "":
            self.scansions = self.__look_up()
            self.next_word_prefix = multireplace(Word.PREFIX.match(self.postfix).group(),
                                            {"u": "v", "j": "i"})

        # workaround for cases when a word is completely unknown
        self.is_new = len(self.scansions) == 0
        if self.is_new:
            self.scansions.add(WordScansion(self.word, False))

        for scansion in self.scansions:
            self.__process(scansion, self.next_word_prefix)

    def __process(self, word_scansion, next_word_prefix):
        scansion = word_scansion.scansion
        scansion = self.__u_to_v(scansion)
        scansion = Word.DIPHTH_REGEX.sub(r"[\1]", scansion)  # marking all diphthongs
        scansion = Word.VOWELS_REGEX.sub(r"\1*", scansion)  # marking all vowels

        if next_word_prefix is not None:
            scansion = self.__elide(scansion, next_word_prefix)
        else:
            next_word_prefix = ""
        word_scansion.scansion = self.__mark_long_by_pos(scansion, next_word_prefix)

    def __check_if_has_postfix(self, next_word_prefix):
        """
        Check if the word ends with que. If it does, check if there is any scansion with long que
        in the dictionary (these are usually adverbs). If there are none, set self.postfix to "que^"
        :param word:        the word as passed to the initializer
        :param scansions:   the scansions as returned by self.__look_up()
        :param next_word:
        :return:
        """
        self.postfix = ""
        if self.word[-3:] not in ["que", "qve"] and self.word[-2:] not in ["ne", "ve", "ue"]:
            return
        for scansion in self.scansions:
            if not scansion.isMqDq:
                return
        # if the code reaches this point, it means that there is a short que at the end of the word
        # now it must be checked for elision and for being long by position
        if self.word[-3:] in ["que", "qve"]:
            self.postfix = "qve^"
            self.word = self.word[:-3]
        else:
            self.postfix = self.word[-2:] + "^"
            self.word = self.word[:-2]
        if next_word_prefix is None:
            return
        self.postfix = self.__elide(self.postfix, next_word_prefix)
        self.postfix = self.__mark_long_by_pos(self.postfix, next_word_prefix)
        return

    def __get_prefix(self):
        """
        Get the part of the word preceding the first vowel\diphthong. Before this function is
        called, self.scansion must be defined
        :return:
        """
        prefixes = set()
        non_mqdq = set()
        if self.word == "":
            prefixes.add(Word.PREFIX.match(self.postfix).group())
        else:
            for option in self.scansions:
                prefix = Word.PREFIX.match(option.scansion).group()
                if not option.isMqDq:
                    non_mqdq.add(prefix)
                prefixes.add(prefix)
        if len(prefixes) != 1:
            if len(non_mqdq) == 1:
                return non_mqdq.pop()
            else:
                warnings.warn("More than one possible prefix for word with the "
                              "following scansions: {}".format(self))
        return prefixes.pop()

    def is_mqdq_only(self, scansion):
        if self.is_new:
            return False
        for option in self.scansions:
            if Scansion(option.scansion + self.postfix).matches(scansion) and not option.isMqDq:
                return False
        return True

    def is_morpheus_only(self, scansion):
        pass

    def compare_scansions(self, scansion1, scansion2):
        """
        Compare two ways of scanning a word by calculating how many mqdq entries match the given
        scansions
        :param scansion1:
        :param scansion2:
        :return:
        """
        if (len(self.postfix) != 0) and ("(" not in self.postfix):
            scansion1 = Scansion(scansion1).pattern[:-1]
            scansion2 = Scansion(scansion2).pattern[:-1]
        key = multireplace(self.word, {"v": "u", "j": "i"})
        mqdq_entries = Word.MQDQ_DICT.look_up(key)
        s1_count, s2_count = 0, 0
        for entry in mqdq_entries.keys():
            mqdq_scansion = WordScansion(entry, True)
            self.__process(mqdq_scansion, self.next_word_prefix)
            matches1 = Scansion(mqdq_scansion.scansion).matches(Scansion(scansion1))
            matches2 = Scansion(mqdq_scansion.scansion).matches(Scansion(scansion2))
            if matches1 and not matches2:
                s1_count += sum(mqdq_entries[entry].values())
            elif not matches1 and matches2:
                s2_count += sum(mqdq_entries[entry].values())
        if s1_count + s2_count == 0:
            return 0.5, 0.5
        if s1_count == 0:
            s1_count = 1
            s2_count += 1
        elif s2_count == 0:
            s2_count = 1
            s1_count += 1
        return s1_count / (s1_count + s2_count), s2_count / (s1_count + s2_count)

    def macronize(self):
        return [Scansion(x.scansion + self.postfix) for x in self.scansions]

    def __look_up(self):
        """
        Look up self.word in the dictionaries. Return a set of WordScansion objects
        :return:
        """
        key = multireplace(self.word, {"v": "u", "j": "i"})
        scansions = {WordScansion(x, False) for x in Word.MORPHEUS_DICT[key]}
        hasMorpheusEntries = len(scansions) != 0
        mqdq_entry = Word.MQDQ_DICT.look_up(key)
        for scansion in mqdq_entry.keys():
            if sum([Scansion(scansion).matches(Scansion(x.scansion)) for x in scansions]) != 0:
                continue  # do not consider scansion options that already exist
                # TODO check how well this works
            if hasMorpheusEntries and (len(mqdq_entry[scansion].keys()) < Word.AUTHOR_COUNT or sum(
                    mqdq_entry[scansion].values()) < Word.TOTAL_COUNT or "*" in scansion):
                continue  # do not consider infrequent scansions
                # TODO should (or "*" in scansion) be added here
            if not hasMorpheusEntries:
                # make final syllable unknown
                scansion = re.sub("[\^_]([^\^_*[\]()]*)$", r"*\1", scansion)
            scansions.add(WordScansion(scansion, True))
        return scansions

    @staticmethod
    def load_mqdq_dict(filename):
        if not filename:
            return
        print("Loading MqDq dictionary...")
        with open(filename, "r") as file:
            Word.MQDQ_DICT.load(file)

    @staticmethod
    def load_morpheus_dict(filename):
        print("Loading Morpheus dictionary...")
        with open(filename, "r") as file:
            lines = file.readlines()
        for line in tqdm(lines):
            key, _, _, scansion = line.rstrip("\n").split("\t")
            key = multireplace(key.lower(), {"v": "u", "j": "i"})
            scansion = re.sub("(_\^|\^_)", r"*", scansion)
            scansion = Word.__u_to_v(scansion)
            scansion = Word.DIPHTH_REGEX.sub(r"[\1]", scansion)  # marking all diphthongs
            scansion = Word.VOWELS_REGEX.sub(r"\1*", scansion)  # marking all vowels
            if not DIPHTHONGS:
                scansion = re.sub("(\[ae\]|\[oe\])", "e_", scansion)
            Word.MORPHEUS_DICT[key].add(scansion.lower())
        # joblib.dump(Word.MORPHEUS_DICT, "../../data/morpheusdict")
        # Word.MORPHEUS_DICT = joblib.load("../../data/morpheusdict")

    def __str__(self):
        result = ""
        for scansion in self.scansions:
            result += "\t" + scansion.scansion
        return result

    @staticmethod
    def __elide(scansion, next_word_prefix):
        scansion += " " + next_word_prefix
        scansion = Word.ELIDE_VOWEL.sub(r"(\1)\2", scansion)
        scansion = Word.ELIDE_DIPHTHONG.sub(r"(\1)\2", scansion)
        return scansion[:-len(next_word_prefix) - 1]

    @staticmethod
    def __mark_long_by_pos(scansion, next_word_prefix):
        # scansion = Word.UNK_BY_POS.sub(r"*\1\2", scansion)
        scansion += next_word_prefix
        scansion = Word.LONG_BY_POS.sub(r"_\1", scansion)
        if len(next_word_prefix) > 0:
            scansion = scansion[:-len(next_word_prefix)]
        return scansion

    @staticmethod
    def __u_to_v(scansion):
        # then "u" follows "s", "g", or "q" - it is a consonant (technically, a
        # semivowel, but this is irrelevant for current purposes)
        # SOURCE: Allen and Greenough
        scansion = re.sub(r'([qg])u([' + VOWELS + '])', r'\1v\2', scansion)
        scansion = re.sub(r'ue$', r've', scansion)
        # u in the beginning of the word followed by a vowel is a consonant.
        return re.sub(r'(^|[' + VOWELS + '])u([' + VOWELS + '])', r'\1v\2', scansion)

Word.LONG_BY_POS = re.compile(r"[\^*](" + CLOSE_SYLLABLE + "|[" + CONSONANTS_NOT_H + "]{3})")

# vowels and diphthongs:
Word.DIPHTH_REGEX = re.compile("(" + "|".join(DIPHTHONGS) + r")(?![\]\^_*])")
# these are diphthongs according to Allen and Greenough with the last three being early latin
# diphthongs, which can alternatively be seen as a long vowel + a consonantal j or v
Word.VOWELS_REGEX = re.compile("(?<!\[)([" + VOWELS + r"])(?![\]\^_*])")

# elision
Word.ELIDE_VOWEL = re.compile("([" + VOWELS + "])[\^_*](m |m h| h| )$")
Word.ELIDE_DIPHTHONG = re.compile("\[(" + "|".join(DIPHTHONGS) + ")\](m | m h| h| )$")

# matches all consonants before the first vowel in a word
Word.PREFIX = re.compile("[^\[\^*_(]*(?=[" + VOWELS + "][\^_*(]|[\[(])")

# Word.DO_NOT_HAVE_PREFIX = ["omne"]
#  words that end in short ne or que, but for which ne or que is not a prefix


class WordScansion:

    def __init__(self, scansion, isMqDq):
        self.scansion = scansion
        self.isMqDq = isMqDq

""" # old assertions:
if __name__ == "__main__":
    Word.USE_DICTIONARY = False
    assert Word("non", None).scansions.pop() == "no*n"  # check one syllable word
    assert Word("faestum", None).scansions.pop() == "f[ae]stu*m"  # check diphthongs
    assert Word("puer", None).scansions.pop() == "pu*e*r"  # check two vowels in a row

    assert Word("omnes", None).scansions.pop() == "o_mne*s"  # check long by position
    assert Word("aflr", None).scansions.pop() == "a_flr"  # check three consonant long by pos
    assert Word("patris", None).scansions.pop() == "pa*tri*s"  # check muta cum liquida
    # check long by position across words:
    assert Word("non", Word("melior", None)).scansions.pop() == "no_n"
    # check long by position with double consonants:
    assert Word("non", Word("Xanthus", None)).scansions.pop() == "no_n"
    # check long by position with a diphthong
    assert Word("puellae", Word("Xanthi", None)).scansions.pop() == "pu*e_ll[ae]"
    # another corner case:
    assert Word("ullus", Word("aeque", None)).scansions.pop() == "u_llu*s"

    assert Word("bene", Word("usquam", None)).scansions.pop() == "be*n(e)"  # check simple elision
    assert Word("puellae", Word("ocium", None)).scansions.pop() == "pu*e_ll(ae)"  # check elision with a diphthong
    assert Word("nam", Word("et", None)).scansions.pop() == "n(a)m"  # check elision with m
    assert Word("mea", Word("haec", None)).scansions.pop() == "me*(a)"  # check elision with h
    assert Word("nam", Word("haec", None)).scansions.pop() == "n(a)m"  # check elision with m h

    assert Word("quam", None).scansions.pop() == "qva*m"  # check u to v conversion
    assert Word("nouam", None).scansions.pop() == "no*va*m"  # check intervocalic u to v conversion
    assert Word("extremumue", None).scansions.pop() == "e_xtre*mu_mve*"  # check ue to ve conversion

    assert Word.PREFIX.match("stringo").group() == "str"
"""
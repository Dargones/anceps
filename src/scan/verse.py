from src.scan.word import Word
from src.scan.scansion import Scansion
from src.utils import *
import math
from copy import deepcopy
import warnings
import re


class Verse:
    """ Represents a single verse of poetry """

    DICT = {}  # dictionary of manual scansion. If a verse is in the dictionary, the scansion
    # returned by scan() will be from this dictionary
    CUTOFF = 0.05  # see scan.py command line argument description

    def __init__(self, verse):
        """
        Initialize a new Verse object from a string
        :param verse:   a verse of poetry (may contain any symbols including punctuation signs)
        """
        self.unaltered = verse
        self.verse_key = Verse.get_verse_key(verse)
        verse = re.sub(r"([^a-z])", " ", verse.lower()).rstrip(" ").lstrip(" ")
        verse = re.sub(" +", " ", verse).split(" ")
        self.words = [Word(verse[-1], None)]
        for i in range(len(verse) - 2, -1, -1):  # in reverse order because of how elision works
            self.words.insert(0, Word(verse[i], self.words[0]))
        self.__macronize()
        self.flags = []

    def __macronize(self):
        """
        Populate self.macronizations, with all possible ways the line can be macronized
        :return:
        """
        self.macronizations = [Scansion("")]
        for i, word in enumerate(self.words):
            new_macrons = []
            for exist in self.macronizations:
                for macrons in word.macronize():
                    new_macrons.append(exist + macrons)
            self.macronizations = new_macrons

    def score_scansions(self, scansion1, scansion2):
        """
        Take two scansions a and b.
        For each word i compute p(i_a) and p(i_b),
        probabilities that word i would be scanned as in a and b respectively.

        Compute p(a) as the product of p(i_a)'s and p(b) as the product of p(i_b)'s

        Return the most likely of the two scansions and
        either p(a)/(p(a) + p(b)) or p(b) / (p(a) + p(b)), whichever is greater.

        Note that the actual computation is somewhat simplified.

        :param scansion1: the first scansion (a)
        :param scansion2: the second scansion (b)
        :return:          a Scansion (either a or b), a float that lies in (0.5, 1)
        """
        p_1 = 1
        p_2 = 1
        word_scansions_1 = scansion1.scansion.lstrip(" ").rstrip(" ").split(" ")
        word_scansions_2 = scansion2.scansion.lstrip(" ").rstrip(" ").split(" ")
        for i, word in enumerate(self.words):
            p_word_1, _ = word.compare_scansions(word_scansions_1[i], word_scansions_2[i])
            p_1 *= p_word_1
            p_2 *= (1 - p_word_1)
        if p_1 > p_2:
            return scansion1, p_1/(p_1 + p_2)
        return scansion2, p_2 / (p_1 + p_2)

    def update_flags(self, scansion):
        """
        Given that the scansion chosen corresponds to particular way the words are macronized,
        record any irregularities in word macronizations in self.flags
        :param scansion:    a scansion (word macronizations separated by " ")
        :return:            None
        """
        for i, macrons in enumerate(scansion.scansion.lstrip(" ").rstrip(" ").split(" ")):
            if self.words[i].is_mqdq_only(Scansion(macrons)):
                self.flags.append("Mqdq only scansion: " + macrons)
            elif self.words[i].is_morpheus_only(Scansion(macrons)):
                self.flags.append("Morpheus only scansion: " + macrons)
            if self.words[i].is_new:
                self.flags.append("A previuosly unencountered word: " + macrons)

    def scan(self, meter, precise=False, interactive=True, add_failed=False):
        """
        Return the scansion for this line or None if correct scansion cannot be determined
        :param meter:       the meter to use as a constraint for the scansion
        :param precise:     whether to allow anceps symbols in the final scansion
        :param interactive: whether to prompt the user to select the correct scansion when
                            several options are available
        :param add_failed:  If True, the lines that the program failed to scan will be added
                            to Verse.DICT, so that they can later be scanned manually in the
                            manual file
        :return:            Scansion object or None
        """
        options = set()
        for i, macronization in enumerate(self.macronizations):
            meter_patterns = meter.get_matching_scansions(macronization, precise)
            for pattern in meter_patterns:
                scansion = macronization.apply_mask(pattern)
                options.add(scansion)
                # TODO consider a very rare but theoretically possible case, when to scansions are
                # the same, but words are macronized diffrently

        manual_options = self.__get_manual_options(meter, precise)
        if len(options) > 1 and len(manual_options) != 1:
            options = self.__resolve(options, interactive)
        return self.__finish_scansion(options, manual_options, add_failed)

    def __resolve_automatically(self, options):
        """
        Attempt to choose a scansion option based on word scansion frequency
        :param options:
        :return:
        """
        options_copy = deepcopy(options)
        best_option = options_copy.pop()
        while options_copy:
            new_option = options_copy.pop()
            best_option, score = self.score_scansions(best_option, new_option)
            if (1 - score) > Verse.CUTOFF:
                return options
        self.flags.append("Resolved Automatically")
        return {best_option, }

    def __resolve(self, options, interactive):
        """
        Prompt the user to choose a correct scansion among several options
        :param options:
        :return:
        """
        resolved = self.__resolve_automatically(options)
        if len(resolved) == 1:
            return resolved
        if not interactive:
            return options
        print("\nPlease choose a scansion option manually for verse:\n" + self.unaltered)
        scansions = list(options)
        for i, scansion in enumerate(scansions):
            print("\t" + str(i) + ") " + str(scansion))
        print("\t" + str(i + 1) + ") None of the above (scansion will be marked as failed)")
        answer = input()
        while (not answer.isdigit()) or (int(answer) < 0) or (int(answer) > i + 1):
            print("Please enter a valid response")
            answer = input()
        if int(answer) == i + 1:
            return options
        Verse.DICT[self.verse_key] = {"scansion": scansions[int(answer)], "comment": ""}
        return {scansions[int(answer)], }

    def __get_manual_options(self, meter, precise):
        """
        Look up the verse in Verse.DICT and return the scansions stored there
        :param meter:       the meter to scan the verse with
        :param precise:     whether to allow anceps symbols in the final scansion
        :return:            a set of Scansion objects (can be empty)
        """
        manual_options = set()
        if self.verse_key not in Verse.DICT:
            return manual_options
        line_scansion = Verse.DICT[self.verse_key]["scansion"]
        meter_patterns = meter.get_matching_scansions(line_scansion, precise)
        for pattern in meter_patterns:
            manual_options.add(line_scansion.apply_mask(pattern))
        if len(manual_options) != 1:
            warnings.warn("Scansion for line " + self.verse_key + " specified manually is "
                                                                  "not acceptable")
        return manual_options

    def __finish_scansion(self, auto_options, manual_options, add_failed):
        """
        Make a decision as to how scan the line based on the scansion created automatically
        and the scansion specified manually (the latter take precedence). Record info about the
        particular scansion chosen and the way it was chosen in self.flags and self.scansion_method
        :param auto_options:    the scansions created automatically (a dictionary)
        :param manual_options:  the scansions created manually (a set)
        :param add_failed:      If True, the lines that the program failed to scan will be added
                                to Verse.DICT, so that they can later be scanned manually in the
                                manual file
        :return:
        """
        if self.verse_key not in Verse.DICT and len(manual_options) != 1:
            if len(auto_options) == 1:
                self.scansion_method = "automatic"
                scansion = auto_options.pop()
                self.update_flags(scansion)
                return scansion
            if add_failed:
                Verse.DICT[self.verse_key] = {"scansion": self.unaltered, "comment": "toBeScanned"}
            if len(auto_options) == 0:
                self.scansion_method = "failed"
            else:
                self.scansion_method = "failed (many options)"
            return None
        if len(manual_options) != 1:
            self.scansion_method = "failed"
            return None
        scansion = manual_options.pop()
        if len(auto_options) == 0:
            self.scansion_method = "manual"
        elif len(auto_options) == 1:
            if scansion in auto_options:
                self.scansion_method = "automatic (verified)"
                self.update_flags(scansion)
            else:
                self.scansion_method = "manual (corrected)"
        elif len(auto_options) > 1:
            if scansion in auto_options:
                self.scansion_method = "semi-automatic"
                self.update_flags(scansion)
            else:
                self.scansion_method = "manual (corrected)"
        return scansion

    @staticmethod
    def get_verse_key(verse):
        """
        Return a key by which the verse can be identified. A key consists of lowercase
        alphabetical characters only with "j" being replacedwith "i" and "v" with "u"
        :param verse:   the verse as it appears in text
        :return:        a string
        """
        key = re.sub(r"( *[^a-zA-Z] *|[ ]+)", "", verse).lower()
        return multireplace(key, {"j": "i", "v": "u"})

    @staticmethod
    def read_manual_file(filename):
        """
        Populate Verse.DICT with manually made scansions
        :param filename:    the name of the file from which to extract the manual scansions
        :return:            None
        """
        if not filename:
            return
        print("Loading manual scansions...")
        with open(filename, "r") as file:
            lines = file.readlines()
        lines = [line.rstrip("\n").split("\t") for line in lines]
        for line in lines:
            verse_key = Verse.get_verse_key(line[0])
            scansion = re.sub(r"([^a-z_\^*\[\]()])", " ", line[0].lower()).rstrip(" ").lstrip(" ")
            scansion = Scansion(re.sub(" +", " ", scansion))
            if len(line) == 1:
                Verse.DICT[verse_key] = {"scansion": scansion, "comment": ""}
            else:
                Verse.DICT[verse_key] = {"scansion": scansion, "comment": line[1]}

    @staticmethod
    def save_manual_file(filename):
        """
        Save Verse.DICT to file
        :param filename:    the name of the file to which to write the data
        :return:            None
        """
        if not filename:
            return
        with open(filename, "w") as file:
            for value in Verse.DICT.values():
                file.write(str(value["scansion"]) + "\t" + value["comment"] + "\n")

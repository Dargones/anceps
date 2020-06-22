import re
from itertools import product


# consonants, vowels, and diphthongs:
MUTES = "bpdtcgf"
LIQUIDS = "rl"
SINGLE_CONSONANTS = MUTES + LIQUIDS + "mnkqfhsjv"
DOUBLE_CONSONANTS = "xz"
CONSONANTS = SINGLE_CONSONANTS + DOUBLE_CONSONANTS
CONSONANTS_NOT_H = SINGLE_CONSONANTS.replace("h", "") + DOUBLE_CONSONANTS
VOWELS = "aeiouy"
DIPHTHONGS = ["ae", "au", "ei", "oe"]  # TODO: should ui be here?

# building regex for marking vowels as long by position:
MCL = [''.join(x) for x in product(MUTES, LIQUIDS)]  # muta cum liquida
SHORT_COMBINATIONS = [x + 'h' for x in SINGLE_CONSONANTS] + ["qv", "sv", "gv"] + MCL
# qv, sv, and gv are added because Allen and Greenough say in 11.c.3 that in rules for quantity
# the "apparently consonantal" u is not counted as consonant in these cases

CLOSE_SYLLABLE = '|'.join([''.join(x) for x in product(CONSONANTS, CONSONANTS)
                  if ''.join(x) not in SHORT_COMBINATIONS]) + '|' + \
                      '|'.join(DOUBLE_CONSONANTS)


def multireplace(string, replacements):
    """
    Given a string and a replacement map, it returns the replaced string.
    :param str string: string to execute replacements on
    :param dict replacements: replacement dictionary {value to find: value to
    replace}
    :rtype str:
    :original source: Bor González Usach (GitHub snippets)
    """
    # Place longer ones first to keep shorter substrings from matching where the
    # longer ones should take place. For instance given the replacements
    # {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc', it should produce
    # 'hey ABC' and not 'hey ABc'
    substrs = sorted(replacements, key=len, reverse=True)

    # Create a big OR regex that matches any of the substrings to replace
    regexp = re.compile("|".join(map(re.escape, substrs)))

    # For each match, look up the new string in the replacements
    return regexp.sub(lambda match: replacements[match.group(0)], string)
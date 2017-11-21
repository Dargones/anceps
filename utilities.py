import re

# ------------------- Paths and Directories ------------------------------------
BASEDIR = '/Users/alexanderfedchin/PycharmProjects/sproj/'
OUTDIR = BASEDIR + 'output/'
INDIR = BASEDIR + 'input/'
# PATH_TO_TEXT = INDIR + 'aeneid.txt'
# PATH_TO_TEXT = INDIR + 'ovid.txt'
# PATH_TO_TEXT = INDIR + 'eclogues1-5.txt'
PATH_TO_TEXT = INDIR + 'query_text.csv'
PATH_TO_NEW_FORMAT = OUTDIR + 'aeneid_scanned.co.txt'
PATH_TO_RESULT = OUTDIR + 'aeneid_scanned.txt'
# PATH_TO_RESULT = OUTDIR + 'metamorphoses_scanned.txt'
# PATH_TO_TEST = INDIR + 'aeneid_test.txt'
PATH_TO_TEST = INDIR + 'query_result.csv'
PATH_TO_AUTO_DICT = OUTDIR + 'dict_vergil.txt'
# PATH_TO_AUTO_DICT2 = OUTDIR + 'dict_ovid.txt'
PATH_TO_DICT = INDIR + 'latin-analyses.txt'

# ------------------- For Reading already Scanned Verses -----------------------
SHORT_MARKED = 'ĂăĕĬĭŎŏŭŷ'
LONG_MARKED = 'ĀāēĪīōŪūȳ'

# ------------------- Info about Syllables and Vowel Lengths -------------------

LONG = '_'
SHORT = '^'
UNK = '?'
ANCEPS = 'X'
DUMMY_TOKEN = 'Y'
PSEUDO_CONSONANT = 'w'  # this is put between prefix and root to prevent elision
CONSONANTS = 'bcdfghklmnpqrstvjxz' + PSEUDO_CONSONANT
LONG_CONSONANTS = ['z', 'x']

# muta cum liquida
SHORT_COMBINATIONS = '(pl|bl|tl|dl|cl|gl|fl|pr|br|tr|dr|cr|gr|fr'
# because v is a semivowel
SHORT_COMBINATIONS += '|qv|sv|gv'
# these were found empirically or on other sites
SHORT_COMBINATIONS += '|ns|dh|rh|nh|ch|sh|ph|th|mh)'

VOWELS = 'aeiouy'
# these are diphthongs according to Allen and Greenough
DIPHTHONGS = 'ae|au|ei|eu|oe|ui'
# early latin diphthong (same source)
DIPHTHONGS += '|ai|oi|ou'
# these are diphthongs in a sense that the vowel is always long in these cases
SYLLAB = r'('+DIPHTHONGS+'|['+VOWELS+'])'

# ------------------- The Definitions of Meter Patterns ------------------------

SPONDEE = [[LONG, LONG]]
DACTYL = [[LONG, SHORT, SHORT]]
H_SIXTH_FOOT = [[LONG, ANCEPS]]
H_FOOT = [[SPONDEE], [DACTYL]]
HEXAMETER = [[[H_FOOT, H_FOOT, H_FOOT, H_FOOT, H_FOOT, H_SIXTH_FOOT]]]

# ------------------- Morphology -----------------------------------------------

# These are prefixes that are very likely to be prefixes and not parts of some
# roots. Id est, this list is very subjective.
PREFIXES = '(circum|post|ante|infra|inter|con|com|juxta|extra|dis|intra|intro|' \
           'preter|quasi|retro|trans|super|ultra)'


# NOTE: these are some of the suffixes and endings from Allen and Greenough

DEC_1ST = [('a', [UNK]), ('ae', [LONG]), ('am', [UNK]), ('a', [LONG]),
                    ('as', [LONG]), ('arum', [LONG, UNK]), ('is', [LONG])]

DEC_2ND = [('us', [UNK]), ('i', [LONG]), ('o', [LONG]), ('um', [UNK]),
                    ('e', [UNK]), ('orum', [LONG, UNK]), ('is', [LONG]),
                    ('os', [LONG]), ('i', [UNK]), ('a', [UNK])]

DEC_3RD = [('is', [UNK]), ('i', [LONG]), ('e', [UNK]), ('em', [UNK]),
                    ('es', [LONG]), ('um', [UNK]), ('ibus', [UNK, UNK]),
                    ('a', [UNK]), ('ia', [UNK, UNK]), ('ium', [UNK, UNK])]

DEC_4TH = [('us', [UNK]), ('us', [LONG]), ('ui', [UNK, LONG]), ('um', [UNK]),
                    ('u', [LONG]), ('uum', [UNK, UNK]), ('ibus', [UNK, UNK]),
                    ('ua', [UNK, UNK])]

DEC_5TH = [('es', [LONG]), ('e', [LONG]), ('ei', [UNK, LONG]), ('em', [UNK]),
                    ('erum', [LONG, UNK]), ('ebus', [LONG, UNK])]

CONJ_PR_ACT_1ST = [('o', [LONG])]

CONJ_PR_ACT_1ST_2 = [('m', [])]

CONJ_PR_PASS_1ST = [('or', [UNK])]

CONJ_PR_PASS_1ST_2 = [('r', [])]

CONJ_PR_ACT = [('s', []), ('t', []), ('nt', []), ('mus', [UNK]),
               ('tis', [UNK])]

CONJ_PR_ACT_2 = [('is', [UNK]), ('it', [UNK]), ('unt', [UNK]), ('imus', [UNK, UNK]),
               ('itis', [UNK, UNK])]

CONJ_PR_PASS = [('ris', [UNK]), ('tur', [UNK]), ('mur', [UNK]),
                ('mini', [UNK, LONG]), ('ntur', [UNK]), ('re', [UNK])]

CONJ_PR_PASS_2 = [('eris', [UNK, UNK]), ('itur', [UNK, UNK]), ('imur', [UNK, UNK]),
                ('imini', [UNK, UNK, LONG]), ('untur', [UNK, UNK]), ('ere', [UNK, UNK])]

CONJ_HI_ACT = [('i', [LONG]), ('isti', [UNK, LONG]), ('it', [UNK]),
               ('imus', [UNK, UNK]), ('istis', [UNK, UNK]),
               ('erunt', [LONG, UNK]), ('ere', [LONG, UNK])]

IMPERATIVE = [('to', [LONG]), ('te', [UNK]), ('tote', [LONG, UNK]), ('nto', [LONG]),
              ('re', [UNK]), ('tor', [UNK]), ('mini', [UNK, LONG]), ('ntor', [UNK])]

IMERATIVE_2 = [('', [])]

INF = [('re', [UNK]), ('ri', [LONG])]

PASS_INF = [('isse', [UNK, UNK])]

CONJ_1ST = [[(CONJ_PR_ACT_1ST, '', []), (CONJ_PR_ACT, 'a', [UNK]),
             (CONJ_PR_ACT, 'aba', [LONG, UNK]), (CONJ_PR_ACT_1ST_2, 'aba', [LONG, UNK]),
             (CONJ_PR_ACT_1ST, 'ab', [LONG]), (CONJ_PR_ACT_2, 'ab', [LONG]),
             (CONJ_PR_ACT_1ST_2, 'e', [UNK]), (CONJ_PR_ACT, 'e', [UNK]),
             (CONJ_PR_ACT_1ST_2, 'are', [LONG, UNK]), (CONJ_PR_ACT, 'are', [LONG, UNK]),
             (IMPERATIVE, 'a', [LONG]), (IMERATIVE_2, 'a', [UNK]), (INF, 'a', [LONG]),
             (CONJ_PR_PASS_1ST, '', []), (CONJ_PR_PASS, 'a', [UNK]),
             (CONJ_PR_PASS_1ST_2, 'aba', [LONG, UNK]), (CONJ_PR_PASS, 'aba', [LONG, UNK]),
             (CONJ_PR_PASS_1ST, 'ab', [LONG]), (CONJ_PR_PASS_2, 'ab', [LONG]),
             (CONJ_PR_PASS_1ST_2, 'e', [UNK]), (CONJ_PR_PASS, 'e', [UNK]),
             (CONJ_PR_PASS_1ST_2, 'are', [LONG, UNK]), (CONJ_PR_PASS, 'are', [LONG, UNK])]]

CONJ_PASS = [[(CONJ_HI_ACT, '', []),
                  (CONJ_PR_ACT_1ST_2, 'era', [UNK, UNK]), (CONJ_PR_ACT, 'era', [UNK, UNK]),
                  (CONJ_PR_ACT_1ST, 'er', [UNK]), (CONJ_PR_ACT, 'eri', [UNK, UNK]),
                  (CONJ_PR_ACT_1ST_2, 'eri', [UNK, UNK]), (CONJ_PR_ACT, 'eri', [UNK, UNK]),
                  (CONJ_PR_ACT_1ST_2, 'isse', [UNK, UNK]), (CONJ_PR_ACT, 'isse', [UNK, UNK]),
                  (PASS_INF, '', [])]]

CONJ_2ND = [[(CONJ_PR_ACT_1ST, 'e', [UNK]), (CONJ_PR_ACT, 'e', [UNK]),
             (CONJ_PR_ACT, 'eba', [LONG, UNK]), (CONJ_PR_ACT_1ST_2, 'eba', [LONG, UNK]),
             (CONJ_PR_ACT_1ST, 'eb', [LONG]), (CONJ_PR_ACT_2, 'eb', [LONG]),
             (CONJ_PR_ACT_1ST_2, 'ea', [UNK, UNK]), (CONJ_PR_ACT, 'ea', [UNK, UNK]),
             (CONJ_PR_ACT_1ST_2, 'ere', [LONG, UNK]), (CONJ_PR_ACT, 'ere', [LONG, UNK]),
             (IMPERATIVE, 'e', [UNK]), (IMERATIVE_2, 'e', [UNK]), (INF, 'e', [LONG]),
             (CONJ_PR_PASS_1ST, 'e', [UNK]), (CONJ_PR_PASS, 'e', [UNK]),
             (CONJ_PR_PASS_1ST_2, 'eba', [LONG, UNK]), (CONJ_PR_PASS, 'eba', [LONG, UNK]),
             (CONJ_PR_PASS_1ST, 'eb', [LONG]), (CONJ_PR_PASS_2, 'eb', [LONG]),
             (CONJ_PR_PASS_1ST_2, 'ea', [UNK]), (CONJ_PR_PASS, 'ea', [UNK]),
             (CONJ_PR_PASS_1ST_2, 'ere', [LONG, UNK]), (CONJ_PR_PASS, 'ere', [LONG, UNK])]]

CONJ_3RD = [[(CONJ_PR_ACT_1ST, '', []), (CONJ_PR_ACT_2, '', []),
             (CONJ_PR_ACT, 'eba', [LONG, UNK]), (CONJ_PR_ACT_1ST_2, 'eba', [LONG, UNK]),
             (CONJ_PR_ACT_1ST_2, 'a', [UNK]), (CONJ_PR_ACT, 'e', [UNK]),
             (CONJ_PR_ACT_1ST_2, 'a', [UNK]), (CONJ_PR_ACT, 'a', [UNK]),
             (CONJ_PR_ACT_1ST_2, 'ere', [UNK, UNK]), (CONJ_PR_ACT, 'ere', [UNK, UNK]),
             (IMPERATIVE, 'i', [UNK]), (IMERATIVE_2, 'e', [UNK]), (INF, 'e', [LONG]),
             (CONJ_PR_PASS_1ST, '', []), (CONJ_PR_PASS_2, '', []),
             (CONJ_PR_PASS_1ST_2, 'eba', [LONG, UNK]), (CONJ_PR_PASS, 'eba', [LONG, UNK]),
             (CONJ_PR_PASS_1ST_2, 'a', [UNK]), (CONJ_PR_PASS, 'e', [UNK]),
             (CONJ_PR_PASS_1ST_2, 'a', [UNK]), (CONJ_PR_PASS, 'a', [UNK]),
             (CONJ_PR_PASS_1ST_2, 'ere', [UNK, UNK]), (CONJ_PR_PASS, 'ere', [UNK, UNK])]]

# TODO: audiunt
CONJ_4TH = [[(CONJ_PR_ACT_1ST, 'i', [UNK]), (CONJ_PR_ACT, 'i', [UNK]),
             (CONJ_PR_ACT, 'ieba', [UNK, LONG, UNK]), (CONJ_PR_ACT_1ST_2, 'ieba', [UNK, LONG, UNK]),
             (CONJ_PR_ACT_1ST_2, 'ia', [UNK, UNK]), (CONJ_PR_ACT, 'ie', [UNK, UNK]),
             (CONJ_PR_ACT_1ST_2, 'ia', [UNK, UNK]), (CONJ_PR_ACT, 'ia', [UNK, UNK]),
             (CONJ_PR_ACT_1ST_2, 'ire', [LONG, UNK]), (CONJ_PR_ACT, 'ire', [LONG, UNK]),
             (IMPERATIVE, 'i', [LONG]), (IMERATIVE_2, 'i', [LONG]), (INF, 'i', [LONG]),
             (CONJ_PR_PASS_1ST, 'i', [UNK]), (CONJ_PR_PASS, 'i', [UNK]),
             (CONJ_PR_PASS_1ST_2, 'ieba', [UNK, LONG, UNK]), (CONJ_PR_PASS, 'ieba', [UNK, LONG, UNK]),
             (CONJ_PR_PASS_1ST, 'ia', [UNK, UNK]), (CONJ_PR_PASS, 'ie', [UNK, UNK]),
             (CONJ_PR_PASS_1ST_2, 'ia', [UNK, UNK]), (CONJ_PR_PASS, 'ia', [UNK, UNK]),
             (CONJ_PR_PASS_1ST_2, 'ire', [LONG, UNK]), (CONJ_PR_PASS, 'ire', [LONG, UNK])]]

NOUNS = [[(DEC_1ST, '', [])], [(DEC_2ND, '', [])], [(DEC_3RD, '', [])],
         [(DEC_4TH, '', [])], [(DEC_5TH, '', [])]]

ADJECTIVES = [[(DEC_1ST, '', []), (DEC_2ND, '', []), (DEC_3RD, '', [])]]

ALL = NOUNS + ADJECTIVES + CONJ_1ST + CONJ_2ND + CONJ_3RD + CONJ_4TH + CONJ_PASS
# These are different groups in which the algorithm can classify the words.
# ALL[i] contains a list of tuples, where every tuple has a form:
# ('suffix_ending', [meter_pattern])

ENDINGS = {}  # Endings['ending'] = list of groups in which this ending can
# be found. See below how ENDINGS is constructed


# ------------------- Various Functions ----------------------------------------


def merge_lists(list1, list2, maximize=True, problem=UNK):
    """
    Take and merge two lists. Lists should only have UNK, ANCEPS, LONG, SHORTM
    Merging mechanism depends on the value of maximize. If maximize == True,
    then whenever at a certain position the longitude is known for one of the
    lists, but unknown in the other, the resulting value will be that in the
    first list, otherwise - that in the second. If both lists have a value
    different from UNK at some position, and this values are not equal,
    the result will have UNK at this position
    :param list1:
    :param list2:
    :param maximize:
    :param problem:  character that will be used when there is a conflict
    :return:
    """
    result = []
    if list1 is None:
        return list2
    elif list2 is None:
        return list1
    if len(list2) < len(list1):
        return merge_lists(list2, list1)
    i = 0
    while i < len(list1):
        if list1[i] == UNK:
            if maximize:
                result.append(list2[i])
            else:
                result.append(UNK)
        elif list2[i] == UNK:
            if maximize:
                result.append(list1[i])
            else:
                result.append(UNK)
        elif list1[i] == list2[i]:
            result.append(list2[i])
        else:
            result.append(problem)
        i += 1
    while i < len(list2):
        result.append(list2[i])
        i += 1
    return result


def dummy_to_unk(l):
    """
    Replace all occurances of DUMMY_TOKEN in the list with UNKNOWN
    :param l:
    :return:
    """
    for i in range(len(l)):
        if l[i] == DUMMY_TOKEN:
            l[i] = UNK
    return l


def i_or_j(word):
    """
    Take a word and replace all "i" that should be read as consonants with "j"
    :param word:    a word that can only contain latin lowercase letters
    :return:        modified word
    """
    vowels = list(re.findall(r'['+VOWELS+']', word))

    # if there are no "i" in the word, there are no problems
    if 'i' not in vowels:
        return word

    # if "i" is the only potential vowel in a word -> it is a vowel
    # SOURCE: http://www.logical.ai/arma/
    if len(vowels) == 1:
        return word

    # initial and intervocalic 'i' is always consonant
    # SOURCE: http://www.logical.ai/arma/ and all around the web
    # TODO: There still are exceptions. Consider "Io".
    return re.sub('(^|['+VOWELS+'])i(['+VOWELS+'])', r'\1j\2', word)


def u_or_v(word):
    """
    Take a word and replace all "u" that should be read as consonants with "v"
    :param word:    a word that can only contain latin lowercase letters
    :return:        modified word
    """

    # then "u" follows "s", "g", or "q" - it is a consonant (technically, a
    # semivowel, but this is irrelevant for current purposes)
    # SOURCE: Allen and Greenough
    word = re.sub(r'([qg])u(['+VOWELS+'])', r'\1v\2', word)

    # u in the beginning of the word followed by a vowel is a consonant.
    return re.sub(r'^u([' + VOWELS + '])', r'v\1', word)


# ------------------- Construction of teh ENDINGS dictionary -------------------


for i in range(len(ALL)):
    newgroup = {}
    for suffix_group in ALL[i]:
        for ending in suffix_group[0]:
            affix = suffix_group[1] + ending[0]
            affix_meter = suffix_group[2] + ending[1]
            if affix not in newgroup:
                newgroup[affix] = affix_meter
            else:
                newgroup[affix] = merge_lists(affix_meter,
                                              newgroup[affix], False)
            if affix not in ENDINGS:
                ENDINGS[affix] = [i]
            elif newgroup not in ENDINGS[affix]:
                ENDINGS[affix].append(i)
    ALL[i] = newgroup

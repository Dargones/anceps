import re

PERSEUS_DATA_FILE_NAME = '/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/diogenes/latin-analyses.txt'
LEWIS_SHORT_FILE_NAME = '/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/diogenes/1999.04.0059.xml'


# ------------------- Info about Syllables and Vowel Lengths -------------------

LONG = '_'
SHORT = '^'
UNK = '&'
ANCEPS = 'X'
DUMMY_TOKEN = 'Y'
PSEUDO_CONSONANT = 'w'  # this is put between prefix and root to prevent elision
CONSONANTS = 'bcdfghklmnpqrstvjxz' + PSEUDO_CONSONANT
LONG_CONSONANTS = ['z','x']

# muta cum liquida
MCL = '(pl|bl|tl|dl|cl|gl|fl|pr|br|tr|dr|cr|gr|fr|qv|sv|gv)'
SHORT_COMBINATIONS = MCL[:-1] + '|dh|rh|nh|ch|sh|ph|th|mh|lh|kh|gh|fh|bh)'

VOWELS = 'aeiouy'
SHORT_BY_NATURE = 'aey'  # This will be used as a last resort
# SOURCE: Gildersleeve and Lodge
LONG_BY_NATURE = 'oiu'
# these are diphthongs according to Allen and Greenough
DIPHTHONGS = 'ae|au|ei|eu|oe|ui'
# early latin diphthongs (same source)
DIPHTHONGS += '|ai|oi|ou'
# these are diphthongs in a sense that the vowel is always long in these cases
SYLLAB = r'('+DIPHTHONGS+'|['+VOWELS+'])'

# ------------------- The Definitions of Meter Patterns ------------------------

SPONDEE = [[LONG, LONG]]
DACTYL = [[LONG, SHORT, SHORT]]
H_SIXTH_FOOT = [[LONG, ANCEPS]]
H_FOOT = [[SPONDEE], [DACTYL]]
HEXAMETER = [[[H_FOOT, H_FOOT, H_FOOT, H_FOOT, H_FOOT, H_SIXTH_FOOT]]]
PENTAMETER = [[[H_FOOT, H_FOOT, LONG, H_FOOT, H_FOOT, LONG]]]

ANC_SYL = [[ANCEPS], [SHORT, SHORT]]
LONG_SYL = [[LONG], [SHORT, SHORT]]
YAMB_METROM = [[ANC_SYL, LONG_SYL, SHORT, LONG_SYL]]
YAMB_METRON_LAST = [[ANC_SYL, LONG_SYL, SHORT, ANCEPS]]
YAMB_METRON_LAST_CORRER = [[ANC_SYL, LONG_SYL, SHORT, ANC_SYL]]
YAMB_METROM_LOOSE = [[ANC_SYL, LONG_SYL, ANC_SYL, LONG_SYL]]

TRIMETER = [[[YAMB_METROM, YAMB_METROM, YAMB_METRON_LAST]]]
CORRER_TRIMETER = [[[YAMB_METROM, YAMB_METROM, YAMB_METRON_LAST_CORRER]]]
LOOSE_TRIMETER = [[[YAMB_METROM_LOOSE, YAMB_METROM_LOOSE, YAMB_METRON_LAST]]]


# ------------------- Morphology -----------------------------------------------

# These are prefixes that are very likely to be prefixes and not parts of some
# roots. Id est, this list is very subjective.
PREFIXES = '(circum|post|ante|infra|inter|con|com|juxta|extra|dis|intro|' \
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


def decide_on_length(vowel, follow):
    """
    decide whether a vowel/diphthong 'vowel' followed by consonants 'follow'
    will be long
    :param vowel:    something from SYLLAB
    :param follow:   a string consisting of consonants or LONG and SHORT tokens
                     that mark the length of the vowel explicitly
    :return:
    """
    if SHORT in follow:
        return SHORT
    if len(follow) > 2 and follow[1] == 'h':
        follow = follow[:1] + follow[2:]
    if (len(vowel) > 1) or (len(follow) > 2) or ((len(follow) == 2) and (
                re.match(SHORT_COMBINATIONS, follow) is None)) or (
                follow in LONG_CONSONANTS) or (LONG in follow):
        return LONG
    return UNK


def stem_it(word):
    """
    Strip off all the endings
    :param word:
    :return: the stem of teh word
    """
    i = len(word) - 1
    end = ENDINGS
    while (i > 0) and word[i] in end:
        end = end[word[i]]
        i -= 1
    return word[:i+1]


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
    regexp = re.compile('|'.join(map(re.escape, substrs)))

    # For each match, look up the new string in the replacements
    return regexp.sub(lambda match: replacements[match.group(0)], string)


def merge_lists(list1, list2, maximize=True, problem=UNK):
    """
    Take and merge two lists. Lists should only have UNK, ANCEPS, LONG, SHORT
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


def meters_are_equal(m1, m2, allowed=ANCEPS):
    """
    returns True if the two meter patterns much each other
    :param m1: the first meter pattern
    :param m2: the second meter patter
    :param allowed: a char that matches everything else
    :return:
    """
    if len(m1) != len(m2):
        return False
    i = 0
    while i < len(m1):
        if m1[i] != m2[i] and m1[i] != allowed and m2[i] != allowed:
            return False
        i += 1
    return True


def u_or_v(word):
    """
    Take a word and replace all "u" that should be read as consonants with "v"
    :param word:    a word that can only contain latin lowercase letters
    :return:        modified word
    """
    # then "u" follows "s", "g", or "q" - it is a consonant (technically, a
    # semivowel, but this is irrelevant for current purposes)
    # SOURCE: Allen and Greenough
    word = re.sub(r'([qsg])u([' + VOWELS + '])', r'\1v\2', word)

    word = re.sub(r'ue$', r've', word)

    # u in the beginning of the word followed by a vowel is a consonant.
    return re.sub(r'(^|['+VOWELS+'])u([' + VOWELS + '])', r'\1v\2', word)


# ------------------- Construction of the ENDINGS dictionary -------------------


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

ENDINGS_OLD = ENDINGS
ENDINGS = {}
for end in ENDINGS_OLD:
    current = ENDINGS
    i = len(end) - 1
    while i >= 0:
        if end[i] not in current:
            current[end[i]] = {}
        current = current[end[i]]
        i -= 1

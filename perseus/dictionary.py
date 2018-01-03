from utilities import *

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

BASE_DIR = '/Users/alexanderfedchin/PycharmProjects/sproj/Scansion_project/perseus/'
LEWIS_SHORT_FILE_NAME = BASE_DIR + '1999.04.0059.xml'
PERSEUS_DATA_FILE_NAME = BASE_DIR + 'latin-analyses.txt'
OUTPUT_FILE_NAME = BASE_DIR + 'final_dict.txt'

D_1_U = {'a': [UNK], 'ae': [LONG], 'am': [UNK], 'as': [LONG],
           'arum': [LONG, UNK], 'is': [LONG]}

D_1_E_ = {'e': [LONG], 'ae': [LONG], 'es': [LONG], 'en': [LONG],
              'as': [LONG],'arum': [LONG, UNK], 'is': [LONG], 'am': [UNK]}

D_1_A_S = {'as': [LONG], 'ae': [LONG], 'a': [LONG], 'an': [LONG],
              'arum': [LONG, UNK], 'is': [LONG]}

D_1_E_S = {'es': [LONG], 'ae': [LONG], 'a': [UNK], 'en': [LONG],
              'arum': [LONG, UNK], 'is': [LONG], 'am': [UNK], 'e': [LONG]}

D_1_ES = {'es': [UNK], 'a': [UNK], 'ae': [LONG], 'am': [UNK], 'as': [LONG],
           'arum': [LONG, UNK], 'is': [LONG]}

D_1_AS = {'a': [UNK], 'ae': [LONG], 'am': [UNK], 'as': [UNK],
           'arum': [LONG, UNK], 'is': [LONG]}

D_2_M = {'us': [UNK], 'i': [LONG], 'o': [LONG], 'um': [UNK], 'e': [UNK],
         'orum': [LONG, UNK], 'is': [LONG], 'os': [LONG]}

D_2_N = {'us': [UNK], 'i': [LONG], 'o': [LONG], 'um': [UNK], 'a': [UNK],
         'orum': [LONG, UNK], 'is': [LONG], 'os': [LONG]}

D_3 = {'i': [LONG], 'e': [UNK], 'em': [UNK], 'es': [LONG],
           'um': [UNK], 'ibus': [UNK, UNK], 'a': [UNK]}

D_ADJ = {'a': [UNK], 'ae': [LONG], 'am': [UNK], 'as': [LONG],
         'arum': [LONG, UNK], 'is': [LONG], 'us': [UNK], 'i': [LONG],
         'o': [LONG], 'um': [UNK], 'e': [UNK], 'orum': [LONG, UNK], 'os': [LONG]}

ENDINGS_REF = {'a,_um_us': D_ADJ, 'i_us': D_2_M, 'i_um': D_2_N, 'ae_a': D_1_U,
               'ae_e_': D_1_E_, 'ae_e_s': D_1_E_S, 'ae_es': D_1_ES,
               'ae_a_s': D_1_A_S, 'ae_as': D_1_AS, 'ōris_or': DEC_3RD,
               'indecl.':{'':[]}}

IS_SET_UP = False
dict = {}
# dict[word] = (meter, [set_of_endings])


def extract_meter(str):
    """
    :param str: A word with long and short vowels marked
    :return: A tuple of two elements. The first is the word without any marking
    whatsoever, the second is the extracted meter
    """
    str = u_or_v(i_or_j(str))
    vowels = list(re.finditer(SYLLAB, str))
    meter = ''

    for i in range(len(vowels) - 1):
        vowel = str[vowels[i].start():vowels[i].end()]
        follow = str[vowels[i].end():vowels[i + 1].start()]
        meter += decide_on_logitude(vowel, follow)

    if vowels:
        vowel = str[vowels[-1].start():vowels[-1].end()]
        follow = str[vowels[-1].end():]
        meter += decide_on_logitude(vowel, follow)

    word = re.sub(r'[' + LONG + '|\\' + SHORT + ']', '', str)
    word = re.sub(r'j', 'i', word)
    word = re.sub(r'v', 'u', word)

    return word, meter


def rebuilt():
    """
    Use the files taken from Diogenes (that are in turn borrowed from perseus)
    to built a dictionary. In this dictionary, keys will be the words from
    latin-analyses.txt and values will be sequences of LONG/SHORT/UNK chars
    :return:
    """
    tree = ET.parse(LEWIS_SHORT_FILE_NAME)
    total_count = 0  # number of different genitives of different words. By
    # genitive a set of principal parts
    treated_count = 0  # number of genitives treated

    count = {}  # for each type of genitive - how many words there are that
    # have this type

    with open(OUTPUT_FILE_NAME,'w') as file:
        genetives = {'a, um': [('us', [('', None)])],
                     'i': [('us', [('', None)]), ('um', [('', None)])],
                     'ae': [('a', [('', None)]), ('e_', [('', None)]),
                            ('a_s', [('', None)]), ('as', [('', None)]),
                            ('e_s', [('', None)]), ('es', [('', None)])],
                     'ōris': [('or', [('or', 'indecl.'), ('o_r', None)])]}

        for entry in tree.iter(tag='entryFree'):
            key = entry.attrib['key'].rstrip('0123456789').lower()
            key = re.sub(r'_\^', '', key)
            key = re.sub(r'\^_', '', key)
            if ' ' in key:
                continue
            # main form of the word with long and short vowels marked

            total_count += 1
            itype_found = False
            for property in entry:
                if property.tag == 'itype':

                    if itype_found:
                        total_count += 1
                    else:
                        itype_found = True

                    # IMPORTANT: there may be multiple variations of genetive.
                    # Hence, cannot put 'break' here
                    if property.text in count:
                        count[property.text] += 1
                    else:
                        count[property.text] = 1

                    if property.text in genetives:
                        for nom, info in genetives[property.text]:
                            if len(key) >= len(nom) and key[-len(nom):] == nom:
                                treated_count += 1
                                for entry, entry_tag in info:
                                    if not entry_tag:
                                        entry_tag = re.sub(
                                            ' ', '_', property.text) + '_' + nom
                                    word, meter = extract_meter(key[:-len(nom)])
                                    file.write(word + ' ' + meter + ' ' +
                                               entry_tag + '\n')
                                break

    print('Done with ' + str(treated_count) + ' out of ' + str(total_count) +
          ' cases. Percentage: ' + str(
        round(treated_count/total_count * 100, 1)))
    sorted_count = sorted(count, key=count.get, reverse=True)
    for i in sorted_count:
        print(str(i) + ' ' + str(count[i]) + ' (' + str(round(
            count[i]/total_count * 100, 1)) + '%)')


def setup():
    with open(OUTPUT_FILE_NAME) as file:
        lines = file.readlines()
    for line in lines:
        line = line.rstrip('\n').split(' ')
        if line[0] in dict:
            dict[line[0]].append((line[1], ENDINGS_REF[line[2]]))
        else:
            dict[line[0]] = [(line[1], ENDINGS_REF[line[2]])]


def look_up(word):
    word = re.sub(r'j', 'i', word)
    word = re.sub(r'v', 'u', word)
    global IS_SET_UP
    if not IS_SET_UP:
        setup()
        IS_SET_UP = True
    meter = None
    for i in range(len(word), 1, -1):
        if word[:i] in dict:
            entries = dict[word[:i]]
            for entry in entries:
                if word[i:] in entry[1]:
                    if not meter:
                        meter = entry[0] + ''.join(entry[1][word[i:]])
                    else:
                        meter = merge_lists(meter, entry[0] + ''.join(
                            entry[1][word[i:]]), maximize=False)
            # TODO: This break is not completely legal
            break
    return meter

if __name__ == "__main__":
    rebuilt()

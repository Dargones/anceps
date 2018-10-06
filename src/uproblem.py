from src.utilities import *

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

BASE_DIR = '/Users/alexanderfedchin/PycharmProjects/sproj/Scansion_project/work_in_progress/'
PERSEUS_DATA_FILE_NAME = BASE_DIR + 'latin-analyses.txt'
OUTPUT_FILE_NAME = BASE_DIR + 'final_dict.txt'
LEWIS_SHORT_FILE_NAME = BASE_DIR + '1999.04.0059.xml'

IS_SET_UP = False

dict = {}



def merge_u_and_v(one, two):
    if len(one) != len(two):
        return None
    news = ""
    for i in range(len(one)):
        if one[i] == two[i]:
            news += one[i]
        elif one[i] == 'u' and two[i] == 'v':
            news += 'v'
        elif one[i] == 'v' and two[i] == 'u':
            news += 'v'
        else:
            return None
    return news


def rebuilt():
    """
    Use the files taken from Diogenes (that are in turn borrowed from perseus)
    to built a dictionary. In this dictionary, keys will be the words from
    latin-analyses.txt and values will be sequences of LONG/SHORT/UNK chars
    :return:
    """
    """tree = ET.parse(LEWIS_SHORT_FILE_NAME)

    for entry in tree.iter(tag='entryFree'):
        key = entry.attrib['key'].rstrip('0987654321').lower()
        key = re.sub(r'[' + LONG + '\\' + SHORT + ']', '', key)
        key_stripped = re.sub('v', 'u', re.sub('j', 'i', key))

        if key_stripped in dict:
            if key != dict[key_stripped]:
                dict[key_stripped] = None
            else:
                dict[key_stripped] = key"""

    with open(PERSEUS_DATA_FILE_NAME) as file:
        lines = file.readlines()
        for line in lines:
            line = line.lower()
            parts = line.split('{')
            key = parts[0].rstrip('\t')
            key = re.sub(r'_^', '', key)

            key_stripped = re.sub('v','u',re.sub('j','i',key))

            if key_stripped in dict:
                if key != dict[key_stripped]:
                    dict[key_stripped] = merge_u_and_v(dict[key_stripped], key)
                    if dict[key_stripped] is None:
                        print(dict[key_stripped], key)
            else:
                dict[key_stripped] = key

    with open(OUTPUT_FILE_NAME, 'w') as out:
        for key, value in dict.items():
            if value:
                value = re.sub(r'(^)v([^' + VOWELS + '])', r'\1u\2', value)
                out.write(key + " " + u_or_v(i_or_j(value)) + "\n")


def setup():
    with open(OUTPUT_FILE_NAME) as file:
        lines = file.readlines()
    for line in lines:
        line = line.rstrip('\n').split(' ')
        dict[line[0]] = line[1]


def look_up(word):
    word = re.sub(r'j', 'i', word)
    word = re.sub(r'v', 'u', word)
    global IS_SET_UP
    if not IS_SET_UP:
        setup()
        IS_SET_UP = True
    if word in dict:
        return dict[word]

if __name__ == "__main__":
    rebuilt()

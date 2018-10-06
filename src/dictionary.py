from src.utilities import *

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

BASE_DIR = '/Users/alexanderfedchin/PycharmProjects/sproj/Scansion_project/work_in_progress/'
LEWIS_SHORT_FILE_NAME = BASE_DIR + '1999.04.0059.xml'
PERSEUS_DATA_FILE_NAME = BASE_DIR + 'latin-analyses.txt'
OUTPUT_FILE_NAME = BASE_DIR + 'final_quantities.txt'

IS_SET_UP = False

dict = {}


def extract_meter(str):
    """
    :param str: A word with long and short vowels marked
    :return: the extracted meter
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

    return meter


def merge_forms(form1, form2, maximize=False):
    """
    Take two words with long and short vowels marked and remove all the long-
    short tags taht are different
    :param form1:
    :param form2:
    :param maximize:
    :return:
    """
    i = 0
    j = 0
    result = ''
    while i < len(form1) and j < len(form2):
        if form1[i] != form2[j]:
            if form1[i] not in [LONG, SHORT]:
                if form2[j] in [LONG, SHORT]:
                    if maximize:
                        result += form2[j]
                    j += 1
                else:
                    return result + form1[i:]
            elif form2[j] not in [LONG, SHORT]:
                if maximize:
                    result += form1[i]
                i += 1
            else:
                i += 1
                j += 1
        else:
            result += form1[i]
            i += 1
            j += 1
    if i < len(form1):
        result = result + form1[i:]
    return result


def rebuilt():
    """
    Use the files taken from Diogenes (that are in turn borrowed from perseus)
    to built a dictionary. In this dictionary, keys will be the words from
    latin-analyses.txt and values will be sequences of LONG/SHORT/UNK chars
    :return:
    """
    tree = ET.parse(LEWIS_SHORT_FILE_NAME)

    tmp_dict = {}

    with open(OUTPUT_FILE_NAME,'w') as file:
        for entry in tree.iter(tag='entryFree'):
            key = entry.attrib['key'].rstrip('0987654321').lower()
            key = re.sub(r'j', 'i', key)
            key = re.sub(r'v', 'u', key)
            key = re.sub(r'(' + LONG + '\\' + SHORT + ')|(\\' + SHORT + LONG + ')', '', key)
            if ' ' in key:
                continue
            word = re.sub(r'[\\' + SHORT + LONG + ']', '', key)
            if word in dict:
                tmp_dict[word] = merge_forms(tmp_dict[word], key)
            else:
                tmp_dict[word] = key

    with open(PERSEUS_DATA_FILE_NAME) as file:
        with open(OUTPUT_FILE_NAME, 'w') as out:
            lines = file.readlines()
            for line in lines:
                line = line.lower()
                parts = line.split('{')
                key = parts[0].rstrip('\t')
                key = re.sub(r'j', 'i', key)
                key = re.sub(r'v', 'u', key)
                versions = []

                problems = False

                for i in range(1, len(parts)):
                    parts[i] = list(
                        re.findall(r'(:? )([a-z_^]*)(:?,)([a-z_^]*)(:?[\t#])',
                                   parts[i]))
                    if parts[i]:
                        versions.append((parts[i][0][1], parts[i][0][3]))
                    else:
                        problems = True

                if problems:
                    continue

                final = None
                for version in versions:
                    dict_entry = re.sub(r'j', 'i', version[1])
                    dict_entry = re.sub(r'v', 'u', dict_entry)
                    if dict_entry in tmp_dict:
                        dict_entry = tmp_dict[dict_entry]
                        tmp = merge_forms(version[0], dict_entry, True)
                        if final:
                            final = merge_forms(tmp, final)
                        else:
                            final = tmp
                    else:
                        if final:
                            final = merge_forms(version[0], final)
                        else:
                            final = version[0]
                if final:
                    out.write(key + ' ' + extract_meter(final) + '\n')


def setup():
    with open(OUTPUT_FILE_NAME) as file:
        lines = file.readlines()
    for line in lines:
        line = line.rstrip('\n').split(' ')
        if line[0] in dict:
            dict[line[0]].append(line[1])
        else:
            dict[line[0]] = [line[1]]


def look_up(word):
    word = re.sub(r'j', 'i', word)
    word = re.sub(r'v', 'u', word)
    global IS_SET_UP
    if not IS_SET_UP:
        setup()
        IS_SET_UP = True
    meter = None
    if word[:i] in dict:
        entries = dict[word[:i]]
        for entry in entries:
            if not meter:
                meter = entry
            else:
                meter = merge_lists(meter, entry, maximize=False)
    return meter

if __name__ == "__main__":
    rebuilt()

from src.utilities import *

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

OUTPUT_FILE_NAME = '/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/diogenes/ijuv_dictionary.txt'
WINGE_DICTIONARY = "/Users/alexanderfedchin/PycharmProjects/Scansion_project/archives/latin-macronizer/macrons.txt"
IS_SET_UP = False
dictionary = {}


def merge_u_and_v(one, two):
    """
    Merging two versions of how a word should be read, favoring v over u
    :param one:
    :param two:
    :return:
    """
    # TODO: is v a better choice?
    if len(one) != len(two):
        return None
    news = ""
    for i in range(len(one)):
        if one[i] == two[i]:
            news += one[i]
        elif (one[i] == 'u' and two[i] == 'v') or (one[i] == 'v' and two[i] == 'u'):
            news += 'v'
        elif (one[i] == 'i' and two[i] == 'j') or (one[i] == 'j' and two[i] == 'i'):
            news += 'j'
        else:
            return None
    return news


def rebuilt():
    """
    Use the files taken from Diogenes (that are in turn borrowed from perseus)
    to built a dictionary. In this dictionary, keys will be the words with no
    "v" or "j" and the values will be the words with u replaced with v and
    i replaced with j whenever necessary.
    :return:
    """
    with open(PERSEUS_DATA_FILE_NAME) as file:
        lines = file.readlines()
        for line in lines:
            line = line.lower()
            parts = line.split('{')
            key = parts[0].rstrip('\t')
            key = re.sub(r'_^', '', key)

            key_stripped = re.sub('v','u',re.sub('j','i',key))

            if key_stripped in dictionary:
                if key != dictionary[key_stripped]:
                    dictionary[key_stripped] = merge_u_and_v(dictionary[key_stripped], key)
                    if dictionary[key_stripped] is None:
                        print(dictionary[key_stripped], key)
            else:
                dictionary[key_stripped] = key

    with open(OUTPUT_FILE_NAME, 'w') as out:
        for key, value in dictionary.items():
            if value:
                value = re.sub(r'(^)v([^' + VOWELS + '])', r'\1u\2', value)
                out.write(key + " " + u_or_v(i_or_j(value)) + "\n")


def rebuilt_winge():
    """
    Load the dictionary into memory
    :return:
    """
    with open(WINGE_DICTIONARY) as file:
        lines = file.readlines()
    for line in lines:
        line = re.sub('[^a-z\t]', '', line.lower()).split('\t')
        line[0] = multireplace(line[0], {'j': 'i', 'v': 'u'})
        if line[0] != multireplace(line[-1], {'j': 'i', 'v': 'u'}):
            print("Bad " + str(line))
            continue
        if line[0] in dictionary:
            line[-1] = merge_u_and_v(dictionary[line[0]], line[-1])
        dictionary[line[0]] = u_or_v(line[-1])
    with open(OUTPUT_FILE_NAME, 'w') as out:
        for key, value in dictionary.items():
            if value:
                out.write(key + " " + value + "\n")


def setup():
    """
    Load the dictionary into memory
    :return:
    """
    with open(OUTPUT_FILE_NAME) as file:
        lines = file.readlines()
    for line in lines:
        line = line.rstrip('\n').split(' ')
        dictionary[line[0]] = line[1]


def look_up(word):
    """
    Look up the word in the dictionary. If the dictionary is not loaded into
    memory, load it.
    :param word: word to look up
    :return:     the form of the word with u replaced with v and i replaced with
    j, whereever necessary
    """
    word = re.sub(r'j', 'i', word)
    word = re.sub(r'v', 'u', word)
    global IS_SET_UP
    if not IS_SET_UP:
        setup()
        IS_SET_UP = True
    if word in dictionary:
        return dictionary[word]

if __name__ == "__main__":
    rebuilt_winge()

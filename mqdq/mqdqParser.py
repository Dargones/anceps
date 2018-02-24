# -*- coding: utf-8 -*-
"""
This module provides tools for extracting information about natural
vowel quantities from the scanned mqdq texts. Can be used in 3 different ways:
1: python3 mqdqParser.py clean FILE CLEANED_FILE
    strips all of the punctuation, etc from the FILE, and replaces all of the
    special characters with normal ones.
2: python3 mqdqParser.py merge FILE_1 FILE_2 ... FILE_N DICT_NAME
    creates the dictionary of vowel quantities by merging 1 to n files indicated
    in the parameters.
3: python3 mqdqParser.py automatic TASK_DESCRIPTION_FILE
    where the first line of TASK_DESCRIPTION_FILE is the DICT_NAME, and all
    the subsequent lines are pairs of FILE CLEANED_FILE
"""

import sys
sys.path.append("../")
from utilities import *

charOK = re.compile('[^a-z\[\]\n\(\-\') \"\t*\.\?!;:0-9\\,' + SHORT + LONG + ']')
# These are characters that do not need special treatment. I.e., they either
# will be deleted or used later

unused = re.compile('[^a-z\[\]\n\\' + SHORT + LONG + ']')
# All the character that should be deleted after replacement. Ideally, what
# matches unused will be a subset of charOK

replace = {' ⁔': '\n', '⁔ ': '\n', '⁔': '\n', '‿': '\n', '  ': '\n', ' ': '\n',
           'ā': 'a_', 'ă': 'a^', 'Ā': 'a_', 'Ă': 'a^', 'Ā́': 'a_', 'ā́': 'a_',
           'ḗ': 'e_', 'ē': 'e_', 'ĕ': 'e^', 'Ḗ': 'e_', 'Ē': 'e_', 'Ĕ': 'e^',
           'ī': 'i_', 'ĭ': 'i^', 'Ī': 'i_', 'Ĭ': 'i^', 'ī́': 'i_', 'Ī́': 'i_',
           'ŏ': 'o^', 'ō': 'o_', 'ṓ': 'o_', 'Ṓ': 'o_', 'Ŏ': 'o^', 'Ō': 'o_',
           'ṓ': 'o_',
           'ū': 'u_', 'ŭ': 'u^', 'V̄': 'u_', 'ū́': 'u_', 'V̄́': 'u_',
           'V̆': 'u^',
           'ȳ': 'y_', 'y̆': 'y^', 'ȳ́': 'y_',
           'ǣ': '[ae]', 'Ǣ': '[ae]', 'æ': '[ae]', 'ǣ́': '[ae]', 'Ǣ́': '[ae]',
           'œ̄́': '[oe]', 'œ̄́': '[oe]', 'œ̄': '[oe]', 'Œ̄́': '[oe]',
           'Œ̄': '[oe]'}

long_by_position = re.compile('_([' + CONSONANTS + ']\n[' + CONSONANTS +
                              ']|\n[' + CONSONANTS + ']{2}|\n[' +
                              ''.join(LONG_CONSONANTS) + '])')

final_u = re.compile('u([^\\'+ SHORT + LONG +'].*\n.)')

SETUP_COMPLETED = False
DICT_NAME = "dictionary.txt"
dictionary = {}


# ------------------------------------------------------------------------------
# ------------- The Entry Class Definition -------------------------------------
# ------------------------------------------------------------------------------


class Entry:
    """Represents a single dictionary entry"""

    to_quant = {']': LONG, 'q': '', 'e': '', 'r': '', 't': '', 'y': '', 'u': '',
                'i': '', 'o': '', 'p': '', 'a': '', 's': '', 'd': '', 'f': '',
                'g': '', 'h': '', 'j': '', 'k': '', 'l': '', 'z': '', 'x': '',
                'c': '', 'v': '', 'b': '', 'n': '', 'm': '', '[': ''}

    DIPHTONG = '['
    DIPHTONG_CLOSE = ']'

    REPEAT = 3

    CERTAIN = 0  # Only load the vowels with very high certainty
    CERTAIN_THRESHOLD = 2

    MOST_PROBABLE = 1 # choose the most probable version

    def __init__(self, total_count, versions):
        """
        :param total_count: 
        :param versions: 
        """
        self.total_count = total_count
        self.versions = versions
        # self.turn_to_mode(Entry.CERTAIN)
        self.quantities = None
        self.mode = None

    def get_quantities(self, mode):
        if (not self.mode or self.mode != mode) and mode != Entry.REPEAT:
            self.turn_to_mode(mode)
            self.mode = mode
        return self.quantities

    def turn_to_mode(self, mode):
        self.quantities = []
        if mode == Entry.CERTAIN:
            mind_quantities = self.total_count > Entry.CERTAIN_THRESHOLD
            last_vowel = 0
            inds = []
            for i in range(len(self.versions)):
                inds.append(0)
            while inds[0] < len(self.versions[0][0]):
                quan_long = 0
                quan_short = 0
                quan = 0
                alph = 0
                diph = 0
                for i in range(len(self.versions)):
                    if inds[i] >= len(self.versions[i][0]):
                        continue
                    if self.versions[i][0][inds[i]] == Entry.DIPHTONG:
                        diph += 1
                    elif self.versions[i][0][inds[i]] == LONG:
                        quan += 1
                        quan_long += 1
                    elif self.versions[i][0][inds[i]] == SHORT:
                        quan += 1
                        quan_short += 1
                    else:
                        alph += 1
                if (diph + quan) == 0:
                    inds = [x + 1 for x in inds]
                elif (diph + alph) == 0:
                    if not mind_quantities or quan_long * quan_short != 0:
                        self.quantities.append(UNK)
                    else:
                        self.quantities.append(self.versions[0][0][inds[0]])
                    last_vowel = inds[0] + 1
                    inds = [x + 1 for x in inds]
                elif diph == 0:
                    if self.versions[0][0][inds[0]] == LONG or \
                                    self.versions[0][0][inds[0]] == SHORT:
                        self.quantities.append(UNK)
                        last_vowel = inds[0] + 1
                    for i in range(len(self.versions)):
                        if inds[i] >= len(self.versions[i][0]):
                            continue
                        if self.versions[i][0][inds[i]] == LONG or \
                                        self.versions[i][0][inds[i]] == SHORT:
                            inds[i] += 1
                elif (alph + quan) == 0:
                    last_vowel = inds[0] + 4
                    self.quantities.append(LONG)
                    inds = [x + 4 for x in inds]
                else:
                    return self.turn_to_mode(Entry.MOST_PROBABLE)
        elif mode == Entry.MOST_PROBABLE:
            last_vowel = len(self.versions[0][0]) - 1
            while not self.versions[0][0][last_vowel] in \
                    [LONG, SHORT, Entry.DIPHTONG_CLOSE] and last_vowel != 0:
                last_vowel -= 1
            self.quantities = multireplace(self.versions[0][0], Entry.to_quant)
        if len(re.findall(r'[' + VOWELS + ']',
                          self.versions[0][0][last_vowel:])) != 0:
            self.quantities += UNK

        
# ------------------------------------------------------------------------------
# ------------- The Line Class Definition --------------------------------------
# ------------------------------------------------------------------------------


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


def check_validity(line, line_id, filename):
    """
    Checks if the following line consists of characters from charOK. Prints a
    warning if it does not.
    :param line:  line to check
    :param line_id: line number inside the text
    """
    for delimiters in list(charOK.finditer(line)):
        end = delimiters.end()
        start = delimiters.start()
        char = line[start:end]
        for i in range(4):
            if start > 0:
                start -= 1
        for i in range(5):
            if end < len(line):
                end += 1

        print('WARNING: char \'' + char + "\' in file " + filename + " on line "
              + str(line_id) +
              ' inside the word ' + line[start:end] + ' should be replaced.\n')


def clean(input_file_name, output_file_name):
    """
    Process a file by stripping off punctuation and repacing all strange
    symbols with appropiate characters
    :param input_file_name: file to process
    :param output_file_name: file to write the output to
    """
    with open(input_file_name) as file:
        lines = file.readlines()
    with open(output_file_name, 'w') as file:
        for i in range(len(lines)):
            line = lines[i]
            line = line.rstrip('DS \n\t')
            if i != len(lines) - 1:
                line += ' '
            line = multireplace(line, replace)
            line = line.lower()
            check_validity(line, i + 1, input_file_name)
            line = unused.sub('', line)
            # print(line)
            line = final_u.sub(r'v\1', line)
            # print(line)
            line = long_by_position.sub(r'\1', line)
            file.write(line)


def merge(files, dict_name):
    """
    Read all of the files, and merge the information obtained from them into one
    big dictionary of vowel quantities.
    :param files:
    :param dict_name:
    """
    dict = {}
    word = re.compile('[^a-z]')
    for input in files:
        with open(input) as file:
            for line in file:
                if line == '\n':
                    continue
                key = re.sub('v', 'u', word.sub('', line))
                value = line[:-1]
                if key in dict:
                    i = 0
                    while i < len(dict[key]):
                        if dict[key][i][0] == value:
                            dict[key][i][1] += 1
                            break
                        i += 1
                    if i == len(dict[key]):
                        dict[key].append([value, 1])
                else:
                    dict[key] = [[value, 1]]
    with open(dict_name, 'w') as file:
        for key in sorted(dict.keys()):
            file.write(key + ' ')
            sum = 0
            for value in dict[key]:
                sum += value[1]
            file.write(str(sum) + ' ')
            for value in sorted(dict[key], key=lambda x: -x[1]):
                file.write(value[0] + ' ' + str(value[1]) + ' ')
            file.write('\n')


def setup():
    """Load all the information from a given dictionary"""
    with open(DICT_NAME) as file:
        for line in file:
            line = line.split(' ')
            key = line[0]
            total_count = int(line[1])
            i = 2
            versions = []
            while i < len(line) - 1:
                versions.append((line[i], int(line[i + 1])))
                i += 2
            dictionary[key] = Entry(total_count, versions)
    global SETUP_COMPLETED
    SETUP_COMPLETED = True


def get_quantities(word, mode):
    """
    Get the information about the vowel quantities in a certain word
    :param word:
    :param mode: the way to get teh quantities
    :return:
    """
    if not SETUP_COMPLETED:
        setup()
    cleaned = multireplace(word, {'v': 'u', 'j': 'i'})
    if cleaned in dictionary:
        return dictionary[cleaned].get_quantities(mode)

if __name__ == "__main__":
    """if (len(sys.argv) < 3) or ((sys.argv[1] == 'clean') and (
                len(sys.argv) < 4)) or ((sys.argv[1] == 'merge') and (
                len(sys.argv) < 4)) or ((sys.argv[1] != 'automatic') and (
                sys.argv[1] != 'merge') and (sys.argv[1] != 'clean')):
        print("Usage: \n1: " + sys.argv[0] + " clean FILE CLEANED_FILE\n" +
              "\tclean the file from various extraterrestrial symbols\n2: " +
              sys.argv[0] + " merge FILE_1 FILE_2 ... FILE_N DICT_NAME\n" +
              "\tcreate a dictionary of vowel quantities\n3: " +
              sys.argv[0] + " automatic TASK_DESCRIPTION_FILE\n" +
              "\tthe first line of TASK_DESCRIPTION_FILE is the DICT_NAME," +
              "and all the subsequent lines are pairs of FILE CLEANED_FILE\n")
    elif sys.argv[1] == "clean":
        clean(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "merge":
        merge(sys.argv[2:-1], sys.argv[-1])
    else:
        with open(sys.argv[2]) as file:
            lines = file.readlines()
            if len(lines) < 2:
                print("Not enough lines in the file")
                sys.exit()
            list_of_files = []
            for i in range(1, len(lines)):
                names = lines[i].rstrip('\n \t').split('\t')
                clean(names[0], names[1])
                list_of_files.append(names[1])
            merge(list_of_files, lines[0].rstrip('\n'))"""
    with open('task_description.txt') as file:
        lines = file.readlines()
        if len(lines) < 2:
            print("Not enough lines in the file")
            sys.exit()
        list_of_files = []
        for i in range(1, len(lines)):
            names = lines[i].rstrip('\n \t').split('\t')
            clean(names[0], names[1])
            list_of_files.append(names[1])
        merge(list_of_files, lines[0].rstrip('\n'))

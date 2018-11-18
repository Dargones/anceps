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
3: python3 mqdqParser.py automatic METAFILE
    where the first line of TMETAFILE is the DICT_NAME, and all
    the subsequent lines are pairs of FILE CLEANED_FILE
"""

import sys
from cltk.stem.latin.stem import Stemmer
from cltk.stem.lemma import LemmaReplacer
from src.utilities import *

LEMMATIZATION_FAILED = "FAIL"
# a token placed in a dictionary, when cltk lemmatizer fails

charOK = re.compile('[^a-z\[\]<>\n†\(\-\') –\"\t*\.\?!;:0-9\\,’“‘' +
                    SHORT + LONG + UNK + ']')
# These are characters that do not need special treatment. I.e., they either
# will be deleted or used later

unused = re.compile('[^a-z\[\]\n\\' + SHORT + LONG + UNK + ']')
# All the character that should be deleted after replacement. Ideally, what
# matches unused will be a subset of charOK

AE_OE_TO_E = False


replace = {' ⁔': '\n', '⁔ ': '\n', '⁔': '\n', ' ': '\n',
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
           'œ': '[oe]', 'Œ̄': '[oe]'}

long_elision = re.compile('(oe|ae)(m?[^a-zA-Z]*)‿')
elision = re.compile('(m?[^a-zA-Z]*)‿')

e_diphtongs = re.compile('(eu|ei|eo|ea)[&_]')
e_diphtongs_between = re.compile('e[&_]([uioa])([^&_\^\]])')
a_diphtongs_between = re.compile('a[&_]([u])([^&_\^\]])')

long_by_position = re.compile('_([' + CONSONANTS + ']\n[' + CONSONANTS +
                              ']|\n[' + CONSONANTS + ']{2}|\n[' +
                              ''.join(LONG_CONSONANTS) + '])')

u_to_v1 = re.compile('([^' + CONSONANTS + '])u([^\\'+ SHORT + LONG + '\\' + UNK + '\]])')
u_to_v2 = re.compile('u([^\\'+ SHORT + LONG + '\\' + UNK + '\]][^' + CONSONANTS+ '])')
i_to_j1 = re.compile('([^' + CONSONANTS + '])i([^\\'+ SHORT + LONG + '\\' + UNK + '\]])')
i_to_j2 = re.compile('i([^\\'+ SHORT + LONG + '\\' + UNK + '\]][^' + CONSONANTS+ '])')

SETUP_COMPLETED = False  # true if the dictionary is loaded into memory
DEFAULT_DICT = "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/mqdq/dictionary.txt"
# the default dictionary from which to load the data
dictionary = {}
# a dictionary of entries that is loaded into memory before scansion begins
lemmas = {}
# a dictionary that ties lemmas to all the forms they can take. This dictionary
# is used whenever the form itself is not present in the dictionary

stemmer = Stemmer()
lemmatizer = LemmaReplacer('latin')


# ------------------------------------------------------------------------------
# ------------- Creating the dictionary ----------------------------------------
# ------------------------------------------------------------------------------


def check_validity(line, line_id, filename):
    """
    Checks if the following line consists of characters from charOK. Prints a
    warning if it does not.
    :param line:    line to check
    :param line_id: line number inside the text
    """
    for delimiters in list(charOK.finditer(line)):
        # if the code here executes, a bad character is found
        end = delimiters.end()
        start = delimiters.start()
        char = line[start:end]

        while start > 0 and line[start] not in '\n ':
            start -= 1
        while end < len(line) and line[end] not in '\n ':
            end += 1

        print('WARNING: char \'' + char + "\' in file " + filename + " on line "
              + str(line_id) + ' inside the word ' + line[start:end] +
              ' should be replaced.\n')


def clean(input_file_name, output_file_name):
    """
    Process a file by stripping off punctuation and replacing all strange
    symbols with appropriate characters
    :param input_file_name: file to process
    :param output_file_name: file to write the output to
    """
    with open(input_file_name) as file:
        lines = file.readlines()
    with open(output_file_name, 'w') as file:
        for i in range(len(lines)):
            line = lines[i]
            line = line.rstrip('\n\t ')  # stripping off the meter type data
            if not re.match('[SD]{4}', line[-4:]):
                # print('WARNING: Bad line ' + line)
                continue
            line = line.rstrip('\n \tSD')
            if i != len(lines) - 1:
                line += ' '
            line = re.sub('[ ][ ]*', ' ', line)
            line = re.sub('[\[\]]', '', line)
            line = long_elision.sub(r'[\1]\2\n', line)
            line = elision.sub(r'&\1\n', line)
            line = multireplace(line, replace)
            # replacing metrical signs with those used by the program
            line = line.lower()
            check_validity(line, i + 1, input_file_name)
            # checking for any 'bad' characters
            line = unused.sub('', line)
            # deleting punctuation signs etc.
            last_vowel = len(line) - 1
            while not line[last_vowel] in [LONG, SHORT, UNK, ']'] \
                    and last_vowel != 0:
                last_vowel -= 1

            j = len(line) - 1
            while j > last_vowel:
                if line[j] in VOWELS:
                    if j + 1 == len(line) or line[j + 1] != ']':
                        if j + 1 == len(line):
                            line = line[:j + 1] + UNK
                        else:
                            line = line[:j + 1] + UNK + line[j + 1:]
                    else:
                        print("Debug line: " + line)
                    break
                j -= 1

            line = e_diphtongs.sub(r'[\1]', line)
            line = e_diphtongs_between.sub(r'[e\1]\2', line)
            line = a_diphtongs_between.sub(r'[a\1]\2', line)
            line = u_to_v1.sub(r'\1v\2', line)
            line = u_to_v2.sub(r'v\1', line)
            line = i_to_j1.sub(r'\1j\2', line)
            line = i_to_j2.sub(r'j\1', line)

            #  .* .*[^\[\n][aeoiu][^_\^&\]]

            if line[-1] != "\n":
                line += "\n"

            if len(list(re.finditer('[^\[][' + VOWELS + '][^&_\^\]]', line))) != 0:
                print("Warning: " + lines[i].rstrip('\n'))
                continue

            if len(list(re.finditer('[' + CONSONANTS + '][&\]_\^]', line))) != 0:
                print("Warning: " + lines[i].rstrip('\n'))
                continue

            if len(list(re.finditer(r"[aeuoi]\^\n[" + CONSONANTS + "][^aeuoihyv\[rl]["+CONSONANTS+"]", line))) != 0:
                print(line)  # TODO: what is this for?

            if AE_OE_TO_E:
                line = re.sub('\[[ao]e\]', 'e_', line)
            line = re.sub('\n[\n]*', '\n', line)
            line = long_by_position.sub(r'' + UNK + r'\1', line)
            file.write(str(i) + " " + line)


def last_quantity(form):
    """
    Return the last quantity mark (&, ], _, ^, or None)
    :param word:
    :return:
    """
    i = len(form) - 1
    while i >= 0 and form[i] not in ['&', '_', '^', ']']:
        i -= 1
    if i == -1:
        return None, -1
    return form[i], i


def clean_dict(dictionary):
    """
    Clean the dictionary (remove all et&, if there are only e^t and no e_t)
    :param dictionary:
    :return:
    """
    for key in sorted(dictionary.keys()):
        last_vowels = [last_quantity(x[0])[0] for x in dictionary[key]]
        last_indexes = [last_quantity(x[0])[1] for x in dictionary[key]]
        j = 0
        for i in range(len(last_vowels)):
            if last_vowels[i] == '&':
                new_form = dictionary[key][j][0]
                new_form_long = new_form[:last_indexes[i]] + '_' + new_form[last_indexes[i] + 1:]
                new_form_short = new_form[:last_indexes[i]] + '^' + new_form[last_indexes[i] + 1:]
                if new_form_long in [x[0] for x in dictionary[key]]:
                    position_long = [x[0] for x in dictionary[key]].index(new_form_long)
                    if new_form_short in [x[0] for x in dictionary[key]]:
                        position_short = [x[0] for x in dictionary[key]].index(new_form_short)
                        total = dictionary[key][position_long][1] + dictionary[key][position_short][1]
                        dictionary[key][position_long][1] += dictionary[key][j][1] * \
                                                             dictionary[key][position_long][1] / total
                        dictionary[key][position_short][1] += dictionary[key][j][1] * \
                                                             dictionary[key][position_short][1] / total
                    else:
                        dictionary[key][position_long][1] += dictionary[key][j][1]
                    del dictionary[key][j]
                elif new_form_short in [x[0] for x in dictionary[key]]:
                    position_short = [x[0] for x in dictionary[key]].index(new_form_short)
                    dictionary[key][position_short][1] += dictionary[key][j][1]
                    del dictionary[key][j]
                else:
                    if '_'in last_vowels and '^' not in last_vowels:
                        dictionary[key][j][0] = dictionary[key][j][0][:last_indexes[i]] + \
                                            '_' + dictionary[key][j][0][last_indexes[i] + 1:]
                    elif '^' in last_vowels and '_' not in last_vowels:
                        dictionary[key][j][0] = dictionary[key][j][0][:last_indexes[i]] + \
                                                '^' + dictionary[key][j][0][last_indexes[i] + 1:]
                    j += 1
            else:
                j += 1
        if len(dictionary[key]) == 0:
            del dictionary[key]


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
                if ' ' in line:
                    line = line.split(' ')[1]
                key = re.sub('j', 'i', re.sub('v', 'u', word.sub('', line)))
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
    clean_dict(dict)
    with open(dict_name, 'w') as file:
        for key in sorted(dict.keys()):
            lemma = lemmatizer.lemmatize(key)
            if not lemma or len(lemma) > 1:
                print("lemmatizing error: " + key + str(lemma))
                file.write(key + ' ' + LEMMATIZATION_FAILED + ' ')
            else:
                file.write(key + ' ' + lemma[0] + ' ')
            sum = 0
            for value in dict[key]:
                sum += value[1]
            file.write(str(sum) + ' ')
            for value in sorted(dict[key], key=lambda x: -x[1]):
                file.write(value[0] + ' ' + str(value[1]) + ' ')
            file.write('\n')


# ------------------------------------------------------------------------------
# ------------- The Entry Class Definition -------------------------------------
# ------------------------------------------------------------------------------


class Entry:
    """Represents a single dictionary entry"""

    to_quant = {']': LONG, 'q': '', 'e': '', 'r': '', 't': '', 'y': '', 'u': '',
                'i': '', 'o': '', 'p': '', 'a': '', 's': '', 'd': '', 'f': '',
                'g': '', 'h': '', 'j': '', 'k': '', 'l': '', 'z': '', 'x': '',
                'c': '', 'v': '', 'b': '', 'n': '', 'm': '', '[': ''}

    def __init__(self, tc, versions, entry_str):
        """
        :param total_count:
        :param versions:
        """
        self.entry_str = entry_str
        # the key, i.e. how this form is written without the vowel quantities
        self.versions = []
        # different versions of how this form can be scanned
        self.initial = versions
        # versions as they appear in the dictionary. Used for debugging purposes
        self.tc = tc  # total count, i.e. the number of occurrences of this form
        for v in versions:
            self.versions.append((multireplace(v[0],
                                               Entry.to_quant), v[1] / tc))
            # replaces the count with frequency and deletes all letters
            # preserving vowel quantities only


# ------------------------------------------------------------------------------
# ------------- Using the dictionary -------------------------------------------
# ------------------------------------------------------------------------------


def setup(dict_name=DEFAULT_DICT):
    """
    Load all the information from a given dictionary
    :param dict_name: the path to the dictionary to load
    """
    with open(dict_name) as file:
        for line in file:
            line = line.split(' ')
            key = line[0]
            lemma = line[1]
            total_count = int(line[2])
            i = 3
            versions = []
            while i < len(line) - 1:
                versions.append((line[i], int(line[i + 1])))
                i += 2
            dictionary[key] = Entry(total_count, versions, key)
            if lemma == LEMMATIZATION_FAILED:
                # TODO: maybe something should be done in this case
                continue
            if lemma in lemmas:
                lemmas[lemma] += [dictionary[key]]
            else:
                lemmas[lemma] = [dictionary[key]]
    global SETUP_COMPLETED
    SETUP_COMPLETED = True


def get_quantities(word, trace=False):
    """
    Get the information about the vowel quantities in a certain word
    :param word:
    :param trace: if True, print various information in the process
    :return:
    """
    if not SETUP_COMPLETED:
        setup()
    cleaned = multireplace(word, {'v': 'u', 'j': 'i'})
    if cleaned in dictionary:
        return dictionary[cleaned].versions, [x[0] for x in dictionary[cleaned].initial]
    # If the execution reached this point, the form seems to be absent from the
    # dictionary (but the lemma might still be present)
    lemma = lemmatizer.lemmatize(cleaned)
    if not lemma or len(lemma) > 1:
        print("lemmatizing error: " + cleaned + " " + str(lemma))
        return None, None
    # the lemma is found
    lemma = lemma[0]
    if lemma in lemmas:
        # TODO: multiple choices here
        meter, scansions, rest = best_guess(lemmas[lemma], cleaned, trace)
        # meter is the scansion of the stem, the rest is the ending/suffixes,
        # for which the scansion is unkown
        if not meter:
            return None, None
        # TODO: perhaps, the code below should be wrapped in a function
        vowels = list(re.finditer(SYLLAB, rest))
        ending = ""
        end_scansion = ""
        if len(vowels) > 0:
            end_scansion += rest[:vowels[0].start()]
        else:
            end_scansion += rest
        for i in range(len(vowels) - 1):
            letter = rest[vowels[i].start():vowels[i].end()]
            follow = rest[vowels[i].end():vowels[i + 1].start()]
            ending += decide_on_length(letter, follow)
            if len(letter) > 2:
                end_scansion += '[' + letter + ']' + follow
            else:
                end_scansion += letter + ending[-1] + follow
        if len(vowels) != 0:
            letter = rest[vowels[-1].start():vowels[-1].end()]
            follow = rest[vowels[-1].end():]
            ending += decide_on_length(letter, follow)
            if len(letter) > 2:
                end_scansion += '[' + letter + ']' + follow
            else:
                end_scansion += letter + ending[-1] + follow
        return [(x[0] + ending, x[1]) for x in meter], [x + end_scansion for x in scansions]
    # Turn on stemming here
    return None, None


def best_guess(cognates, word, trace=False):
    """
    Given the list of entries in a dictionary of words cognate to that given
    return a possible scansion of the stem
    :param cognates:
    :param word:
    :param trace: If True, will print various stats
    :return:
    """
    to_print = "Word: " + word + "\nCognates:\n"
    for form in cognates:
        to_print += form.entry_str + ' ' + str(form.tc) + ' ' + \
                    stem_it(form.entry_str) + '\n'
    best_form = None
    best = 0
    stem = stem_it(word)
    to_print += "\nStem: " + stem
    for form in cognates:
        if stem_it(form.entry_str) == stem:
            if form.tc > best:
                best = form.tc
                best_form = form
    if not best_form:
        if trace:
            print(to_print +
                  "\nNo word with the same stem. Choosing among lemmas")
        # TODO
        return None, None, None

    to_print += "\nBest: " + str(best) + ", best form: " + best_form.entry_str \
                + ", meter: " + best_form.initial[0][0] + ", rest: " + \
                word[len(stem):]

    # now it is only the matter of extracting the part of the word that is
    # common to both
    # TODO: maybe only the stem itself should be used
    meter = []
    scansions = []
    for version in best_form.initial:
        info = version[0]
        count = len(best_form.entry_str) - len(stem)
        i = len(info) - 1
        while count > 0:
            if info[i] == ']':
                i -= 4
                count -= 1
            elif info[i] in [LONG, SHORT, UNK]:
                i -= 2
            else:
                i -= 1
            count -= 1
        new_v = multireplace(info[0: i + 1], Entry.to_quant)
        found = False
        for v in meter:
            if v[0] == new_v:
                v[1] += version[1] / best_form.tc
                found = True
        if not found:
            meter.append([multireplace(info[0: i + 1], Entry.to_quant),
                          version[1] / best_form.tc])
            scansions.append(info[0: i + 1])
    if trace:
        print(to_print + "\nFinal meter: " + str(meter) + "\n")
    return meter, scansions, word[len(stem):]


if __name__ == "__main__":
    if (len(sys.argv) < 3) or ((sys.argv[1] == 'clean') and (
                len(sys.argv) < 4)) or ((sys.argv[1] == 'merge') and (
                len(sys.argv) < 4)) or ((sys.argv[1] != 'automatic') and (
                sys.argv[1] != 'merge') and (sys.argv[1] != 'clean')):
        print("Usage: \n1: " + sys.argv[0] + " clean FILE CLEANED_FILE\n" +
              "\tclean the file from various extraterrestrial symbols\n2: " +
              sys.argv[0] + " merge FILE_1 FILE_2 ... FILE_N DICT_NAME\n" +
              "\tcreate a dictionary of vowel quantities\n3: " +
              sys.argv[0] + " automatic METAFILE\n" +
              "\tthe first line of METAFILE is the DICT_NAME, " +
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
            merge(list_of_files, lines[0].rstrip('\n'))

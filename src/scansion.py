"""
This module is the bulk of the algorithm. Usage:
python3 scansion.py file1 file2 ... filen
"""

import sys
import copy
from src import mqdqParser
from src import uproblem
from src.utilities import *

MQDQ = 0
REPEAT = 1
MAX_ATTEMPT = 200

MODES = [(MQDQ, False)]
# each time the program makes an attempt to scan the lines it can employ a
# different method to do so. On the i-th attempt, method MODES[i] shall be
# employed. If MODES[-1] is None, the program will terminate after the
# len(MODES) - 1 attempt. Otherwise, when i >= len(MODES), MODES[-1]
# method is used. The program terminates when no further progress is being done.
# The program only attempts to rescan already scanned lines
# if MODES[i][1] == True.

LINES_TO_DEBUG = []

# ------------------------------------------------------------------------------
# ------------- The Word Class Definition --------------------------------------
# ------------------------------------------------------------------------------


class Word:
    """Represents a word"""

    mqdqit = 0
    total = 0
    A_VOWEL = 'a'
    elision_count = 0

    ELID_END = {}  # dictionary of words elided at the end
    ELID_BEG = {}  # dictionary of words elided at the beginning

    def __init__(self, word):
        """
        Initialize the word object
        :param word:        this word
        :param next_word:   the next word in the line (to track elision)
        """
        self.word = u_or_v(i_or_j(word))
        word_trial = uproblem.look_up(self.word)
        if word_trial:
            if word_trial != self.word:
                self.word = word_trial
        self.mid = 0
        self.meter = []
        self.in_dict = False
        self.elision = False
        self.long_by_pos = False
        self.case_problem = False
        self.muta_cum_liquida = False

    def analyse(self, next_word, trace=False):
        """
        Decide on the length of the vowels
        :param next_word:
        :return:
        """
        # TODO: fix the problem with ve
        Word.total += 1
        self.meter = mqdqParser.get_quantities(self.word, trace)
        if self.meter:
            Word.mqdqit += 1
            self.in_dict = True
            if next_word:
                vowels = list(re.finditer(SYLLAB, self.word))
                follow = self.word[vowels[-1].end():]
                follow += ' ' + list(re.findall(
                    r'^[' + CONSONANTS + ']*', next_word))[0]
                if re.match(r'[m]? [h]?$', follow) is not None:
                    self.add_elision(next_word)
                elif decide_on_length(Word.A_VOWEL,
                                      re.sub(' ', '', follow)) == LONG:
                    self.long_by_pos = True
                elif self.word[-1] == 'a':
                    if trace:
                        print("Case", self.word, follow)
                    self.case_problem = True
                else:
                    follow = re.sub(' ', '', follow)
                    if len(follow) > 2 and follow[1] == 'h':
                        follow = follow[:1] + follow[2:]
                    if (len(follow) == 2) and (re.match(SHORT_COMBINATIONS, follow)):
                        self.muta_cum_liquida = True
            return

        self.meter = []
        vowels = list(re.finditer(SYLLAB, self.word))
        for i in range(len(vowels) - 1):
            letter = self.word[vowels[i].start():vowels[i].end()]
            follow = self.word[vowels[i].end():vowels[i + 1].start()]
            self.meter.append(decide_on_length(letter, follow))
        if len(vowels) > 0:
            letter = self.word[vowels[-1].start():vowels[-1].end()]
            follow = self.word[vowels[-1].end():]
            if next_word:
                follow += ' ' + list(re.findall(
                    r'^[' + CONSONANTS + ']*', next_word))[0]
            if re.match(r'[m]? [h]?$', follow) is None:
                follow = re.sub(' ', '', follow)
                self.meter.append(decide_on_length(letter, follow))
            else:
                self.add_elision(next_word)

    def add_elision(self, next_word):
        this_word = mqdqParser.lemmatizer.lemmatize(self.word)[0]
        next_word = mqdqParser.lemmatizer.lemmatize(u_or_v(i_or_j(next_word)))[0]
        next_word = mqdqParser.lemmatizer.lemmatize(u_or_v(i_or_j(next_word)))[0]
        self.elision = True
        Word.elision_count += 1
        if this_word in self.ELID_END:
            self.ELID_END[this_word] += 1
        else:
            self.ELID_END[this_word] = 1
        if next_word in self.ELID_BEG:
            self.ELID_BEG[next_word] += 1
        else:
            self.ELID_BEG[next_word] = 1

    def get_meter(self, mode):
        """
        Get the meter pattern for this word
        :param mode: see MODES in the beginning of this file
        :return: meter in form of the list of LONG, SHORT, UNK
        """
        if mode == MQDQ and self.in_dict:
            self.meter = mqdqParser.get_quantities(self.word)[self.mid][0]
            if self.elision:
                self.meter = self.meter[:-1]
            elif self.long_by_pos:
                self.meter = self.meter[:-1] + LONG
            elif self.case_problem:
                self.meter = self.meter[:-1] + UNK
            elif len(self.meter) > 0 and self.meter[-1] == SHORT and self.muta_cum_liquida:
                self.meter = self.meter[:-1] + UNK
        return self.meter

    def get_metrics(self):
        if self.in_dict:
            if not self.elision and not self.long_by_pos:
                return [x[1] for x in mqdqParser.get_quantities(self.word)]
            quant = mqdqParser.get_quantities(self.word)
            if len(quant[0][0]) < 2:
                return [1]
            result = []
            for version in quant:
                if not ((version[0][:-1] + LONG in result)
                        or (version[0][:-1] + UNK in result)
                        or (version[0][:-1] + SHORT in result)):
                    result.append(version[1])
                else:
                    result.append(0)
            return result
        return [1]

    @staticmethod
    def save_elision_stats(filename, n_lines):
        """
        Save statistics about elision to a specific file
        :param filename:
        :param n_lines: number of lines in the original file
        :return:
        """
        with open(filename, 'w') as file:
            file.write("Elision rate: " +
                       str(round(Word.elision_count / n_lines, 5)) + '\n')
            file.write("Elided at the end:\n")
            sorted_elided = sorted(Word.ELID_END, key=Word.ELID_END.get,
                                   reverse=True)
            for word in sorted_elided:
                file.write(word + " " + str(Word.ELID_END[word]) + '\n')
            file.write("\nElided at the beginning:\n")
            sorted_elided = sorted(Word.ELID_BEG, key=Word.ELID_BEG.get,
                                   reverse=True)
            for word in sorted_elided:
                file.write(word + " " + str(Word.ELID_BEG[word]) + '\n')

# ------------------------------------------------------------------------------
# ------------- The Line Class Definition --------------------------------------
# ------------------------------------------------------------------------------


class Line:
    """This class represents a single line"""

    line_counter = 0

    def __init__(self, string):
        """
        The basic constructor.
        :param string: the string representation of the line. May contain
                     punctuation signs, vowel u should be typed as "u", not "v",
                     vowel "i" should be typed as "i", not as "j"
        """
        self.scanned = False
        self.line = []
        self.id = Line.line_counter
        self.initial_orthography = copy.deepcopy(string)
        Line.line_counter += 1
        string = string.lower()
        mqdqParser.check_validity(string, self.id, '')
        string = re.sub(r'[^a-z0-9/ ]', ' ', string)  # dealing with punctuation
        string = re.sub(r'[ ]+', ' ', string)
        string = string.rstrip(' ').lstrip(' ')
        # make the ending 'que' into a separate word
        # string = re.sub(r'([a-z])que( |$)', r'\1 que\2', string)
        # string = re.sub(r'([a-z])ne( |$)', r'\1 ne\2', string)
        # string = re.sub(r'( |^)' + PREFIXES + '([a-z])', r'\1\2w \3', string)
        # make certain prefixes into separate words

        string = string.split(' ')

        if self.id in LINES_TO_DEBUG:
            print('debug_here')
            pass

        for i in range(len(string)):
            self.line.append(Word(string[i]))
        for i in range(len(self.line) - 1):
            self.line[i].analyse(self.line[i + 1].word,
                                 self.id in LINES_TO_DEBUG)
        self.line[-1].analyse(None, self.id in LINES_TO_DEBUG)

        self.mqdq = [(1, [])]
        metrics = [x.get_metrics() for x in self.line]
        for word in metrics:
            mqdqNew = []
            for i in range(len(word)):
                if word[i] != 0:
                    for seq in self.mqdq:
                        mqdqNew.append((seq[0] * word[i], seq[1] + [i]))
            self.mqdq = mqdqNew
        self.mqdq = sorted(self.mqdq, key=lambda x: -x[0])
        self.mqdq_id = 0

    def get_meter(self, mode):
        """
        Return the longitude of all vowels if known as a list
        :return:
        """
        if mode != REPEAT and self.id in LINES_TO_DEBUG and \
                (mode != MQDQ or self.mqdq_id < len(self.mqdq)):
            print('debug_here')
            pass

        if mode == MQDQ and self.mqdq_id < len(self.mqdq):
            for i in range(len(self.line)):
                self.line[i].mid = self.mqdq[self.mqdq_id][1][i]
            self.mqdq_id += 1

        result = []
        for word in self.line:
            result += word.get_meter(mode)

        if mode != REPEAT and self.id in LINES_TO_DEBUG and \
                (mode != MQDQ or self.mqdq_id < len(self.mqdq)):
            print('id: ' + str(self.id) + '\n')
            print(' '.join(result))
            for i in range(len(self.line)):
                print(self.line[i].word + ': ' + ' '.join(
                    self.line[i].get_meter(REPEAT)))
            print('')
        return result


# ------------- The Main Program -----------------------------------------------


def scansion_versions(line, meter, meter_index):
    """
    Propose different scansions on a pure logical basis
    :param line: a list where every element represents a syllable. A syllable
                 can either be LONG, SHORT or UNK
    :param meter: meter description
    :param meterIndex: the leftmost part of the meter that can be broken into
                       different parts
    :return: 
    """
    result = []
    for i in range(meter_index, len(meter)):
        token = meter[i]
        if isinstance(token, list):
            del meter[i]
            for tokenVersion in token:
                meter[i:i] = tokenVersion
                result += scansion_versions(line, meter, i)
                del meter[i:i + len(tokenVersion)]
            meter[i:i] = [token]
            return result
        elif (i >= len(line)) or ((line[i] != meter[i]) and (
                    line[i] != UNK) and meter[i] != ANCEPS):
            return result
    if len(meter) == len(line):
        result.append(copy.deepcopy(meter))
    return result


def main(path_to_text, meters, trace=True, print_problems=True, elision=False, manual=False):
    """
    Load the lines from the file and attempt to scan them. Print some statistic
    at the end. Return the scanned lines
    :param path_to_text: The text to scan
    :param meters: What meter should be used for scanning. E.g., use [HEXAMETER]
    for hexameters and [HEXAMETER, PENTAMETER] for elegiacs
    :param elision: If True, save elision statistics to a separate file
    :param print_problems: If True, print info about problematic lines
    :param trace: If True, print various stats
    :param manual: Ask the user for manual guidence
    :return: list of possible scansions for each line
    """
    lines = []
    result = []
    Word.elision_count = 0
    Word.ELID_END = {}
    Word.ELID_BEG = {}
    with open(path_to_text) as file:
        for line in file:
            lines.append(Line(line))
            result.append([])
    print("Scanning: " + path_to_text)
    if elision:
        elision_file = 'output/' + path_to_text.split('/')[-1] + '.elision'
        Word.save_elision_stats(elision_file, len(lines))
    print("Fraction of words in dictionary: " + str(Word.mqdqit/Word.total))

    progress = -1
    attempt_n = 0
    versions_total = 0
    possible_progress = False

    if print_problems:
        with open('output/' + path_to_text.split('/')[-1]) as file:
            previous_attempt = file.readlines()

    while (progress != 0 or possible_progress) and (
                    attempt_n < MAX_ATTEMPT or MAX_ATTEMPT == -1):
        possible_progress = False
        if attempt_n >= len(MODES):
            mode = MODES[-1]
        else:
            mode = MODES[attempt_n]
            if mode is None:
                break
        if trace:
            print('\nAttempt #' + str(attempt_n))
        empty = 0
        identified = 0
        versions_total_new = 0
        for i in range(len(lines)):
            if not mode[1] and lines[i].scanned:
                versions_total_new += 1
                identified += 1
                continue
            meter = meters[i % len(meters)]
            att = lines[i].get_meter(mode[0])
            curr = scansion_versions(att, meter, 0)

            if attempt_n == 0 and print_problems:
                if UNK in previous_attempt[i]:
                    print("Line:" + lines[i].initial_orthography +
                          "Output: " + " ".join(att) +
                          "\nNumber of syllables according to the program: " +
                          str(len(att)) + "\n" +
                          "The program failed to scan the line\n\n")
                elif '|' in previous_attempt[i]:
                    print("Line:" + lines[i].initial_orthography +
                          "Output: " + " ".join(att) +
                          "\nNumber of syllables according to the program: " +
                          str(len(att)) + "\n" +
                          "The program gave multiple possible scansions\n\n")

            if len(curr) == 1:
                versions_total += 1
                identified += 1
                lines[i].scanned = True
                result[i] = curr
            else:
                if lines[i].mqdq_id < len(lines[i].mqdq):
                    possible_progress = True
                lines[i].scanned = False
                if len(curr) == 0 and not result[i]:
                    empty += 1
                elif not result[i]:
                    result[i] = curr
                    versions_total += len(curr)
                else:
                    new_result = []
                    for v in result[i]:
                        if v in curr:
                            new_result.append(v)
                    if new_result:
                        result[i] = new_result
                    if attempt_n == MAX_ATTEMPT - 1 and manual:
                        result[i] = solve_manually(lines[i], result[i])
                        if len(result[i]) == 1:
                            identified += 1
                            lines[i].scanned = True
                    versions_total += len(result)

            if i in LINES_TO_DEBUG:
                print(result[i])

        progress = versions_total_new - versions_total
        versions_total = versions_total_new
        attempt_n += 1
        if trace:
            print('average = ' + str(round(versions_total / len(lines), 2)) +
                  ' versions per line.\nidentified = ' +
                  str(round(identified / len(lines) * 100, 1)) + '%\nempty = ' +
                  str(round(empty / len(lines) * 100, 1)) + '%')

    for i in range(len(lines)):
        if not result[i]:
            lines[i].mqdq_id = 0
            result[i] = [lines[i].get_meter(MQDQ)[:-1] + [UNK]]
    return result


def solve_manually(line, scansions):
    """
    Ask the user to indicate the correct scansion
    :param lines:
    :param scansions:
    :return:
    """
    for scansion in scansions:
        if len(scansion) != len(scansions[0]):
            return scansions
    word_id = []
    for i in range(len(line.line)):
        for j in range(len(line.line[i].get_meter(REPEAT))):
            word_id.append((i, j, len(line.line[i].get_meter(REPEAT))))
    i = 0
    while len(scansions) != 1 and i < len(scansions[0]):
        versions = [x[i] for x in scansions]
        if LONG in versions and SHORT in versions:
            print("All versions: " + '\t'.join([' '.join(x) for x in scansions]))
            print("In sentence: " + line.initial_orthography.strip('\n'))
            print("In word: " + line.line[word_id[i][0]].word)
            data = input(("In (one-based) syllable #" +
                          str(word_id[i][1] + 1)) + " out of " + str(word_id[i][2]) + ":\n")
            if data in [LONG, SHORT]:
                scansions = [x for x in scansions if x[i] == data]
            else:
                return scansions
        i += 1
    if len(scansions) == 1:
        print("This helped!")
        return scansions


def print_results(lines, output_file):
    """
    Save the results of scansion to the file indicated
    :param lines:       Data to save
    :param output_file: File to print the data to
    :return:
    """
    with open(output_file, 'w') as file:
        for i in range(len(lines)):
            curr = lines[i]
            if UNK in curr[0]:
                # TODO: does it make sense to print only one character?
                file.write(UNK + "\n")
                continue
            to_print = ''
            j = 0
            while j < len(curr):
                to_print += ' '.join(curr[j])
                if j < len(curr) - 1:
                    to_print += '|'
                j += 1
            file.write(to_print + '\n')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s file1 file2 ... filen" % sys.argv[0])
        sys.exit(-1)

    for filename in sys.argv[1:]:
        output_filename = 'output/' + filename.split('/')[-1]
        result = main(filename, [TRIMETER], True, False, False, True)
        print_results(result, output_filename)
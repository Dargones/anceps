"""
This module is the bulk of the algorithm. Usage:
python3 scansion.py input_file_name output_file_name
where input_file_name          is the name of the file that contains the lines
                               to be scanned
      output_file_name         the name of the file to which to print the output

"""

from __future__ import division
import copy
import mqdqParser

import sys
sys.path.append("../")

from work_in_progress import uproblem
from utilities import *

MQDQ = 0
REPEAT = 1
MAX_ATTEMPT = 300

MODES = [(MQDQ, False)]
# each time the program makes an attempt to scan the lines it can employ a
# different method to do so. On the i-th attempt, method MODES[i] shall be
# employed. If MODES[-1] is None, the program will terminate after the
# len(MODES) - 1 attempt. Otherwise, when i >= len(MODES), MODES[-1]
# method is used. The program terminates when no further progress is being done.
# The program only attempts to rescan already scanned lines
# if MODES[i][1] == True.

LINES_TO_DEBUG = [10]

# ------------------------------------------------------------------------------
# ------------- The Word Class Definition --------------------------------------
# ------------------------------------------------------------------------------


class Word:
    """Represents a word"""

    mqdqit = 0
    total = 0
    A_VOWEL = 'a'


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

    def analyse(self, next_word):
        """
        Decide on the length of the vowels
        :param next_word:
        :return:
        """
        Word.total += 1
        self.meter = mqdqParser.get_quantities(self.word)
        if self.meter:
            Word.mqdqit += 1
            self.in_dict = True
            if next_word:
                vowels = list(re.finditer(SYLLAB, self.word))
                follow = self.word[vowels[-1].end():]
                follow += ' ' + list(re.findall(
                    r'^[' + CONSONANTS + ']*', next_word))[0]
                if re.match(r'[m]? [h]?$', follow) is not None:
                    self.elision = True
                elif decide_on_length(Word.A_VOWEL,
                                      re.sub(' ', '', follow)) == LONG:
                    self.long_by_pos = True
            return

        self.meter = []
        vowels = list(re.finditer(SYLLAB, self.word))
        for i in range(len(vowels) - 1):
            letter = self.word[vowels[i].start():vowels[i].end()]
            follow = self.word[vowels[i].end():vowels[i + 1].start()]
            self.meter.append(decide_on_length(letter, follow))
        letter = self.word[vowels[-1].start():vowels[-1].end()]
        follow = self.word[vowels[-1].end():]
        if next_word:
            follow += ' ' + list(re.findall(
                r'^[' + CONSONANTS + ']*', next_word))[0]
        if re.match(r'[m]? [h]?$', follow) is None:
            follow = re.sub(' ', '', follow)
            self.meter.append(decide_on_length(letter, follow))

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

        Line.line_counter += 1
        string = string.lower()
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
            # print('debug_here')
            pass

        for i in range(len(string)):
            self.line.append(Word(string[i]))
        for i in range(len(self.line) - 1):
            self.line[i].analyse(self.line[i + 1].word)
        self.line[-1].analyse(None)

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


def main(path_to_text, meters, trace=True):
    """
    Load the lines from the file and attempt to scan them. Print some statistic
    at the end. Return the scanned lines
    :param path_to_text: The text to scan
    :param meters: What meter should be used for scanning. E.g., use [HEXAMETER]
    for hexameters and [HEXAMETER, PENTAMETER] for elegiacs
    :param trace: Print statistics?
    :return: list of possible scansions for each line
    """
    lines = []
    result = []
    with open(path_to_text) as file:
        for line in file:
            lines.append(Line(line))
            result.append([])

    print(Word.mqdqit/Word.total)

    progress = -1
    attempt_n = 0
    versions_total = 0
    possible_progress = False

    while (progress != 0 or possible_progress) and (
                    attempt_n < MAX_ATTEMPT or MAX_ATTEMPT == -1):
        possible_progress = False
        if attempt_n >= len(MODES):
            mode = MODES[-1]
        else:
            mode = MODES[attempt_n]
            if mode is None:
                break
        print('This is the ' + str(attempt_n) + 'st/nd/th scansion attempt...')
        empty = 0
        identified = 0
        versions_total_new = 0
        for i in range(len(lines)):
            if not mode[1] and lines[i].scanned:
                versions_total_new += 1
                identified += 1
                continue
            meter = meters[i % len(meters)]
            curr = scansion_versions(lines[i].get_meter(mode[0]), meter, 0)
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


def print_results(lines, output_file):
    """
    Print the results of scansion into the file indicated
    :param lines: Lines to print
    :param output_file: The name of the file to print the files to
    :param meters: What meter should be used for scanning. E.g., use [HEXAMETER]
    for hexameters and [HEXAMETER, PENTAMETER] for elegiacs
    :return:
    """
    with open(output_file, 'w') as file:
        for i in range(len(lines)):
            curr = lines[i]
            to_print = ''
            j = 0
            while j < len(curr):
                for char in curr[j]:
                    to_print += char
                if j < len(curr) - 1:
                    to_print += '|'
                j += 1
            file.write(to_print + '\n')


if __name__ == "__main__":
    """if len(sys.argv) != 3:
        print("Usage: %s input_file_name output_file_name"
              % sys.argv[0])
        sys.exit(-1)
    result = main(sys.argv[1], [HEXAMETER], False)
    print_results(result, sys.argv[2], [HEXAMETER])"""
    # result = main('../texts/Seneca.txt', [TRIMETER], True)
    # print_results(result, '../output/Seneca.txt')
    # result = main('../texts/Thyestes.txt', [TRIMETER], False)
    # print_results(result, '../output/Thyestes.txt')
    result = main('../texts/Ovid_mqdq.txt', [HEXAMETER], True)
    print_results(result, '../output/Ovid_mqdq.txt')
    # result = main('../texts/Aeneid_mqdq.txt', [HEXAMETER], True)
    # print_results(result, '../output/Aeneid_mqdq.txt')
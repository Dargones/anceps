" this module is a tool for automatic creation of n-grams for newsela data "
import math
import random


import scansion
import compare
import sys
is_py2 = sys.version[0] == '2'

# ------------------------------------------------------------------------------
# ------------- The Language Model Class Definition ----------------------------
# ------------------------------------------------------------------------------


class LanguageModel:

    WORD_LENGTH = 4
    LOG_BASE = 2  # log base to use
    WEIGTHS = [7, 3, 3]  # weights for different orders of ngrams
    CONSIDER_AMBIGUOUS = True

    def __init__(self, file_name, order):
        """
        Load a file containing scanned lines and build a language model
        :param file_name: name of the file to read the info from
        :param order:     the order of ngram models to build
        """
        with open(file_name) as file:
            lines = file.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].rstrip('\n')
        self.ngrams = []
        for i in range(order):
            self.ngrams.append({})
        self.total = 0
        self.learn(lines)

    def learn(self, lines):
        """
        Built ngrams based on lines read from a file
        :param lines: the lines read from a file .co format
        :return:
        """
        for i in range(len(lines)):
            if len(lines[i]) == LanguageModel.WORD_LENGTH:
                self.addNGram([lines[i]], 0)
        for i in range(len(lines)):
            for j in range(len(self.ngrams)):
                if j + i < len(lines):
                    if j != 0:
                        self.addNGram(lines[i:i+j+1], j)
                    elif not LanguageModel.CONSIDER_AMBIGUOUS or \
                                    len(lines[i]) != LanguageModel.WORD_LENGTH:
                        self.addNGram([lines[i]], 0)
        """to_print = [""] * (len(self.ngrams[0].keys()) + 1)
        for key, value in self.ngrams[0].items():
            p1 = str(round(value / self.total * 100, 2))
            to_print[0] += key + ": " + p1 + "," + " " * (8 - len(p1))
            j = 0
            for k in self.ngrams[0].keys():
                j += 1
                if k + key in self.ngrams[1]:
                    p2 = str(round(self.ngrams[1][k + key] /
                                   self.ngrams[0][k] * 100, 2))
                else:
                    p2 = '0'
                to_print[j] += key + ": " + p2 + "," + " " * (8 - len(p2))
        for line in to_print:
            print(line)"""

    def addNGram(self, lines, order, weight=1, start=0):
        """
        Add a single Ngram
        :param lines: lines from which to add the ngram
        :param order: order of the ngram
        :param weight: weight to assign to this ngram
        :param start: the index from which to start scanning this ngram for
                    multiple options
        :return:
        """
        if LanguageModel.CONSIDER_AMBIGUOUS:
            for i in range(start, len(lines)):
                if '|' in lines[i]:
                    versions = lines[i].split('|')
                    normalizer = 0
                    for version in versions:
                        normalizer += self.ngrams[0][version]
                    for version in versions:
                        self.addNGram(lines[0:i] + [version] + lines[i+1:],
                                      order, weight * self.ngrams[0][version]/
                                      normalizer, i + 1)
                    return
                elif lines[i] == '':
                    return
        key = ''.join(lines)
        if not LanguageModel.CONSIDER_AMBIGUOUS and \
                        len(key) != (order + 1) * LanguageModel.WORD_LENGTH:
            return
        if key in self.ngrams[order]:
            self.ngrams[order][key] += weight
        else:
            self.ngrams[order][key] = weight
        suffix = key[:-LanguageModel.WORD_LENGTH]
        if len(suffix) == 0:
            self.total += weight

    def evaluate(self, lines):
        """
        Evaluate the model on a testing sample
        :param lines:   the lines on which to evaluate the model
        :return:        the perplexity of teh model
        """
        sequence = []
        p = 0
        n = 0
        for i in range(len(lines)):
            lines[i] = lines[i].rstrip('\n')
            if len(lines[i]) != "" and (len(lines[i]) == LanguageModel.WORD_LENGTH
                                        or LanguageModel.CONSIDER_AMBIGUOUS):
                sequence.append(lines[i])
                if len(sequence) > len(self.ngrams):
                    sequence = sequence[len(sequence) - len(self.ngrams):]
                prob = self.sequence_p(sequence)
                if prob != 0:
                    p += math.log(prob, LanguageModel.LOG_BASE)
                n += 1
            else:
                sequence = []
        if n == 0:
            return 0
        return math.pow(LanguageModel.LOG_BASE, -p/n)

    def sequence_p(self, sequence, weight=1, start=0):
        """
        Return the probability of a particular sequence of words in this
        language model
        :param sequence:
        :param weight: weight to assign to this ngram
        :param start: the index from which to start scanning this ngram for
                    multiple options
        :return:
        """
        if LanguageModel.CONSIDER_AMBIGUOUS:
            for i in range(start, len(sequence)):
                if '|' in sequence[i]:
                    versions = sequence[i].split('|')
                    normalizer = 0
                    for version in versions:
                        normalizer += self.ngrams[0][version]
                    result = 0
                    for version in versions:
                        result += self.sequence_p(
                            sequence[0:i] + [version] + sequence[i+1:],
                            weight * self.ngrams[0][version]/normalizer, i + 1)
                    return result
        newWeigths = []
        probs = []
        for i in range(len(self.ngrams)):
            if i < len(sequence):
                newWeigths.append(LanguageModel.WEIGTHS[i])
                start = len(sequence) - i - 1
                hashable = ''.join(sequence[start:])
                if hashable in self.ngrams[i]:
                    if i == 0:
                        norma = self.total
                    else:
                        norma = self.ngrams[i - 1][''.join(sequence[start:-1])]
                    probs.append(self.ngrams[i][hashable] / norma)
                    continue
            j = i
            while j < len(self.ngrams):
                newWeigths[-1] += LanguageModel.WEIGTHS[j]
                j += 1
            break
        # result = 1
        result = 0
        for i in range(len(probs)):
            # result *= pow(probs[i], newWeigths[i])
            result += probs[i]* newWeigths[i]
        return result


def prepare(l, recompute=True, trace=False):
    """
    Scan all the files needed for language model evaluation
    :param l:
    :param recompute:
    :param trace: if True, will print intermediate results
    :return:
    """
    for file in l:
        if trace:
            print('Preparing ' + file + '...')
        if recompute:
            scansion.main('input/' + file, 'output/dict.txt', 'output/usual/' +
                     file)
            compare.co_format('output/usual/' + file, 'output/usual/' + file)


def comp_lms(m1, m2, samples1, samples2, sSize, sN, recompute=False,
             trace=False):
    """
    Compare how well two language model determine authorship
    :param m1: the first model to use
    :param m2: the second
    :param samples1: list of files that belong to the first model
    :param samples2: - to the second
    :param sSize:   the size of sample with which to feed the models when
                        evaluating them
    :param sN:      number of samples per file in samples1 and samples2
    :param recompute  if True, the program will rescan all the files
    :param trace: if True, will print intermediate results
    :return: the overall accuracy
    """
    if trace:
        print("Scanning...")
    prepare(samples1 + samples2, recompute, trace)
    if trace:
        print("Evaluating the first model...")
    u1_count = 0
    for sample in samples1:
        sample = 'output/usual/' + sample
        if trace:
            print("File: " + sample)
        with open(sample) as file:
            s = file.readlines()
        count = 0
        for j in range(sN):
            # while True:
            begin = random.randint(0, len(s) - sSize)
            lines = s[begin:begin + sSize]
                # if len("".join(lines)) == \
                                # sSize * (LanguageModel.WORD_LENGTH + 1):
                    # break
            p1 = m1.evaluate(lines)
            p2 = m2.evaluate(lines)
            if p1 < p2:
                count += 1
        if trace:
            print("True: " + str(count) + " False: " + str(sN - count))
        u1_count += count
    u2_count = 0
    if trace:
        print("Evaluating the second model...")
    for sample in samples2:
        sample = 'output/usual/' + sample
        if trace:
            print("File: " + sample)
        with open(sample) as file:
            s = file.readlines()
        count = 0
        for j in range(sN):
            begin = random.randint(0, len(s) - sSize)
            lines = s[begin:begin + sSize]
            p1 = m1.evaluate(lines)
            p2 = m2.evaluate(lines)
            if p1 > p2:
                count += 1
        if trace:
            print("True: " + str(count) + " False: " + str(sN - count))
        u2_count += count
    if trace:
        print("--------Results for model1-----------\n" +
          "True: " + str(u1_count) + " False: " +
          str(sN * len(samples1) - u1_count))
    if trace:
        print("--------Results for model2-----------\n" +
          "True: " + str(u2_count) + " False: " +
          str(sN * len(samples2) - u2_count))
    accuracy = (u1_count + u2_count) / sN / (len(samples1) + len(samples2))
    if trace:
        print("Overall accuracy: " + str(accuracy))
    return accuracy


if __name__ == '__main__':
    TIMES_TO_REPEAT = 100
    # samples1 = ['6', '7', '8', '9', '10', '11', '12']
    # samples2 = ['6', '7', '8', '9', '10', '11', '12', '13', '14', '15']
    samples1 = ['s6_12']
    samples2 = ['s6_15']
    m1_prefix = 'Aeneid/book'
    m2_prefix = 'Metamorphoses/book'
    m1_postfix = '.txt'
    m2_postfix = '.txt'
    m_names = ['Aeneid/books1_5.txt', 'Metamorphoses/books1_5.txt']
    prepare(m_names, False)
    for i in range(len(samples1)):
        samples1[i] = m1_prefix + samples1[i] + m1_postfix
    for i in range(len(samples2)):
        samples2[i] = m2_prefix + samples2[i] + m2_postfix
    """avg = 3 * [0]
    for i in range(len(avg)):
        m1 = LanguageModel('output/usual/' + m_names[0], i + 1)
        m2 = LanguageModel('output/usual/' + m_names[1], i + 1)
        print("Testing " + str(i + 1) + "-grams...")
        for j in range(TIMES_TO_REPEAT):
            print(str(round(j/TIMES_TO_REPEAT * 100, 0)) + "% done...")
            avg[i] += comp_lms(m1, m2, samples1, samples2,
                               30, 100, False)
        avg[i] /= TIMES_TO_REPEAT
    print(avg)"""
    sampleSizes = [1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    results = []
    m1 = LanguageModel('output/usual/' + m_names[0], 1)
    m2 = LanguageModel('output/usual/' + m_names[1], 1)
    for size in sampleSizes:
        print("Testing size of " + str(size))
        threshold = 0
        threshold_step = 0.2
        tmp = 0
        for j in range(TIMES_TO_REPEAT):
            if j / TIMES_TO_REPEAT >= threshold:
                print(str(round(j / TIMES_TO_REPEAT * 100, 0)) + "% done...")
                threshold += threshold_step
            tmp += comp_lms(m1, m2, samples1, samples2, size, 100, False)
        results.append(tmp/TIMES_TO_REPEAT)
    print(results)


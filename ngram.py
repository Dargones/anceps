"""
This module is a tool for simple author detection using ngram-language-models
Usage: python3 ngram.py model1 model2 sample1 sample2 sampleSize timesToRepeat
where model1    is the name of the file on which to build the first language
                model (it will be automatically scanned by the program). This
                file should be in the input folder. If the file is input/x.txt,
                then the parameter should be just x.txt. The same holds for the
                rest of the parameters
      model2    --- "" --- same for the second model
      sample1   is the name of the file from which to take testing samples that
                    are written by the same author as model1
      sample2       --- "" --- same for the second model
      sampleSize    the size of the samples on which to evaluate the perplexity
      timesToRepeat the number of samples to draw from each of sample1 and
                    sample2

"""
from __future__ import division
import math
import random
import sys

import scansion
import compare

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
        result = 0
        for i in range(len(probs)):
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
            scansion.main('input/' + file, 'output/' +
                     file, trace=False)
            compare.co_format('output/' + file, 'output/' + file)


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
        print("Evaluating the first model...")
    u1_count = 0
    for sample in samples1:
        sample = 'output/' + sample
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
        sample = 'output/' + sample
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


def main(m_names, samples1, samples2, samplesSize, timesToRepeat):
    """
    See the description at the top of the file
    :param m_names:
    :param samples1:
    :param samples2:
    :param samplesSize:
    :param timesToRepeat:
    :return:
    """
    RECOMPUTE = True
    print('Scanning the models...')
    prepare(m_names, RECOMPUTE, True)
    print('Scanning the samples...')
    prepare(samples1 + samples2, RECOMPUTE, True)
    avg = 3 * [0]
    for i in range(len(avg)):
        m1 = LanguageModel('output/' + m_names[0], i + 1)
        m2 = LanguageModel('output/' + m_names[1], i + 1)
        print("Testing " + str(i + 1) + "-grams...")
        avg[i] = comp_lms(m1, m2, samples1, samples2,
                           samplesSize, timesToRepeat, False)
    for i in range(len(avg)):
        print("Accuracy for " + str(i+1) + "-grams: " + str(
            round(avg[i] * 100, 1)) + "%")

if __name__ == '__main__':
    if len(sys.argv) != 7:
        print("Usage: %s model1 model2 sample1 sample2 sampleSize timesToRepeat"
              % sys.argv[0])
        sys.exit(-1)
    main([sys.argv[1], sys.argv[2]], [sys.argv[3]], [sys.argv[4]],
         int(sys.argv[5]), int(sys.argv[6]))

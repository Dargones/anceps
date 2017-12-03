"""
This module contains the utilities that should help to evaluate algorithm's
performance.
python3 compare.py input_file_name test_file_name
where input_file_name          is the name of the file that contains the lines
                               scanned by scanasion.py
      test_file_name           the name of the file that contains the answer key
                               to some part of input file. The performance of
                               the algorithm is evaluated by comparing
                               input_file_name against test_file_name

"""
import sys
import random

from utilities import *


def clear(string):
    """
    take a string, return its meter version
    :param string:
    :return:
    """
    SHORT_MARKED = 'ĂăĕĬĭŎŏŭŷ'
    LONG_MARKED = 'ĀāēĪīōŪūȳ'
    string = re.sub(r'[^' + LONG_MARKED + SHORT_MARKED + ']', '', string)
    string = re.sub(r'[' + SHORT_MARKED + ']', SHORT, string)
    return re.sub(r'[' + LONG_MARKED + ']', LONG, string) + '\n'


def clear_file(text_name):
    with open(text_name) as file:
        lines = list(map(clear, file.readlines()))
    with open(text_name, 'w') as file:
        file.writelines(lines)


def print_stats(text):
    """
    Print the statistics about the frequency of specific meter patterns
    :param text: the output of teh algorithm
    :return:
    """
    print("Distribution of meter patterns:")
    meters = {}
    with open(text) as file:
        lines = file.readlines()
    count = 0
    for line in lines:
        if UNK in line or '|' in line:
            continue
        count += 1
        line = line.rstrip('\n')
        line = re.sub(LONG+'\\'+SHORT+'\\'+SHORT, 'D', line)
        line = re.sub(r'(' + LONG+LONG+'|' + LONG+ANCEPS + ')', 'S', line)
        line = line[:4]
        if line in meters:
            meters[line] += 1
        else:
            meters[line] = 1
    for meter in sorted(meters.keys()):
        print(meter + ': ' + str(round(meters[meter] / count * 100, 2)) + '%')


def co_format(text, new_format_text):
    """
    Convert the LONG_SHORT format of algorithm's output to the DACTYL-SPONDEE
    format. Example: _^^___^^_^^_^^_X = DSDD
    :param text:
    :param new_format_text:
    :return:
    """
    with open(text) as file:
        old = file.readlines()
    with open(new_format_text, 'w') as file:
        for line in old:
            if UNK in line:
                file.write('\n')
                continue
            line= line.rstrip('\n')
            versions = line.split('|')
            for i in range(len(versions) - 1):
                version = versions[i]
                version = re.sub(LONG + '\\' + SHORT + '\\' + SHORT, 'D', version)
                version = re.sub(r'(' + LONG + LONG + '|' + LONG + ANCEPS + ')','S', version)
                file.write(version[:4] + '|')
            versions[-1] = re.sub(LONG + '\\' + SHORT + '\\' + SHORT, 'D', versions[-1])
            versions[-1] = re.sub(r'(' + LONG + LONG + '|' + LONG + ANCEPS + ')',
                             'S', versions[-1])
            file.write(versions[-1][:4] + '\n')


def compare(man, auto, text):
    countTrue = 0
    countFalse = 0
    countNotSizedId = 0
    countNotSizedEp = 0
    countNotSizedMult = 0
    countEmpty = 0
    countPTrue = 0
    countPFalse = 0
    with open(man) as file:
        m = file.readlines()
    with open(auto) as file:
        a = file.readlines()
    with open(text) as file:
        t = file.readlines()
    for i in range(len(m[i])):
        m[i] = m[i].rstrip('\n')
        a[i] = a[i].rstrip('\n')
        t[i] = t[i].rstrip('\n')
        print(str(i) + ":\t" + t[i])
        if UNK in a[i]:
            print("[] - failed to determine the meter\n")
            countEmpty += 1
            if len(a[i]) != len(m[i]):
                countNotSizedEp += 1
            continue
        versions = a[i].split('|')
        if len(versions) == 1:
            if a[i] == m[i]:
                countTrue += 1
                print(a[i] + " - correct\n")
            else:
                print(a[i] + " - incorrect\n")
                countFalse += 1
                if len(a[i]) != len(m[i]):
                    countNotSizedId += 1
        else:
            found = False
            for version in versions:
                if version == m[i]:
                    found = True
                    break
            if found:
                countPTrue += 1
                print(a[i] + ", of which " + m[i] + " is correct\n")
            else:
                print(a[i] + ", of which no are correct\n")
                countPFalse += 1
                if len(versions[-1]) != len(m[i]):
                    countNotSizedMult += 1
    den = (countFalse+countTrue+countPFalse+countPTrue+countEmpty)
    cNSE = str(countNotSizedEp) + ' (' + str(round(
        countNotSizedEp / countEmpty * 100, 1)) + '%)'
    cNSI = str(countNotSizedId) + ' (' + str(round(
        countNotSizedId / countFalse * 100, 1)) + '%)'
    if countPFalse == 0:
        cNSM = str(countNotSizedMult) + ' (0%)'
    else:
        cNSM = str(countNotSizedMult) + ' (' + str(round(
            countNotSizedMult / countPFalse * 100, 1)) + '%)'
    cT = str(countTrue) + ' (' + str(round(countTrue / den * 100, 1)) + '%)'
    cF = str(countFalse) + ' (' + str(round(
        countFalse / den * 100, 1)) + '%)\tof this syll-err: ' + cNSI
    cPT = str(countPTrue) + ' (' + str(round(countPTrue / den * 100, 1)) + '%)'
    cPF = str(countPFalse) + ' (' + str(round(
        countPFalse / den * 100, 1)) + '%)\tof this syll-err: ' + cNSM
    cE = str(countEmpty) + ' (' + str(
        round(countEmpty / den * 100, 1)) + '%)\tof this syll-err: ' + cNSE
    total_not_sized = countNotSizedMult + countNotSizedId + countNotSizedEp
    cNST = str(total_not_sized) + ' (' + str(
        round((total_not_sized) / (
            countEmpty + countFalse + countPFalse) * 100, 1)) + '%)'

    print("\n\ncTrue:    " + cT + "\ncFalse:   " + cF + "\ncPTrue:   " + cPT
          + "\ncPFalse:  " + cPF + "\ncEmpty:   " + cE + "\ncNotSize: " + cNST)


def ngram_format(text, new_format_text, sub_section=False, size=100):
    """
    Convert the LONG_SHORT format of algorithm's output to the DACTYL-SPONDEE
    format. Example: _^^___^^_^^_^^_X = DSDD. Also, make this prepared for
    building an n-gram model
    :param text:
    :param new_format_text:
    :return:
    """
    with open(text) as file:
        old = file.readlines()
    if sub_section and (size < len(old)):
        begin = random.randint(0, len(old) - size)
        end = begin + size
    else:
        begin = 0
        print('WARNING: in compare.py/ngram_format')
        end = len(old)
    with open(new_format_text, 'w') as file:
        newline = True
        i = -1
        for line in old:
            i += 1
            if (UNK in line) or ('|' in line):
                if not newline:
                    if (i > begin) and (i < end):
                        file.write(' ')
                    newline = True
                continue
            line = line.rstrip('\n')
            line = re.sub(LONG + '\\' + SHORT + '\\' + SHORT, 'D', line)
            line = re.sub(r'(' + LONG + LONG + '|' + LONG + ANCEPS + ')',
                          'S', line)
            if newline:
                if (i >= begin) and (i < end):
                    file.write(line[:4])
                newline = False
            elif (i >= begin) and (i < end):
                file.write(' ' + line[:4])


def compare_dictionaries(dict1, dict2):
    MIN_LENGTH = 3
    with open(dict1) as file:
        d1 = file.readlines()
    with open(dict2) as file:
        d2 = file.readlines()
    i = 0
    j = 0
    while (i < len(d1)) and (j < len(d2)):
        curr1 = d1[i].split(' ')
        curr2 = d2[j].split(' ')
        if curr1[0] < curr2[0]:
            i += 1
        elif curr1[0] > curr2[0]:
            j += 1
        else:
            l1 = len(curr1[2].split('|'))
            l2 = len(curr2[2].split('|'))
            if UNK in merge_lists(curr1[1], curr2[1], True) and l1 >= MIN_LENGTH\
                    and l2 >= MIN_LENGTH:
                print(d1[i] + '\n' + d2[j] + '\n\n')
            i += 1
            j += 1

def compare_co_format(man, auto, text=None):
    """
    Read the two files, one of which contains the output of the algorithm, and
    the other the "correct" data from the testing set and report algorithm's
    performance
    :param man:  the file with correct results
    :param auto: the file with algorithm's output
    :return:
    """
    versions = ['DDDD', 'DDDS', 'DDSD', 'DDSS', 'DSDD', 'DSDS', 'DSSD', 'DSSS',
                'SDDD', 'SDDS', 'SDSD', 'SDSS', 'SSDD', 'SSDS', 'SSSD', 'SSSS']
    countTrue = 0
    countFalse = 0
    countEmpty = 0
    countPTrue = 0
    countPFalse = 0
    result = {}
    for v in versions:
        result[v] = {}
        for v2 in versions:
            result[v][v2] = 0
    with open(man) as file:
        m = file.readlines()
    with open(auto) as file:
        a = file.readlines()
    if text:
        with open(text) as file:
            t = file.readlines()
    else:
        t = None
    for i in range(len(m)):
        m[i] = m[i].rstrip('\n ').split(' ')[0]
        a[i] = a[i].rstrip('\n')
        if a[i] == '':
            countEmpty += 1
            if t:
                print(t[i] + str(i) + ': ' + m[i] + '\n')
            continue
        versions = a[i].split('|')
        if len(versions) == 1:
            result[m[i]][a[i]] += 1
            if a[i] == m[i]:
                countTrue += 1
            else:
                countFalse += 1
        else:
            found = False
            for version in versions:
                if version == m[i]:
                    found = True
                    break
            if found:
                countPTrue += 1
            else:
                countPFalse += 1
    den = (countFalse+countTrue+countPFalse+countPTrue+countEmpty)
    cT = str(countTrue) + ' (' + str(round(countTrue / den * 100, 1)) + '%)'
    cF = str(countFalse) + ' (' + str(round(
        countFalse / den * 100, 1)) + '%)'
    cPT = str(countPTrue) + ' (' + str(round(countPTrue / den * 100, 1)) + '%)'
    cPF = str(countPFalse) + ' (' + str(round(
        countPFalse / den * 100, 1)) + '%)'
    cE = str(countEmpty) + ' (' + str(
        round(countEmpty / den * 100, 1)) + '%)'

    print("\n\nIdentified correctly:    " + cT + "\nIdentified incorrectly:   "
          + cF + "\nTwo or more possible versions given, among those there is a"
                 " correct one:   " + cPT
          + "\nTwo or more possible versions given, among those all are "
            "incorrect:  " + cPF + "\nFailed to determine the meter:   " + cE)\

    for r in result.values():
        print(r.values())


def main(path_to_result, path_to_test, text=None):
    print_stats(path_to_result)
    new_format_file_name = '.'.join(path_to_result.split('.')[:-1])+'.co.txt'
    co_format(path_to_result, new_format_file_name)
    compare_co_format(path_to_test, new_format_file_name, text)


if __name__ == "__main__":
    """if len(sys.argv) != 3:
        print("Usage: %s program_output_file_name answer_key_file_name"
              % sys.argv[0])
        sys.exit(-1)
    main(sys.argv[1], sys.argv[2])"""
    # main('output/scanned.txt', 'input/manual_result.txt', 'input/input.txt')
    # clear_file('input/small_test.txt')
    compare('input/small_test.txt', 'output/scanned.txt', 'input/aeneid.txt')
    # compare_dictionaries('output/dict.txt', 'output/dict_2.txt')
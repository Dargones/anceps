"""
This module contains the utilities that should help to evaluate algorithm's
performance.
python3 compare.py input_file_name test_file_name text_file_name format
where input_file_name          is the name of the file that contains the lines
                               scanned by scanasion.py
      test_file_name           the name of the file that contains the answer key
                               to some part of input file. The performance of
                               the algorithm is evaluated by comparing
                               input_file_name against test_file_name
      text_file_name           the file with initial text
      format                   either 'longshort' - in which case the format of
                               the test file should be _^^_^^_^^___^^_X
                               or 'dactylspondee', in which case the format of
                               the test file should be DDDS

"""
from __future__ import division
import sys

from utilities import *


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
    """
    Compare the manual results with automatically generated results.
    :param man:
    :param auto:
    :param text:
    :return:
    """
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
    for i in range(len(m)):
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

    print("\n\nIdentified correctly:    " + cT + "\nIdentified incorrectly:   "
          + cF + "\nTwo or more possible versions given, among those there is a"
                 " correct one:   " + cPT
          + "\nTwo or more possible versions given, among those all are "
            "incorrect:  " + cPF + "\nFailed to determine the meter:   " +
          cE + "\ncNotSize: " + cNST)


def compare_co_format(man, auto):
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
    for i in range(len(m)):
        m[i] = m[i].rstrip('\n ').split(' ')[0]
        a[i] = a[i].rstrip('\n')
        if a[i] == '':
            countEmpty += 1
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
            "incorrect:  " + cPF + "\nFailed to determine the meter:   " + cE)
    print("\nConfusion matrix:")
    line = "     "
    for key in result.keys():
        line += key + " "
    print(line)
    for key, value in result.items():
        line = key + " "
        for v in value.values():
            line += str(v) + (5 - len(str(v))) * " "
        print(line)


def main(path_to_result, path_to_test, path_to_text, format):
    print_stats(path_to_result)
    if not format:
        new_format_file_name = '.'.join(path_to_result.split('.')[:-1]) + \
                               '.co.txt'
        co_format(path_to_result, new_format_file_name)
        compare_co_format(path_to_test, new_format_file_name)
    else:
        compare(path_to_test, path_to_result, path_to_text)


if __name__ == "__main__":
    if len(sys.argv) != 5 or ((sys.argv[4] != 'longshort') and (
                sys.argv[4] != 'dactylspondee')):
        print("Usage: " + sys.argv[0] + " program_output_file_name " +
              "answer_key_file_name text_file_name format" +
              "[longshort|dactylspondee]")
        sys.exit(-1)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == 'longshort')
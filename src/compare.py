"""
This module contains utilities for evaluating algorithm's performance.
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
import sys
from src.utilities import *
from src.analyze import print_stats


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
                file.write(version[:5] + '|')
            versions[-1] = re.sub(LONG + '\\' + SHORT + '\\' + SHORT, 'D', versions[-1])
            versions[-1] = re.sub(r'(' + LONG + LONG + '|' + LONG + ANCEPS + ')',
                             'S', versions[-1])
            file.write(versions[-1][:5] + '\n')


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
        if '\t' in m[i]:
            m[i] = re.sub('[^\\^_&]', '', m[i])
        else:
            m[i] = re.sub('[^\\^_&X]', '', m[i].split('|')[-1])
        ma = re.sub('&', 'X', m[i])
        a[i] = re.sub('[ \n]', '', a[i].split('\t')[0])
        t[i] = re.sub('[^a-zA-Z ]', '', t[i])
        if UNK in a[i]:
            print(str(i) + ":\t" + t[i])
            print("Program failed to determine the meter. \nCorrect scansion: " + ma + '\n')
            countEmpty += 1
            if len(a[i]) != len(m[i]):
                countNotSizedEp += 1
            continue
        versions = a[i].split('|')
        if len(versions) == 1:
            if meters_are_equal(a[i], m[i]):
                countTrue += 1
                # print(a[i] + " - correct\n")
            else:
                print(str(i) + ":\t" + t[i])
                print("Incorrect answer. Program output: " + a[i] + "\nCorrect scansion: " + ma + '\n')
                countFalse += 1
                if len(a[i]) != len(m[i]):
                    countNotSizedId += 1
        else:
            print(str(i) + ":\t" + t[i])
            print("Multiple answers. Program output: " + a[i] + "\nCorrect scansion: " + ma + '\n')
            found = False
            for version in versions:
                if meters_are_equal(version, m[i]):
                    found = True
                    break
            if found:
                countPTrue += 1
                # print(a[i] + ", of which " + m[i] + " is correct\n")
            else:
                # print(a[i] + ", of which no are correct\n")
                countPFalse += 1
                if len(versions[-1]) != len(m[i]):
                    countNotSizedMult += 1
    den = (countFalse+countTrue+countPFalse+countPTrue+countEmpty)
    if countEmpty == 0:
        cNSE = '0'
    else:
        cNSE = str(countNotSizedEp) + ' (' + str(round(
            countNotSizedEp / countEmpty * 100, 1)) + '%)'
    if countFalse == 0:
        cNSI = '0'
    else:
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
    if countEmpty + countFalse + countPFalse == 0:
        cNST = '0'
    else:
        cNST = str(total_not_sized) + ' (' + str(
            round((total_not_sized) / (
                countEmpty + countFalse + countPFalse) * 100, 1)) + '%)'

    print("\n\nIdentified correctly:    " + cT + "\nIdentified incorrectly:   "
          + cF + "\nTwo or more possible versions given, among those there is a"
                 " correct one:   " + cPT
          + "\nTwo or more possible versions given, among those all are "
            "incorrect:  " + cPF + "\nFailed to determine the meter:   " +
          cE + "\ncNotSize: " + cNST)


def compare_winge(native_file, winge_file):
    native = open(native_file).readlines()
    while native[0][:2] != "*/":
        del native[0]
    del native[0:2]
    winge = open(winge_file).readlines()
    assert(len(native) == len(winge))
    print(native_file.split('/')[-1])
    for i in range(len(native)):
        line, _, meter, marks = native[i].split('\t')
        if meter != winge[i].rstrip('\n') and winge[i] != '\n':
            print(line + '\t' + meter + '\t' + marks + 'Winge:' + " " * (len(line) - 6) + "\t" + winge[i])
            # print(line)
    """print("\n Unscanned: ")
    for i in range(len(native)):
        line, _, meter, marks = native[i].split('\t')
        if winge[i] == '\n':
            print(line + '\t' + meter + '\t' + marks.rstrip('\n'))"""



def compare_co_format(man, auto, text):
    """
    Read the two files, one of which contains the output of the algorithm, and
    the other the "correct" data from the testing set and report algorithm's
    performance
    :param man:  the file with correct results
    :param auto: the file with algorithm's output
    :return:
    """
    versions = ['DDDDD', 'DDDSD', 'DDSDD', 'DDSSD', 'DSDDD', 'DSDSD', 'DSSDD', 'DSSSD',
                'SDDDD', 'SDDSD', 'SDSDD', 'SDSSD', 'SSDDD', 'SSDSD', 'SSSDD', 'SSSSD',
                'DDDDS', 'DDDSS', 'DDSDS', 'DDSSS', 'DSDDS', 'DSDSS', 'DSSDS', 'DSSSS',
                'SDDDS', 'SDDSS', 'SDSDS', 'SDSSS', 'SSDDS', 'SSDSS', 'SSSDS', 'SSSSS'
                ]
    countTrue = 0
    countFalse = 0
    countEmpty = 0
    countPTrue = 0
    countPFalse = 0
    cNotSize = 0;
    result = {}
    for v in versions:
        result[v] = {}
        for v2 in versions:
            result[v][v2] = 0
    with open(man) as file:
        m = file.readlines()
    with open(auto) as file:
        a = file.readlines()
    with open(text) as file:
        t = file.readlines()
    for i in range(len(m)):
        m[i] = m[i].rstrip('\n ').split(' ')[0]
        a[i] = a[i].rstrip('\n')
        if len(m[i]) == 4:
            m[i] += 'D'
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
                print(t[i] + ' auto:' + a[i] + ' man:' + m[i] + ' id:' + str(i))
                if len(list(re.finditer('S', m[i]))) != len(list(re.finditer('S', a[i]))):
                    cNotSize += 1;
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
    print("\nNot right number of syllables: " + str(cNotSize) + " ("
          + str(round(cNotSize / countFalse * 100, 1)) + "%)");
    print("\nConfusion matrix:")
    line = "     "
    for key in result.keys():
        line += key + " "
    print(line)
    for key, value in result.items():
        line = key + " "
        for v in value.values():
            line += str(v) + (6 - len(str(v))) * " "
        print(line)


def main(path_to_result, path_to_test, path_to_text, format):
    print_stats(path_to_result, not format)
    if not format:
        new_format_file_name = '.'.join(path_to_result.split('.')[:-1]) + \
                               '.co.txt'
        co_format(path_to_result, new_format_file_name)
        compare_co_format(path_to_test, new_format_file_name, path_to_text)
    else:
        compare(path_to_test, path_to_result, path_to_text)


if __name__ == "__main__":
    names = ["Medea.txt", "Oedipus.txt", "Hercules_Oetaeus.txt", "Hercules_furens.txt",
             "Troades.txt", "Phoenissae.txt", "Octavia.txt", "Phaedra.txt"]
    """if len(sys.argv) != 5 or ((sys.argv[4] != 'longshort') and (
                sys.argv[4] != 'dactylspondee')):
        print("Usage: " + sys.argv[0] + " program_output_file_name " +
              "answer_key_file_name text_file_name format" +
              "[longshort|dactylspondee]")
        sys.exit(-1)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == 'longshort')"""
    for name in names:
        compare_winge("/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/completedScansions/" + name,
                  "/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/winge/" + name)
        print('\n\n\n\n\n\n\n\n')
    """main("output/input.txt", "testing_data/input_test.txt", "texts/input.txt",
         False)"""
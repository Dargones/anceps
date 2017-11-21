from utilities import *

MIN_LENGTH = 3

def clear(string):
    """
    take a string, return its meter version
    :param string:
    :return:
    """
    string = re.sub(r'[^' + LONG_MARKED + SHORT_MARKED + ']', '', string)
    string = re.sub(r'[' + SHORT + ']', SHORT, string)
    return re.sub(r'[' + LONG + ']', LONG, string)


def clear_file(text_name):
    with open(text_name) as file:
        lines = list(map(clear, file.readlines()))
    with open(text_name, 'w') as file:
        file.writelines(lines)


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
    for i in range(len(m)):
        m[i] = m[i].rstrip('\n')
        a[i] = a[i].rstrip('\n')
        t[i] = t[i].rstrip('\n')
        if UNK in a[i]:
            countEmpty += 1
            if len(a[i]) != len(m[i]):
                countNotSizedEp += 1
                print(t[i], i, ' e\n')
            continue
        versions = a[i].split('|')
        if len(versions) == 1:
            if a[i] == m[i]:
                countTrue += 1
            else:
                countFalse += 1
                if len(a[i]) != len(m[i]):
                    countNotSizedId += 1
                    print(t[i], i, 'i\n')
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
                if len(versions[-1]) != len(m[i]):
                    countNotSizedMult += 1
                    print(t[i], i, 'm\n')
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


def compare_dictionaries(dict1, dict2):
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


def print_stats(text):
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


def compare_co_format(man, auto, text):
    countTrue = 0
    countFalse = 0
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
        m[i], rating = m[i].rstrip('\n ').split(' ')
        a[i] = a[i].rstrip('\n')
        t[i] = t[i].rstrip('\n')
        if a[i] == '':
            countEmpty += 1
            continue
        versions = a[i].split('|')
        if len(versions) == 1:
            if a[i] == m[i]:
                countTrue += 1
            else:
                print(t[i], i, ' if\n')
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

    print("\n\ncTrue:    " + cT + "\ncFalse:   " + cF + "\ncPTrue:   " + cPT
          + "\ncPFalse:  " + cPF + "\ncEmpty:   " + cE)


if __name__ == '__main__':
    # clear_file(PATH_TO_TEST)
    # compare(PATH_TO_TEST, PATH_TO_RESULT, PATH_TO_TEXT)
    # compare_dictionaries(PATH_TO_AUTO_DICT, PATH_TO_AUTO_DICT2)
    # print_stats(PATH_TO_RESULT)
    co_format(PATH_TO_RESULT, PATH_TO_NEW_FORMAT)
    compare_co_format(PATH_TO_TEST, PATH_TO_NEW_FORMAT, PATH_TO_TEXT)
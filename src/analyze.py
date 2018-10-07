import re
from src.scansion import scansion_versions
from src.utilities import *


MONOLOGUE_LENGTH = 4
WINDOW_LEN = 100
SEARCH_LEN = 5
LIMIT = 0


def get_all_meter_types(meter):
    """
    Get all variations of a given meter
    :param meter:
    :return:
    """
    i = 1
    meter_found = False
    result = []
    variations = scansion_versions(UNK * i, meter, 0)
    while not meter_found or variations != []:
        if variations != []:
            meter_found = True
        result += variations
        variations = scansion_versions(UNK * i, meter, 0)
        i += 1
    return result


def print_stats(text, dactylsponcee=False, meter=TRIMETER):
    """
    Print the statistics about the frequency of specific meter patterns
    :param text: the output of the algorithm
    :param dactylsponcee: whether the file is in dactylspondee format or not
    :param meter: the type of meter in which the work in question is written
    :return:
    """
    print("Distribution of meter patterns:")
    with open(text) as file:
        lines = file.readlines()

    meters = {' '.join(x): 0 for x in get_all_meter_types(meter)}
    count = 0
    for line in lines:
        if UNK in line or '|' in line:
            continue
        count += 1
        line = line.rstrip('\n')
        if dactylsponcee:
            line = re.sub(LONG + '\\' + SHORT + '\\' + SHORT, 'D', line)
            line = re.sub(r'(' + LONG + LONG + '|' + LONG + ANCEPS + ')', 'S',
                          line)
            line = line[:4]
        meters[line] += 1
    for pattern in meters.keys():
        print(pattern + '\t' + str(meters[pattern]) + '\t' + str(
            round(meters[pattern] / count * 100, 2)) + '%')


def get_stats(full_text_file, text_file, supplement, output):
    all_trimeters = []
    for i in range(12, 21):
        all_trimeters += scansion.scansion_versions(UNK * i, utilities.TRIMETER, 0)

    dict = {}
    for meter in all_trimeters:
        dict[''.join(meter)] = 0

    max_for_len = []
    for i in range(SEARCH_LEN + 1):
        max_for_len.append((0, 0, 0))

    resolutions = 0
    anceps_resolution = 0
    speaker_stats = {}
    monologue_stats = []
    speaker_stats["Mixed"] = [0, 0]
    speakers = []
    last = ""
    big_long_line = ""
    trimeter_break = False
    with open(full_text_file) as file:
        for line in file:
            if line[0] == '$':
                if '*' in line:
                    trimeter_break = True
                    last = line[1:-3]
                else:
                    last = line[1:-2]
            elif '$' in line:
                speakers.append(("Mixed", trimeter_break))
                trimeter_break = False
                line = line.split('$')
                last = line[-2]
                if (len(speakers) == 1) or (speakers[-1][0] != speakers[-2][0]):
                    monologue_stats.append(
                        [speakers[-1][0], len(speakers) - 1, 0, 0])
            else:
                speakers.append((last, trimeter_break))
                trimeter_break = False
                if (len(speakers) == 1) or (speakers[-1][0] != speakers[-2][0]):
                    monologue_stats.append(
                        [speakers[-1][0], len(speakers) - 1, 0, 0])
            if last not in speaker_stats:
                speaker_stats[last] = [0, 0];

    mon = 0
    info = []

    with open(output) as file:
        lines = file.readlines()

    with open(supplement) as file:
        supp = file.readlines()
        for i in range(len(supp)):
            line = supp[i].split(MANY)[0]
            text = re.sub(r'[\^_&]', '', line).rstrip(' \t\n')
            meter = re.sub(UNK, ANCEPS, re.sub(r'[^\^_&]', '', line))
            supp[i] = [text, meter]



    with open(text_file) as file:
        text = file.readlines()
        for i in range(len(text)):
            found = False
            unk = UNK in lines[i] or MANY in lines[i]
            for j in range(len(supp)):
                if supp[j][0] == text[i].rstrip(' \t\n'):
                    if unk:
                        lines[i] = supp[j][1]
                    elif not equal(lines[i].rstrip('\n'), supp[j][1]):
                        print("Problem " + str(lines[i]) + " " + str(supp[j][1]) + "\n")
                        pass
                    found = True
                    break
            if unk:
                if not found:
                    print("Cannot scan: " + text[i])
                else:
                    found = False
                    for trimeter in all_trimeters:
                        if equal(''.join(trimeter), lines[i]):
                            print(text[i].rstrip(' \t\n') + " | " + ''.join(trimeter) + " - scansion obtained manualy")
                            lines[i] = ''.join(trimeter)
                            found = True
                            break
                    if not found:
                        print("\n\nmeter not found: " + text[i] + "\n\n")
            else:
                lines[i] = lines[i].rstrip('\n')
                print(text[i].rstrip(' \t\n') + " | " + lines[i])
            dict[lines[i]] += 1

    for key in dict.keys():
        print(str(dict[key]))

    for i in range(len(lines)):
        if mon != len(monologue_stats) - 1 and i == monologue_stats[mon + 1][1]:
            mon += 1
        entry = lines[i]
        speaker_stats[speakers[i][0]][1] += 1
        monologue_stats[mon][2] += 1
        r_count = len(re.findall(r'[\\' + SHORT + ']{2}', entry))
        if r_count != 0:
            resolutions += r_count
            anceps_resolution += 4 - len(re.findall(r'[' + ANCEPS + ']', entry))
            speaker_stats[speakers[i][0]][0] += r_count
            monologue_stats[mon][3] += r_count
            # big_long_line += '|' * r_count + '.' * (4 - r_count)
            big_long_line += ' ' + str(r_count)
            if len(re.findall(r'[\\' + SHORT + ']{6}', entry)) != 0:
                print("WARNING: Long resolution sequence")
        else:
            # big_long_line += '....'
            big_long_line += ' 0'

        if speakers[i][1]:
            info = []
        info.append(r_count)
        if len(info) > SEARCH_LEN:
            del info[0]
        if len(info) == SEARCH_LEN and sum(info) <= LIMIT:
            print(str(i - SEARCH_LEN + 1) +
                  "-" + str(i) + ": " + str(sum(info)))
            # big_long_line = big_long_line[: -4 * SEARCH_LEN]
            # big_long_line += 4 * SEARCH_LEN * '*'
            big_long_line = big_long_line[: -2 * SEARCH_LEN]
            big_long_line += 2 * SEARCH_LEN * '*'

        for j in range(len(info)):
            count = sum(info[j:])
            if max_for_len[len(info) - j][0] < count:
                max_for_len[len(info) - j] = (
                    count, str(i - len(info) + j), str(i))

    print('\n')

    for i in range(len(max_for_len)):
        print(max_for_len[i])

    print('\n')

    i = 0
    while i + WINDOW_LEN < len(big_long_line):
        print(big_long_line[i: i + WINDOW_LEN])
        i += WINDOW_LEN
    print(big_long_line[i:] + "\n")

    for speaker in speaker_stats.keys():
        if speaker_stats[speaker][1] == 0:
            print(speaker + ": " + str(speaker_stats[speaker]) + " 0")
        else:
            print(speaker + ": " + str(speaker_stats[speaker]) + " " + str(
                round(speaker_stats[speaker][0] /
                      speaker_stats[speaker][1], 2)))
    print('\n')
    for i in range(len(monologue_stats)):
        mono = monologue_stats[i]
        if mono[2] == 0:
            mono.append(0)
        else:
            mono.append(mono[3] / mono[2])
        if i < len(monologue_stats) - 1:
            mono.append(monologue_stats[i + 1][1])
        else:
            mono.append(len(lines))
    monologue_stats.sort(key=lambda x: x[4], reverse=True)
    for i in range(len(monologue_stats)):
        mono = monologue_stats[i]
        rate = str(round(mono[4], 2))
        if mono[5] - mono[1] >= MONOLOGUE_LENGTH:
            print(mono[0] + ", " + str(mono[1]) + "-" + str(mono[5]) + ": " +
                  str(mono[2]) + ", " + str(mono[3]) + ": " + rate)
    print("\nResolution_rate:" + str(round(resolutions / len(lines), 3)))
    print("Anceps_res_rate:" + str(round(anceps_resolution / resolutions, 3)))


def equal(m1, m2):
    if len(m1) != len(m2):
        return False
    i = 0
    while i < len(m1):
        if m1[i] != m2[i] and m1[i] != ANCEPS and m2[i] != ANCEPS:
            return False
        i += 1
    return True

if __name__ == "__main__":
    get_stats('../texts/full/Medea_full2.txt', '../texts/Medea.txt',
                '../texts/Medea_suppl.txt', '../output/Medea.txt')
    # get_stats('../texts/full/Agamemnon_full.txt', '../texts/Agamemnon.txt',
              # '../texts/Agamemnon_suppl.txt', '../output/Agamemnon.txt')


import re
import sys

DEFAULT_QUERY = \
    ['ego', 'mihi', 'me', 'mei', 'tu', 'tui', 'tibi', 'te', 'se', 'sui', 'sibi']


def pronouns(filename, query=DEFAULT_QUERY):
    print("\n" + filename)
    count = {}
    total = 0
    for p in query:
        count[p] = 0
    with open(filename) as file:
        lines = file.readlines()
        for line in lines:
            for p in query:
                c = len(list(re.finditer(r'[^a-z]' + p + '[^a-z]', line)))
                count[p] += c
                total += c

    print("Total: " +
          str(total) + "(" + str(round(total / len(lines), 2)) + "%)")
    for key in count.keys():
        print(key + ": " + str(count[key]))


def elision(filename):
    texts = 0
    count_end = {}
    count_beg = {}
    with open(filename) as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            texts += 1
            print("\n" + lines[i].rstrip('\n'))
            i += 2
            while lines[i] != '\n':
                key, count = lines[i].rstrip('\n').split(' ')
                if key in count_end:
                    count_end[key][0] += 1
                    count_end[key][1].append(count)
                else:
                    count_end[key] = [1, [count]]
                i += 1
            i += 2
            while i < len(lines) and lines[i] != '\n':
                key, count = lines[i].rstrip('\n').split(' ')
                if key in count_beg:
                    count_beg[key][0] += 1
                    count_beg[key][1].append(count)
                else:
                    count_beg[key] = [1, [count]]
                i += 1
            i += 2

    print("Elided in the end")
    sort = sorted(count_end, key=lambda x: x[0], reverse=True)
    for i in sort:
        if count_end[i][0] == texts:
            print(i + ' ' + str(count_end[i][1]))

    print("\nElided in the beginning")
    sort = sorted(count_beg, key=lambda x: x[0], reverse=True)
    for i in sort:
        if count_beg[i][0] == texts:
            print(i + ' ' + str(count_beg[i][1]))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s input_file_name word0 word1 ... wordn" % sys.argv[0])
        sys.exit(-1)
    elision(filename=sys.argv[1])
    if len(sys.argv) > 2:
        pronouns(filename=sys.argv[1], query=sys.argv[2:])
    else:
        pronouns(filename=sys.argv[1])

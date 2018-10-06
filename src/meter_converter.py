import copy
from src.utilities import *


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


with open("../texts/Test_full.txt") as file:
    lines = file.readlines()
with open("../texts/Test_full.txt", 'w') as file:
    for line in lines:
        meter = re.sub(r'[^\^&_]', '', line)
        meter = scansion_versions(meter, TRIMETER, 0)
        if len(meter) > 1 or meter == []:
            print('WARNING: ' + line)
            file.write(line)
            continue
        meter = meter[0]
        meter = re.sub('X', '&', ''.join(meter))
        j = 0
        for i in range(len(line)):
            if line[i] in ['^', '_', '&']:
                line = line[:i] + meter[j] + line[i + 1:]
                j += 1
        file.write(line)




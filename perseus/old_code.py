
"""def merge(versions):
    ls = '_^'
    U_AND_V = ["uv", "vu"]
    I_AND_J = ["ij", "ji"]
    if not versions:
        return None
    result = ""
    ind = []
    for i in range(len(versions)):
        ind.append(0)
    keepWorking = True
    while keepWorking:
        equal = True
        for i in range(1, len(versions)):
            if versions[i][ind[i]] != versions[0][ind[0]]:
                if versions[i][ind[i]]+versions[0][ind[0]] in U_AND_V:
                    versions[i] = versions[i][:ind[i]] + 'v' + versions[i][
                                                               ind[i] + 1:]
                    versions[0] = versions[0][:ind[0]] + 'v' + versions[0][
                                                               ind[0] + 1:]
                elif versions[i][ind[i]]+versions[0][ind[0]] in I_AND_J:
                    versions[i] = versions[i][:ind[i]] + 'j' + versions[i][
                                                               ind[i] + 1:]
                    versions[0] = versions[0][:ind[0]] + 'j' + versions[0][
                                                               ind[0] + 1:]
                equal = False
                break
        if equal:
            result += versions[0][ind[0]]
        for i in range(len(versions)):
            if equal or versions[i][ind[i]] in ls:
                ind[i] += 1
                if ind[i] == len(versions[i]):
                    keepWorking = False
                    break
    return result


def turn_into_meter(str):
    if not str:
        return None
    str = u_or_v(i_or_j(str))
    vowels = list(re.findall(r'('+LONG+'|\\'+SHORT+'|'+DIPHTHONGS+'|['+VOWELS+'])', str))
    i = 0
    while i < len(vowels):
        if (vowels[i] == LONG) or (vowels[i] == SHORT):
            vowels[i-1] = vowels[i]
            del vowels[i]
        else:
            vowels[i] = UNK
            i += 1
    if not vowels:
        return None
    return ''.join(vowels)"""

"""with open(PERSEUS_DATA_FILE_NAME) as file:
        with open(OUTPUT_FILE_NAME, 'w') as dict:
            lines = file.readlines()
            for line in lines:
                line = line.lower()
                parts = line.split('{')
                key = parts[0].rstrip('\t')
                versions = []
                for i in range(1, len(parts)):
                    parts[i] = list(re.findall(r'(:? )([a-zA-Z_^]*)(:?,)', parts[i]))
                    if parts[i]:
                        versions.append(parts[i][0][1])
                meter = turn_into_meter(merge(versions))
                if not meter:
                    meter = "None"
                dict.write(key + ' ' + meter + '\n')"""
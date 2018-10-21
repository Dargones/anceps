def search_pattern(pattern, text):
    """
    Searches a text for particular meter pattern
    :param pattern: list of meter patterns to search
    :param text:    list of meter patterns comprising teh text
    :return: list of indexes that mark the beginnings of matches
    """
    result = []
    for i in range(len(text) - len(pattern) + 1):
        if str(text[i:i + len(pattern)]) == str(pattern):
            result.append(i)
    return result


def full_search(pattern_size, text1_name, text2_name, text1, text2):
    """
    Search for patterns of length pattern_size that appear in both texts
    :param pattern_size:
    :param text1_name:
    :param text2_name:
    :param text1:
    :param text2:
    :return: dictionary of pattern: indexes_in_one_work, indexes_in_other_work
    """
    result = {}
    for i in range(len(text1) - pattern_size + 1):
        pattern = text1[i:i + pattern_size]
        if str(pattern) in result:
            result[str(pattern)][text1_name] += [i]
        else:
            curr = search_pattern(pattern, text2)
            if curr != []:
                result[str(pattern)] = {text1_name: [i], text2_name: curr}
    return result


def read_complete_scansion(filename):
    with open("/Users/alexanderfedchin/PycharmProjects/Scansion_project/data/completedScansions/" + filename + '.txt') as file:
        lines = file.readlines()
    if lines[0][:2] == "/*":
        while len(lines[0]) < 2 or lines[0][:2] != "*/":
            del lines[0]
        del lines[0:2]
    return [line.split('|')[1].split('-')[0].rstrip(' \t\n').lstrip(' \t\n') for line in lines]


def main(starting_size, text1_name, text2_name):
    text1 = read_complete_scansion(text1_name)
    text2 = read_complete_scansion(text2_name)

    size = starting_size
    while len(full_search(size, text1_name, text2_name, text1, text2).keys()) == 0:
        size -= 1
        print("Size decreased to " + str(size))
    print(full_search(size, text1_name, text2_name, text1, text2))


if __name__ == "__main__":
    main(20, "Medea", "Agamemnon")
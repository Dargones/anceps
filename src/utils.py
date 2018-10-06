import re

PRONOUNS = ['ego', 'mihi', 'me', 'mei', 'tu', 'tui', 'tibi', 'te', 'se', 'sui', 'sibi']


def pronouns(filename):
    print("\n" + filename)
    count = {}
    total = 0
    for p in PRONOUNS:
        count[p] = 0
    with open(filename) as file:
        lines = file.readlines()
        for line in lines:
            for p in PRONOUNS:
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


def to_do_manualy(scanned, text_name):
    with open(text_name) as text:
        lines = text.readlines()
    with open(scanned) as sc:
        i = 0
        for line in sc:
            if '&' in line or '|' in line:
                print(lines[i].rstrip('\n'))
            i += 1


if __name__ == "__main__":
    """texts = ["Medea", "Troades", "Phaedra", "Oedipus", "Agamemnon",
               "Thyestes_full", "Hercules_Oetaeus", "Hercules_furens",
               "Phoenissae", "Octavia"]
    for text in texts:
        pronouns("../texts/" + text + ".txt")"""
    # elision("Elision_data.txt")
    to_do_manualy('../output/Medea.txt', '../texts/Medea.txt')
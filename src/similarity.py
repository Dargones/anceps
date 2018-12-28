from scipy import spatial
import sys
import math

MAX = -1  # If MAX != -1 only consider the first MAX meter patterns (they are
# ordered by the number of syllables, so short meters come first


def similar(filename):
    """
    With different text being represented as vectors, calculate the cosine
    similarity between the texts and print a nice looking table
    :param filename: the input file. First comes a line with the play title,
    next every line contains a number (count of a particular meter type). Then
    there is a blank line, and so on.
    :return:
    """

    # read the file
    with open(filename) as file:
        lines = file.readlines()
    texts = []  # play titles
    new_text = True
    i = 0
    while i < len(lines):
        lines[i] = lines[i].rstrip('\n')
        if lines[i] == "":
            new_text = True
            i += 1
            continue
        if new_text:
            texts.append([lines[i], []])
        else:
            if len(texts[-1][1]) < MAX or MAX == -1:
                texts[-1][1].append(int(lines[i]))
        new_text = False
        i += 1

    sim_factor = {}
    for text in texts:
        sim_factor[text[0]] = 0

    print("Cosine similarity between each pair of plays\n"
          "(all entries are repeated twice so that it is easier to read):\n")
    FIELD = 17  # the longest play title
    to_print = " " * FIELD
    for i in range(len(texts)):
        to_print += texts[i][0] + " " * (FIELD - len(texts[i][0]))
    print(to_print)
    for i in range(len(texts)):
        to_print = texts[i][0] + " " * (FIELD - len(texts[i][0]))
        for j in range(len(texts)):
            similarity = 1 - spatial.distance.cosine(texts[i][1],
                                                     texts[j][1])
            if i != j:
                term = str(round(similarity, 5))
                to_print += term + " " * (FIELD - len(term))
                if j > i:
                    sim_factor[texts[i][0]] += similarity
                    sim_factor[texts[j][0]] += similarity
            else:
                to_print += " " * FIELD
        print(to_print)

    print("\nPlays in the order of descending average cosine similarity:")

    sorted_sim = sorted(sim_factor, key=sim_factor.get, reverse=True)
    for key in sorted_sim:
        print(key + " " * (FIELD - len(key)) + str(round(sim_factor[key]/
                                                         (len(texts) - 1), 5)))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s input_file_name" % sys.argv[0])
        sys.exit(-1)
    similar(sys.argv[1])
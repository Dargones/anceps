from scipy import spatial

MAX = -1


def similar(filename):
    with open(filename) as file:
        lines = file.readlines()
    texts = []
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
    FIELD = 15
    # to_print = " " * FIELD
    for i in range(len(texts)):
        # to_print += texts[i][0] + " " * (FIELD - len(texts[i][0]))
        print(texts[i][0])
    # print(to_print)
    for i in range(len(texts)):
        # to_print = texts[i][0] + " " * (FIELD - len(texts[i][0]))
        print(texts[i][0])
        """for j in range(i + 1, len(texts)):
            print(texts[i][0] + "----" + texts[j][0])
            similarity = 1 - spatial.distance.cosine(texts[i][1], texts[j][1])
            print(str(similarity) + "\n")
            sim_factor[texts[i][0]] += similarity
            sim_factor[texts[j][0]] += similarity"""
        for j in range(len(texts)):
            similarity = 1 - spatial.distance.cosine(texts[i][1],
                                                     texts[j][1])
            if i != j:
                term = str(round(similarity, 5))
                # to_print += term + " " * (FIELD - len(term))
                print(term)
                if j > i:
                    sim_factor[texts[i][0]] += similarity
                    sim_factor[texts[j][0]] += similarity
            else:
                # to_print += " " * FIELD
                print('')
                pass
        # print(to_print)

    print("\nPlays in the order of descending avergage cosine similarity:")

    sorted_sim = sorted(sim_factor, key=sim_factor.get, reverse=True)
    for key in sorted_sim:
        print(key + " " * (FIELD - len(key)) + str(round(sim_factor[key]/
                                                         len(texts), 5)))

if __name__ == "__main__":
    similar("Senecan_tragedies.txt")
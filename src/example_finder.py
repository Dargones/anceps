"""
This module allows to quickly skim through the texts donlowded from mqdq and find a desired scansion
"""
import sys
import re


def look_up_word(filename, query):
    """
    Look up a regex expresssion in a file
    :param filename:
    :param query:
    :return:
    """
    line_id = 0
    lines = []
    for line in open(filename):
        digitString = line.split(' ')[0]
        if digitString.isdecimal():
            line_id = int(digitString)
        if query.match(line):
            lines.append(line_id)
    return lines


def print_finds(lines_ids, filename, titlr):
    """
    Print results
    :param lines:
    :param filename:
    :return:
    """
    lines = open(filename).readlines()
    for id in lines_ids:
        print(lines[id].rstrip('\n') + '\t' + title + '\t' + str(id))


if __name__ == "__main__":
    query = re.compile("me.d[ij]u.s\n")
    with open(sys.argv[1]) as file:
        lines = file.readlines()
        list_of_files = []
        for i in range(1, len(lines)):
            names = lines[i].rstrip('\n \t').split('\t')
            title = names[1].split('/')[-1]
            lines_ids = look_up_word(names[1], query)
            print_finds(lines_ids, names[0], title)
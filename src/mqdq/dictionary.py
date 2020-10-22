# -*- coding: utf-8 -*-
"""
This module provides tools for extracting information about natural vowel quantities from the
scanned mqdq texts.
"""

from pathlib import Path
import argparse
import sys
from collections import defaultdict
from tqdm import tqdm
import json
from src.utils import *


class MqDqDictionary:

    # replacements for fancy quantity symbols used by MqDq
    REPLACEMENTS = {u"\xa0": " ", "‿": "‿ ",
                    "ṓ": "o_", "ó": "o*", "ō": "o_", "ŏ": "o^",
                    "ā́": "a_", "á": "a*", "ā": "a_", "ă": "a^",
                    "ī́": "i_", "í": "i*", "ī": "i_", "ĭ": "i^",
                    "j̄́": "i_", "j́": "j*", "j̄": "i_", "j̆": "j^",
                    "ḗ": "e_", "é": "e*", "ē": "e_", "ĕ": "e^",
                    "ū́": "u_", "ú": "u*", "ū": "u_", "ŭ": "u^",
                    "v̄́": "u_", "v́": "v*", "v̄": "u_", "v̆": "v^",
                    "ȳ́": "y_", "ý": "y*", "ȳ": "y_", "y̆": "y^",
                    "œ": "[oe]", "œ̄́": "[oe]", "œ́": "[oe]", "œ̄": "[oe]", "œ̆": "[oe]",
                    "æ": "[ae]", "ǣ́": "[ae]", "ǽ": "[ae]", "ǣ": "[ae]", "æ̆": "[ae]"}

    # to catch unexpected characters
    UNEXPECTED = re.compile("[^a-z\^_‿⁔*\[\]<>\n†(\-\") –\"\t&.?!;:0-9,’“‘\"\\xc2\\xa0\\\]")
    UNUSED = re.compile("[^a-z\[\] \^_*‿]")  # to replace unused characters

    # elision, etc.
    ELIDE = re.compile("([" + VOWELS + "])(["+ CONSONANTS + "]|"+"|".join(SHORT_COMBINATIONS)+ "|)‿?$")
    ELIDE_LONG = re.compile("([" + VOWELS + "])([" + CONSONANTS + "]*)‿?$")
    LONG_BY_POS = re.compile("_(" + CLOSE_SYLLABLE + "|[" + CONSONANTS_NOT_H + "]{3})(["
                             + CONSONANTS + "]*)$")
    PREFIX = re.compile("^[" + DOUBLE_CONSONANTS + CONSONANTS + "]*")
    ERROR = re.compile("(?<!\[)[oyea](?![*_^\]])")  # no quantity specified
    U_ERROR = re.compile("[*_\^]u([" + VOWELS + "]|$)")  # does not work wel with novum

    def __init__(self):
        self.data = defaultdict(dict)

    def load(self, file):
        """
        Load the dictionary from a file
        :param file:
        :return:
        """
        self.data = json.load(file)

    def save(self, file):
        """
        Save the dictionary to
        :param file:
        :return:
        """
        json.dump(self.data, file, indent=2)

    def look_up(self, form):
        """
        Look up a form in the dictionary and return the dictionary entry
        :param form:
        :return:
        """
        key = re.sub("[^a-z]", "", form.lower())
        key = multireplace(key, {"v": "u", "j": "i"})
        return self.data.get(key, {})

    def add_word(self, word, next_word, author, diphthongs):
        """
        Add a particular word-scansion to a dictionary
        :param word:        the word-scansion
        :param next_word    the following word
        :param author:      the author of that word-scansion
        :param diphthongs: if True, replace [ae] and [oe] with e
        :return:
        """
        if next_word is None or word[-1] == "‿" or next_word == "est":
            word = MqDqDictionary.ELIDE.sub(r"\1*\2", word)
            word = MqDqDictionary.ELIDE_LONG.sub(r"\1_\2", word)
        else:
            prefix = MqDqDictionary.PREFIX.match(next_word).group()
            if MqDqDictionary.LONG_BY_POS.search(word) is None and len(prefix) > 0:
                word += prefix
                word = MqDqDictionary.LONG_BY_POS.sub(r"*\1\2", word)
                word = word[:-len(prefix)]
        if MqDqDictionary.ERROR.search(word) is not None:
            # if MqDqDictionary.ERROR.search(word) is not None or MqDqDictionary.U_ERROR.search(word) is not None:
            return
        if len(word) > 4 and word[-4:] in ["que^", "que*", "qve^", "qve*"]:
            self.add_word(word[:-4], "qv", author, diphthongs)
            return
        word = re.sub("u([^\]\^*_])", r"v\1", word)
        word = re.sub("i([^\]\^*_])", r"j\1", word)
        if not diphthongs:
            word = re.sub("(\[ae\]|\[oe\])", "e_", word)

        key = re.sub("[^a-z]", "", word.lower())
        key = multireplace(key, {"v": "u", "j": "i"})
        if word not in self.data[key]:
            self.data[key][word] = defaultdict(int)
        self.data[key][word][author] += 1

    def add_verse(self, verse, author, diphthongs):
        """
        Take a scanned verse of poetry and record all the word scansions in it in the dictionary
        :param verse:   the verse to record the scansions from
        :param author:  the author of the verse
        :param diphthongs: if True, replace [ae] and [oe] with e
        :return:
        """
        verse = re.sub("[\^_*\[\]\n\t]", "", verse)
        verse = multireplace(verse.lower(), MqDqDictionary.REPLACEMENTS)
        if list(MqDqDictionary.UNEXPECTED.finditer(verse)):
            # warnings.warn("An unexpected character found: " + verse)
            return
        verse = MqDqDictionary.UNUSED.sub("", verse)
        verse = re.sub(" +", " ", verse).rstrip(" ").lstrip(" ")  # removing extra spaces
        if len(verse) == 0:
            return
        words = verse.split(" ")
        words.append(None)  # marks the end of the line
        for i, word in enumerate(words[:-1]):
            self.add_word(word, words[i+1], author, diphthongs)

    def augment(self, dir, authors, diphthongs):
        """
        Augment the dictionary with scansions of all the texts written by the specified set of
        authors
        :param dir:     the directory with the scansions (where scraping.py downloads them to)
        :param authors: list of authors. If authors == [], all authors will be considered
        :param diphthongs: if True, replace [ae] and [oe] with e
        :return:        None
        """
        authors_list = [str(x).split("/")[-1] for x in list(Path(dir).glob("*"))]
        authors_list = [x for x in authors_list if x[0] != "."]  # exclude hidden files
        assert sum([x in authors_list for x in authors]) == len(authors)
        if not authors:
            authors = authors_list
        for author in tqdm(authors):  # for any author
            files = list(Path(dir.rstrip("/")+"/"+author).rglob("*.scanned"))
            for file in files:  # for any text of that author that can be scanned
                with open(file, "r", encoding="utf-8") as f:
                    verses = f.readlines()
                for verse in verses:  # for any line in that text
                    self.add_verse(verse, author, diphthongs)  # add the word scansions to the dictionary


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Create a frequency-based dictionary of possible"
                                            "vowel quantities based on scansions of texts by "
                                            "a set of specific authors")
    p.add_argument("dir", type=str, help="directory from which to extract the scansions")
    p.add_argument("output", type=argparse.FileType("w"),
                   help="output file name and path")
    p.add_argument("-authors", type=str, nargs="*", default=[],
                   help="set of authors to consider when constructing the dictionary. Leave "
                        "blank to include all authors")
    p.add_argument("--no_diphthongs", dest="diphthongs", action="store_false",
                   help="use to build a dictionary where 'ae' and 'oe' is replaced with 'e'")
    p.set_defaults(diphthongs=True)
    args = p.parse_args(sys.argv[1:])

    dictionary = MqDqDictionary()
    dictionary.augment(args.dir, args.authors, args.diphthongs)
    dictionary.save(args.output)

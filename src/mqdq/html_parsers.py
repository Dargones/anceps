""" This module contains html parsers used in scraping.py"""

from html.parser import HTMLParser
from collections import defaultdict
import re


class AuthorListParser(HTMLParser):
    """ Parses the page that lists all authors in the database """

    def __init__(self):
        super(AuthorListParser, self).__init__()
        self.parsing_author = -1  # The id of the currently parsed author <tr id="autori##"
        self.data = defaultdict(str)  # all the data collected since self.parsing_author was changed
        self.current_tags = []  # tag tree
        self.results = {}       # author name -> id

    def feed(self, data):
        super().feed(data)
        return {re.sub("[^a-zA-Z]", "_", x): self.results[x] for x in self.results.keys()}

    def handle_starttag(self, tag, attrs):
        attrs = {x[0]: x[1] for x in attrs}
        if tag == "tr" and "onclick" in attrs:
            self.parsing_author = int(attrs["id"][6:])
        self.current_tags.append(tag)

    def handle_endtag(self, tag):
        if tag == "tr" and self.parsing_author != -1:
            if "b" in self.data:  # authors are sometimes inside the b tag
                self.results[self.data["b"]] = self.parsing_author
            else:
                self.results[self.data["i"]] = self.parsing_author  # and otherwise inside i tag
            self.parsing_author = -1
            self.data = defaultdict(str)
        self.current_tags.pop()

    def handle_data(self, data):
        if self.parsing_author != -1 and len(self.current_tags) > 0:
            self.data[self.current_tags[-1]] += data


class WorkListParser(HTMLParser):
    """ Parses the page that lists all the works of a particular author """

    def __init__(self):
        super(WorkListParser, self).__init__()
        self.parsing_link = ""  # Not "" when inside <a class="opera"...
        self.parsing_text = ""  # Text inside <a class="opera"...
        self.works = {}  # title -> link

    def feed(self, data):
        super().feed(data)
        return self.works

    def handle_starttag(self, tag, attrs):
        attrs = {x[0]: x[1] for x in attrs}
        if tag == "a" and "class" in attrs and attrs["class"] == "opera":
            self.parsing_link = attrs["href"]

    def handle_endtag(self, tag):
        if tag == "a" and self.parsing_link != "":
            work_key = re.sub("[^a-zA-Z]", "_", self.parsing_text)
            if work_key in self.works:  # sometimes there are several identically named works
                i = 2
                while work_key + "_" + str(i) in self.works:
                    i += 1
                work_key += "_" + str(i)
            self.works[work_key] = self.parsing_link
            self.parsing_link, self.parsing_text = "", ""

    def handle_data(self, data):
        if self.parsing_link != "":
            self.parsing_text += data


class PageListParser(HTMLParser):
    """
    Parses the page corresponding to some work and returns all the pages on which parts of
    this work can be found
    """

    def __init__(self):
        super(PageListParser, self).__init__()
        self.select_found = True  # is true whenever inside <select class="form-control"...
        self.pages = []

    def feed(self, data):
        super().feed(data)
        return self.pages

    def handle_starttag(self, tag, attrs):
        attrs = {x[0]: x[1] for x in attrs}
        if tag == "select" and "class" in attrs and attrs["class"] == "form-control":
            self.select_found = True
        elif self.select_found and tag == "option":
            self.pages.append(attrs["value"])

    def handle_endtag(self, tag):
        if tag == "select":
            self.select_found = False


class PageParser(HTMLParser):
    """
    Parses a page with text and, potentially, scansions
    """

    def __init__(self):
        super(PageParser, self).__init__()
        self.recording = None   # is "text" if inside <p class="cv"> or <p class="vv"> and
        # "scansions" if inside <td class="bianco super"
        self.data = {"scansions":[], "text":[]}
        self.recorded = ""  # currently recorded text

    def feed(self, data):
        super().feed(data)
        return self.data

    def handle_starttag(self, tag, attrs):
        attrs = {x[0]: x[1] for x in attrs}
        if tag == "p" and "class" in attrs and attrs["class"] in ["c_v", "vv"]:
            self.recording = "text"
        elif tag == "td" and "class" in attrs and attrs["class"][:12] == "bianco super":
            self.recording = "scansions"

    def handle_endtag(self, tag):
        if (tag == "p" and self.recording == "text") or (
                        tag == "td" and self.recording == "scansions"):
            self.data[self.recording].append(self.recorded + "\n")
            self.recorded = ""
            self.recording = None

    def handle_data(self, data):
        if self.recording:
            self.recorded += data


"""
Module for web scraping the mqdq.it database
"""


import requests
import shutil
import re
import pathlib
import os

BASEDIR = "/home/af9562/mqdq/PoetiDItalia2/"
NUM_AUTHORS = 310
DATABASE = "http://www.poetiditalia.it"


def process_work(url, title):
    """
    Process a single work (which might be divided into separate files)
    :param url:
    :param title:
    :return:
    """
    outdir = BASEDIR + title
    append = outdir[-2:]
    directory_created = False
    while not directory_created:
        directory_created = True
        outdir = outdir[:-2] + append
        try:
            pathlib.Path(outdir).mkdir(parents=False, exist_ok=False)
        except FileExistsError:
            directory_created = False
            if append[-1] not in "0123456789":
                append = "_1"
                outdir += "_0"
            else:
                append = "_" + str(int(append[-1]) + 1)
    baseUrl = url[:-3]
    file_name = outdir + "/" + url[-3:] + ".txt"
    new_lines = download_file(url, file_name)
    ids = get_all_page_indexes(new_lines)
    parse_file(new_lines, file_name)
    previous = []
    for id in ids:
        url = baseUrl + id
        file_name = outdir + "/" + id + ".txt"
        new_lines = download_file(url, file_name)
        if not new_file_is_different(new_lines, previous):
            os.remove(file_name)
            break
        parse_file(new_lines, file_name)
        previous = new_lines


def get_all_page_indexes(new_lines):
    """
    Extract all the page numbers
    :param new_lines:
    :return:
    """
    ids = []
    containerOpened = False
    for line in new_lines:
        if re.match(".*<select class=\"form-control\".*", line):
            containerOpened = True
        elif containerOpened:
            if line == "</select>\n":
                containerOpened = False
            else:
                ids.append(re.sub('.*<option.*?value=.*?\|.*?\|(.*)\".*', r'\1', line))
    return [x.rstrip('\n') for x in ids]


def new_file_is_different(new_lines, old_lines):
    """
    Return True if the two list of lines differ or if the older file is empty
    :param new_lines:
    :param old_lines:
    :return:
    """
    if old_lines == []:
        return True
    equal = True
    offset = 0
    for i in range(len(old_lines)):
        if i + offset >= len(new_lines):
            equal = False
            break
        elif old_lines[i] != new_lines[i + offset]:
            if re.sub('random=[0-9a-z]*\"', '', new_lines[i + offset]) \
                    != re.sub('random=[0-9a-z]*\"', '', old_lines[i]):
                offset += 1
    return not equal


def parse_file(lines, new_file_name):
    """
    Parse a single file
    :param lines: the lines to parse
    :param new_file_name: the name of the output file
    :return:
    """
    with open(new_file_name, 'w') as file:
        containerOpened = False
        divCount = 0
        for line in lines:
            if line == "<div class=\"container\">\n":
                if not containerOpened:
                    containerOpened = True
                else:
                    print("Only one container should be opened at a time")
            elif containerOpened:
                if re.match('.*<div.*', line):
                    if len(re.findall('<div', line)) != 1:
                        print("Two tags opened at the same line")
                    divCount += 1
                if re.match('</div', line):
                    if len(re.findall('</div', line)) != 1:
                        print("Two tags closed at the same line")
                    divCount -= 1
                if divCount == -1:
                    containerOpened = False
                else:
                    parse_line(line, file)
    return True


def get_int_from_line_id(lineid, default=0):
    """
    Convert a string toa line number. A string might even contain some letters
    in it
    :param lineid:
    :param default: the default number to return if integer convertion fails
    :return:
    """
    if not re.match('.*[^0-9].*', lineid):
        return int(lineid)
    if re.match('^[^0-9]*[0-9]*[^0-9]*$', lineid):
        return int(re.sub('[^0-9]', '', lineid))
    return default


def parse_line(line, file):
    """
    Parse a single line of text
    :param line:
    :param file:
    :param newline:
    :param lineid:
    :return:
    """
    lineid = ""
    if re.match('.*<p class=\"c_v\">.*</p>.*', line):
        if len(re.findall('<p class=\"c_v\">.*?</p>', line)) != 1:
            print("Two verses on the same line is bad")
        line = re.sub('.*<p class=\"c_v\">(.*)</p>.*', r'\1', line)
    elif re.match('.*<p class=\"c_n\">.*?</p><p class=\"vv\">.*</p>.*', line):
        if len(re.findall("<p class=\"c_n\">.*?</p><p class=\"vv\">.*?</p>",
                          line)) != 1:
            print("Two verses on teh same line is bad")
        line = re.sub("<p class=\"c_n\">(.*?)</p><p class=\"vv\">(.*?)</p>",
                      r'\1\t\2', line)
        lineid, line = line.split('\t')
    elif re.match(".*<p class=\"c_t\">.*?</p>.*", line):
        title = re.sub(".*<p class=\"c_t\">(.*?)</p>.*", r'\1', line)
        file.write('\n' + title + '\n')
        return
    else:
        return
    line = re.sub('&(lt|gt);', '', line)
    line = re.sub('<(p|/p|br /)>', '', line)
    line = re.sub('<a.*?>(.*?)</a>', r'\1', line)
    line = re.sub('<span.*?>(.*?)</span>', r'\1', line)
    line = re.sub('<img.*?/>', '', line)
    line = re.sub('&nbsp;', '\t', line)
    line = re.sub('\t\t*', '\t', line)
    file.write(lineid + '\t' + line.rstrip('\n') + '\n')
    return


def process_author(url, name):
    """
    Process a webpage that lists all the works by a given author
    :param url:
    :param name: the name of the author
    :return:
    """
    outdir = BASEDIR + name
    file_name = outdir + "/" + "Content.txt"
    pathlib.Path(outdir).mkdir(parents=False, exist_ok=False)
    lines = download_file(url, file_name)
    with open(file_name, 'w') as file:
        containerOpened = False
        for line in lines:
            if re.match(".*<div id=\"div_opere\".*", line):
                containerOpened = True
            if containerOpened:
                works = re.findall("<a class=\"opera\".*?</a>", line)
                editors = re.findall("<span class=\"edizione\".*?</span>", line)
                for i in range(len(works)):
                    works[i] = re.sub(".*href=\"(.*?)\" >(.*?)</a>.*", r'\1\t\2', works[i])
                    link, title = works[i].split('\t')
                    link = DATABASE + link
                    title = re.sub(' ', '_', title)
                    editors[i] = re.sub(".*?>\((.*?)\).*", r'\t\1\n', editors[i])
                    file.write(link + '\t' + title + editors[i])
                    process_work(link, name + '/' + title)
                if re.match(r'.*/div>.*', line):
                    containerOpened = False


def download_file(url, filename):
    """
    Download file from teh url, save its content to filename and return the
    content of that file as a list of lines
    :param url:
    :param filename:
    :return:
    """
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
    with open(filename) as file:
        return file.readlines()


def process_all(url, start=0, max=-1):
    """
    Download data from poetiditaila.it
    :param url: the webpage with all the authors listed in alphabetical order
    :return:
    """
    metafile = BASEDIR + "/" + "Content.txt"
    lines = download_file(url, metafile)
    with open(metafile, 'w') as file:
        count = 0
        for line in lines:
            if line[:14] != "<tr id='autori":
                continue
            oldline = line
            line = re.sub("<tr id='autori([0-9]*).*<b>(.*)</b>.*", r'\1\t\2', line)
            if line == oldline:
                line = re.sub("<tr id='autori([0-9]*).*<i>(.*)</i>.*", r'\1\t\2', line)
                if line == oldline:
                    continue
            count += 1
            id, name = line.split('\t')
            name = re.sub(' ', '_', name.rstrip('\n'))
            link = DATABASE + "/public/indici/autori/idautori/" + id
            file.write(link + '\t' + name + '\n')
            max -= 1
            if max > 0 and count >= start:
                print("Downloading " + name + " (" +
                      str(round(count/NUM_AUTHORS * 100, 1)) + "% done)")
                process_author(link, name)


if __name__ == "__main__":
    process_all(DATABASE + "/public/indici/autori/tipo/crono", start=0, max=400)
""" Module for web scraping the mqdq.it database """

import argparse
import requests
import sys
import pathlib

import urllib3
from selenium.webdriver.support import wait
from tqdm import tqdm
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from src.mqdq.html_parsers import *
driver = webdriver.Firefox()

DOMEN = "http://mizar.unive.it/"
CHRONO_LIST = "/public/indici/autori/tipo/crono"
WORK_LIST = "/public/indici/autori/idautori/"


def process_work(url, dir, set_descr=None):
    """
    Download all the parts of a particular text
    :param url:         url that leads to the first page corresponding to this work
    :param dir:         the directory to store all the data to
    :param set_descr:   a function that can be used to set description to the tqdm progress bar
    :return:
    """
    pathlib.Path(dir).mkdir(parents=False, exist_ok=True)
    metadata = download_url(url)
    parser = PageListParser()
    pages = parser.feed(metadata)
    if not pages:  # if there is only one page
        pages = [url.split("/")[-1]]
    baseUrl = url[:-len(url.split("/")[-1])]
    for i, page in enumerate(pages):
        set_descr(" {}:{}".format(i, len(pages)))
        scrap_page(baseUrl + page, dir + "/" + page.split("|")[-1] + ".txt")


def scrap_page(url, filename):
    """
    Download all the text from a particular page on MqDq. Also attempt to scan the page
    :param url:
    :param filename:
    :return:
    """
    driver.get(url)
    scansionIdLocation = "//input[@name='idScansione' and @type='hidden']"
    livelloIdLocation = "//input[@name='livello' and @type='hidden']"
    try:
        wait.WebDriverWait(driver, 300).until(lambda x: element_exists(scansionIdLocation))
        scansionId = driver.find_element_by_xpath(scansionIdLocation).get_attribute('value')
        scansionId += "," + driver.find_element_by_xpath(livelloIdLocation).get_attribute('value')
    except:
        print("Waiting for page timeout for\t" + url + "\t" + filename)
        scansionId = "0"
    buttonLocation = "//button[@class='btn btn-primary' and @title='' and " \
                     "@onclick='eseguiScansione("+scansionId+")']"
    appearAfterScansion = ["//div[@class='pedecerto']", "//table[@class='versoScandito']"]
    try:
        driver.find_element_by_xpath(buttonLocation).click()
        wait.WebDriverWait(driver, 1200).until(
            lambda x: sum([element_exists(y) for y in appearAfterScansion]) != 0)

    except TimeoutException:
        print("Waiting for scansion timeout for\t" + url + "\t" + filename)
    except urllib3.exceptions.MaxRetryError:
        sleep(1800)
    except:
        pass

    try:
        html = driver.page_source
    except urllib3.exceptions.MaxRetryError:
        sleep(1800)
    parser = PageParser()
    data = parser.feed(html)

    with open(filename, "w") as file:
        file.writelines(data["text"])
    if len(data["scansions"]) > 0:
        with open(filename + ".scanned", "w") as file:
            file.writelines(data["scansions"])


def element_exists(element):
    """
    Returns True or False depending on whether an element can be located by the driver
    :param element:
    :return:
    """
    try:
        driver.find_element_by_xpath(element)
    except:
        return False
    return True


def process_author(url, dir, set_descr=None):
    """
    Download all the works of a particular author on the local machine
    :param url:         url that leads to the page that lists all of this author's works
    :param dir:         the directory to store all the data to
    :param set_descr:   a function that can be used to set description to the tqdm progress bar
    :return:
    """
    try:
        pathlib.Path(dir).mkdir(parents=False, exist_ok=False)
    except:
        print("directory " + dir + " already exists. Skipping the corresponding author...")
        return

    metadata = download_url(url)
    parser = WorkListParser()
    works_dict = parser.feed(metadata)

    for i, work in enumerate(works_dict.keys()):
        if set_descr:
            set_descr_work = lambda x: set_descr("{}:{}".format(i, len(works_dict)) + x)
        else:
            set_descr_work = None
        process_work(DOMEN.rstrip("/") + works_dict[work], dir + "/" + work, set_descr_work)


def process_all(database, dir, authors_to_download):
    """
    Download a databse or a portion of it on the local machine
    :param database:                the database to download (either mqdq or poetiditalia)
    :param dir:                     the directory to store all the data to
    :param authors_to_download:     the list of authors to download or [] if all authors are
                                    to be downloaded
    :return:                        None
    """
    authors_dict = list_all_authors(database)
    # assert that all the requensted authors can be downloaded
    assert sum([x in authors_dict for x in authors_to_download]) == len(authors_to_download)
    pathlib.Path(dir).mkdir(parents=False, exist_ok=True)
    if not authors_to_download:
        authors_to_download = list(authors_dict.keys())
    index = tqdm(authors_to_download)
    for author in index:
        author_dir = dir.rstrip("/") + "/" + author
        author_url = DOMEN + database + WORK_LIST + str(authors_dict[author])
        set_descr = lambda x: index.set_description(author + " " + x)
        process_author(author_url, author_dir, set_descr)


def list_all_authors(database):
    """
    List all authors available for download in a given database
    :param database:    either mqdq or poetiditalia
    :return:            a dictionary that maps author name to its id
    """
    metadata = download_url(DOMEN + database + CHRONO_LIST)
    parser = AuthorListParser()
    return parser.feed(metadata)


def download_url(url):
    """
    Download url from the web and return html as a string
    :param url: Url to download
    :return:    A string
    """
    return requests.get(url, stream=True).content.decode("utf-8")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Web-scrape the MqDq database")
    p.add_argument("database", type=str, choices=("mqdq", "poetiditalia"),
                   help="database to web-scrape")
    p.add_argument("-dir", type=str, help="directory to put all the data to",
                   default="./downloaded")
    p.add_argument("-authors", type=str, nargs="*", default=[],
                   help="particular authors to download")
    p.add_argument("--list-all-authors", action="store_true", dest="list_all_authors",
                   help="instead of downloading the data simply list all the available authors")
    p.set_defaults(list_all_authors=False)
    args = p.parse_args(sys.argv[1:])

    if args.list_all_authors:
        print(list(list_all_authors(args.database).keys()))
    else:
        process_all(args.database, args.dir, args.authors)

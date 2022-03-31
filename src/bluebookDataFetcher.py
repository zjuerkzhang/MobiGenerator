# -*- coding: utf-8 -*-

from logger import MyLogger
import json
import os
from datetime import datetime
import htmlFilesGenerator
import requests
from bs4 import BeautifulSoup as bs
import re

selfDir = os.path.dirname(os.path.abspath(__file__))
bookLogger = MyLogger.getLogger("bluebookFetcher")

def fetchWebContent2Soup(url):
    bookLogger.debug("Try to fetch content from link: " + url)
    r = requests.get(url)
    if r == None:
        bookLogger.error("Fail to get %s" % url)
        return None
    r.encoding = "utf-8"
    return bs(r.text, 'html5lib')

def regularizeUrl(mainUrl, url):
    if re.search("^http[s]?://", url):
        return url
    if re.search("^/", url):
        siteUrl = '/'.join(mainUrl.split('/')[3])
        return siteUrl + url

    dirUrl = '/'.join(mainUrl.split('/')[:-1])
    if re.search("^\./", url):
        return dirUrl + '/' + re.sub("^\./", "", url)
    return dirUrl + url

def getSectionContent(url):
    soup = fetchWebContent2Soup(url)
    if soup == None:
        bookLogger.error("Fail to transfer web content from [%s] to soup" % url)
        return ""
    div = soup.find("div", attrs = {"class": "customer"})
    if div == None:
        bookLogger.error("Fail to get div@class from [%s]" % url)
        return ""
    return div.prettify()

def getNovelStructureLinks(mainUrl):
    chapter = {
        "title": "",
        "sections": []
    }
    soup = fetchWebContent2Soup(mainUrl)
    if soup == None:
        bookLogger.error("Fail to transfer web content from [%s] to soup" % mainUrl)
        return chapter
    h1 = soup.find("h1")
    if h1 == None:
        bookLogger.error("Fail to get novel title from [%s]" % mainUrl)
        return chapter
    chapter['title'] = h1.string
    table = soup.find("table", attrs = {"class": "center"})
    if table == None:
        bookLogger.error("Fail to get section table from [%s]" % mainUrl)
        return chapter
    tds = table.find_all("td")
    for td in tds:
        a = td.find("a")
        if not a:
            continue
        section = {
            "title": a.string,
            "description": getSectionContent(regularizeUrl(mainUrl, a["href"]))
        }
        chapter['sections'].append(section)
    return chapter

if __name__ == "__main__":
    configPath = "%s/../config/config.json" % selfDir
    if not os.path.exists(configPath):
        bookLogger.error("no valid config file")
        exit(1)

    configData = {}
    try:
        with open(configPath, 'r') as f:
            configData = json.load(f)
    except:
        bookLogger.error("Fail to parse configure file to json data")
        exit(1)

    if 'bluebooks' not in configData.keys():
        bookLogger.error("No attribute bluebooks in config file")
        exit(1)

    data = {
        'bookName': "%s %s" % ("小说合集", datetime.today().strftime("%Y-%m-%d")),
        'chapters': []
    }
    for bookEntry in configData['bluebooks']:
        if "generated" in bookEntry.keys() and bookEntry["generated"] == True:
            continue
        chapter = getNovelStructureLinks(bookEntry["url"])
        if chapter != None and len(chapter['sections']) > 0:
            data['chapters'].append(chapter)
            bookEntry['title'] = chapter['title']
            bookEntry["generated"] = True
    if len(data['chapters']) == 0:
        bookLogger.info("No html files are generated")
        exit(1)

    htmlFilesGenerator.buildHtmls(data, 'bluebook')
    with open(configPath, 'w') as f:
        json.dump(configData, f, indent = 4)
    exit(0)

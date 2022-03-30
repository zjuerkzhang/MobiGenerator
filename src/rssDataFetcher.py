import feedparser
from logger import MyLogger
import re
import json
import os
from datetime import datetime
import htmlFilesGenerator

selfDir = os.path.dirname(os.path.abspath(__file__))
rssLogger = MyLogger.getLogger("rssDataFetcher")

def fillImgMapping(content, imgSubdir, startImgIdx):
    newContent = content
    mapList = []
    imgTagStrs = re.findall('<img.*?/>', newContent)
    for imgTagStr in imgTagStrs:
        #print(imgTagStr)
        urlRe = re.search("http[s]?://.*?['\"]", imgTagStr)
        if not urlRe:
            rssLogger.info("Fail to parse url from img tag [%s]" % imgTagStr)
            continue
        url = urlRe.group()[:-1]
        startImgIdx = startImgIdx + 1
        imgFilename = '.'.join(["%04d" % startImgIdx ,url.split('.')[-1]])
        mapList.append({
            'srcUrl': url,
            'dstFile': imgFilename
        })
        newImgTagStr = "<img src=\"./images/%s/%s\">" % (imgSubdir, imgFilename)
        newContent = newContent.replace(imgTagStr, newImgTagStr)
    return startImgIdx, mapList, newContent

def entryNewerThanLast(entry, lastUpdate):
    entryTime = "%04d%02d%02d%02d%02d%02d" % entry.published_parsed[:6]
    if entryTime > lastUpdate:
        rssLogger.debug("entry %s published at %s" % (entry.title, entryTime))
        rssLogger.debug("===> New item")
        return True, entryTime
    else:
        return False, lastUpdate

def fetchRssData(rssConfig):
    lastUpdate = rssConfig['update']
    newUpdate = lastUpdate
    feed = feedparser.parse(rssConfig['url'])
    if len(feed['entries']) == 0:
        return None
    imgSubdir = str(hash(feed.feed.title))
    chapter = {
        'title': feed.feed.title,
        'sections': [],
        'imgSubdir': imgSubdir,
        'imgDlMap': []
    }
    imgFileIdx = 0
    for entry in feed.entries:
        newer, entryTime = entryNewerThanLast(entry, lastUpdate)
        if not newer:
            continue
        if entryTime > newUpdate:
            newUpdate = entryTime
        section = {
            'title': entry.title,
            'description': entry.description
        }
        imgFileIdx, mapList, newContent = fillImgMapping(section['description'], imgSubdir, imgFileIdx)
        section['description'] = newContent
        chapter['sections'].append(section)
        chapter['imgDlMap'].extend(mapList)
        #print(section['description'])
    #for img in chapter['imgDlMap']:
        #print(img)
    #print(chapter['imgSubdir'])
    rssConfig['update'] = newUpdate
    return chapter

if __name__ == "__main__":
    configPath = "%s/../config/config.json" % selfDir
    if not os.path.exists(configPath):
        rssLogger.error("no valid config file")
        exit(1)

    configData = {}
    try:
        with open(configPath, 'r') as f:
            configData = json.load(f)
    except:
        rssLogger.error("Fail to parse configure file to json data")
        exit(1)

    if 'rssFeeds' not in configData.keys():
        rssLogger.error("No attribute rssFeeds in config file")
        exit(1)

    data = {
        'bookName': "%s %s" % ("RSS阅读合集", datetime.today().strftime("%Y-%m-%d")),
        'chapters': []
    }
    for rssFeed in configData['rssFeeds']:
        chapter = fetchRssData(rssFeed)
        if chapter != None and len(chapter['sections']) > 0:
            data['chapters'].append(chapter)
    if len(data['chapters']) == 0:
        rssLogger.info("No html files are generated")
        exit(1)

    htmlFilesGenerator.buildHtmls(data)
    with open(configPath, 'w') as f:
        json.dump(configData, f, indent = 4)
    exit(0)

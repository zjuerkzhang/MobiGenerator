from cgitb import html
import os
from datetime import datetime
import requests
from jinja2 import Environment, FileSystemLoader
from logger import MyLogger

htmlLogger = MyLogger.getLogger("htmlGenerator")
selfDir = os.path.dirname(os.path.abspath(__file__))
gTemplateTargetMap = [
    {'template': 'toc.ncx.xml', 'target': 'toc.ncx'},
    {'template': 'opf.xml', 'target': 'target.opf'},
    {'template': 'toc.html', 'target': 'toc.html'},
]
gHeaders = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-Hans-CN,zh-CN;q=0.9,zh;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5,ja;q=0.4',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.53 Safari/537.36 Edg/80.0.361.33',
    'Connection' : 'keep-alive',
    'Cache-Control': 'no-cache',
    'Host': 'user.guancha.cn'
}

'''
Input data format:
data = {
    'bookName': 'aaa',
    'chapters': [
        {
            'title': 'bbb',
            'sections': [
                'title': 'ccc',
                'description': 'ddd'
            ]
        }
    ]
}

Extended during function execution:
data = {
    'bookName': 'aaa',
    'generateDate': '2020-01-01-00-00'
    'chapters': [
        {
            'title': 'bbb',
            'number': 1,
            'playOrder': 1,
            'sections': [
                {
                    'title': 'ccc',
                    'number': 1,
                    'playOrder': 2,
                    'description': 'ddd'
                }
            ]
        }
    ]
}
'''
def extendData(data, buildDate):
    data['generateDate'] = buildDate
    # reserve 1 for ToC
    chapterNum = 1
    playOrder = 1

    for chapter in data['chapters']:
        chapterNum += 1
        playOrder += 1
        chapter['number'] = chapterNum
        chapter['playOrder'] = playOrder

        sectionNum = 0
        for section in chapter['sections']:
            playOrder += 1
            sectionNum += 1
            section['number'] = sectionNum
            section['playOrder'] = playOrder
    logDataTree(data)
    return data

def downloadImages(mapList, outputDir, imgSubdir):
    imgSubdirPath = '/'.join([outputDir, 'images', imgSubdir])
    os.mkdir(imgSubdirPath)
    session = requests.Session()
    for img in mapList:
        try:
            htmlLogger.debug("<Image Dl>: %s ==> %s/%s" % (img['srcUrl'], imgSubdir, img['dstFile']))
            imgContent = None
            r = session.get(img['srcUrl'])
            if r.status_code == 200:
                imgContent = r.content
            else:
                htmlLogger.info("Fail to download image from [%s], retry with headers again ..." % img['srcUrl'])
                r = session.get(img['srcUrl'], headers = gHeaders)
                if r.status_code == 200:
                    imgContent = r.content
                else:
                    htmlLogger.info("Fail to download image from [%s] with headers again" % img['srcUrl'])
            if imgContent == None:
                continue
            imgFilePath = '/'.join([imgSubdirPath, img['dstFile']])
            #print(imgFilePath)
            with open(imgFilePath, 'wb') as f:
                f.write(imgContent)
        except:
            htmlLogger.error("exception occurs during downloading [%s]" % img['srcUrl'])

def buildHtmls(data, prefix = ''):
    buildDate = datetime.today().strftime("%Y-%m-%d-%H-%M")
    outputDir = "%s/../%s-%s" % (selfDir, prefix, buildDate)
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
    if not os.path.isdir(outputDir):
        os.unlink(outputDir)
        os.mkdir(outputDir)
    os.mkdir(outputDir + '/images' )
    extendData(data, buildDate)
    templateEnv = Environment(loader=FileSystemLoader("%s/../templates" % selfDir))
    for mapElem in gTemplateTargetMap:
        renderAndWrite(templateEnv, mapElem['template'], data, mapElem['target'], outputDir)
    for chapter in data['chapters']:
        renderAndWrite(templateEnv, 'chapter.html', chapter, '%s.html' % chapter['number'], outputDir)
        if 'imgDlMap' in chapter.keys() and 'imgSubdir' in chapter.keys():
            downloadImages(chapter['imgDlMap'], outputDir, chapter['imgSubdir'])
    return outputDir

def renderAndWrite(env, templateName, context, targetFilename, outputDir):
    """Render `templateName` with `context` and write the result in the file
    `outputDir`/`targetFilename`."""

    template = env.get_template(templateName)
    with open(os.path.join(outputDir, targetFilename), 'w') as f:
        f.write(template.render(**context))

def logDataTree(data):
    htmlLogger.debug( '='*10)
    htmlLogger.debug( ' '*1 + 'title: ' + data['bookName'])
    htmlLogger.debug( ' '*1 + 'date: ' + data['generateDate'])
    htmlLogger.debug( ' '*1 + 'chapters: ')
    for chapter in data['chapters']:
        htmlLogger.debug( ' '*3 + 'chapter: ' + chapter['title'])
        htmlLogger.debug( ' '*3 + 'chapterNum: %d' % (chapter['number']))
        htmlLogger.debug( ' '*3 + 'order: %d' % (chapter['playOrder']))
        htmlLogger.debug( ' '*3 + 'sections: ' )
        for section in chapter['sections']:
            htmlLogger.debug( ' '*5 + 'section: ' + section['title'])
            htmlLogger.debug (' '*5 + 'sectionNum: %d' % (section['number']))
            htmlLogger.debug (' '*5 + 'order: %d' % (section['playOrder']))

if __name__ == "__main__":
    data = {
        'bookName': 'aaa',
        'chapters': [
            {
                'title': 'bbb',
                'sections': [
                    {
                        'title': 'ccc',
                        'description': 'ddd'
                    }
                ]
            }
        ]
    }
    buildHtmls(data)

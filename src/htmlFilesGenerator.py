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
    for img in mapList:
        try:
            r = requests.get(img['srcUrl'])
            if r.status_code != 200:
                htmlLogger.info("Fail to download image from [%s]" % img['srcUrl'])
                continue
            imgFilePath = '/'.join([imgSubdirPath, img['dstFile']])
            print(imgFilePath)
            with open(imgFilePath, 'wb') as f:
                f.write(r.content)
        except:
            htmlLogger.error("exception occurs during downloading [%s]" % img['srcUrl'])

def buildHtmls(data, outputDir = ''):
    buildDate = datetime.today().strftime("%Y-%m-%d-%H-%M")
    if outputDir == '':
        outputDir = "%s/../%s" % (selfDir, buildDate)
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
        downloadImages(chapter['imgDlMap'], outputDir, chapter['imgSubdir'])
    return True

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

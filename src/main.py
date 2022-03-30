import rssDataFetcher
import htmlFilesGenerator


if __name__ == "__main__":
    chapter = rssDataFetcher.fetchRssData('http://192.168.119.47/rss/RSS_PengpaiUserArticles.xml')
    data = {
        'bookName': '第一本书',
        'chapters': [
            chapter
        ]
    }
    htmlFilesGenerator.buildHtmls(data)

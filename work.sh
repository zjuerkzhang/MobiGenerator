#!/bin/sh

filePath=$0
fileDir=`dirname $filePath`
cd $fileDir

configFileViewDir="/var/www/html/privateFiles/"
rssMobiDir="/var/www/html/publicFiles/mobiBooks/"
bookMobiDir="/var/www/html/privateFiles/mobiBooks/"
mkdir -p $rssMobiDir
mkdir -p $bookMobiDir
mkdir -p log

rm -rf rss-202*
rm -rf bluebook-202*
echo "===== RSS Mobi Generation ====="
python3 src/rssDataFetcher.py
ret=$?
if [ $ret -eq 0 ]
then
    htmlDir=`ls -l|awk '{print $NF}'|grep -P "rss-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}"|tail -n 1`
    echo $htmlDir
    cp assets/*.css ./$htmlDir/
    ./kindlegen -c1 ./$htmlDir/target.opf

    mv ./$htmlDir/target.mobi $rssMobiDir/$htmlDir.mobi
    #rm -rf $htmlDir
else
    echo "`date`: no html files for RSS generated"
fi

echo "===== Bluebook Mobi Generation ====="
python3 src/bluebookDataFetcher.py
ret=$?
if [ $ret -eq 0 ]
then
    htmlDir=`ls -l|awk '{print $NF}'|grep -P "bluebook-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}"|tail -n 1`
    echo $htmlDir
    cp assets/*.css ./$htmlDir/
    ./kindlegen -c1 ./$htmlDir/target.opf

    mv ./$htmlDir/target.mobi $bookMobiDir/$htmlDir.mobi
    #rm -rf $htmlDir
else
    echo "`date`: no html files for RSS generated"
fi

cp config/config.json $configFileViewDir/


exit 0

#!/bin/sh

filePath=$0
fileDir=`dirname $filePath`
cd $fileDir

targetDirPath="./mobi"
mkdir -p $targetDirPath
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
    scp -r "./$htmlDir" debian:~/mobi/
    ssh debian "cd ~/mobi/; ./kindlegen -c1 ./$htmlDir/target.opf;"
    scp debian:~/mobi/$htmlDir/target.mobi targetDirPath/$htmlDir.mobi
    ssh debian "rm -rf ~/mobi/$htmlDir"

    #rm -rf $htmlDir
else
    echo "`date`: no html files for RSS generated"
fi

echo "===== Bluebook Mobi Generation ====="
python3 src/bluebookDataFetcher.py
ret=$?
if [ $ret -eq 0 ]
then
    htmlDirs=`ls -l|awk '{print $NF}'|grep -P "bluebook-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}"`
    for htmlDir in $htmlDirs
    do
        echo $htmlDir
        cp assets/*.css ./$htmlDir/
        scp -r "./$htmlDir" debian:~/mobi/
        ssh debian "cd ~/mobi/; ./kindlegen -c1 ./$htmlDir/target.opf;"
        scp debian:~/mobi/$htmlDir/target.mobi $targetDirPath/$htmlDir.mobi
        ssh debian "rm -rf ~/mobi/$htmlDir"
        #rm -rf $htmlDir
    done
else
    echo "`date`: no html files for RSS generated"
fi

cp config/config.json $targetDirPath/


exit 0

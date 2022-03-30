#!/bin/sh

filePath=$0
fileDir=`dirname $filePath`
cd $fileDir

targetDir="/var/www/html/publicFiles/mobiBooks/"
mkdir -p $targetDir
mkdir -p log

rm -rf 202*

python3 src/rssDataFetcher.py
ret=$?
ret=0
if [ $ret -ne 0 ]
then
    echo "`date`: no html files generated"
    exit $ret
fi

htmlDir=`ls -l|awk '{print $NF}'|grep -P "\d{4}-\d{2}-\d{2}-\d{2}-\d{2}"|tail -n 1`
#echo $htmlDir
cp assets/*.css ./$htmlDir/
./kindlegen -c1 ./$htmlDir/target.opf

mv ./$htmlDir/target.mobi $targetDir/$htmlDir.mobi
#rm -rf $htmlDir
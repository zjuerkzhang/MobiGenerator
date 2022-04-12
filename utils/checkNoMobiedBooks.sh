#!/bin/sh

filePath=$0
fileDir=`dirname $filePath`
cd $fileDir

notMobiedBookListFile=NoMobiedBooks.txt
MobiedBookListFile=MobiedBooks.txt

rm -rf $notMobiedBookListFile
rm -rf $MobiedBookListFile

jsonContent=`ssh bwg "cat /root/bluebook/html/config/config.json"`
titles=`echo "$jsonContent"|jq '.[]|.title'|awk -F '"' '{print $2}'`
titlesAndHashes=`echo "$jsonContent"|jq '.[]|.title, .dir'|awk -F '"' '{print $2}'`

mobiedBooks=`cat "../config/config.json" |jq '.bluebooks|.[]|.books|.[]|.title'|awk -F '"' '{print $2}'`
for t in $titles
do
    mobiedBook=`echo "$mobiedBooks" |grep "$t"`
    if [ -z "$mobiedBook" ]
    then
        echo "$t" >> $notMobiedBookListFile
        hashCode=`echo "$titlesAndHashes"|grep "$t" -A 1|tail -n 1`
        echo "https://bloghz.ddns.net/b/static/books/$hashCode/main.html" >> $notMobiedBookListFile
    else
        echo "$t" >> $MobiedBookListFile
    fi
done
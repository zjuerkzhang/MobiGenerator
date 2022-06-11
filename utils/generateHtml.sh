#/bin/sh

scriptPath=$0
scriptDir=`dirname $scriptPath`
cd $scriptDir

configPath="../config/config.json"
htmlPath="../mobi/index.html"
hiddenHtmlPath="../mobi/hidden.html"

purgeOldRssFiles()
{
    today=`date +%d`
    if [ $today -lt 10 ]
    then
        return 0
    fi
    thisMonthFilePattern="rss-`date +%Y-%m-`"

    rssMobisToPurge=`ls -l ../mobi|awk '{print $NF}'|grep -P "rss-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}"|grep -v "$thisMonthFilePattern"`
    echo "remove old rss files: $rssMobisToPurge"
    for rss in $rssMobisToPurge
    do
        rm -f ../mobi/$rss
    done
}

generateHtmlBorderHeader()
{
    targetHtmlPath=$1
    echo "<html>" > $targetHtmlPath
    echo "<head>" >> $targetHtmlPath
    echo "<title>Mobi电子书</title>" >> $targetHtmlPath
    echo "<meta charset='UTF-8'>" >> $targetHtmlPath
    echo "<meta name='viewport' content='width=device-width, height=device-height, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'>" >> $targetHtmlPath
    echo "</head>" >> $targetHtmlPath
    echo "<body>" >> $targetHtmlPath
}

generateRssContent()
{
    targetHtmlPath=$1
    # generate Rss Mobi part
    echo "<h1>RSS</h1>" >> $targetHtmlPath
    echo "<div><table border='2' width='800px' height='50px'>" >> $targetHtmlPath
    echo "<tr><th width='40%'>RSS文件名</th><th></th></tr>" >> $targetHtmlPath

    rssMobis=`ls -l ../mobi|awk '{print $NF}'|grep -P "rss-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}"`
    for rss in $rssMobis
    do
        echo "<tr>" >> $targetHtmlPath
        echo "<td><a href='./$rss'>$rss</a></td>" >> $targetHtmlPath
        echo "<td></td>" >> $targetHtmlPath
        echo "</tr>" >> $targetHtmlPath
    done
    echo "</table></div>" >> $targetHtmlPath
}

generateEbookContent()
{
    targetHtmlPath=$1
    # generate normal book Mobi part
    echo "<h1>Book</h1>" >> $targetHtmlPath
    echo "<div><table border='2' width='800px' height='50px'>" >> $targetHtmlPath
    echo "<tr><th width='40%'>书名</th><th></th></tr>" >> $targetHtmlPath
    books=`ls -l ../mobi/|grep -P "\.(mobi)|(azw3)$"|awk '{print $NF}'|grep -v -P "^(rss)|(bluebook)"`
    for b in $books
    do
        echo "<tr>" >> $targetHtmlPath
        echo "<td><a href='./$b'>$b</a></td>" >> $targetHtmlPath
        echo "<td></td>" >> $targetHtmlPath
        echo "</tr>" >> $targetHtmlPath
    done
    echo "</table></div>" >> $targetHtmlPath
}

generateBluebookContent()
{
    targetHtmlPath=$1
    configContent=`cat $configPath`
    # generate Book Mobi part
    echo "<h1>Blue Book</h1>" >> $targetHtmlPath
    echo "<div><table border='2' width='800px' height='50px'>" >> $targetHtmlPath
    echo "<tr><th width='40%'>书名</th><th>章节内容</th></tr>" >> $targetHtmlPath
    titleLines=`echo "$configContent" |jq '.bluebooks|.[]|.title'|awk -F '"' '{print $2}'|sort`
    lineCount=`echo "$titleLines"|wc -l`
    idxes=`seq $lineCount`
    for i in $idxes
    do
        echo "<tr>" >> $targetHtmlPath
        title=`echo "$titleLines"|head -n $i|tail -n 1`
        link=`echo "$configContent"|jq -r --arg x "$title" '.bluebooks|.[]|select(.title == $x)|.filename'|awk -F '/' '{print "./"$NF}'`
        echo "<td valign='top'><a href='$link'>$title</a></td>" >> $targetHtmlPath
        echo "<td>" >> $targetHtmlPath
        chapterLines=`echo "$configContent"|jq -r --arg x "$title" '.bluebooks|.[]|select(.title == $x)|.books|.[]|.title'|sort`
        chapterCount=`echo "$chapterLines"|wc -l`
        if [ $chapterCount -ne 1 ]
        then
            echo "<ul>" >> $targetHtmlPath
            cidxes=`seq $chapterCount`
            for j in $cidxes
            do
                chapter=`echo "$chapterLines"|head -n $j|tail -n 1`
                echo "<li>$chapter</li>" >> $targetHtmlPath
            done
            echo "</ul>" >> $targetHtmlPath
        fi
        echo "</td></tr>" >> $targetHtmlPath
    done
    echo "</table></div>" >> $targetHtmlPath
}

generateHtmlBorderTail()
{
    targetHtmlPath=$1
    echo "</body></html>" >> $targetHtmlPath
}

purgeOldRssFiles
generateHtmlBorderHeader $htmlPath.new
generateRssContent $htmlPath.new
generateEbookContent $htmlPath.new
generateHtmlBorderTail $htmlPath.new
mv $htmlPath.new $htmlPath

generateHtmlBorderHeader $hiddenHtmlPath.new
generateRssContent $hiddenHtmlPath.new
generateEbookContent $hiddenHtmlPath.new
generateBluebookContent $hiddenHtmlPath.new
generateHtmlBorderTail $hiddenHtmlPath.new
mv $hiddenHtmlPath.new $hiddenHtmlPath

bwgFiles=`ssh bwg "ls -l /var/www/html/privateFiles/mobi/" |grep -v -P "^(total)|(总用量)"| awk '{print $NF}'`
localFiles=`ls -l ../mobi/|grep -v -P "^(total)|(总用量)"| awk '{print $NF}'`
for localFile in $localFiles
do
    found=`echo "$bwgFiles"|grep "$localFile"`
    if [ -z "$found" ]
    then
        scp ../mobi/$localFile bwg:/var/www/html/privateFiles/mobi/
    fi
done
scp ../mobi/*.html bwg:/var/www/html/privateFiles/mobi/

for bwgFile in $bwgFiles
do
    found=`echo "$localFiles"|grep "$bwgFile"`
    if [ -z "$found" ]
    then
        ssh bwg "rm -f /var/www/html/privateFiles/mobi/$bwgFile"
    fi
done

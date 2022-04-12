#/bin/sh

scriptPath=$0
scriptDir=`dirname $scriptPath`
cd $scriptDir

configPath="../config/config.json"
htmlPath="../mobi/index.html"
newHtmlPath=$htmlPath.new

configContent=`cat $configPath`

echo "<html>" > $newHtmlPath
echo "<head>" >> $newHtmlPath
echo "<title>Mobi电子书</title>" >> $newHtmlPath
echo "<meta charset='UTF-8'>" >> $newHtmlPath
echo "<meta name='viewport' content='width=device-width, height=device-height, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'>" >> $newHtmlPath
echo "</head>" >> $newHtmlPath
echo "<body>" >> $newHtmlPath

# generate Rss Mobi part
echo "<h1>RSS</h1>" >> $newHtmlPath
echo "<div><table border='2' width='800px' height='50px'>" >> $newHtmlPath
echo "<tr><th width='40%'>RSS文件名</th><th></th></tr>" >> $newHtmlPath

rssMobis=`ls -l ../mobi|awk '{print $NF}'|grep -P "rss-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}"`
for rss in $rssMobis
do
    echo "<tr>" >> $newHtmlPath
    echo "<td><a href='./$rss'>$rss</a></td>" >> $newHtmlPath
    echo "<td></td>" >> $newHtmlPath
    echo "</tr>" >> $newHtmlPath
done
echo "</table></div>" >> $newHtmlPath

# generate normal book Mobi part
echo "<h1>Book</h1>" >> $newHtmlPath
echo "<div><table border='2' width='800px' height='50px'>" >> $newHtmlPath
echo "<tr><th width='40%'>书名</th><th></th></tr>" >> $newHtmlPath
books=`ls -l ../mobi/|grep -P "\.mobi$"|awk '{print $NF}'|grep -v -P "^(rss)|(bluebook)"`
for b in $books
do
    echo "<tr>" >> $newHtmlPath
    echo "<td><a href='./$b'>$b</a></td>" >> $newHtmlPath
    echo "<td></td>" >> $newHtmlPath
    echo "</tr>" >> $newHtmlPath
done
echo "</table></div>" >> $newHtmlPath

# generate Book Mobi part
echo "<h1>Blue Book</h1>" >> $newHtmlPath
echo "<div><table border='2' width='800px' height='50px'>" >> $newHtmlPath
echo "<tr><th width='40%'>书名</th><th>章节内容</th></tr>" >> $newHtmlPath
titleLines=`echo "$configContent" |jq '.bluebooks|.[]|.title'|awk -F '"' '{print $2}'|sort`
lineCount=`echo "$titleLines"|wc -l`
idxes=`seq $lineCount`
for i in $idxes
do
    echo "<tr>" >> $newHtmlPath
    title=`echo "$titleLines"|head -n $i|tail -n 1`
    link=`echo "$configContent"|jq -r --arg x "$title" '.bluebooks|.[]|select(.title == $x)|.filename'|awk -F '/' '{print "./"$NF}'`
    echo "<td><a href='$link'>$title</a></td>" >> $newHtmlPath
    echo "<td>" >> $newHtmlPath
    chapterLines=`echo "$configContent"|jq -r --arg x "$title" '.bluebooks|.[]|select(.title == $x)|.books|.[]|.title'|sort`
    chapterCount=`echo "$chapterLines"|wc -l`
    if [ $chapterCount -ne 1 ]
    then
        echo "<ul>" >> $newHtmlPath
        cidxes=`seq $chapterCount`
        for j in $cidxes
        do
            chapter=`echo "$chapterLines"|head -n $j|tail -n 1`
            echo "<li>$chapter</li>" >> $newHtmlPath
        done
        echo "</ul>" >> $newHtmlPath
    fi
    echo "</td></tr>" >> $newHtmlPath
done
echo "</table></div>" >> $newHtmlPath


echo "</body></html>" >> $newHtmlPath
mv $newHtmlPath $htmlPath
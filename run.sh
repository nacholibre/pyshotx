#!/bin/bash
showUsage () {
    echo 'Usage: run.sh [arguments]'
    echo ''
}
showArguments () {
    echo 'Arguments:'
    echo '       -c[=NUM]                    Number of children screenshot taking processes'
    echo '       -d[=PATH]                   Path to the screenshot directory, ending with /'
    echo '       -l                          Use directory levels when saving screenshots'
}

childrenProcesses=1
screenshotsDirectory='screens/'
useLevels=false
while getopts "h?cld:" opt; do
    case "$opt" in
        h|\?)
            showUsage
            showArguments
            exit 0
            ;;
        c)  childrenProcesses=$OPTARG
            ;;
        d)  screenshotsDirectory=$OPTARG
            ;;
        l)
            useLevels='levels'
            ;;
    esac
done

pidsList=""

./webserver.py $useLevels > /dev/null 2> /dev/null &
pidsList="$pidsList $!"
for (( i=1; i <= childrenProcesses; i++ ))
do
    phantomjs screenshot.js $screenshotsDirectory > /dev/null 2> /dev/null &
    pidsList="$pidsList $!"
done

trap "kill $pidsList" exit INT TERM
wait

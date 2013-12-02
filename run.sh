#!/bin/bash
showUsage () {
    echo 'Usage: run.sh [arguments]'
    echo ''
}
showArguments () {
    echo 'Arguments:'
    echo '       -c                    Number of children screenshot taking processes'
    echo '       -d                    Path to the screenshot directory, ending with /'
    echo '       -l                    Use levels'
}

childrenProcesses=1
screenshotsDirectory='screens/'
while getopts "h?cd:" opt; do
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
    esac
done

pidsList=""

./webserver.py > /dev/null 2> /dev/null &
pidsList="$pidsList $!"
for (( i=1; i <= childrenProcesses; i++ ))
do
    phantomjs screenshot.js $screenshotsDirectory > /dev/null 2> /dev/null &
    pidsList="$pidsList $!"
done

trap "kill $pidsList" exit INT TERM
wait

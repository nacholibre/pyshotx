#!/bin/bash
showUsage () {
    echo 'Usage: run.sh [arguments]'
    echo ''
}
showArguments () {
    echo 'Arguments:'
    echo '       -c                    Number of children screenshot taking processes'
}

while getopts "h?c:" opt; do
    case "$opt" in
        h|\?)
            showUsage
            showArguments
            exit 0
            ;;
        c)  childrenProcesses=$OPTARG
            ;;
    esac
done

if [ -z "$*" ]; then
    childrenProcesses=1
fi

pidsList=""

./webserver.py > /dev/null 2> /dev/null &
pidsList="$pidsList $!"
for (( i=1; i <= childrenProcesses; i++ ))
do
    phantomjs screenshot.js > /dev/null 2> /dev/null &
    pidsList="$pidsList $!"
done

trap "kill $pidsList" exit INT TERM
wait

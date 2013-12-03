#!/bin/bash
showUsage () {
    echo 'Usage: run.sh [arguments]'
    echo ''
}
showArguments () {
    echo 'Arguments:'
    echo '       -c[=NUM]                    Number of children screenshot taking processes'
    echo '       -d[=PATH]                   Path to the screenshot directory, ending with /'
    echo '       -e                          When in debug mode log files will be created, works only with one children'
    echo '       -l                          Use directory levels when saving screenshots. If you use this you need to fist generate levels using generate_levels.sh'
}

childrenProcesses=1
screenshotsDirectory='screens/'
useLevels=false
debug=false
while getopts "h?cled:" opt; do
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
        e)
            debug=true
            ;;
        l)
            useLevels='levels'
            ;;
    esac
done

pidsList=""

if $debug; then
    ./webserver.py $useLevels >& webserver.log &
else
    ./webserver.py $useLevels >& /dev/null &
fi
pidsList="$pidsList $!"
for (( i=1; i <= childrenProcesses; i++ ))
do
    if $debug; then
        phantomjs screenshot.js $screenshotsDirectory >& phantomjs_children.log &
    else
        phantomjs screenshot.js $screenshotsDirectory >& /dev/null &
    fi
    pidsList="$pidsList $!"
done

trap "kill $pidsList" exit INT TERM
wait

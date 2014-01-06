#!/bin/bash
showUsage () {
    echo 'Usage: run.sh [arguments]'
    echo ''
}

runProcess () {
    debug=$1
    logNumber=$2
    echo 'starting new process'
    if [[ -z "$debug" ]]; then
        phantomjs screenshot.js $screenshotsDirectory >& phantomjs_children_$logNumber.log &
    else
        phantomjs screenshot.js $screenshotsDirectory >& /dev/null &
    fi
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
while getopts "h?c:led:" opt; do
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
runningChildrenProcesses=""
childPids=""

if $debug; then
    ./webserver.py $useLevels >& webserver.log &
else
    ./webserver.py $useLevels >& /dev/null &
fi

pidsList="$pidsList $!"
for (( i=1; i <= childrenProcesses; i++ ))
do
    runProcess $debug $i
    runningChildrenProcesses="$runningChildrenProcesses $!-$i"
    childPids="$childPids $!"
done

trap "kill $pidsList $childPids" exit INT TERM

while true
do
    for serverIds in $pidsList
    do
        if [ ! -d "/proc/$serverIds" ]; then
            exit
        fi
    done
    for processID_logNumber in $runningChildrenProcesses
    do
        split=(`echo $processID_logNumber | tr '-' ' '`)
        processID=${split[0]}
        logNumber=${split[1]}
        if [ ! -d "/proc/$processID" ]; then
            runProcess $debug $logNumber
            runningChildrenProcesses=$(echo $runningChildrenProcesses | sed "s/$processID/$!/g")
            childPids=$(echo $childPids | sed "s/$processID/$!/g")
            trap "kill $pidsList $childPids" exit INT TERM
        fi
    done
    sleep 5
done

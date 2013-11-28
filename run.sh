#!/bin/sh
while getopts "h?vf:" opt; do
    case "$opt" in
        h|\?)
            echo 'HELP'
            show_help
            exit 0
            ;;
        v)  verbose=1
            echo 'VERBOSE'
            ;;
        f)  output_file=$OPTARG
            echo $OPTARG
            echo 'F'
            ;;
    esac
done
exit

pidsList=""

./webserver.py > /dev/null 2> /dev/null &
pidsList="$pidsList $!"
phantomjs screenshot.js > /dev/null 2> /dev/null &
pidsList="$pidsList $!"

trap "kill $pidsList" exit INT TERM
wait

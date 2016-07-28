#!/usr/bin/env bash
# Requires options BUILDFILE, BUILDNAME, DISTRIBUTE_FLAG
# BUILDNAME should be the same as the BUILDFILE, without .py...


echo "BUILDNAME '$1' supplied. Is this correct? [y/n]"
say "Please confirm your build name." &
read checkforargs
if [ "$checkforargs" == "n" ]; then
    echo "Exiting!"; exit
fi

# COMMENT SAY LINES FOR NON MACOSX SYSTEMS
say "Would you like to update the todo.txt file?" &
echo "Would you like to update the todo.txt file? [y/n]"
read checkfortodo
if [ "$checkfortodo" == "y" ]; then
    say "Updating TODO tags for PingStats." &
    if [ "$2" == "v" ]; then
        todotracker -p ./ -f py,sh -Q
    else
        todotracker -p ./ -f py,sh
    fi
fi

echo "Build? [y/n]"
read checkforbuild
if [ "$checkforbuild" == "n" ]; then
    echo "Exiting!"; say "Exiting"; exit
fi

echo "Building $1!"

# COMMENT SAY LINES FOR NON MACOSX SYSTEMS
say "Performing build!"

zip -db -dc -dg -T -9 ./dist/$1.zip ./PingStats.py ./install.sh

#!/usr/bin/env bash
# Requires options BUILDFILE, BUILDNAME, DISTRIBUTE_FLAG
# BUILDNAME should be the same as the BUILDFILE, without .py...

echo "Updating TODO tags for ./PingStats.py."

echo "TODO MASTER" &> "TODO.txt"
echo "" >> "TODO.txt"

echo "./PingStats.py" >> "TODO.txt"
cat ./PingStats.py | grep "# TODO" >> "TODO.txt"
echo "" >> "TODO.txt"


echo "BUILDNAME '$1' supplied. Is this correct? [y/n]"
say "Please confirm your build name."
read checkforargs
if [ "$checkforargs" == "n" ]; then
    echo "Exiting!"; exit
fi

if [ "$(cat ./PingStats.py | grep -c "# TODO")" != "0" ]; then
    echo "There are TODO's that require attention, would you like to review them? [y/n]"
    # COMMENT SAY LINES FOR NON MACOSX SYSTEMS
    say "There are TODO's that require your attention!"
    read checkfortodo
    if [ "$checkfortodo" == "y" ]; then
        cat ./PingStats.py | grep "# TODO"
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

zip ./dist/$1.zip ./PingStats.py ./install.sh
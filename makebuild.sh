#!/usr/bin/env bash
# Requires options BUILDFILE, BUILDNAME, DISTRIBUTE_FLAG
# BUILDNAME should be the same as the BUILDFILE, without .py...

# TODO BUG FileCreationError: Bug was caused by the statement "if [ $(cat $1 | grep -c "# TODO") > 0]" was outputting the results of grep to ./0
# TODO BUG FileCreationError: Review Pull Request #9 for full bug report.
# TODO BUG FileCreationError: **CLOSED**

echo "Updating TODO tags for ./PingStats.py and ./makebuil.sh."

echo "TODO MASTER" &> "TODO.txt"
echo "" >> "TODO.txt"

echo "./PingStats.py" >> "TODO.txt"
cat ./PingStats.py | grep "# TODO" >> "TODO.txt"
echo "" >> "TODO.txt"

echo "./makebuild.sh" >> "TODO.TXT"
cat ./makebuild.sh | grep "# TODO" >> "TODO.txt"
echo "" >> "TODO.txt"

if [ "$(cat $1 | grep -c "# TODO")" != "0" ]; then  # logic changed to reflect usage.
    echo "There are TODO's that require attention, would you like to review them? [y/n]"
    # COMMENT SAY LINES FOR NON MACOSX SYSTEMS
    say "There are TODO's that require your attention!"
    read checkfortodo
    if [ "$checkfortodo" == "y" ]; then
        cat $1 | grep "# TODO"
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

#cp $1 ./build/build.py
## Version Dating string replacement functionality
#OLD="versiondate = **DEV**"
#NEW="versiondate = "
#currdate=$(date)
#newdate="version date = '$currdate'"
#echo $newdate
#sed "s/$OLD/$newdate/g"

pyinstaller -w -n "$2" "$1"

if [ "$3" == "dist" ]; then
    echo "Removing old binary '$2' from /usr/local/bin/ and copying the new one."
    rm /usr/local/bin/$2
    cp ./dist/$2 /usr/local/bin/$2
fi

echo "Done!"
# COMMENT SAY LINES FOR NON MACOSX SYSTEMS
say "Done!"
echo ""
echo "Testing build..."
./dist/$2 -v

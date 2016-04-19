#!/usr/bin/env bash
# Requires options BUILDFILE, BUILDNAME, DISTRIBUTE_FLAG
# BUILDNAME should be the same as the BUILDFILE, without .py...

# TODO BUG FileCreationError: Bug was caused the statement if [ $(cat $1 | grep -c "# TODO") > 0] was outputting the results of grep to ./0
# TODO BUG FileCreationError: **CLOSED**

if [ "$(cat $1 | grep -c "# TODO")" != "0" ]; then  # logic changed to reflect usage.
    echo "There are TODO's that require attention, would you like to review them? [y/n]"
    say "There are TODO's that require your attention!"
    read checkfortodo
    if [ "$checkfortodo" == "y" ]; then
        cat $1 | grep "# TODO"
        echo "Build? [y/n]"
        read checkforbuild
        if [ "$checkforbuild" == "n" ]; then
            echo "Exiting!"; say "Exiting"; exit
        fi
    fi
fi

echo "Building $1!"

# UNCOMMENT SAY LINES FOR NON MACOSX SYSTEMS
say "Performing build!"

pyinstaller -F -c -n "$2" "$1"

if [ "$3" == "dist" ]; then
    echo "Removing old binary '$2' from /usr/local/bin/ and copying the new one."
    rm /usr/local/bin/$2
    cp ./dist/$2 /usr/local/bin/$2
fi

#rm ./0 &> /dev/null

echo "Done!"
# UNCOMMENT SAY LINES FOR NON MACOSX SYSTEMS
say "Done!"
echo ""
echo "Testing build..."
./dist/$2 -v


#!/usr/bin/env bash
# Requires options BUILDFILE, BUILDNAME, Distribute option
# BUILDNAME should be the same as the BUILDFILE, without .py...

if [ $(cat $1 | grep -c "# TODO") > 1 ]; then
    echo "There are TODO's that require attention, would you like to review them? [y/n]"
    say "There are TODO's that require your attention!"
    read checkfortodo
    if [ "$checkfortodo" == "y" ]; then
        cat $1 | grep "# TODO"
        echo "Would you still like to build? [y/n]"
        read checkforbuild
        if [ "$checkforbuild" == "y" ]; then
            echo "Building $1!"
            #echo "Removing old build files..."
            #rm -r build &> /dev/null
            #rm -r dist &> /dev/null
            #rm -r $2.spec &> /dev/null

            # UNCOMMENT SAY LINES FOR NON MACOSX SYSTEMS
            say "Performing build!"
            pyinstaller -F -c $1

            if [ "$3" == "dist" ]; then
                echo "Removing old binary '$2' from /usr/local/bin/ and copying the new one."
                rm /usr/local/bin/$2
                cp ./dist/$2 /usr/local/bin/$2
            fi

            echo "Done!"
            # UNCOMMENT SAY LINES FOR NON MACOSX SYSTEMS
            say "Done!"
            echo ""
            echo "Testing build..."
            $2 -v
        else echo "Exiting!"; say "Exiting!"; exit
        fi
        exit
    else
        #echo "Removing old build files..."
        #rm -r build &> /dev/null
        #rm -r dist &> /dev/null
        #rm -r $2.spec &> /dev/null

        echo "Performing build..."
        # UNCOMMENT SAY LINES FOR NON MACOSX SYSTEMS
        say "Performing build!"
        pyinstaller -F -c $1

        if [ "$3" == "dist" ]; then
            echo "Removing old binary '$2' from /usr/local/bin/ and copying the new one."
            rm /usr/local/bin/$2
            cp ./dist/$2 /usr/local/bin/$2
        fi
        echo "Done!"
        # UNCOMMENT SAY LINES FOR NON MACOSX SYSTEMS
        say "Done!"
        echo ""
        echo "Testing build..."
        $2 -v
    fi
else
    #echo "Removing old build files..."
    #rm -r build &> /dev/null
    #rm -r dist &> /dev/null
    #rm -r $2.spec &> /dev/null

    echo "Performing build..."
    # UNCOMMENT SAY LINES FOR NON MACOSX SYSTEMS
    say "Performing build!"
    pyinstaller -F -c $1

    if [ "$3" == "dist" ]; then
        echo "Removing old binary '$2' from /usr/local/bin/ and copying the new one."
        rm /usr/local/bin/$2
        cp ./dist/$2 /usr/local/bin/$2
    fi

    echo "Done!"
    # UNCOMMENT SAY LINES FOR NON MACOSX SYSTEMS
    say "Done!"
    echo ""
    echo "Testing build..."
    $2 -v
fi

#echo "Removing old build files..."
#rm -r build &> /dev/null
#rm -r dist &> /dev/null
#rm -r $2.spec &> /dev/null

#echo "Performing build..."
## UNCOMMENT SAY LINES FOR NON MACOSX SYSTEMS
#say "Performing build!"
#pyinstaller -F -c $1
#
#if [ "$3" == "dist" ]; then
#    echo "Removing old binary '$2' from /usr/local/bin/ and copying the new one."
#    rm /usr/local/bin/$2
#    cp ./dist/$2 /usr/local/bin/$2
#fi
#
#echo "Done!"
## UNCOMMENT SAY LINES FOR NON MACOSX SYSTEMS
#say "Done!"
#echo ""
#echo "Testing build..."
#$2 -v
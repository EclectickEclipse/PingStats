#!/usr/bin/env bash

echo "Checking for python install!"
python3.5 -V &> /dev/null
if [ $? != 0 ]; then
    echo "Could not execute Python interpreter, attempting to install Python3.5."
    sudo apt-get install python3.5 &> /dev/null
    if [ $? != 0 ]; then
        echo "Could not get Python3.5!"
        echo "Exiting!"; exit
    fi
    echo "Getting required packages, this can take a while..."
    echo "Getting numpy! (Used for matplotlib)"
    pip3.5 install numpy &> /dev/null
    echo "Getting matplotlib! (Used for displaying ping packet data statistics)"
    pip3.5 install matplotlib &> /dev/null
fi

echo "Building Executable script!"
interpreterloc=$(python3.5 -c "import sys; print(sys.executable)")
echo "#! $interpreterloc" &> ./pingstats
pingstatscode=$(cat ./PingStats.py)
echo "$pingstatscode" >> ./pingstats

echo "Changing executable permissions to a+x and copying to /usr/local/bin"
sudo chmod a+x ./pingstats
mv ./pingstats /usr/local/bin/pingstats

echo ""

pingstats -v
echo ""
pingstats

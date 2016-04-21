#!/usr/bin/env bash

echo "TODO MASTER" &> "TODO.txt"
echo "" >> "TODO.txt"

echo "./PingStats.py" >> "TODO.txt"
cat ./PingStats.py | grep "# TODO" >> "TODO.txt"
echo "" >> "TODO.txt"

echo "./makebuild.sh" >> "TODO.TXT"
cat ./makebuild.sh | grep "# TODO" >> "TODO.txt"
echo "" >> "TODO.txt"
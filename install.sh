#! /bin/bash
git submodule update --init --recursive --remote
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
mkdir logs

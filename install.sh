#!/bin/sh

echo "============Creating Python Virtual Environment for Installation==============="
python3 -m venv venv

echo "============Activate the environment==============="
source venv/bin/activate

echo "============Installing Dependencies==============="
pip3 install -r requirements.txt

echo "============Installing MongoDB==============="
sudo apt install mongodb

echo "==========Done=========="
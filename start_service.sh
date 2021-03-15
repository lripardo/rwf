#!/bin/bash
cd $(dirname "$0")
./pull.sh
source venv/bin/activate
#pip install -r requirements.txt
python rwf.py

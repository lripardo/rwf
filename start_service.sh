#!/bin/bash
cd $(dirname "$0")
./pull.sh
source venv/bin/activate
python rwf.py

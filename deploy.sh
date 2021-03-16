#!/bin/bash
./pull.sh
source venv/bin/activate
if [ $# -eq 1 ]
then
    pip install -r requirements.txt
fi
sudo systemctl restart rwf.service

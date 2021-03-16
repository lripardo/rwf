#!/bin/bash
./pull.sh
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart rwf.service

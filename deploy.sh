#!/bin/bash
./pull.sh
pip install -r requirements.txt
sudo systemctl restart rwf.service

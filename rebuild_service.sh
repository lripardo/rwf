#!/bin/bash
./pull.sh
sudo systemctl stop rwf.service
sudo cp rwf.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start rwf.service

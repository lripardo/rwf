#!/bin/bash
./pull.sh
sudo systemctl stop rwf.service
sudo cp rwf.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable rwf.service
sudo systemctl start rwf.service

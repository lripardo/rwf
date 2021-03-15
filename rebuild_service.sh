#!/bin/bash
git fetch --all
git reset --hard origin/master
chmod +x start_service.sh
chmod +x rebuild_service.sh
sudo systemctl stop rwf.service
sudo cp rwf.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start rwf.service
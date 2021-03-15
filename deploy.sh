#!/bin/bash
./pull.sh
sudo systemctl stop rwf.service
sudo systemctl start rwf.service
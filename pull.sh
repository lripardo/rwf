#!/bin/bash
git fetch --all
git reset --hard origin/master
chmod +x start_service.sh
chmod +x rebuild_service.sh
chmod +x deploy.sh
chmod +x pull.sh

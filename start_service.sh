#!/bin/bash
chmod +x start_service.sh
chmod +x rebuild_service.sh
source venv/bin/activate
pip install -r requirements.txt
python rwf.py

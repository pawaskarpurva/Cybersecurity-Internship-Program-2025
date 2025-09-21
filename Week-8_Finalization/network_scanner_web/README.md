# Network Scanner Web App (Final Project)

## Overview
A local Flask-based Network Scanner that:
- Scans a subnet for open TCP ports
- Grabs basic service banners
- Stores scan items in SQLite history
- Exports CSV/HTML reports

## Setup
1. Create folder and files as provided.
2. Create and activate virtual environment:
   - Windows:
     python -m venv venv
     venv\Scripts\activate
   - Linux/macOS:
     python -m venv venv
     source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

## Run
python app.py

Open http://127.0.0.1:5000 in your browser.

## Notes
- For ARP discovery or advanced features, install scapy and Npcap (Windows) and update scanner.py.
- Only scan networks you own or have permission to scan.

## Deliverables (for final project)
- Source code
- README + documentation
- Sample CSV/HTML outputs
- Demo screenshots

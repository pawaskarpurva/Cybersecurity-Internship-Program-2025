# db.py
import sqlite3
from datetime import datetime
import csv

DB_NAME = "scanner.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subnet TEXT,
                    ports TEXT,
                    host TEXT,
                    open_ports TEXT,
                    scan_time TEXT
                )''')
    conn.commit()
    conn.close()

def save_scan(subnet, ports_text, host, open_ports):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO scans (subnet, ports, host, open_ports, scan_time) VALUES (?, ?, ?, ?, ?)",
              (subnet, ports_text, host, ",".join(map(str, open_ports)), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_history(limit=200):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, subnet, ports, host, open_ports, scan_time FROM scans ORDER BY scan_time DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def export_csv(filename="scans_export.csv", limit=200):
    rows = get_history(limit)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id","subnet","ports","host","open_ports","scan_time"])
        w.writerows(rows)
    return filename

def export_html(filename="scans_export.html", limit=200):
    rows = get_history(limit)
    with open(filename, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='utf-8'><title>Scan Export</title></head><body>")
        f.write("<h1>Scan Export</h1>")
        f.write("<table border='1' cellpadding='6' cellspacing='0'>")
        f.write("<tr><th>ID</th><th>Subnet</th><th>Ports</th><th>Host</th><th>Open Ports</th><th>Time</th></tr>")
        for row in rows:
            f.write("<tr>" + "".join(f"<td>{col}</td>" for col in row) + "</tr>")
        f.write("</table></body></html>")
    return filename

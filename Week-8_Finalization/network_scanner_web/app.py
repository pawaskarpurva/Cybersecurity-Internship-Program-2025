# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import time
import io
import pandas as pd

from scanner import scan_subnet
from db import init_db, save_scan, get_history, export_csv, export_html

app = Flask(__name__)
app.secret_key = "change-me-to-a-random-secret"
init_db()

# In-memory last results for quick downloads
_last_results = None
_last_meta = {}

@app.route("/", methods=["GET", "POST"])
def index():
    global _last_results, _last_meta
    if request.method == "POST":
        subnet = request.form.get("subnet", "").strip()
        ports = request.form.get("ports", "22 80 443").strip()
        timeout = float(request.form.get("timeout", 1.0))
        workers = int(request.form.get("workers", 200))
        per_host_workers = int(request.form.get("per_host_workers", 40))
        max_hosts = request.form.get("max_hosts") or None

        if not subnet:
            flash("Please enter a subnet (e.g., 192.168.1.0/24)", "danger")
            return redirect(url_for("index"))

        t0 = time.time()
        results = scan_subnet(subnet, ports, timeout=timeout, workers=workers, per_host_workers=per_host_workers, max_hosts=max_hosts)
        elapsed = time.time() - t0

        # persist each non-empty host result to DB
        for r in results:
            # group by ip (we save a row per host with the discovered port; this keeps simple)
            save_scan(subnet, ports, r["ip"], [r["port"]])

        _last_results = results
        _last_meta = {"subnet": subnet, "ports": ports, "elapsed": elapsed, "count": len(results)}

        return render_template("results.html", results=results, meta=_last_meta)

    return render_template("index.html")

@app.route("/history")
def history():
    rows = get_history()
    return render_template("history.html", rows=rows)

@app.route("/download/csv")
def download_csv():
    global _last_results
    if not _last_results:
        flash("No recent results to download. Use History -> Download to export saved scans.", "warning")
        return redirect(url_for("history"))
    df = pd.DataFrame(_last_results)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return send_file(io.BytesIO(buf.getvalue().encode("utf-8")), as_attachment=True,
                     download_name="scan_results.csv", mimetype="text/csv")

@app.route("/download/html")
def download_html():
    global _last_results
    if not _last_results:
        flash("No recent results to download.", "warning")
        return redirect(url_for("history"))
    df = pd.DataFrame(_last_results)
    html = df.to_html(index=False)
    return send_file(io.BytesIO(html.encode("utf-8")), as_attachment=True,
                     download_name="scan_results.html", mimetype="text/html")

@app.route("/export/history/csv")
def export_history_csv():
    filename = export_csv()
    return send_file(filename, as_attachment=True)

@app.route("/export/history/html")
def export_history_html():
    filename = export_html()
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

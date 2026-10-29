import base64
import csv
import io
import json
import os

import qrcode
import requests
from flask import Flask, render_template

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

SHEET_CSV_URL = os.environ.get(
    "SHEET_CSV_URL",
    "https://docs.google.com/spreadsheets/d/1QekapgQjyjzut7o_yevTTvbTwTAUKqx_ZMtuFiYNl8Y/edit?resourcekey=&gid=683822780#gid=683822780",
)


def fetch_rows():
    resp = requests.get(SHEET_CSV_URL, timeout=20)
    resp.raise_for_status()
    reader = csv.DictReader(io.StringIO(resp.text))
    return list(reader), reader.fieldnames or []


def make_qr(data):
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


@app.route("/")
def index():
    try:
        rows, fields = fetch_rows()
    except Exception as e:
        return f"Sheet fetch error: {e}", 500
    entries = []
    for i, row in enumerate(rows, start=1):
        uid = f"UW-TECNOVA-{i:03d}"
        payload = {"id": uid, **row}
        entries.append({"id": uid, "data": row, "qr": make_qr(json.dumps(payload))})
    return render_template("index.html", entries=entries, fields=fields)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

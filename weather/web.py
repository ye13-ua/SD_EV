from flask import Flask, jsonify, render_tmplate
import threading
import os

from EV_W import request_locales, assign_regions, REGIONS

PORT = os.getenv("WEATHER_INTERFACE_PORT", "")

app = Flask(__name__)

@app.route("/")
def index():
    return render_tmplate(index.html)

@app.route("/api/regions")
def api_regions():
    return jsonify(REGIONS)

@app.route("/api/region/<int:index>")
def api_region(index):
    if 0 <= index <= len(REGIONS):
        return jsonify(REGIONS[index])
    return jsonify({"error": "Not found"}), 404

@app.route("/api/refresh")
def api_refresh():
    request_locales()
    return jsonify({"status": "updated", "regions": len(REGIONS)})

def start_web():
    app.run(host="0.0.0.0", port=PORT)
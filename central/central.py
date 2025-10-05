from flask import Flask, render_template_string, request
import threading
import time
import random

# --------------------------
#  FAKE SIMULATION DATA
# --------------------------
charging_points = {
    "CP1": {"location": "North Avenue", "price": 0.25, "state": "Available", "kw": 0.0, "driver": None},
    "CP2": {"location": "South Street", "price": 0.30, "state": "Available", "kw": 0.0, "driver": None},
}

# --------------------------
#  BACKGROUND SIMULATION
# --------------------------
def simulate_data():
    while True:
        for cp in charging_points.values():
            if cp["state"] == "Charging":
                cp["kw"] += random.uniform(0.1, 0.5)
        time.sleep(1)

# --------------------------
#  WEB INTERFACE
# --------------------------
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>EV Central Dashboard</title>
<style>
  body { font-family: Arial, sans-serif; background: #111; color: #eee; text-align: center; }
  table { margin: auto; border-collapse: collapse; width: 80%; }
  th, td { padding: 10px; border: 1px solid #333; }
  .Available { background: #2e7d32; }    /* green */
  .Charging { background: #0277bd; }     /* blue */
  .OutOfOrder { background: #ef6c00; }   /* orange */
</style>
</head>
<body>
<h1>EVCharging Central Dashboard</h1>
<table>
<tr><th>ID</th><th>Location</th><th>Price €/kWh</th><th>State</th><th>kWh</th><th>Driver</th><th>Action</th></tr>
{% for id, cp in cps.items() %}
<tr class="{{ cp.state }}">
  <td>{{ id }}</td>
  <td>{{ cp.location }}</td>
  <td>{{ cp.price }}</td>
  <td>{{ cp.state }}</td>
  <td>{{ "%.2f"|format(cp.kw) }}</td>
  <td>{{ cp.driver or "-" }}</td>
  <td>
    {% if cp.state == "Available" %}
      <form action="/start/{{ id }}" method="post"><button>Start</button></form>
    {% elif cp.state == "Charging" %}
      <form action="/stop/{{ id }}" method="post"><button>Stop</button></form>
    {% endif %}
  </td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML, cps=charging_points)

@app.post("/start/<cp_id>")
def start(cp_id):
    cp = charging_points.get(cp_id)
    if cp and cp["state"] == "Available":
        cp["state"] = "Charging"
        cp["driver"] = "Driver1"
    return ("", 204)

@app.post("/stop/<cp_id>")
def stop(cp_id):
    cp = charging_points.get(cp_id)
    if cp and cp["state"] == "Charging":
        cp["state"] = "Available"
        cp["driver"] = None
        cp["kw"] = 0.0
    return ("", 204)

# --------------------------
#  MAIN
# --------------------------
if __name__ == "__main__":
    threading.Thread(target=simulate_data, daemon=True).start()
    app.run(host="0.0.0.0", port=8000, debug=False)

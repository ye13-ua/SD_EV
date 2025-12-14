import os
from flask import Flask, render_template_string
from weather_state import CITY_STATE, MIN_TEMP

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Weather Monitor</title>
  <meta http-equiv="refresh" content="4">
  <style>
    body {
      font-family: Segoe UI, sans-serif;
      background: #f8f9fa;
      padding: 30px;
    }
    table {
      border-collapse: collapse;
      width: 600px;
      background: white;
      box-shadow: 0 2px 5px rgba(0,0,0,.1);
    }
    th, td {
      padding: 10px;
      border-bottom: 1px solid #ddd;
      text-align: center;
    }
    th {
      background: #343a40;
      color: white;
    }
    .ok { color: green; font-weight: bold; }
    .alert { color: red; font-weight: bold; }
  </style>
</head>
<body>

<h2>🌦 Weather Monitor</h2>
<p>Alert threshold: {{ min_temp }} °C</p>

<table>
  <tr>
    <th>City</th>
    <th>Temperature (°C)</th>
    <th>Status</th>
    <th>Last update</th>
  </tr>
  {% for city, data in cities.items() %}
  <tr>
    <td>{{ city }}</td>
    <td>
        {{ "%.2f"|format(data["last_temp"]) if data["last_temp"] is not none else "—" }}
    </td>
    <td class="{{ 'alert' if data["alert"] else 'ok' }}">
        {{ "ALERT" if data["alert"] else "OK" }}
    </td>
    <td>{{ data.get("last_update", "—") }}</td>
  </tr>
  {% endfor %}
</table>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(
        TEMPLATE,
        cities=CITY_STATE,
        min_temp=MIN_TEMP
    )

def run_flask():
    port = int(os.getenv("WEATHER_PORT", "9100"))
    app.run(host="0.0.0.0", port=port, debug=False)
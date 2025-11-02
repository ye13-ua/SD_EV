##### EV_CP_Engine ##############################################################################################
# ENV definitions:                                                                                              #
# Default Engine port -> 7000                                                                                   #
# Default Central port -> 4000                                                                                  #
# Default Engine host -> "ev_cp_engine"                                                                         # 
# Default Central host -> "ev_central"                                                                          # 
# Default local UUID path -> "/app/cp_uuid.json"                                                                #
# Default Kafka Broker -> kafka:9092                                                                            #
# Docker network env. -> ev_net                                                                                 #
# Execution prompt -> "python EV_CP_M.py"                                                                       #
#                                                                                                               #
# env. dependencies -> cp_engine, central                                                                       #
#                                                                                                               #
#                                                                                                               #
#################################################################################################################

# Default libs
import socket
import time
import json
import os
import uuid
import random
import threading
import socketio
from flask import Flask, render_template_string, jsonify

# Config
ENGINE_HOST = os.getenv("ENGINE_HOST","localhost")
ENGINE_PORT = int(os.getenv("ENGINE_PORT","7000"))

CENTRAL_HOST = os.getenv("CENTRAL_HOST","http://localhost:4000")

UUID_PATH = os.getenv("UUID_PATH", f"/app/cp_uuid_{os.getenv('CP_INDEX','0')}.json")

PING_INTERVAL = 2

MONITOR_DOWN = False

CP_STATUS_CHANGED = False
already_charged = 0.0
target_kwh = 0.0
driver_id = None

sio = socketio.Client()

@sio.event
def connect():
    print("[Monitor] Connected to Central via Socket.IO")

@sio.event
def disconnect():
    print("[Monitor] Disconnected from Central")

def generate_alias(uuid_str, ciudad):
    prefix = uuid_str.split('-')[0].upper()  # primeros 8 chars del UUID
    city_tag = ciudad[:3].upper()
    return f"CP-{city_tag}-{prefix}"

# Attempts to load the UUID from local path
# If it fails, that means it's first launch and thus will create a new UUID and send it to both:
#   central for registry and engine for communication
# It is fundamentally pointless to bother central's BD as if it's the first launch; Central inevitably won't have records on the CP
def load_or_create_cp_data():
    # If a local file exists
    if os.path.exists(UUID_PATH):
        # Attempt to read
        try:
            with open(UUID_PATH, "r") as f:
                data = json.load(f)
                if "id" in data and "location" in data:
                    return data
        except Exception:
            pass
    # If no local source is found
    # Generate a new UUID
    new_id = str(uuid.uuid4())
    calle = random.choice(['Sol','Luna','Mar','Paz','Río'])
    ciudad = random.choice(['Alicante','Valencia','Zaragoza','Madrid','Barcelona'])
    location = f"Calle {calle}, {ciudad}"
    alias = generate_alias(new_id, ciudad)
    data = {"id": new_id, "alias":alias, "location":location}
    # Write down the UUID locally for future acces and send the data to 
    with open(UUID_PATH, "w") as f:
        json.dump(data, f)
    return data

# Launches in the beggining
CP_DATA = load_or_create_cp_data()
CP_ID = CP_DATA["id"]
CP_ALIAS = CP_DATA["alias"]
CP_LOCATION = CP_DATA["location"]

# Default price generated in range from 0.10 to 0.45 with only 3 decimals
CP_DEFAULT_PRICE = round(random.uniform(0.10, 0.45), 3)

engine_status = "Desconocido"
kafka_ok = False
last_ping = "---"
last_central_contact = "---"
car_status = False

# Ping engine for connection checkup
def ping_engine(action):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Establish timeout threshhold
        s.settimeout(0.75)
        # Attempt to connect and ping
        try:
            s.connect((ENGINE_HOST, ENGINE_PORT))
            payload = {"action": action, "cp_id": CP_ID}
            if action == 'AUTH':
                payload = {"action": action, "cp_id": CP_ID, "cp_price": CP_DEFAULT_PRICE}
            s.sendall(json.dumps(payload).encode())
            data = s.recv(1024)
            reply = json.loads(data.decode())
            return reply
        except Exception:
            return None
        
# Handler of infinite pings
def handle_engine():
    global engine_status, last_ping, kafka_ok, car_status, CP_STATUS_CHANGED, driver_id, already_charged, CP_DEFAULT_PRICE
    global target_kwh
    # By default there was no report yet
    last_report = None
    last_local_request = None
    
    while True:

        while MONITOR_DOWN:
            print(f"[Monitor] Simulating MONITOR_DOWN")
            time.sleep(PING_INTERVAL)
            

        reply = ping_engine("PING")
        if not reply:
            status = "BROKEN"
            kafka_ok = False
        else:
            status = reply.get("status")

            if status == "WAITING" and "local_request" in reply:
                req = reply["local_request"]
                if req != last_local_request:
                    send_charging_petition_to_central(req["driver_id"], req["target_kwh"])
                    last_local_request = req
            if status == "CHARGING_CENTRAL":
                already_charged = reply.get("charging_process")
                target_kwh = reply.get("target_kwh")
            else:
                already_charged = 0.0
                target_kwh = 0.0

            kafka_ok = reply.get("kafka_ok",True)
            car_status = reply.get("car_connected",False)
            driver_id = reply.get("driver_id",None)

            
    
        CP_DEFAULT_PRICE = reply.get("price_kwh")
        last_ping = time.strftime("%H:%M:%S")
        engine_status = status

        current_report = (status, kafka_ok)

        CP_STATUS_CHANGED = current_report != last_report
        last_report = current_report
        try:
            send_status_to_central(status, kafka_ok)
        except Exception as e:
            print(f"[[{CP_ALIAS}]] Could not send data to Central: {e}")
        
        time.sleep(PING_INTERVAL)

# Registers the CP with the Central and Central's BD
def register_CP_in_central():
    msg = {"ID_UUID": CP_ID,
           "Ubicacion": CP_ALIAS,
           "UbicacionLarga": CP_LOCATION,
           "Precio_KWH": CP_DEFAULT_PRICE,
           "Timestamp": time.strftime("%H:%M:%S")}
    sio.emit("CP_Central_Create_Socket", msg)

# Sends, on change, the status of the charging point
def send_status_to_central(status, kafka_ok):
    global last_central_contact, already_charged, driver_id
    msg = {"ID_UUID": CP_ID,
           "Estado": status,
           "KafkaOk": kafka_ok,
           "isChanged": CP_STATUS_CHANGED,
           "alreadyCharged": already_charged,
           "DriverID": driver_id,
           "Timestamp": time.strftime("%H:%M:%S")}
    sio.emit("CP_Central_Status_Socket", msg)
    last_central_contact = time.strftime("%H:%M:%S")
    already_charged = 0.0

#
def send_charging_petition_to_central(driver_id, target_charge):
    msg = {
        "ID_UUID": CP_ID,
        "DriverID": driver_id,
        "TargetCharge": target_charge,
        "Timestamp": time.strftime("%H:%M:%S")
    }
    sio.emit("CP_Central_RequestCharge_Socket", msg)

def simulate_monitor_down(t):
    global MONITOR_DOWN
    MONITOR_DOWN = True
    print(f"[Monitor] Simulating monitor down for {t} seconds")
    time.sleep(t)
    MONITOR_DOWN = False
    print("[Monitor] Monitor recovered")

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>{{ alias }}</title>
  <meta http-equiv="refresh" content="2">
  <style>
    body { font-family: Segoe UI, sans-serif; margin: 40px; background: #f8f9fa; }
    .card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); width: 400px; }
    h2 { margin-top: 0; }
    .status-ok { color: green; }
    .status-fail { color: red; }
    .status-warn { color: orange; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Monitor {{ alias }}</h2>
    <p><b>UUID:</b> {{ uuid }}</p>
    <p><b>Ubicación:</b> {{ location }}</p>
    <p><b>Precio:</b> {{ price }} €/kWh</p>
    <hr>
    <p><b>Estado Engine:</b>
      <span class="{{ 'status-ok' if status in ['ACTIVE','AUTH SUCCESS'] else 'status-fail' if status=='BROKEN' else 'status-warn' }}">
        {{ status }}
      </span>
    </p>
    <p><b>Coche conectado:</b> {{ c_status }} </p>
    {% if status == 'CHARGING_CENTRAL' %}
    <hr>
    <h3>⚡ Proceso de carga en curso</h3>
    <p><b>Progreso:</b> {{ "%.2f"|format(charged) }} / {{ "%.2f"|format(target) }} kWh</p>
    <p><b>Precio por kWh:</b> {{ "%.3f"|format(unit_price) }} €</p>
    <p><b>Costo acumulado:</b> {{ "%.2f"|format(cost) }} €</p>
    <progress value="{{ charged }}" max="{{ target }}" style="width:100%; height:20px;"></progress>
    {% endif %}
    <p><b>Kafka:</b> <span class="{{ 'status-ok' if kafka_ok else 'status-fail' }}">{{ 'OK' if kafka_ok else 'FALLO' }}</span></p>
    <p><b>Último ping:</b> {{ last_ping }}</p>
    <p><b>Último contacto con Central:</b> {{ last_central }}</p>
    <hr>
    <button onclick="simulateMonitorDown()" 
            style="padding:10px 15px; background:red; color:white; border:none; border-radius:5px; cursor:pointer;">
    Simular avería
    </button>

    <button onclick="simulateLocalUse()" 
            style="padding:10px 15px; background:green; color:white; border:none; border-radius:5px; cursor:pointer;">
    Simular uso local
    </button>

    <button onclick="simulateEngineDown()" 
            style="padding:10px 15px; background:orange; color:white; border:none; border-radius:5px; cursor:pointer;">
    Simular avería Engine
    </button>
    
    <script>
      async function simulateMonitorDown() {
        const res = await fetch('/simulate_monitor_down', {method:'POST'});
        if (res.ok) alert('Simulación de la caída del monitor');
        else alert('Error al activar simulación');
      }

      async function simulateLocalUse() {
        const res = await fetch('/simulate_local_use', {method:'POST'});
        if (res.ok) alert('Simulación de uso local activada');
        else alert('Error al simular uso local');
      }

      async function simulateEngineDown() {
        const res = await fetch('/simulate_engine_down', {method:'POST'});
        if (res.ok) alert('Avería del engine simulada');
        else alert('Error al simular avería del engine');
      }
    </script>

  </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(
        TEMPLATE,
        alias=CP_ALIAS,
        uuid=CP_ID,
        location=CP_LOCATION,
        price=CP_DEFAULT_PRICE,
        status=engine_status,
        kafka_ok=kafka_ok,
        last_ping=last_ping,
        last_central=last_central_contact,
        c_status=car_status,
        charged=already_charged,
        target=target_kwh,
    )

@app.route("/simulate_monitor_down", methods=["POST"])
def trigger_MONITOR_DOWN():
    threading.Thread(target=simulate_monitor_down, args=(12,), daemon=True).start()
    return jsonify({"message": "Simulación de avería activada durante 10s"}), 200

@app.route('/favicon.ico')
def favicon():
    from flask import Response
    # Devuelve un favicon vacío para evitar el 404
    return Response(status=204)

@app.route("/simulate_local_use", methods=["POST"])
def trigger_local_use():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ENGINE_HOST, ENGINE_PORT))
        payload = {"action": "SIMULATE_LOCAL"}
        s.sendall(json.dumps(payload).encode())
    return jsonify({"message": "Uso local simulado"}), 200

@app.route("/simulate_engine_down", methods=["POST"])
def trigger_engine_down():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ENGINE_HOST, ENGINE_PORT))
        payload = {"action": "SIMULATE_ENGINE_DOWN"}
        s.sendall(json.dumps(payload).encode())
    return jsonify({"message": "Simulación de avería del engine activada"}), 200

# Checks the status of the engine each 5 seconds, and reports changes to Central
def main():
    print(f"[{CP_ALIAS}] Monitor initiated")
    # Assumption that there's one monitor for each engine (ref. UML)
    print(f"    Engine: {ENGINE_HOST}:{ENGINE_PORT}")
    print(f"    Central: {CENTRAL_HOST}")
    
    try:
        sio.connect(CENTRAL_HOST)
        print(f"[{CP_ALIAS}] Conectado al {CENTRAL_HOST}")
    except Exception as e:
        print(f"[{CP_ALIAS}] No se pudo conectar con Central ({CENTRAL_HOST}): {e}")
        print(f"[{CP_ALIAS}] Continuando simulación sin Central...")

    # Authenticate the engine connection

    for attempt in range(5):
        auth = ping_engine("AUTH")
        if auth and auth.get("status") == "AUTH_SUCCESS":
            print(f"[{CP_ALIAS}] Engine AUTH success on attempt {attempt+1}")
            register_CP_in_central()
            break
        else:
            print(f"[{CP_ALIAS}] Engine AUTH failed, retrying... ({attempt+1}/5)")
            time.sleep(1)
    else:
        print(f"[{CP_ALIAS}] Engine AUTH failed after 5 attempts, continuing without link")

    # Infinitelly check the status each PING_INTERVAL seconds
    threading.Thread(target=handle_engine, daemon=True).start()

    port = int(os.getenv("MONITOR_PORT", 9000))
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()

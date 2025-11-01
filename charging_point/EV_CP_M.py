##### EV_CP_Engine ##############################################################################################
# ENV definitions:                                                                                              #
# Default Engine port -> 7000                                                                                   #
# Default Central port -> 8000                                                                                  #
# Default Engine host -> "ev_cp_engine"                                                                         # 
# Default Central host -> "ev_central"                                                                          # 
# Default local UUID path -> "/app/cp_uuid.json"                                                                #
# Default Kafka Broker -> kafka:9092                                                                            #
# Docker network env. -> ev_net                                                                                 #
# Execution prompt -> "python EV_CP_M.py"                                                                       #
#                                                                                                               #
# env. dependencies -> cp_engine, central                                                                       #
#                                                                                                               #
# Communication:                                                                                                #                                            
#   Register:                                                                                                   #                                        
#       action: "REGISTER"                                                                                      #                                                    
#       cp_id: CP ID                                                                                            #                                                
#       alias: Alias                                                                                            #                                                
#       location: Location                                                                                      #                                                    
#       price:  Defaul price                                                                                    #                                                        
#                                                                                                               #
#   Engine ping:                                                                                                #
#       action: "PING"                                                                                          #
#       cp_id: CP ID                                                                                            #
#                                                                                                               #
#   Report to Central:                                                                                          #
#       action: "REPORT"                                                                                        #
#       cp_id: CP ID                                                                                            #
#       status: Engine Status                                                                                   #
#       kafka_ok: Kafka status                                                                                  #
#       timestamp: timestamp                                                                                    #
#################################################################################################################

# Default libs
import socket
import time
import json
import os
import uuid
import random
import threading
from flask import Flask, render_template_string, jsonify

# Config
ENGINE_HOST = os.getenv("ENGINE_HOST","localhost")
ENGINE_PORT = int(os.getenv("ENGINE_PORT","7000"))

CENTRAL_HOST = os.getenv("CENTRAL_HOST","localhost")
CENTRAL_PORT = int(os.getenv("CENTRAL_PORT","8000"))

UUID_PATH = os.getenv("UUID_PATH", os.path.join(os.getcwd(), "cp_uuid.json"))

PING_INTERVAL = 2

MONITOR_DOWN = False


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
    global engine_status, last_ping, kafka_ok, car_status
    # By default there was no report yet
    last_report = None
    
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
            kafka_ok = reply.get("kafka_ok",True)
            car_status = reply.get("car_connected",False)
    
        last_ping = time.strftime("%H:%M:%S")
        engine_status = status

        current_report = (status, kafka_ok)

        if (current_report != last_report):
            send_status_to_central(status, kafka_ok)
            last_report = current_report
        
        time.sleep(PING_INTERVAL)

# Registers the CP with the Central and Central's BD
def register_CP_in_central():
    msg = {"action": "REGISTER",
           "cp_id": CP_ID,
           "alias": CP_ALIAS,
           "location": CP_LOCATION,
           "price": CP_DEFAULT_PRICE}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((CENTRAL_HOST, CENTRAL_PORT))
            s.sendall(json.dumps(msg).encode())
        print(f"[{CP_ALIAS}] Sent to central: {msg}")
    except Exception as e:
        print(f"[{CP_ALIAS}] Could not register with cental")

# Sends, on change, the status of the charging point
def send_status_to_central(status, kafka_ok):
    global last_central_contact
    msg = {"action": "REPORT", "cp_id": CP_ID, "status": status, "kafka_ok": kafka_ok, "timestamp": time.time()}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((CENTRAL_HOST, CENTRAL_PORT))
            s.sendall(json.dumps(msg).encode())
        last_central_contact = time.strftime("%H:%M:%S")
        print(f"[{CP_ALIAS}] Sent to Central: {msg}")
    except Exception as e:
        print(f"[{CP_ALIAS}] Could not send status to Central: {e}")

def send_perpetual_ping_cental():
    while True:
        


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
    <p><b>Kafka:</b> <span class="{{ 'status-ok' if kafka_ok else 'status-fail' }}">{{ 'OK' if kafka_ok else 'FALLO' }}</span></p>
    <p><b>Último ping:</b> {{ last_ping }}</p>
    <p><b>Último contacto con Central:</b> {{ last_central }}</p>
    <hr>
    <button onclick="simulate_monitor_down()" style="padding:10px 15px; background:red; color:white; border:none; border-radius:5px; cursor:pointer;">
      Simular avería
    </button>

    <script>
      async function simulateMonitorDown() {
        const res = await fetch('/simulate_monitor_down', {method:'POST'});
        if (res.ok) alert('Simulación de la caída del monitor');
        else alert('Error al activar simulación');
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
        c_status =car_status
    )

@app.route("/simulate_monitor_down", methods=["POST"])
def trigger_MONITOR_DOWN():
    threading.Thread(target=simulate_monitor_down, args=(12,), daemon=True).start()
    return jsonify({"message": "Simulación de avería activada durante 10s"}), 200


# Checks the status of the engine each 5 seconds, and reports changes to Central
def main():
    print(f"[{CP_ALIAS}] Monitor initiated")
    # Assumption that there's one monitor for each engine (ref. UML)
    print(f"    Engine: {ENGINE_HOST}:{ENGINE_PORT}")
    print(f"    Central: {CENTRAL_HOST}:{CENTRAL_PORT}")
    
    # Authenticate the engine connection
    auth = ping_engine("AUTH")
    if not auth or auth.get("status")!="AUTH SUCCESS":
        print(f"[{CP_ALIAS}] Engine AUTH failed or unreachable")
    else:
        register_CP_in_central()

    # Infinitelly check the status each PING_INTERVAL seconds
    threading.Thread(target=handle_engine, daemon=True).start()

    port = int(os.getenv("MONITOR_PORT", 9000))
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()

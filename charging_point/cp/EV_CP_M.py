# Registry port :4001
# Central port :4000

################################
# Logging functuionality, SKIP #
################################
import os
import logging
import cryptography
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from logging.handlers import RotatingFileHandler

LOG_PATH = os.getenv("CP_LOG_PATH", "/app/cp.log")

logger = logging.getLogger("CP_MONITOR")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

file_handler = RotatingFileHandler(
    LOG_PATH,
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# STFU Flask
logging.getLogger("werkzeug").setLevel(logging.WARNING)

##############################
# THE CHARGING POINT'S LOGIC #
##############################

# Default libs
import socket
import time
import json
import uuid
import random
import threading
import requests
import urllib3
from flask import Flask, render_template_string, jsonify

# Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ENGINE_HOST = os.getenv("ENGINE_HOST","localhost")
ENGINE_PORT = int(os.getenv("ENGINE_PORT","7000"))

CENTRAL_HOST = os.getenv("CENTRAL_HOST","https://localhost:4000")

UUID_PATH = os.getenv("UUID_PATH", f"/app/cp_uuid_{os.getenv('CP_INDEX','0')}.json")

PING_INTERVAL = 2

MONITOR_DOWN = False

CITY_LIST = ['Alicante',
             'Valencia',
             'Zaragoza',
             'Madrid',
             'Barcelona',
             'Ulaanbaatar',
             'Yakutsk',
             'Tomsk',
             'Norilsk',
             'Oymyakon']

REGISTRY_GRAPHQL = os.getenv("REGISTRY_GRAPHQL", "https://central:4001/graphql")

CP_SECRET_PATH = "/app/cp_secret.json"

CLIENT_SECRET = None

SYMMETRIC_KEY = None

CP_STATUS_CHANGED = False
already_charged = 0.0
target_kwh = 0.0
driver_id = None
last_status = None

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
    ciudad = random.choice(CITY_LIST)
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

# We load the secret we recieved from registry unit
def load_cp_secrets():
    global CLIENT_SECRET, SYMMETRIC_KEY
    if os.path.exists(CP_SECRET_PATH):
        with open(CP_SECRET_PATH, "r") as f:
            data = json.load(f)
            CLIENT_SECRET = data.get("clientSecret")
            SYMMETRIC_KEY = data.get("symmetricKey")

def save_cp_secrets(client_secret, symmetric_key):
    with open(CP_SECRET_PATH, "w") as f:
        json.dump(
            {
                "clientSecret": client_secret,
                "symmetricKey": symmetric_key
            }
        , f)

def encrypt_json(data: dict, key_hex: str) -> dict:
    key = bytes.fromhex(key_hex)
    iv = os.urandom(12)
    aesgcm = AESGCM(key)

    plaintext = json.dumps(data, separators=(",", ":")).encode("utf-8")
    ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, None)

    return {
        "iv": iv.hex(),
        "ciphertext": ciphertext_with_tag[:-16].hex(),
        "tag": ciphertext_with_tag[-16:].hex(),
    }

# GQL post function used to update/relay the status in Central
def gql_post_central(query: str, variables: dict | None = None, timeout: int = 5, _retry: bool = True):
    global SYMMETRIC_KEY, CLIENT_SECRET

    def detect_identity_issue(errors):
        try:
            for err in errors or []:
                msg = (err.get("message") or "").lower()
                code = (err.get("extensions") or {}).get("code")
                if code == "UNAUTHENTICATED":
                    return "FULL"
                if "missing symmetric key" in msg:
                    return "SYMMETRIC_ONLY"
        except Exception:
            pass
        return None

    if not CLIENT_SECRET:
        raise RuntimeError("CLIENT_SECRET missing!")
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    headers = {"Authorization": f"Bearer {CLIENT_SECRET}"}

    resp = requests.post(
        CENTRAL_HOST + "/graphql",
        json=payload,
        headers=headers,
        timeout=timeout,
        verify=False
    )
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data and data["errors"] and _retry:
        identity_issue = detect_identity_issue(data["errors"])
        try:
            if identity_issue == "SYMMETRIC_ONLY":
                logger.warning(
                    f"[{CP_ALIAS}] Central lost symmetric key — re-authenticating"
                )
                SYMMETRIC_KEY = None
                SYMMETRIC_KEY = central_auth_request(CLIENT_SECRET)
                save_cp_secrets(CLIENT_SECRET, SYMMETRIC_KEY)
            elif identity_issue == "FULL":
                logger.warning(
                    f"[{CP_ALIAS}] Central lost CP identity — full bootstrap"
                )
                CLIENT_SECRET = None
                SYMMETRIC_KEY = None
                bootstrap_cp_integrity(force_reauth=False)
        except Exception as e:
            logger.error(f"Identity recovery failed: {e}")
            raise RuntimeError(data["errors"])
        return gql_post_central(
            query,
            variables=variables,
            timeout=timeout,
            _retry=False
        )
    
    return data.get("data")

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
                payload = {"action": action, "cp_id": CP_ID, "cp_price": CP_DEFAULT_PRICE, "city": CP_LOCATION.split(",", 1)[-1].strip()}
            s.sendall(json.dumps(payload).encode())
            data = s.recv(1024)
            reply = json.loads(data.decode())
            return reply
        except Exception:
            return None
        
# Handler of infinite pings
def handle_engine():
    global engine_status, last_ping, kafka_ok, car_status, CP_STATUS_CHANGED
    global driver_id, already_charged, CP_DEFAULT_PRICE, target_kwh, last_status, CP_LOCATION

    last_local_request = None
    last_report = None

    while True:
        finished_sent = False

        while MONITOR_DOWN:
            logger.warning("Simulating MONITOR_DOWN")
            time.sleep(PING_INTERVAL)

        reply = ping_engine("PING")

        if not reply:
            logger.error("Engine unreachable — marking CP as BROKEN")
            status = "BROKEN"
            kafka_ok = False
            driver_id = None
            already_charged = 0.0
            target_kwh = 0.0
            car_status = False

        else:
            status = reply.get("status")
            kafka_ok = reply.get("kafka_ok", True)

            # FINISHED_CHARGING event
            if last_status == "CHARGING_CENTRAL" and status != "CHARGING_CENTRAL":
                prev_driver = driver_id
                prev_charged = already_charged
                logger.info(f"[{CP_ALIAS}] Charging finished, reporting FINISHED_CHARGING")
                try:
                    send_status_to_central(
                        status="FINISHED_CHARGING",
                        kafka_ok=kafka_ok,
                        extra_data={
                            "driverId": prev_driver,
                            "alreadyCharged": prev_charged,
                            "price": 80085,
                        }
                    )
                    finished_sent = True
                except Exception as e:
                    logger.error(f"Failed to report FINISHED_CHARGING: {e}")

            # local request logic
            if status == "WAITING" and "local_request" in reply:
                req = reply["local_request"]
                if req != last_local_request:
                    send_charging_petition_to_central(req["driver_id"], req["target_kwh"])
                    last_local_request = req

            # charging metrics
            if status == "CHARGING_CENTRAL":
                already_charged = float(reply.get("charging_process", 0.0) or 0.0)
                target_kwh = float(reply.get("target_kwh", 0.0) or 0.0)
            else:
                already_charged = 0.0
                target_kwh = 0.0

            car_status = reply.get("car_connected", False)
            driver_id = reply.get("driver_id", None)

            CP_DEFAULT_PRICE = reply.get("price_kwh")
            new_city = reply.get("city")
            if new_city and new_city != CP_LOCATION.split(",")[-1].strip():
                calle = CP_LOCATION.split(",")[0]
                CP_LOCATION = f"{calle}, {new_city}"
                logger.info(f"City updated from Engine: {new_city}")

            last_ping = time.strftime("%H:%M:%S")
            engine_status = status
            last_status = status

        # compute isChanged for BOTH branches
        current_report = (status, kafka_ok)
        CP_STATUS_CHANGED = current_report != last_report
        last_report = current_report

        # send status (skip duplicate if FINISHED already sent)
        try:
            if not finished_sent:
                send_status_to_central(status, kafka_ok)
        except Exception as e:
            logger.error(f"Could not send status to Central: {e}")

        if CP_STATUS_CHANGED:
            logger.info(f"Status changed: status={status}, kafka={kafka_ok}, driver={driver_id}")

        time.sleep(PING_INTERVAL)

def central_auth_request(client_secret: str):
    ciudad = CP_LOCATION.split(",")[-1].strip()

    mutation = """
    mutation AuthenticateCp($input: RegisterCpInput!) {
        authenticateCp(registerCpInput: $input) {
            id
            ciudad
            precio_kwh
            clientSecret
            symmetricKey
        }
    }
    """

    variables = {
        "input": {
            "id": CP_ID,
            "ciudad": ciudad,
            "precio_kwh": CP_DEFAULT_PRICE,
            "clientSecret": client_secret
        }
    }

    resp = requests.post(
        CENTRAL_HOST + "/graphql",
        json={"query": mutation, "variables": variables},
        timeout=5,
        verify=False
    )
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        raise RuntimeError(data["errors"])

    result = data["data"]["authenticateCp"]

    sym = result.get("symmetricKey")
    if not sym:
        raise RuntimeError("Central did not return symmetricKey")
    
    return sym

# Replacement for register_CP_in_central
def bootstrap_cp_integrity(force_reauth: bool = False):
    global CLIENT_SECRET, SYMMETRIC_KEY

    ciudad = CP_LOCATION.split(",")[-1].strip()
    # calle
    # calle = CP_LOCATION.split(",")[0].replace("Calle", "").strip()

    def registry_request():
        nonlocal ciudad

        mutation = """
        mutation CreateCp($input: CreateCpInput!) {
            createCp(createCpInput: $input) {
                id
                ciudad
                precio_kwh
                clientSecret
            }
        }
        """

        variables = {
            "input": {
                "id": CP_ID,
                "ciudad": ciudad,
                "precio_kwh": CP_DEFAULT_PRICE
            }
        }

        resp = requests.post(
            REGISTRY_GRAPHQL,
            json={"query": mutation, "variables": variables},
            timeout=5,
            verify=False
        )
        resp.raise_for_status()
        data = resp.json()

        if "errors" in data:
            raise RuntimeError(data["errors"])

        result = data["data"]["createCp"]

        if result["id"] != CP_ID:
            raise RuntimeError("Registry returned mismatching ID")
        
        secret = result.get("clientSecret")
        if not secret:
            raise RuntimeError("Registry did not return clientSecret")

        return secret
    
    if CLIENT_SECRET and SYMMETRIC_KEY and not force_reauth:
        logger.info(f"[{CP_ALIAS}] Identity already present (clientSecret + symmetricKey)")
        return

    if force_reauth and CLIENT_SECRET:
        logger.warning(f"[{CP_ALIAS}] Forcing re-auth in Central (refresh symmetricKey)")
        SYMMETRIC_KEY = central_auth_request(CLIENT_SECRET)
        save_cp_secrets(CLIENT_SECRET, SYMMETRIC_KEY)
        return
    
    if not CLIENT_SECRET:
        logger.info(f"[CP_ALIAS] Registering in Registry...")
        CLIENT_SECRET = registry_request()
        save_cp_secrets(CLIENT_SECRET, SYMMETRIC_KEY)

    logger.info(f"[{CP_ALIAS}] Authenticating in Central...")
    SYMMETRIC_KEY = central_auth_request(CLIENT_SECRET)

    save_cp_secrets(CLIENT_SECRET, SYMMETRIC_KEY)
    logger.info(f"[{CP_ALIAS}] Bootstrap complete (clientSecret + symmetricKey stored)")


# Sends, on change, the status of the charging point
#TODO rework for GQL (ID_UUID is now ID)
def send_status_to_central(status, kafka_ok, extra_data: dict | None = None):
    global last_central_contact, already_charged, driver_id, CP_DEFAULT_PRICE

    mutation = """
    mutation UpdateStatusCP($input: StatusCpInput!) {
        updateStatusCP(statusCpInput: $input)
    }
    """
    input_obj = {
        "id": CP_ID,
        "estado": status,
        "isChanged": CP_STATUS_CHANGED,
        "kafkaOK": kafka_ok,
        "alreadyCharged": already_charged,
        #"price": CP_DEFAULT_PRICE,
        "city": CP_LOCATION.split(",")[-1].strip(),
    }
    if extra_data:
        input_obj.update(extra_data)
    if driver_id is not None:
        input_obj["driverId"] = driver_id

    if not SYMMETRIC_KEY:
        raise RuntimeError("Missing symmetric key for encryption")
    encrypted = encrypt_json(input_obj, SYMMETRIC_KEY)
    encrypted["id"] = CP_ID  # El id va fuera del objeto encriptado
    variables = {"input": encrypted}

    try:
        gql_post_central(mutation, variables=variables)
        last_central_contact = time.strftime("%H:%M:%S")
    except Exception as e:
        logger.error(f"Failed to update status in Central: {e}")

#
def send_charging_petition_to_central(driver_id, target_charge):
    mutation = """
    mutation PostCommand($input: CommandInput!) {
            postCommand(commandInput: $input)
        }
    """
    payload = {
        "input": {
            "command": "CHARGING_PETTITION",
            "cpId": CP_ID,
            "driverId": driver_id,
            "targetCharge": target_charge
        }
    }

    if not SYMMETRIC_KEY:
        raise RuntimeError("Missing symmetric key for encryption")
    encrypted = encrypt_json(payload, SYMMETRIC_KEY)
    variables = {"input": encrypted}

    try:
        gql_post_central(mutation, variables=variables)
        logger.info(f"Charging petition sent: driver={driver_id}, target={target_charge} kWh")
    except Exception as e:
        logger.error(f"Failed to send charging petition: {e}")

def simulate_monitor_down(t):
    global MONITOR_DOWN
    MONITOR_DOWN = True
    logger.warning(f"Simulating MONITOR_DOWN for {t} seconds")
    time.sleep(t)
    MONITOR_DOWN = False
    logger.info("Monitor recovered")

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
  <h3>Proceso de carga en curso</h3>
  <p><b>Progreso:</b> {{ "%.2f"|format(charged) }} / {{ "%.2f"|format(target) }} kWh</p>
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
        charged=already_charged or 0.0,
        target=target_kwh or 0.0,
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
    logger.info(f"Monitor initiated for {CP_ALIAS}")
    # Assumption that there's one monitor for each engine (ref. UML)
    logger.info(f"Engine: {ENGINE_HOST}:{ENGINE_PORT}")
    logger.info(f"Registry: {REGISTRY_GRAPHQL}")

    # Load CP secret
    load_cp_secrets()

    try:
        bootstrap_cp_integrity(force_reauth=False)
    except Exception as e:
        logger.error(f"Identity bootstrap failed: {e}")
        logger.critical("Cannot continue without identity")
        return

    # Authenticate the engine connection
    for attempt in range(5):
        auth = ping_engine("AUTH")
        if auth and auth.get("status") == "AUTH_SUCCESS":
            logger.info(f"Engine AUTH success on attempt {attempt+1}")
            break
        else:
            logger.warning("Engine AUTH failed, retrying")
            time.sleep(1)
    else:
        logger.error("Engine AUTH failed after 5 attempts, continuing without link")

    # Infinitelly check the status each PING_INTERVAL seconds
    threading.Thread(target=handle_engine, daemon=True).start()

    port = int(os.getenv("MONITOR_PORT", 9000))
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()

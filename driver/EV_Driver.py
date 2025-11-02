## Driver de prueba igual que dummy_central, es una solución temporal àra verificar funcionamiento de kafka y CPs

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
import os
import random
import threading
import time
import uuid

from flask import Flask, render_template_string, jsonify

alias_list = [
    'Julio César',
    'Alejandro Magno',
    'Ada Lovelace',
    'Alan Turing',
    'Juana de Arco',
    'Leonardo da Vinci',
    'Isaac Newton',
    'Marie Curie',
    'Nikola Tesla',
    'Albert Einstein',
    'Galileo Galilei',
    'Hipatia de Alejandría',
    'Sofía Kovalevskaya',
    'Charles Babbage',
    'Grace Hopper',
    'Carl Gauss',
    'Arquímedes de Siracusa',
    'Niels Bohr',
    'Rosalind Franklin',
    'Lise Meitner',
    'Claude Shannon',
    'Gregor Mendel',
    'Johannes Kepler',
    'Carl Sagan',
    'Stephen Hawking'
]


BROKER = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
INFO_FILE = "driver_info.json"
STATE_FILE = "driver_state.json"

available_cps = []

driver_info = {}
driver_state = {"status": "IDLE", "current_cp": None, "last_ticket": None}

def load_or_register_driver(producer):
    if os.path.exists(INFO_FILE):
        with open(INFO_FILE, "r") as f:
            info = json.load(f)
            print(f"[Driver] DRIVER existente: {info['alias']} (ID={info['id']})")
            return info
        
    driver_id = str(uuid.uuid4())[:8]
    random.seed(driver_id)
    alias = random.choice(alias_list)

    
    driver_info = {"alias": alias, "id": driver_id}
    with open(INFO_FILE, "w") as f:
        json.dump(driver_info, f)
    
    print(f"[Driver] Creado como: {alias} (ID={driver_id})")
    # msg = {"action": "REGISTER", "alias": alias, "id": driver_id}
    # producer.send("Driver.Commands", msg)
    # producer.flush()
    # print(f"[Driver] Enviando registro a la central...")

    return driver_info


# def wait_for_registration_response(consumer):
#     for msg in consumer:
#         data = msg.value
#         if data.get("action") == "REGISTER":
#             driver_id = data.get("id")
#             print(f"[Driver] Registrado con ID: {driver_id}")
# 
#             with open(INFO_FILE, "w") as f:
#                 json.dump({"alias": data["alias"], "id": driver_id}, f)
#             return driver_id

def safe_send(producer, topic, message):
    try:
        producer.send(topic, message)
        producer.flush()
    except KafkaError as e:
        driver_state["status"] = "ERROR: Central no disponible"
        print(f"[Driver] Error enviando Kafka: {e}")

def save_driver_state():
    with open(STATE_FILE, "w") as f:
        json.dump(driver_state, f)

def load_driver_state():
    global driver_state
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            driver_state = json.load(f)

def request_charge(producer, driver_info, cp_id=None):
    msg = {
        "action": "CONNECTCP",
        "driver_id": driver_info["id"],
        "cp_id": cp_id,
        "charge": round(random.uniform(3, 12), 2)
    }

    safe_send(producer, "Driver.Commands", msg)
    driver_state["status"] = f"Requested charge at {msg['cp_id']}"
    print(f"[Driver] Solicitando carga en: {msg['cp_id']}")

def disconnect_vehicle(producer, driver_info, cp_id):
    if not driver_state["current_cp"]:
        return
    msg = {
        "action": "DISCONNECT",
        "driver_id": driver_info["id"],
        "cp_id": cp_id
    }
    safe_send(producer, "Driver.Commands", msg)
    driver_state["status"] = f"Disconnected from {driver_state['current_cp']}"
    driver_state["current_cp"] = None
    save_driver_state()
    print(f"[Driver] Desconexión forzosa para CP:{cp_id}")

def listen_to_central(producer, consumer, stop_event, driver_info):
    for msg in consumer:
        if stop_event.is_set():
            break

        data = msg.value
        action = data.get("action")

        if action == "CONNECT_CP_RESPONSE":
            if data.get("isValidated"):
                cp_id = data.get("cp_id")
                driver_state["current_cp"] = cp_id
                driver_state["status"] = f"Conectado a CP {cp_id}"
                save_driver_state()
                print(f"[Driver] Conexión validada con {cp_id}")
            else:
                driver_state["status"] = "Conexión denegada"
                print(f"[Driver] Conexión denegada")
        elif action == "TICKET":
            driver_state["last_ticket"] = data
            driver_state["status"] = "Carga completada"
            save_driver_state()
            print(f"[Driver] Ticket recibido desde CP:{data.get('cp_id')} | Coste {data.get('price')}€")
        elif action == "READALL_RESPONSE":
            global available_cps
            available_cps = data.get("cps", [])
            if not available_cps:
                print(f"[Driver] No hay CPs activos")
                return
            
            print(f"[Driver] Lista de puntos disponibles ({len(available_cps)}):")
            for cp in available_cps:
                cp_id = cp.get("ID_UUID")
                cp_alias = cp.get("Ubicacion")
                cp_location = cp.get("UbicacionLarga")
                cp_precio = cp.get("Precio_KWH")
                cp_state = cp.get("Estado")
                print(f"ID: {cp_id} | Estado: {cp_state} | Precio: {cp_precio} €/kWh | Ubicación: {cp_location} | Alias: {cp_alias}")
        elif action == "DISCONNECT":
            disconnect_vehicle(producer, driver_info, data.get("cp_id"))
        elif action == "CONNECTION_LOGS":
            print(f"[Driver] LOG: {data.get('logs')}")

app = Flask(__name__)

HTML_TEMPLATE = HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>EV Driver Interface</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        button { margin: 0.5em; padding: 1em; border-radius: 8px; border: none; cursor: pointer; }
        .info { margin-top: 1em; padding: 1em; border: 1px solid #ccc; border-radius: 8px; white-space: pre-line; }
        .driver-info { background: #f0f0f0; padding: 1em; border-radius: 8px; }
    </style>
</head>
<body>
    <h2>EV Charging Driver</h2>
    <div class="driver-info" id="driverInfo">Cargando información del conductor...</div>

    <button onclick="requestCharge()">Solicitar carga aleatoria</button>
    <button onclick="disconnect()">Desconectar</button>
    
    <div class="info" id="status">Cargando estado...</div>

    document.getElementById('status').innerText =
    "Estado: " + data.status +
    (data.current_cp ? "\\nCP: " + data.current_cp : "") +
    (data.last_ticket ? "\\nTicket: " + JSON.stringify(data.last_ticket) : "") +
    (data.available_cps?.length ? "\\n\\nPuntos activos:\\n" +
        data.available_cps.map(c => ` - ${c.ID_UUID} (${c.state})`).join("\\n") : "");

    <script>
    async function updateStatus(){
        const res = await fetch('/status');
        const data = await res.json();
        document.getElementById('driverInfo').innerText = 
            "Alias: " + data.alias + "\\nUUID: " + data.driver_id;
        document.getElementById('status').innerText = 
            "Estado: " + data.status + 
            (data.current_cp ? "\\nCP: " + data.current_cp : "") +
            (data.last_ticket ? "\\nTicket: " + JSON.stringify(data.last_ticket) : "");
    }

    async function requestCharge(){
        await fetch('/charge', {method: 'POST'});
        updateStatus();
    }

    async function disconnect(){
        await fetch('/disconnect', {method: 'POST'});
        updateStatus();
    }

    setInterval(updateStatus, 2000);
    updateStatus();
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/charge", methods=["POST"])
def api_charge():
    request_charge(app.producer, driver_info)
    return jsonify({"ok": True})

@app.route("/disconnect", methods=["POST"])
def api_disconnect():
    disconnect_vehicle(app.producer, driver_info, driver_state["current_cp"])
    return jsonify({"ok": True})

@app.route("/status")
def api_status():
    return jsonify({
        "status": driver_state["status"],
        "current_cp": driver_state["current_cp"],
        "last_ticket": driver_state["last_ticket"],
        "driver_id": driver_info.get("id"),
        "alias": driver_info.get("alias"),
        "available_cps": available_cps
    })

def wait_for_kafka(broker, retries = 15, delay = 3):
    for attempt in range (1, retries+1):
        try:
            test_producer = KafkaProducer(
                bootstrap_servers=broker,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            return True
        except Exception as e:
            time.sleep(delay)
    exit(1)

def main():
    global driver_info
    load_driver_state()

    wait_for_kafka(BROKER)

    app.producer = KafkaProducer(
        bootstrap_servers=BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    consumer = KafkaConsumer(
        "Central.Driver.Commands",
        bootstrap_servers=BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        group_id="driver"
    )

    driver_info = load_or_register_driver(app.producer)
    print(f"[Driver] App ready for use || ID:{driver_info['id']} Alias:{driver_info['alias']}")

    stop_event = threading.Event()
    threading.Thread(target=listen_to_central, args=(app.producer, consumer, stop_event, driver_info), daemon=True).start()

    PORT = int(os.getenv("FLASK_PORT", "5000"))
    print(f"[Driver] Interfaz disponible en http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)


if __name__ == "__main__":
    main()
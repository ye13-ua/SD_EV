## Driver de prueba igual que dummy_central, es una solución temporal àra verificar funcionamiento de kafka y CPs

from kafka import KafkaProducer, KafkaConsumer
import json
import os
import random
import threading
import time

from flask import Flask, render_template_string, jsonify

BROKER = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
INFO_FILE = "driver_info.json"

driver_info = {}
driver_state = {"status": "IDLE", "current_cp": None, "last_ticket": None}

def load_or_register_driver(producer):
    if os.path.exists(INFO_FILE):
        with open(INFO_FILE, "r") as f:
            info = json.load(f)
            print(f"[Driver] DRIVER existente: {info['alias']} (ID={info['id']})")
            return info
        
    alias = random.choice(['Julio César','Alejando Magno','Ada Lovelace','Alan Turing','Juana De Arco'])
    print(f"[Driver] Registrando a: {alias}")
    msg = {"action": "REGISTER", "alias": alias}
    producer.send("Driver.Commands, msg")
    producer.flush()
    print(f"[Driver] Enviando registro al central...")
    return {"alias": alias, "id": None}

def wait_for_registration_response(consumer):
    for msg in consumer:
        data = msg.value
        if data.get("action") == "REGISTER":
            driver_id = data.get("id")
            print(f"[Driver] Registrado con ID: {driver_id}")

            with open(INFO_FILE, "w") as f:
                json.dump({"alias": data["alias"], "id": driver_id}, f)
            return driver_id

def request_charge(producer, driver_info, cp_id=None):
    msg = {
        "action": "CONNECTCP",
        "driver_id": driver_info["id"],
        "cp_id": cp_id,
        "charge": round(random.uniform(3, 12), 2)
    }

    producer.send("Driver.Commands", msg)
    producer.flush()
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
    producer.send("Driver.Commands", msg)
    producer.flush()
    driver_state["status"] = f"Disconnected from {driver_state['current_cp']}"
    driver_state["current_cp"] = None
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
                print(f"[Driver] Conexión validada con {cp_id}")
            else:
                driver_state["status"] = "Conexión denegada"
                print(f"[Driver] Conexión denegada")
        elif action == "TICKET":
            driver_state["last_ticket"] = data
            driver_state["status"] = "Carga completada"
            print(f"[Driver] Ticket recibido desde CP:{data.get('cp_id')} | Coste {data.get('price')}€")
        elif action == "READALL_RESPONSE":
            # TODO REVIEW THIS PART JUST IN CASE
            cps = data.get("cps", [])
            print("[Driver] Lista de puntos disponibles:")
            for cp in cps:
                print(f"    - {cp['cp_id']}")
        elif action == "DISCONNECT":
            disconnect_vehicle(producer, driver_info, data.get("cp_id"))
        elif action == "CONNECTION_LOGS":
            print(f"[Driver] LOG: {data.get('logs')}")

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>EV Driver Interface</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        button { margin: 0.5em; padding: 1em; border-radius: 8px; border: none; cursor: pointer; }
        .info { margin-top: 1em; padding: 1em; border: 1px solid #ccc; border-radius: 8px; }
    </style>
</head>
<body>
    <h2>EV Charging Driver</h2>
    <button onclick="requestCharge()">Solicitar carga aleatoria</button>
    <button onclick="disconnect()">Desconectar</button>
    <div class="info" id="status">Cargando estado...</div>

    <script>
    async function updateStatus(){
        const res = await fetch('/status');
        const data = await res.json();
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
    request_charge(app.producer)
    return jsonify({"ok": True})

@app.route("/disconnect", methods=["POST"])
def api_disconnect():
    disconnect_vehicle(app.producer)
    return jsonify({"ok": True})

@app.route("/status")
def api_status():
    return jsonify(driver_state)

def main():
    global driver_info

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
    if not driver_info.get("id"):
        driver_info["id"] = wait_for_registration_response(consumer)

    PORT = int(os.getenv("FLASK_PORT", "5000"))
    print(f"[Driver] Interfaz disponible en http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)

    print(f"[Driver] App ready for use || ID:{driver_info['id']} Alias:{driver_info['alias']}")

    stop_event = threading.Event()
    threading.Thread(target=listen_to_central, args=(app.producer, consumer, stop_event, driver_info), daemon=True).start()


if __name__ == "__main__":
    main()
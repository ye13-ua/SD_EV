## Driver de prueba igual que dummy_central, es una solución temporal àra verificar funcionamiento de kafka y CPs

# TODO implemented patch which would impede ALL the drivers to comply to only one's charging petition
# The patch is awfull but works, should rewrite grouping in kafka. Fix: lines 148-152

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
import os
import random
import threading
import time
import uuid

from flask import Flask, render_template_string, jsonify, request

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

def request_readall(producer):
    msg = {
        "action": "READALL",
        "driver_id": driver_info["id"]
    }
    safe_send(producer, "Driver.Commands", msg)
    print(f"[Driver] Solicitando listado de CPs disponibles...")

def listen_to_central(producer, consumer, stop_event, driver_info):
    global available_cps
    for msg in consumer:
        if stop_event.is_set():
            break

        data = msg
    
        if data.get("driver_id") and data["driver_id"] != driver_info["id"]:
            continue

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
            available_cps = data.get("cps", [])
            if not available_cps:
                print(f"[Driver] No hay CPs activos")
                return
            
            print(f"[Driver] Lista de puntos disponibles ({len(available_cps)}):")
            for cp in available_cps:
                cp_id = cp.get("id")
                ciudad = cp.get("ciudad", "N/A")
                calle = cp.get("calle", "N/A")
                cp_precio = cp.get("precio_kwh")
                cp_state = cp.get("estado", "UNKNOWN")

                ubicacion_larga = f"{calle}, {ciudad}"
                print(
                    f"ID: {cp_id} | Estado: {cp_state} | "
                    f"Precio: {cp_precio} €/kWh | "
                    f"Ubicación: {ubicacion_larga}"
                )
        elif action == "DISCONNECT":
            disconnect_vehicle(producer, driver_info, data.get("cp_id"))
        elif action == "CONNECTION_LOGS":
            print(f"[Driver] LOG: {data.get('logs')}")

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Driver {{ alias }}</title>
  <meta http-equiv="refresh" content="2">
  <style>
    body { font-family: Segoe UI, sans-serif; margin: 40px; background: #f8f9fa; }
    .card { background: white; border-radius: 10px; padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1); width: 450px; }
    button { margin: 5px; padding: 10px 15px; border-radius: 5px;
             border: none; cursor: pointer; }
    h2 { margin-top: 0; }
    pre { background: #eee; padding: 10px; border-radius: 5px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Driver {{ alias }}</h2>
    <p><b>UUID:</b> {{ uuid }}</p>
    <hr>
    <p><b>Estado:</b> {{ status }}</p>
    {% if current_cp %}
      <p><b>CP Actual:</b> {{ current_cp }}</p>
    {% endif %}
    {% if ticket %}
      <p><b>Último Ticket:</b></p>
      <pre>{{ ticket | tojson(indent=2) }}</pre>
    {% endif %}
    {% if cps %}
      <hr>
      <b>CPs activos:</b><br>
      {% for cp in cps %}
        - {{ cp['id'] }} |
          {{ cp['calle'] }}, {{ cp['ciudad'] }} |
          {{ cp['precio_kwh'] }} €/kWh
      {% endfor %}
    {% endif %}
    <hr>
    <b>Solicitar carga:</b><br>
    <button style="background:#007bff;color:white; margin-top:5px;" 
            onclick="fetch('/charge',{method:'POST'}).then(()=>location.reload())">
    Solicitar carga aleatoria
    </button>
    <b>Solicitar carga manual:</b><br>
    <input id="uuidBox" type="text" placeholder="Pega UUID del CP..." 
        style="width:100%; padding:8px; border-radius:5px; border:1px solid #ccc; margin-top:5px;">
    <button style="background:#007bff;color:white; margin-top:5px;" 
            onclick="sendCharge()">Solicitar carga en UUID</button>
    <hr>
    <button style="background:#28a745;color:white;" onclick="fetch('/readall',{method:'POST'}).then(()=>location.reload())">
    Actualizar CPs
    </button>
    <button style="background:#dc3545;color:white;" onclick="fetch('/disconnect',{method:'POST'}).then(()=>location.reload())">
    Desconectar
    </button>

    <script>
    function sendCharge() {
    const cpId = document.getElementById('uuidBox').value.trim();
    if (!cpId) {
        alert("Introduce una UUID válida.");
        return;
    }
    fetch('/charge', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ cp_id: cpId })
    }).then(()=>location.reload());
    }
</script>
  </div>
</body>
</html>
"""



@app.route("/")
def index():
    # Pasa valores simples, igual que el Monitor
    return render_template_string(
        TEMPLATE,
        alias=driver_info["alias"],
        uuid=driver_info["id"],
        status=driver_state["status"],
        current_cp=driver_state["current_cp"],
        ticket=driver_state["last_ticket"],
        cps=available_cps
    )

@app.route("/charge", methods=["POST"])
def api_charge():
    data = request.get_json(force=True, silent=True) or {}
    cp_id = data.get("cp_id")
    request_charge(app.producer, driver_info, cp_id)
    return jsonify({"ok": True, "cp_id": cp_id})

@app.route("/disconnect", methods=["POST"])
def api_disconnect():
    disconnect_vehicle(app.producer, driver_info, driver_state["current_cp"])
    return jsonify({"ok": True})

@app.route("/readall", methods=["POST"])
def api_readall():
    request_readall(app.producer)
    return jsonify({"ok": True})

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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

    driver_info = load_or_register_driver(app.producer)

    consumer = KafkaConsumer(
        "Central.Driver.Commands",
        bootstrap_servers=BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        group_id=f"driver_{driver_info['id']}"
    )

    print(f"[Driver] App ready for use || ID:{driver_info['id']} Alias:{driver_info['alias']}")

    request_readall(app.producer)

    stop_event = threading.Event()
    threading.Thread(target=listen_to_central, args=(app.producer, consumer, stop_event, driver_info), daemon=True).start()

    PORT = int(os.getenv("FLASK_PORT", "5000"))
    print(f"[Driver] Interfaz disponible en http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
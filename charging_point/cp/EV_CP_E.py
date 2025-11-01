##### EV_CP_Engine ##############################################################################################
# ENV definitions:                                                                                              #
# Default Kafka Broker -> kafka:9092 || "kafka" in "kafka:9092" being the docker container running kafka server #
# Default Engine port -> 7000        || ie. each monitor connects to it's respective engine via "7000"          #
# Docker network env. -> ev_net                                                                                 #
# Execution prompt -> "python EV_CP_E.py"                                                                       #
#                                                                                                               #
# env. dependencies -> kafka                                                                                    #
#################################################################################################################

# Default libs
import socket
import time
import json
import os
import threading
import random

# Traffic lights for multithread editing of the states
from threading import Lock
# Kafka
from kafka import KafkaProducer, KafkaConsumer

# Config
HOST = "0.0.0.0"
PORT = int(os.getenv("ENGINE_PORT","7000"))
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
CP_ID = None

# Estado de conexión a kafka, no tiene nada que ver con la habilidad de recibir/enviar mensajes, solo conexión
kafka_ok = True
CP_STATUS = "AUTH_PENDING"
CP_PRICE = None
CP_TARGET_CHARGE = 0.0
CP_CHARGE_PROCESS = 0.0
CP_PROCESS = None
CP_CHARGE_PRICE = None
CP_CAR_IS_CONNECTED = False
CP_DRIVER_ID = None
CP_DRIVER_ALIAS = None

PENDING_LOCAL_REQ = False
LOCAL_REQ = {
    "driver_id": CP_DRIVER_ID,
    "target_kwh": CP_TARGET_CHARGE
}

state_lock = Lock()

# Respond to ping from monitor
def handle_monitor(conn):
    global kafka_ok, CP_ID, CP_STATUS, CP_PRICE, CP_DRIVER_ID
    try:
        data = conn.recv(1024)
        if not data:
            return
        msg = json.loads(data.decode())
        action = msg.get("action")

        if action == "PING":
            response = {"status": CP_STATUS, "kafka_ok": kafka_ok, "car_connected": CP_CAR_IS_CONNECTED}
            
            if CP_STATUS == "CHARGING_CENTRAL":
                response.update({
                "target_kwh": CP_TARGET_CHARGE,
                "price_kwh": CP_PRICE,
                "current_cost": CP_CHARGE_PRICE,
                "charging_process": CP_CHARGE_PROCESS,
                "driver_id": CP_DRIVER_ID
            })
            
            if PENDING_LOCAL_REQ and CP_STATUS == "WAITING":
                response.update({
                    "local_request": {
                        "cp_id": CP_ID,
                        "driver_id": LOCAL_REQ["driver_id"],
                        "target_kwh": LOCAL_REQ["target_kwh"]
                    }
                })
            
            conn.sendall(json.dumps(response).encode())
            #if CP_ID:
            #    publish_status("ACTIVE")
        elif action == "AUTH":
            if CP_ID is None and "cp_id" in msg:
                CP_ID = msg["cp_id"]
                CP_PRICE = msg["cp_price"]
                CP_STATUS = "AUTH_SUCCESS"
                print (f"[Engine] Linked to CP_ID {CP_ID}")
            response = {"status": CP_STATUS, "kafka_ok":kafka_ok}
            conn.sendall(json.dumps(response).encode())
            CP_STATUS = "ACTIVE"

    except Exception as e:
        print(f"[Engine] Error handling monitor: {e}")
    finally:
        conn.close()

# Listens for kafka topic commands
def listen_central_commands():
    global kafka_ok
    # Attempting to connect to cafca and retrieve topic relevant data
    try:
        # Consumer definition
        consumer = KafkaConsumer(
            "Central.CP.Commands",
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="cp_engines"
        )
        kafka_ok = True
        print(f"[Engine] Listening for commands from CENTRAL via Kafka...")
        # For each message we retrieve we process it accordingly
        for message in consumer:
            # Retrieve the targer value
            cmd = message.value
            target = cmd.get("target")
            # If we are a/the target we react accordingly
            if target in [CP_ID, "ALL"]:
                print(f"[Engine] Received command from Central: {cmd}")
                handle_central_command(cmd)
    except Exception as e:
        print(f"[Engine] Kafka-Central consumer error: {e}")

# Handles command recieved via kafka from the central
def handle_central_command(cmd):
    global PENDING_LOCAL_REQ, CP_STATUS, CP_DRIVER_ID, CP_CAR_IS_CONNECTED, CP_TARGET_CHARGE, CP_PRICE
    action = cmd.get("action", "").upper()
    if action == "STOP":
        with state_lock:
            if CP_STATUS == "CHARGING_CENTRAL":
                save_current_session()
            if CP_STATUS == "WAITING":
                PENDING_LOCAL_REQ = False
            CP_STATUS = "OUT_OF_SERVICE"
        return
    elif action == "START":
        CP_STATUS = "ACTIVE"
        recover_previous_session()
    elif action == "CHARGE":
        with state_lock:
            PENDING_LOCAL_REQ = False

            CP_CAR_IS_CONNECTED = True
            CP_DRIVER_ID = cmd.get("driver_id").upper()
            CP_TARGET_CHARGE = cmd.get("target_charge")
        simulate_app_use()
        CP_CAR_IS_CONNECTED = False
        CP_DRIVER_ID = None
    elif action == "UPDATE_PRICE":
        CP_PRICE = cmd.get("price")
    elif action == "BROKEN":
        with state_lock:
            if CP_STATUS == "CHARGING_CENTRAL":
                save_current_session()
            if CP_STATUS == "WAITING":
                PENDING_LOCAL_REQ = False
        simulate_local_fault()
        return
    elif action == "DRIVER_DISCONNECT":
        simulate_driver_disconnect()
        return
    else:
        print(f"[Engine] Unknown command action: {action}")

# stub
# Simulates breakdown or other issue
def simulate_local_fault():
    global CP_STATUS
    CP_STATUS = "BROKEN"

def simulate_driver_disconnect():
    global CP_STATUS, CP_TARGET_CHARGE, CP_CAR_IS_CONNECTED, CP_DRIVER_ID, PENDING_LOCAL_REQ, LOCAL_REQ
    
    CP_STATUS = "ACTIVE"
    CP_CAR_IS_CONNECTED = False
    
    return

# stub
# Simulates using the CP's own interface to recharge the car
def simulate_local_use():
    global CP_STATUS, CP_TARGET_CHARGE, CP_CAR_IS_CONNECTED, CP_DRIVER_ID, PENDING_LOCAL_REQ, LOCAL_REQ
    
    with state_lock:
        CP_CAR_IS_CONNECTED = True
        CP_STATUS = "WAITING"
        CP_DRIVER_ID = random.randint(1,3)
        CP_TARGET_CHARGE = round(random.uniform(3, 12), 2)
        PENDING_LOCAL_REQ = True
        LOCAL_REQ = {
            "driver_id": CP_DRIVER_ID,
            "target_kwh": CP_TARGET_CHARGE
        }


# Simulate charging petition from Centreal
def simulate_app_use():
    global CP_STATUS, CP_TARGET_CHARGE, CP_CHARGE_PRICE, CP_DRIVER_ALIAS, CP_CAR_IS_CONNECTED, CP_CHARGE_PROCESS, CP_STATUS
    if not CP_CAR_IS_CONNECTED:
        print(f"[Engine] Car not connected, petition refused")

    CP_STATUS = "CHARGING_CENTRAL"
    CP_CHARGE_PRICE = 0
    CP_CHARGE_PROCESS = 0
    while CP_CHARGE_PROCESS < CP_TARGET_CHARGE:
        if (CP_STATUS in ("OUT_OF_SERVICE", "BROKEN")):
            save_current_session()
            return
        CP_CHARGE_PROCESS += 1
        CP_CHARGE_PRICE += CP_PRICE
        time.sleep(1)
    CP_CHARGE_PRICE = 0

def save_current_session():
    session = {
        "cp_id": CP_ID,
        "driver_id": CP_DRIVER_ID,
        "driver_alias": CP_DRIVER_ALIAS,
        "status": CP_STATUS,
        "charged_kwh": CP_CHARGE_PROCESS,
        "target_kwh": CP_TARGET_CHARGE,
        "price_kwh": CP_PRICE,
        "total_cost": round(CP_CHARGE_PRICE, 3) if CP_CHARGE_PRICE else 0,
        "timestamp": time.time()
    }

    try:
        with open(f"session_{CP_ID}.json", "w") as f:
            json.dump(session, f, indent=4)
        print(f"[ENGINE] Saved session: {CP_DRIVER_ID} ({CP_CHARGE_PROCESS:.2f} kWh, {CP_CHARGE_PRICE:.2f}€)")
    except Exception as e:
        print(f"[Engine] Error while saving session: {e}")

def recover_previous_session():
    global CP_DRIVER_ID, CP_DRIVER_ALIAS, CP_CHARGE_PROCESS, CP_TARGET_CHARGE, CP_CHARGE_PRICE, CP_PRICE
    path = f"session_{CP_ID}.json"
    if not os.path.exists(path):
        return False

    try:
        with open(path, "r") as f:
            session = json.load(f)
        os.remove(path)
        CP_DRIVER_ID = session.get("driver_id")
        CP_DRIVER_ALIAS = session.get("driver_alias")
        CP_TARGET_CHARGE = session.get("target_kwh", 0)
        CP_CHARGE_PROCESS = session.get("charged_kwh", 0)
        CP_CHARGE_PRICE = session.get("total_cost", 0)
        CP_PRICE = session.get("price_kwh", CP_PRICE)
        print(f"[Engine] Recovered previous session: {CP_CHARGE_PROCESS:.1f}/{CP_TARGET_CHARGE} kWh ({CP_CHARGE_PRICE:.2f}€)")
        return True
    except Exception as e:
        print(f"[Engine] Error recovering session: {e}")
        return False
            

# Defacto main function
def start_server():
    # Initialize sockets
    recover_previous_session()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen()
    print(f"[{CP_ID}] Engine listening on port {PORT}")

    # Creating a thread to listen for central commands
    if CP_ID:
        threading.Thread(target=listen_central_commands, daemon=True).start()

    # Monitor will persistently check the status via pings after connecting via sockets
    while True:
        conn, _ = s.accept()
        # For each time we need to handle the monitor, we spawn a thread
        threading.Thread(target=handle_monitor, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    start_server()
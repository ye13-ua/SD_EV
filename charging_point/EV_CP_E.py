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

# Kafka
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    print(f"[Engine] Connected to Kafka at {KAFKA_BROKER}")
except Exception as e:
    kafka_ok = False
    print(f"[Engine] Could not connect to Kafka: {e}")

# Respond to ping from monitor
def handle_monitor(conn):
    global kafka_ok, CP_ID, CP_STATUS
    try:
        data = conn.recv(1024)
        if not data:
            return
        msg = json.loads(data.decode())
        action = msg.get("action")

        if action == "PING":
            response = {"status": CP_STATUS, "kafka_ok": kafka_ok}
            conn.sendall(json.dumps(response).encode())
            if CP_ID:
                publish_status("ACTIVE")
        elif action == "AUTH":
            if CP_ID is None and "cp_id" in msg:
                CP_ID = msg["cp_id"]
                CP_STATUS = "AUTH SUCCESS"
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
    # Attempting to connect to cafca and retrieve topic relevant data
    try:
        # Consumer definition
        consumer = KafkaConsumer(
            "central_cmd",
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="cp_engines"
        )
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
    action = cmd.get("action", "").upper()
    if action == "STOP":
        publish_status("OUT_OF_SERVICE")
    elif action == "START":
        publish_status("ACTIVE")
    else:
        print(f"[Engine] Unknown command action: {action}")

# Publishes the active status of the charging point including error traces
def publish_status(status):
    # If the kafka server/connection is faulty we abort
    if not kafka_ok:
        return
    # Status message containing the id, status and timestamp
    msg = {"cp_id": CP_ID, "status": status, "timestamp": time.time()}
    try:
        # Sending the status via kafka
        producer.send("cp_status", msg)
        producer.flush()
        print(f"[Engine] Published status: {msg}")
    except Exception as e:
        print(f"[Engine] Kafka publish error: {e}")

# stub
# Simulates breakdown or other issue
def simulate_local_fault():
    return False

# stub
# Simulates using the CP's own interface to recharge the car
def simulate_local_use():
    return False

# Defacto main function
def start_server():
    # Initialize sockets
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen()
    print(f"[{CP_ID}] Engine listening on port {PORT}")

    # Creating a thread to listen for central commands
    threading.Thread(target=listen_central_commands, daemon=True).start()

    # Monitor will persistently check the status via pings after connecting via sockets
    while True:
        conn, _ = s.accept()
        # For each time we need to handle the monitor, we spawn a thread
        threading.Thread(target=handle_monitor, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    start_server()
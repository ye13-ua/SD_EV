import socket
import time
import json
import os
import threading
# Kafka
from kafka import KafkaProducer, KafkaConsumer

# Config
HOST = "0.0.0.0"
PORT = int(os.getenv("ENGINE_PORT","7000"))
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
CP_ID = None

# stub
kafka_ok = True

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
    global kafka_ok, CP_ID
    try:
        data = conn.recv(1024)
        if not data:
            return
        msg = json.loads(data.decode())

        if msg.get("action") == "PING":
            if CP_ID is None and "cp_id" in msg:
                CP_ID = msg["cp_id"]
                print (f"[Engine] Linked to CP_ID {CP_ID}")
            response = {"pong": True, "kafka_ok": kafka_ok}
            conn.sendall(json.dumps(response).encode())

            if CP_ID:
                publish_status("ACTIVE")
    except Exception as e:
        print(f"[Engine] Error handling monitor: {e}")
    finally:
        conn.close()

def listen_central_commands():
    try:
        consumer = KafkaConsumer(
            "central_cmd",
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="cp_engines"
        )
        print(f"[Engine] Listening for commands from Central via Kafka...")
        for message in consumer:
            cmd = message.value
            target = cmd.get("target")
            if target in [CP_ID, "ALL"]:
                print(f"[Engine] Received command from Central: {cmd}")
                handle_command(cmd)
    except Exception as e:
        print(f"[Engine] Kafka consumer error: {e}")

def handle_command(cmd):
    action = cmd.get("action", "").upper()
    if action == "STOP":
        publish_status("OUT_OF_SERVICE")
    elif action == "START":
        publish_status("ACTIVE")
    else:
        print(f"[Engine] Unknown command action: {action}")

def publish_status(status):
    if not kafka_ok:
        return
    msg = {"cp_id": CP_ID, "status": status, "timestamp": time.time()}
    try:
        producer.send("cp_status", msg)
        producer.flush()
        print(f"[Engine] Published status: {msg}")
    except Exception as e:
        print(f"[Engine] Kafka publish error: {e}")

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen()
    print(f"[{CP_ID}] Engine listening on port {PORT}")

    threading.Thread(target=listen_central_commands, daemon=True).start()

    while True:
        conn, _ = s.accept()
        # For each time we need to handle the monitor, we spawn a thread
        threading.Thread(target=handle_monitor, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    start_server()
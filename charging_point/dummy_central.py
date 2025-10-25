# Dummy central for testing purpose
import socket
import json
import threading
import os
from kafka import KafkaConsumer, KafkaProducer

HOST, PORT = "0.0.0.0", 9000
BROKER = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

print(f"[Central] Starting test central on port {PORT}...")
print(f"[Central] Connecting to Kafka broker at {BROKER}...")

consumer = KafkaConsumer(
    "cp_status",
    bootstrap_servers=BROKER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    group_id="central"
)

producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def listen_cp_status():
    print("[Central] Kafka listener started...")
    for msg in consumer:
        data = msg.value
        print(f"[Central] CP {data['cp_id']} → {data['status']}")
        # Ejemplo: enviar orden si detecta un fallo
        if data["status"] == "BROKEN":
            print(f"[Central] Sending STOP command to {data['cp_id']}")
            producer.send("central_cmd", {"target": data["cp_id"], "action": "STOP"})
            producer.flush()

threading.Thread(target=listen_cp_status, daemon=True).start()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
print("[Central] Socket listener ready...")

while True:
    conn, _ = s.accept()
    data = conn.recv(1024)
    print("[Central] Received via socket:", data.decode())
    conn.close()

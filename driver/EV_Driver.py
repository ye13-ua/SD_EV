## Driver de prueba igual que dummy_central, es una solución temporal àra verificar funcionamiento de kafka y CPs

from kafka import KafkaProducer, KafkaConsumer
import json
import os
import time
import threading

BROKER = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
DRIVER_ID = os.getenv("DRIVER_ID", "Driver_Test")

# Crear productor Kafka
producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Crear consumidor Kafka
consumer = KafkaConsumer(
    "driver_updates",
    bootstrap_servers=BROKER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    group_id=f"driver_{DRIVER_ID}"
)

def listen_updates():
    print(f"[{DRIVER_ID}] Listening for updates from Central...")
    for msg in consumer:
        data = msg.value
        if data.get("driver_id") == DRIVER_ID or data.get("driver_id") == "ALL":
            print(f"[{DRIVER_ID}] Update from Central: {data}")

def request_charge(cp_id):
    req = {"driver_id": DRIVER_ID, "cp_id": cp_id, "action": "REQUEST_CHARGE"}
    producer.send("driver_requests", req)
    producer.flush()
    print(f"[{DRIVER_ID}] Sent charge request for CP {cp_id}")

if __name__ == "__main__":
    print(f"[{DRIVER_ID}] Driver started. Connected to Kafka at {BROKER}")

    # Hilo de escucha de actualizaciones
    threading.Thread(target=listen_updates, daemon=True).start()

    # Simulación de solicitud cada 10 segundos
    while True:
        cp = input(f"[{DRIVER_ID}] Enter CP_ID to request charge (or ENTER to exit): ").strip()
        if not cp:
            print(f"[{DRIVER_ID}] Exiting...")
            break
        request_charge(cp)
        time.sleep(2)
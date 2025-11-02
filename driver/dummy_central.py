import threading
import time
import json
import os
from kafka import KafkaConsumer, errors
from flask import Flask

BROKER = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
FLASK_PORT = int(os.getenv("FLASK_PORT", "4000"))

app = Flask(__name__)

@app.route("/")
def index():
    return f"Dummy Central operativo en puerto {FLASK_PORT} — escuchando mensajes de Drivers en Kafka."

def kafka_listener():
    """Escucha mensajes de Drivers y los imprime."""
    print("[DummyCentral] Hilo de escucha Kafka iniciado.")
    while True:
        try:
            consumer = KafkaConsumer(
                "Driver.Commands",
                bootstrap_servers=BROKER,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                group_id="dummy_central"
            )
            print(f"[DummyCentral] Conectado a Kafka ({BROKER}), esperando mensajes...")

            for msg in consumer:
                print(f"[DummyCentral] Mensaje recibido: {msg.value}")
        except errors.NoBrokersAvailable:
            print("[DummyCentral] Kafka no disponible, reintentando en 5s...")
            time.sleep(5)
        except Exception as e:
            print(f"[DummyCentral] Error en KafkaConsumer: {e}")
            time.sleep(3)

if __name__ == "__main__":
    print(f"[DummyCentral] Iniciando servidor Flask en 0.0.0.0:{FLASK_PORT}")
    # Lanzar Kafka listener en hilo aparte
    threading.Thread(target=kafka_listener, daemon=True).start()
    # Mantener Flask vivo
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=False)

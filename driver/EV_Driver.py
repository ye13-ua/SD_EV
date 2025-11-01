## Driver de prueba igual que dummy_central, es una solución temporal àra verificar funcionamiento de kafka y CPs

from kafka import KafkaProducer, KafkaConsumer
import json
import os
import random
import time
import threading

BROKER = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
DRIVER_ID = os.getenv("DRIVER_ID", "Driver_Test")
DRIVER_ALIAS = random.choice(['Julio César','Alejando Magno','Ada Lovelace','Alan Turing','Juana De Arco'])

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
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

# Crear productor Kafka


# Crear consumidor Kafka

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
        "charge": random.uniform(3,12)
    }

    producer.send("Driver.Commands", msg)
    producer.flush()
    print(f"[Driver] Solicitando carga en: {msg['cp_id']}")

def disconnect_vehicle(producer, driver_info, cp_id):
    msg = {
        "action": "DISCONNECT",
        "driver_id": driver_info["id"],
        "cp_id": cp_id
    }
    producer.send("Driver.Commands", msg)
    producer.flush()
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
                print(f"[Driver] Conexión validada con {cp_id}")
            else:
                print(f"[Driver] Conexión denegada")
        elif action == "TICKET":
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



def main():
    producer = KafkaProducer(
        bootstrap_servers=BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    consumer = KafkaConsumer(
        "Central.Driver.Commands",
        bootstrap_servers=BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        group_id="driver"
    )

    info = load_or_register_driver(producer)

    if not info.get("id"):
        info["id"] = wait_for_registration_response(consumer)

    print(f"[Driver] App ready for use || ID:{info['id']} Alias:{info['alias']}")

    stop_event = threading.Event()



if __name__ == "__main__":
    main()
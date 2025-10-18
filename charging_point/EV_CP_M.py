import socket
import time
import json
import os
import uuid

# Config
ENGINE_HOST = os.getenv("ENGINE_HOST","localhost")
ENGINE_PORT = int(os.getenv("ENGINE_PORT","7000"))

CENTRAL_HOST = os.getenv("CENTRAL_HOST","localhost")
CENTRAL_PORT = int(os.getenv("CENTRAL_PORT","8000"))

UUID_PATH = os.getenv("UUID_PATH", os.path.join(os.getcwd(), "cp_uuid.json"))

PING_INTERVAL = 5 

def load_or_create_uuid():
    if os.path.exists(UUID_PATH):
        try:
            with open(UUID_PATH, "r") as f:
                data = json.load(f)
                if "id" in data:
                    return data["id"]
        except Exception:
            pass
    new_id = str(uuid.uuid4())
    with open(UUID_PATH, "w") as f:
        json.dump({"id": new_id}, f)
    return new_id

CP_ID = load_or_create_uuid()

# Ping engine for connection
def ping_engine():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((ENGINE_HOST, ENGINE_PORT))
            payload = {"action": "PING", "cp_id": CP_ID}
            s.sendall(json.dumps(payload).encode())
            data = s.recv(1024)
            reply = json.loads(data.decode())
            return reply
        except Exception:
            return None

def send_status_to_central(status, kafka_ok):
    msg = {"cp_id": CP_ID, "status": status, "kafka_ok": kafka_ok}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((CENTRAL_HOST, CENTRAL_PORT))
            s.sendall(json.dumps(msg).encode())
        print(f"[{CP_ID}] Sent to Central: {msg}")
    except Exception as e:
        print(f"[{CP_ID}] Could not send status to Central: {e}")

# Checks the status of the engine each 5 seconds, and reports changes to Central
def main():
    print(f"[{CP_ID}] Monitor initiated")
    # Assumption that there's one monitor for each engine (ref. UML)
    print(f"Engine: {ENGINE_HOST}:{ENGINE_PORT}")
    print(f"Central: {CENTRAL_HOST}:{CENTRAL_PORT}")

    last_report = None

    while True:
        reply = ping_engine()
        if reply:
            status = "OK"
            kafka_ok = reply.get("kafka_ok",True)
        else:
            status = "BROKEN"
            kafka_ok = False
    
        current_report = (status, kafka_ok)

        if (current_report != last_report):
            send_status_to_central(status, kafka_ok)
            last_report = current_report
        
        time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    main()

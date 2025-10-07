import socket
import time
import json
import os

# Config
ENGINE_HOST = os.getenv("ENGINE_HOST","localhost")
ENGINE_PORT = int(os.getenv("ENGINE_PORT","9100"))

CENTRAL_HOST = os.getenv("CENTRAL_HOST","localhost")
CENTRAL_PORT = int(os.getenv("CENTRAL_PORT","9000"))

CP_ID = os.getenv("CP_ID","CP1")
PING_INTERVAL = 5

# Ping engine for connection
def ping_engine():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((ENGINE_HOST, ENGINE_PORT))
            s.sendall(b"PING")
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

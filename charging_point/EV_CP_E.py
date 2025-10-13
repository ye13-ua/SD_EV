import socket
import time
import json
import os
import threading

# Config
HOST = "0.0.0.0"
PORT = int(os.getenv("ENGINE_PORT","7000"))
CP_ID = None

# stub
kafka_ok = True

# Respond to ping from monitor
def handle_monitor(conn):
    global kafka_ok, CP_ID
    try:
        data = conn.recv(1024)
        if not data:
            return
        msg = json.loads(data.decode())

        if msg.get("atcion") == "PING":
            if CP_ID is None and "cp_id" in msg:
                CP_ID = msg["cp_id"]
                print (f"[Engine] Linked to CP_ID {CP_ID}")
            response = {"pong": True, "kafka_ok": kafka_ok}
            conn.sendall(json.dumps(response.encode()))
    except Exception as e:
        print(f"[Engine] Error handling monitor: {e}")
    finally:
        conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen()
    print(f"[{CP_ID}] Engine listening on port {PORT}")

    while True:
        conn, _ = s.accept()
        # For each time we need to handle the monitor, we spawn a thread
        threading.Thread(target=handle_monitor, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    start_server()
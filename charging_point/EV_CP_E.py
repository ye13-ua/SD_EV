import socket
import time
import json
import os
import threading

# Config
HOST = "0.0.0.0"
PORT = int(os.getenv("ENGINE_PORT","9100"))
CP_ID = os.getenv("CP_ID","CP1")

# stub
kafka_ok = True

# Respond to ping from monitor
def handle_monitor(conn):
    global kafka_ok
    data = conn.recv(1024)
    if data == b"PING":
        response = {"pong": True, "kafka_ok": kafka_ok}
        conn.sendall(json.dumps(response).encode())
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
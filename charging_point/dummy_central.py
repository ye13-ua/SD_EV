# Dummy central for testing purpose
import socket

HOST, PORT = "0.0.0.0", 9000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
print("Central test listening on port 9000...")

while True:
    conn, _ = s.accept()
    data = conn.recv(1024)
    print("Received:", data.decode())
    conn.close
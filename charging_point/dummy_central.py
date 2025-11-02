from flask import Flask, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Evento de conexión
@socketio.on('connect')
def handle_connect():
    print("[DummyCentral] Nuevo cliente conectado vía Socket.IO")

@socketio.on('disconnect')
def handle_disconnect():
    print("[DummyCentral] Cliente desconectado")

# Simulación de los eventos esperados desde los CP Monitors
@socketio.on('CP_Central_Create_Socket')
def handle_register_cp(data):
    print(f"[DummyCentral] Registro de CP recibido: {data}")

@socketio.on('CP_Central_Status_Socket')
def handle_status_update(data):
    print(f"[DummyCentral] Estado recibido: {data}")

@socketio.on('CP_Central_RequestCharge_Socket')
def handle_request_charge(data):
    print(f"[DummyCentral] Solicitud de carga recibida: {data}")

@app.route('/')
def index():
    return "Dummy Central operativo — Socket.IO listo en /socket.io/"

if __name__ == "__main__":
    print("[DummyCentral] Iniciando servidor en 0.0.0.0:4000")
    socketio.run(app, host="0.0.0.0", port=4000)

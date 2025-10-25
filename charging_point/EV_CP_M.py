##### EV_CP_Engine ##############################################################################################
# ENV definitions:                                                                                              #
# Default Engine port -> 7000           || ie. each monitor connects to it's respective engine via "7000"       #
# Default Central port -> 8000                                                                                  #
# Default Engine host -> "ev_cp_engine"                                                                         # 
# Default Central host -> "ev_central"                                                                          # 
# Default local UUID path -> "/app/cp_uuid.json"                                                                #
# Default Kafka Broker -> kafka:9092    || Unused as per architecture. Could be implemented to doublecheck      #
# Docker network env. -> ev_net                                                                                 #
# Execution prompt -> "python EV_CP_M.py"                                                                       #
#                                                                                                               #
# env. dependencies -> cp_engine, central                                                                       #
#################################################################################################################

# Default libs
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

# Attempts to load the UUID from local path
# If it fails, that means it's first launch and thus will create a new UUID and send it to both:
#   central for registry and engine for communication
# It is fundamentally pointless to bother central's BD as if it's the first launch; Central inevitably won't have records on the CP
def load_or_create_uuid():
    # If a local file exists
    if os.path.exists(UUID_PATH):
        # Attempt to read
        try:
            with open(UUID_PATH, "r") as f:
                data = json.load(f)
                if "id" in data:
                    return data["id"]
        except Exception:
            pass
    # If no local source is found
    # Generate a new UUID
    new_id = str(uuid.uuid4())
    # Write down the UUID locally for future acces and send the data to 
    with open(UUID_PATH, "w") as f:
        json.dump({"id": new_id}, f)
    # !!!! MAYBE WILL BE MOVED TO ENGINE !!!! (20/10/25)
    # register_CP_in_central()
    #
    return new_id

# launches in the beggining
CP_ID = load_or_create_uuid()

# Ping engine for connection checkup
def ping_engine():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Establish timeout threshhold
        s.settimeout(1)
        # Attempt to connect and ping
        try:
            s.connect((ENGINE_HOST, ENGINE_PORT))
            payload = {"action": "PING", "cp_id": CP_ID}
            s.sendall(json.dumps(payload).encode())
            data = s.recv(1024)
            reply = json.loads(data.decode())
            return reply
        except Exception:
            return None

# Registers the CP with the Central and Central's BD
def register_CP_in_central():
    msg = {"action": "REGISTER", "cp_id": CP_ID}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((CENTRAL_HOST, CENTRAL_PORT))
            s.sendall(json.dumps(msg).encode())
        print(f"[{CP_ID}] Sent to central: {msg}")
    except Exception as e:
        print(f"[{CP_ID}] Could not register with cental")

# Sends, on change, the status of the charging point
def send_status_to_central(status, kafka_ok):
    msg = {"action": "REPORT", "cp_id": CP_ID, "status": status, "kafka_ok": kafka_ok}
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

    # By default there was no report yet
    last_report = None
    
    # Infinitelly check the status each PING_INTERVAL seconds
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

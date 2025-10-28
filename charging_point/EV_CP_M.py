##### EV_CP_Engine ##############################################################################################
# ENV definitions:                                                                                              #
# Default Engine port -> 7000                                                                                   #
# Default Central port -> 8000                                                                                  #
# Default Engine host -> "ev_cp_engine"                                                                         # 
# Default Central host -> "ev_central"                                                                          # 
# Default local UUID path -> "/app/cp_uuid.json"                                                                #
# Default Kafka Broker -> kafka:9092                                                                            #
# Docker network env. -> ev_net                                                                                 #
# Execution prompt -> "python EV_CP_M.py"                                                                       #
#                                                                                                               #
# env. dependencies -> cp_engine, central                                                                       #
#                                                                                                               #
# Communication:                                                                                                #                                            
#   Register:                                                                                                   #                                        
#       action: "REGISTER"                                                                                      #                                                    
#       cp_id: CP ID                                                                                            #                                                
#       alias: Alias                                                                                            #                                                
#       location: Location                                                                                      #                                                    
#       price:  Defaul price                                                                                    #                                                        
#                                                                                                               #
#   Engine ping:                                                                                                #
#       action: "PING"                                                                                          #
#       cp_id: CP ID                                                                                            #
#                                                                                                               #
#   Report to Central:                                                                                          #
#       action: "REPORT"                                                                                        #
#       cp_id: CP ID                                                                                            #
#       status: Engine Status                                                                                   #
#       kafka_ok: Kafka status                                                                                  #
#       timestamp: timestamp                                                                                    #
#################################################################################################################

# Default libs
import socket
import time
import json
import os
import uuid
import random

# Config
ENGINE_HOST = os.getenv("ENGINE_HOST","localhost")
ENGINE_PORT = int(os.getenv("ENGINE_PORT","7000"))

CENTRAL_HOST = os.getenv("CENTRAL_HOST","localhost")
CENTRAL_PORT = int(os.getenv("CENTRAL_PORT","8000"))

UUID_PATH = os.getenv("UUID_PATH", os.path.join(os.getcwd(), "cp_uuid.json"))

PING_INTERVAL = 2


def generate_alias(uuid_str):
    prefix = uuid_str.split('-')[0].upper()  # primeros 8 chars del UUID
    return f"CP-{prefix}"

# Attempts to load the UUID from local path
# If it fails, that means it's first launch and thus will create a new UUID and send it to both:
#   central for registry and engine for communication
# It is fundamentally pointless to bother central's BD as if it's the first launch; Central inevitably won't have records on the CP
def load_or_create_cp_data():
    # If a local file exists
    if os.path.exists(UUID_PATH):
        # Attempt to read
        try:
            with open(UUID_PATH, "r") as f:
                data = json.load(f)
                if "id" in data and "location" in data:
                    return data
        except Exception:
            pass
    # If no local source is found
    # Generate a new UUID
    new_id = str(uuid.uuid4())
    location = f"Calle {random.choice(['Sol','Luna','Mar','Paz','Río'])}, Alicante"
    alias = generate_alias(new_id)
    data = {"id": new_id, "alias":alias, "location":location}
    # Write down the UUID locally for future acces and send the data to 
    with open(UUID_PATH, "w") as f:
        json.dump(data, f)
    return data

# Launches in the beggining
CP_DATA = load_or_create_cp_data()
CP_ID = CP_DATA["id"]
CP_ALIAS = CP_DATA["alias"]
CP_LOCATION = CP_DATA["location"]

# Default price generated in range from 0.10 to 0.45 with only 3 decimals
CP_DEFAULT_PRICE = round(random.uniform(0.10, 0.45), 3)

# Ping engine for connection checkup
def ping_engine(action):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Establish timeout threshhold
        s.settimeout(0.75)
        # Attempt to connect and ping
        try:
            s.connect((ENGINE_HOST, ENGINE_PORT))
            payload = {"action": action, "cp_id": CP_ID}
            s.sendall(json.dumps(payload).encode())
            data = s.recv(1024)
            reply = json.loads(data.decode())
            return reply
        except Exception:
            return None
        
# Handler of infinite pings
def handle_engine():
    # By default there was no report yet
    last_report = None
    
    while True:
        reply = ping_engine("PING")
        if not reply:
            status = "NO CONNECTION"
            kafka_ok = False
        else:
            status = reply.get("status")
            kafka_ok = reply.get("kafka_ok",True)
    
        current_report = (status, kafka_ok)

        if (current_report != last_report):
            send_status_to_central(status, kafka_ok)
            last_report = current_report
        
        time.sleep(PING_INTERVAL)

# Registers the CP with the Central and Central's BD
def register_CP_in_central():
    msg = {"action": "REGISTER",
           "cp_id": CP_ID,
           "alias": CP_ALIAS,
           "location": CP_LOCATION,
           "price": CP_DEFAULT_PRICE}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((CENTRAL_HOST, CENTRAL_PORT))
            s.sendall(json.dumps(msg).encode())
        print(f"[{CP_ALIAS}] Sent to central: {msg}")
    except Exception as e:
        print(f"[{CP_ALIAS}] Could not register with cental")

# Sends, on change, the status of the charging point
def send_status_to_central(status, kafka_ok):
    msg = {"action": "REPORT", "cp_id": CP_ID, "status": status, "kafka_ok": kafka_ok, "timestamp": time.time()}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((CENTRAL_HOST, CENTRAL_PORT))
            s.sendall(json.dumps(msg).encode())
        print(f"[{CP_ALIAS}] Sent to Central: {msg}")
    except Exception as e:
        print(f"[{CP_ALIAS}] Could not send status to Central: {e}")

# Checks the status of the engine each 5 seconds, and reports changes to Central
def main():
    print(f"[{CP_ALIAS}] Monitor initiated")
    # Assumption that there's one monitor for each engine (ref. UML)
    print(f"    Engine: {ENGINE_HOST}:{ENGINE_PORT}")
    print(f"    Central: {CENTRAL_HOST}:{CENTRAL_PORT}")
    
    # Authenticate the engine connection
    auth = ping_engine("AUTH")
    if not auth or auth.get("status")!="AUTH SUCCESS":
        print(f"[{CP_ALIAS}] Engine AUTH failed or unreachable")
    else:
        register_CP_in_central()

    # Infinitelly check the status each PING_INTERVAL seconds
    handle_engine()

if __name__ == "__main__":
    main()

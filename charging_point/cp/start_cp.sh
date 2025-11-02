#!/bin/bash
echo "[CP_PAIR] Starting Engine + Monitor pair..."
echo "ENGINE_PORT=$ENGINE_PORT | MONITOR_PORT=$MONITOR_PORT"

# Lanzar el Engine
python /app/EV_CP_E.py &
ENGINE_PID=$!

# Esperar un poco a que el Engine arranque
sleep 1.5

# Lanzar el Monitor (mantiene el contenedor activo)
python /app/EV_CP_M.py &

# Mantener el contenedor vivo (control de señales)
wait -n $ENGINE_PID
wait

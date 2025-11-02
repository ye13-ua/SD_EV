#!/bin/bash
# Uso:
#   ./scale.sh <num_cp> <num_driver>

CP_COUNT=${1:-3}
DRIVER_COUNT=${2:-1}

echo "Scaling containers..."

docker compose -f docker-compose.yml up -d \
  --scale cp_pair=$CP_COUNT \
  --scale driver=$DRIVER_COUNT
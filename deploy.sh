#!/bin/bash
# Uso:
#   ./deploy.sh <num_cp> <num_driver>

CP_COUNT=${1:-3}
DRIVER_COUNT=${2:-1}

echo "Deploying docker with #CP_COUNT CPs and $DRIVER_COUNT Drivers..."

docker compose -f docker-compose.yml up -d --build \
  --scale cp_pair=$CP_COUNT \
  --scale driver=$DRIVER_COUNT
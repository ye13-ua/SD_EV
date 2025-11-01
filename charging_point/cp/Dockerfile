FROM python:3.11-slim

WORKDIR /app
COPY EV_CP_E.py EV_CP_M.py /app/
RUN pip install kafka-python flask python-socketio

# Variables base
ENV KAFKA_BROKER=kafka:9092
ENV CENTRAL_HOST=http://central:8000
ENV ENGINE_PORT=7000
ENV ENGINE_HOST=localhost
ENV MONITOR_PORT=9000
ENV CP_INDEX=0

COPY start_cp.sh /app/start_cp.sh
RUN chmod +x /app/start_cp.sh

CMD ["bash", "start_cp.sh"]

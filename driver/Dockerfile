FROM python:3.11-slim

WORKDIR /app

COPY EV_Driver.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV KAFKA_BOOTSTRAP=kafka:9092
ENV FLASK_PORT=5000

CMD ["python", "EV_Driver.py"]
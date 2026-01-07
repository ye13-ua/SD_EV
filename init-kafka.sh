#!/bin/bash
# Script para crear los topics de Kafka necesarios

echo "Esperando a que Kafka esté listo..."
sleep 10

echo "Creando topics de Kafka..."

kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic Driver.Commands --partitions 1 --replication-factor 1
kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic Central.Driver.Commands --partitions 1 --replication-factor 1
kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic Central.CP.Commands --partitions 1 --replication-factor 1

echo "Topics creados exitosamente"
kafka-topics --bootstrap-server kafka:9092 --list

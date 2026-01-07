#!/bin/bash
# Generar certificados para central
openssl req -x509 -newkey rsa:4096 -keyout central.key -out central.crt -days 365 -nodes -subj "/CN=ev_central/O=EV/C=ES"

echo "Certificados para central generados: central.key y central.crt"

# Script PowerShell para generar certificados para central
$certPath = $PSScriptRoot

# Generar certificados para central usando OpenSSL
& openssl req -x509 -newkey rsa:4096 -keyout "$certPath\central.key" -out "$certPath\central.crt" -days 365 -nodes -subj "/CN=ev_central/O=EV/C=ES"

Write-Host "Certificados para central generados: central.key y central.crt"

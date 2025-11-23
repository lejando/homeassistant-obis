#!/usr/bin/env bashio

bashio::log.info "Starte OBIS D0 Reader..."

# Konfiguration anzeigen
TCP_HOST=$(bashio::config 'tcp_host')
TCP_PORT=$(bashio::config 'tcp_port')
MQTT_ENABLED=$(bashio::config 'mqtt_enabled')
MQTT_HOST=$(bashio::config 'mqtt_host')
METER_NAME=$(bashio::config 'meter_name')

bashio::log.info "Konfiguration:"
bashio::log.info "  TCP: ${TCP_HOST}:${TCP_PORT}"
bashio::log.info "  MQTT: ${MQTT_ENABLED} (${MQTT_HOST})"
bashio::log.info "  Zähler: ${METER_NAME}"

# Starte Python-Anwendung
cd /app
exec python3 -u obis_reader.py

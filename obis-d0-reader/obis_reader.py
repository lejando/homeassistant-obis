#!/usr/bin/env python3
"""
OBIS D0 Reader für Home Assistant
Liest D0-Protokoll Stromzähler via TCP und sendet Daten an MQTT
"""

import socket
import time
import json
import sys
import logging
import re
from typing import Dict, Optional, Any
from dataclasses import dataclass
import paho.mqtt.client as mqtt

# OBIS Code Definitionen und Mapping
OBIS_CODES = {
    '1-0:0.0.0*255': {'name': 'device_id', 'unit': '', 'device_class': None, 'state_class': None},
    '1-0:96.1.0*255': {'name': 'meter_id', 'unit': '', 'device_class': None, 'state_class': None},
    '1-0:1.8.0*255': {'name': 'total_energy_import', 'unit': 'kWh', 'device_class': 'energy', 'state_class': 'total_increasing'},
    '1-0:2.8.0*255': {'name': 'total_energy_export', 'unit': 'kWh', 'device_class': 'energy', 'state_class': 'total_increasing'},
    '1-0:16.7.0*255': {'name': 'power_total', 'unit': 'W', 'device_class': 'power', 'state_class': 'measurement'},
    '1-0:36.7.0*255': {'name': 'power_l1', 'unit': 'W', 'device_class': 'power', 'state_class': 'measurement'},
    '1-0:56.7.0*255': {'name': 'power_l2', 'unit': 'W', 'device_class': 'power', 'state_class': 'measurement'},
    '1-0:76.7.0*255': {'name': 'power_l3', 'unit': 'W', 'device_class': 'power', 'state_class': 'measurement'},
    '1-0:32.7.0*255': {'name': 'voltage_l1', 'unit': 'V', 'device_class': 'voltage', 'state_class': 'measurement'},
    '1-0:52.7.0*255': {'name': 'voltage_l2', 'unit': 'V', 'device_class': 'voltage', 'state_class': 'measurement'},
    '1-0:72.7.0*255': {'name': 'voltage_l3', 'unit': 'V', 'device_class': 'voltage', 'state_class': 'measurement'},
    '1-0:31.7.0*255': {'name': 'current_l1', 'unit': 'A', 'device_class': 'current', 'state_class': 'measurement'},
    '1-0:51.7.0*255': {'name': 'current_l2', 'unit': 'A', 'device_class': 'current', 'state_class': 'measurement'},
    '1-0:71.7.0*255': {'name': 'current_l3', 'unit': 'A', 'device_class': 'current', 'state_class': 'measurement'},
    '1-0:14.7.0*255': {'name': 'frequency', 'unit': 'Hz', 'device_class': 'frequency', 'state_class': 'measurement'},
    '1-0:96.5.0*255': {'name': 'device_status', 'unit': '', 'device_class': None, 'state_class': None},
    '0-0:96.8.0*255': {'name': 'operating_time', 'unit': '', 'device_class': None, 'state_class': None},
}

@dataclass
class Config:
    """Konfiguration für den OBIS Reader"""
    tcp_host: str
    tcp_port: int
    mqtt_enabled: bool
    mqtt_host: str
    mqtt_port: int
    mqtt_user: str
    mqtt_password: str
    mqtt_base_topic: str
    mqtt_discovery: bool
    mqtt_discovery_prefix: str
    mqtt_topic_mode: str
    mqtt_custom_topics: Dict[str, str]
    meter_name: str
    poll_interval: int
    log_level: str

class OBISReader:
    """OBIS D0 Protokoll Reader"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = self._setup_logging()
        self.mqtt_client: Optional[mqtt.Client] = None
        self.connected = False
        self.last_values: Dict[str, Any] = {}

    def _setup_logging(self) -> logging.Logger:
        """Logging konfigurieren"""
        logger = logging.getLogger('obis_reader')
        level = getattr(logging, self.config.log_level.upper())
        logger.setLevel(level)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def parse_d0_message(self, data: bytes) -> Dict[str, str]:
        """Parst D0-Protokoll Nachrichten"""
        try:
            text = data.decode('ascii', errors='ignore')
            values = {}

            # D0 Format: 1-0:1.8.0*255(000012345.6789*kWh)
            pattern = r'([0-9]-[0-9]+:[0-9]+\.[0-9]+\.[0-9]+\*[0-9]+)\(([^)]+)\)'
            matches = re.findall(pattern, text)

            for code, value in matches:
                # Extrahiere numerischen Wert und Einheit
                value_match = re.match(r'([0-9.-]+)\*?(\w+)?', value)
                if value_match:
                    numeric_value = value_match.group(1)
                    unit = value_match.group(2) if value_match.group(2) else ''
                    values[code] = numeric_value
                else:
                    # Falls keine numerischer Wert (z.B. Seriennummer)
                    values[code] = value

            return values

        except Exception as e:
            self.logger.error(f"Fehler beim Parsen der D0-Nachricht: {e}")
            return {}

    def connect_tcp(self) -> Optional[socket.socket]:
        """Verbindet zu ser2net via TCP"""
        try:
            self.logger.info(f"Verbinde zu {self.config.tcp_host}:{self.config.tcp_port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.config.tcp_host, self.config.tcp_port))
            self.logger.info("TCP-Verbindung erfolgreich")
            return sock
        except Exception as e:
            self.logger.error(f"TCP-Verbindung fehlgeschlagen: {e}")
            return None

    def read_tcp_data(self, sock: socket.socket, timeout: int = 10) -> Optional[bytes]:
        """Liest Daten vom TCP-Socket"""
        try:
            data = b''
            start_time = time.time()

            while time.time() - start_time < timeout:
                sock.setblocking(0)
                try:
                    chunk = sock.recv(4096)
                    if chunk:
                        data += chunk
                        # Wenn wir eine vollständige Nachricht haben (endet meist mit !)
                        if b'!' in data or len(data) > 512:
                            return data
                except BlockingIOError:
                    pass

                time.sleep(0.1)

            return data if data else None

        except Exception as e:
            self.logger.error(f"Fehler beim Lesen vom TCP-Socket: {e}")
            return None

    def setup_mqtt(self):
        """MQTT-Client initialisieren"""
        if not self.config.mqtt_enabled:
            self.logger.info("MQTT ist deaktiviert")
            return

        try:
            self.mqtt_client = mqtt.Client()

            if self.config.mqtt_user and self.config.mqtt_password:
                self.mqtt_client.username_pw_set(
                    self.config.mqtt_user,
                    self.config.mqtt_password
                )

            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect

            self.logger.info(f"Verbinde zu MQTT Broker {self.config.mqtt_host}:{self.config.mqtt_port}...")
            self.mqtt_client.connect(self.config.mqtt_host, self.config.mqtt_port, 60)
            self.mqtt_client.loop_start()

        except Exception as e:
            self.logger.error(f"MQTT-Verbindung fehlgeschlagen: {e}")

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT Connect Callback"""
        if rc == 0:
            self.logger.info("MQTT-Verbindung erfolgreich")
            self.connected = True
            if self.config.mqtt_discovery:
                self.publish_discovery()
        else:
            self.logger.error(f"MQTT-Verbindung fehlgeschlagen mit Code {rc}")

    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT Disconnect Callback"""
        self.logger.warning("MQTT-Verbindung getrennt")
        self.connected = False

    def publish_discovery(self):
        """Publiziert Home Assistant MQTT Discovery Nachrichten"""
        if not self.config.mqtt_discovery or not self.mqtt_client:
            return

        self.logger.info("Publiziere MQTT Discovery Konfigurationen...")

        for obis_code, info in OBIS_CODES.items():
            entity_id = f"{self.config.meter_name}_{info['name']}"

            config = {
                "name": f"{self.config.meter_name} {info['name'].replace('_', ' ').title()}",
                "unique_id": f"obis_{self.config.meter_name}_{info['name']}",
                "state_topic": f"{self.config.mqtt_base_topic}/{info['name']}/state",
                "object_id": entity_id,
            }

            if info['unit']:
                config["unit_of_measurement"] = info['unit']
            if info['device_class']:
                config["device_class"] = info['device_class']
            if info['state_class']:
                config["state_class"] = info['state_class']

            # Geräte-Informationen
            config["device"] = {
                "identifiers": [f"obis_{self.config.meter_name}"],
                "name": self.config.meter_name,
                "model": "D0 Smart Meter",
                "manufacturer": "OBIS",
            }

            # Discovery Topic
            discovery_topic = f"{self.config.mqtt_discovery_prefix}/sensor/{entity_id}/config"

            # Publiziere Discovery
            self.mqtt_client.publish(
                discovery_topic,
                json.dumps(config),
                retain=True
            )
            self.logger.debug(f"Discovery publiziert für {info['name']}")

        self.logger.info("MQTT Discovery abgeschlossen")

    def get_topic_for_code(self, obis_code: str, sensor_name: str) -> str:
        """Bestimmt das MQTT-Topic für einen OBIS-Code"""
        # Custom Topics haben Vorrang
        if self.config.mqtt_topic_mode == 'custom':
            if obis_code in self.config.mqtt_custom_topics:
                return self.config.mqtt_custom_topics[obis_code]
            if sensor_name in self.config.mqtt_custom_topics:
                return self.config.mqtt_custom_topics[sensor_name]

        # Auto-Modus: Standard-Topic-Struktur
        return f"{self.config.mqtt_base_topic}/{sensor_name}/state"

    def publish_values(self, values: Dict[str, str]):
        """Publiziert Werte zu MQTT"""
        if not self.mqtt_client or not self.connected:
            return

        for obis_code, value in values.items():
            if obis_code in OBIS_CODES:
                info = OBIS_CODES[obis_code]
                sensor_name = info['name']

                # Topic bestimmen
                topic = self.get_topic_for_code(obis_code, sensor_name)

                # Wert publizieren
                self.mqtt_client.publish(topic, value, retain=True)
                self.logger.debug(f"Publiziert {sensor_name}: {value} → {topic}")

                # Speichere letzten Wert
                self.last_values[sensor_name] = value

        # Zusätzlich: Publiziere alle Werte als JSON (optional)
        json_topic = f"{self.config.mqtt_base_topic}/all"
        self.mqtt_client.publish(json_topic, json.dumps(self.last_values), retain=True)

    def run(self):
        """Hauptschleife"""
        self.logger.info("OBIS D0 Reader gestartet")

        # MQTT Setup
        self.setup_mqtt()

        # Warte auf MQTT-Verbindung
        if self.config.mqtt_enabled:
            for i in range(10):
                if self.connected:
                    break
                self.logger.info("Warte auf MQTT-Verbindung...")
                time.sleep(1)

        # Hauptschleife
        while True:
            try:
                # TCP-Verbindung aufbauen
                sock = self.connect_tcp()
                if not sock:
                    self.logger.error("Keine TCP-Verbindung, warte 10 Sekunden...")
                    time.sleep(10)
                    continue

                # Daten lesen
                data = self.read_tcp_data(sock, timeout=self.config.poll_interval + 5)
                sock.close()

                if data:
                    self.logger.debug(f"Empfangen: {len(data)} Bytes")

                    # D0-Nachricht parsen
                    values = self.parse_d0_message(data)

                    if values:
                        self.logger.info(f"Erfolgreich {len(values)} Werte geparst")

                        # Werte zu MQTT publizieren
                        if self.config.mqtt_enabled:
                            self.publish_values(values)

                        # Log einige Werte
                        if '1-0:16.7.0*255' in values:
                            self.logger.info(f"Aktuelle Leistung: {values['1-0:16.7.0*255']} W")
                    else:
                        self.logger.warning("Keine Werte in der Nachricht gefunden")
                else:
                    self.logger.warning("Keine Daten empfangen")

                # Warte bis zum nächsten Poll
                time.sleep(self.config.poll_interval)

            except KeyboardInterrupt:
                self.logger.info("Beende...")
                break
            except Exception as e:
                self.logger.error(f"Fehler in Hauptschleife: {e}", exc_info=True)
                time.sleep(10)

        # Cleanup
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

def load_config() -> Config:
    """Lädt Konfiguration aus /data/options.json (Home Assistant Add-on)"""
    try:
        with open('/data/options.json', 'r') as f:
            options = json.load(f)

        return Config(
            tcp_host=options.get('tcp_host', '192.168.1.100'),
            tcp_port=options.get('tcp_port', 3000),
            mqtt_enabled=options.get('mqtt_enabled', True),
            mqtt_host=options.get('mqtt_host', 'core-mosquitto'),
            mqtt_port=options.get('mqtt_port', 1883),
            mqtt_user=options.get('mqtt_user', ''),
            mqtt_password=options.get('mqtt_password', ''),
            mqtt_base_topic=options.get('mqtt_base_topic', 'homeassistant/sensor/obis'),
            mqtt_discovery=options.get('mqtt_discovery', True),
            mqtt_discovery_prefix=options.get('mqtt_discovery_prefix', 'homeassistant'),
            mqtt_topic_mode=options.get('mqtt_topic_mode', 'auto'),
            mqtt_custom_topics=options.get('mqtt_custom_topics', {}),
            meter_name=options.get('meter_name', 'easyMeter'),
            poll_interval=options.get('poll_interval', 2),
            log_level=options.get('log_level', 'info'),
        )
    except Exception as e:
        print(f"Fehler beim Laden der Konfiguration: {e}")
        sys.exit(1)

def main():
    """Hauptfunktion"""
    config = load_config()
    reader = OBISReader(config)
    reader.run()

if __name__ == '__main__':
    main()

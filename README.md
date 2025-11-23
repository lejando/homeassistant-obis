# Home Assistant OBIS D0 Reader Add-on

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Home Assistant Add-on zum Auslesen von OBIS D0-Stromzählern via ser2net mit MQTT-Integration.

## 🎯 Features

- ✅ **D0-Protokoll Support** - Kompatibel mit vielen deutschen Stromzählern (EasyMeter, EBZ, etc.)
- ✅ **TCP/IP Verbindung** - Funktioniert mit ser2net auf Raspberry Pi oder anderen Systemen
- ✅ **MQTT Auto-Discovery** - Sensoren erscheinen automatisch in Home Assistant
- ✅ **Konfigurierbare MQTT-Topics** - Flexibles Topic-Mapping für externe Systeme
- ✅ **Energy Dashboard Ready** - Direkte Integration in HA Energy Dashboard
- ✅ **15+ Sensoren** - Energie, Leistung, Spannung, Strom pro Phase
- ✅ **Keine Hardware-Änderungen** - Nutzt bestehende ser2net-Installation

## 📊 Unterstützte Messwerte

Das Add-on liest automatisch alle verfügbaren OBIS-Codes aus:

### Energiezähler
- Gesamtbezug (kWh)
- Gesamteinspeisung (kWh)

### Leistung
- Gesamtleistung (W)
- Leistung pro Phase L1, L2, L3 (W)

### Elektrische Parameter
- Spannung pro Phase (V)
- Strom pro Phase (A)
- Netzfrequenz (Hz)

### Geräteinformationen
- Zähler-ID / Seriennummer
- Gerätestatus
- Betriebszeit

## 🚀 Schnellstart

### 1. Installation

Fügen Sie dieses Repository zu Ihren Home Assistant Add-on Repositories hinzu:

1. **Einstellungen** → **Add-ons** → **Add-on Store**
2. Klicken Sie auf **⋮** (drei Punkte) → **Repositories**
3. Fügen Sie hinzu: `https://github.com/lejando/homeassistant-obis`
4. Suchen Sie nach **"OBIS D0 Reader"** und installieren Sie es

### 2. Konfiguration

```yaml
tcp_host: "192.168.1.100"    # IP Ihres ser2net Servers
tcp_port: 3000               # ser2net Port

mqtt_enabled: true
mqtt_host: "core-mosquitto"  # MQTT Broker
mqtt_base_topic: "homeassistant/sensor/obis"

meter_name: "easyMeter"
poll_interval: 2
```

### 3. Starten

1. Speichern Sie die Konfiguration
2. Starten Sie das Add-on
3. Prüfen Sie die Logs
4. Sensoren erscheinen automatisch unter **Geräte & Dienste** → **MQTT**

## 🔧 Voraussetzungen

### ser2net auf Raspberry Pi

Ihr Raspberry Pi mit IR-Lesekopf benötigt ser2net:

**Installation:**
```bash
sudo apt install ser2net
```

**Konfiguration** (`/etc/ser2net/ser2net.yaml`):
```yaml
connection: &easyMeter
  accepter: tcp,3000
  enable: on
  options:
    kickolduser: true
    telnet-brk-on-sync: false
  connector: serialdev,/dev/ttyUSB0,9600e71,local
```

**Neustart:**
```bash
sudo systemctl restart ser2net
```

### MQTT Broker

Installieren Sie das **Mosquitto broker** Add-on aus dem Home Assistant Add-on Store.

## 📖 Architektur

```
OBIS-Stromzähler (D0-Protokoll)
         ↓
    IR-Lesekopf
         ↓
  Raspberry Pi
  /dev/ttyUSB0
  (9600,7,E,1)
         ↓
   ser2net (Port 3000)
         ↓
   [TCP/IP-Netzwerk]
         ↓
 Home Assistant OS (VM)
   OBIS D0 Reader Add-on
         ↓
   MQTT Broker
         ↓
  Home Assistant
  - Energy Dashboard
  - 15+ Sensoren
  - Automationen
```

## 🎛️ Erweiterte Konfiguration

### Custom MQTT-Topics

Senden Sie Daten an beliebige MQTT-Topics:

```yaml
mqtt_topic_mode: "custom"
mqtt_custom_topics:
  "1-0:16.7.0*255": "energie/stromzaehler/leistung"
  "1-0:1.8.0*255": "energie/stromzaehler/verbrauch"
  "power_total": "nodered/power/current"
  "total_energy_import": "grafana/energy/import"
```

### Externe Systeme

Das Add-on kann gleichzeitig Daten an mehrere Systeme senden:

- **Home Assistant** (via Auto-Discovery)
- **Node-RED** (via custom topics)
- **Grafana** (via custom topics)
- **ioBroker** (via custom topics)

Alle Werte werden zusätzlich als JSON publiziert unter: `{mqtt_base_topic}/all`

## 📁 Repository-Struktur

```
homeassistant-obis/
├── obis-d0-reader/          # Add-on Verzeichnis
│   ├── config.yaml          # Add-on Konfiguration
│   ├── Dockerfile           # Docker Image Definition
│   ├── build.yaml           # Multi-Arch Build Config
│   ├── run.sh              # Startup Script
│   ├── obis_reader.py      # Python Hauptprogramm
│   ├── requirements.txt    # Python Dependencies
│   ├── README.md           # Add-on Dokumentation
│   └── CHANGELOG.md        # Versionshistorie
├── INSTALL.md              # Installations-Anleitung
├── LICENSE                 # MIT Lizenz
├── repository.json         # Add-on Repository Definition
└── README.md               # Dieses README
```

## 🔧 Verbindung testen

### ser2net Verbindung prüfen

Testen Sie die Verbindung zum ser2net Server:

```bash
# Von einem beliebigen Rechner im Netzwerk
telnet 192.168.1.100 3000
```

Sie sollten ASCII-Text vom Stromzähler sehen (D0-Protokoll).

### Raspberry Pi Diagnose

Prüfen Sie Ihre ser2net-Installation auf dem Raspberry Pi:

```bash
# Status prüfen
sudo systemctl status ser2net

# Port prüfen
sudo netstat -tulpn | grep 3000

# USB-Gerät prüfen
ls -la /dev/ttyUSB*

# Rohdaten testen
sudo timeout 5 cat /dev/ttyUSB0 | xxd
```

## 🐛 Fehlerbehebung

### Keine Verbindung zum ser2net

```bash
# Auf dem Raspberry Pi
sudo systemctl status ser2net
sudo netstat -tulpn | grep 3000

# Von Home Assistant aus testen (IP durch Ihre ersetzen)
telnet 192.168.1.100 3000
```

### Keine MQTT-Daten

1. Prüfen Sie die Add-on Logs
2. Prüfen Sie MQTT Integration: **Einstellungen** → **Geräte & Dienste** → **MQTT**
3. Prüfen Sie Mosquitto Logs

### Sensoren erscheinen nicht

1. Aktivieren Sie `mqtt_discovery: true`
2. Prüfen Sie Discovery Messages: **Entwicklerwerkzeuge** → **MQTT** → Lauschen auf `homeassistant/#`
3. Neustart des Add-ons

## 🤝 Beitragen

Contributions sind willkommen! Bitte:

1. Forken Sie das Repository
2. Erstellen Sie einen Feature Branch
3. Committen Sie Ihre Änderungen
4. Pushen Sie zum Branch
5. Öffnen Sie einen Pull Request

## 📝 Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei

## ✨ Danksagungen

- Home Assistant Community
- ser2net Projekt
- Paho MQTT Client
- Alle Contributors

## 📧 Support

- **Issues:** [GitHub Issues](https://github.com/lejando/homeassistant-obis/issues)
- **Discussions:** [GitHub Discussions](https://github.com/lejando/homeassistant-obis/discussions)

## 🔗 Links

- [Home Assistant](https://www.home-assistant.io/)
- [ser2net Dokumentation](https://github.com/cminyard/ser2net)
- [OBIS-Kennzahlen Wikipedia](https://de.wikipedia.org/wiki/OBIS-Kennzahlen)
- [D0-Protokoll Spezifikation](https://wiki.volkszaehler.org/software/obis)

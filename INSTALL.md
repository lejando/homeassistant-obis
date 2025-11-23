# Installationsanleitung - Schritt für Schritt

Diese Anleitung führt Sie durch die komplette Installation von der Hardware bis zur fertigen Integration in Home Assistant.

## Übersicht

```
┌─────────────────────┐
│  OBIS-Stromzähler   │
│   (D0-Protokoll)    │
└──────────┬──────────┘
           │ IR-Schnittstelle
           ▼
┌─────────────────────┐
│   IR-Lesekopf       │
│   (USB)             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Raspberry Pi       │
│  + ser2net          │
│  Port 3000          │
└──────────┬──────────┘
           │
           │ TCP/IP Netzwerk
           ▼
┌─────────────────────┐
│  Home Assistant     │
│  (VM auf Synology)  │
│  + OBIS D0 Reader   │
│  + Mosquitto MQTT   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Energy Dashboard   │
│  + 15+ Sensoren     │
└─────────────────────┘
```

## Teil 1: Hardware-Setup

### Benötigte Hardware

1. **OBIS-Stromzähler** mit D0-Schnittstelle
   - Z.B. EasyMeter, EBZ, EMH, Iskraemeco, etc.

2. **IR-Lesekopf** mit USB-Anschluss
   - Empfohlen: Hichi USB IR Lesekopf
   - Alternative: Selbstbau mit IR-LED/Photodiode

3. **Raspberry Pi** (bereits vorhanden ✓)
   - Modell: Beliebig (Pi 3, Pi 4, Pi Zero W)
   - OS: Raspberry Pi OS (ehemals Raspbian)

4. **Netzwerkverbindung**
   - LAN oder WLAN zwischen Pi und Home Assistant

### IR-Lesekopf montieren

1. Positionieren Sie den IR-Lesekopf auf der optischen Schnittstelle des Zählers
2. Die Schnittstelle ist meist mit einem Symbol markiert: 🔦
3. Befestigen Sie den Lesekopf mit Magneten oder Klebeband
4. Verbinden Sie den Lesekopf via USB mit dem Raspberry Pi

## Teil 2: Raspberry Pi einrichten

### 2.1 Raspberry Pi OS installieren (falls noch nicht geschehen)

```bash
# System aktualisieren
sudo apt update
sudo apt upgrade -y
```

### 2.2 USB-Lesekopf identifizieren

```bash
# USB-Geräte anzeigen
lsusb

# Serielle Geräte finden
ls -la /dev/ttyUSB*
# Ausgabe sollte sein: /dev/ttyUSB0

# Falls /dev/ttyACM* statt ttyUSB*
ls -la /dev/ttyACM*
```

**Notieren Sie sich das Gerät** (meist `/dev/ttyUSB0`)

### 2.3 Rohdaten vom Zähler testen

```bash
# Berechtigung setzen
sudo chmod 666 /dev/ttyUSB0

# Rohdaten anzeigen (5 Sekunden)
sudo timeout 5 cat /dev/ttyUSB0

# Mit Hex-Ausgabe
sudo timeout 5 cat /dev/ttyUSB0 | xxd
```

Sie sollten jetzt Daten vom Zähler sehen!

### 2.4 ser2net installieren und konfigurieren

```bash
# ser2net installieren
sudo apt install ser2net -y

# Version prüfen
ser2net -v
```

**Für ser2net 4.x (neuere Versionen):**

```bash
# Konfigurationsdatei erstellen
sudo nano /etc/ser2net/ser2net.yaml
```

Fügen Sie ein:

```yaml
connection: &easyMeter
  accepter: tcp,3000
  enable: on
  options:
    kickolduser: true
    telnet-brk-on-sync: false
  connector: serialdev,
             /dev/ttyUSB0,
             9600e71,local
```

**Für ser2net 3.x (ältere Versionen):**

```bash
# Konfigurationsdatei bearbeiten
sudo nano /etc/ser2net.conf
```

Fügen Sie ein:

```
3000:raw:600:/dev/ttyUSB0:9600 EVEN 7DATABITS 1STOPBIT XONXOFF LOCAL -RTSCTS
```

### 2.5 ser2net starten

```bash
# Dienst starten
sudo systemctl start ser2net

# Autostart aktivieren
sudo systemctl enable ser2net

# Status prüfen
sudo systemctl status ser2net
# Sollte "active (running)" zeigen

# Port prüfen
sudo netstat -tulpn | grep 3000
# Sollte zeigen: tcp  0.0.0.0:3000  LISTEN
```

### 2.6 ser2net testen

```bash
# Von einem anderen Rechner im Netzwerk
telnet 192.168.1.100 3000

# Sie sollten jetzt Daten vom Stromzähler sehen
# Beenden mit: Ctrl+]  dann quit
```

**Notieren Sie sich die IP des Raspberry Pi!**

## Teil 3: Home Assistant vorbereiten

### 3.1 Mosquitto MQTT Broker installieren

1. Öffnen Sie Home Assistant
2. Gehen Sie zu **Einstellungen** → **Add-ons**
3. Klicken Sie auf **Add-on Store**
4. Suchen Sie nach **"Mosquitto broker"**
5. Klicken Sie auf **Installieren**
6. Nach der Installation:
   - Aktivieren Sie **Start on boot**
   - Aktivieren Sie **Watchdog**
   - Klicken Sie auf **Start**

### 3.2 MQTT Integration einrichten

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **+ Integration hinzufügen**
3. Suchen Sie nach **"MQTT"**
4. Wählen Sie **MQTT**
5. Konfiguration:
   - Broker: `core-mosquitto` (oder `localhost`)
   - Port: `1883`
   - Benutzername: (leer lassen)
   - Passwort: (leer lassen)
6. Klicken Sie auf **Absenden**

## Teil 4: OBIS D0 Reader Add-on installieren

### 4.1 Verbindung testen

Testen Sie die Verbindung zum ser2net Server:

```bash
# Von Ihrem PC/Mac aus
telnet 192.168.1.100 3000
```

Sie sollten ASCII-Text (D0-Protokoll) vom Stromzähler sehen, z.B.:
```
/EBZ...
1-0:1.8.0*255(...)
1-0:16.7.0*255(...)
...
```

Beenden mit: `Ctrl+]` dann `quit`

### 4.2 Add-on Repository zu Home Assistant hinzufügen

**Option A: Via GitHub (empfohlen)**

1. Forken Sie das Repository auf GitHub
2. In Home Assistant:
   - **Einstellungen** → **Add-ons** → **Add-on Store**
   - Klicken Sie auf **⋮** (drei Punkte oben rechts)
   - Wählen Sie **Repositories**
   - Fügen Sie hinzu: `https://github.com/IHR-USERNAME/homeassistant-obis`
   - Klicken Sie auf **Hinzufügen**

**Option B: Lokale Installation**

1. Kopieren Sie den `obis-d0-reader` Ordner auf Ihren Home Assistant Server:

```bash
# Via SSH
scp -r obis-d0-reader/ root@homeassistant.local:/addons/

# Oder via Samba/SMB
# Kopieren Sie den Ordner nach: /addons/obis-d0-reader/
```

2. In Home Assistant:
   - **Einstellungen** → **Add-ons** → **Add-on Store**
   - Klicken Sie auf **Reload** (↻ Symbol oben rechts)

### 4.3 OBIS D0 Reader installieren

1. Im **Add-on Store** suchen Sie nach **"OBIS D0 Reader"**
2. Klicken Sie auf das Add-on
3. Klicken Sie auf **Installieren**
4. Warten Sie, bis die Installation abgeschlossen ist (kann mehrere Minuten dauern)

### 4.4 Add-on konfigurieren

Gehen Sie zum **Konfiguration** Tab:

```yaml
tcp_host: "192.168.1.100"    # IP Ihres Raspberry Pi
tcp_port: 3000               # ser2net Port

mqtt_enabled: true
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_user: ""
mqtt_password: ""

mqtt_base_topic: "homeassistant/sensor/obis"
mqtt_discovery: true
mqtt_discovery_prefix: "homeassistant"

mqtt_topic_mode: "auto"
mqtt_custom_topics: {}

meter_name: "easyMeter"      # Ihr Zählername
poll_interval: 2             # Alle 2 Sekunden

log_level: "info"
```

**Speichern** Sie die Konfiguration!

### 4.5 Add-on starten

1. Gehen Sie zum **Info** Tab
2. Aktivieren Sie:
   - ☑️ **Start on boot** - Auto-Start
   - ☑️ **Watchdog** - Automatischer Neustart
3. Klicken Sie auf **Start**

### 4.6 Logs prüfen

Gehen Sie zum **Log** Tab. Sie sollten sehen:

```
[info] Starte OBIS D0 Reader...
[info] Konfiguration:
[info]   TCP: 192.168.1.100:3000
[info]   MQTT: True (core-mosquitto)
[info]   Zähler: easyMeter
[info] OBIS D0 Reader gestartet
[info] Verbinde zu MQTT Broker core-mosquitto:1883...
[info] MQTT-Verbindung erfolgreich
[info] Publiziere MQTT Discovery Konfigurationen...
[info] MQTT Discovery abgeschlossen
[info] Verbinde zu 192.168.1.100:3000...
[info] TCP-Verbindung erfolgreich
[info] Erfolgreich 16 Werte geparst
[info] Aktuelle Leistung: 1234.56 W
```

✅ **Perfekt!** Das Add-on läuft!

## Teil 5: Sensoren in Home Assistant nutzen

### 5.1 Sensoren finden

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **MQTT**
3. Sie sollten ein Gerät sehen: **easyMeter**
4. Klicken Sie darauf

Sie sehen jetzt alle Sensoren:
- easyMeter Total Energy Import
- easyMeter Total Energy Export
- easyMeter Power Total
- easyMeter Power L1, L2, L3
- easyMeter Voltage L1, L2, L3
- ... und mehr

### 5.2 Energy Dashboard einrichten

1. Gehen Sie zu **Einstellungen** → **Dashboards** → **Energie**
2. **Stromnetz** → **Netzverbrauch**
3. Wählen Sie: `sensor.easymeter_total_energy_import`
4. Optional: **Rücklieferung zum Netz**
5. Wählen Sie: `sensor.easymeter_total_energy_export`
6. Speichern

Nach 1-2 Stunden sehen Sie die erste Statistik!

### 5.3 Dashboard-Karte erstellen

Erstellen Sie eine Lovelace-Karte:

```yaml
type: entities
title: Stromzähler
entities:
  - entity: sensor.easymeter_power_total
    name: Aktuelle Leistung
  - entity: sensor.easymeter_total_energy_import
    name: Gesamtverbrauch
  - entity: sensor.easymeter_total_energy_export
    name: Einspeisung
  - entity: sensor.easymeter_voltage_l1
    name: Spannung L1
  - entity: sensor.easymeter_voltage_l2
    name: Spannung L2
  - entity: sensor.easymeter_voltage_l3
    name: Spannung L3
```

## Teil 6: Erweiterte Konfiguration (Optional)

### 6.1 Custom MQTT-Topics für externe Systeme

Falls Sie Daten an andere Systeme senden möchten (Node-RED, Grafana, etc.):

```yaml
mqtt_topic_mode: "custom"
mqtt_custom_topics:
  "1-0:16.7.0*255": "energie/leistung/aktuell"
  "1-0:1.8.0*255": "energie/verbrauch/total"
  "power_total": "nodered/power"
  "total_energy_import": "grafana/energy"
```

### 6.2 Automationen erstellen

Beispiel: Benachrichtigung bei hohem Verbrauch

```yaml
automation:
  - alias: "Hoher Stromverbrauch"
    trigger:
      - platform: numeric_state
        entity_id: sensor.easymeter_power_total
        above: 3000  # 3000 Watt
        for:
          minutes: 5
    action:
      - service: notify.mobile_app
        data:
          title: "Hoher Stromverbrauch!"
          message: "Aktuell: {{ states('sensor.easymeter_power_total') }} W"
```

## Fehlerbehebung

### Problem: Keine Daten empfangen

```bash
# Auf Raspberry Pi
sudo systemctl status ser2net
sudo netstat -tulpn | grep 3000
sudo timeout 10 cat /dev/ttyUSB0 | xxd
```

### Problem: MQTT-Verbindung fehlgeschlagen

- Ist Mosquitto gestartet?
- Prüfen Sie Add-on Logs
- Prüfen Sie MQTT Integration

### Problem: Sensoren erscheinen nicht

- Discovery aktiviert?
- MQTT Integration konfiguriert?
- Home Assistant neu starten

## Checkliste

Vor dem Abschluss prüfen Sie:

- [ ] IR-Lesekopf am Zähler montiert
- [ ] Raspberry Pi ser2net läuft
- [ ] TCP-Verbindung funktioniert (telnet test)
- [ ] Home Assistant Mosquitto läuft
- [ ] MQTT Integration eingerichtet
- [ ] OBIS D0 Reader Add-on gestartet
- [ ] Add-on Logs zeigen erfolgreiche Verbindung
- [ ] Sensoren in MQTT-Integration sichtbar
- [ ] Energy Dashboard konfiguriert
- [ ] Dashboard-Karte erstellt

## Nächste Schritte

1. **Überwachen Sie die Daten** für 24 Stunden
2. **Erstellen Sie Automationen** basierend auf Verbrauch
3. **Integrieren Sie in Dashboards** für Visualisierung
4. **Exportieren Sie zu Grafana** für erweiterte Auswertungen (optional)

## Support

Bei Problemen:

1. Prüfen Sie die Add-on **Logs**
2. Testen Sie die **TCP-Verbindung** zum ser2net (telnet)
3. Prüfen Sie die **ser2net Logs** auf dem Pi
4. Öffnen Sie ein **GitHub Issue** mit Logs

**Viel Erfolg!** 🎉

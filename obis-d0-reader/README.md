# OBIS D0 Reader Add-on für Home Assistant

Liest Stromzähler mit OBIS D0-Protokoll via ser2net und sendet die Daten an MQTT mit Home Assistant Auto-Discovery.

## Über dieses Add-on

Dieses Add-on verbindet sich mit einem OBIS D0-Stromzähler über TCP (ser2net) und publiziert alle Messwerte automatisch an Home Assistant via MQTT. Es unterstützt:

- ✅ **D0-Protokoll** (ASCII-basiert) - Kompatibel mit vielen deutschen Stromzählern
- ✅ **TCP-Verbindung** - Funktioniert mit ser2net auf Raspberry Pi oder anderen Systemen
- ✅ **MQTT Auto-Discovery** - Sensoren erscheinen automatisch in Home Assistant
- ✅ **Konfigurierbare MQTT-Topics** - Flexibles Topic-Mapping
- ✅ **Energy Dashboard Integration** - Alle Energiewerte sind kompatibel
- ✅ **15+ Sensoren** - Energie, Leistung, Spannung, Strom pro Phase

## Unterstützte Messwerte

Das Add-on erkennt und publiziert automatisch:

### Energiezähler
- **Gesamtbezug** (1-0:1.8.0*255) - Total Import in kWh
- **Gesamteinspeisung** (1-0:2.8.0*255) - Total Export in kWh

### Leistung
- **Gesamtleistung** (1-0:16.7.0*255) - Total Power in W
- **Leistung Phase L1** (1-0:36.7.0*255)
- **Leistung Phase L2** (1-0:56.7.0*255)
- **Leistung Phase L3** (1-0:76.7.0*255)

### Spannung
- **Spannung Phase L1** (1-0:32.7.0*255) in V
- **Spannung Phase L2** (1-0:52.7.0*255) in V
- **Spannung Phase L3** (1-0:72.7.0*255) in V

### Strom
- **Strom Phase L1** (1-0:31.7.0*255) in A
- **Strom Phase L2** (1-0:51.7.0*255) in A
- **Strom Phase L3** (1-0:71.7.0*255) in A

### Weitere
- **Frequenz** (1-0:14.7.0*255) in Hz
- **Zähler-ID** (1-0:96.1.0*255)
- **Gerätestatus** (1-0:96.5.0*255)

## Installation

### 1. Add-on Repository hinzufügen

1. Öffnen Sie Home Assistant
2. Navigieren Sie zu **Einstellungen** → **Add-ons** → **Add-on Store**
3. Klicken Sie auf die **⋮** (drei Punkte) oben rechts
4. Wählen Sie **Repositories**
5. Fügen Sie diese URL hinzu:
   ```
   https://github.com/lejando/homeassistant-obis
   ```

### 2. Add-on installieren

1. Suchen Sie nach **"OBIS D0 Reader"** im Add-on Store
2. Klicken Sie auf **Installieren**
3. Warten Sie, bis die Installation abgeschlossen ist

### 3. Konfiguration

#### Basis-Konfiguration

```yaml
tcp_host: "192.168.1.100"  # IP des ser2net Servers
tcp_port: 3000              # ser2net Port

mqtt_enabled: true
mqtt_host: "core-mosquitto"  # MQTT Broker (Standard: Home Assistant Mosquitto)
mqtt_port: 1883
mqtt_user: ""                # Optional: MQTT Benutzername
mqtt_password: ""            # Optional: MQTT Passwort

mqtt_base_topic: "homeassistant/sensor/obis"
mqtt_discovery: true
mqtt_discovery_prefix: "homeassistant"

meter_name: "easyMeter"
poll_interval: 2             # Abfrageintervall in Sekunden

log_level: "info"            # debug, info, warning, error
```

#### Erweiterte MQTT-Konfiguration

**Auto-Modus (Standard):**
```yaml
mqtt_topic_mode: "auto"
```
Topics folgen dem Schema: `{mqtt_base_topic}/{sensor_name}/state`

Beispiel:
- `homeassistant/sensor/obis/power_total/state`
- `homeassistant/sensor/obis/total_energy_import/state`

**Custom Topics:**
```yaml
mqtt_topic_mode: "custom"
mqtt_custom_topics:
  "1-0:16.7.0*255": "energie/stromzaehler/leistung"
  "1-0:1.8.0*255": "energie/stromzaehler/verbrauch"
  "power_total": "custom/power"
  "total_energy_import": "custom/energy"
```

Sie können entweder OBIS-Codes oder Sensor-Namen als Keys verwenden.

### 4. Add-on starten

1. Gehen Sie zum **Konfiguration** Tab des Add-ons
2. Konfigurieren Sie die Einstellungen
3. Speichern Sie die Konfiguration
4. Klicken Sie auf **Start**
5. Aktivieren Sie optional:
   - ☑️ **Start on boot** - Auto-Start beim Neustart
   - ☑️ **Watchdog** - Automatischer Neustart bei Absturz

### 5. Logs prüfen

Wechseln Sie zum **Log** Tab um zu sehen:
- TCP-Verbindungsstatus
- MQTT-Verbindungsstatus
- Empfangene Messwerte
- Eventuelle Fehler

## Voraussetzungen

### ser2net auf dem Raspberry Pi

Ihr Raspberry Pi mit dem IR-Lesekopf benötigt ser2net:

**ser2net 4.x Konfiguration** (`/etc/ser2net/ser2net.yaml`):
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

**ser2net 3.x Konfiguration** (`/etc/ser2net.conf`):
```
3000:raw:600:/dev/ttyUSB0:9600 EVEN 7DATABITS 1STOPBIT XONXOFF LOCAL -RTSCTS
```

**ser2net neu starten:**
```bash
sudo systemctl restart ser2net
```

### MQTT Broker

Sie benötigen einen MQTT Broker. Am einfachsten:

1. Installieren Sie das **Mosquitto broker** Add-on
2. Starten Sie es
3. Verwenden Sie `core-mosquitto` als `mqtt_host`

## Home Assistant Integration

### Automatische Discovery

Bei aktivierter Auto-Discovery (`mqtt_discovery: true`) erscheinen die Sensoren automatisch unter:

**Einstellungen** → **Geräte & Dienste** → **MQTT** → Gerät: **{meter_name}**

### Energy Dashboard

Die Energiezähler können direkt im Energy Dashboard verwendet werden:

1. **Einstellungen** → **Dashboards** → **Energie**
2. **Stromnetz** → **Netzverbrauch hinzufügen**
3. Wählen Sie: `sensor.easymeter_total_energy_import`
4. Optional: **Rücklieferung** → `sensor.easymeter_total_energy_export`

### Manuelle Sensor-Konfiguration

Falls Auto-Discovery nicht funktioniert, können Sie Sensoren manuell in `configuration.yaml` definieren:

```yaml
mqtt:
  sensor:
    - name: "Stromzähler Gesamtleistung"
      state_topic: "homeassistant/sensor/obis/power_total/state"
      unit_of_measurement: "W"
      device_class: power
      state_class: measurement

    - name: "Stromzähler Gesamtverbrauch"
      state_topic: "homeassistant/sensor/obis/total_energy_import/state"
      unit_of_measurement: "kWh"
      device_class: energy
      state_class: total_increasing
```

## Erweiterte Nutzung

### Custom MQTT-Topics für externe Systeme

Sie können das Add-on nutzen, um Daten an andere MQTT-Clients zu senden:

```yaml
mqtt_topic_mode: "custom"
mqtt_custom_topics:
  # Sende an Node-RED
  "1-0:16.7.0*255": "nodered/power/current"

  # Sende an Grafana
  "total_energy_import": "metrics/energy/import"
  "total_energy_export": "metrics/energy/export"

  # Sende an ioBroker
  "power_l1": "iobroker/energy/phase1"
  "power_l2": "iobroker/energy/phase2"
  "power_l3": "iobroker/energy/phase3"
```

### Alle Werte als JSON

Das Add-on publiziert zusätzlich alle Werte als JSON-Objekt:

**Topic:** `{mqtt_base_topic}/all`

**Payload Beispiel:**
```json
{
  "power_total": "1234.56",
  "total_energy_import": "12345.67890",
  "total_energy_export": "123.45",
  "voltage_l1": "230.0",
  "voltage_l2": "230.5",
  "voltage_l3": "229.8",
  "power_l1": "450.00",
  "power_l2": "400.50",
  "power_l3": "384.06"
}
```

## Fehlerbehebung

### Keine Daten empfangen

1. **Prüfen Sie die TCP-Verbindung:**
   ```bash
   telnet 192.168.1.100 3000
   ```
   Sie sollten Daten vom Zähler sehen.

2. **Prüfen Sie ser2net auf dem Pi:**
   ```bash
   sudo systemctl status ser2net
   sudo netstat -tulpn | grep 3000
   ```

3. **Prüfen Sie den USB-Lesekopf:**
   ```bash
   ls -la /dev/ttyUSB*
   sudo cat /dev/ttyUSB0
   ```

### MQTT-Verbindung fehlgeschlagen

1. **Prüfen Sie Mosquitto:**
   - Ist das Mosquitto Add-on installiert und gestartet?
   - Einstellungen → Add-ons → Mosquitto broker

2. **Prüfen Sie MQTT-Credentials:**
   - Falls Sie Authentifizierung nutzen, sind User/Password korrekt?

3. **Logs prüfen:**
   - Add-on → Log Tab
   - Suchen Sie nach "MQTT" Fehlermeldungen

### Sensoren erscheinen nicht

1. **Prüfen Sie MQTT Integration:**
   - Einstellungen → Geräte & Dienste → MQTT
   - Ist MQTT konfiguriert?

2. **Manuelle Discovery:**
   - Einstellungen → Geräte & Dienste → MQTT
   - Klicken Sie auf "Configure"
   - Prüfen Sie "Discovered entities"

3. **Logs prüfen:**
   - Suchen Sie nach "Discovery publiziert"

## Sensor-Namen und OBIS-Codes

| Sensor Name | OBIS-Code | Beschreibung | Einheit |
|-------------|-----------|--------------|---------|
| `device_id` | 1-0:0.0.0*255 | Geräte-ID | - |
| `meter_id` | 1-0:96.1.0*255 | Zähler-ID | - |
| `total_energy_import` | 1-0:1.8.0*255 | Gesamtbezug | kWh |
| `total_energy_export` | 1-0:2.8.0*255 | Gesamteinspeisung | kWh |
| `power_total` | 1-0:16.7.0*255 | Gesamtleistung | W |
| `power_l1` | 1-0:36.7.0*255 | Leistung Phase 1 | W |
| `power_l2` | 1-0:56.7.0*255 | Leistung Phase 2 | W |
| `power_l3` | 1-0:76.7.0*255 | Leistung Phase 3 | W |
| `voltage_l1` | 1-0:32.7.0*255 | Spannung Phase 1 | V |
| `voltage_l2` | 1-0:52.7.0*255 | Spannung Phase 2 | V |
| `voltage_l3` | 1-0:72.7.0*255 | Spannung Phase 3 | V |
| `current_l1` | 1-0:31.7.0*255 | Strom Phase 1 | A |
| `current_l2` | 1-0:51.7.0*255 | Strom Phase 2 | A |
| `current_l3` | 1-0:71.7.0*255 | Strom Phase 3 | A |
| `frequency` | 1-0:14.7.0*255 | Netzfrequenz | Hz |
| `device_status` | 1-0:96.5.0*255 | Gerätestatus | - |
| `operating_time` | 0-0:96.8.0*255 | Betriebszeit | - |

## Support

Bei Problemen oder Fragen:

1. Prüfen Sie die **Logs** des Add-ons
2. Prüfen Sie die **ser2net Konfiguration** auf dem Pi
3. Öffnen Sie ein Issue auf GitHub

## Lizenz

MIT License

## Changelog

### Version 1.0.0
- Initiale Version
- D0-Protokoll Support
- MQTT Auto-Discovery
- Konfigurierbare Custom Topics
- 15+ OBIS-Codes unterstützt

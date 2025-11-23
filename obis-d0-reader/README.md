# OBIS D0 Reader Add-on for Home Assistant

Reads electricity meters with OBIS D0 protocol via ser2net and sends data to MQTT with Home Assistant Auto-Discovery.

## About this Add-on

This add-on connects to an OBIS D0 electricity meter via TCP (ser2net) and publishes all measurement values automatically to Home Assistant via MQTT. It supports:

- ✅ **D0 Protocol** (ASCII-based) - Compatible with many German electricity meters
- ✅ **TCP Connection** - Works with ser2net on Raspberry Pi or other systems
- ✅ **MQTT Auto-Discovery** - Sensors appear automatically in Home Assistant
- ✅ **Configurable MQTT Topics** - Flexible topic mapping
- ✅ **Energy Dashboard Integration** - All energy values are compatible
- ✅ **15+ Sensors** - Energy, power, voltage, current per phase

## Supported Measurements

The add-on automatically detects and publishes:

### Energy Meters
- **Total Import** (1-0:1.8.0*255) - Total Import in kWh
- **Total Export** (1-0:2.8.0*255) - Total Export in kWh

### Power
- **Total Power** (1-0:16.7.0*255) - Total Power in W
- **Power Phase L1** (1-0:36.7.0*255)
- **Power Phase L2** (1-0:56.7.0*255)
- **Power Phase L3** (1-0:76.7.0*255)

### Voltage
- **Voltage Phase L1** (1-0:32.7.0*255) in V
- **Voltage Phase L2** (1-0:52.7.0*255) in V
- **Voltage Phase L3** (1-0:72.7.0*255) in V

### Current
- **Current Phase L1** (1-0:31.7.0*255) in A
- **Current Phase L2** (1-0:51.7.0*255) in A
- **Current Phase L3** (1-0:71.7.0*255) in A

### Other
- **Frequency** (1-0:14.7.0*255) in Hz
- **Meter ID** (1-0:96.1.0*255)
- **Device Status** (1-0:96.5.0*255)

## Installation

### 1. Add Add-on Repository

1. Open Home Assistant
2. Navigate to **Settings** → **Add-ons** → **Add-on Store**
3. Click on **⋮** (three dots) top right
4. Select **Repositories**
5. Add this URL:
   ```
   https://github.com/lejando/homeassistant-obis
   ```

### 2. Install Add-on

1. Search for **"OBIS D0 Reader"** in the Add-on Store
2. Click on **Install**
3. Wait for the installation to complete

### 3. Configuration

#### Basic Configuration

```yaml
tcp_host: "192.168.1.100"  # IP of ser2net server
tcp_port: 3000              # ser2net port

mqtt_enabled: true
mqtt_host: "core-mosquitto"  # MQTT Broker (default: Home Assistant Mosquitto)
mqtt_port: 1883
mqtt_user: ""                # Optional: MQTT username
mqtt_password: ""            # Optional: MQTT password

mqtt_base_topic: "homeassistant/sensor/obis"
mqtt_discovery: true
mqtt_discovery_prefix: "homeassistant"

meter_name: "easyMeter"
poll_interval: 2             # Poll interval in seconds

log_level: "info"            # debug, info, warning, error
```

#### Advanced MQTT Configuration

**Auto Mode (default):**
```yaml
mqtt_topic_mode: "auto"
```
Topics follow the schema: `{mqtt_base_topic}/{sensor_name}/state`

Example:
- `homeassistant/sensor/obis/power_total/state`
- `homeassistant/sensor/obis/total_energy_import/state`

**Custom Topics:**
```yaml
mqtt_topic_mode: "custom"
mqtt_custom_topics:
  "1-0:16.7.0*255": "energy/meter/power"
  "1-0:1.8.0*255": "energy/meter/consumption"
  "power_total": "custom/power"
  "total_energy_import": "custom/energy"
```

You can use either OBIS codes or sensor names as keys.

### 4. Start Add-on

1. Go to the **Configuration** tab of the add-on
2. Configure the settings
3. Save the configuration
4. Click on **Start**
5. Optionally enable:
   - ☑️ **Start on boot** - Auto-start on reboot
   - ☑️ **Watchdog** - Automatic restart on crash

### 5. Check Logs

Switch to the **Log** tab to see:
- TCP connection status
- MQTT connection status
- Received measurements
- Any errors

## Prerequisites

### ser2net on Raspberry Pi

Your Raspberry Pi with the IR read head requires ser2net:

**ser2net 4.x configuration** (`/etc/ser2net/ser2net.yaml`):
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

**ser2net 3.x configuration** (`/etc/ser2net.conf`):
```
3000:raw:600:/dev/ttyUSB0:9600 EVEN 7DATABITS 1STOPBIT XONXOFF LOCAL -RTSCTS
```

**Restart ser2net:**
```bash
sudo systemctl restart ser2net
```

### MQTT Broker

You need an MQTT broker. The easiest way:

1. Install the **Mosquitto broker** add-on
2. Start it
3. Use `core-mosquitto` as `mqtt_host`

## Home Assistant Integration

### Automatic Discovery

With auto-discovery enabled (`mqtt_discovery: true`), sensors appear automatically under:

**Settings** → **Devices & Services** → **MQTT** → Device: **{meter_name}**

### Energy Dashboard

The energy meters can be used directly in the Energy Dashboard:

1. **Settings** → **Dashboards** → **Energy**
2. **Grid consumption** → **Add consumption**
3. Select: `sensor.easymeter_total_energy_import`
4. Optional: **Return to grid** → `sensor.easymeter_total_energy_export`

### Manual Sensor Configuration

If auto-discovery doesn't work, you can manually define sensors in `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name: "Meter Total Power"
      state_topic: "homeassistant/sensor/obis/power_total/state"
      unit_of_measurement: "W"
      device_class: power
      state_class: measurement

    - name: "Meter Total Consumption"
      state_topic: "homeassistant/sensor/obis/total_energy_import/state"
      unit_of_measurement: "kWh"
      device_class: energy
      state_class: total_increasing
```

## Advanced Usage

### Custom MQTT Topics for External Systems

You can use the add-on to send data to other MQTT clients:

```yaml
mqtt_topic_mode: "custom"
mqtt_custom_topics:
  # Send to Node-RED
  "1-0:16.7.0*255": "nodered/power/current"

  # Send to Grafana
  "total_energy_import": "metrics/energy/import"
  "total_energy_export": "metrics/energy/export"

  # Send to ioBroker
  "power_l1": "iobroker/energy/phase1"
  "power_l2": "iobroker/energy/phase2"
  "power_l3": "iobroker/energy/phase3"
```

### All Values as JSON

The add-on additionally publishes all values as a JSON object:

**Topic:** `{mqtt_base_topic}/all`

**Payload Example:**
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

## Troubleshooting

### No Data Received

1. **Check TCP connection:**
   ```bash
   telnet 192.168.1.100 3000
   ```
   You should see data from the meter.

2. **Check ser2net on the Pi:**
   ```bash
   sudo systemctl status ser2net
   sudo netstat -tulpn | grep 3000
   ```

3. **Check USB read head:**
   ```bash
   ls -la /dev/ttyUSB*
   sudo cat /dev/ttyUSB0
   ```

### MQTT Connection Failed

1. **Check Mosquitto:**
   - Is the Mosquitto add-on installed and running?
   - Settings → Add-ons → Mosquitto broker

2. **Check MQTT credentials:**
   - If you use authentication, are user/password correct?

3. **Check logs:**
   - Add-on → Log tab
   - Look for "MQTT" error messages

### Sensors Not Appearing

1. **Check MQTT integration:**
   - Settings → Devices & Services → MQTT
   - Is MQTT configured?

2. **Manual discovery:**
   - Settings → Devices & Services → MQTT
   - Click on "Configure"
   - Check "Discovered entities"

3. **Check logs:**
   - Look for "Discovery published"

## Sensor Names and OBIS Codes

| Sensor Name | OBIS Code | Description | Unit |
|-------------|-----------|-------------|------|
| `device_id` | 1-0:0.0.0*255 | Device ID | - |
| `meter_id` | 1-0:96.1.0*255 | Meter ID | - |
| `total_energy_import` | 1-0:1.8.0*255 | Total Import | kWh |
| `total_energy_export` | 1-0:2.8.0*255 | Total Export | kWh |
| `power_total` | 1-0:16.7.0*255 | Total Power | W |
| `power_l1` | 1-0:36.7.0*255 | Power Phase 1 | W |
| `power_l2` | 1-0:56.7.0*255 | Power Phase 2 | W |
| `power_l3` | 1-0:76.7.0*255 | Power Phase 3 | W |
| `voltage_l1` | 1-0:32.7.0*255 | Voltage Phase 1 | V |
| `voltage_l2` | 1-0:52.7.0*255 | Voltage Phase 2 | V |
| `voltage_l3` | 1-0:72.7.0*255 | Voltage Phase 3 | V |
| `current_l1` | 1-0:31.7.0*255 | Current Phase 1 | A |
| `current_l2` | 1-0:51.7.0*255 | Current Phase 2 | A |
| `current_l3` | 1-0:71.7.0*255 | Current Phase 3 | A |
| `frequency` | 1-0:14.7.0*255 | Grid Frequency | Hz |
| `device_status` | 1-0:96.5.0*255 | Device Status | - |
| `operating_time` | 0-0:96.8.0*255 | Operating Time | - |

## Support

For problems or questions:

1. Check the **logs** of the add-on
2. Check the **ser2net configuration** on the Pi
3. Open an issue on GitHub

## License

MIT License

## Changelog

### Version 1.0.0
- Initial release
- D0 protocol support
- MQTT Auto-Discovery
- Configurable custom topics
- 15+ OBIS codes supported

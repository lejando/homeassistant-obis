# OBIS D0 Reader - Configuration Documentation

This document provides detailed explanations for all configuration parameters available in the OBIS D0 Reader add-on.

## Table of Contents

- [TCP/IP Connection Settings](#tcpip-connection-settings)
- [MQTT Broker Settings](#mqtt-broker-settings)
- [MQTT Discovery Settings](#mqtt-discovery-settings)
- [Advanced MQTT Topic Configuration](#advanced-mqtt-topic-configuration)
- [Meter Settings](#meter-settings)
- [Logging Settings](#logging-settings)
- [Configuration Examples](#configuration-examples)

---

## TCP/IP Connection Settings

These settings configure the connection to your ser2net server running on the Raspberry Pi (or other device) that has the IR read head connected.

### `tcp_host`

**Type:** String
**Required:** Yes
**Default:** `"192.168.1.100"`
**Example:** `"192.168.1.50"` or `"raspberrypi.local"`

The IP address or hostname of your ser2net server.

**How to find this value:**
- If you're using a Raspberry Pi, run `hostname -I` on the Pi to get its IP address
- You can also use the hostname instead of IP (e.g., `raspberrypi.local`)
- Make sure the device is reachable from your Home Assistant instance

**What happens if this is wrong:**
- The add-on will fail to connect and show connection errors in the logs
- You'll see messages like "Connection refused" or "Host unreachable"

---

### `tcp_port`

**Type:** Integer
**Required:** Yes
**Default:** `3000`
**Range:** 1-65535
**Example:** `3000`

The TCP port number on which ser2net is listening.

**How to find this value:**
- Check your ser2net configuration file on the Raspberry Pi:
  - For ser2net 4.x: Look in `/etc/ser2net/ser2net.yaml` for the `accepter:` line
  - For ser2net 3.x: Look in `/etc/ser2net.conf` for the port number (first value)
- Common ports: `3000`, `3001`, `10001`

**Test the connection:**
```bash
telnet YOUR_RASPBERRY_PI_IP 3000
```
If successful, you should see data from your meter.

---

## MQTT Broker Settings

These settings configure the connection to your MQTT broker, which is used to send sensor data to Home Assistant.

### `mqtt_enabled`

**Type:** Boolean
**Required:** Yes
**Default:** `true`
**Options:** `true` or `false`

Enable or disable MQTT publishing.

**When to disable:**
- For testing purposes only
- If you want to run the add-on without MQTT (not recommended)

**Recommendation:** Keep this set to `true` for normal operation.

---

### `mqtt_host`

**Type:** String
**Required:** Yes (if MQTT is enabled)
**Default:** `"core-mosquitto"`
**Example:** `"core-mosquitto"`, `"192.168.1.10"`, or `"mqtt.example.com"`

The hostname or IP address of your MQTT broker.

**Common values:**
- `"core-mosquitto"` - If you're using the Mosquitto broker add-on in Home Assistant (recommended)
- `"localhost"` or `"127.0.0.1"` - If the broker is on the same machine
- `"192.168.1.x"` - IP address of a remote MQTT broker
- `"mqtt.example.com"` - Hostname of a remote MQTT broker

**How to verify:**
- Go to Settings → Add-ons → Mosquitto broker
- If it's running, use `"core-mosquitto"`

---

### `mqtt_port`

**Type:** Integer
**Required:** Yes (if MQTT is enabled)
**Default:** `1883`
**Range:** 1-65535
**Example:** `1883` (standard), `8883` (SSL/TLS)

The port number of your MQTT broker.

**Standard ports:**
- `1883` - Default MQTT port (unencrypted)
- `8883` - MQTT over SSL/TLS (encrypted)

**Note:** The Mosquitto add-on in Home Assistant uses port `1883` by default.

---

### `mqtt_user`

**Type:** String (Optional)
**Required:** No
**Default:** `""` (empty)
**Example:** `"homeassistant"` or `"mqtt_user"`

The username for MQTT broker authentication.

**When to use:**
- Leave empty if your MQTT broker doesn't require authentication
- The default Mosquitto add-on in Home Assistant doesn't require authentication when accessed locally

**If authentication is required:**
- Create a user in your MQTT broker configuration
- Enter the username here

---

### `mqtt_password`

**Type:** Password (Optional)
**Required:** No
**Default:** `""` (empty)
**Example:** `"your_secure_password"`

The password for MQTT broker authentication.

**Security note:**
- This value is stored securely by Home Assistant
- Use a strong password if authentication is required

**When to use:**
- Leave empty if your MQTT broker doesn't require authentication
- The default Mosquitto add-on in Home Assistant doesn't require authentication when accessed locally

---

### `mqtt_base_topic`

**Type:** String
**Required:** Yes
**Default:** `"homeassistant/sensor/obis"`
**Example:** `"energy/meter"`, `"home/electricity"`

The base MQTT topic under which all sensor data will be published.

**Topic structure (auto mode):**
```
{mqtt_base_topic}/{sensor_name}/state
```

**Examples:**
- With `"homeassistant/sensor/obis"`:
  - `homeassistant/sensor/obis/power_total/state`
  - `homeassistant/sensor/obis/total_energy_import/state`

- With `"energy/meter"`:
  - `energy/meter/power_total/state`
  - `energy/meter/total_energy_import/state`

**Recommendation:** Use the default unless you have specific integration requirements.

---

## MQTT Discovery Settings

MQTT Discovery allows Home Assistant to automatically detect and configure sensors without manual configuration.

### `mqtt_discovery`

**Type:** Boolean
**Required:** Yes
**Default:** `true`
**Options:** `true` or `false`

Enable or disable MQTT Auto-Discovery for Home Assistant.

**When enabled (recommended):**
- Sensors automatically appear in Home Assistant
- Go to Settings → Devices & Services → MQTT to see your meter device
- All sensors are pre-configured with correct units and device classes

**When to disable:**
- If you want to manually configure sensors
- If you're using the add-on with non-Home Assistant systems only

**Recommendation:** Keep enabled for automatic sensor detection.

---

### `mqtt_discovery_prefix`

**Type:** String
**Required:** Yes (if discovery is enabled)
**Default:** `"homeassistant"`
**Example:** `"homeassistant"`, `"ha"`

The MQTT discovery prefix used by Home Assistant.

**Default Home Assistant value:** `"homeassistant"`

**Discovery topic structure:**
```
{mqtt_discovery_prefix}/sensor/{device_id}/{sensor_name}/config
```

**Important:** This must match your Home Assistant MQTT integration configuration.

**How to verify:**
- Go to Settings → Devices & Services → MQTT → Configure
- Check the "Discovery prefix" setting (usually `homeassistant`)
- Use the same value here

**Recommendation:** Use the default `"homeassistant"` unless you've changed it in Home Assistant.

---

## Advanced MQTT Topic Configuration

These settings allow you to customize how sensor data is published to MQTT topics.

### `mqtt_topic_mode`

**Type:** List (Selection)
**Required:** Yes
**Default:** `"auto"`
**Options:** `"auto"` or `"custom"`

Controls how MQTT topics are generated for sensor values.

#### **Auto Mode** (Recommended)
```yaml
mqtt_topic_mode: "auto"
```

Topics are automatically generated based on sensor names:
- Format: `{mqtt_base_topic}/{sensor_name}/state`
- Example: `homeassistant/sensor/obis/power_total/state`

**Pros:**
- Simple and automatic
- Works perfectly with Home Assistant Auto-Discovery
- No configuration needed

**When to use:**
- For standard Home Assistant integration
- When you don't need custom topic names

#### **Custom Mode** (Advanced)
```yaml
mqtt_topic_mode: "custom"
```

Allows you to define custom MQTT topics for each sensor.

**Pros:**
- Full control over topic names
- Integration with external systems (Node-RED, Grafana, ioBroker, etc.)
- Can publish same data to multiple topics

**When to use:**
- When integrating with non-Home Assistant systems
- When you need specific topic naming schemes
- For advanced MQTT routing scenarios

---

### `mqtt_custom_topics`

**Type:** Dictionary (Key-Value Pairs)
**Required:** Only when `mqtt_topic_mode: "custom"`
**Default:** `{}` (empty)

Custom MQTT topic mappings for individual sensors.

**Format:**
```yaml
mqtt_custom_topics:
  "source_identifier": "target/topic"
```

**Source identifier can be:**
1. **OBIS code** (e.g., `"1-0:16.7.0*255"`)
2. **Sensor name** (e.g., `"power_total"`)

**Example 1: Simple custom topics**
```yaml
mqtt_topic_mode: "custom"
mqtt_custom_topics:
  "power_total": "energy/current_power"
  "total_energy_import": "energy/total_consumption"
```

**Example 2: Integration with Node-RED**
```yaml
mqtt_topic_mode: "custom"
mqtt_custom_topics:
  "1-0:16.7.0*255": "nodered/power/current"
  "1-0:1.8.0*255": "nodered/energy/import"
  "1-0:2.8.0*255": "nodered/energy/export"
```

**Example 3: Multi-system integration**
```yaml
mqtt_topic_mode: "custom"
mqtt_custom_topics:
  # Home Assistant
  "power_total": "homeassistant/sensor/meter/power"

  # Grafana
  "total_energy_import": "metrics/energy/import"
  "total_energy_export": "metrics/energy/export"

  # ioBroker
  "power_l1": "iobroker/energy/phase1"
  "power_l2": "iobroker/energy/phase2"
  "power_l3": "iobroker/energy/phase3"
```

**Available sensor names:**
- `device_id`
- `meter_id`
- `total_energy_import`
- `total_energy_export`
- `power_total`
- `power_l1`, `power_l2`, `power_l3`
- `voltage_l1`, `voltage_l2`, `voltage_l3`
- `current_l1`, `current_l2`, `current_l3`
- `frequency`
- `device_status`
- `operating_time`

**Available OBIS codes:**
See the full list in the [README.md](README.md#sensor-names-and-obis-codes)

**Note:** In custom mode, Auto-Discovery still works if `mqtt_discovery: true` is set.

---

## Meter Settings

These settings configure the meter identification and polling behavior.

### `meter_name`

**Type:** String
**Required:** Yes
**Default:** `"easyMeter"`
**Example:** `"easyMeter"`, `"MainMeter"`, `"HouseMeter"`

A friendly name for your electricity meter.

**Used for:**
- Device name in Home Assistant (shown in Devices & Services)
- MQTT device identifier
- Sensor entity prefixes

**Recommendations:**
- Use a descriptive name without spaces (or use underscores)
- Examples: `"easyMeter"`, `"Main_Meter"`, `"Basement_Meter"`

**What you'll see in Home Assistant:**
- Device name: `{meter_name}` (e.g., "easyMeter")
- Sensor names: `{meter_name} Power Total` (e.g., "easyMeter Power Total")

---

### `poll_interval`

**Type:** Integer
**Required:** Yes
**Default:** `2`
**Range:** 1-60 seconds
**Example:** `2` (every 2 seconds), `5` (every 5 seconds)

How often (in seconds) to read data from the meter.

**Recommended values:**
- `2` seconds - Real-time monitoring (default, recommended)
- `5` seconds - Balanced between updates and load
- `10-15` seconds - Reduced network traffic
- `30-60` seconds - Minimal polling for energy totals only

**Considerations:**
- **Lower values (1-2 seconds):**
  - More real-time data
  - Better for monitoring rapid power changes
  - More network traffic
  - More CPU usage

- **Higher values (10-60 seconds):**
  - Reduced network and CPU load
  - Still accurate for energy totals (kWh)
  - May miss short power spikes
  - Suitable for historical tracking only

**Impact on Energy Dashboard:**
- The Energy Dashboard uses cumulative values (kWh), so polling interval doesn't significantly affect accuracy
- Power monitoring (W) benefits from faster polling

**Recommendation:** Use `2` seconds for best real-time experience.

---

## Logging Settings

### `log_level`

**Type:** List (Selection)
**Required:** Yes
**Default:** `"info"`
**Options:** `"debug"`, `"info"`, `"warning"`, `"error"`

Sets the verbosity of log messages.

#### **debug**
- Most verbose level
- Shows all internal operations
- Includes raw data from meter
- Connection details
- MQTT publish details

**When to use:**
- Troubleshooting connection issues
- Verifying meter data parsing
- Debugging MQTT topics
- Development and testing

**Warning:** Creates large log files, use temporarily.

#### **info** (Recommended)
- Shows important events
- Connection status (TCP, MQTT)
- Sensor value updates
- Discovery publishing
- Errors and warnings

**When to use:**
- Normal operation
- Monitoring system health
- Initial setup and verification

#### **warning**
- Shows only warnings and errors
- Unusual situations
- Failed operations
- Connection interruptions

**When to use:**
- After successful setup
- Production environments
- When you want quiet logs

#### **error**
- Shows only errors
- Failed connections
- Critical failures

**When to use:**
- When system is known to be working
- To minimize log output

**Recommendation:** Use `"info"` for normal operation, `"debug"` for troubleshooting.

---

## Configuration Examples

### Basic Configuration (Recommended for most users)

```yaml
tcp_host: "192.168.1.100"
tcp_port: 3000

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

meter_name: "easyMeter"
poll_interval: 2

log_level: "info"
```

This configuration:
- Connects to ser2net on 192.168.1.100:3000
- Uses local Mosquitto broker
- Auto-discovery enabled
- Automatic topic generation
- 2-second polling
- Standard logging

---

### Configuration with Authentication

```yaml
tcp_host: "192.168.1.100"
tcp_port: 3000

mqtt_enabled: true
mqtt_host: "192.168.1.50"
mqtt_port: 1883
mqtt_user: "mqtt_user"
mqtt_password: "secure_password_here"
mqtt_base_topic: "homeassistant/sensor/obis"
mqtt_discovery: true
mqtt_discovery_prefix: "homeassistant"

mqtt_topic_mode: "auto"
mqtt_custom_topics: {}

meter_name: "MainMeter"
poll_interval: 5

log_level: "info"
```

This configuration:
- Uses remote MQTT broker with authentication
- 5-second polling interval
- Custom meter name

---

### Advanced Configuration with Custom Topics

```yaml
tcp_host: "raspberrypi.local"
tcp_port: 3000

mqtt_enabled: true
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_user: ""
mqtt_password: ""
mqtt_base_topic: "homeassistant/sensor/obis"
mqtt_discovery: true
mqtt_discovery_prefix: "homeassistant"

mqtt_topic_mode: "custom"
mqtt_custom_topics:
  # Energy values for Grafana
  "total_energy_import": "metrics/energy/house/import"
  "total_energy_export": "metrics/energy/house/export"

  # Power values for Node-RED
  "power_total": "nodered/energy/power/total"
  "power_l1": "nodered/energy/power/phase1"
  "power_l2": "nodered/energy/power/phase2"
  "power_l3": "nodered/energy/power/phase3"

  # Voltage for monitoring
  "voltage_l1": "monitoring/grid/voltage/l1"
  "voltage_l2": "monitoring/grid/voltage/l2"
  "voltage_l3": "monitoring/grid/voltage/l3"

meter_name: "HouseMeter"
poll_interval: 2

log_level: "debug"
```

This configuration:
- Uses hostname instead of IP
- Custom MQTT topics for integration with external systems
- Sends data to multiple systems simultaneously
- Debug logging for verification

---

### Minimal Configuration (Testing)

```yaml
tcp_host: "192.168.1.100"
tcp_port: 3000

mqtt_enabled: false
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_user: ""
mqtt_password: ""
mqtt_base_topic: "homeassistant/sensor/obis"
mqtt_discovery: false
mqtt_discovery_prefix: "homeassistant"

mqtt_topic_mode: "auto"
mqtt_custom_topics: {}

meter_name: "TestMeter"
poll_interval: 5

log_level: "debug"
```

This configuration:
- MQTT disabled (for testing TCP connection only)
- Debug logging to see meter data
- Use this to verify ser2net connection before enabling MQTT

---

## Troubleshooting Configuration Issues

### Problem: Can't connect to ser2net

**Check these parameters:**
- `tcp_host`: Verify IP address is correct (`ping IP_ADDRESS`)
- `tcp_port`: Verify port matches ser2net configuration
- Test connection: `telnet TCP_HOST TCP_PORT`

**Solution:**
```bash
# On Raspberry Pi
sudo systemctl status ser2net
sudo netstat -tulpn | grep 3000
```

---

### Problem: No sensors appear in Home Assistant

**Check these parameters:**
- `mqtt_enabled`: Must be `true`
- `mqtt_discovery`: Must be `true`
- `mqtt_host`: Must point to your MQTT broker
- `mqtt_discovery_prefix`: Must match Home Assistant (usually `"homeassistant"`)

**Solution:**
1. Verify MQTT broker is running (Settings → Add-ons → Mosquitto broker)
2. Check MQTT integration (Settings → Devices & Services → MQTT)
3. Check add-on logs for MQTT connection errors
4. Set `log_level: "debug"` to see discovery messages

---

### Problem: Sensors appear but no data

**Check these parameters:**
- `poll_interval`: Try setting to `2` for faster updates
- `tcp_host` and `tcp_port`: Verify connection is working

**Solution:**
1. Check add-on logs for parsing errors
2. Test raw data: `telnet TCP_HOST TCP_PORT`
3. Set `log_level: "debug"` to see received data

---

### Problem: Custom topics not working

**Check these parameters:**
- `mqtt_topic_mode`: Must be `"custom"`
- `mqtt_custom_topics`: Verify syntax (YAML dictionary format)
- Sensor names must match available sensors (see list above)

**Solution:**
1. Verify YAML syntax (indentation, quotes)
2. Check logs for "Publishing to custom topic" messages
3. Use MQTT explorer tool to verify topics
4. Test with a simple mapping first

---

## Getting Help

If you need assistance:

1. **Check the logs** (Log tab in add-on)
2. **Set log level to debug** for detailed information
3. **Verify configuration** against examples above
4. **Test connections** using command-line tools
5. **Open an issue** on [GitHub](https://github.com/lejando/homeassistant-obis/issues) with:
   - Your configuration (remove sensitive data)
   - Relevant log excerpts
   - Description of the problem

---

## Additional Resources

- [Main README](../README.md)
- [Installation Guide](../INSTALL.md)
- [Sensor Reference](README.md#sensor-names-and-obis-codes)
- [GitHub Repository](https://github.com/lejando/homeassistant-obis)

# Installation Guide - Step by Step

This guide will walk you through the complete installation from hardware to full integration in Home Assistant.

## Overview

```
┌─────────────────────┐
│  OBIS Meter         │
│   (D0 Protocol)     │
└──────────┬──────────┘
           │ IR Interface
           ▼
┌─────────────────────┐
│   IR Read Head      │
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
           │ TCP/IP Network
           ▼
┌─────────────────────┐
│  Home Assistant     │
│  (VM on Synology)   │
│  + OBIS D0 Reader   │
│  + Mosquitto MQTT   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Energy Dashboard   │
│  + 15+ Sensors      │
└─────────────────────┘
```

## Part 1: Hardware Setup

### Required Hardware

1. **OBIS Electricity Meter** with D0 interface
   - E.g., EasyMeter, EBZ, EMH, Iskraemeco, etc.

2. **IR Read Head** with USB connection
   - Recommended: Hichi USB IR Read Head
   - Alternative: DIY with IR LED/Photodiode

3. **Raspberry Pi** (already available ✓)
   - Model: Any (Pi 3, Pi 4, Pi Zero W)
   - OS: Raspberry Pi OS (formerly Raspbian)

4. **Network Connection**
   - LAN or WLAN between Pi and Home Assistant

### Mount IR Read Head

1. Position the IR read head on the optical interface of the meter
2. The interface is usually marked with a symbol: 🔦
3. Secure the read head with magnets or adhesive tape
4. Connect the read head via USB to the Raspberry Pi

## Part 2: Raspberry Pi Setup

### 2.1 Install Raspberry Pi OS (if not already done)

```bash
# Update system
sudo apt update
sudo apt upgrade -y
```

### 2.2 Identify USB Read Head

```bash
# Show USB devices
lsusb

# Find serial devices
ls -la /dev/ttyUSB*
# Output should be: /dev/ttyUSB0

# If /dev/ttyACM* instead of ttyUSB*
ls -la /dev/ttyACM*
```

**Note the device** (usually `/dev/ttyUSB0`)

### 2.3 Test Raw Data from Meter

```bash
# Set permissions
sudo chmod 666 /dev/ttyUSB0

# Display raw data (5 seconds)
sudo timeout 5 cat /dev/ttyUSB0

# With hex output
sudo timeout 5 cat /dev/ttyUSB0 | xxd
```

You should now see data from the meter!

### 2.4 Install and Configure ser2net

```bash
# Install ser2net
sudo apt install ser2net -y

# Check version
ser2net -v
```

**For ser2net 4.x (newer versions):**

```bash
# Create configuration file
sudo nano /etc/ser2net/ser2net.yaml
```

Add:

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

**For ser2net 3.x (older versions):**

```bash
# Edit configuration file
sudo nano /etc/ser2net.conf
```

Add:

```
3000:raw:600:/dev/ttyUSB0:9600 EVEN 7DATABITS 1STOPBIT XONXOFF LOCAL -RTSCTS
```

### 2.5 Start ser2net

```bash
# Start service
sudo systemctl start ser2net

# Enable autostart
sudo systemctl enable ser2net

# Check status
sudo systemctl status ser2net
# Should show "active (running)"

# Check port
sudo netstat -tulpn | grep 3000
# Should show: tcp  0.0.0.0:3000  LISTEN
```

### 2.6 Test ser2net

```bash
# From another computer on the network
telnet 192.168.1.100 3000

# You should now see data from the electricity meter
# Exit with: Ctrl+]  then quit
```

**Note the IP of your Raspberry Pi!**

## Part 3: Prepare Home Assistant

### 3.1 Install Mosquitto MQTT Broker

1. Open Home Assistant
2. Go to **Settings** → **Add-ons**
3. Click on **Add-on Store**
4. Search for **"Mosquitto broker"**
5. Click on **Install**
6. After installation:
   - Enable **Start on boot**
   - Enable **Watchdog**
   - Click on **Start**

### 3.2 Set up MQTT Integration

1. Go to **Settings** → **Devices & Services**
2. Click on **+ Add Integration**
3. Search for **"MQTT"**
4. Select **MQTT**
5. Configuration:
   - Broker: `core-mosquitto` (or `localhost`)
   - Port: `1883`
   - Username: (leave empty)
   - Password: (leave empty)
6. Click on **Submit**

## Part 4: Install OBIS D0 Reader Add-on

### 4.1 Test Connection

Test the connection to the ser2net server:

```bash
# From your PC/Mac
telnet 192.168.1.100 3000
```

You should see ASCII text (D0 protocol) from the electricity meter, e.g.:
```
/EBZ...
1-0:1.8.0*255(...)
1-0:16.7.0*255(...)
...
```

Exit with: `Ctrl+]` then `quit`

### 4.2 Add Add-on Repository to Home Assistant

**Option A: Via GitHub (recommended)**

1. Fork the repository on GitHub
2. In Home Assistant:
   - **Settings** → **Add-ons** → **Add-on Store**
   - Click on **⋮** (three dots top right)
   - Select **Repositories**
   - Add: `https://github.com/lejando/homeassistant-obis`
   - Click on **Add**

**Option B: Local Installation**

1. Copy the `obis-d0-reader` folder to your Home Assistant server:

```bash
# Via SSH
scp -r obis-d0-reader/ root@homeassistant.local:/addons/

# Or via Samba/SMB
# Copy the folder to: /addons/obis-d0-reader/
```

2. In Home Assistant:
   - **Settings** → **Add-ons** → **Add-on Store**
   - Click on **Reload** (↻ icon top right)

### 4.3 Install OBIS D0 Reader

1. In the **Add-on Store** search for **"OBIS D0 Reader"**
2. Click on the add-on
3. Click on **Install**
4. Wait for the installation to complete (may take several minutes)

### 4.4 Configure Add-on

Go to the **Configuration** tab:

```yaml
tcp_host: "192.168.1.100"    # IP of your Raspberry Pi
tcp_port: 3000               # ser2net port

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

meter_name: "easyMeter"      # Your meter name
poll_interval: 2             # Every 2 seconds

log_level: "info"
```

**Save** the configuration!

### 4.5 Start Add-on

1. Go to the **Info** tab
2. Enable:
   - ☑️ **Start on boot** - Auto-start
   - ☑️ **Watchdog** - Automatic restart
3. Click on **Start**

### 4.6 Check Logs

Go to the **Log** tab. You should see:

```
[info] Starting OBIS D0 Reader...
[info] Configuration:
[info]   TCP: 192.168.1.100:3000
[info]   MQTT: True (core-mosquitto)
[info]   Meter: easyMeter
[info] OBIS D0 Reader started
[info] Connecting to MQTT Broker core-mosquitto:1883...
[info] MQTT connection successful
[info] Publishing MQTT Discovery configurations...
[info] MQTT Discovery completed
[info] Connecting to 192.168.1.100:3000...
[info] TCP connection successful
[info] Successfully parsed 16 values
[info] Current power: 1234.56 W
```

✅ **Perfect!** The add-on is running!

## Part 5: Use Sensors in Home Assistant

### 5.1 Find Sensors

1. Go to **Settings** → **Devices & Services**
2. Click on **MQTT**
3. You should see a device: **easyMeter**
4. Click on it

You will now see all sensors:
- easyMeter Total Energy Import
- easyMeter Total Energy Export
- easyMeter Power Total
- easyMeter Power L1, L2, L3
- easyMeter Voltage L1, L2, L3
- ... and more

### 5.2 Set up Energy Dashboard

1. Go to **Settings** → **Dashboards** → **Energy**
2. **Grid consumption** → **Add consumption**
3. Select: `sensor.easymeter_total_energy_import`
4. Optional: **Return to grid**
5. Select: `sensor.easymeter_total_energy_export`
6. Save

After 1-2 hours you will see the first statistics!

### 5.3 Create Dashboard Card

Create a Lovelace card:

```yaml
type: entities
title: Electricity Meter
entities:
  - entity: sensor.easymeter_power_total
    name: Current Power
  - entity: sensor.easymeter_total_energy_import
    name: Total Consumption
  - entity: sensor.easymeter_total_energy_export
    name: Feed-in
  - entity: sensor.easymeter_voltage_l1
    name: Voltage L1
  - entity: sensor.easymeter_voltage_l2
    name: Voltage L2
  - entity: sensor.easymeter_voltage_l3
    name: Voltage L3
```

## Part 6: Advanced Configuration (Optional)

### 6.1 Custom MQTT Topics for External Systems

If you want to send data to other systems (Node-RED, Grafana, etc.):

```yaml
mqtt_topic_mode: "custom"
mqtt_custom_topics:
  "1-0:16.7.0*255": "energy/power/current"
  "1-0:1.8.0*255": "energy/consumption/total"
  "power_total": "nodered/power"
  "total_energy_import": "grafana/energy"
```

### 6.2 Create Automations

Example: Notification on high consumption

```yaml
automation:
  - alias: "High Power Consumption"
    trigger:
      - platform: numeric_state
        entity_id: sensor.easymeter_power_total
        above: 3000  # 3000 Watts
        for:
          minutes: 5
    action:
      - service: notify.mobile_app
        data:
          title: "High Power Consumption!"
          message: "Current: {{ states('sensor.easymeter_power_total') }} W"
```

## Troubleshooting

### Problem: No Data Received

```bash
# On Raspberry Pi
sudo systemctl status ser2net
sudo netstat -tulpn | grep 3000
sudo timeout 10 cat /dev/ttyUSB0 | xxd
```

### Problem: MQTT Connection Failed

- Is Mosquitto running?
- Check add-on logs
- Check MQTT integration

### Problem: Sensors Not Appearing

- Discovery enabled?
- MQTT integration configured?
- Restart Home Assistant

## Checklist

Before completion, verify:

- [ ] IR read head mounted on meter
- [ ] Raspberry Pi ser2net running
- [ ] TCP connection working (telnet test)
- [ ] Home Assistant Mosquitto running
- [ ] MQTT integration set up
- [ ] OBIS D0 Reader add-on started
- [ ] Add-on logs show successful connection
- [ ] Sensors visible in MQTT integration
- [ ] Energy Dashboard configured
- [ ] Dashboard card created

## Next Steps

1. **Monitor data** for 24 hours
2. **Create automations** based on consumption
3. **Integrate into dashboards** for visualization
4. **Export to Grafana** for advanced analytics (optional)

## Support

If you encounter problems:

1. Check the add-on **logs**
2. Test the **TCP connection** to ser2net (telnet)
3. Check the **ser2net logs** on the Pi
4. Open a **GitHub issue** with logs

**Good luck!** 🎉

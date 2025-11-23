# Home Assistant OBIS D0 Reader Add-on

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Home Assistant Add-on for reading OBIS D0 electricity meters via ser2net with MQTT integration.

## 🎯 Features

- ✅ **D0 Protocol Support** - Compatible with many German electricity meters (EasyMeter, EBZ, etc.)
- ✅ **TCP/IP Connection** - Works with ser2net on Raspberry Pi or other systems
- ✅ **MQTT Auto-Discovery** - Sensors appear automatically in Home Assistant
- ✅ **Configurable MQTT Topics** - Flexible topic mapping for external systems
- ✅ **Energy Dashboard Ready** - Direct integration into HA Energy Dashboard
- ✅ **15+ Sensors** - Energy, power, voltage, current per phase
- ✅ **No Hardware Modifications** - Uses existing ser2net installation

## 📊 Supported Measurements

The add-on automatically reads all available OBIS codes:

### Energy Meters
- Total Import (kWh)
- Total Export (kWh)

### Power
- Total Power (W)
- Power per phase L1, L2, L3 (W)

### Electrical Parameters
- Voltage per phase (V)
- Current per phase (A)
- Grid frequency (Hz)

### Device Information
- Meter ID / Serial number
- Device status
- Operating time

## 🚀 Quick Start

### 1. Installation

Add this repository to your Home Assistant add-on repositories:

1. **Settings** → **Add-ons** → **Add-on Store**
2. Click on **⋮** (three dots) → **Repositories**
3. Add: `https://github.com/lejando/homeassistant-obis`
4. Search for **"OBIS D0 Reader"** and install it

### 2. Configuration

```yaml
tcp_host: "192.168.1.100"    # IP of your ser2net server
tcp_port: 3000               # ser2net port

mqtt_enabled: true
mqtt_host: "core-mosquitto"  # MQTT Broker
mqtt_base_topic: "homeassistant/sensor/obis"

meter_name: "easyMeter"
poll_interval: 2
```

### 3. Start

1. Save the configuration
2. Start the add-on
3. Check the logs
4. Sensors appear automatically under **Devices & Services** → **MQTT**

## 🔧 Prerequisites

### ser2net on Raspberry Pi

Your Raspberry Pi with IR read head requires ser2net:

**Installation:**
```bash
sudo apt install ser2net
```

**Configuration** (`/etc/ser2net/ser2net.yaml`):
```yaml
connection: &easyMeter
  accepter: tcp,3000
  enable: on
  options:
    kickolduser: true
    telnet-brk-on-sync: false
  connector: serialdev,/dev/ttyUSB0,9600e71,local
```

**Restart:**
```bash
sudo systemctl restart ser2net
```

### MQTT Broker

Install the **Mosquitto broker** add-on from the Home Assistant Add-on Store.

## 📖 Architecture

```
OBIS Electricity Meter (D0 Protocol)
         ↓
    IR Read Head
         ↓
  Raspberry Pi
  /dev/ttyUSB0
  (9600,7,E,1)
         ↓
   ser2net (Port 3000)
         ↓
   [TCP/IP Network]
         ↓
 Home Assistant OS (VM)
   OBIS D0 Reader Add-on
         ↓
   MQTT Broker
         ↓
  Home Assistant
  - Energy Dashboard
  - 15+ Sensors
  - Automations
```

## 🎛️ Advanced Configuration

### Custom MQTT Topics

Send data to custom MQTT topics:

```yaml
mqtt_topic_mode: "custom"
mqtt_custom_topics:
  "1-0:16.7.0*255": "energy/meter/power"
  "1-0:1.8.0*255": "energy/meter/consumption"
  "power_total": "nodered/power/current"
  "total_energy_import": "grafana/energy/import"
```

### External Systems

The add-on can simultaneously send data to multiple systems:

- **Home Assistant** (via Auto-Discovery)
- **Node-RED** (via custom topics)
- **Grafana** (via custom topics)
- **ioBroker** (via custom topics)

All values are additionally published as JSON under: `{mqtt_base_topic}/all`

## 📁 Repository Structure

```
homeassistant-obis/
├── obis-d0-reader/          # Add-on directory
│   ├── config.yaml          # Add-on configuration
│   ├── Dockerfile           # Docker image definition
│   ├── build.yaml           # Multi-arch build config
│   ├── run.sh              # Startup script
│   ├── obis_reader.py      # Python main program
│   ├── requirements.txt    # Python dependencies
│   ├── README.md           # Add-on documentation
│   └── CHANGELOG.md        # Version history
├── INSTALL.md              # Installation guide
├── LICENSE                 # MIT License
├── repository.yaml         # Add-on repository definition
└── README.md               # This README
```

## 🔧 Testing the Connection

### Check ser2net Connection

Test the connection to the ser2net server:

```bash
# From any computer on the network
telnet 192.168.1.100 3000
```

You should see ASCII text from the electricity meter (D0 protocol).

### Raspberry Pi Diagnostics

Check your ser2net installation on the Raspberry Pi:

```bash
# Check status
sudo systemctl status ser2net

# Check port
sudo netstat -tulpn | grep 3000

# Check USB device
ls -la /dev/ttyUSB*

# Test raw data
sudo timeout 5 cat /dev/ttyUSB0 | xxd
```

## 🐛 Troubleshooting

### No Connection to ser2net

```bash
# On the Raspberry Pi
sudo systemctl status ser2net
sudo netstat -tulpn | grep 3000

# Test from Home Assistant (replace IP with yours)
telnet 192.168.1.100 3000
```

### No MQTT Data

1. Check the add-on logs
2. Check MQTT integration: **Settings** → **Devices & Services** → **MQTT**
3. Check Mosquitto logs

### Sensors Not Appearing

1. Enable `mqtt_discovery: true`
2. Check discovery messages: **Developer Tools** → **MQTT** → Listen to `homeassistant/#`
3. Restart the add-on

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## ✨ Acknowledgments

- Home Assistant Community
- ser2net Project
- Paho MQTT Client
- All Contributors

## 📧 Support

- **Issues:** [GitHub Issues](https://github.com/lejando/homeassistant-obis/issues)
- **Discussions:** [GitHub Discussions](https://github.com/lejando/homeassistant-obis/discussions)

## 🔗 Links

- [Home Assistant](https://www.home-assistant.io/)
- [ser2net Documentation](https://github.com/cminyard/ser2net)
- [OBIS Codes Wikipedia](https://en.wikipedia.org/wiki/OBIS)
- [D0 Protocol Specification](https://wiki.volkszaehler.org/software/obis)

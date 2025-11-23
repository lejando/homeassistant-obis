# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-23

### Added
- Initial release
- D0-Protokoll Parser für OBIS-Stromzähler
- TCP/IP Verbindung zu ser2net
- MQTT Auto-Discovery für Home Assistant
- Unterstützung für 15+ OBIS-Codes
- Konfigurierbare MQTT-Topics (auto/custom Modus)
- JSON-Export aller Werte
- Energy Dashboard Integration
- Multi-Architektur Support (amd64, aarch64, armv7, armhf, i386)
- Umfangreiche Dokumentation
- Protokoll-Erkennungs-Tool
- Diagnose-Scripts für Raspberry Pi

### Supported OBIS Codes
- 1-0:0.0.0*255 - Device ID
- 1-0:96.1.0*255 - Meter ID
- 1-0:1.8.0*255 - Total Energy Import (kWh)
- 1-0:2.8.0*255 - Total Energy Export (kWh)
- 1-0:16.7.0*255 - Total Power (W)
- 1-0:36.7.0*255 - Power L1 (W)
- 1-0:56.7.0*255 - Power L2 (W)
- 1-0:76.7.0*255 - Power L3 (W)
- 1-0:32.7.0*255 - Voltage L1 (V)
- 1-0:52.7.0*255 - Voltage L2 (V)
- 1-0:72.7.0*255 - Voltage L3 (V)
- 1-0:31.7.0*255 - Current L1 (A)
- 1-0:51.7.0*255 - Current L2 (A)
- 1-0:71.7.0*255 - Current L3 (A)
- 1-0:14.7.0*255 - Frequency (Hz)
- 1-0:96.5.0*255 - Device Status
- 0-0:96.8.0*255 - Operating Time

### Configuration Options
- TCP connection settings (host, port)
- MQTT broker configuration
- MQTT topic customization
- Auto-discovery enable/disable
- Configurable poll interval
- Adjustable log level

[1.0.0]: https://github.com/yourusername/homeassistant-obis/releases/tag/v1.0.0

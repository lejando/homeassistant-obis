# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-11-23

### Added
- Translation files for configuration UI (en.yaml, de.yaml)
  - Field descriptions appear below each configuration parameter in Home Assistant
  - Multi-language support (English and German)
  - Detailed help texts for all configuration options
  - Contextual guidance and examples for each parameter

### Improved
- Configuration UI experience in Home Assistant
- User guidance with inline help texts like professional add-ons
- Better discoverability of configuration options
- Reduced need to consult external documentation

## [1.1.0] - 2025-11-23

### Added
- Complete English translation of all documentation
- Comprehensive configuration documentation (DOCS.md)
  - Detailed parameter explanations with examples
  - Configuration examples for different use cases
  - Troubleshooting guide for common issues
  - Best practices and recommendations
- Extensive inline comments in config.yaml
  - Clear descriptions for each parameter
  - Practical examples and default values
  - How to find/test each value
- Release process documentation (.dev/RELEASE_PROCESS.md)
  - How Home Assistant detects updates
  - Step-by-step release workflow
  - Versioning best practices

### Changed
- All documentation now in English (README.md, INSTALL.md, etc.)
- Improved configuration UI experience in Home Assistant
- Enhanced user guidance for setup and configuration

### Documentation
- README.md: Fully translated to English
- INSTALL.md: Complete step-by-step guide in English
- repository.yaml: English descriptions
- obis-d0-reader/README.md: English add-on documentation
- obis-d0-reader/CHANGELOG.md: English changelog
- obis-d0-reader/DOCS.md: New comprehensive configuration guide
- obis-d0-reader/config.yaml: Enhanced with detailed comments

## [1.0.0] - 2025-11-23

### Added
- Initial release
- Updated to paho-mqtt 2.x for future compatibility
- D0 protocol parser for OBIS electricity meters
- TCP/IP connection to ser2net
- MQTT Auto-Discovery for Home Assistant
- Support for 15+ OBIS codes
- Configurable MQTT topics (auto/custom mode)
- JSON export of all values
- Energy Dashboard integration
- Multi-architecture support (amd64, aarch64, armv7, armhf, i386)
- Comprehensive documentation
- Protocol detection tool
- Diagnostic scripts for Raspberry Pi

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

[1.1.1]: https://github.com/lejando/homeassistant-obis/releases/tag/v1.1.1
[1.1.0]: https://github.com/lejando/homeassistant-obis/releases/tag/v1.1.0
[1.0.0]: https://github.com/lejando/homeassistant-obis/releases/tag/v1.0.0

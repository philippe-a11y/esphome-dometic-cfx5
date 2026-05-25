# esphome-dometic-cfx5

ESPHome external component for integrating the **Dometic CFX5 portable fridge/freezer** into Home Assistant via BLE (Bluetooth Low Energy).

Reverse engineered from BLE HCI snoop logs. The component communicates using Dometic's proprietary DDM protocol over GATT notifications.

## Hardware

- **ESP32-S3** (or any ESP32 with BLE support), framework: `esp-idf`
- Optionally an **INA226** current sensor on the 12V supply line (I²C, address `0x40`) for power monitoring

## Features

| Entity | Type | Description |
|---|---|---|
| CFX Kühlbox | Climate | Current + target temperature, on/off control |
| CFX Tür offen | Binary sensor | Door open/closed state |
| CFX Tür-Alarm | Binary sensor | Door open > 3 min alarm |
| CFX Batteriespannung | Sensor | Battery/supply voltage (V) |
| CFX Ist-Temperatur | Sensor | Measured compartment temperature (°C) |
| CFX Firmware | Text sensor | Firmware version string |
| CFX Stromquelle | Text sensor | Power source: AC or DC |
| CFX5 Re-Pair | Button | Clear BLE bond and reboot |
| Kühlbox Strom | Sensor | DC current draw (INA226) |
| Kühlbox Leistung | Sensor | Calculated power in Watts |

## Installation

Add to your ESPHome YAML:

```yaml
external_components:
  - source: github://YOURNAME/esphome-dometic-cfx
    components: [dometic_cfx_ble]
```

See [`example/fridgepower.yaml`](example/fridgepower.yaml) for a full working configuration.

## BLE Pairing

The CFX5 uses BLE bonding (encrypted connection). On first connect the ESP32 will bond automatically. The bond is stored in NVS and survives OTA updates.

If pairing fails or the fridge forgets the bond, press the **CFX5 Re-Pair** button in Home Assistant to clear the bond and reboot.

> **Note:** Flashing with `erase_flash` will delete the bond. Use OTA for updates to preserve it.

## Protocol

The CFX5 uses Dometic's DDM protocol over BLE GATT:

| | UUID |
|---|---|
| Service | `537a0400-0995-481f-926c-1604e23fd515` |
| Write | `537a0401-0995-481f-926c-1604e23fd515` |
| Notify | `537a0402-0995-481f-926c-1604e23fd515` |

Message format:
- **Subscribe:** `0x12 p1 p2 p3 p4`
- **Publish (CFX → ESP):** `0x10 p1 p2 p3 p4 <value...>`
- **Set (ESP → CFX):** `0x11 p1 p2 p3 p4 <value...>`

Temperatures and voltages are encoded as `int32 LE / 1000`.

### Confirmed Parameters (Group `0x1A`)

| Param | Description |
|---|---|
| `04 00 00 1A` | Measured temperature |
| `05 00 00 1A` | Set temperature |
| `03 00 00 1A` | Compressor running |
| `0B 00 00 1A` | Compartment power (on/off) |
| `07 00 00 1A` | Door open |
| `10 00 00 1A` | Power source (0=AC, 1=DC) |
| `0C 00 00 1A` | Battery voltage |
| `12 00 00 1A` | Door alert (non-empty = alarm active) |

## Tested With

- Dometic CFX5 25 (firmware 1.0.1, model MC1)
- ESP32-S3 DevKitC-1

## License

MIT

# esphome-dometic-cfx5

ESPHome external component for integrating **Dometic CFX5** portable
fridge/freezers into Home Assistant over BLE (Bluetooth Low Energy).

Reverse engineered from BLE HCI snoop logs and the official Mobile Cooling
app. The component speaks Dometic's proprietary DDM2 protocol over GATT
notifications - no cloud, no WiFi setup, everything runs locally on an ESP32.

## Hardware

- **ESP32-S3** (or any ESP32 with BLE), framework: `esp-idf`
- Optionally an **INA226** current sensor on the 12 V supply line
  (I²C, address `0x40`) for external power monitoring

## Supported models

All CFX5 models share firmware family **MC1** and the same BLE service, so
the protocol is identical across the range. Support status reflects what has
actually been verified on hardware:

| Model | SKU | Type | Status |
|---|---|---|---|
| CFX5 25 | 9620015957 | Single zone | ✅ Tested (dev's own box) |
| CFX5 35 | 9620015958 | Single zone | ✅ Tested (via fork) |
| CFX5 45 | 9620015959 | Single zone | 🔮 Expected to work |
| CFX5 55 | 9620015960 | Single zone | 🔮 Expected to work |
| CFX5 55IM | 9620015961 | Single zone + ice maker | 🧪 Experimental (SZI, untested) |
| CFX5 75DZ | 9620015962 | Dual zone | 🧪 Experimental (DZ, untested) |
| CFX5 95DZ | 9620015963 | Dual zone | 🧪 Experimental (DZ, untested) |

**Single-zone models are the tested, recommended path.** Dual-zone (DZ) and
ice-maker (SZI) support is implemented from the reverse-engineered reference
protocol but has **not** been verified on real hardware yet - see
[Dual zone & ice maker](#dual-zone--ice-maker-experimental) below. If you own
a DZ or SZI box, testing and feedback are very welcome.

## Features

| Entity | Type | Description |
|---|---|---|
| Climate | Climate | Measured + target temperature, on/off |
| Door open | Binary sensor | Door open/closed |
| Door alert | Binary sensor | Door-open-too-long alarm |
| Temperature alert | Binary sensor | Temperature-out-of-band alarm |
| Measured temperature | Sensor | Compartment temperature (°C) |
| Battery voltage | Sensor | Supply voltage (V) |
| Current (internal) | Sensor | Current draw reported by the box (A) |
| Battery protection | Text sensor | DC cut-off level (Low/Medium/High) |
| Battery protection | Select | Set the DC cut-off level |
| Firmware | Text sensor | Firmware version |
| Power source | Text sensor | AC / DC / Solar |
| Model / family / exact model | Text sensors | See [Model detection](#model-detection) |
| Serial number, SKU | Text sensors | Device identity |
| Re-Pair | Button | Clear BLE bond and reboot |
| Current / Power (INA226) | Sensor | External power monitoring (optional) |

## Installation

```yaml
external_components:
  - source: github://philippe-a11y/esphome-dometic-cfx5
    components: [dometic_cfx_ble]
```

See [`example/fridgepower.yaml`](example/fridgepower.yaml) for a full working
configuration.

## Model detection

The exact model name is resolved entirely on-device, in three tiers:

1. **CMS SKU → name table.** The box reports its CMS SKU (e.g.
   `9620015957`), which maps to Dometic's exact marketing name
   (`CFX5 25`) via a built-in table - offline, no cloud.
2. **On-device product name.** If the SKU is unknown, the box's own product
   name string is used (e.g. `CFX525`).
3. **Derived name.** As a last resort, family + product type
   (`CFX5 Single Zone`) derived from the firmware model code.

### The `0x1C` product-info class

Most of the readable data lives in DDM2 class `0x1A` (realtime state). The
exact model name and CMS SKU, however, live in a **separate `0x1C` class**
that - as far as we know - no other CFX integration reads. Probing it was a
hardware-verified discovery in this project:

| Param | Content | Example |
|---|---|---|
| `01 00 00 1C` | Exact product name | `CFX525` |
| `03 00 00 1C` | CMS SKU | `97000050759` |

This is why the component can report the precise model locally, without the
cloud lookup the official app relies on.

## Dual zone & ice maker (experimental)

Set `product_type` on the hub to match your box:

```yaml
dometic_cfx_ble:
  id: dometic_cfx_ble1
  ble_client_id: cfx_ble_client
  product_type: SZ   # SZ (default) | SZI | DZ
```

- **SZ** - single zone. Tested, recommended.
- **SZI** - single zone + ice maker. Adds an `ICEMAKER_POWER` switch.
  Low-risk but untested.
- **DZ** - dual zone. On dual-zone boxes the compartment values arrive as
  a 2-element array; the component reads compartment 1 from the same frame
  and, when writing, rebuilds the full array so the other zone is preserved
  (mirroring the reference implementation). To expose the second zone, add a
  climate entity with `compartment: 1` and the matching `COMPARTMENT_1_*`
  entities.

> ⚠️ **DZ and SZI are unverified on real hardware.** The single-zone path is
> byte-identical to the tested code and unaffected. If you own a CFX5 75DZ,
> 95DZ or 55IM, please open an issue with your results.

## Connection behavior

The component subscribes once after connecting; all parameters then arrive as
push updates. An earlier version re-subscribed periodically, which could
trigger a "communication error" on the cooler after extended runtime - do not
reintroduce polling loops.

## BLE pairing

The CFX5 uses BLE bonding (encrypted connection). On first connect the ESP32
bonds automatically; the bond is stored in NVS and survives OTA updates.

If pairing fails or the fridge forgets the bond, press the **Re-Pair** button
to clear the bond and reboot.

> **Note:** flashing with `erase_flash` deletes the bond. Use OTA to preserve
> it.

### A note on Home Assistant's built-in Bluetooth

Connecting the CFX5 directly to Home Assistant's own Bluetooth (BlueZ) stack
is unreliable: the bond is lost across restarts and the box disconnects. This
is a BlueZ/kernel-level limitation, not a fault of this component - the same
issue is documented independently by other Dometic projects. Using an ESP32
with this ESPHome component (ESP-IDF's NimBLE stack) sidesteps it entirely.

## Protocol

| | UUID |
|---|---|
| Service | `537a0400-0995-481f-926c-1604e23fd515` |
| Write | `537a0401-0995-481f-926c-1604e23fd515` |
| Notify | `537a0402-0995-481f-926c-1604e23fd515` |

Message format:
- **Subscribe:** `0x12 p1 p2 p3 p4`
- **Publish (CFX → ESP):** `0x10 p1 p2 p3 p4 <value...>`
- **Set (ESP → CFX):** `0x11 p1 p2 p3 p4 <value...>`

Temperatures, voltages and currents are `int32 LE / 1000`. On dual-zone
boxes the compartment parameters carry one `int32` per compartment.

### Confirmed parameters (class `0x1A`)

| Param | Description |
|---|---|
| `04 00 00 1A` | Measured temperature (array on DZ) |
| `05 00 00 1A` | Set temperature (array on DZ) |
| `03 00 00 1A` | Compressor / cooler power |
| `0B 00 00 1A` | Compartment power (array on DZ) |
| `07 00 00 1A` | Door open (array on DZ) |
| `0C 00 00 1A` | Battery voltage |
| `0D 00 00 1A` | Battery protection level (0/1/2) |
| `0F 00 00 1A` | Current draw (signed) |
| `10 00 00 1A` | Power source (0=AC, 1=DC, 2=Solar) |
| `11 00 00 1A` | Ice maker power (SZI) |
| `12 00 00 1A` | Error/alert array (uint16 codes; 23=door, 27=temp) |
| `13 00 00 1A` | Serial number |
| `14 00 00 1A` | SKU / article number |

### Product-info parameters (class `0x1C`)

| Param | Description |
|---|---|
| `01 00 00 1C` | Exact product name |
| `03 00 00 1C` | CMS SKU |

## Tested with

- Dometic CFX5 25 (firmware 1.0.1, model MC1) - the developer's own box
- Dometic CFX5 35 (firmware 2.0.0) - via a community fork
- ESP32-S3 DevKitC-1

## Related projects

- **andrewbackway/esphome-dometic_cfx_ble** - similar ESPHome component for
  earlier CFX families; uses service `537a0300` (does not cover CFX5).
- **JS-DE-Tech/hacs-dometic-cfx3** - CFX3 over WiFi/TCP (needs WiFi set up
  via the app first).
- **prebsit/dometic-fjx7-ha** - Dometic FJX7 air conditioner (not a fridge);
  independently documents the same BlueZ incompatibility.

## License

MIT

# KiCad Module Libraries — vehicle-platform

Source: `vehicle-defs/docs/hardware-procurement-list.md` v2.8 (Part 1–5, D-082 Board C1/C2). Generator script: `_generator/` (`python3 _generator/build.py [output folder]`, default = this folder; `python3 _generator/check.py` validates the result). The libraries are generated files: edit `_generator/modules.py`, not the `.kicad_sym` / `.kicad_mod` files.

Every module is a **KiCad symbol + footprint pair**: a symbol with its real name and pins in the schematic (its `Footprint` property is `moto-<x>:<MODULE>`), and a board-sized footprint (pads + mounting holes, origin at the board centre, board outline on `F.Fab` and `F.CrtYd`). STEP models are not referenced by the footprints; they are attached later in the footprint editor (3D Models tab).

Passives (TVS, 1N5822, resistor, capacitor, Zener), DIP ICs such as 74HC14/74HC123/74AHCT125 and the single PC817 (DIP-4), and enclosures/cable glands/cables are not in this list. They come from KiCad's standard libraries (`Device`, `74xx`, `Diode`, `Connector_*`) or from mechanical assembly (FreeCAD).

## Installation

1. In KiCad (Schematic Editor or Project Manager): **Preferences → Manage Symbol Libraries** → *Project Specific Libraries* tab → add each `moto-<x>.kicad_sym` with nickname `moto-<x>` (`moto-core`, `moto-anomaly`, `moto-safety`, `moto-hud`, `moto-edge-hil`).
2. **Preferences → Manage Footprint Libraries** → *Project Specific Libraries* → add each `moto-<x>.pretty` folder with the same nickname `moto-<x>`. The symbols' `Footprint` fields (`moto-core:NUCLEO-H755ZI-Q` etc.) then resolve automatically.
3. In the schematic **Add Symbol** (`A`) → pick `moto-<x>` → module. Passives and 74xx parts come from KiCad's standard libraries.
4. 3D attachment: open the footprint in the Footprint Editor → **Footprint Properties → 3D Models** tab → add the STEP file → align it with the footprint's pads (pin 1 = **square pad**) → save. STEP exchange with FreeCAD goes through the KiCad StepUp workbench.

> Large boards (Nucleo-144) are drawn as a multi-unit symbol with **one unit per connector** (CN7, CN8 …). Pins with the same name (`GND`) appear several times with distinct pin numbers. Pad names are `<header>-<n>` (e.g. `CN11-5`), and the symbol pin number is the same string. Pin electrical types: `power_in` for supply/GND pins, `no_connect` for `NC`, `bidirectional` otherwise.

## Verification — compare the board with calipers

On hobby modules the pin order and header position vary by seller. Values with **Confidence: Low** are approximate; they must be measured before moving to a PCB. All of them are usable for the schematic (the pin names come out correct); the real risk is in the footprint positions.

Check order: (1) board outer dimensions, (2) pin 1 position and pin order (silkscreen on the board), (3) header distance to the edge, (4) mounting hole positions and diameter.

## `moto-core` (`moto-core.kicad_sym` + `moto-core.pretty`) — Part 1 - Main controller, power chain, CAN, GPS/IMU, OBD2

| Module | Board (mm) | Confidence | STEP from | Note |
|---|---|---|---|---|
| NUCLEO-H755ZI-Q | 70.0 × 133.34 | Low | NUCLEO-H755ZI-Q STEP (st.com > CAD resources) / GrabCAD 'Nucleo-144' | Pin names as connector-pin (CN11-1..). Signal names must be filled in from the UM2408 'ST morpho' and 'ZIO' tables. Header X/Y positions are approximate: verify against ST's mechanical drawing (MB1363). |
| ESP32-S3-DEVKITC-1 | 28.0 × 69.0 | High | Espressif ESP32-S3-DevKitC-1 STEP (GrabCAD / espressif KiCad lib) | On clone boards the width varies between 25.5-28 mm; the row spacing (22.86) is fixed. |
| SN65HVD230-MODULE | 27.0 × 11.0 | Medium | GrabCAD 'SN65HVD230 module' | — |
| LM2596HVS-MODULE | 43.0 × 21.0 | Medium | models/hardware-integration/cad-exports/lm2596_buck_module (existing) / GrabCAD 'LM2596 module' | Pad positions from the 'blue LM2596' clone board. HVS boards are the same size. HW-788 has a different size/pinout: a separate part if bought. |
| INA226-MODULE | 20.5 × 19.4 | Medium | GrabCAD 'INA226 CJMCU' | — |
| MICROSD-MODULE-SPI | 24.0 × 42.0 | Medium | GrabCAD 'micro SD card module catalex' | — |
| NEO-M8N-GPS-MODULE | 26.0 × 36.0 | Low | GrabCAD 'GY-NEO-M8N' | Pin order varies by board (VCC/GND/TX/RX/PPS). Check against the silkscreen on your board. |
| MPU6500-MODULE | 15.0 × 25.0 | Medium | GrabCAD 'GY-6500' / 'GY-521' (same form) | — |
| OBD2-J1962 | 40.0 × 18.0 | High | GrabCAD 'OBD2 J1962 female connector' | CL250 DLC (4/6-pin) pinout is CONFIRM in hardware-integration §1; this device is the 16-pin end of the adapter. |

## `moto-anomaly` (`moto-anomaly.kicad_sym` + `moto-anomaly.pretty`) — Part 2 - Anomaly / master mechanic sensors

| Module | Board (mm) | Confidence | STEP from | Note |
|---|---|---|---|---|
| INMP441-MODULE | 14.0 × 14.0 | Medium | GrabCAD 'INMP441' | — |
| BME280-MODULE | 15.0 × 12.0 | Medium | GrabCAD 'GY-BME280' | — |
| ADXL345-GY291 | 20.0 × 16.0 | Medium | GrabCAD 'GY-291 ADXL345' | — |
| MAX31856-MODULE | 20.0 × 25.0 | Low | GrabCAD 'MAX31856 breakout' | Generic clone pin order; the Adafruit board has extra VIN/3Vo pins. |
| ACS758-200B-MODULE | 38.0 × 30.0 | Low | GrabCAD 'ACS758 module' | — |
| MLX90614-GY906 | 11.0 × 17.0 | Medium | GrabCAD 'GY-906 MLX90614' | — |
| LJ12A3-4-Z-BX | 12.5 × 6.0 | High | GrabCAD 'LJ12A3-4-Z/BX' (M12x60 body) | 12V output -> 3.3V level shifting on Board B. |
| PC817-4CH-MODULE | 48.0 × 41.0 | Low | GrabCAD 'PC817 4 channel optocoupler module' | Input/output terminal order varies by manufacturer; always check on the board. |
| VL53L1X-TOF400C | 25.0 × 13.0 | Medium | GrabCAD 'VL53L1X module' | — |
| AS5600-MODULE | 23.0 × 23.0 | Medium | GrabCAD 'AS5600 magnetic encoder module' | — |

## `moto-safety` (`moto-safety.kicad_sym` + `moto-safety.pretty`) — Part 3 - Safety: radar, cornering LED, NFC immobilizer, GSM, camera

| Module | Board (mm) | Confidence | STEP from | Note |
|---|---|---|---|---|
| HLK-LD2451-RADAR | 35.0 × 18.0 | Low | hlktech.net LD2451 3D / GrabCAD | Pin pitch and order must be verified from the datasheet (there may be a 1.25 mm connector variant). |
| WS2812B-RING-12 | 37.0 × 37.0 | Medium | GrabCAD 'NeoPixel ring 12' | — |
| PN532-NFC-MODULE | 43.0 × 41.0 | Medium | GrabCAD 'PN532 NFC module V3' | — |
| LATCHING-RELAY-2COIL | 29.0 × 12.7 | Low | Manufacturer STEP (Hongfa HFE20 / Omron G6AK etc. depending on the selected model) | Generic DIP layout; correct the pad positions per the datasheet of the selected relay model. |
| SIM800L-MODULE | 25.0 × 23.0 | Medium | GrabCAD 'SIM800L module' | — |
| PI-CAMERA-MODULE-3 | 25.0 × 24.0 | High | raspberrypi.com Camera Module 3 STEP | — |

## `moto-hud` (`moto-hud.kicad_sym` + `moto-hud.pretty`) — Part 4 - Helmet HUD and audio unit

| Module | Board (mm) | Confidence | STEP from | Note |
|---|---|---|---|---|
| SSD1306-OLED-096-I2C | 27.0 × 27.0 | Medium | GrabCAD 'SSD1306 0.96 OLED' | — |
| MICRO-OLED-049-I2C | 15.0 × 13.0 | Low | GrabCAD '0.49 OLED 64x32' | — |
| MAX98357A-MODULE | 18.0 × 19.0 | Medium | GrabCAD 'MAX98357A breakout' | — |
| TP4056-TYPEC-PROT | 26.0 × 17.0 | Medium | GrabCAD 'TP4056 type-c module' | — |
| LIPO-1S-JSTPH2 | 8.0 × 6.0 | High | Battery: 50x34x8 box model / JST-PH 2P STEP | — |
| SPEAKER-8R-2P | 6.0 × 4.0 | High | GrabCAD '28mm speaker' | — |

## `moto-edge-hil` (`moto-edge-hil.kicad_sym` + `moto-edge-hil.pretty`) — Part 5 - Raspberry Pi 5 edge unit and HIL bench

| Module | Board (mm) | Confidence | STEP from | Note |
|---|---|---|---|---|
| RASPBERRY-PI-5 | 85.0 × 56.0 | High | raspberrypi.com Pi 5 STEP (datasheets.raspberrypi.com) | — |
| MCP2515-TJA1050-MODULE | 40.0 × 28.0 | Medium | GrabCAD 'MCP2515 CAN module' | J1 jumper = 120R termination. |
| HCW-P715-BUCK-5V5A | 54.0 × 29.0 | Low | GrabCAD '5V 5A buck module' | — |
| NUCLEO-F446RE | 70.0 × 82.5 | Medium | st.com NUCLEO-F446RE STEP / GrabCAD 'Nucleo-64' | Arduino headers (CN5/6/8/9) were not added because they carry the same signals as morpho. X/Y approximate. |
| STM32F103-BLUEPILL | 22.8 × 53.0 | High | GrabCAD 'STM32 Blue Pill' | — |
| ARDUINO-NANO | 18.0 × 45.0 | High | arduino.cc Nano STEP | — |
| MCP4725-DAC-MODULE | 18.0 × 21.0 | Medium | GrabCAD 'MCP4725 module' | — |

## Known gaps

- **NUCLEO-H755ZI-Q:** the pins were named as connector pins (`CN11-1` …). You need to enter the signal names (PA0, PB7 …) from the *ST morpho* and *ZIO* tables in UM2408. The header positions are also approximate: they should be corrected with ST's mechanical drawing (MB1363). Once the pins you will use are known, we can fill in this table together.
- **Honda DLC (4/6-pin):** the pinout is still CONFIRM in `hardware-integration §1`. The library has only the J1962 16-pin end of the adapter.
- **Latching relay:** generic because the model has not been selected. Once the model is clear, the pads must be updated per the datasheet.
- **Pi Camera 3 → Pi 5:** the camera is 15-pin and the Pi 5 is 22-pin CSI. An adapter cable is needed in between.
- **MCP2515 (TJA1050, 5V) + Pi 5 (3.3V):** pay attention to level compatibility on the SO line.

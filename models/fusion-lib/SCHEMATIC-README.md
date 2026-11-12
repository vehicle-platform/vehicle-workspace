# Circuit Schematic Setup Guide — vehicle-platform (Fusion)

**Version:** 1.3 — 2026-10-29 (cross-check: `hardware-integration.md`, `hardware-procurement-list.md` v2.8, `fusion-lib/README.md`, `DECISIONS.md` D-044, D-072, D-073, D-075, D-076, D-082, Q-031, Q-032, Q-033, Q-034). 1.2 → 1.3: English translation, no content change. Difference from 1.1: D-082 Board C1/C2 split and circuit rules, BOM notes per v2.6–v2.8, input capacitor ≥ 50 V.
**Priority order:** `DECISIONS.md` > `ARCHITECTURE.md` > `hardware-integration.md` > this file.
**Libraries:** the `moto-*.lbr` files in the same folder (installation: `README.md`). Parts that are not modules come from Fusion's own libraries: passives, diodes, 74HC14 / 74HC123 / 74AHCT125 (74xx library, DIP-14/16), single PC817 (DIP-4 optocoupler), MOSFETs and connectors.

> **Rule:** Pins marked **CONFIRM** or **TBD** in the documents are not drawn in the schematic on a guess; they are left as a net label only and connected once the pin is settled. Values marked **Proposal** in this file (divider resistor, driver transistor, etc.) are not a decision, only a starting value. They are checked before being put into the circuit and written into the relevant decision file.

---

## 1. Schematic files and sheet plan

| Design | Sheets | Content | Section |
|---|---|---|---|
| **`moto-bike-p0`** (now) | 1 | Phase 0: ESP32-S3 + SN65HVD230 + MPU-6500 + NEO-M8N + power chain + DLC | §3 |
| **`moto-bike`** (W1→W5) | S1 Power · S2 M7 (CAN, logging, GPS, park) · S3 Anomaly (Board B) · S4 M4 safety (Board C1) + M7 chassis IMU (Board C2) · S5 Pi 5 | H755 architecture (D-072) | §4 |
| **`moto-helmet`** (W3) | 1 | Helmet ESP32-S3 HUD + audio (D-073) | §5 |
| **`moto-hil`** (W6) | 1 | HIL bench (not on the vehicle) | §6 |

### Sheet → reference figures (`moto-bike`)

The figures in `vehicle-defs/docs/img/hardware/` are the reference for each sheet; `vehicle-defs/docs/hardware-integration.md` §0 indexes them. Sheets are mapped by content, following the sheet definitions above (S3 is the Board B anomaly sheet, S4 holds the M4 board C1 and the M7 chassis IMU board C2).

| Sheet | Reference figures | Files (`vehicle-defs/docs/img/hardware/`) |
|---|---|---|
| S1 Power (Board A) | Fig. 02 power chain | `02-power-chain.svg` |
| S2 M7 (CAN, logging, GPS, park) | Fig. 04 H755 pin map, Fig. 05 CAN topology, Fig. 03 Main Box | `04-h755-pin-map.svg`, `05-can-topology.svg`, `03-main-box-layout.svg` |
| S3 Anomaly (Board B) | Fig. 03 Main Box (Board B placement), Fig. 13 harness rules | `03-main-box-layout.svg`, `13-harness.svg` |
| S4 M4 safety (C1) + M7 chassis IMU (C2) | Fig. 04 pin map (M4 side), Fig. 07 IMU boxes, Fig. 09 immobilizer, Fig. 10 LED ring and dead-man | `04-h755-pin-map.svg`, `07-imu-boxes.svg`, `09-immobilizer.svg`, `10-led-ring-deadman.svg` |
| S5 Raspberry Pi 5 | Fig. 11 Pi 5 box | `11-pi5-box.svg` |

**License note:** Fusion's personal/free licence has a schematic sheet limit (usually 2 sheets; check under your own licence). If you hit the limit, put the `moto-bike` design on a single sheet and draw each subsystem inside its own frame. Connections between frames are made by net labels with the same name.

---

## 2. Net naming rule

Labels with the same name are merged automatically in Fusion, so the names must be written **exactly** as in the table. `UART_x_TX` is always the **MCU's TX** pin and goes to the module's RX.

| Group | Net names | Owner / note |
|---|---|---|
| Power | `+12V_IGN` (raw after ignition) · `+12V_PROT` (after fuse, diode, TVS and LC) · `+5V` · `+5V_PI` · `+3V3` · `+3V3_C1` · `+3V3_C2` (C1/C2 LDO branches, D-082) · `+4V0_GSM` (later) · `GND` · `AGND` | Ground goes to the battery negative, not to the chassis. `AGND` connects to `GND` at a single point (S1) |
| Vehicle CAN | `VCAN_H` · `VCAN_L` | M7 FDCAN1. **No termination resistor** |
| Platform CAN | `PCAN_H` · `PCAN_L` | M7 FDCAN2, bike ESP32, Pi 5, HIL. 120 Ω only at the two physical ends of the bus |
| Measurement (M7) | `V_BAT_SENSE` · `I_BAT_SENSE` · `SPARK_IN` · `WHEEL_F` · `WHEEL_R` · `NTC_1..n` · `GPS_PPS` | `GPS_PPS`: NEO-M8N timepulse → M7 timer input capture (sub-ms timestamp alignment, Part 2A) |
| Bus (M7) | `I2C_M7_SDA/SCL` · `SPI_M7_SCK/MOSI/MISO` + `CS_*` · `UART_GPS_TX/RX` · `UART_GSM_TX/RX` | Pins TBD (§7) |
| Bus (M4) | `SPI_M4_SCK/MOSI/MISO/CS_IMU` · `UART_RAD_L_TX/RX` · `UART_RAD_R_TX/RX` · `I2C_M4_SDA/SCL` (if PN532 I2C is chosen) | GPIO port belonging to M4, not shared with M7 (D-072 item 4a) |
| Output (M4) | `LED_RING_L_DIN` · `LED_RING_R_DIN` · `MIRROR_LED_L` · `MIRROR_LED_R` · `DEADMAN_KICK` · `IMMO_SET` · `IMMO_RESET` | D-072 items 3 and 5 |
| Input (M4) | `IND_L` · `IND_R` | Left and right turn-signal supply, opto-isolated (D-075 item 4, Q-033 provisional answer (a)) |
| Tap (M7, read-only) | `TAP_CLUTCH` · `TAP_BRAKE` · `TAP_FAN` | Isolated with PC817. **Not connected before the Q-031 (c) decision** |
| I2S (Pi 5) | `I2S_SCK` · `I2S_WS` · `I2S_SD` | Engine microphone INMP441 → Pi 5 (D-044) |

---

## 3. Phase 0 schematic — `moto-bike-p0` (pins documented)

Source: `hardware-integration.md` §1, §3.

**Power chain** (draw from left to right):
```
+12V_IGN ─ 2A fuse ─ 1N5822 (series, reverse polarity) ─ SMBJ30CA TVS (bidirectional, to GND)
        ─ L1 (LC filter inductor, value TBD) ─ 470µF/50V ∥ 100nF ─ = +12V_PROT ─ LM2596HVS IN+/IN-
LM2596HVS OUT+ (set to 5.0 V) ─ +5V ─ ESP32-S3 5V pin            (IN-/OUT- → GND)
```

- **Capacitor voltage:** the SMBJ30CA starts conducting at 33.3–36.8 V and clamps to 48.4 V at the peak pulse, so the electrolytic on `+12V_PROT` must be **at least 50 V** (63 V preferred). 35 V is not enough.
- **1N5822 (40 V):** because it sits behind the TVS diode, it does not limit the reverse voltage that a negative pulse at the input puts on the diode. A 60 V, ≥ 3 A Schottky (SS36 / SB360 class) is a cheap margin (**Proposal**).
- **Buck module:** the library only has `LM2596HVS-MODULE` (43×21 mm). If the HW-788 in stock is bought, its dimensions and pin layout are different; draw whichever was bought (use a generic 4-pin part for the HW-788).

| Source | Pin | → | Target | Pin | Note |
|---|---|---|---|---|---|
| ESP32-S3 | IO4 (TWAI TX) | → | SN65HVD230 | CTX | |
| ESP32-S3 | IO5 (TWAI RX) | ← | SN65HVD230 | CRX | |
| ESP32-S3 | 3V3 | → | SN65HVD230 | 3V3 | **Remove** the on-board 120 Ω if present (CONFIRM) |
| SN65HVD230 | CANH / CANL | → | OBD2-J1962 | 6_CAN_H / 14_CAN_L | Twisted pair, < 50 cm |
| OBD2-J1962 | 4_CGND, 5_SGND | → | GND | | DLC 4/6-pin side **CONFIRM** |
| ESP32-S3 | IO7 | ↔ | MPU-6500 | SDA/SDI | I2C 400 kHz, 0x68 |
| ESP32-S3 | IO6 | → | MPU-6500 | SCL/SCLK | |
| MPU-6500 | AD0/SDO | → | GND | | For the 0x68 address |
| ESP32-S3 | IO15 (UART1 RX) | ← | NEO-M8N | TX | Pins **CONFIRM** (§7.3) |
| ESP32-S3 | IO16 (UART1 TX) | → | NEO-M8N | RX | The module's UART must be 3.3 V |
| NEO-M8N | PPS | | (empty) | | PPS is not documented as connected in Phase 0. `GPS_PPS` is on M7 in the target architecture (§4 S2) |
| ESP32-S3 | IO8 | → | TP | | loop() pulse output (scope) |
| ESP32-S3 | IO17 / IO18 | | (empty) | | Nextion UART2, later |

---

## 4. Target schematic — `moto-bike` (H755, D-072)

### S1 — Power (Board A)

**Chain:** as in §3, `+12V_IGN` → fuse → 1N5822 → SMBJ30CA → **L1** (value TBD) → 470 µF/50 V ∥ 100 nF → `+12V_PROT` → LM2596HVS (or HW-788) → `+5V`.

- **C1 and C2 branches:** two separate fuses + two separate LDOs from `+12V_PROT` (`+3V3_C1`, `+3V3_C2`), separate connectors (S4, D-082 item 2).

- `INA226 #1`, high side: the `+5V` line passes between IN+ → IN−; VBS connects to `+5V`. I2C `I2C_M7_*`, address 0x40.
- **Pi 5 branch:** `+12V_PROT` → HCW-P715 → `+5V_PI` (to S5). The Pi is **not powered** from the LM2596.
- **Battery measurement:** `+12V_PROT` → 100 kΩ → node → 22 kΩ → `AGND`. Connect 10 nF and BZX55C3V3 to the node (both to `AGND`); the node becomes `V_BAT_SENSE` and goes to the M7 ADC (1 kHz DMA).

**`+3V3` source — decision pending (TBD):**

| Option | What | Pro / con |
|---|---|---|
| (a) Nucleo's 3V3 output | On-board regulator | No extra part. But how much current it can supply to external sensors must be **CONFIRM**ed from UM2408. If a short circuit occurs on a long sensor cable, the MCU supply collapses too |
| (b) Separate 3.3 V LDO on Board A (`+5V` input) | Separate rail for external sensors | The MCU supply is isolated from a sensor short. The LDO and PTCs are in the procurement list (Part 1, v2.6, only if (b) is chosen) |

**Proposal:** (b). Also put a series PTC or a low-value resistor on the `+3V3` end of every sensor cable that leaves the enclosure. The current budget (number of sensors × typical current) must be calculated during the decision.

**`AGND` ↔ `GND` tie:** two separate nets in Fusion. So that `AGND` does not float, it is connected to `GND` at the H755 analogue reference point with a **single** 0 Ω resistor (net-tie / star connection). It is not tied anywhere else. Whether the Nucleo board's AGND pin is already connected to GND on the board must be **CONFIRM**ed from UM2408. If it is, that is the star point and no external 0 Ω is fitted.

**Harness EMI (not in the schematic, in the BOM and assembly):** clip-on ferrite cores (5–7 mm) on the CAN, SPI (ADXL345), camera and 12 V cables, just outside the PG7 cable glands of the main enclosure and the Pi enclosure. These are not schematic elements. Write a note (text) on the schematic sheet and add them to the BOM manually as mechanical items (§8).

### S2 — M7 rt-core: CAN, logging, GPS, park mode (Board A)

| Source | → | Target | Note |
|---|---|---|---|
| H755 FDCAN1 TX/RX (pin TBD) | → | SN65HVD230 #1 CTX/CRX | `VCAN_H/L`, no termination |
| H755 FDCAN2 TX/RX (pin TBD) | → | SN65HVD230 #2 CTX/CRX | `PCAN_H/L`, 120 Ω at the ends |
| H755 SPI / SDMMC (TBD) | → | microSD | D-072 item 2: SDMMC on M7. If the SPI module in the library does not fit SDMMC, a separate decision is needed (**TBD**) |
| H755 `UART_GPS_TX/RX` (TBD) | ↔ | NEO-M8N RX/TX | GPS on M7 (D-072 item 2) |
| NEO-M8N PPS | → | H755 timer input capture (`GPS_PPS`, TBD) | Part 2A |
| MPU-6590 (M7 chassis IMU) | ↔ | `I2C_M7_*` | 0x68, on Board C2, in its own enclosure and cable (see S4) |
| `INA226 #1` | ↔ | `I2C_M7_*` | 0x40 |
| Bike ESP32-S3 (conn) | ↔ | its own SN65HVD230 → `PCAN_H/L` | Separate enclosure (DT-0508). Leaves the vehicle bus with the `no-tester` env once the H755 arrives |
| *(optional)* WS2812B strip (gear light) | ← M7 GPIO (TBD) | Belongs to M7, procurement list Part 3A. A **separate** buffer is needed for the 5 V data level: the 74AHCT125 on C1 belongs to M4 and is not shared (D-072 item 4a) |
| **SIM800L (later, park mode)** | ↔ | `UART_GSM_TX/RX` (TBD) | Park mode belongs to M7 (D-072 item 2). Details below |

**SIM800L supply warning:** VCC must be in the **3.4–4.4 V** range and must handle a peak current of about **2 A**. It is **not connected directly** to `+5V` or `+3V3`: 5 V damages the module and at 3.3 V the module drops out. A separate `+4V0_GSM` branch is needed: its own buck regulator (≥ 2 A, set to ~4.0 V) and a large capacitor at the input (≥ 470 µF). This regulator and capacitor are in the procurement list (Part 3A, Later, only with the GSM module). UART level compatibility (whether 3.3 V can be applied to the module's RX input) must be **CONFIRM**ed from the SIM800L datasheet.

### S3 — Anomaly sensors (Board B, Scale 1B, detachable)

| Module | Bus / signal | Note |
|---|---|---|
| ADXL345 ×2 | `SPI_M7_*`, separate `CS_ADXL_ENG` and `CS_ADXL_ARM` | LiYCY 4×0.22; shield connected to GND only on the H755 side |
| MAX31856 | `SPI_M7_*` + `CS_EGT`, DRDY/FLT → GPIO | T+/T− K-type probe |
| MLX90614 | `I2C_M7_*` | 0x5A |
| BME280 | `I2C_M7_*` | 0x76 (SDO=GND) |
| ACS758-200B | VOUT → divider → `I_BAT_SENSE` (ADC) | Divider below |
| PC817 4 channel | IN1..3 ← 12 V taps, OUT → GPIO (`TAP_*`) | **Not connected before Q-031 (c).** 4th channel spare; not used for M4's `IND_L/R` inputs (see S4) |
| LJ12A3 ×2 | BLK_OUT → level circuit → `WHEEL_F/R` (timer input) | Sensor powered from `+12V_PROT` |
| Spark clip | 1N4148 + 3.3 V Zener + 74HC14 → `SPARK_IN` | 74HC14 from Fusion's 74xx library |
| NTC ×3–5 | 10 kΩ 0.1% + 100 nF divider → ADC (`NTC_n`) | Twisted Signal+AGND pair |
| I2C pull-up | 2.2–4.7 kΩ → `+3V3` | The on-board 10 kΩ resistors are not enough on a long cable |
| *(2C, later)* VL53L1X ×2 | `I2C_M7_*` + XSHUTs on separate GPIOs | Both are 0x29 at boot; enable them one at a time with XSHUT and change the address |
| *(2C, later)* AS5600 | `I2C_M7_*` | 0x36 fixed, only one can be on the same bus |
| *(2B, optional)* Oil pressure/temperature | Interface **TBD** | Intervention in the pressurised oil gallery needs a safety decision before fitting (procurement list Part 2B) |
| *(2C, later)* Crankcase blow-by | BMP280 → `I2C_M7_*` **0x77** (SDO=VCC; BME280 at 0x76) **or** MPXV7002DP → divider → ADC | The MPXV7002DP is 5 V supplied and its output is 0.5–4.5 V, so a divider is needed as with the ACS758. There is no module for it in the library: use a generic 3-pin part (VCC, GND, VOUT) |

**Divider and level circuits (Proposal values — check before putting into the circuit):**

| Signal | Source range | Circuit | Check |
|---|---|---|---|
| `I_BAT_SENSE` (ACS758-200B, 5 V supply) | about 0.5–4.5 V at ±200 A (VCC/2 ± 10 mV/A) | VOUT → 10 kΩ → node → 20 kΩ → AGND (×0.667). 100 nF to the node; node to ADC | 4.5 V → must be 3.0 V; full scale ≤ VREF+. Sensitivity **CONFIRM** from the datasheet |
| `WHEEL_F/R` (LJ12A3 NPN) | Most are NPN-NO open collector, but some have an internal pull-up to +V | If open collector: output → 10 kΩ pull-up to `+3V3` (12 V never reaches the pin). If there is an internal pull-up: 10 kΩ series + BZX55C3V3 (to GND) clamp, or PC817 | Measure the output voltage with the sensor unloaded (no target): **CONFIRM** |
| `SPARK_IN` | Inductive pulse | 1N4148 + 3.3 V Zener + 74HC14 (Part 2B) | — |
| MPXV7002DP (later) | 0.5–4.5 V | Same ×0.667 divider as the ACS758 | — |

### S4 — M4 safety board (Board C1) and M7 chassis IMU (Board C2)

D-082 split the single Board C in two. Every peripheral and GPIO port belonging to M4 is not shared with M7 (D-072 item 4a). Draw C1 and C2 in **separate frames** in the schematic.

**Supply and separation (D-082 item 2):** each of C1-IO and C2 is supplied from `+12V_PROT` through **its own fuse**; C1-IMU's LDO (`+3V3_C1`) comes from the C1-IO branch and C2's (`+3V3_C2`) from its own branch. They have their own connectors and their own cables. C1's 5 V (LED buffer, radars, ring) comes from the buck on Board A. A fault in C2 cannot take down an M4 function. A fault in C1 takes down all M4 functions together and must appear as a dark ring / UNAVAILABLE.

**Board C1 (`4×6 cm`, M4 safety board):**

| Module | Connection | Note |
|---|---|---|
| MPU-6500 (M4 IMU) | `SPI_M4_*` | Independent of the M7 IMU (D-042, D-075 item 6 (3)). Powered from the `+3V3_C1` LDO but talks to Nucleo-powered pins: **33–100 Ω series resistor on each of the `SPI_M4_SCK/MOSI/MISO/CS_IMU` lines** (against back-powering). If the C1 LDO fails, WHO_AM_I/self-test error → UNAVAILABLE. Cable **6 or 8 core** shielded LiYCY (4×0.22 is not enough) |
| HLK-LD2451 ×2 | `UART_RAD_L_*`, `UART_RAD_R_*` (header) | Supply and UART level **CONFIRM** from the datasheet |
| WS2812B ring ×2 | `LED_RING_L/R_DIN` ← 74AHCT125 (3.3→5 V) ← M4 GPIO | 330 Ω series to DIN; 5 V supply through the dead-man (below) |
| **Mirror blind-spot LEDs (left/right)** | `MIRROR_LED_L/R` ← M4 GPIO → low-side logic-level N-MOSFET → LED + series resistor | MOSFET in the procurement list (Part 3A); its model and the resistor value are **TBD** based on the current of the selected LED. The "side clear" state is never shown with a static output (D-072 item 5) |
| Dead-man: 74HC123 + P-MOSFET | `DEADMAN_KICK` ← M4 GPIO; the P-MOSFET cuts the ring supply | If M4 hangs, GREEN does not freeze (D-072 item 5). **Mandatory** unless the moving alive-pixel method is chosen. Triggered with a GPIO edge after every completed decision step in the M4 main loop (never a timer, PWM or DMA). **Pull-down resistor on the trigger input:** a pin floating during reset cannot trigger the circuit |
| **Turn-signal inputs** | `IND_L`, `IND_R`: signal supply → PC817 → M4 GPIO | D-075 item 4: a separate opto-isolated M4 input for each side. Two single PC817s (DIP-4, Part 3A); M7's `TAP_*` module is not shared. **Input:** series resistor sized for ≥ 16 V, reverse-parallel diode across the LED. **Output:** pull-up resistor chosen according to the PC817's minimum CTR. A broken cable, a dead opto or a stuck input reads as "no signal" and can only raise the warning; it can never suppress PRESENT/APPROACHING. The tap point and how it connects to the harness are **CONFIRM** (the cable is not cut) |
| PN532 | `I2C_M4_*` (0x24) or SPI | Interface choice TBD |
| Latching relay drivers | `IMMO_SET`/`IMMO_RESET` ← driver (NPN/MOSFET + flyback diode) | **Starter relay coil only**. Default unlocked, hidden bypass switch in parallel (invariant 6). **Pull-down resistor on the gate/base:** the drivers stay off while M4 pins float; pulse-only drive. The relay keeps its position when C1 or the M4 supply is lost; M4 never sends a SET pulse at boot; a hidden bypass is needed for an M4 that dies while locked (D-082 item 6, **awaiting user approval**) |
| PIN input | M4 GPIO (TBD) | D-072 item 3; its hardware has not been selected yet |

**C1 split in two (2026-10-24, user approval, D-082 item 2):** the MPU-6500 row of the table above goes to the **C1-IMU** board (`3×7 cm`, cut to ~`30×40 mm`, in the small IP65/IP67 enclosure on the chassis; it carries only the MPU-6500, its LDO and the SPI series resistors). All the other rows go to the **C1-IO** board (`4×6 cm`, in the main enclosure, never on Board B, with its own fused branch and its own connector to the M4 pins). C1-IMU's LDO is supplied from the C1-IO branch through the C1-IMU cable (6/8 core shielded). Draw two separate frames in the schematic: `C1-IO` and `C1-IMU`. If C1-IMU or its cable fails, only the M4 IMU is lost (cornering UNAVAILABLE, shown on the ring); if C1-IO fails, its functions are lost together (dark ring / UNAVAILABLE).

**Board C2 (`3×7 cm`, cut to ~`30×40 mm`, M7 chassis IMU carrier):**

| Module | Connection | Note |
|---|---|---|
| "MPU-6590" marked board (M7 IMU, chip **CONFIRM**, WHO_AM_I) | `I2C_M7_*`, 0x68 | Owner is M7 (S2). `+3V3_C2` from its own branch, with its own cable |

**Enclosures:** C1-IMU and C2 in the same small IP65/IP67 enclosure type (product **CONFIRM**, Q-034), with short rigid 6 mm brass standoffs, each in its own enclosure, bolted to the main chassis near the centre of gravity and aligned with the motorcycle's axes. No damped plate. According to the store page, `DT-0505` / `DT-0508` in the procurement list are `126×136×48` / `126×136×54 mm` ABS enclosures and the IP class is not stated (v2.8 correction). The enclosure choice (size and sealing) is made with Q-034.

### S5 — Raspberry Pi 5

| Source | → | Target | Note |
|---|---|---|---|
| HCW-P715 OUT+ | → | `+5V_PI` → Pi 5V (GPIO pin 2/4) | 5 A |
| `INA226 #2` | | on the `+5V_PI` line | Pi I2C, 0x40 (separate bus, does not conflict with #1) |
| MCP2515 SI / SCK / CS | ← | Pi GPIO10 / GPIO11 / GPIO8 (CE0) | SPI0 |
| MCP2515 SO | → | Pi GPIO9 (MISO), **level-shifted down** | See below |
| MCP2515 INT | → | Pi GPIO25 (common overlay value, **CONFIRM** per overlay), **level-shifted down** | See below |
| MCP2515 CAN_H/L | → | `PCAN_H/L` | J1 jumper = 120 Ω; fit only at the end of the bus |
| Pi Camera 3 | → | CSI | 15→22 pin adapter cable |
| INMP441 (engine microphone) | → | `I2S_SCK` = GPIO18 (PCM_CLK) · `I2S_WS` = GPIO19 (PCM_FS) · `I2S_SD` = GPIO20 (PCM_DIN) | D-044: the engine microphone is on the Pi; the "USB or I2S" choice is open. If I2S is chosen, these pins are used. L/R → GND (left channel), VDD → Pi 3V3 |

**MCP2515 5 V → Pi 3.3 V:** these modules supply both the MCP2515 and the TJA1050 from 5 V, so the **SO and INT outputs are 5 V**. The Pi's inputs are not 5 V tolerant. Options:

| Option | Circuit | Note |
|---|---|---|
| (a) Resistor divider | SO and INT → 1 kΩ → node → 2 kΩ → GND (×0.667) | Simple. Edges slow at high SPI speed; lower the SPI clock in the overlay and switch to (b) if needed |
| (b) Unidirectional level-shifter IC | e.g. 74LVC1T45 ×2 | Fast. It is in the procurement list (Part 5A) for when (a) is not enough |
| (c) Supply the MCP2515 from 3.3 V | Cut the trace on the module; the TJA1050 stays at 5 V | Requires a board modification; **CONFIRM** per module variant |

---

## 5. `moto-helmet` (W3, D-073, `moto-hud.lbr`)

Stages: **H0** (desk, SSD1306) and **H1** (helmet, micro-OLED + prism). Pin assignments are not documented; all **TBD**. Q-032 (PTT location, audio path, battery target) is open.

**Power chain:**
```
LiPo 1S (with protection circuit) ─ JST-PH ─ TP4056 B+/B-
TP4056 OUT+ ─ slide switch ─ +VBAT_SW ─┬─ ESP32-S3 5V pin (CONFIRM, below)
                                        └─ MAX98357A VIN
TP4056 OUT- ─ GND          (charging: TP4056 Type-C input)
```
- **CONFIRM:** when the LiPo voltage (3.0–4.2 V) is applied to the DevKitC's 5V pin, can 3.3 V be maintained with the on-board LDO's dropout voltage? It must be checked from the board LDO's datasheet. If not, supply the 3V3 pin from a separate low-dropout 3.3 V LDO (procurement list Part 4, conditional).
- MAX98357A VIN is 2.5–5.5 V, can be powered directly from the battery.

**Net names:** `+VBAT`, `+VBAT_SW`, `+3V3`, `GND`, `I2C_HUD_SDA/SCL`, `I2S_MIC_SCK/WS/SD`, `I2S_AMP_BCLK/LRC/DIN`, `PTT`, `VBAT_SENSE` (optional, TBD).

| Source | → | Target | Note |
|---|---|---|---|
| ESP32-S3 (GPIO TBD) | ↔ | SSD1306 (H0) / micro-OLED (H1) SCL/SDA | `I2C_HUD_*`, 0x3C. VCC → `+3V3` |
| ESP32-S3 (GPIO TBD) | ← | INMP441 SCK/WS/SD | `I2S_MIC_*`, ESP-SR (D-047). L/R → GND. VDD → `+3V3` |
| ESP32-S3 (GPIO TBD) | → | MAX98357A BCLK/LRC/DIN | `I2S_AMP_*`. Whether the same I2S unit as the microphone or a separate one: **TBD** |
| MAX98357A SPK+/SPK- | → | 8 Ω speaker | GAIN/SD can be left at default (datasheet) |
| PTT button | → | ESP32-S3 GPIO (TBD) + internal pull-up, other end GND | Location open in Q-032 (helmet or handlebar) |
| Slide switch | | `+VBAT` ↔ `+VBAT_SW` | Main on/off |

---

## 6. `moto-hil` (W6, `moto-edge-hil.lbr`)

Not on the vehicle. The bench has its own CAN bus and **120 Ω termination at both ends**. The simulator is an F446RE; the fault/supply node is an F103 Blue Pill (D-072 items 1 and 9, Q-003). There is no STM32 board on hand; both will be bought (D-082 item 5). An Arduino Nano on hand is an alternative.

**Net names:** `HCAN_H/L` (bench CAN), `+12V_BENCH`, `+V_DUT` (programmable supply output), `+5V`, `+3V3`, `GND`, `I2C_HIL_SDA/SCL`.

| Source | → | Target | Note |
|---|---|---|---|
| NUCLEO-F446RE CAN1 TX/RX (pin TBD, CubeMX) | → | SN65HVD230 #1 CTX/CRX → `HCAN_H/L` | Restbus simulator |
| NUCLEO-F446RE USB (ST-LINK VCP) | → | i7 host | Default VCP USART2 on Nucleo-64 (PA2/PA3, UM1724) |
| Blue Pill CAN TX/RX | → | SN65HVD230 #2 → `HCAN_H/L` | Malformed frame injection. On the F103, USB and CAN share the same PA11/PA12 pins and the same SRAM; **Proposal:** move CAN to PB8/PB9 (remap), **CONFIRM** |
| Blue Pill (I2C, TBD) | ↔ | MCP4725 SCL/SDA | 0x60/0x62 (A0) |
| MCP4725 OUT | → | Programmable supply control input → `+V_DUT` | Buck + DAC circuit (5×7 perfboard). Topology TBD |
| `+V_DUT` | → | OBD2-J1962 (female) 16_BAT+ | Supply for the DUT |
| `HCAN_H/L` | → | OBD2-J1962 (female) 6_CAN_H / 14_CAN_L | The DUT connects through this socket |
| GND | → | OBD2-J1962 (female) 4_CGND, 5_SGND | |
| *(alternative)* Arduino Nano | | supply control only | There is no CAN on the Nano: if it is used instead of the Blue Pill, SN65HVD230 #2 stays unused and an MCP2515 is needed for frame injection |

---

## 7. H755 pin map — open decision

Which H755 pin goes to which function has not been written as a decision yet. Order:
1. Build S1–S5 with net labels; leave the MCU side empty.
2. Produce the pin map in STM32CubeMX. **For M7:** FDCAN1/2, SDMMC (or SPI), I2C, SPI (ADXL ×2, MAX31856), UART (GPS, GSM), ADC (V_BAT, I_BAT, NTCs), timer capture (`GPS_PPS`, `SPARK_IN`, `WHEEL_F/R`), `TAP_*` GPIOs. **For M4, on separate GPIO ports:** SPI (IMU), UART ×2 (radars), ring DIN ×2 (timer/DMA), `MIRROR_LED_L/R`, `DEADMAN_KICK`, `IND_L/R`, `IMMO_SET/RESET`, PN532, PIN input.
3. Add the map to `DECISIONS.md` as an item, then connect only the used pins on the NUCLEO-H755ZI-Q gates (CN7–CN12).

---

## 8. Board-to-board and external connectors

Every connector is placed in the schematic as a **part**. That way it enters the BOM automatically and both ends of the cable match with the same net names.

| Transition | In the schematic | In the BOM |
|---|---|---|
| Board A ↔ Board B (inside the main enclosure) | One JST-XH header part on each board (search "XH" in the Fusion library or use a 2.5 mm pin header). Same net names on the mating ends. Board B's "Scale 1B expansion port" should be a separate connector | Headers enter automatically. Female housings and terminals (JST-XH 560-piece set) are added manually |
| Main enclosure ↔ C1-IMU and ↔ Board C2 (separate enclosures); C1-IO ↔ M4 pins inside the main enclosure through its own connector | A **separate** connector part and a separate cable for each board (D-082 item 2). Type **CONFIRM** (Deutsch DT proposed). C1's SPI cable is 6/8 core shielded | Connector kit and cable added manually |
| NUCLEO ↔ Board A/B (2nd storey) | Long-pin (stacking) header part, CN7–CN10 signals | Automatic |
| Chassis sensors outside the enclosure | **Deutsch DT** (2–6 pin) part on the enclosure side. If it is not in the library, use a generic connector with the same pin count as a placeholder for now and write "Deutsch DT04-xP" in the `MPN` attribute | DT kit and crimp tool added manually |
| Power and CAN cable entries | 3.81 mm (pluggable) / 5.0 mm screw terminal part | Automatic |
| Ferrite, cable, shield, Tesa tape, spiral wrap, cable gland | **Not** in the schematic; written on the sheet as a note | Added manually from the mechanical items in the procurement list |

---

## 9. ERC and BOM checklist

- [ ] **ERC:** because all pins are of type `pass`, Fusion does not report direction errors. The real check is going through the unconnected warnings one by one.
- [ ] `AGND` and `GND` are tied at **one** point only (0 Ω net-tie or Nucleo AGND). There is no second tie, `AGND` is not floating.
- [ ] The source of `+3V3` is chosen (S1 (a)/(b)) and it comes from a single source in the schematic.
- [ ] There is no 120 Ω anywhere on the `VCAN` line (including the resistor on the SN65HVD230 board). There are exactly two on the `PCAN` and `HCAN` lines.
- [ ] No I2C address conflict: on `I2C_M7`, INA226 0x40, MPU-6590 0x68, MLX90614 0x5A, BME280 0x76, blow-by BMP280 0x77, AS5600 0x36, the VL53L1Xs separated by XSHUT.
- [ ] No 5 V output signal goes directly into a 3.3 V pin: ACS758, MPXV7002DP, MCP2515 SO and INT, LJ12A3 (if it has an internal pull-up).
- [ ] M4 signals (`SPI_M4`, `UART_RAD`, `IND_L/R`, `MIRROR_LED`, ring, dead-man, relay) are not on a GPIO port shared with M7 (D-072 item 4a).
- [ ] The `TAP_*` lines are not connected until the Q-031 (c) decision is made; they exist only as labels.
- [ ] SIM800L is not connected to `+5V`/`+3V3`; it is on the `+4V0_GSM` branch.
- [ ] On every sensor cable leaving the enclosure, the LiYCY shield is connected to GND at one end only (in the H755 enclosure).
- [ ] C1 and C2 are supplied from separate fuses + separate LDO branches; there is no M4 signal on the C2 line.
- [ ] There are 33–100 Ω series resistors on the `SPI_M4_*` lines; there are pull-downs on the 74HC123 trigger input and on the relay drivers' gate/base; there are reverse diodes on the `IND_L/R` inputs.
- [ ] The electrolytic on `+12V_PROT` is ≥ 50 V.
- [ ] Export the BOM from Fusion (**Export > BOM**) and compare it with `hardware-procurement-list.md` v2.8. The previous version's BOM gaps (L1, 3.3 V LDO, `+4V0_GSM` buck, mirror LED MOSFETs, MCP2515 level shifter, helmet LDO) entered the list with v2.6; the ones whose value is still **TBD**: L1, MOSFET model and LED resistor, LDO current budget.
- [ ] Enter every **CONFIRM/TBD** label in the schematic into the open-items table in `hardware-integration.md` §10 (items 10 and 11 collect the items of this guide).

"""Module database for moto-platform KiCad libraries.

All coordinates in mm, origin = board lower-left, board seen from TOP (component side).
Header spec:
  name, x, y        : position of pin 1
  dir               : 'h' (pins advance +x) or 'v' (pins advance +y)
  pins              : list of pin names in pad order 1..N
  rows              : 1 or 2. For 2 rows, odd pins on row A, even on row B (morpho style)
  row_off           : (dx, dy) offset of row B from row A
  pitch             : default 2.54
  drill, dia        : pad drill / copper diameter
conf: 'H' high (well-known standard), 'M' medium (common variant), 'L' low (approx., verify)
"""

P = 2.54


def hdr(name, x, y, pins, dir="h", rows=1, row_off=(0, -P), pitch=P, drill=1.0, dia=1.7, shape="round"):
    return dict(name=name, x=x, y=y, pins=pins, dir=dir, rows=rows, row_off=row_off,
                pitch=pitch, drill=drill, dia=dia, shape=shape)


def lug(name, x, y, pins, dir="h", pitch=5.0):
    """Screw-terminal / power pads (bigger drill)."""
    return hdr(name, x, y, pins, dir=dir, pitch=pitch, drill=1.3, dia=2.6)


# ------------------------------------------------------------------ pin tables
ESP32S3_J1 = ["3V3", "3V3", "RST", "IO4", "IO5", "IO6", "IO7", "IO15", "IO16", "IO17", "IO18",
              "IO8", "IO3", "IO46", "IO9", "IO10", "IO11", "IO12", "IO13", "IO14", "5V", "GND"]
ESP32S3_J3 = ["GND", "TX/IO43", "RX/IO44", "IO1", "IO2", "IO42", "IO41", "IO40", "IO39", "IO38",
              "IO37", "IO36", "IO35", "IO0", "IO45", "IO48", "IO47", "IO21", "IO20", "IO19", "GND", "GND"]

# NUCLEO-64 (UM1724) ST morpho, F446RE
F446_CN7 = ["PC10", "PC11", "PC12", "PD2", "VDD", "E5V", "BOOT0", "GND", "NC", "NC", "NC", "IOREF",
            "PA13", "RESET", "PA14", "+3V3", "PA15", "+5V", "GND", "GND", "PB7", "GND", "PC13", "VIN",
            "PC14", "NC", "PC15", "PA0", "PH0", "PA1", "PH1", "PA4", "VBAT", "PB0", "PC2", "PC1",
            "PC3", "PC0"]
F446_CN10 = ["PC9", "PC8", "PB8", "PC6", "PB9", "PC5", "AVDD", "U5V", "GND", "NC", "PA5", "PA12",
             "PA6", "PA11", "PA7", "PB12", "PB6", "NC", "PC7", "GND", "PA9", "PB2", "PA8", "PB1",
             "PB10", "PB15", "PB4", "PB14", "PB5", "PB13", "PB3", "AGND", "PA10", "PC4", "PA2", "NC",
             "PA3", "NC"]

BLUEPILL_L = ["B12", "B13", "B14", "B15", "A8", "A9", "A10", "A11", "A12", "A15", "B3", "B4", "B5",
              "B6", "B7", "B8", "B9", "5V", "GND", "3V3"]
BLUEPILL_R = ["VBAT", "C13", "C14", "C15", "A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "B0",
              "B1", "B10", "B11", "RST", "3V3", "GND", "GND"]

NANO_L = ["D1/TX", "D0/RX", "RST", "GND", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10",
          "D11", "D12"]
NANO_R = ["VIN", "GND", "RST", "5V", "A7", "A6", "A5", "A4", "A3", "A2", "A1", "A0", "AREF", "3V3",
          "D13"]

PI_GPIO = ["3V3", "5V", "GPIO2/SDA1", "5V", "GPIO3/SCL1", "GND", "GPIO4", "GPIO14/TXD", "GND",
           "GPIO15/RXD", "GPIO17", "GPIO18", "GPIO27", "GND", "GPIO22", "GPIO23", "3V3", "GPIO24",
           "GPIO10/MOSI", "GND", "GPIO9/MISO", "GPIO25", "GPIO11/SCLK", "GPIO8/CE0", "GND",
           "GPIO7/CE1", "GPIO0/ID_SD", "GPIO1/ID_SC", "GPIO5", "GND", "GPIO6", "GPIO12", "GPIO13",
           "GND", "GPIO19", "GPIO16", "GPIO26", "GPIO20", "GND", "GPIO21"]

OBD2 = ["1_OEM", "2_J1850+", "3_OEM", "4_CGND", "5_SGND", "6_CAN_H", "7_K_LINE", "8_OEM", "9_OEM",
        "10_J1850-", "11_OEM", "12_OEM", "13_OEM", "14_CAN_L", "15_L_LINE", "16_BAT+"]

PI_CSI15 = ["GND", "D0_N", "D0_P", "GND", "D1_N", "D1_P", "GND", "CLK_N", "CLK_P", "GND",
            "IO0", "IO1", "SCL", "SDA", "3V3"]


def nucleo144_pins(prefix, n):
    return [f"{prefix}-{i}" for i in range(1, n + 1)]


# ------------------------------------------------------------------ modules
# lib: core | anomaly | safety | hud | edge-hil
M = []


def mod(**kw):
    kw.setdefault("holes", [])
    kw.setdefault("gates", "auto")
    kw.setdefault("notes", "")
    kw.setdefault("outline", "rect")
    M.append(kw)


# ============================ CORE (Part 1)
mod(lib="core", name="NUCLEO-H755ZI-Q", prefix="U", w=70.0, h=133.34, conf="L",
    desc="STM32H755ZI Nucleo-144 (M7 rt-core + M4 safety). ST morpho CN11/CN12 + ZIO CN7..CN10.",
    step="NUCLEO-H755ZI-Q STEP (st.com > CAD resources) / GrabCAD 'Nucleo-144'",
    notes="Pin isimleri konnektor-pin olarak (CN11-1..). Sinyal adlari UM2408 'ST morpho' ve 'ZIO' tablolarindan doldurulmali. Header X/Y konumlari yaklasik: ST mekanik cizimiyle (MB1363) dogrula.",
    hdrs=[hdr("CN11", 3.81, 30.0, nucleo144_pins("CN11", 70), dir="v", rows=2, row_off=(P, 0)),
          hdr("CN12", 63.65, 30.0, nucleo144_pins("CN12", 70), dir="v", rows=2, row_off=(P, 0)),
          hdr("CN7", 17.0, 92.0, nucleo144_pins("CN7", 20), dir="v", rows=2, row_off=(P, 0)),
          hdr("CN10", 17.0, 40.0, nucleo144_pins("CN10", 34), dir="v", rows=2, row_off=(P, 0)),
          hdr("CN8", 48.5, 98.0, nucleo144_pins("CN8", 16), dir="v", rows=2, row_off=(P, 0)),
          hdr("CN9", 48.5, 50.0, nucleo144_pins("CN9", 30), dir="v", rows=2, row_off=(P, 0))],
    holes=[(3.5, 3.5, 3.2), (66.5, 3.5, 3.2), (3.5, 129.8, 3.2), (66.5, 129.8, 3.2)])

mod(lib="core", name="ESP32-S3-DEVKITC-1", prefix="U", w=28.0, h=69.0, conf="H",
    desc="Espressif ESP32-S3-DevKitC-1 (N16R8). J1 sol, J3 sag; USB'ler altta. Satirlar arasi 22.86 mm.",
    step="Espressif ESP32-S3-DevKitC-1 STEP (GrabCAD / espressif KiCad lib)",
    notes="Klon kartlarda genislik 25.5-28 mm arasi degisir, satir araligi (22.86) sabittir.",
    hdrs=[hdr("J1", 2.57, 64.0, ESP32S3_J1, dir="v", pitch=-P),
          hdr("J3", 25.43, 64.0, ESP32S3_J3, dir="v", pitch=-P)])

mod(lib="core", name="SN65HVD230-MODULE", prefix="M", w=27.0, h=11.0, conf="M",
    desc="SN65HVD230 3.3V CAN transceiver karti (VP230). Kart uzerinde 120R olabilir (R2) - arac hattinda sok.",
    step="GrabCAD 'SN65HVD230 module'",
    hdrs=[hdr("J1", 2.0, 1.69, ["3V3", "GND", "CTX", "CRX"], dir="v"),
          hdr("J2", 25.0, 4.23, ["CANH", "CANL"], dir="v")])

mod(lib="core", name="LM2596HVS-MODULE", prefix="PS", w=43.0, h=21.0, conf="M",
    desc="LM2596HVS ayarli buck (4.5-53V giris, 3A). 4 kose pad + 2 capraz M3 delik.",
    step="models/hardware-integration/cad-exports/lm2596_buck_module (mevcut) / GrabCAD 'LM2596 module'",
    notes="Pad yerleri 'mavi LM2596' klon karttan. HVS kartlar ayni boyutta. HW-788 farkli boyut/pin: alinirsa ayri parca.",
    hdrs=[lug("IN", 2.0, 2.5, ["IN-", "IN+"], dir="v", pitch=16.0),
          lug("OUT", 41.0, 2.5, ["OUT-", "OUT+"], dir="v", pitch=16.0)],
    holes=[(7.0, 17.5, 3.0), (36.0, 3.5, 3.0)])

mod(lib="core", name="INA226-MODULE", prefix="M", w=20.5, h=19.4, conf="M",
    desc="INA226 (CJMCU-226) I2C akim/guc izleme, 0.1R shunt. VBUS ayri pin.",
    step="GrabCAD 'INA226 CJMCU'",
    hdrs=[hdr("J1", 3.9, 2.0, ["VCC", "GND", "SCL", "SDA", "ALE", "VBS"], dir="h"),
          lug("J2", 5.75, 16.5, ["IN+", "IN-"], dir="h", pitch=9.0)])

mod(lib="core", name="MICROSD-MODULE-SPI", prefix="M", w=24.0, h=42.0, conf="M",
    desc="Catalex tipi microSD SPI karti (3.3V regulator + level shifter).",
    step="GrabCAD 'micro SD card module catalex'",
    hdrs=[hdr("J1", 5.65, 2.0, ["GND", "VCC", "MISO", "MOSI", "SCK", "CS"], dir="h")],
    holes=[(2.5, 2.5, 3.0), (21.5, 2.5, 3.0), (2.5, 39.5, 3.0), (21.5, 39.5, 3.0)])

mod(lib="core", name="NEO-M8N-GPS-MODULE", prefix="M", w=26.0, h=36.0, conf="L",
    desc="GY-GPSV3-M8N tipi u-blox NEO-M8N karti, PPS cikisli. Harici anten u.FL.",
    step="GrabCAD 'GY-NEO-M8N'",
    notes="Pin sirasi karta gore degisir (VCC/GND/TX/RX/PPS). Kartindaki baski ile kontrol et.",
    hdrs=[hdr("J1", 7.92, 2.0, ["VCC", "GND", "TX", "RX", "PPS"], dir="h")],
    holes=[(2.5, 33.5, 3.0), (23.5, 33.5, 3.0)])

mod(lib="core", name="MPU6500-MODULE", prefix="M", w=15.0, h=25.0, conf="M",
    desc="GY-6500 MPU-6500 / MPU-6590 IMU karti (SPI/I2C). Board C1 (M4, SPI) / Board C2 (M7, I2C), rijit montaj.",
    step="GrabCAD 'GY-6500' / 'GY-521' (ayni form)",
    hdrs=[hdr("J1", 2.0, 1.5, ["VCC", "GND", "SCL/SCLK", "SDA/SDI", "EDA", "ECL", "AD0/SDO",
                                "INT", "NCS", "FSYNC"], dir="v")],
    holes=[(11.5, 3.0, 3.0), (11.5, 22.0, 3.0)])

mod(lib="core", name="OBD2-J1962", prefix="X", w=40.0, h=18.0, conf="H",
    desc="SAE J1962 16-pin OBD2 konnektor (Honda DLC adaptor ucu / HIL dişi soket). Pin numaralari standart.",
    step="GrabCAD 'OBD2 J1962 female connector'",
    notes="CL250 DLC (4/6-pin) pinout'u hardware-integration §1'de CONFIRM; bu cihaz adaptorun 16-pin ucu.",
    hdrs=[hdr("ROW1", 5.0, 12.0, OBD2[:8], dir="h", pitch=4.0, drill=1.2, dia=2.2),
          hdr("ROW2", 5.0, 6.0, OBD2[8:], dir="h", pitch=4.0, drill=1.2, dia=2.2)],
    gates="single")

# ============================ ANOMALY (Part 2)
mod(lib="anomaly", name="INMP441-MODULE", prefix="MIC", w=14.0, h=14.0, outline="circle", conf="M",
    desc="INMP441 I2S MEMS mikrofon karti (yuvarlak, 2x3 pin).",
    step="GrabCAD 'INMP441'",
    hdrs=[hdr("J1", 4.46, 3.0, ["SCK", "WS", "L/R"], dir="h"),
          hdr("J2", 4.46, 11.0, ["SD", "VDD", "GND"], dir="h")])

mod(lib="anomaly", name="BME280-MODULE", prefix="M", w=15.0, h=12.0, conf="M",
    desc="GY-BME280 6-pin (I2C/SPI) ortam sicaklik/basinc/nem.",
    step="GrabCAD 'GY-BME280'",
    hdrs=[hdr("J1", 1.15, 1.5, ["VCC", "GND", "SCL", "SDA", "CSB", "SDO"], dir="h")])

mod(lib="anomaly", name="ADXL345-GY291", prefix="M", w=20.0, h=16.0, conf="M",
    desc="GY-291 ADXL345 ivmeolcer (SPI kullanimi). Motor blogu / salincak.",
    step="GrabCAD 'GY-291 ADXL345'",
    hdrs=[hdr("J1", 1.11, 1.5, ["GND", "VCC", "CS", "INT1", "INT2", "SDO", "SDA/SDI", "SCL/SCLK"],
              dir="h", pitch=2.54)],
    holes=[(2.5, 13.0, 3.0), (17.5, 13.0, 3.0)])

mod(lib="anomaly", name="MAX31856-MODULE", prefix="M", w=20.0, h=25.0, conf="L",
    desc="MAX31856 termokupl (K-tip EGT) amplifikatoru, SPI.",
    step="GrabCAD 'MAX31856 breakout'",
    notes="Genel klon pin sirasi; Adafruit kartinda VIN/3Vo ek pinleri var.",
    hdrs=[hdr("J1", 2.0, 2.0, ["VCC", "GND", "SCK", "SDO", "SDI", "CS", "DRDY", "FLT"], dir="h",
              pitch=2.2),
          lug("TC", 6.5, 21.5, ["T+", "T-"], dir="h", pitch=7.0)])

mod(lib="anomaly", name="ACS758-200B-MODULE", prefix="M", w=38.0, h=30.0, conf="L",
    desc="ACS758LCB-200B hall akim sensoru (+/-200A) karti. IP+/IP- buyuk akim terminalleri.",
    step="GrabCAD 'ACS758 module'",
    hdrs=[hdr("J1", 2.0, 12.46, ["VCC", "GND", "VOUT"], dir="v"),
          hdr("IP", 33.0, 7.0, ["IP+", "IP-"], dir="v", pitch=16.0, drill=4.2, dia=7.0)])

mod(lib="anomaly", name="MLX90614-GY906", prefix="M", w=11.0, h=17.0, conf="M",
    desc="GY-906 MLX90614 temassiz IR termometre (I2C). TO-39 kap ust tarafta.",
    step="GrabCAD 'GY-906 MLX90614'",
    hdrs=[hdr("J1", 1.69, 1.5, ["VIN", "GND", "SCL", "SDA"], dir="h")])

mod(lib="anomaly", name="LJ12A3-4-Z-BX", prefix="S", w=12.5, h=6.0, conf="H",
    desc="LJ12A3-4-Z/BX enduktif NPN sensor (kablolu). Footprint = 3-pin JST-XH harness girisi.",
    step="GrabCAD 'LJ12A3-4-Z/BX' (M12x60 govde)",
    notes="12V cikis -> 3.3V seviye kaydirma Board B'de.",
    hdrs=[hdr("J1", 3.75, 3.0, ["BRN_+V", "BLU_0V", "BLK_OUT"], dir="h", pitch=2.5)])

mod(lib="anomaly", name="PC817-4CH-MODULE", prefix="M", w=48.0, h=41.0, conf="L",
    desc="PC817 4 kanal optokuplor izolasyon karti (12V -> 3.3V salt-okunur tap).",
    step="GrabCAD 'PC817 4 channel optocoupler module'",
    notes="Giris/cikis klemens sirasi ureticiye gore degisir; mutlaka kartindan kontrol et.",
    hdrs=[lug("IN", 4.0, 5.5, ["IN1", "IN2", "IN3", "IN4", "IGND"], dir="v", pitch=7.5),
          hdr("OUT", 44.0, 12.95, ["VCC", "OUT1", "OUT2", "OUT3", "OUT4", "GND"], dir="v")],
    holes=[(3.0, 38.0, 3.0), (45.0, 38.0, 3.0)])

mod(lib="anomaly", name="VL53L1X-TOF400C", prefix="M", w=25.0, h=13.0, conf="M",
    desc="TOF400C VL53L1X 4 m ToF lazer mesafe (suspansiyon stroku, ileri asama).",
    step="GrabCAD 'VL53L1X module'",
    hdrs=[hdr("J1", 6.15, 1.5, ["VIN", "GND", "SCL", "SDA", "XSHUT", "GPIO1"], dir="h")],
    holes=[(2.5, 9.5, 2.2), (22.5, 9.5, 2.2)])

mod(lib="anomaly", name="AS5600-MODULE", prefix="M", w=23.0, h=23.0, conf="M",
    desc="AS5600 12-bit manyetik aci enkoderi (salincak/direksiyon acisi, ileri asama).",
    step="GrabCAD 'AS5600 magnetic encoder module'",
    hdrs=[hdr("J1", 3.88, 2.0, ["VCC", "OUT", "GND", "DIR", "SCL", "SDA", "GPO"], dir="h")],
    holes=[(3.0, 20.0, 3.0), (20.0, 20.0, 3.0)])

# ============================ SAFETY (Part 3)
mod(lib="safety", name="HLK-LD2451-RADAR", prefix="M", w=35.0, h=18.0, conf="L",
    desc="Hi-Link HLK-LD2451 24 GHz arac algilama radari (kor nokta), UART.",
    step="hlktech.net LD2451 3D / GrabCAD",
    notes="Pin araligi ve sira datasheet'ten dogrulanmali (1.25 mm konnektor varyanti olabilir).",
    hdrs=[hdr("J1", 13.69, 2.0, ["5V", "GND", "TX", "RX"], dir="h")])

mod(lib="safety", name="WS2812B-RING-12", prefix="LED", w=37.0, h=37.0, outline="circle", conf="M",
    desc="12 LED WS2812B NeoPixel halka (dis O37 mm). Viraj aydinlatma.",
    step="GrabCAD 'NeoPixel ring 12'",
    hdrs=[hdr("J1", 14.69, 4.5, ["DIN", "5V", "GND", "DOUT"], dir="h", drill=0.9, dia=1.6)])

mod(lib="safety", name="PN532-NFC-MODULE", prefix="M", w=43.0, h=41.0, conf="M",
    desc="PN532 NFC V3 karti (kirmizi). I2C/HSU 4-pin + SPI 8-pin header.",
    step="GrabCAD 'PN532 NFC module V3'",
    hdrs=[hdr("I2C", 16.69, 2.0, ["GND", "VCC", "SDA/TXD", "SCL/RXD"], dir="h"),
          hdr("SPI", 40.5, 11.61, ["SCK", "MISO", "MOSI", "SS", "VCC@SPI", "GND@SPI", "IRQ", "RSTO"],
              dir="v")],
    holes=[(3.0, 38.0, 3.0), (40.0, 38.0, 3.0)])

mod(lib="safety", name="LATCHING-RELAY-2COIL", prefix="K", w=29.0, h=12.7, conf="L",
    desc="12V bistable (latching) 2 bobinli role - mars rolesi bobini immobilizer (varsayilan kilitsiz).",
    step="Uretici STEP (Hongfa HFE20 / Omron G6AK vb. secilen modele gore)",
    notes="Generic DIP yerlesim; secilen role modelinin datasheet'ine gore pad konumlarini duzelt.",
    hdrs=[hdr("A", 2.0, 2.5, ["SET+", "RESET+", "COIL-"], dir="h", pitch=5.08, drill=1.1, dia=2.0),
          hdr("B", 17.0, 2.5, ["COM", "NO", "NC"], dir="h", pitch=5.08, drill=1.3, dia=2.4)],
    gates="single")

mod(lib="safety", name="SIM800L-MODULE", prefix="M", w=25.0, h=23.0, conf="M",
    desc="SIM800L GSM/GPRS mini kart (park modu bildirimi). VCC 3.4-4.4V, 2A tepe.",
    step="GrabCAD 'SIM800L module'",
    hdrs=[hdr("L", 1.5, 3.15, ["NET", "VCC", "RST", "RXD", "TXD", "GND"], dir="v"),
          hdr("R", 23.5, 3.15, ["SPK-", "SPK+", "MIC-", "MIC+", "DTR", "RING"], dir="v")])

mod(lib="safety", name="PI-CAMERA-MODULE-3", prefix="CAM", w=25.0, h=24.0, conf="H",
    desc="Raspberry Pi Camera Module 3 (15-pin 1mm FPC). Pi 5 tarafi 22-pin: adaptor kablo gerekir.",
    step="raspberrypi.com Camera Module 3 STEP",
    hdrs=[hdr("FPC", 5.5, 1.0, PI_CSI15, dir="h", pitch=1.0, drill=0, dia=0)],
    holes=[(2.0, 2.0, 2.2), (23.0, 2.0, 2.2), (2.0, 14.5, 2.2), (23.0, 14.5, 2.2)])

# ============================ HUD (Part 4)
mod(lib="hud", name="SSD1306-OLED-096-I2C", prefix="DSP", w=27.0, h=27.0, conf="M",
    desc="0.96 inc 128x64 SSD1306 I2C OLED (4-pin).",
    step="GrabCAD 'SSD1306 0.96 OLED'",
    hdrs=[hdr("J1", 9.69, 25.0, ["GND", "VCC", "SCL", "SDA"], dir="h")],
    holes=[(2.0, 2.0, 2.0), (25.0, 2.0, 2.0), (2.0, 25.0, 2.0), (25.0, 25.0, 2.0)])

mod(lib="hud", name="MICRO-OLED-049-I2C", prefix="DSP", w=15.0, h=13.0, conf="L",
    desc="0.42/0.49 inc micro OLED I2C (4-pin) - kask ici HUD kaynagi.",
    step="GrabCAD '0.49 OLED 64x32'",
    hdrs=[hdr("J1", 3.69, 1.5, ["GND", "VCC", "SCL", "SDA"], dir="h")])

mod(lib="hud", name="MAX98357A-MODULE", prefix="M", w=18.0, h=19.0, conf="M",
    desc="MAX98357A I2S 3W D sinifi amfi.",
    step="GrabCAD 'MAX98357A breakout'",
    hdrs=[hdr("J1", 1.38, 1.5, ["LRC", "BCLK", "DIN", "GAIN", "SD", "GND", "VIN"], dir="h"),
          lug("SPK", 6.0, 16.5, ["SPK+", "SPK-"], dir="h", pitch=3.5)])

mod(lib="hud", name="TP4056-TYPEC-PROT", prefix="M", w=26.0, h=17.0, conf="M",
    desc="TP4056 Type-C 1S LiPo sarj + DW01 koruma karti.",
    step="GrabCAD 'TP4056 type-c module'",
    hdrs=[hdr("IN", 2.0, 4.0, ["IN-", "IN+"], dir="v", pitch=9.0, drill=1.0, dia=2.2),
          hdr("BAT", 13.0, 4.0, ["B-", "B+"], dir="v", pitch=9.0, drill=1.0, dia=2.2),
          hdr("OUT", 24.0, 4.0, ["OUT-", "OUT+"], dir="v", pitch=9.0, drill=1.0, dia=2.2)],
    gates="single")

mod(lib="hud", name="LIPO-1S-JSTPH2", prefix="BT", w=8.0, h=6.0, conf="H",
    desc="3.7V 1S LiPo (koruma devreli) - JST-PH 2.0 mm 2-pin baglanti.",
    step="Pil: 50x34x8 kutu modeli / JST-PH 2P STEP",
    hdrs=[hdr("J1", 3.0, 3.0, ["BAT+", "BAT-"], dir="h", pitch=2.0, drill=0.8, dia=1.4)])

mod(lib="hud", name="SPEAKER-8R-2P", prefix="LS", w=6.0, h=4.0, conf="H",
    desc="8 ohm 1-2W ince hoparlor - 2-pin kablo girisi.",
    step="GrabCAD '28mm speaker'",
    hdrs=[hdr("J1", 1.73, 2.0, ["+", "-"], dir="h")])

# ============================ EDGE + HIL (Part 5)
mod(lib="edge-hil", name="RASPBERRY-PI-5", prefix="U", w=85.0, h=56.0, conf="H",
    desc="Raspberry Pi 5 - 40-pin GPIO header (HAT standardi), 58x49 M2.5 delik deseni.",
    step="raspberrypi.com Pi 5 STEP (datasheets.raspberrypi.com)",
    hdrs=[hdr("GPIO", 8.37, 51.23, PI_GPIO, dir="h", rows=2, row_off=(0, P))],
    holes=[(3.5, 3.5, 2.7), (61.5, 3.5, 2.7), (3.5, 52.5, 2.7), (61.5, 52.5, 2.7)])

mod(lib="edge-hil", name="MCP2515-TJA1050-MODULE", prefix="M", w=40.0, h=28.0, conf="M",
    desc="MCP2515 + TJA1050 SPI CAN karti (8 MHz kristal). TJA1050 5V: Pi 3.3V SPI icin seviye dikkat.",
    step="GrabCAD 'MCP2515 CAN module'",
    notes="J1 jumper = 120R sonlandirma.",
    hdrs=[hdr("J1", 2.0, 6.38, ["INT", "SCK", "SI", "SO", "CS", "GND", "VCC"], dir="v"),
          lug("CAN", 37.0, 11.5, ["CAN_H", "CAN_L"], dir="v", pitch=5.0)],
    holes=[(5.0, 2.5, 3.0), (35.0, 25.5, 3.0)])

mod(lib="edge-hil", name="HCW-P715-BUCK-5V5A", prefix="PS", w=54.0, h=29.0, conf="L",
    desc="HCW-P715 9-36V -> 5V 5A buck (Pi 5 beslemesi).",
    step="GrabCAD '5V 5A buck module'",
    hdrs=[lug("IN", 3.0, 9.0, ["IN+", "IN-"], dir="v", pitch=11.0),
          lug("OUT", 51.0, 9.0, ["OUT+", "OUT-"], dir="v", pitch=11.0)])

mod(lib="edge-hil", name="NUCLEO-F446RE", prefix="U", w=70.0, h=82.5, conf="M",
    desc="STM32F446RE Nucleo-64 (HIL simulator). ST morpho CN7/CN10 (UM1724).",
    step="st.com NUCLEO-F446RE STEP / GrabCAD 'Nucleo-64'",
    notes="Arduino headerlari (CN5/6/8/9) morpho ile ayni sinyaller oldugu icin eklenmedi. X/Y yaklasik.",
    hdrs=[hdr("CN7", 3.3, 63.0, F446_CN7, dir="v", rows=2, row_off=(P, 0), pitch=-P),
          hdr("CN10", 64.16, 63.0, F446_CN10, dir="v", rows=2, row_off=(P, 0), pitch=-P)])

mod(lib="edge-hil", name="STM32F103-BLUEPILL", prefix="U", w=22.8, h=53.0, conf="H",
    desc="STM32F103C8T6 Blue Pill. Satirlar 15.24 mm, USB ustte.",
    step="GrabCAD 'STM32 Blue Pill'",
    hdrs=[hdr("L", 3.78, 50.0, BLUEPILL_L, dir="v", pitch=-P),
          hdr("R", 19.02, 50.0, BLUEPILL_R, dir="v", pitch=-P)])

mod(lib="edge-hil", name="ARDUINO-NANO", prefix="U", w=18.0, h=45.0, conf="H",
    desc="Arduino Nano (elde var) - HIL ariza/besleme dugumu alternatifi. Satirlar 15.24 mm.",
    step="arduino.cc Nano STEP",
    hdrs=[hdr("L", 1.38, 4.72, NANO_L, dir="v"),
          hdr("R", 16.62, 4.72, NANO_R, dir="v")])

mod(lib="edge-hil", name="MCP4725-DAC-MODULE", prefix="M", w=18.0, h=21.0, conf="M",
    desc="MCP4725 12-bit I2C DAC (programlanabilir besleme referansi).",
    step="GrabCAD 'MCP4725 module'",
    hdrs=[hdr("J1", 2.65, 1.5, ["VCC", "GND", "SCL", "SDA", "A0", "OUT"], dir="h")])

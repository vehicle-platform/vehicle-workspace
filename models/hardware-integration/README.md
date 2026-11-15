# Honda CL250 Hardware Integration & CAD Assets

This directory contains 3D reference models, orthographic photos, enclosure dimensions, and CAD export files for the `moto-platform` hardware integration on the Honda CL250 (Scrambler).

---

## 1. Honda CL250 Official Engineering Dimensions

Use these dimensions to calibrate Meshy.ai mesh exports (`Scale Mesh`) or orthographic reference image planes in FreeCAD (Image workbench; mesh scaling with the Mesh/Part workbench):

| Parameter | Official Value | Notes |
|---|---|---|
| **Overall Length** | `2175 mm` | Total front tyre to rear fender tip |
| **Wheelbase (Aks Mesafesi)** | `1485 mm` | **Primary calibration metric** (front axle centre to rear axle centre) |
| **Overall Width** | `830 mm` | Handlebar width |
| **Overall Height** | `1135 mm` | Ground to instrument cluster / mirror top |
| **Seat Height** | `790 mm` | Ground to rider seat baseline |
| **Ground Clearance** | `163 mm` | Ground to lowest frame/engine sump point |
| **Rear Wheel Travel** | `150 mm` | **Suspension bottoming clearance bound** (never mount boxes below this line) |
| **Front Wheel / Tyre** | `19" (110/80R19)` | Large scrambler front wheel |
| **Rear Wheel / Tyre** | `17" (150/70R17)` | Compact wide scrambler rear wheel |

---

## 2. Main Enclosure Targets & Form Factors

| Subsystem | Enclosure Target | Mounting Type | Placement |
|---|---|---|---|
| **Core Controller (H755)** | `170 × 120 × 55 mm` (IP65) | Silicone bobbin vibration dampers (M4/M5) | Left Subframe Carrier Plate (`M8 × 2` bosses) |
| **Linux Node (Raspberry Pi 5)** | `170 × 120 × 55 mm` (IP65) | Silicone bobbin vibration dampers (M4/M5) | Beside H755 on Left Carrier Plate or Front Left Crash Bar |
| **IMU boxes (Board C1 M4, Board C2 M7, D-082)** | box open, Q-034 (`DT-0505` is `126 × 136 × 48 mm`, no IP rating stated) | **Rigid 6 mm brass standoffs** (never damped) | Bolted to main steel frame spine near CG |
| **Rear Radar & Sensor Hub** | `DT-0508` is `126 × 136 × 54 mm` (store page); size **CONFIRM** | Rigid bracket | Rear subframe / tail licence plate bracket |

---

## 3. Directory Layout

- `reference-images/`: High-resolution studio and orthographic images of the Honda CL250 / CL500 for Meshy.ai generation and FreeCAD image-plane calibration.
- `cad-exports/`: Exported `.OBJ`, `.STL`, and `.STEP` files generated via Meshy.ai and designed in FreeCAD. STEP exchange with the KiCad PCB design goes through the KiCad StepUp workbench.

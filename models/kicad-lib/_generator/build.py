"""Build KiCad 8/9 libraries (.kicad_sym + .pretty/*.kicad_mod) from modules.py.

Stdlib only, deterministic output. Usage: python3 build.py [out_dir]   (default: ..)

Geometry notes
- modules.py coordinates are board lower-left, Y up, board seen from the top.
  KiCad footprints are Y down, so y is flipped; the footprint origin is the board centre.
- Pad names are "<header>-<n>" (e.g. CN11-5); the symbol pin number is the same string.
- A module with several connectors and many pins becomes a multi-unit symbol,
  one unit per connector (same rule as the old per-connector gates).
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules import M  # noqa: E402

P = 2.54
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GEN = "vehicle_platform_gen"

LIBS = {
    "core": ("moto-core", "Part 1 - Ana kontrolcu, guc zinciri, CAN, GPS/IMU, OBD2"),
    "anomaly": ("moto-anomaly", "Part 2 - Anomali / usta-mekanik sensorleri"),
    "safety": ("moto-safety", "Part 3 - Guvenlik: radar, viraj LED, NFC immobilizer, GSM, kamera"),
    "hud": ("moto-hud", "Part 4 - Kask HUD ve ses birimi"),
    "edge-hil": ("moto-edge-hil", "Part 5 - Raspberry Pi 5 kenar birimi ve HIL tezgahi"),
}

SUPPLY = {"3V3", "+3V3", "5V", "+5V", "VCC", "VDD", "VIN", "VBAT", "VBS", "E5V", "U5V", "AVDD",
          "IOREF", "VCC@SPI", "VIN"}


def f(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def disp(name):
    return name.split("@")[0]


def pin_type(name):
    n = disp(name)
    if n == "NC":
        return "no_connect"
    if "GND" in n.upper() or name in SUPPLY or n in SUPPLY:
        return "power_in"
    return "bidirectional"


# ------------------------------------------------------------------ geometry
def pad_positions(h):
    """(padname, pinname, x, y) in board coords for one header."""
    out = []
    for i, pin in enumerate(h["pins"]):
        k, row = divmod(i, 2) if h["rows"] == 2 else (i, 0)
        dx, dy = (h["pitch"] * k, 0) if h["dir"] == "h" else (0, h["pitch"] * k)
        x, y = h["x"] + dx, h["y"] + dy
        if row == 1:
            x += h["row_off"][0]
            y += h["row_off"][1]
        out.append((f"{h['name']}-{i + 1}", pin, x, y))
    return out


def units_of(m):
    total = sum(len(h["pins"]) for h in m["hdrs"])
    if m["gates"] == "single" or (m["gates"] == "auto" and total <= 40) or len(m["hdrs"]) == 1:
        return [(m["name"], m["hdrs"])]
    return [(h["name"], [h]) for h in m["hdrs"]]


# ------------------------------------------------------------------ footprint
def footprint(m):
    w, h = m["w"], m["h"]
    cx, cy = w / 2, h / 2
    desc = f'{m["desc"]} | Kart: {w} x {h} mm | Guven: {m["conf"]}'
    pads = [pp for hd in m["hdrs"] for pp in pad_positions(hd)]
    all_smd = all(hd["drill"] == 0 for hd in m["hdrs"])
    S = lambda layer, wd: f'(stroke (width {wd}) (type default)) (layer "{layer}")'
    L = [f'(footprint {q(m["name"])}',
         '\t(version 20240108)', f'\t(generator "{GEN}")', '\t(generator_version "8.0")',
         '\t(layer "F.Cu")', f'\t(descr {q(desc)})', '\t(tags "module")',
         f'\t(property "Reference" "REF**" (at {f(-cx)} {f(-cy - 1.5)} 0) (layer "F.SilkS") '
         '(effects (font (size 1 1) (thickness 0.15)) (justify left)))',
         f'\t(property "Value" {q(m["name"])} (at {f(-cx)} {f(cy + 1.5)} 0) (layer "F.Fab") '
         '(effects (font (size 1 1) (thickness 0.15)) (justify left)))',
         '\t(property "Footprint" "" (at 0 0 0) (layer "F.Fab") hide (effects (font (size 1.27 1.27))))',
         '\t(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") hide (effects (font (size 1.27 1.27))))',
         f'\t(attr {"smd" if all_smd else "through_hole"})']
    mg = 0.25
    if m["outline"] == "circle":
        r = w / 2
        L.append(f'\t(fp_circle (center 0 0) (end {f(r)} 0) {S("F.Fab", 0.1)} (fill none))')
        L.append(f'\t(fp_circle (center 0 0) (end {f(r + mg)} 0) {S("F.CrtYd", 0.05)} (fill none))')
    else:
        L.append(f'\t(fp_rect (start {f(-cx)} {f(-cy)}) (end {f(cx)} {f(cy)}) {S("F.Fab", 0.1)} (fill none))')
        L.append(f'\t(fp_rect (start {f(-cx - mg)} {f(-cy - mg)}) (end {f(cx + mg)} {f(cy + mg)}) '
                 f'{S("F.CrtYd", 0.05)} (fill none))')
    L.append(f'\t(fp_text user "${{REFERENCE}}" (at 0 0 0) (layer "F.Fab") '
             '(effects (font (size 1 1) (thickness 0.15))))')
    for hd in m["hdrs"]:
        L.append(f'\t(fp_text user {q(hd["name"])} (at {f(hd["x"] - cx)} {f(cy - hd["y"] - 1.6)} 0) '
                 '(layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))')
    for hd in m["hdrs"]:
        for pname, _, x, y in pad_positions(hd):
            X, Y = x - cx, cy - y
            if hd["drill"] == 0:
                L.append(f'\t(pad {q(pname)} smd rect (at {f(X)} {f(Y)}) (size 0.6 2) '
                         '(layers "F.Cu" "F.Paste" "F.Mask"))')
            else:
                shape = "rect" if pname.endswith("-1") else "circle"
                L.append(f'\t(pad {q(pname)} thru_hole {shape} (at {f(X)} {f(Y)}) '
                         f'(size {f(hd["dia"])} {f(hd["dia"])}) (drill {f(hd["drill"])}) '
                         '(layers "*.Cu" "*.Mask"))')
    for (x, y, d) in m["holes"]:
        L.append(f'\t(pad "" np_thru_hole circle (at {f(x - cx)} {f(cy - y)}) '
                 f'(size {f(d)} {f(d)}) (drill {f(d)}) (layers "*.Cu" "*.Mask"))')
    L.append(")")
    return "\n".join(L) + "\n", len(pads)


# ------------------------------------------------------------------ symbol
def tprops(m, lib):
    fp = f'{lib}:{m["name"]}'
    hidden = '(effects (font (size 1.27 1.27)) (hide yes))'
    return fp, hidden


def unit_body(uidx, uname, pads, multi, m):
    n = len(pads)
    names = [disp(p[1]) for p in pads]
    nl = math.ceil(n / 2)
    left, right = pads[:nl], pads[nl:]
    longest = max((len(x) for x in names), default=4)
    half_w = max(7.62, math.ceil((longest * 1.3 + 2.0) / P) * P)
    rows = max(len(left), len(right))
    top = math.ceil((rows - 1) / 2) * P
    y_bot = top - (rows - 1) * P
    L = [f'\t\t(symbol {q(f"{m["name"]}_{uidx}_1")}']
    if multi:
        L.append(f'\t\t\t(unit_name {q(uname)})')
    L.append(f'\t\t\t(rectangle (start {f(-half_w)} {f(top + P / 2)}) (end {f(half_w)} {f(y_bot - P / 2)}) '
             '(stroke (width 0.254) (type default)) (fill (type background)))')
    for col, items, x, ang in ((0, left, -half_w - P, 0), (1, right, half_w + P, 180)):
        for i, (pname, pin, _, _) in enumerate(items):
            L.append(f'\t\t\t(pin {pin_type(pin)} line (at {f(x)} {f(top - i * P)} {ang}) (length {f(P)}) '
                     f'(name {q(disp(pin))} (effects (font (size 1.27 1.27)))) '
                     f'(number {q(pname)} (effects (font (size 1.27 1.27)))))')
    L.append("\t\t)")
    return "\n".join(L), top + P / 2, y_bot - P / 2, half_w


def symbol(m, lib):
    units = units_of(m)
    multi = len(units) > 1
    fp, hidden = tprops(m, lib)
    bodies, tops, bots, hw = [], [], [], []
    npins = 0
    for i, (uname, hds) in enumerate(units, 1):
        pads = [pp for hd in hds for pp in pad_positions(hd)]
        npins += len(pads)
        b, t, bo, w_ = unit_body(i, uname, pads, multi, m)
        bodies.append(b)
        tops.append(t)
        bots.append(bo)
        hw.append(w_)
    top, bot, half = max(tops), min(bots), max(hw)
    desc = f'{m["desc"]} | Kart: {m["w"]} x {m["h"]} mm | Guven: {m["conf"]}'
    if m["notes"]:
        desc += f' | NOT: {m["notes"]}'
    pr = [("Reference", m["prefix"], (-half, top + 1.5), False, "left"),
          ("Value", m["name"], (-half, bot - 1.5), False, "left"),
          ("Footprint", fp, (0, 0), True, None),
          ("Datasheet", "", (0, 0), True, None),
          ("Description", desc, (0, 0), True, None),
          ("BOARD_SIZE", f'{m["w"]}x{m["h"]}mm', (0, 0), True, None),
          ("CONFIDENCE", m["conf"], (0, 0), True, None),
          ("STEP", m["step"], (0, 0), True, None)]
    L = [f'\t(symbol {q(m["name"])}', '\t\t(exclude_from_sim no)', '\t\t(in_bom yes)', '\t\t(on_board yes)']
    for k, (name, val, (x, y), hide, just) in enumerate(pr):
        eff = "(font (size 1.27 1.27))" + (f" (justify {just})" if just else "") + (" (hide yes)" if hide else "")
        L.append(f'\t\t(property {q(name)} {q(val)} (at {f(x)} {f(y)} 0) (effects {eff}))')
    L.append("\t\t(pin_names (offset 1.016))")
    L += bodies
    L.append("\t)")
    return "\n".join(L), npins


def build_all(out):
    os.makedirs(out, exist_ok=True)
    report = []
    for key, (lib, _) in LIBS.items():
        mods = [m for m in M if m["lib"] == key]
        syms = []
        pretty = os.path.join(out, lib + ".pretty")
        os.makedirs(pretty, exist_ok=True)
        for fn in os.listdir(pretty):
            if fn.endswith(".kicad_mod"):
                os.remove(os.path.join(pretty, fn))
        for m in mods:
            s, npins = symbol(m, lib)
            syms.append(s)
            fp, npads = footprint(m)
            assert npins == npads, (m["name"], npins, npads)
            with open(os.path.join(pretty, m["name"] + ".kicad_mod"), "w", encoding="utf-8") as fh:
                fh.write(fp)
        body = "\n".join(syms)
        txt = (f'(kicad_symbol_lib\n\t(version 20231120)\n\t(generator "{GEN}")\n'
               f'\t(generator_version "8.0")\n{body}\n)\n')
        with open(os.path.join(out, lib + ".kicad_sym"), "w", encoding="utf-8") as fh:
            fh.write(txt)
        report.append((lib, len(mods)))
    return report


if __name__ == "__main__":
    for lib, n in build_all(OUT):
        print(lib, n, "modules")

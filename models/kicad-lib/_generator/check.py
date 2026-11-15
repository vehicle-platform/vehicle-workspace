"""Sanity checks for the generated KiCad libraries (stdlib only).

1. every .kicad_sym / .kicad_mod has balanced parentheses (string-aware);
2. each symbol's total pin count (all units) equals its footprint's pad count
   (mounting holes, i.e. np_thru_hole pads, excluded) and the Footprint property resolves;
3. every symbol pin number exists as a pad name in the footprint.
Usage: python3 check.py [lib_dir]   (default: ..). Exit code 1 on any failure.
"""
import glob
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def balanced(txt):
    depth, in_str, esc = 0, False, False
    for ch in txt:
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0 and not in_str


def main():
    errors, nsym = [], 0
    files = glob.glob(os.path.join(ROOT, "*.kicad_sym")) + glob.glob(os.path.join(ROOT, "*.pretty", "*.kicad_mod"))
    for p in files:
        if not balanced(open(p, encoding="utf-8").read()):
            errors.append(f"unbalanced parentheses: {p}")
    for sp in sorted(glob.glob(os.path.join(ROOT, "*.kicad_sym"))):
        txt = open(sp, encoding="utf-8").read()
        parts = re.split(r'\n\t\(symbol "', txt)[1:]
        for part in parts:
            name = part.split('"', 1)[0]
            nsym += 1
            fpm = re.search(r'\(property "Footprint" "([^"]*)"', part)
            lib, _, fpname = (fpm.group(1) if fpm else "").partition(":")
            mod = os.path.join(ROOT, lib + ".pretty", fpname + ".kicad_mod")
            if not os.path.isfile(mod):
                errors.append(f"{name}: footprint not found ({fpm and fpm.group(1)})")
                continue
            mtxt = open(mod, encoding="utf-8").read()
            pads = [m for m in re.findall(r'\(pad "([^"]*)" (\w+)', mtxt) if m[1] != "np_thru_hole"]
            pins = re.findall(r'\(number "([^"]*)"', part)
            if len(pins) != len(pads):
                errors.append(f"{name}: {len(pins)} pins != {len(pads)} pads")
            if set(pins) != {p_[0] for p_ in pads}:
                errors.append(f"{name}: pin numbers differ from pad names")
            if len(set(pins)) != len(pins):
                errors.append(f"{name}: duplicate pin numbers")
    for e in errors:
        print("FAIL", e)
    print(f"checked {len(files)} files, {nsym} symbols, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

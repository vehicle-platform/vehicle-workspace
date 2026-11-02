---
date: 2026-11-02
tool: gemini/gemini-3.8-flash
topic: procurement-list
repos: [vehicle-workspace]
branches: []
prs: []
zone: green
review: done 2026-11-02 (research only, no code; H745 board change put to the user as a D-072 amendment)
---

# Procurement List Creation / Review

## Goal
Session initialized for creating and reviewing the hardware procurement list for the vehicle-platform project (Phase 0 / Wave 1 and onwards), specifically locating STM32 dual-core Nucleo board stock.

## Changes
- None (research / inquiry).

## Result
- User confirmed the purchase of `NUCLEO-H745ZI-Q` (fully compatible dual-core M7+M4 alternative to H755 per D-072).
- Addressed breakout module supply shortage for SN65HVD230: identified 4 viable alternatives:
  1. Direct IC purchase (`SN65HVD230DR` SOIC-8 from Direnc.net) + SOP-8 to DIP-8 adapter PCB (cleanest, original TI silicon, avoids on-board 120R issues).
  2. NXP `TJA1051T/3` (Direnc.net) with VIO connected to 3.3V.
  3. Ubiquitous 5V transceivers (TJA1050 / MCP2551 breakout modules) with a 1k/2k resistive divider on RX.
  4. Waveshare RS485/CAN Shield on Direnc.net (contains on-board SN65HVD230).



## Checks
- None yet.

## Unsure about
- Exact user requirements / scope for this procurement session (e.g., Wave 1 ordering, Phase 0 ESP32 prototype parts, or full budget review).

## For Claude
- User purchased `NUCLEO-H745ZI-Q` instead of `NUCLEO-H755ZI-Q` (due to local stock availability at Hiber Bilişim in Adana). No functional difference for rt-core and safety-node (both Cortex-M7 480 MHz + Cortex-M4 240 MHz, 2MB Flash, 1MB RAM, 2x FDCAN). Please note in STATUS.md / DECISIONS.md when updating.

## Claude review
- No code or doc change; the log was left uncommitted by the tool, Claude committed it.
- Correction: NUCLEO-H745ZI-Q is **not** identical to the H755: the STM32H755 adds the CRYP/HASH crypto accelerators (and secure-access features); cores, clocks, flash, RAM, SRAM4 and FDCAN x2 are the same. No recorded decision relies on hardware crypto (DECISIONS searched), so the swap looks safe, but D-072 names the H755 and the CubeMX target part (rt-core `cubemx/`, red) changes with the board. Recorded only after the user confirms (new decision amending D-072).
- SN65HVD230 alternatives: the procurement doc is not changed by this log; the choice belongs with the user's next procurement update.


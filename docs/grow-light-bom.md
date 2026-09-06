# 20 W USB-C PD Grow Light — Schematic BOM

This BOM is taken from the KiCad schematics as of 2026-09-04, not from the
older pre-schematic parts list. Re-check LCSC stock and JLCPCB assembly
eligibility at checkout.

## Frozen electrical architecture (as drawn)

USB-C PD sink (**U1** HUSB238) plus **STM8S003F3** (**U2**) on a 3.3 V
**HT7533** rail. The MCU requests the PDO over I2C and PWM-dims four
**TPS61165DRV** boost channels. There is no panel-mount switch or pot.

The LED board has four electrically independent, constant-current strings:

```
String 1..4:  4000K - 4000K - 4000K - 4000K - 660nm
                 0.244 A nominal (200 mV / 0.82 Ω)
```

At nominal forward voltages of 3.2 V (white) and 3.0 V (red), each string
is about 15.8 V / 3.85 W. LED load is about 15.4 W.

TPS61165 is a **boost** converter with 3–18 V VIN. Firmware must request
**9 V or 12 V**, not 20 V.

## Controller board (from `grow-light.kicad_sch` + `led_driver.kicad_sch`)

| Refs | Qty | Value / MPN | LCSC | Footprint |
|---|---|---|---|---|
| J2 | 1 | USB-C 16P | C2927039 | TYPE-C 16-pin SMD |
| U1 | 1 | HUSB238 | C7471904 (not on symbol) | WDFN-10 3×3 |
| U3 | 1 | USBLC6-2SC6 | C7519 | SOT-23-6 |
| F1 | 1 | 3 A / 24 V PTC | C7500481 | 1812 |
| D7 | 1 | SMAJ24A | C19077541 | SMA |
| Q1 | 1 | AO3401A | C15127 | SOT-23 |
| D8 | 1 | BZX84C10 | C19077470 | SOT-23 |
| R1 | 1 | 10 Ω | C17415 | 0805 |
| R2 | 1 | 49.9 kΩ | C17719 | 0805 |
| R3 | 1 | 5.1 kΩ | C27834 | 0805 |
| C1, C16 | 2 | 1 µF 50 V X5R | C15849 | 0603 |
| C6, C7 | 2 | 10 µF 50 V X5R | C13585 | 1206 |
| C17, C18 | 2 | 100 nF 50 V X7R | C14663 | 0603 |
| U7 | 1 | HT7533-1 3.3 V LDO | C14289 | SOT-89-3 |
| U2 | 1 | STM8S003F3P6TR | C52717 | TSSOP-20 |
| S1, S2 | 2 | TS-1187A-B-A-B | C318884 | 5.1 mm tactile |
| D5 | 1 | Red 0805 | C84256 | 0805 |
| D6 | 1 | Green 0805 | C2297 | 0805 |
| R16, R17 | 2 | 1 kΩ | C21190 | 0603 |
| R8, R11–R14 | 5 | 10 kΩ | C17414 | 0805 |
| R9, R10, R15 | 3 | 4.7 kΩ | C23162 | 0603 |
| J3 | 1 | PROG 1×4 | — | TH 2.54 mm |
| J4 | 1 | UART 1×4 | — | TH 2.54 mm |
| J1 | 1 | 2×4 IDC TH | — | IDC 2.54 mm |
| U4, U5, U11, U12 | 4 | TPS61165DRV | — | WSON-6-EP 2×2 |
| L1–L4 | 4 | 22 µH CKCS4030 | **C354592** | 4×4×3.0 mm |
| D1–D4 | 4 | B5819WS | C7420331 | SOD-323 |
| R4–R7 | 4 | 820 mΩ | C2907361 | 1206 |
| C2–C5 | 4 | 4.7 µF 25 V X5R | C1779 | 0805 |
| C8–C11 | 4 | 1 µF 50 V X5R | C15849 | 0603 |
| C19–C22 | 4 | 220 nF 25 V X7R | C21120 | 0603 |

## LED panel (from `grow-light-LEDS.kicad_sch`)

| Refs | Qty | Value | LCSC | Footprint |
|---|---|---|---|---|
| D1–D4, D6, D7, D9–D12, D14–D17, D19, D20 | 16 | 4000 K white | C17398997 (not on sheet) | 3030 |
| D5, D8, D13, D18 | 4 | 660 nm red | C2833507 (not on sheet) | 3535-3P |
| J1 | 1 | 2×4 IDC SMD | — | IDC 2.54 mm SMD |

## What changed vs the pre-schematic BOM

| Old plan | Now in schematic |
|---|---|
| AL8860Q buck, 20 V PD | TPS61165 boost, MCU-selected 9/12 V PD |
| No MCU / no 3.3 V | STM8S003F3 + HT7533 |
| RV1 pot + SW1 | S1/S2 buttons + PWM on PC6 |
| L1–L4 68 µH C5291881 | L1–L4 **22 µH C354592** CKCS4030 4×4 mm (was C354634 6×6) |
| 0.402 Ω sense → 0.249 A | 820 mΩ sense → 0.244 A |
| SK24 SMA Schottky | B5819WS SOD-323 |
| USB-C C165948 | USB-C C2927039 |
| Fuse 1.5 A | Fuse 3 A / 24 V C7500481 |
| 12 V VGS zener | 10 V BZX84C10 |
| Off-board switch/pot harness | On-board UI only |

## Ordering notes

1. Import `grow-light-bom.csv` and re-check live stock.
2. TPS61165DRV has no LCSC on the symbol — pick a JLC-stocked WSON-6
   (`TPS61165DRV`) before assembly.
3. Do not substitute a 20 V PD request: it exceeds TPS61165 VIN.
4. LED LCSC numbers are still the previously qualified Cree / Silverlight
   parts; they are not written on the LED schematic.

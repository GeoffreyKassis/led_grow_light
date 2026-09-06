# Grow-light

USB-C PD grow light in two assemblies: an FR-4 controller (`MAIN_BOARD/`) and
a one-layer aluminum LED panel (`LED_BOARD/`), joined by an 8-wire 2×4 IDC
harness. Schematic connectivity and the as-drawn BOM come from KiCad
(`MAIN_BOARD/production/`, `LED_BOARD/production/`). This file records *why*
parts and numbers are what they are.

## Architecture

USB-C is the only power inlet. An **HUSB238** PD sink negotiates the contract
over I2C. An **STM8S003F3** requests **9 V or 12 V** (never 20 V) and PWM-dims
four **TPS61165** boost channels from `PC6`. Each channel drives one isolated
LED string: four 4000 K whites plus one 660 nm red in series.

Boost, not buck: string forward voltage is ~15.8 V, so the converter must sit
above that. TPS61165 VIN is 3–18 V recommended (20 V abs max). A 20 V PDO
leaves no boost headroom and violates that VIN rating.

On/off and dimming are MCU functions. There is no panel switch or pot.

## LED current and power

TPS61165 FB is **200 mV**. String current is set only by the sense resistor:

```
I_LED = V_FB / R_sense
      = 0.200 V / 0.82 Ω
      ≈ 0.244 A
```

A 1 Ω 1206 Basic (`C17928`) is a same-footprint swap: **0.200 A**. Dissipation
in the sense resistor is `I²R` ≈ 49 mW at 0.244 A, so 1206 is thermal margin,
not a requirement.

Nominal string voltage and power (generic 3 V whites / ~3 V red):

```
V_string ≈ 4 × 3.2 V + 3.0 V = 15.8 V
P_string ≈ 15.8 V × 0.244 A  ≈ 3.85 W
P_LEDs   ≈ 4 × 3.85 W        ≈ 15.4 W
```

XP-E2 / Oslon reds are ~2.0–2.1 V, which drops `V_string` a volt or so; the
boost still works. Input current is about **1.7 A at 9 V** or **1.3 A at 12 V**
plus converter and LDO overhead. Product class is still ~20 W at the USB-C
port.

Open-string OVP on TPS61165 is ~38 V. Do not hot-plug the LED harness with
drivers enabled.

## Controller choices

| Role | Part | Why |
|---|---|---|
| PD sink | HUSB238 `C7471904` (DFN-10 3×3) | I2C so firmware picks 9/12 V. CH224K is also Extended and has no I2C. |
| MCU | STM8S003F3P6TR `C52717` | Preferred (no $3 feeder). I2C + TIM1 PWM on remapped `PC6` (set OPT2 AFR0). |
| LED drivers | TPS61165**DRVR** `C122568` ×4 | WSON-6-EP 2×2. Do not pick the SOT-23 `C58756`. VIN 3–18 V, Vout to 38 V. |
| Inductors | CENKER CKCS4030 22 µH `C354592` | 1.0 A Irms / 1.3 A sat. Peak ~0.5 A at 9 V VIN, ~0.83 A at 5 V. No Basic 1 A 4×4. |
| Sense | 820 mΩ 1206 `C2907361` | Sets 0.244 A. True Extended; only same-footprint Basic swap is 1 Ω `C17928`. |
| Freewheel | B5819WS SOD-323 `C7420331` | 40 V / 1 A. Preferred, not a $3 line. |
| Load switch | AO3401A + BZX84C10 + 10 Ω | HUSB238 GATE after contract. 10 V VGS clamp; AO3401A is ±12 V. |
| 3.3 V | HT7533-1 | From switched VIN, 100 mA. Fine at 9/12 V; watch dissipation `(VIN−3.3)×I`. |
| USB-C | 16P `C2927039` | Cheap Extended 7.35 mm. Listing is 3 A / **5 V**; 9–12 V PD is common use but the listing is the weak one. `C165948` is 20 V / 5 A, still Extended. |
| CC ESD | USBLC6-2SC6 `C7519` | CC1/CC2 only. True Extended; no Basic SOT-23-6 equivalent. Do not tie pin 5 to 12 V. |
| Input protect | F1 3 A / 24 V PTC `C7500481`; D9 SMAJ15A | PTC is true Extended. SMAJ15A high-current clamp is ~24.4 V vs TPS61165 20 V abs max — a known gap, not a precise 15 V wall. |

HUSB238 **R2** 49.9 kΩ / **R3** 5.1 kΩ are the typical-app VSET/ISET pair.
5.1 kΩ ISET is about 1.5 A. 49.9 kΩ is **not** a datasheet VSET tap; firmware
must request 9/12 V so the default contract cannot land on 20 V.

TPS61165 VIN ceramics are 25 V. That is correct for 9/12 V and is not a 20 V
design.

## JLCPCB assembly (controller)

Economic PCBA charges **$3 per unique true Extended line**. Preferred parts
often show as “Extended” in the cart and **do not** get that fee.

**No $3 (Preferred):** D1–D4 B5819WS, D8 BZX84C10, D9 SMAJ15A, R2 49.9 kΩ, U2 STM8.

**$3 each (true Extended):** U1 HUSB238, TPS61165DRVR (one fee for four),
L1–L4 (one fee), J2 USB-C, F1 PTC, U3 USBLC6, R4–R7 820 mΩ.

Leave **J1, J3, J4** unselected and solder the TH headers yourself (avoids
the hand-solder surcharge). The only cart swap that drops a $3 line without
touching copper is **R4–R7 → `C17928` 1 Ω**.

## LED panel

Intent is a **1-layer aluminum** MCPCB: SMT on the copper face, no vias, no
through-hole parts (leads can short to the aluminum). The saved KiCad board
is already electrically single-layer (all F.Cu, no B.Cu copper, no vias) but
still declares two copper layers. Set copper layers to **1** before Gerbers
and order aluminum / 1 layer (typically 1.6 mm, 1 oz, white mask).

Do **not** JLC-assemble this panel. Fab bare aluminum; populate by hand
(preheat / hot plate — the core sinks iron heat).

### Heatsink and camera mount

Selected heatsink: **Advanced Thermal Solutions
`ATS-CPX070070025-136-C1-R0`**. It is a 70 × 70 × 25 mm blue-anodized,
coarse-pitch X-cut aluminum heatsink. ATS specifies **2.17 °C/W at 100 LFM**
(~0.5 m/s) airflow; it does not publish a natural-convection value. The LED
panel is expected to put about **10–12 W of heat** into the MCPCB (15.4 W
electrical LED input less emitted light). Thus this heatsink is suitable with
intentional airflow, but is not a qualified passive full-brightness solution.
For a passive revision, target a heatsink rated **≤2.0 °C/W natural
convection** (≤1.5 °C/W preferred for a warm grow enclosure).

The ATS part has a four-corner **63.0 × 63.0 mm** mounting pattern. Direct
MCPCB mounting uses four **3.2 mm NPTH** clearance holes on that grid (centres
3.5 mm from the edges of a 70 mm square), M3 screws, and a thin layer of
thermal grease/TIM against the flat heatsink base. These are mechanical holes,
not component leads: keep front copper clear and insulate the LED-side screw
heads from copper/exposed core with shoulder washers. The current board has no
mounting holes; add them through the KiCad workflow before relying on this
mounting method.

The **1/4-20 UNC camera interface** belongs on a separate metal crossbar or
saddle bolted to the ATS factory holes, not in the heatsink or MCPCB. Capture
a steel 1/4-20 coupling nut in that crossbar for adequate thread engagement;
include an anti-rotation feature and a separate safety tether for overhead use.

This layout: **16× 3030 2-pad** whites (asymmetric A/K) and **4× 3535-3P**
reds (A/K + isolated thermal; pad 3 is unnetted). A 3030 *outline* is not a
3030 *footprint*.

### Whites

Drive ~0.244 A needs a **3 V, ~350–400 mA** 3030. Not mid-power 65 mA parts.

| MPN | Use |
|---|---|
| Cree `JK3030AWT-P-U40EA0000-N0000001` (`C17398997`) | 90 CRI, ~126 lm @ 350 mA. On the LCSC leftover list. |
| Cree `JK3030AWT-P-H40EA0000-N0000001` | Same 3 V / 400 mA max, **80 CRI**, ~154 lm @ 350 mA (~22% more light). Better for plants. |
| Everlight `XI3030P/KKE-5M4014034Z35/2N` | Still manufactured. 4000 K, 80 CRI, 3.05 V, 145 lm @ 350 mA, **max 350 mA**. 3.24×3.00 mm; check pads. |

**Cree JK3030 3 V P class is EOL** (PCN-06128, last-time buy 2026-09-04).
Remaining Digi-Key/Mouser reels are leftover. Cree’s named substitute is
`JB3030SWT-J-H40EA0000-NZ000001` (JB3030S 3 V J class): 65 mA test / 480 mA
max, **757 / Samsung-style pads**, not a 1:1 clone of JK3030 P.

Do not buy 6 V Cree `…EB…` 3030s (Vf ~6.1 V; four of those plus a red blow
the string budget and the 244 mA drive). Do not use Samsung LM301H / EVO
(EOL, and typically max ~200 mA).

### Reds

| MPN | Use |
|---|---|
| Silverlight `M3535N1IRG6U12-660NM` (`C2833507`) | Generic 3535 on LCSC. Weak horticulture part. |
| Cree XP-E2 Photo Red `XPEBPR-L1-0000-00D01` | **Still active.** 660 nm, 3.45 mm, ~2.05 V, 350 mA test / 1 A max. Closest 3535-class upgrade; confirm A/K vs the open thermal pad. |
| ams OSRAM `GH CSSRM6.24-VAA3-1-1-700-R33` | Best 660 nm (~4 µmol/J class). **3.0×3.0 mm ceramic + ~2.2 mm dome, 3-pad (A/K/thermal).** Will not solder to the 2-pad white 3030 or the 3535-3P. |

Samsung LH351H 660 nm is EOL (same lighting-LED shutdown: last ship 2025-12-31).

### Next revision — one footprint

To actually share lands, put the whole panel on **Oslon Square** (ceramic
3-pad 3.0 mm): red `GH CSSRM6.24` + white `GW CSSRM4.HW`. Same stencil,
same pad. Those whites are ~700 mA class and ~$1.50; at 0.244 A they run
cool but you pay 1 W prices. Do not mix Oslon Square pads with
Cree/Everlight 2-pad 3030 whites.

## Firmware notes

- Remap STM8 **OPT2 AFR0** so TIM1_CH1 appears on `PC6`. Default pinout does
  not.
- Hold CTRL low through reset and PD negotiation. Read the contract before
  enabling PWM.
- ~20 kHz PWM is a reasonable starting point; confirm startup does not enter
  TPS61165 EasyScale.
- Four channels at once, on the intended heatsink, after thermal equilibrium.

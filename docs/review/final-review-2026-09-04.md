# Grow-light — final-design review, 2026-09-04

## Verdict

The saved boards are routed and DRC-clean under their configured rules. I found no new confirmed signal-wiring fault. The earlier WIP connectivity and placement issues have been addressed. This is a credible prototype candidate, but not yet a fully qualified production design: resolve the assembly/BOM and mechanical questions below before ordering, and validate startup, transient behavior, and temperature on hardware.

No schematic or PCB was changed during this review. Review artifacts were generated in this directory.

## Scope and check results

Reviewed the main schematic, all four instances of its LED-driver subsheet, the LED-panel schematic, exported connectivity, and saved PCB copper/placement views. Both automated design reviews completed without missing-sheet diagnostics.

| Check | Main board | LED board |
|---|---:|---:|
| DRC violations reported | 0 | 0 |
| Unrouted connections reported | 0 | 0 |
| Schematic-parity findings reported | 0 | 0 |
| ERC errors | 5 | 0 |
| ERC warnings | 7 | 0 |
| PCB footprints | 64 | 21 |

Structural connectivity checks found no orphan wires or unintended shorts. Generic manufacturing checks passed, but these do not establish suitability of a particular metal-core fabrication process.

The live KiCad IPC interface failed its document queries. File-based checks and exports succeeded; this review covers saved files, not unsaved editor changes. Exact per-net trace/pad queries through IPC and a complete manufacturer-land-pattern comparison were therefore not completed. DRC cleanliness is not a thermal, EMC, surge, or assembly certification.

## Confirmed improvements

- PC3 and PC4 now connect to the two indicator LEDs.
- R23 provides a 10 kΩ pulldown on the shared PC6/PWM-to-CTRL net.
- HUSB238 ISET now uses R19 (10 kΩ) plus R8 (470 Ω) in series: 10.47 kΩ, approximately 0.29% below the nominal 10.5 kΩ setting. This addresses the earlier resistor discussion without a new resistor value in the BOM.
- D9 is now an SMAJ15A on fused VBUS, with cathode to VBUS and anode to ground.
- The gate pullup, series gate resistor, and gate-source Zener are connected coherently around Q1.
- The four boost channels include their input/output capacitors, 220 nF compensation capacitors, and 0.82 Ω sense resistors.
- MCU VCAP has C16 (1 µF); supply bypassing and reset components are present.
- Main-board and LED-board J1 pin assignments agree: pins 1–8 are 2+, 1+, 2−, 1−, 3−, 4−, 3+, 4+.
- Previously unfinished component placement and routing are no longer reported as outstanding.

The HUSB238 resistor selections should remain tied to the exact ordered device variant. See the [Hynetek datasheet](https://www.hynetek.com/uploadfiles/site/219/news/c16af076-8c40-4e8d-b126-b4f9b83e86ea.pdf).

## Before ordering

### 1. Lock the actual assembly parts and footprints

U1 still has the placeholder-style value `HUSB238_xxxDD`; select the exact orderable suffix and confirm its package and startup behavior. The driver symbol identifies the DRV package, but an explicit orderable MPN should also be recorded for all four instances.

The panel's generic LED values are not enough to specify an assembly. Record manufacturer MPNs and supplier codes, then check anode/cathode numbering, body orientation, and the red LED's third pad against the manufacturer's drawing. This review does not certify the imported EasyEDA footprints.

The previously documented white part, Cree `JK3030AWT-P-U40EA0000-N0000001`, is from the JK3030 3 V family, whose maximum current is 400 mA—not the 240 mA rating of some other 3030 variants. Thus the nominal approximately 244 mA drive is not inherently excessive for that exact white LED. It still requires thermal derating. Confirm that this is what will actually be populated. See the [Cree J Series 3030 datasheet](https://downloads.cree-led.com/files/ds/j/JSeries-3030.pdf).

### 2. Settle panel fabrication, heatsinking, and mounting

The LED board remains configured as a two-copper-layer board, while the project intent calls for a single-layer aluminum panel. Explicitly reconcile the design and fabrication stackup; a generic fabrication check cannot select or validate the metal-core construction for you.

Neither board currently provides dedicated mounting holes. That can be intentional, but decide how the controller is retained and how the LED panel makes reliable thermal contact to its heatsink. Confirm insulation, connector clearance, and strain relief before freezing the outlines. Avoid relying on the cable or USB connector to support the board mechanically.

The controller's USB connector courtyard extends approximately 0.25 mm past the outline. That is not automatically an error for an edge connector; verify the shell position against the enclosure and manufacturer's mechanical drawing. The LED connector's distance from the edge is merely an automated placement heuristic, not a defect for a vertical connector.

### 3. Clean up ERC deliberately

The main-board five errors are power-source declarations on the power network, not newly discovered disconnected signals. Its seven warnings concern unspecified electrical pin types on S1/S2 and U7.

Use appropriate power flags on externally supplied/passive-fed rails and correct the switch/regulator symbol pin types through the library workflow. Do not simply disable these ERC checks globally. Re-run ERC after cleanup.

The automated review also labels five decoupling items as critical. Manual connectivity review does not support adding those parts blindly: C16 supplies VCAP, C1 bypasses U1 VIN, the USB bulk capacitance is downstream of F1, and U3 pin 5 is deliberately unused. In particular, do not connect the USBLC6 clamp-supply pin to negotiated 12 V merely to satisfy that heuristic.

## Firmware and bench validation

### Startup and PWM

PC6 needs the STM8 alternate-function remap to expose TIM1_CH1: set OPT2 AFR0 appropriately; retain the I²C mapping on PB4/PB5. Merely starting a timer will not put its output on default PC6. See the [STM8S003 datasheet](https://www.st.com/resource/pio/datasheet/stm8s003f3.pdf).

Keep CTRL low during reset and power negotiation. Confirm the intended PD supply before enabling substantial LED power; do not assume every source offers 12 V. Test cold start, reset, reconnect, unsupported adapters, and supply loss. No firmware implementation was available to validate.

A roughly 20 kHz PWM is a reasonable starting point. Verify startup timing does not inadvertently enter EasyScale mode. The nominal channel current is 0.2/0.82 ≈ 244 mA; including a 1% resistor and the specified reference tolerance gives approximately 237–251 mA. Four simultaneous channels must be tested. See the [TPS61165 datasheet](https://www.ti.com/lit/ds/symlink/tps61165.pdf).

### Transient protection

Moving D9 after the fuse is an improvement, but an SMAJ15A is not a precise 15 V limiter. Its listed high-current clamp voltage is about 24.4 V, whereas TPS61165 VIN has a 20 V absolute maximum. These specifications describe a protection gap, not a prediction that normal startup will reach 24.4 V. Q1/HUSB238 shutdown helps but does not establish fast-transient protection by itself.

Measure VBUS and switched VIN during hot-plug and negotiation, including the intended cable/source combinations. If guaranteed surge survival is a requirement, qualify a coordinated clamp/disconnect solution; the existing TVS alone is not sufficient evidence. The exact TVS datasheet should be retained with the final BOM.

### Layout and temperature

The boost components are grouped compactly, with short local switching connections and broad ground copper. Preserve that arrangement. Confirm exposed-pad soldering and a short ground return around each driver; thermal vias to the bottom plane are an improvement to consider where practical.

The 40 V boost rectifiers are not automatically wrong: TI's reference designs also use 40 V parts. Their margin against open-string overshoot and switching ringing still needs verification; a higher rating is optional additional margin, not a confirmed required fix. Keep oscilloscope probe ground connections short.

Measure panel temperature, driver/inductor/diode temperature, and U7 temperature at full load and maximum intended ambient after thermal equilibrium. U7 dissipates approximately (12−3.3)×I: 174 mW at 20 mA or 348 mW at 40 mA. Check actual consumption rather than assuming the LDO is cool because it is rated for the input voltage.

## Suggested first-power sequence

1. Inspect polarity, solder bridges, exposed pads, and supply resistance before power.
2. With LEDs disabled, verify negotiated VBUS, switched VIN, 3.3 V, reset, programming, and the CTRL-low default.
3. Start with low brightness; measure each string's current and output voltage.
4. Test all channels at full brightness on the intended heatsink, watching input current and temperature.
5. Check hot-plug/reset recovery and an open-string condition without exceeding instrument ratings. Do not hot-plug the LED harness as a routine operating procedure.

## Evidence

- `final-m.net`, `final-l.net`: exported connectivity used for manual cross-checks.
- `final-m-schematic.png`, `final-l-schematic.png`: schematic exports.
- `final-F.Cu.svg/png`, `final-B.Cu.svg/png`: controller copper views.
- `final-l-copper.svg`: panel copper export.
- `final-main-drc.json`: final all-severity controller DRC result.

This report supersedes the earlier WIP review's outstanding-wiring assessment; it does not replace prototype testing or final assembly-package verification.

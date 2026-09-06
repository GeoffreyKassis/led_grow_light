# Grow-light

Two KiCad projects: `MAIN_BOARD/` (controller) and `LED_BOARD/` (LED panel). Docs and BOM live in `docs/`.

## KiCad files are not text

Never edit `*.kicad_sch`, `*.kicad_pcb`, `*.kicad_pro`, `*.kicad_sym`, `*.kicad_mod`, `fp-lib-table`, or `sym-lib-table` with file-writing tools. All schematic and PCB changes go through Konnect MCP. If Konnect is unavailable, stop and say so — do not patch the files.

## One writer at a time

Konnect is not single-instance. Each Grok/Codex session starts its own Konnect process. The clash is the project files.

- **One agent writes** this project's schematics or PCBs at a time.
- Extra sessions may read, search JLCPCB, review nets, and export.
- Do not run Grok and Codex (or two Grok sessions) both placing parts, routing, or saving the same board.
- One KiCad window per board. Do not open the same project twice.

## Locks and live KiCad

- Schematic writes: if `~*.kicad_sch.lck` exists, close that sheet in eeschema first. Konnect refuses to overwrite a locked schematic.
- Live PCB edits: leave that board open in **one** KiCad window with the API enabled (`Edit → Preferences → Plugins → Enable KiCad API`).
- IPC socket: `ipc://C:\users\geoff\appdata\local\temp\kicad\api.sock` (also in `konnect.toml` and Konnect `settings.json`).

## Konnect on Grok

`konnect.toml` in this repo sets `eager_toolsets = true` because Grok caches the first `tools/list` and will not see tools added later by `load_toolset`. If Konnect tools look missing, restart the session. Do not fall back to editing KiCad files as text.

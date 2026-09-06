"""Rasterize only Konnect-exported SVGs for review; never reads KiCad sources."""
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import resvg_py
import re
ET.register_namespace('', 'http://www.w3.org/2000/svg')

src = Path(sys.argv[1])
root = ET.parse(src).getroot()
if len(sys.argv) == 6:
    x, y, w, h = map(float, sys.argv[2:])
    root.set('viewBox', f'{x} {y} {w} {h}')
    root.set('width', f'{w}mm')
    root.set('height', f'{h}mm')
svg = src.read_text(encoding='utf-8')
if len(sys.argv) == 6:
    svg = re.sub(r'viewBox="[^"]+"', f'viewBox="{x} {y} {w} {h}"', svg, count=1)
    svg = re.sub(r'width="[^"]+" height="[^"]+"', f'width="{w}mm" height="{h}mm"', svg, count=1)
src.with_suffix('.png').write_bytes(resvg_py.svg_to_bytes(
    svg_string=svg, width=2200, dpi=96,
    background='white'))
print(src.with_suffix('.png'))

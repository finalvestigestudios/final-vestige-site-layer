#!/usr/bin/env python3
"""Python -I entrypoint for the R330 private, read-only export custody gate."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / 'preparedness' / 'tools'
if TOOLS.is_symlink() or not TOOLS.is_dir() or (TOOLS / 'r330_native_export_parity_hold.py').is_symlink():
    raise SystemExit('INVALID_HARD_HOLD: untrusted Preparedness tools checkout')
sys.path.insert(0, str(ROOT))
from preparedness.tools import r330_native_export_parity_hold as gate
raise SystemExit(gate.main())

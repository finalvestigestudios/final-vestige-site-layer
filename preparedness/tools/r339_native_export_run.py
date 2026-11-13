#!/usr/bin/env python3
"""R339 isolated Python -I read-only private draft destination entrypoint."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / 'preparedness' / 'tools'
if (ROOT.is_symlink() or TOOLS.is_symlink() or not TOOLS.is_dir()
        or (TOOLS / 'r339_export_draft_safety_gate.py').is_symlink()):
    raise SystemExit('INVALID_HARD_HOLD: untrusted Preparedness tools checkout')
sys.path.insert(0,str(ROOT))
from preparedness.tools import r339_export_draft_safety_gate as gate
raise SystemExit(gate.main())

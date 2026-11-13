#!/usr/bin/env python3
"""R344 isolated, read-only source identity validation entrypoint."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
if ROOT.is_symlink() or (ROOT/'preparedness'/'tools').is_symlink():
    raise SystemExit('INVALID_HARD_HOLD: untrusted source checkout')
sys.path.insert(0,str(ROOT))
from preparedness.tools.r344_source_url_identity_citation_hold import main

if __name__=='__main__':
    raise SystemExit(main())

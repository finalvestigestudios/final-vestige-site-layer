#!/usr/bin/env python3
"""Read-only R345 canonical-source conflict quarantine; no QD/public approval."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if ROOT.is_symlink() or (ROOT / "preparedness" / "tools").is_symlink():
    raise SystemExit("INVALID_HARD_HOLD: untrusted source checkout")
sys.path.insert(0, str(ROOT))

from preparedness.tools.r345_conflicted_source_claim_quarantine import main

if __name__ == "__main__":
    raise SystemExit(main())

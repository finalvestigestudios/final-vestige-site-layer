#!/usr/bin/env python3
"""Isolated (-I) entrypoint for R343 on an authenticated native checkout.

Import paths are anchored to the script's own repository, never a user
working directory. This wrapper never grants review or publishing approval.
"""
from __future__ import annotations
from pathlib import Path
import sys

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY))
from preparedness.tools.r343_claim_citation_review_crosswalk_hold import main

if __name__ == '__main__':
    raise SystemExit(main())

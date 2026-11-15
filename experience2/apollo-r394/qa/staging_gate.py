#!/usr/bin/env python3
"""R394 read-only staging gate; retains every inherited R391–R393 guard.

The R392 version of staging_smoke.py calls its module-level verify_page() once
for JS and once for no-JS, so this exact injection is invoked in both contexts.
Do not substitute the earlier R391 artifact version (which lacked the call).
"""
import sys
from pathlib import Path
from visibility_custody import verify_page

STAGING_QA=Path(__file__).resolve().parents[2]/'apollo-r389'/'qa'
if str(STAGING_QA) not in sys.path:sys.path.insert(0,str(STAGING_QA))
import staging_smoke

# Refuse to silently weaken custody coverage if the inherited harness changes.
import inspect
source=inspect.getsource(staging_smoke.main)
if source.count('verify_page(page)')!=1 or source.count('verify_page(nojs)')!=1:
    raise SystemExit('HARD HOLD: inherited staging harness no longer verifies JS + no-JS source custody')
staging_smoke.verify_page=verify_page

if __name__=='__main__': staging_smoke.main()

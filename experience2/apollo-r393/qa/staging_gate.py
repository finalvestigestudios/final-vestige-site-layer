#!/usr/bin/env python3
"""HARD-HOLD staging entry point extending R392/R391 with exact topology QA.

Reuses existing deny-by-default real HTTPS/GET/HEAD boundary and genuine pinned
axe-core preflight without altering the inherited harness or active release lanes.
"""
import sys
from pathlib import Path
from topology import verify_page

STAGING_QA=Path(__file__).resolve().parents[2]/'apollo-r389'/'qa'
if str(STAGING_QA) not in sys.path:
    sys.path.insert(0,str(STAGING_QA))
import staging_smoke
# The staging harness calls this verifier on BOTH JavaScript and no-JavaScript
# page instances; preserve all inherited security, stylesheet, axe and vitals gates.
staging_smoke.verify_page=verify_page
if __name__=='__main__':
    staging_smoke.main()

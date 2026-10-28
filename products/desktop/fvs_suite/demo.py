"""Manual local launch: python -m fvs_suite.demo ledger"""
import sys
from .app import run, APPS
if __name__ == "__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in APPS:
        raise SystemExit("Choose: " + ", ".join(APPS))
    run(sys.argv[1])

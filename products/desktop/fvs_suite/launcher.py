"""Shared launcher with offline packaged-binary self-test."""
from __future__ import annotations

import sys
import traceback

from . import __version__


def launch(app_id: str) -> None:
    args = sys.argv[1:]
    if args == ["--smoke-test"]:
        try:
            from .smoke import run_smoke
            outputs = run_smoke(app_id)
            if not outputs:
                raise RuntimeError("No smoke-test output")
        except Exception:
            traceback.print_exc()
            raise SystemExit(1)
        raise SystemExit(0)
    if args == ["--version"]:
        print(__version__)
        return
    if args:
        raise SystemExit("Unsupported arguments. Use --version or --smoke-test.")

    from .app import run
    run(app_id)

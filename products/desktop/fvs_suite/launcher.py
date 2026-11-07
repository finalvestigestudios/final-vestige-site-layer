"""Shared launcher with offline packaged-binary self-test."""
from __future__ import annotations

import sys

from . import __version__
from .offline_network import install_offline_guard


def launch(app_id: str) -> None:
    # All six packaged EXEs: fail before GUI or smoke if offline guard fails.
    install_offline_guard()
    args = sys.argv[1:]
    if args == ["--smoke-test"]:
        # Smoke failures may contain private financial paths, invoice IDs, or
        # source data in their exception text *and* chained traceback. Never
        # print or chain them into CI logs or an operator's terminal.
        successful = False
        try:
            from .smoke import run_smoke
            successful = bool(run_smoke(app_id))
        except Exception:
            pass
        # Raise outside the handler: preserve neither __context__ nor __cause__.
        # Keep the same zero/nonzero success contract and no-GUI dispatch.
        if not successful:
            raise SystemExit(
                "Final Vestige Labs smoke test failed; no private diagnostics printed"
            )
        raise SystemExit(0)
    if args == ["--version"]:
        print(__version__)
        return
    if args:
        raise SystemExit("Unsupported arguments. Use --version or --smoke-test.")

    from .app import run
    run(app_id)

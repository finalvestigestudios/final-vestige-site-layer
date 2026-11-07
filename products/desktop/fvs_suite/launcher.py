"""Shared launcher with offline packaged-binary self-test."""
from __future__ import annotations

import sys

from . import __version__
from .offline_network import install_offline_guard
from .background_privacy import install_background_privacy


def launch(app_id: str) -> None:
    # All six packaged EXEs: fail before GUI or smoke if offline guard fails.
    # Audit-hook initialization can fail with private filesystem paths in the
    # exception message or traceback. Fail CLOSED without printing/chaining it.
    # Do not trap BaseException: KeyboardInterrupt and SystemExit retain their
    # normal interpreter semantics.
    guard_ready = False
    try:
        install_offline_guard()
        install_background_privacy()
        guard_ready = True
    except Exception:
        pass
    # Exit *outside* the handler: otherwise __context__ retains private data.
    if not guard_ready:
        raise SystemExit(
            "Final Vestige Labs security startup failed; no private diagnostics printed"
        )
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

    # Synchronous GUI imports and entrypoint failures can expose customer
    # paths, ledger IDs or financial rows in interpreter tracebacks.
    # Keep only a fixed failure diagnostic at the executable entry boundary.
    # Raising OUTSIDE the except also prevents private exception retention in
    # SystemExit.__context__. Preserve KeyboardInterrupt and SystemExit.
    gui_finished = False
    try:
        from .app import run
        run(app_id)
        gui_finished = True
    except Exception:
        pass
    if not gui_finished:
        raise SystemExit(
            "Final Vestige Labs application failed; no private diagnostics printed"
        )

"""Fixed-text GUI diagnostics for private, local-first financial workflows.

Never interpolate an exception, filename, CSV cell, entitlement, or filesystem
path into a dialog or status line. Engine exceptions may legitimately include
user-controlled record values, report names, or operating-system paths.

These messages are intentionally less detailed than developer exceptions;
there is no automatic telemetry or private-data logging fallback.
"""
from __future__ import annotations

_GUIDANCE = {
    "generate": "Check the input files, required columns, dates, amounts, and output folder.",
    "report": "Check that the selected report belongs to this product and has valid evidence.",
    "review": "Check the selected exception, reviewer details, and local review evidence.",
    "export": "Check the review evidence and select an existing, writable output folder.",
    "backup": "Check the local evidence, passphrase, and backup destination.",
    "restore": "Check the encrypted archive, passphrase, and restore destination.",
}


def safe_error_message(exc: BaseException, *, operation: str) -> str:
    """Return solely fixed safe text; never call str/repr on ``exc``.

    A distinct action gives actionable next steps without revealing private
    filenames or user-controlled exception messages. Unsupported actions
    deliberately fail closed rather than accidentally echoing unknown text.
    """
    if operation not in _GUIDANCE:
        raise ValueError("Unsupported UI error operation")
    if isinstance(exc, UnicodeError):
        summary = "The selected file has an unsupported text encoding. Export as UTF-8."
    elif isinstance(exc, PermissionError):
        summary = "The file operation was denied. Check local permissions and open-file locks."
    elif isinstance(exc, FileNotFoundError):
        summary = "A required local file was not found. Select an existing file."
    elif isinstance(exc, IsADirectoryError):
        summary = "A regular file was expected, but a directory was selected."
    elif isinstance(exc, OSError):
        summary = "A local file operation failed. Check file availability and free space."
    elif isinstance(exc, ValueError):
        summary = "The selected data or evidence did not pass validation."
    else:
        summary = "The operation could not be completed."
    return summary + " " + _GUIDANCE[operation]

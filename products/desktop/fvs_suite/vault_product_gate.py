"""Fail-closed product binding for locally restored premium evidence archives.

Archive authentication alone does not prove the caller is in the matching
premium review workflow. GUI callers supply their already-entitled product;
this guard compares it with the authenticated vault payload *before* any
plaintext restore directory is created. This is not DRM or an authorization
substitute: the GUI must separately revalidate signed entitlement.
"""
from __future__ import annotations

_ALLOWED = frozenset(("grants", "procurement"))


def require_restore_product(archive_product: object,
                            expected_product: str | None = None) -> str:
    """Return a validated archive product or reject a cross-product restore.

    ``None`` is retained for backward-compatible, trusted direct API callers.
    A licensed GUI MUST pass its own scoped product; never infer entitlement
    from the archive, its filename or its symmetric passphrase.
    """
    if type(archive_product) is not str or archive_product not in _ALLOWED:
        raise ValueError("Invalid premium evidence product")
    if expected_product is not None:
        if type(expected_product) is not str or expected_product not in _ALLOWED:
            raise ValueError("Invalid premium review product scope")
        if archive_product != expected_product:
            raise ValueError("Encrypted evidence does not match this premium review product")
    return archive_product

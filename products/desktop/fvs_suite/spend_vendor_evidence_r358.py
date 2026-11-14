"""Retain significant Unicode boundary characters in SpendMap vendor evidence.

Vendor matching keys intentionally discard non-ASCII characters. This helper
preserves the original distinct, readable labels for human collision review;
it does not authenticate the CSV or authorize any compliance decision.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Iterable, Mapping

from .audit_display import visible_identity_label
from .review import ascii_case_identity

# Compatibility with existing CSV import: only ordinary ASCII boundary
# whitespace is insignificant to *matching*, not to source-label evidence.
_ASCII_BOUNDARY_WHITESPACE = " \t\r\n\v\f"

# Every accepted import is limited to 64 MiB of source bytes, but repeating a
# vendor-wide label list in every category/month bucket could amplify that to
# hundreds of MiB of CSV/GUI text. Keep the review display bounded. A digest
# covers every distinct source label whenever any display text is omitted.
_MAX_LABEL_DISPLAY_CHARS = 1_024
_MAX_LABEL_PREFIX_CHARS = 64
_MAX_PREVIEW_LABELS = 32
_MAX_PREVIEW_TEXT_CHARS = 8_000
_MAX_REPORT_TEXT_CHARS = 8_192
_LABELS_DIGEST_DOMAIN = b"FVS-SPEND-RAW-VENDOR-LABELS-v1\n"
_ERROR = "Invalid SpendMap original vendor label evidence"


def _visible_vendor_label_preview(value: str) -> tuple[str, bool]:
    """Return full rendered text if small, else a bounded and marked prefix."""
    if len(value) <= _MAX_LABEL_DISPLAY_CHARS:
        visible = visible_identity_label(value)
        if len(visible) <= _MAX_LABEL_DISPLAY_CHARS:
            return visible, False
    return (visible_identity_label(value[:_MAX_LABEL_PREFIX_CHARS])
            + r"\u[LABEL_PREFIX_ONLY]", True)


def _all_original_labels_digest(ordered: list[str]) -> str:
    """Hash complete distinct native originals with collision-free framing."""
    digest = sha256(_LABELS_DIGEST_DOMAIN)
    for value in ordered:
        invalid_utf8 = False
        try:
            data = value.encode("utf-8")
        except UnicodeError:
            invalid_utf8 = True
        if invalid_utf8:
            # Raise outside the UnicodeError handler: no private source may
            # survive via the replacement error's __context__ chain.
            raise ValueError(_ERROR)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def spend_vendor_evidence(
    rows: Iterable[Mapping[str, str]],
) -> tuple[bool, int, str]:
    """Return (needs identity review, ASCII-case variants, bounded label evidence).

    Matching stays unchanged; source labels remain exact within the visible
    preview. Larger labels and high-cardinality clusters are explicitly marked
    as partial and include a domain-separated digest of *all* distinct raw
    labels, which reviewers can recompute against the SHA-bound source file.
    A digest is not a signature, provenance guarantee, or compliance finding.
    """
    originals: set[str] = set()
    for row in rows:
        original = row.get("vendor")
        if type(original) is not str:
            raise ValueError("Spend vendor evidence requires native source text")
        if original.strip(_ASCII_BOUNDARY_WHITESPACE):
            originals.add(original)

    identities = {ascii_case_identity(value.strip(_ASCII_BOUNDARY_WHITESPACE))
                  for value in originals}
    ordered = sorted(originals, key=lambda value: (value.casefold(), value))
    visible: list[str] = []
    displayed_chars = 0
    any_truncated = False
    for value in ordered[:_MAX_PREVIEW_LABELS]:
        label, truncated = _visible_vendor_label_preview(value)
        required = len(label) + (2 if visible else 0)
        if required > _MAX_PREVIEW_TEXT_CHARS - displayed_chars:
            break
        visible.append(label)
        displayed_chars += required
        any_truncated |= truncated
    omitted = len(ordered) - len(visible)
    if omitted or any_truncated:
        marker = (r"\u[PREVIEW_ONLY:shown=" + str(len(visible))
                  + ":omitted=" + str(omitted)
                  + ":sha256=" + _all_original_labels_digest(ordered) + "]")
        visible.append(marker)
    labels = "; ".join(visible)
    if len(labels) > _MAX_REPORT_TEXT_CHARS:
        raise ValueError(_ERROR)  # Fail closed if internal budgets diverge.
    return (len(identities) > 1, len(identities), labels)

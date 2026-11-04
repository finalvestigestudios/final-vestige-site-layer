"""Fail-closed pre-release *visible text* policy for the six-app Labs catalog.

This is an additional source-draft gate, not a browser accessibility audit,
license/entitlement check, malware scan, or authorization to publish. It never
logs submitted text (including accidentally pasted confidential download URLs).
"""
from __future__ import annotations

import re
import unicodedata

from catalog_fragment_custody_r189 import check_fragmented_claims

# All text from HTMLParser.handle_data is joined without delimiters, so link
# fragments concealed across innocent inline tags do not evade this check.
_URI = re.compile(r"(?:https?|ftps?|file|data|javascript|mailto|s3|gs):|www\.", re.I)
_ARTIFACT = re.compile(r"\.(?:exe|msi|msix|msixbundle|appx|zip|7z|rar|dmg|pkg)(?:\b|$)", re.I)
_RELEASE = re.compile(
    r"\b(?:download|buy|purchase|get)\s+(?:now|here|today)\b"
    r"|\bavailable\s+(?:now|today|for\s+download|for\s+purchase)\b"
    r"|\b(?:public|instant|direct)\s+download\b"
    r"|\b(?:released|on\s+sale|for\s+sale)\b",
    re.I,
)
_FAILURE = "Catalog visible copy violates pre-release publication hold"


def _scan_rendered_copy(chunks: list[str]) -> None:
    """Scan one bounded text representation without logging original text."""
    visible = "".join(chunks)
    if len(visible) > 81920:
        raise ValueError(_FAILURE)
    for ch in visible:
        category = unicodedata.category(ch)
        # Unicode default-ignorable format controls include zero-width and
        # bidi markers that can disguise public release claims or destinations.
        # Preserve ordinary line breaks/tabs in source text.
        if category in ("Cf", "Cs", "Cc", "Zl", "Zp") and ch not in "\r\n\t":
            raise ValueError(_FAILURE)
    compact = "".join(ch for ch in visible if not ch.isspace())
    spaced = " ".join(chunks)
    if (_URI.search(compact) or _ARTIFACT.search(compact)
            or _ARTIFACT.search(spaced) or _RELEASE.search(spaced)):
        raise ValueError(_FAILURE)
    check_fragmented_claims(chunks)


def check_visible_hold(chunks: list[str]) -> None:
    """Raise a text-private ValueError if a draft exposes destinations/claims.

    ``chunks`` must be *only* decoded visible HTML text nodes, not raw HTML or
    Gutenberg comments. The structural catalog gate separately approves the
    sole contact anchor. This fails closed for suspicious links/artifacts even
    when rendered as plain text rather than actual <a href> anchors.
    """
    if type(chunks) is not list or len(chunks) > 10000:
        raise ValueError(_FAILURE)
    if any(type(part) is not str for part in chunks):
        raise ValueError(_FAILURE)
    _scan_rendered_copy(chunks)
    # NFKC folds fullwidth/circled/math-alphanumeric release words, installer
    # extensions and scheme punctuation. Only the *review copy* is normalized:
    # the tracked Gutenberg source remains byte-for-byte untouched. Preserve
    # HTMLParser's original node boundaries so R189 still finds split words.
    normalized = [unicodedata.normalize("NFKC", part) for part in chunks]
    if normalized != chunks:
        _scan_rendered_copy(normalized)

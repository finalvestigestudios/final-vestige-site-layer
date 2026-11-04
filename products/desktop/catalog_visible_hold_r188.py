"""Fail-closed pre-release *visible text* policy for the six-app Labs catalog.

This is an additional source-draft gate, not a browser accessibility audit,
license/entitlement check, malware scan, or authorization to publish. It never
logs submitted text (including accidentally pasted confidential download URLs).
"""
from __future__ import annotations

import re
import unicodedata

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
    # Whitespace-separated schemes/extensions are not safe either. URL text
    # split across <strong> or WordPress blocks must still fail closed.
    compact = "".join(ch for ch in visible if not ch.isspace())
    normalized = " ".join(visible.split())
    if _URI.search(compact) or _ARTIFACT.search(compact) or _RELEASE.search(normalized):
        raise ValueError(_FAILURE)

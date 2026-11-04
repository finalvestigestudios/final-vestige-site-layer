"""Fail closed on pre-release claims split across rendered HTML text nodes.

R188 checks joined and spaced text, but neither sees every placement of a
markup boundary inside a word *and* next to another word. R189 treats each
parser data-node boundary as an ambiguous separation without printing text.
This is a static draft safeguard, not authorization to publish any product.
"""
from __future__ import annotations

import re

_NODE = "\ue000"  # internal-only separator; forbidden in source text
_FAILURE = "Catalog fragment custody violates pre-release publication hold"
_MAX_CHUNKS = 10000
_MAX_CHARS = 81920


def _word(token: str) -> str:
    # Only developer-controlled ASCII literals reach this function.
    return (re.escape(_NODE) + "*").join(re.escape(char) for char in token)


# A node boundary can represent the middle of a split word OR a word break.
# Real visible spaces are preserved; no combinatorial segmentation search.
_SEPARATION = r"(?:\s|" + re.escape(_NODE) + r")+"
_END = r"(?=$|\W|" + re.escape(_NODE) + r")"

_RELEASE_PHRASES = (
    ("download", "now"), ("download", "here"), ("download", "today"),
    ("buy", "now"), ("buy", "here"), ("buy", "today"),
    ("purchase", "now"), ("purchase", "here"), ("purchase", "today"),
    ("get", "now"), ("get", "here"), ("get", "today"),
    ("available", "now"), ("available", "today"),
    ("available", "for", "download"), ("available", "for", "purchase"),
    ("public", "download"), ("instant", "download"),
    ("direct", "download"), ("on", "sale"), ("for", "sale"),
    ("released",),
)
_RELEASE_NODE_RE = tuple(
    re.compile(r"(?<!\w)" + _SEPARATION.join(_word(token) for token in phrase)
               + _END, re.IGNORECASE)
    for phrase in _RELEASE_PHRASES
)
_INSTALLER_EXTENSIONS = ("exe", "msi", "msix", "msixbundle", "appx",
                         "zip", "7z", "rar", "dmg", "pkg")
_ARTIFACT_NODE_RE = re.compile(
    re.escape(".") + re.escape(_NODE) + "*"
    + "(?:" + "|".join(_word(ext) for ext in _INSTALLER_EXTENSIONS) + ")"
    + _END,
    re.IGNORECASE,
)


def check_fragmented_claims(chunks: list[str]) -> None:
    """Reject node-fragmented installer suffixes and availability claims.

    Rejects native-text shape violations before joining; doesn't echo source.
    Uses bounded input and compiled regexes; does not access the filesystem or
    network, make compliance decisions, or modify the user's documents.
    """
    if (type(chunks) is not list or len(chunks) > _MAX_CHUNKS
            or any(type(chunk) is not str for chunk in chunks)):
        raise ValueError(_FAILURE)
    length = 0
    for chunk in chunks:
        length += len(chunk)
        if length > _MAX_CHARS or _NODE in chunk:
            raise ValueError(_FAILURE)
    decorated = _NODE.join(chunks)
    if (_ARTIFACT_NODE_RE.search(decorated)
            or any(pattern.search(decorated) for pattern in _RELEASE_NODE_RE)):
        raise ValueError(_FAILURE)

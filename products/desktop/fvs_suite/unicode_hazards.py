"""Narrow, shared list of visually blank Unicode glyphs in financial evidence.

These characters have non-control Unicode categories and can look like an
empty cell, ordinary whitespace or no character at all in common viewers.
This is a deliberately limited display/reviewer-input guard, not a complete
Unicode confusable detector. Preserve raw source bytes and hashes elsewhere.
"""
from __future__ import annotations


VISUALLY_BLANK_FILLERS = frozenset((
    0x115F,  # HANGUL CHOSEONG FILLER (Lo)
    0x1160,  # HANGUL JUNGSEONG FILLER (Lo)
    0x17B4,  # KHMER VOWEL INHERENT AQ (Mn)
    0x17B5,  # KHMER VOWEL INHERENT AA (Mn)
    0x2800,  # BRAILLE PATTERN BLANK (So)
    0x3164,  # HANGUL FILLER (Lo)
    0xFFA0,  # HALFWIDTH HANGUL FILLER (Lo)
))


def is_visually_blank_filler(character: str) -> bool:
    """Identify explicitly enumerated non-control blank glyphs, without I/O."""
    return ord(character) in VISUALLY_BLANK_FILLERS

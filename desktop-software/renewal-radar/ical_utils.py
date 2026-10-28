"""RFC 5545 iCalendar UTF-8 content-line folding. No external dependencies."""
from __future__ import annotations

from collections.abc import Iterable


def fold_ical_line(line: str) -> list[str]:
    """Fold one logical iCalendar line into lines of at most 75 UTF-8 octets.

    Continuation lines start with a space that counts against the octet limit.
    Folding never splits a multibyte UTF-8 character.
    """
    if not isinstance(line, str) or "\r" in line or "\n" in line:
        raise ValueError("A content line must be a single line of text.")
    folded: list[str] = []
    current: list[str] = []
    octets = 0
    for char in line:
        size = len(char.encode("utf-8"))
        if octets + size > 75:
            folded.append("".join(current))
            current = [" ", char]
            octets = 1 + size
        else:
            current.append(char)
            octets += size
    folded.append("".join(current))
    return folded


def render_ical_lines(lines: Iterable[str]) -> str:
    """Serialize logical lines with RFC 5545 folding and CRLF line endings."""
    return "\r\n".join(part for line in lines for part in fold_ical_line(line)) + "\r\n"

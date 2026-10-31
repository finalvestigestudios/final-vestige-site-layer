#!/usr/bin/env python3
"""Fail-closed citation-token placement guard for Preparedness draft HTML.

Check raw source locations and common *semantic/inline* hidden contexts. This is
not a browser rendering engine or a human claim/safety review. External CSS can
hide content; this guard alone never permits publication.
"""
from __future__ import annotations
from html.parser import HTMLParser
import re

TOKEN = re.compile(r'\{\{cite:([A-Za-z0-9_.-]+)\}\}')
CANDIDATE = re.compile(r'\{\{\s*cite\b', re.IGNORECASE)
# Tags with non-visible/inert/non-editorial text that cannot count as supporting
# an article claim. Other markup is treated as visible text by the parser.
INERT = frozenset({'script', 'style', 'template', 'textarea', 'noscript',
                   'svg', 'math', 'iframe', 'object', 'pre', 'code',
                   'head', 'title', 'select', 'option', 'optgroup',
                   'datalist', 'button'})
VOID = frozenset({'area','base','br','col','embed','hr','img','input','link','meta',
                  'param','source','track','wbr'})
CSS_COMMENT = re.compile(r'/\*.*?\*/', re.DOTALL)


class CitationPlacementHold(ValueError):
    """Citation malformed, invisible in the markup, or outside article prose."""


def _hidden_attributes(attrs: list[tuple[str, str | None]]) -> bool:
    """Reject common semantic or inline-style-hidden citation positions.

    Class-dependent visibility requires trusted browser computed styles; this
    is intentionally NOT sufficient to establish visible or safe public copy.
    """
    for key, value in attrs:
        key = key.lower()
        if key in ('hidden', 'inert'):
            return True  # HTML boolean attr: hidden="false" is still hidden
        if key == 'aria-hidden' and (value or '').strip().lower() == 'true':
            return True
        if key == 'style' and value:
            style = CSS_COMMENT.sub('', value).lower()
            for declaration in style.split(';'):
                if ':' not in declaration:
                    continue
                prop, val = (part.strip() for part in declaration.split(':', 1))
                val = re.sub(r'\s*!important\s*
    def __init__(self, body: str):
        super().__init__(convert_charrefs=False)
        self.body = body
        self.line_starts = [0] + [m.end() for m in re.finditer(r'\n', body)]
        self.positions: list[int] = []
        self.stack: list[tuple[str, bool]] = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, tag in INERT or _hidden_attributes(attrs)))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        tags = [item[0] for item in self.stack]
        if tag in tags:
            # Close named ancestor and all nested scopes. Never discard an
            # invisible outer ancestor before its own matching end tag.
            del self.stack[len(tags)-1-tags[::-1].index(tag):]

    def handle_data(self, data):
        if any(hidden for _, hidden in self.stack):
            return
        line, col = self.getpos()
        if not (1 <= line <= len(self.line_starts)):
            raise CitationPlacementHold('parser location outside frozen HTML')
        start = self.line_starts[line-1] + col
        # HTMLParser's data chunks must be exact raw slices. This also
        # safeguards Unicode codepoint offsets, newlines and entity boundaries.
        if self.body[start:start+len(data)] != data:
            raise CitationPlacementHold('HTML parser/raw-source position mismatch')
        for match in TOKEN.finditer(data):
            self.positions.append(start + match.start())


def verified_citations(body: str) -> list[re.Match]:
    """Return original regex matches iff each token is valid, visible HTML text.

    Handles every full token occurrence, never deduplicating shared sources.
    Raises on partial/misspelled citation starts even when the recognized-token
    count is otherwise unchanged. Does not mutate body or sources.
    """
    if type(body) is not str:
        raise CitationPlacementHold('article HTML must be an original string')
    matches = list(TOKEN.finditer(body))
    starts = [m.start() for m in matches]
    candidates = [m.start() for m in CANDIDATE.finditer(body)]
    if candidates != starts:
        raise CitationPlacementHold('unrecognized or malformed citation token start')
    # For exact offsets in HTMLParser data, these positions are Unicode
    # codepoints (not encoded UTF-8 byte offsets), matching R26 packet claims.
    parser = _TextPositions(body)
    try:
        parser.feed(body)
        parser.close()
    except (ValueError, AssertionError) as exc:
        raise CitationPlacementHold('malformed or unparseable HTML') from exc
    if sorted(parser.positions) != starts:
        raise CitationPlacementHold('citation token in HTML tag, attribute, comment or inert/hidden region')
    return matches
, '', val).strip()
                if (prop == 'display' and val == 'none') or (
                    prop == 'visibility' and val in ('hidden', 'collapse')) or (
                    prop == 'content-visibility' and val == 'hidden') or (
                    prop == 'opacity' and bool(re.fullmatch(r'(?:0+(?:\.0*)?|\.0+)(?:%)?', val))
                ):
                    return True
    return False


class _TextPositions(HTMLParser):
    def __init__(self, body: str):
        super().__init__(convert_charrefs=False)
        self.body = body
        self.line_starts = [0] + [m.end() for m in re.finditer(r'\n', body)]
        self.positions: list[int] = []
        self.stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in self.stack:
            # HTML often contains optional closing tags; close the associated
            # scope and everything nested within it, rather than guessing
            # whether a token inside an open inert element is visible.
            del self.stack[len(self.stack)-1-self.stack[::-1].index(tag):]

    def handle_data(self, data):
        if any(tag in INERT for tag in self.stack):
            return
        line, col = self.getpos()
        if not (1 <= line <= len(self.line_starts)):
            raise CitationPlacementHold('parser location outside frozen HTML')
        start = self.line_starts[line-1] + col
        # HTMLParser's data chunks must be exact raw slices. This also
        # safeguards Unicode codepoint offsets, newlines and entity boundaries.
        if self.body[start:start+len(data)] != data:
            raise CitationPlacementHold('HTML parser/raw-source position mismatch')
        for match in TOKEN.finditer(data):
            self.positions.append(start + match.start())


def verified_citations(body: str) -> list[re.Match]:
    """Return original regex matches iff each token is valid, visible HTML text.

    Handles every full token occurrence, never deduplicating shared sources.
    Raises on partial/misspelled citation starts even when the recognized-token
    count is otherwise unchanged. Does not mutate body or sources.
    """
    if type(body) is not str:
        raise CitationPlacementHold('article HTML must be an original string')
    matches = list(TOKEN.finditer(body))
    starts = [m.start() for m in matches]
    candidates = [m.start() for m in CANDIDATE.finditer(body)]
    if candidates != starts:
        raise CitationPlacementHold('unrecognized or malformed citation token start')
    # For exact offsets in HTMLParser data, these positions are Unicode
    # codepoints (not encoded UTF-8 byte offsets), matching R26 packet claims.
    parser = _TextPositions(body)
    try:
        parser.feed(body)
        parser.close()
    except (ValueError, AssertionError) as exc:
        raise CitationPlacementHold('malformed or unparseable HTML') from exc
    if sorted(parser.positions) != starts:
        raise CitationPlacementHold('citation token in HTML tag, attribute, comment or inert region')
    return matches

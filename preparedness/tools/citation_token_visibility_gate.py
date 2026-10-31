#!/usr/bin/env python3
"""Fail-closed source citation placement guard for Preparedness *draft* HTML.

Only visible-by-static-HTML evidence positions qualify. This is not a CSS
engine, browser QA, claim evaluation or approval to publish. Class-based CSS,
External CSS, media queries, Web Components and dynamically altered visibility require
independent rendered-browser review and remain a release HOLD.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from html import unescape as html_unescape
import re

TOKEN = re.compile(r'\{\{cite:([A-Za-z0-9_.-]+)\}\}')
CANDIDATE = re.compile(r'\{\{\s*cite\b', re.IGNORECASE)
INERT = frozenset({'script', 'style', 'template', 'textarea', 'noscript',
                   'svg', 'math', 'iframe', 'object', 'pre', 'code',
                   'head', 'title', 'select', 'option', 'optgroup',
                   'datalist', 'button'})
VOID = frozenset({'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                  'link', 'meta', 'param', 'source', 'track', 'wbr'})
CSS_COMMENT = re.compile(r'/\*.*?\*/', re.DOTALL)
CSS_ESCAPE = re.compile(r'\\(?:([0-9A-Fa-f]{1,6})(?:\r\n|[\t\n\f\r ])?|([^\r\n\f0-9a-fA-F]))')
CSS_NUMBER = re.compile(r'([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(%)?\Z')
ZERO_LENGTH = re.compile(r'(?i)\s*(?:0+(?:\.0*)?|\.0+)(?:px|pt|pc|em|rem|ex|ch|vw|vh|vmin|vmax|%)?\s*\Z')
NEGATIVE_LENGTH = re.compile(r'(?i)\s*-(?:\d+(?:\.\d*)?|\.\d+)(?:px|pt|pc|em|rem|ex|ch|vw|vh|vmin|vmax|%)\s*\Z')
CSS_UNRESOLVED = re.compile(r'(?i)(?:var|env|attr|calc|clamp|min|max)\s*\(')
CSS_SENSITIVE = frozenset({'display', 'visibility', 'content-visibility', 'opacity',
                           'color', '-webkit-text-fill-color', 'font-size',
                           'line-height', 'filter', '-webkit-filter', 'transform',
                           'translate', 'scale', 'zoom', 'clip', 'clip-path',
                           'mask', 'mask-image', '-webkit-mask', '-webkit-mask-image',
                           'overflow', 'overflow-x', 'overflow-y', 'text-indent',
                           'width', 'height', 'min-width', 'min-height',
                           'max-width', 'max-height', 'block-size', 'inline-size',
                           'max-block-size', 'max-inline-size', 'left', 'right',
                           'top', 'bottom'})
CSS_CLIPPERS = frozenset({'clip', 'clip-path', 'mask', 'mask-image',
                          '-webkit-mask', '-webkit-mask-image'})
CSS_SIZES = frozenset({'width', 'height', 'max-width', 'max-height',
                       'min-width', 'min-height', 'block-size', 'inline-size',
                       'max-block-size', 'max-inline-size'})
CSS_POSITIONS = frozenset({'left', 'right', 'top', 'bottom', 'text-indent'})
CSS_TRANSFORM_ZERO = re.compile(r'(?i)\b(?:scale|scalex|scaley)\(\s*[+\-]?0+(?:\.0*)?(?:\s*[,)]|\s*\Z)')
CSS_HEX_TRANSPARENT = re.compile(r'(?i)#(?:[a-f0-9]{3}0|[a-f0-9]{6}00)\Z')
CSS_ALPHA_TRANSPARENT = re.compile(r'(?i)(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\([^)]*(?:,|/)\s*[+\-]?0+(?:\.0*)?%?\s*\)\Z')


class CitationPlacementHold(ValueError):
    """Unverifiable or non-editorial citation placement; no approval implied."""


def _css_unescape(value: str) -> str:
    """Decode CSS escapes before matching concealment declarations.

    Fail-closed on malformed escapes rather than treating an obfuscated CSS
    keyword as harmless. This is intentionally not a complete CSS parser.
    """
    def decode(m: re.Match) -> str:
        if m.group(1) is not None:
            cp = int(m.group(1), 16)
            if not cp or cp > 0x10FFFF or 0xD800 <= cp <= 0xDFFF:
                raise CitationPlacementHold('invalid CSS escape code point')
            return chr(cp)
        return m.group(2)
    result = CSS_ESCAPE.sub(decode, value)
    if '\\' in result:
        raise CitationPlacementHold('ambiguous CSS escape on citation ancestor')
    return result


def _css_zero_number(value: str) -> bool:
    m = CSS_NUMBER.fullmatch(value)
    if not m:
        return False
    try:
        return Decimal(m.group(1)) == 0
    except InvalidOperation:
        return False


def _transparent_color(value: str) -> bool:
    """Detect common fully transparent text fills, not all CSS color syntax."""
    return (value == 'transparent' or
            bool(CSS_HEX_TRANSPARENT.fullmatch(value)) or
            bool(CSS_ALPHA_TRANSPARENT.fullmatch(value)))


def _concealing_style(style: str) -> bool:
    """Conservative *inline-only* paint/geometry checks for citation ancestors.

    A CSS browser/computed-style engine is not being simulated. Unresolved CSS
    functions or clipping properties that might conceal a citation are a HOLD,
    not evidence that they are genuinely invisible in a particular viewport.
    """
    style = CSS_COMMENT.sub('', style)
    for declaration in style.split(';'):
        if ':' not in declaration:
            continue
        property_name, val = (part.strip() for part in declaration.split(':', 1))
        prop = _css_unescape(property_name).lower()
        val = _css_unescape(val).lower()
        val = re.sub(r'\s*!important\s*$', '', val).strip()
        if prop not in CSS_SENSITIVE:
            continue
        if CSS_UNRESOLVED.search(val):
            return True
        if (prop == 'display' and val == 'none') or (prop == 'visibility' and val in ('hidden', 'collapse')) or (prop == 'content-visibility' and val == 'hidden'):
            return True
        if prop == 'opacity' and _css_zero_number(val):
            return True
        if prop in {'color', '-webkit-text-fill-color'} and _transparent_color(val):
            return True
        if prop in {'font-size', 'line-height', 'zoom'} and ZERO_LENGTH.fullmatch(val):
            return True
        if prop in CSS_CLIPPERS and val not in ('none', 'auto', 'initial', 'unset'):
            return True
        # Filters can destroy text contrast or opacity; only 'none' is a safe
        # static declaration. Specific computed effects need rendered review.
        if prop in {'filter', '-webkit-filter'} and val not in ('none', 'initial', 'unset'):
            return True
        if (prop == 'scale' and ZERO_LENGTH.fullmatch(val)) or (prop in {'transform', 'scale'} and CSS_TRANSFORM_ZERO.search(val)):
            return True
        if prop in CSS_SIZES and ZERO_LENGTH.fullmatch(val):
            return True
        if prop in {'overflow', 'overflow-x', 'overflow-y'} and val in ('hidden', 'clip'):
            return True
        if prop in CSS_POSITIONS and NEGATIVE_LENGTH.fullmatch(val):
            # This is deliberately conservative; even a small negative offset
            # might be harmless, but static checks cannot prove visibility.
            return True
    return False


def _hidden_attributes(attrs: list[tuple[str, str | None]], tag: str = '') -> bool:
    """Flag common states concealing citations in a static HTML draft.

    Class-based, external, responsive and script-modified CSS are not proved
    visible by these checks and always require independent rendered review.
    """
    keys = {key.lower() for key, _ in attrs}
    if 'hidden' in keys or 'inert' in keys or 'popover' in keys:
        return True
    if tag in ('details', 'dialog') and 'open' not in keys:
        return True
    for key, value in attrs:
        key = key.lower()
        if key == 'aria-hidden' and (value or '').strip().lower() == 'true':
            return True
        if key == 'style' and value and _concealing_style(value):
            return True
    return False


class _TextPositions(HTMLParser):
    def __init__(self, body: str):
        super().__init__(convert_charrefs=False)
        self.body = body
        self.line_starts = [0] + [m.end() for m in re.finditer(r'\n', body)]
        self.positions: list[int] = []
        self.stack: list[tuple[str, bool]] = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, tag in INERT or _hidden_attributes(attrs, tag)))

    def handle_startendtag(self, tag, attrs):
        # Critical R29 browser/parser differential: in HTML, <div hidden/>
        # is NOT a self-closing div; browsers ignore the slash and its content
        # remains hidden. HTMLParser calls this callback, not handle_starttag.
        # Reject the malformed HTML rather than accidentally approving a cite.
        if tag not in VOID:
            raise CitationPlacementHold('HTML non-void self-closing tag: browser visibility differs')

    def handle_endtag(self, tag):
        tags = [item[0] for item in self.stack]
        if tag in tags:
            del self.stack[len(tags)-1-tags[::-1].index(tag):]

    def handle_data(self, data):
        if any(hidden for _, hidden in self.stack):
            return
        line, col = self.getpos()
        if not (1 <= line <= len(self.line_starts)):
            raise CitationPlacementHold('parser location outside frozen HTML')
        start = self.line_starts[line-1] + col
        if self.body[start:start+len(data)] != data:
            raise CitationPlacementHold('HTML parser/raw-source position mismatch')
        for match in TOKEN.finditer(data):
            self.positions.append(start + match.start())


def verified_citations(body: str) -> list[re.Match]:
    """Return unchanged source matches, only when all are in editorial text.

    Offsets remain Unicode codepoints in original HTML. A success means only
    that no *recognized* hidden markup contains a source token. All human
    source, claim, safety, CSS/browser and independent-QD gates remain HOLD.
    """
    if type(body) is not str:
        raise CitationPlacementHold('article HTML must be an original string')
    matches = list(TOKEN.finditer(body))
    starts = [m.start() for m in matches]
    candidates = [m.start() for m in CANDIDATE.finditer(body)]
    if candidates != starts:
        raise CitationPlacementHold('unrecognized or malformed citation token start')
    # A browser decodes character references. If a citation appears only after
    # entity decoding, the template renderer may not recognize it while a
    # reader sees a fake source token. Reject that discrepancy outright.
    rendered = html_unescape(body)
    if ([m.group(0) for m in TOKEN.finditer(rendered)] !=
            [m.group(0) for m in matches] or
            len(list(CANDIDATE.finditer(rendered))) != len(matches)):
        raise CitationPlacementHold('HTML entity-encoded or altered citation token')
    parser = _TextPositions(body)
    try:
        parser.feed(body)
        parser.close()
    except (ValueError, AssertionError) as exc:
        raise CitationPlacementHold('malformed or unparseable HTML') from exc
    if sorted(parser.positions) != starts:
        raise CitationPlacementHold('citation token in HTML tag, attribute, comment or inert/hidden region')
    return matches

#!/usr/bin/env python3
"""R230: conservative HTML tokenizer-mode safety guard for draft exports.

Python HTMLParser is not a browser tree builder. This separate preflight refuses
legacy/tokenizer-changing elements that could make source/review markup text or
otherwise shift parsing context. Passing never grants source, QD or release approval.
"""
from __future__ import annotations

from html.parser import HTMLParser

HOLD = 'DRAFT_HARD_HOLD'
# <plaintext> switches to PLAINTEXT until EOF. xmp/noembed/noframes use
# RAWTEXT, whereas the Python parser can tokenize their apparent descendants
# as ordinary HTML. Frameset/legacy constructs can replace the reading body.
# Rather than attempting fragile emulation, these are not supported in drafts.
UNSUPPORTED = frozenset({
    'plaintext', 'xmp', 'noembed', 'noframes', 'frameset', 'frame',
    'listing', 'isindex', 'applet',
})


class _TokenizerPolicy(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.forbidden: list[str] = []
        self.tags_seen = 0

    def handle_starttag(self, tag, attrs):
        self.tags_seen += 1
        if tag.lower() in UNSUPPORTED:
            self.forbidden.append(tag.lower())

    def handle_startendtag(self, tag, attrs):
        # HTMLParser reports <plaintext/> as self-closing although HTML does
        # not. This policy rejects such syntax without treating it as closed.
        self.handle_starttag(tag, attrs)


def verify_tokenizer_states(page: str) -> dict:
    """Reject unsupported tokenizer-changing markup; always return HOLD only."""
    if type(page) is not str or not page.strip():
        raise ValueError('R230 invalid HTML draft')
    gate = _TokenizerPolicy()
    gate.feed(page)
    gate.close()
    if gate.forbidden:
        raise ValueError('R230 unsupported tokenizer/legacy HTML: ' +
                         ', '.join(sorted(set(gate.forbidden))))
    return {'state': HOLD, 'tokenizer_policy': 'conservative-unsupported-elements',
            'unsupported_count': 0, 'release_authorized': False}

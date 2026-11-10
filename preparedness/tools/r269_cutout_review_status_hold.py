#!/usr/bin/env python3
"""R269: authenticate the strictly unpublished cutout-status *review* alternative.

Does not repair Tool #104, approve any card for use, certify privacy or medical
safety, or change the 35-article / citation corpus. Offline, pure Python, no I/O
except the caller-provided safe_read in audit(). Original R267 stays immutable.
"""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser

HOLD = 'DRAFT_HARD_HOLD'
OLD_PATH = 'audits/r267_responsive_wallet_card_REVIEW_ONLY.html'
NEW_PATH = 'audits/r269_cutout_status_card_REVIEW_ONLY.html'
OLD_BLOB = '5ae643302faf6bce47e8c507fbcfff9c099eaf00'
NEW_BLOB = '4fbe028e0460dc81478825f501d76b03596faeaf'
LABEL = 'UNAPPROVED - DO NOT USE'
CSS_ANCHOR = b'.pa-privacy { font-weight:bold; font-size:8pt; margin:.06in 0; line-height:1.2; }\n'
CSS_ADD = (b'.pa-prototype-status { font-size:8pt; line-height:1.1; font-weight:700; '
           b'margin:0 0 .03in; border:1px solid #111; padding:1px 2px; }\n')
FACE_NAMES = ('Front', 'Back')
FALSE_STATES = ('source_approved', 'privacy_approved', 'accessibility_approved',
                'physical_print_approved', 'child_information_approved',
                'independent_qd_pass', 'ready_for_wordpress',
                'publication_authorized', 'public_published',
                'commerce_approved', 'full_native_pipeline_executed')


def git_blob(b: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(b)).encode('ascii') + b'\0' + b).hexdigest()


def need(ok, why):
    if not ok:
        raise ValueError('R269 HARD HOLD: ' + why)


def proposed(old: bytes) -> bytes:
    need(type(old) is bytes and git_blob(old) == OLD_BLOB, 'source R267 Git blob drift')
    need(old.count(CSS_ANCHOR) == 1, 'missing/duplicate CSS anchor')
    new = old.replace(CSS_ANCHOR, CSS_ANCHOR + CSS_ADD, 1)
    for face in FACE_NAMES:
        anchor = f'<section class="pa-face" aria-label="{face}">\n'.encode()
        need(new.count(anchor) == 1, 'missing/duplicate face: ' + face)
        new = new.replace(anchor, anchor +
            f'<p class="pa-prototype-status">{LABEL}</p>\n'.encode(), 1)
    return new


class FaceObserver(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.badges = []
        self.face_names = []
        self._badge = None
        self._badge_depth = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script','iframe','form','input','button'):
            raise ValueError('R269 prohibited executable/form HTML')
        if any(k.startswith('on') or k in ('src','srcdoc') for k in attrs):
            raise ValueError('R269 unexpected executable/remote attribute')
        self.stack.append((tag, attrs))
        if tag == 'section' and attrs.get('class') == 'pa-face':
            self.face_names.append(attrs.get('aria-label'))
        if tag == 'p' and attrs.get('class') == 'pa-prototype-status':
            need(self._badge is None, 'nested badge')
            need(len(self.stack) >= 2 and self.stack[-2][0] == 'section'
                 and self.stack[-2][1].get('class') == 'pa-face',
                 'badge not a direct child of a card face')
            need(not attrs.get('hidden') and attrs.get('aria-hidden') != 'true',
                 'review badge concealed')
            self._badge = [self.stack[-2][1].get('aria-label'), '']
            self._badge_depth = len(self.stack)

    def handle_data(self, data):
        if self._badge is not None:
            self._badge[1] += data

    def handle_endtag(self, tag):
        need(bool(self.stack) and self.stack[-1][0] == tag,
             'unbalanced review candidate markup: ' + tag)
        if self._badge is not None and len(self.stack) == self._badge_depth:
            need(tag == 'p', 'review badge structure invalid')
            self.badges.append(tuple(self._badge))
            self._badge = None
            self._badge_depth = None
        self.stack.pop()


def inspect(original: bytes, candidate: bytes) -> dict:
    need(type(candidate) is bytes, 'candidate bytes not supplied')
    intended = proposed(original)
    need(candidate == intended, 'unexpected alternative markup or original custody drift')
    need(git_blob(candidate) == NEW_BLOB, 'candidate Git blob drift')
    parser = FaceObserver()
    parser.feed(candidate.decode('utf-8'))
    parser.close()
    need(not parser.stack and parser._badge is None, 'unbalanced markup')
    need(parser.face_names == list(FACE_NAMES), 'card faces missing/reordered')
    need(parser.badges == [(name, LABEL) for name in FACE_NAMES],
         'review-only label must be in *each* detached card face')
    need(original.count(LABEL.encode()) == 0,
         'prior negative source observation changed')
    need(candidate.count(LABEL.encode()) == 2,
         'unexpected review status multiplicity')
    need(candidate.replace(CSS_ADD, b'', 1).replace(
         f'<p class="pa-prototype-status">{LABEL}</p>\n'.encode(), b'') == original,
         'not exactly reversible to original bytes')
    return {
        'state': HOLD,
        'old_git_blob': OLD_BLOB,
        'candidate_git_blob': NEW_BLOB,
        'original_cutout_review_status_missing': True,
        'candidate_badge_in_each_face_source': True,
        'browser_cropping_legibility_not_safety_certified': True,
        'eight_point_privacy_text_unchanged': True,
        **{key: False for key in FALSE_STATES},
    }


def audit(root, safe_read):
    return inspect(safe_read(root, OLD_PATH), safe_read(root, NEW_PATH))

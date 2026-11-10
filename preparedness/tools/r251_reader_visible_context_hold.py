#!/usr/bin/env python3
"""R251: independently reject non-reader disclosure contexts in held HTML.

A preserved R249 receipt proves its original inspector ran, not that browser
visibility is certified. This narrower guard rejects future markup edits that
move mandatory notice text into popovers or other conditional HTML contexts.
Neither source parity nor this gate licenses publication, privacy, or commerce.
"""
from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser

HOLD = 'DRAFT_HARD_HOLD'
TAG_SET = frozenset({'section', 'h2', 'h3', 'p', 'a'})
ATTRS = {
    'section': {'class', 'aria-labelledby'},
    'h2': {'id'},
    'h3': set(),
    'p': {'class'},
    'a': {'href'},
}
REQUIRED_PARAGRAPHS = (
    ('proposed clarification', 'editorial review', 'real browser and print checks'),
    ('six filled-in fields:', 'household name', 'household phone number',
     'out-of-area contact', 'out-of-area phone number', 'first meeting place',
     'review date', 'lost or shared'),
    ('thirteen filled-in fields', 'excludes seven fields', 'empty field'),
    ('javascript turned off', 'interactive form is hidden when javascript is off'),
    ('written plan at home', 'private identifying information'),
    ('free household-planning resources', 'preparedness archive', 'subject to review'),
    ('review copy only', 'no paid kit', 'no paid checkout'),
)
FALSE_FLAGS = ('source_and_medical_safety_approved', 'browser_print_verified',
               'privacy_certified', 'independent_qd_pass', 'commerce_approved',
               'release_authorized')


class ReaderOnly(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.paragraphs = []
        self.current = None
        self.text_outside = []
        self.tags = []
        self.links = []
        self.p_attrs = []
        self.comments = []

    def handle_starttag(self, tag, attrs):
        if tag not in TAG_SET:
            raise ValueError('R251 HARD HOLD: conditional, foreign or executable element')
        keys = [k for k, _ in attrs]
        if len(keys) != len(set(keys)) or any(k not in ATTRS[tag] for k in keys):
            raise ValueError('R251 HARD HOLD: unapproved attributes (including popover/hidden)')
        if (tag == 'section' and (self.stack or len(self.tags) != 0 or
             dict(attrs) != {'class':'pa-act pa-r249-review', 'aria-labelledby':'r249-title'})):
            raise ValueError('R251 HARD HOLD: top-level section identity')
        if tag != 'section' and not self.stack:
            raise ValueError('R251 HARD HOLD: extra top-level elements')
        if tag in ('h2', 'h3', 'p') and self.stack != ['section']:
            raise ValueError('R251 HARD HOLD: disclosure no longer direct reader content')
        if tag == 'a' and self.stack != ['section', 'p']:
            raise ValueError('R251 HARD HOLD: unexpected anchor nesting')
        if tag == 'h2' and dict(attrs) != {'id':'r249-title'}:
            raise ValueError('R251 HARD HOLD: visible heading identity')
        if tag == 'h3' and attrs:
            raise ValueError('R251 HARD HOLD: hidden heading properties')
        if tag == 'p' and attrs not in ([], [('class','pa-review-hold')]):
            raise ValueError('R251 HARD HOLD: altered visible paragraph state')
        if tag == 'p':
            self.p_attrs.append(list(attrs))
        if tag == 'a':
            if attrs != [('href', '/preparedness/')]:
                raise ValueError('R251 HARD HOLD: changed or commercial destination')
            self.links.append('/preparedness/')
        if tag == 'p':
            self.current = []
        self.tags.append(tag)
        self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        raise ValueError('R251 HARD HOLD: self-closing reader markup')

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            raise ValueError('R251 HARD HOLD: unbalanced reader markup')
        if tag == 'p':
            self.paragraphs.append(re.sub(r'\s+', ' ', ''.join(self.current)).strip())
            self.current = None
        self.stack.pop()

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)
        elif data.strip():
            # Headings are intentionally isolated from critical disclosures.
            if self.stack not in (['section', 'h2'], ['section', 'h3']):
                self.text_outside.append(data)

    def handle_comment(self, data):
        self.comments.append(data.strip())

    def handle_decl(self, decl):
        raise ValueError('R251 HARD HOLD: HTML declaration')

    def handle_pi(self, data):
        raise ValueError('R251 HARD HOLD: processing instruction')


def inspect(markup: str, prior: dict) -> dict:
    if type(markup) is not str or type(prior) is not dict:
        raise ValueError('R251 HARD HOLD: invalid gate types')
    if not 400 < len(markup) < 20000 or '\x00' in markup:
        raise ValueError('R251 HARD HOLD: invalid preview bytes')
    if prior.get('state') != HOLD or prior.get('issue') != 136 or prior.get('conversion_issue') != 820:
        raise ValueError('R251 HARD HOLD: source review receipt scope')
    if prior.get('preview_sha256') != hashlib.sha256(markup.encode('utf-8')).hexdigest():
        raise ValueError('R251 HARD HOLD: prior preview digest mismatch')
    if prior.get('visible_free_destinations') != ['/preparedness/'] or prior.get('human_review_required') is not True:
        raise ValueError('R251 HARD HOLD: prior public route or review requirement')
    if any(prior.get(k) is not False for k in FALSE_FLAGS):
        raise ValueError('R251 HARD HOLD: prior source/release approval drift')
    p = ReaderOnly()
    try:
        p.feed(markup)
        p.close()
    except (AssertionError, UnicodeError) as exc:
        raise ValueError('R251 HARD HOLD: malformed HTML') from exc
    if p.stack or p.text_outside:
        raise ValueError('R251 HARD HOLD: escaped or dangling disclosure text')
    if p.tags != ['section', 'h2', 'p', 'h3', 'p', 'p', 'p', 'p', 'p', 'a', 'p']:
        raise ValueError('R251 HARD HOLD: altered visible reading order')
    if p.p_attrs != [[]]*6 + [[('class', 'pa-review-hold')]]:
        raise ValueError('R251 HARD HOLD: review-only notice badge removed')
    if p.links != ['/preparedness/']:
        raise ValueError('R251 HARD HOLD: missing unique free destination')
    if len(p.comments) != 1 or not p.comments[0].startswith('UNPUBLISHED EDITORIAL OPTION B.'):
        raise ValueError('R251 HARD HOLD: unsigned preview identity missing')
    if len(p.paragraphs) != len(REQUIRED_PARAGRAPHS):
        raise ValueError('R251 HARD HOLD: paragraph count')
    for index, (paragraph, phrases) in enumerate(zip(p.paragraphs, REQUIRED_PARAGRAPHS)):
        normalized = paragraph.lower()
        if any(phrase not in normalized for phrase in phrases):
            raise ValueError('R251 HARD HOLD: displaced or hidden notice in paragraph %d' % (index+1))
    bound = json.dumps({'preview_sha256':prior['preview_sha256'],
                        'paragraphs':p.paragraphs, 'links':p.links,
                        'review_state': HOLD}, sort_keys=True,
                       separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return {'state':HOLD, 'issue':136, 'conversion_issue':820,
            'scope':'UNAPPROVED_OFFLINE_READER_COPY_ONLY',
            'visible_paragraph_count':len(p.paragraphs),
            'unique_free_destinations':p.links,
            'context_custody_sha256':hashlib.sha256(bound).hexdigest(),
            'source_review_approved':False, 'medical_safety_verified':False,
            'privacy_certified':False, 'independent_qd_pass':False,
            'merchant_approved':False, 'release_authorized':False,
            'human_review_required':True}

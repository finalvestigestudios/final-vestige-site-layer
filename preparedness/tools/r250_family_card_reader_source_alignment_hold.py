#!/usr/bin/env python3
"""R250 independent, fail-closed Article 15/Tool 104 source-to-reader parity.

Receipts must be authenticated by R220's pinned R248/R249 guards FIRST.
Parity of an unapproved preview with source behavior is NOT publication,
privacy, medical, editorial, browser/print, or paid-offer clearance.
"""
from __future__ import annotations
import hashlib
import json
import re
from html.parser import HTMLParser

HOLD = 'DRAFT_HARD_HOLD'
SIX = (
    ('hhName', 'household name'),
    ('hhPhone', 'household phone number'),
    ('outName', 'out-of-area contact'),
    ('outPhone', 'out-of-area phone number'),
    ('meet1', 'first meeting place'),
    ('reviewed', 'review date'),
)
ALL_KEYS = (
    'hhName', 'hhPhone', 'outName', 'outPhone', 'meet1', 'meet2',
    'school', 'schoolPlan', 'pickup', 'careName', 'carePhone', 'access', 'reviewed',
)
FALSE_FLAGS = (
    'reader_disclosure_approved', 'privacy_certified', 'claims_adjudicated',
    'medical_safety_verified', 'source_review_approved', 'independent_qd_pass',
    'merchant_approved', 'release_authorized',
)
PREVIEW_FALSE_FLAGS = (
    'source_and_medical_safety_approved', 'browser_print_verified',
    'privacy_certified', 'independent_qd_pass', 'commerce_approved',
    'release_authorized',
)

class ParagraphReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.level = 0
        self.parts = []
        self.paragraphs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            if self.level:
                raise ValueError('R250 nested paragraph')
            self.level = 1
            self.parts = []
        elif self.level and tag not in ('a', 'strong', 'em', 'span'):
            raise ValueError('R250 unexpected paragraph child')

    def handle_endtag(self, tag):
        if tag == 'p':
            if self.level != 1:
                raise ValueError('R250 unmatched paragraph')
            self.paragraphs.append(re.sub(r'\s+', ' ', ''.join(self.parts)).strip())
            self.level = 0

    def handle_data(self, data):
        if self.level:
            self.parts.append(data)


def _must(test: bool, why: str):
    if not test:
        raise ValueError('R250 SOURCE/READER HARD HOLD: ' + why)


def inspect(field: dict, preview: dict, html: str) -> dict:
    _must(type(field) is dict and type(preview) is dict and type(html) is str,
          'receipt types')
    _must(field.get('state') == HOLD and preview.get('state') == HOLD,
          'missing hard hold')
    _must(field.get('issue') == preview.get('issue') == 136 and
          field.get('conversion_issue') == preview.get('conversion_issue') == 820,
          'cross-issue custody')
    for flag in FALSE_FLAGS:
        _must(field.get(flag) is False, 'unapproved original-source flag: '+flag)
    for flag in PREVIEW_FALSE_FLAGS:
        _must(preview.get(flag) is False, 'unapproved preview flag: '+flag)
    _must(field.get('human_review_required') is True and
          preview.get('human_review_required') is True, 'human review missing')
    _must(field.get('source_count') == 5 and
          (field.get('full_field_count'), field.get('minimal_field_count'),
           field.get('minimal_excluded_field_count')) == (13, 6, 7),
          'source-model counts')
    _must((preview.get('printed_full_fields'), preview.get('printed_shorter_fields'),
           preview.get('excluded_shorter_fields')) == (13, 6, 7),
          'preview counts')
    _must(preview.get('visible_free_destinations') == ['/preparedness/'],
          'free-only destination')
    _must(preview.get('preview_sha256') == hashlib.sha256(html.encode()).hexdigest(),
          'preview digest mismatch')
    matrix = field.get('field_matrix')
    _must(type(matrix) is list and len(matrix) == 13, 'source field roster count')
    _must([x.get('field') for x in matrix if type(x) is dict] == list(ALL_KEYS),
          'source field order/identity changed')
    _must(all(type(x) is dict and x.get('in_full') is True and
              type(x.get('in_minimal')) is bool and
              x.get('reader_authorization') == 'UNREVIEWED' for x in matrix),
          'source field review/status changed')
    _must([x['field'] for x in matrix if x['in_minimal']] == [x[0] for x in SIX],
          'minimal-mode print roster drift')
    for witness in ('unconditional_minimal_household_name',
                    'unconditional_minimal_household_phone',
                    'unconditional_home_plan_statement',
                    'claimed_only_list_is_incomplete',
                    'nojs_form_claim_is_contradicted',
                    'privacy_claim_scope_requires_browser_review'):
        _must(field.get(witness) is True, 'original claim witness missing: '+witness)
    reader = ParagraphReader()
    reader.feed(html)
    reader.close()
    _must(reader.level == 0, 'unclosed reader paragraph')
    intro = [p for p in reader.paragraphs if 'six filled-in fields:' in p.lower()]
    _must(len(intro) == 1, 'six-field disclosure missing or duplicated')
    clause = intro[0].lower().split('six filled-in fields:', 1)[1].split('.', 1)[0]
    actual = [re.sub(r'\s+', ' ', w).strip(' .,') for w in
              re.split(r',\s*|\s+and\s+', re.sub(r',\s+and\s+', ', ', clause)) if w.strip()]
    _must(actual == [label for _,label in SIX], 'visible six-field list is not exact')
    _must(any('printed card is lost or shared' in p.lower() for p in reader.paragraphs),
          'paper-loss disclosure missing')
    _must(any('interactive form is hidden when javascript is off' in p.lower()
              for p in reader.paragraphs), 'no-JS disclosure missing')
    _must(any('written plan at home' in p.lower() for p in reader.paragraphs),
          'unconditional written-plan claim not warned')
    _must(any('no paid kit' in p.lower() and 'no paid checkout' in p.lower()
              for p in reader.paragraphs), 'commercial hold omitted')
    custody = json.dumps({'field_keys': [x['field'] for x in matrix],
                          'min_keys': [x['field'] for x in matrix if x['in_minimal']],
                          'preview_sha256': preview['preview_sha256']},
                         sort_keys=True, separators=(',', ':')).encode()
    return {'state': HOLD, 'issue': 136, 'conversion_issue': 820,
            'source_to_reader_six_field_parity': 'OBSERVED_NOT_APPROVED',
            'source_count': 5, 'printed_full_fields': 13,
            'printed_shorter_fields': 6, 'excluded_shorter_fields': 7,
            'custody_sha256': hashlib.sha256(custody).hexdigest(),
            'independent_qd_pass': False, 'source_review_approved': False,
            'privacy_certified': False, 'medical_safety_verified': False,
            'merchant_approved': False, 'release_authorized': False,
            'human_review_required': True}

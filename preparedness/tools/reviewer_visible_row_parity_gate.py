#!/usr/bin/env python3
"""R47: independent visible-cell parity against the frozen R42 review dossier.

R44 verifies private ZIP bytes and R45/R46 verify HTML topology. This gate
checks that every reviewer-visible <pre> field and its article/title/index
identity is exactly the original R42 claim/source/fallback/shared-URL evidence.
It does not visit links, attest source accuracy, identify reviewers, approve
emergency guidance, produce a public page or write files.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from io import BytesIO
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

R45 = Path(__file__).with_name('reviewer_html_semantic_gate.py')
if not R45.is_file() or R45.is_symlink():
    raise ValueError('R45 exact nonsymlinked HTML safety gate required')
_spec = importlib.util.spec_from_file_location('preparedness_r47_frozen_r45', R45)
if _spec is None or _spec.loader is None:
    raise ValueError('cannot load exact R45/R46 gate')
r45 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r45)

EXPECTED = (35, 1, 1959, 367, 43, 30)
AUTHORITY = 'PRIVATE_VISIBLE_EVIDENCE_CELL_PARITY_NOT_HUMAN_OR_SAFETY_APPROVAL'
KINDS = ('claims', 'scopes', 'fallbacks', 'groups')
IDS = ('claim_case_sha256', 'source_case_sha256', 'fallback_case_sha256',
       'global_group_case_sha256')
IDENTITY_FIELDS = ('slug', 'fingerprint_sha256', 'counts',
                   'taxonomy_status_recorded_not_a_human_verdict',
                   'taxonomy_safety_gate_recorded_not_approval',
                   'required_independent_checks')
WARNING = ('PRIVATE / UNVERIFIED / HOLD. No source, emergency guidance, '
           'medical recommendation or historical method is approved by this '
           'machine-produced page. URLs are inert text.')
DISCLAIMER = ('Original taxonomy status is historical metadata, NOT human '
              'safety or publication approval.')

class VisibleEvidenceHold(ValueError):
    """Reviewer-visible evidence differs from the frozen original."""

def need(ok, reason):
    if not ok:
        raise VisibleEvidenceHold(reason)

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def as_text(value):
    return value if type(value) is str else canonical(value).decode('utf-8')

def pairs(item):
    need(type(item) is dict and all(type(key) is str for key in item),
         'malformed original evidence row')
    return [(key, as_text(item[key])) for key in sorted(item)]

class VisiblePage(HTMLParser):
    """Read literal browser-visible text from the already R46-vetted DOM grammar."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections = []
        self.meta_pairs = []
        self.current_pairs = None
        self.active_article = False
        self.current_key = None
        self.current_value = None
        self.captures = {}
        self.title = []
        self.h1 = []
        self.paragraphs = []
        self.li_text = []
        self.links = []
        self.link_labels = []

    def handle_starttag(self, tag, attrs):
        if tag == 'section':
            self.sections.append({'heading': None, 'rows': []})
        if tag == 'article':
            need(not self.active_article and bool(self.sections),
                 'nested or unscoped evidence record')
            self.active_article = True
        if tag == 'dl':
            need(self.current_pairs is None, 'nested evidence dictionary')
            self.current_pairs = []
        if tag in ('title', 'h1', 'h2', 'dt', 'pre', 'p', 'li', 'a'):
            need(tag not in self.captures, 'nested text capture')
            self.captures[tag] = []
        if tag == 'a':
            self.links.append(dict(attrs).get('href'))

    def handle_data(self, data):
        for chunks in self.captures.values():
            chunks.append(data)

    def handle_endtag(self, tag):
        if tag in self.captures:
            value = ''.join(self.captures.pop(tag))
            if tag == 'title':
                self.title.append(value)
            elif tag == 'h1':
                self.h1.append(value)
            elif tag == 'h2':
                need(bool(self.sections) and
                     self.sections[-1]['heading'] is None,
                     'repeated or unscoped evidence section heading')
                self.sections[-1]['heading'] = value
            elif tag == 'dt':
                need(self.current_pairs is not None and
                     self.current_key is None,
                     'unscoped source field name')
                self.current_key = value
            elif tag == 'pre':
                need(self.current_pairs is not None and
                     self.current_value is None,
                     'unscoped source field value')
                self.current_value = value
            elif tag == 'p':
                self.paragraphs.append(value)
            elif tag == 'li':
                self.li_text.append(value)
            elif tag == 'a':
                self.link_labels.append(value)
        if tag == 'dd':
            if self.current_pairs is not None:
                need(self.current_key is not None and
                     self.current_value is not None,
                     'field without original literal value')
                self.current_pairs.append((self.current_key,
                                           self.current_value))
                self.current_key = self.current_value = None
        if tag == 'dl':
            need(self.current_pairs is not None and
                 self.current_key is None and self.current_value is None,
                 'partial or malformed source row')
            if not self.active_article:
                need(not self.meta_pairs, 'duplicate article identity table')
                self.meta_pairs = self.current_pairs
            else:
                need(bool(self.sections), 'orphaned source row')
                self.sections[-1]['rows'].append(self.current_pairs)
            self.current_pairs = None
        if tag == 'article':
            need(self.active_article and self.current_pairs is None,
                 'incomplete source article')
            self.active_article = False

def parse_page(html):
    need(type(html) is str, 'non-UTF8 reviewer page')
    page = VisiblePage()
    try:
        page.feed(html)
        page.close()
    except (ValueError, AssertionError, TypeError, UnicodeError) as exc:
        raise VisibleEvidenceHold('cannot parse visible source-review fields') from exc
    need(not page.captures and page.current_pairs is None and
         not page.active_article and len(page.title) == len(page.h1) == 1,
         'incomplete or ambiguous visible review page')
    return page

def check_dossier(dossier, page):
    slug = dossier['slug']
    need(page.title == [dossier['title'] + ' — PRIVATE HOLD'] and
         page.h1 == [dossier['title']] and WARNING in page.paragraphs and
         DISCLAIMER in page.paragraphs,
         'wrong article title, missing warning or misleading taxonomy disclaimer: '+slug)
    need(len(page.sections) == 5 and
         page.sections[0]['heading'] == 'Evidence identity and review requirements' and
         not page.sections[0]['rows'],
         'missing article evidence identity section: '+slug)
    identity = [(name, as_text(dossier[name])) for name in IDENTITY_FIELDS]
    need(page.meta_pairs == identity,
         'article fingerprint, safety taxonomy or review scope not visibly identical: '+slug)
    total_fields = len(identity)
    for offset, kind in enumerate(KINDS, 1):
        originals = dossier['original_review_records'][kind]
        actual = page.sections[offset]
        need(actual['heading'] == kind + ': ' + str(len(originals)) and
             actual['rows'] == [pairs(row) for row in originals],
             'dropped, duplicated, moved, reordered or altered visible '+kind+' evidence: '+slug)
        total_fields += sum(len(row) for row in originals)
    return total_fields

def check_index(dossiers, page, expected):
    ordered = sorted(dossiers, key=lambda d: d['slug'])
    need(page.title == ['Preparedness PRIVATE review desk — PRIVATE HOLD'] and
         page.h1 == ['Preparedness PRIVATE review desk'] and
         WARNING in page.paragraphs and len(page.sections) == 1 and
         page.sections[0]['heading'] == 'All original article/tool reviews' and
         not page.sections[0]['rows'] and not page.meta_pairs,
         'private index page lost its original visible status/structure')
    summary = ('Unreviewed citations: '+str(expected[2])+
               ', separate source reading relationships: '+str(expected[3])+
               ', fallbacks: '+str(expected[4])+
               ', repeated-source groups: '+str(expected[5]))
    need(summary in page.paragraphs and
         page.li_text == [d['title']+' — '+str(d['counts']['claims'])+
                          ' individual citation checks' for d in ordered] and
         page.link_labels == ['Review every shared URL group']+
                             [d['title'] for d in ordered],
         'article identities, counts or shared-source index labels misrepresent source evidence')

def check_global(groups, page):
    need(page.title == ['All shared URL variants — PRIVATE HOLD'] and
         page.h1 == ['All shared URL variants'] and
         WARNING in page.paragraphs and len(page.sections) == 1 and
         page.sections[0]['heading'] ==
           'Global cited and uncited source variants: '+str(len(groups)) and
         page.sections[0]['rows'] == [pairs(groups[key]) for key in sorted(groups)] and
         not page.meta_pairs,
         'globally cited/uncited repeated URL evidence not visibly identical')
    return sum(len(row) for row in groups.values())

def audit_visible_evidence_rows(packet, archive, *, trusted_r42_sha256,
                                trusted_r43_sha256, expected=EXPECTED):
    """Independent private review-cell parity. Neither machine nor human approval."""
    need(type(expected) is tuple and len(expected) == 6 and
         all(type(n) is int and n >= 0 for n in expected),
         'invalid six-part article/source frozen census')
    need(type(packet) is dict and
         packet.get('fingerprint_sha256') == trusted_r42_sha256 and
         r45.sha(r45.canonical({k:v for k,v in packet.items()
                                if k != 'fingerprint_sha256'})) == trusted_r42_sha256 and
         packet.get('release_state') == 'HOLD' and
         all(packet.get(flag) is False for flag in r45.FLAGS),
         'R42 originals must be independently pinned and remain unapproved')
    verified = r45.audit_private_zip_html(archive,
             trusted_r42_sha256=trusted_r42_sha256,
             trusted_r43_sha256=trusted_r43_sha256, expected=expected)
    dossiers = packet.get('article_dossiers')
    need(type(dossiers) is list and len(dossiers) == expected[0]+expected[1] and
         packet.get('counts') == dict(zip(r45.r44.COUNT_KEYS, expected)),
         'R42 source dossier census lost')
    slugs = set()
    globals_by_case = {}
    totals = Counter()
    fields = 0
    with ZipFile(BytesIO(archive), 'r') as z:
        for dossier in dossiers:
            need(type(dossier) is dict and type(dossier.get('slug')) is str and
                 dossier['slug'] not in slugs, 'duplicate or unbound dossier')
            slug = dossier['slug']
            slugs.add(slug)
            for kind in KINDS:
                records = dossier['original_review_records'][kind]
                need(type(records) is list and
                     len(records) == dossier['counts'][kind],
                     'source evidence group cardinality drift')
                if kind != 'groups':
                    totals[kind] += len(records)
                for row in records if kind == 'groups' else ():
                    key = row['global_group_case_sha256']
                    need(key not in globals_by_case or globals_by_case[key] == row,
                         'original duplicate URL groups conflated across articles')
                    globals_by_case[key] = row
            name = 'articles/'+slug+'.html'
            need(name in z.namelist(), 'article evidence page missing: '+slug)
            fields += check_dossier(dossier, parse_page(z.read(name).decode('utf-8')))
        uncited = packet.get('uncited_shared_url_groups_unreviewed')
        need(type(uncited) is list, 'uncited shared URLs lost')
        for row in uncited:
            key = row['global_group_case_sha256']
            need(key not in globals_by_case, 'uncited duplicate URL wrongly merged')
            globals_by_case[key] = row
        need((len(dossiers)-expected[1],expected[1],totals['claims'],
              totals['scopes'],totals['fallbacks'],len(globals_by_case)) == expected,
             'full 35+1 source/claim/duplicate-URL census mismatch')
        check_index(dossiers, parse_page(z.read('index.html').decode('utf-8')), expected)
        fields += check_global(globals_by_case,
                               parse_page(z.read('global-source-variants.html').decode('utf-8')))
    report = {
        'schema_version':1, 'issue':136, 'release_state':'HOLD',
        'machine_authority':AUTHORITY,
        'parent_R42_fingerprint_sha256':trusted_r42_sha256,
        'parent_R43_fingerprint_sha256':trusted_r43_sha256,
        'parent_R45_fingerprint_sha256':verified['fingerprint_sha256'],
        'counts':packet['counts'],
        'private_pages_checked':len(dossiers)+2,
        'visible_source_and_identity_fields_checked':fields,
        'individual_claim_reviews_still_unstarted':expected[2],
        'external_links_visited':False, 'source_accuracy_established':False,
        'actual_human_review_started':False,
        **{flag:False for flag in r45.FLAGS},
    }
    report['fingerprint_sha256'] = hashlib.sha256(canonical(report)).hexdigest()
    return report

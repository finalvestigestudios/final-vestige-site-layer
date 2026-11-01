#!/usr/bin/env python3
"""R43 offline, PRIVATE-HOLD HTML view for complete R42 review evidence.

Pure transformations: no network, CMS, publication, human approval, URL rewriting
or source truncation. URLs remain inert text. Caller pins R42 SHA separately.
"""
from collections import Counter
import hashlib
from html import escape
import json
import re

EXPECTED = (35, 1, 1959, 367, 43, 30)
FLAGS = ('may_publish', 'qualified_safety_clearance', 'independent_QD_approval',
         'human_source_reviews_completed', 'source_claim_accuracy_verified',
         'reviewer_real_identity_verified')
KEYS = {'claims': 'claim_case_sha256', 'scopes': 'source_case_sha256',
        'fallbacks': 'fallback_case_sha256', 'groups': 'global_group_case_sha256'}
COUNT_KEYS = ('articles', 'tools', 'claim_reviews', 'source_scope_reviews',
              'fallback_reviews', 'global_shared_url_reviews')
HEX = re.compile(r'[0-9a-f]{64}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')

class OfflineHold(ValueError):
    """Untrusted, missing or mistakenly approved source-review evidence."""

def need(ok, reason):
    if not ok:
        raise OfflineHold(reason)

def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False,
        separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()

def frozen(item):
    need(type(item) is dict and item.get('schema_version') == 1 and
         item.get('issue') == 136 and item.get('release_state') == 'HOLD'
         and all(item.get(key) is False for key in FLAGS)
         and type(item.get('fingerprint_sha256')) is str
         and HEX.fullmatch(item['fingerprint_sha256'])
         and item['fingerprint_sha256'] ==
         digest({k: v for k, v in item.items() if k != 'fingerprint_sha256'}),
         'altered or approved R42 evidence')

def literal(value):
    text = value if type(value) is str else json.dumps(value, sort_keys=True,
         ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    need('\x00' not in text, 'unprintable NUL in original source evidence')
    return escape(text, quote=True)

def page(title, body, back=None):
    link = f'<p><a href="{back}">Private index</a></p>' if back else ''
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta http-equiv="Content-Security-Policy" content="default-src '
            "'none'; style-src 'unsafe-inline'; connect-src 'none'; img-src 'none'; "
            "font-src 'none'; form-action 'none'; base-uri 'none'\">"
            f'<title>{literal(title)} — PRIVATE HOLD</title>'
            '<style>body{font:16px/1.6 system-ui,sans-serif;max-width:1000px;'
            'margin:2rem auto;padding:1rem;background:#f5f5f1;color:#202833}'
            'section,article{background:white;border:1px solid #ddd;padding:1rem;'
            'margin:1rem 0}pre{white-space:pre-wrap;overflow-wrap:anywhere}'
            'dt{font-weight:700;margin-top:.6rem}.hold{border-left:6px solid #753900;'
            'background:#ffe2ae;padding:1rem;font-weight:700}'
            'a:focus-visible{outline:3px solid orange}</style></head><body>'
            f'<h1>{literal(title)}</h1><p class="hold">PRIVATE / UNVERIFIED / HOLD. '
            'No source, emergency guidance, medical recommendation or historical '
            'method is approved by this machine-produced page. URLs are inert text.'
            f'</p>{link}<main>{body}</main></body></html>\n')

def rows_html(label, rows):
    parts = [f'<section><h2>{literal(label)}: {len(rows)}</h2>']
    for row in rows:
        parts.append('<article><dl>')
        for key in sorted(row):
            parts.append(f'<dt>{literal(key)}</dt><dd><pre>{literal(row[key])}</pre></dd>')
        parts.append('</dl></article>')
    return ''.join(parts) + '</section>'

def build_offline_html(packet, *, trusted_r42_sha256, expected=EXPECTED):
    """Prepare deterministic private HTML pages without touching the filesystem.

    Independently pin trusted_r42_sha256. Passing the packet's own digest
    only checks internal consistency, NOT original research provenance.
    """
    need(type(expected) is tuple and len(expected) == 6 and
         all(type(n) is int and n >= 0 for n in expected), 'invalid census')
    frozen(packet)
    need(type(trusted_r42_sha256) is str and HEX.fullmatch(trusted_r42_sha256)
         and packet['fingerprint_sha256'] == trusted_r42_sha256,
         'external R42 pin mismatch')
    need(packet.get('machine_authority') ==
         'PRIVATE_PER_ARTICLE_EVIDENCE_AND_SAFETY_HANDOFF_NOT_APPROVAL'
         and packet.get('all_case_rows_preserved_without_url_deduplication') is True
         and packet.get('publication_authorized') is False
         and packet.get('all_human_reviews_completed') is False
         and packet.get('qualified_hazard_safety_check_completed') is False
         and packet.get('counts') == dict(zip(COUNT_KEYS, expected)),
         'R42 census or release authority drift')
    dossiers = packet.get('article_dossiers')
    need(type(dossiers) is list and len(dossiers) == expected[0] + expected[1],
         'lost article/tool dossier')
    slugs = set()
    counts = Counter()
    cases = {k: set() for k in KEYS}
    relationships = {}
    cited = Counter()
    groups = {}
    urls = {}
    tool_count = 0
    pages = {}
    for d in dossiers:
        frozen(d)
        slug = d.get('slug')
        records = d.get('original_review_records')
        need(type(slug) is str and SLUG.fullmatch(slug)
             and slug not in slugs and type(records) is dict
             and set(records) == set(KEYS)
             and type(d.get('title')) is str and bool(d['title'].strip())
             and type(d.get('is_tool')) is bool, 'unsafe or missing article/tool')
        slugs.add(slug)
        tool_count += int(d['is_tool'])
        need(type(d.get('counts')) is dict and
             d.get('high_priority_claim_cases') ==
             sum(x.get('triage_priority_not_verdict') == 'REVIEW_FIRST'
                 for x in records['claims']), 'priority/count drift')
        parts = ['<section><p>Original taxonomy status is historical metadata, '
                 'NOT human safety or publication approval.</p>',
                 '<h2>Evidence identity and review requirements</h2><dl>']
        for k in ('slug', 'fingerprint_sha256', 'counts',
                  'taxonomy_status_recorded_not_a_human_verdict',
                  'taxonomy_safety_gate_recorded_not_approval',
                  'required_independent_checks'):
            parts.append(f'<dt>{literal(k)}</dt><dd><pre>{literal(d[k])}</pre></dd>')
        parts.append('</dl></section>')
        for kind, key in KEYS.items():
            rows = records[kind]
            need(type(rows) is list and d['counts'].get(kind) == len(rows),
                 'missing or duplicated source/citation rows')
            local = set()
            for row in rows:
                rid = row.get(key)
                need(type(rid) is str and HEX.fullmatch(rid) and rid not in local
                     and row.get('review_state') == 'NOT_STARTED'
                     and all(v == '' for k, v in row.items() if k.startswith('human_')),
                     'unverified evidence or fabricated human review')
                local.add(rid)
                if kind == 'groups':
                    need(rid not in groups or groups[rid] == row,
                         'shared URL case changed across articles')
                    groups[rid] = row
                    prior = urls.setdefault(row['source_url'], rid)
                    need(prior == rid, 'same URL mapped to different group cases')
                else:
                    need(rid not in cases[kind], 'duplicated source/citation case')
                    cases[kind].add(rid)
                    counts[kind] += 1
                if kind == 'scopes':
                    rel = row.get('relationship_sha256')
                    need(row.get('slug') == slug and rel not in relationships,
                         'source relationship moved or duplicated')
                    relationships[rel] = row
                if kind == 'claims':
                    need(row.get('slug') == slug, 'claim moved to different article')
                    cited[row.get('relationship_sha256')] += 1
            parts.append(rows_html(kind, rows))
        pages['articles/' + slug + '.html'] = page(
            d['title'], ''.join(parts), '../index.html')
    need(tool_count == expected[1] and counts['claims'] == expected[2] and
         counts['scopes'] == expected[3] and counts['fallbacks'] == expected[4] and
         set(cited) == set(relationships) and
         all(cited[k] == int(v['impacted_claims']) for k, v in relationships.items()),
         'article or claim-to-source-reading census lost')
    uncited = packet.get('uncited_shared_url_groups_unreviewed')
    need(type(uncited) is list, 'uncited shared source evidence lost')
    for row in uncited:
        ident = row.get('global_group_case_sha256')
        need(type(ident) is str and HEX.fullmatch(ident)
             and ident not in groups and row.get('source_url') not in urls
             and row.get('used_in_any_citation') == 'false'
             and row.get('review_state') == 'NOT_STARTED'
             and all(v == '' for k, v in row.items() if k.startswith('human_')),
             'uncited source variant changed or duplicated')
        groups[ident] = row
        urls[row['source_url']] = ident
    need(len(groups) == expected[5], 'original repeated URL groups omitted')
    pages['global-source-variants.html'] = page(
        'All shared URL variants',
        rows_html('Global cited and uncited source variants',
                  [groups[k] for k in sorted(groups)]), 'index.html')
    links = ['<section><h2>All original article/tool reviews</h2>',
             '<p>Unreviewed citations: ' + str(counts['claims']) +
             ', separate source reading relationships: ' + str(counts['scopes']) +
             ', fallbacks: ' + str(counts['fallbacks']) +
             ', repeated-source groups: ' + str(len(groups)) + '</p>',
             '<p><a href="global-source-variants.html">'
             'Review every shared URL group</a></p><ol>']
    for d in sorted(dossiers, key=lambda x: x['slug']):
        links.append(f'<li><a href="articles/{d["slug"]}.html">'
                     f'{literal(d["title"])}</a> — {d["counts"]["claims"]} '
                     'individual citation checks</li>')
    links.append('</ol></section>')
    pages['index.html'] = page('Preparedness PRIVATE review desk', ''.join(links))
    manifest = {'issue':136, 'release_state':'HOLD',
                'machine_authority':
                  'OFFLINE_UNVERIFIED_EVIDENCE_PRESENTATION_NOT_APPROVAL',
                'parent_R42_fingerprint_sha256':trusted_r42_sha256,
                'counts':dict(zip(COUNT_KEYS, expected)),
                'files':{p:{'sha256_utf8':hashlib.sha256(c.encode()).hexdigest(),
                            'bytes_utf8':len(c.encode())}
                         for p,c in sorted(pages.items())},
                **{key:False for key in FLAGS}}
    manifest['fingerprint_sha256'] = digest(manifest)
    return {'manifest':manifest, 'html_files':pages}

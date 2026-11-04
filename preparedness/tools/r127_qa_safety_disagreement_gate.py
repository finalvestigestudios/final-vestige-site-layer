#!/usr/bin/env python3
"""R127 read-only, fail-closed comparison of QA #157 and RC #584 safety wording.

This is an evidence-handoff gate, NEVER a medical/editorial/QD release approval.
Usage: python -I preparedness/tools/r127_qa_safety_disagreement_gate.py --candidate-root /exact/rc584 --qa-root /exact/qa157
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

RC = 'ddb3528ba6494dada1fa1c3a142ce746e3a67706'
QA = '7d1ae6b8ef93d10cfb6810987672360885e9c1aa'
FILES = {
    'plan': 'preparedness/content/articles/household-emergency-plan.body.html',
    'kit': 'preparedness/content/articles/three-day-kit.body.html',
    'source': 'preparedness/sources/fragments/start.json',
    'taxonomy': 'preparedness/taxonomy.json',
}
PINS = {
    'candidate': {'plan': 'f81cd43516e8295104230412f18776919148f905',
                  'kit': '933f38ff3cd55a241cf9b392014fc52d4961e84f',
                  'source': '96140d6d1872588e5d20d9052445c9157e88934d',
                  'taxonomy': '15c547bb3018ac182b12a51036389cfa39a59168'},
    'qa': {'plan': '6407a31a882211e62c00f4e07ec7dc4d5abf99c6',
           'kit': 'f578cdbae602c1ad58a9237c8dea0fd74c99f7da',
           'source': 'd5a5087042381227d840675d9eb08ddc375d21e8',
           'taxonomy': 'd20ff18bc6f243e08796c0505981979a10fca2d9'},
}
OPEN = ('electrical_drill_wording', 'refrigerated_medicine_product_specific',
        'source_regulatory_classification', 'four_start_here_safety_gates')


class Hold(ValueError):
    pass


def require(cond, code):
    if not cond:
        raise Hold(code)


def unique_pairs(pairs):
    d = {}
    for k, v in pairs:
        require(k not in d, 'DUPLICATE_JSON_KEY:' + k)
        d[k] = v
    return d


def gitblob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


class Paragraphs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'li'):
            self.stack.append([tag, []])

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1][0] == tag:
            _, pieces = self.stack.pop()
            self.nodes.append(' '.join(''.join(pieces).split()))

    def handle_data(self, data):
        for _, pieces in self.stack:
            pieces.append(data)


def passage(html, terms):
    parser = Paragraphs()
    parser.feed(html)
    matches = [node for node in parser.nodes if any(t in node.lower() for t in terms)]
    require(len(matches) == 1, 'AMBIGUOUS_OR_MISSING_PASSAGE:' + ','.join(terms))
    return matches[0]


def article_roster(tax):
    slate = tax.get('slate')
    require(isinstance(slate, list) and len(slate) == 35, 'MISSING_35_ARTICLE_SLATE')
    slugs = [s.get('slug') for s in slate]
    require(all(isinstance(x, str) and x for x in slugs) and len(set(slugs)) == 35,
            'DUPLICATE_OR_INVALID_ARTICLE_ROUTE')
    require(tax.get('base_path') == '/preparedness/', 'UNEXPECTED_BASE_PATH')
    for slug in ('household-emergency-plan', 'three-day-kit', 'go-bags', 'preparedness-real-households'):
        obj = next((s for s in slate if s['slug'] == slug), None)
        require(obj is not None and obj.get('gate') is True,
                'MISSING_START_HERE_SAFETY_GATE:' + slug)
    return slugs


def source_kind(source):
    records = source.get('sources')
    require(isinstance(records, list), 'MISSING_SOURCES')
    matching = [s for s in records if s.get('id') == 'start-redcross-older-adults']
    require(len(matching) == 1, 'REDCROSS_SOURCE_ID')
    require(matching[0].get('kind') == 'nonprofit', 'REDCROSS_MISCLASSIFIED')
    require(matching[0].get('human_link_check') is False, 'UNAUTHORIZED_HUMAN_LINK_CHECK')
    return matching[0]['kind']


def audit(objects, *, pins=PINS):
    """objects[version][logical filename] are RAW bytes. No write or network."""
    require(set(objects) == {'candidate', 'qa'}, 'VERSION_ROSTER')
    texts = {}
    for version in ('candidate', 'qa'):
        require(set(objects[version]) == set(FILES), 'FILE_ROSTER:' + version)
        texts[version] = {}
        for key, raw in objects[version].items():
            require(isinstance(raw, bytes), 'NON_BYTE_EVIDENCE')
            require(gitblob(raw) == pins[version][key],
                    'EVIDENCE_BLOB_MISMATCH:' + version + ':' + key)
            texts[version][key] = raw.decode('utf-8')
    details = {}
    for version in ('candidate', 'qa'):
        d = texts[version]
        tax = json.loads(d['taxonomy'], object_pairs_hook=unique_pairs)
        source = json.loads(d['source'], object_pairs_hook=unique_pairs)
        roster = article_roster(tax)
        source_kind(source)
        plan = passage(d['plan'], ('simulated-outage evening', 'lights-out evening'))
        require('do not switch off the main breaker' in plan.lower(),
                'UNPROTECTED_MAIN_BREAKER_DRILL:' + version)
        require(all(w in plan.lower() for w in ('alarms', 'medical')),
                'MISSING_SAFETY_CRITICAL_EQUIPMENT:' + version)
        kit = passage(d['kit'], ('refrigerated medicine',))
        require(any(x in kit.lower() for x in ('pharmacist', 'prescriber')),
                'NO_PRODUCT_SPECIFIC_MEDICATION_REFERRAL:' + version)
        require('{{cite:' in kit, 'MISSING_MEDICATION_SOURCE_CITATION:' + version)
        details[version] = {'article_roster': roster, 'drill': plan, 'medicine': kit}
    require(details['qa']['article_roster'] == details['candidate']['article_roster'],
            'ARTICLE_ROUTE_DRIFT')
    divergence = {k: details['qa'][k] != details['candidate'][k]
                  for k in ('drill', 'medicine')}
    require(all(divergence.values()), 'REVIEW_COMPARISON_UNEXPECTEDLY_IDENTICAL')
    return {'status': 'HOLD_HUMAN_ADJUDICATION', 'publish_permitted': False,
            'independent_QD_PASS': False, 'medical_safety_verified': False,
            'candidate_commit': RC, 'qa_commit': QA, 'article_count': 35,
            'source_classification': 'nonprofit-in-both-snapshots',
            'electrical_drill_wording_differs': divergence['drill'],
            'medication_wording_differs': divergence['medicine'],
            'review_items': [{'id': x, 'status': 'OPEN_HUMAN_REVIEW',
                              'approved': False} for x in OPEN],
            'note': 'Protective wording markers are NOT clinical, source or safety clearance.'}


def load(root):
    root = Path(root)
    return {name: (root / path).read_bytes() for name, path in FILES.items()}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate-root', type=Path, required=True)
    p.add_argument('--qa-root', type=Path, required=True)
    a = p.parse_args(argv)
    try:
        print(json.dumps(audit({'candidate': load(a.candidate_root),
                                'qa': load(a.qa_root)}), sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, UnicodeError, KeyError, TypeError) as exc:
        print('HOLD: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

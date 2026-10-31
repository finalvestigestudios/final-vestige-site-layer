#!/usr/bin/env python3
"""R16: prove why draft QA PR #157 must NOT be blindly transplanted.

The integrated articles already contain distinct, expanded electrical-drill and
refrigerated-medication cautionary text. This gate freezes that exact content,
its 35-article inventory and contributor-specific source/taxonomy evidence.
Passing means content custody only, NEVER emergency or medical safety clearance.
No CMS, publishing, network, or source-tree writes.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

BASE = '2492be67054ca1228752df64368ad75dec8dc586'
QA157 = '7d1ae6b8ef93d10cfb6810987672360885e9c1aa'
QA169 = 'e9cd7766dac59d47ab467d8945269b9146c2aef5'
ARTICLES = {
  'household-emergency-plan': '8ca5c261dba56eeaf79c445332381a74867233de',
  'three-day-kit': 'ef5463ca668166766ca3d868908bc0bcb6040a23',
}
GUARDS = {
  'preparedness/taxonomy.json': 'eea601e53e16e36cd4fc890876bc249b39632370',
  'preparedness/sources/fragments/start.json': '29574c328cbab0548e6e5d4a026694857d56b6b4',
}
KEY = {
  'household-emergency-plan': (
    'The simulated-outage evening.',
    'Do not switch off the main breaker as a drill.',
    'Leave on everything that keeps people safe',
    'smoke and carbon monoxide alarms',
    'medical or safety-critical equipment',
  ),
  'three-day-kit': (
    'Medicines that need refrigeration: ask your prescriber or pharmacist first',
    'Do not stop, throw away or ration a medicine you depend on',
    'If you are already in an outage and unsure, call your doctor or pharmacist.',
    'Only use the medicine until you have a new supply.',
    'The older "discard" line, read alone, could lead someone to go without a medicine they need',
    '{{cite:start-fema-power-sheet}}',
    '{{cite:start-ready-power}}',
    '{{cite:ready-are-you-ready}}',
  ),
}
UNSAFE_OLD = (
  ('household-emergency-plan', "Switch off the main power for an evening"),
  ('three-day-kit', 'it also says that if the power is out more than a day you should discard refrigerated medication'),
)
QA_NEW = (
  ('household-emergency-plan', 'The lights-out evening.</strong> Keep the household electricity on.'),
  ('three-day-kit', 'That general rule cannot tell you whether a particular prescription is safe to continue'),
)
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')


class HoldError(ValueError):
    pass


def require(test, message):
    if not test:
        raise HoldError(message)


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def read(root: Path, relative: str) -> bytes:
    p = root / relative
    require(root.is_dir() and not root.is_symlink() and p.is_file() and
            not p.is_symlink() and p.resolve().is_relative_to(root.resolve()),
            'missing, linked or out-of-tree input: ' + relative)
    data = p.read_bytes()
    require(0 < len(data) < 300_000, 'file size limit: ' + relative)
    return data


def verify(root: Path) -> dict:
    root = root.resolve(strict=True)
    for path, digest in GUARDS.items():
        require(blob(read(root,path)) == digest, 'source/taxonomy regression or drift: '+path)
    article_dir = root / 'preparedness/content/articles'
    names = {p.name.removesuffix('.body.html') for p in article_dir.glob('*.body.html')}
    metas = {p.name.removesuffix('.meta.json') for p in article_dir.glob('*.meta.json')}
    require(len(names) == 35 and names == metas, '35 full-depth articles and metadata not preserved')
    tax = json.loads(read(root,'preparedness/taxonomy.json').decode('utf-8'))
    slate = tax.get('slate')
    require(type(slate) is list and len(slate) == 35 and
            {q.get('slug') for q in slate if type(q) is dict} == names,
            'original 35 article URLs/slate changed')
    source = json.loads(read(root,'preparedness/sources/fragments/start.json').decode('utf-8'))
    require(type(source.get('sources')) is list, 'source notes malformed')
    citation_rows = {}
    for slug, digest in ARTICLES.items():
        path = 'preparedness/content/articles/' + slug + '.body.html'
        data = read(root,path)
        require(blob(data) == digest, 'QA repair would overwrite a newer article revision: '+slug)
        text = data.decode('utf-8',errors='strict')
        for phrase in KEY[slug]:
            require(text.count(phrase) >= 1, 'integrated caution/source token absent: '+slug+' '+phrase)
        for s, obsolete in UNSAFE_OLD + QA_NEW:
            if s == slug:
                require(obsolete not in text, 'stale unsafe or QA text was merged: '+slug)
        citation_rows[slug] = Counter(CITE.findall(text))
        require(sum(citation_rows[slug].values()) > 0, 'missing article citations')
    return {
        'schema_version':1,'issue':136,'frozen_integration_commit':BASE,
        'qa_157_head':QA157,'qa_169_head':QA169,
        'release_state':'HOLD','may_publish':False,
        'independent_source_claim_checks':0,'qualified_safety_clearance':False,
        'qa_157_transplant':'REJECT_STALE_ALREADY_SUPERSEDED',
        'qa_169_fixture_change':'NOT_MERGED_PENDING_NATIVE_TESTS',
        'source_metadata_rollback':'BLOCKED','taxonomy_rollback':'BLOCKED',
        'article_count':len(names),
        'citation_occurrences_in_examined_articles': {k:sum(v.values()) for k,v in citation_rows.items()},
        'notice':'Text custody is NOT clinical, factual, QD, or public-release approval.'
    }


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,required=True)
    args=p.parse_args(argv)
    try:
        print(json.dumps(verify(args.repo_root),indent=2,sort_keys=True))
        return 0
    except (HoldError,ValueError,OSError,UnicodeError,TypeError) as err:
        print('INVALID/HOLD '+str(err),file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())

"""R381: read-only claim-to-original-source qualifier custody, never a medical or release gate.

Target: the original Water Article #7, not a new article or an automatic rewrite.
Returns an unresolved human-review docket. Accepts caller-supplied original bytes for
isolated adversarial tests; native mode requires SHA-matched original Git objects.
"""
from __future__ import annotations
import argparse
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

REPO = 'finalvestigestudios/final-vestige-site-layer'
BRANCH = 'claude/prep-start-bbfeb8'
BRANCH_SHA = '2122d856fce9f64887c16df3d52e64be9f59a55b'
BODY_SHA = '67aa44e9a332f57fb70298a3867410d8f66c8c15'
META_SHA = '33789d3db0ec06007deb50d0293361f07cea27ae'
REGISTER_SHA = 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77'
SOURCE_ID = 'cdc-find-clean-water'
SOURCE_URL = 'https://www.cdc.gov/water-emergency/about/how-to-find-clean-water-in-an-emergency.html'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
WHITESPACE = re.compile(r'\s+')


def blob_sha(b: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b, usedforsecurity=False).hexdigest()


def git_blob(root: Path, sha: str) -> bytes:
    if not re.fullmatch('[0-9a-f]{40}', sha):
        raise ValueError('Malformed immutable Git SHA')
    out = subprocess.run(['git','-C',str(root),'cat-file','blob',sha],
                         capture_output=True,timeout=20,check=True).stdout
    if blob_sha(out) != sha:
        raise ValueError('Git blob mismatch')
    return out


class LIParser(HTMLParser):
    """Extract each complete list item with nested descendants, not surrounding prose."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.chunks = []
        self.items = []
    def handle_starttag(self, tag, attrs):
        if tag == 'li':
            if self.depth == 0:
                self.chunks = []
            self.depth += 1
    def handle_endtag(self, tag):
        if tag == 'li' and self.depth:
            self.depth -= 1
            if self.depth == 0:
                self.items.append(WHITESPACE.sub(' ',unescape(' '.join(self.chunks))).strip())
    def handle_data(self,data):
        if self.depth:
            self.chunks.append(data)


def assess(body: bytes, meta: dict, register: dict) -> dict:
    """Deterministic machine flags only. PASS is impossible even if all issues disappear."""
    errors = []
    risks = []
    if not isinstance(body, bytes) or not isinstance(meta, dict) or not isinstance(register, dict):
        return {'status':'INVALID_HARD_HOLD','errors':['Invalid original inputs'],
                'risks':[], 'publication_approved':False,'qualified_safety_approved':False}
    try:
        html = body.decode('utf-8')
    except UnicodeError:
        return {'status':'INVALID_HARD_HOLD','errors':['Body is not UTF-8'],
                'risks':[], 'publication_approved':False,'qualified_safety_approved':False}
    if meta.get('slug') != 'homemade-water-filters' or meta.get('section') != 'water':
        errors.append('WRONG_ARTICLE_IDENTITY')
    if meta.get('status',{}).get('publish') != 'draft':
        errors.append('NOT_A_PRIVATE_DRAFT')
    if meta.get('safety_review',{}).get('state') != 'pending':
        errors.append('SAFETY_REVIEW_NOT_PENDING')
    sources = register.get('sources')
    if not isinstance(sources,list):
        sources = []
        errors.append('MALFORMED_BASE_REGISTER')
    matching = [s for s in sources if isinstance(s,dict) and s.get('id')==SOURCE_ID]
    if len(matching)!=1:
        errors.append('BASE_SOURCE_ID_NOT_UNIQUE')
    src = matching[0] if len(matching)==1 else {}
    raw_url = src.get('url')
    if raw_url != SOURCE_URL or urlsplit(str(raw_url)).scheme != 'https':
        errors.append('SOURCE_DESTINATION_CHANGED')
    if src.get('human_link_check') is True:
        risks.append('HUMAN_CHECK_CLAIM_NOT_ACCEPTED_AS_INDEPENDENT_REVIEW')
    citations = CITE.findall(html)
    if SOURCE_ID not in citations:
        errors.append('ORIGINAL_CITATION_ABSENT')
    if html.count('{{cite:') != len(citations):
        errors.append('MALFORMED_CITATION_TOKEN')
    uses = meta.get('source_use')
    if not isinstance(uses,dict):
        errors.append('SOURCE_USE_NOT_OBJECT')
        uses = {}
    if SOURCE_ID not in uses or not isinstance(uses.get(SOURCE_ID),str) or not uses.get(SOURCE_ID,'').strip():
        risks.append('SOURCE_USE_SCOPE_MISSING_NEEDS_HUMAN_ADJUDICATION')
    # BASE 'supports' is a short paraphrase, NOT permission to state a claim
    # without the actual agency's conditions; a missing condition is a review flag.
    support = WHITESPACE.sub(' ',str(src.get('supports','')).lower())
    if not support.strip():
        errors.append('SOURCE_SUPPORTS_MISSING')
    if ('melted ice' in support or 'ice cubes' in support) and not any(
            q in support for q in ('uncontaminated','not contaminated','safe water','not been contaminated')):
        risks.append('BASE_SUMMARY_ICE_ORIGIN_CONDITION_OMITTED')
    if 'heater tank' in support and not ('home heating system' in support or 'radiator' in support):
        risks.append('BASE_SUMMARY_TAP_VERSUS_HEATING_TANK_UNDIFFERENTIATED')
    parser = LIParser()
    parser.feed(html)
    # This source also supports a separate chemical-contamination caution later
    # in the manuscript. Select only the *household inside-water* assertion.
    candidates = [li for li in parser.items if SOURCE_ID in CITE.findall(li)
                  and 'other clean water in the house' in li.lower()]
    if len(candidates)!=1:
        errors.append('EXPECTED_SINGLE_CLAIM_LIST_ITEM_NOT_FOUND')
    claim = candidates[0] if len(candidates)==1 else ''
    lower = claim.lower()
    if 'melted ice' in lower or 'ice cubes' in lower:
        if not any(q in lower for q in ('uncontaminated','not contaminated','made from safe water','made with safe water','not been contaminated')):
            risks.append('ARTICLE_ICE_ORIGIN_CONDITION_OMITTED')
    else:
        errors.append('ORIGINAL_ICE_CLAIM_MISSING')
    if 'water heater tank' in lower:
        if not any(q in lower for q in ('tap water heater tank','domestic tap water heater','not the home heating system','not a radiator')):
            risks.append('ARTICLE_HEATER_TANK_TYPE_CONDITION_OMITTED')
    else:
        errors.append('ORIGINAL_HEATER_CLAIM_MISSING')
    # A printed household guide must not treat this machine review as a green light.
    risks.append('HUMAN_LOCAL_CONTAMINATION_AND_QUALIFIED_SAFETY_REVIEW_REQUIRED')
    return {
        'status':'INVALID_HARD_HOLD' if errors else 'CLAIM_CONTEXT_REVIEW_HARD_HOLD',
        'original_article':'homemade-water-filters', 'original_source_id':SOURCE_ID,
        'claim_excerpt':claim[:500], 'citation_occurrences':citations.count(SOURCE_ID),
        'errors':sorted(set(errors)), 'risks':sorted(set(risks)),
        'source_url':SOURCE_URL, 'human_source_check_passed':False,
        'publication_approved':False,'qualified_safety_approved':False,
        'verified_paid_offer':False,'verified_net_revenue':None,
    }


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
    args=p.parse_args()
    try:
        body=git_blob(args.repo,BODY_SHA)
        meta=json.loads(git_blob(args.repo,META_SHA))
        register=json.loads(git_blob(args.repo,REGISTER_SHA))
        report=assess(body,meta,register)
        report['original_blobs_verified']=True
    except (ValueError,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired,TypeError) as e:
        report={'status':'INVALID_HARD_HOLD','original_blobs_verified':False,
                'errors':[type(e).__name__+': '+str(e)],'publication_approved':False,
                'qualified_safety_approved':False}
    print(json.dumps(report,indent=2,sort_keys=True))
    return 2  # Never claim QD PASS / production readiness.

if __name__=='__main__':
    raise SystemExit(main())

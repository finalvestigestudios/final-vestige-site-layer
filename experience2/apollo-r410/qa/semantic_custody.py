#!/usr/bin/env python3
"""Apollo R410 read-only source-to-rendered semantic custody.

Does not produce a release PASS. Production accepts only original PR #158 template
with the pinned Git blob. Synthetic positive fixtures require explicit test API.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import importlib.util
import json
import re
import sys

BASE = Path(__file__).resolve().parents[2]
PARENT = BASE / 'apollo-r409' / 'qa' / 'source_custody.py'
spec = importlib.util.spec_from_file_location('apollo_r409_custody', PARENT)
if not spec or not spec.loader: raise RuntimeError('R409 parent source inspector missing')
r409 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r409
spec.loader.exec_module(r409)

@dataclass
class Record:
    id: str = ''
    text: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    headings: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)

@dataclass
class Card:
    kind: str = ''
    links: list[str] = field(default_factory=list)
    text: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)


def norm(text: str) -> str:
    return ' '.join(text.split())

class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth=0;self.active_record=None;self.active_card=None
        self.records: list[Record]=[];self.cards: list[Card]=[]
        self._heading_depth=None;self._heading_text=[]
        self._ledger_depth=None;self._ledger_text=[]
        self.events=[]
    def handle_starttag(self,tag,items):
        a=dict(items);self.depth += 0 if tag in {'meta','input','link','br','hr','img','source','wbr','area'} else 1
        if 'data-fvx-ledger' in a: self._ledger_depth=self.depth
        if tag=='article' and 'data-fvx-record' in a:
            self.active_record=(Record(id=a.get('id','')),self.depth)
        if tag=='li' and 'data-fv-r408-card' in a:
            self.active_card=(Card(kind=a.get('data-fv-r408-kind','')),self.depth)
        if tag in ('h2','h3') and self.active_record:
            self._heading_depth=self.depth;self._heading_text=[]
        for item in (self.active_card,self.active_record):
            if item:
                obj=item[0]
                if a.get('hidden') is not None or 'hidden' in a or a.get('aria-hidden')=='true' or re.search(r'(^|;)\s*(display\s*:\s*none|visibility\s*:\s*hidden)',a.get('style',''),re.I):
                    obj.flags.append('concealed_content')
                if tag=='a':obj.links.append(a.get('href',''))
        if tag=='a' and a.get('href')==r409.ARTICLE:self.events.append(('cta',self.depth))
    def handle_data(self,data):
        if self.active_record:self.active_record[0].text.append(data)
        if self.active_card:self.active_card[0].text.append(data)
        if self._heading_depth is not None:self._heading_text.append(data)
    def handle_endtag(self,tag):
        if tag in ('h2','h3') and self._heading_depth==self.depth and self.active_record:
            self.active_record[0].headings.append(norm(''.join(self._heading_text)))
            self._heading_depth=None
        if tag=='article' and self.active_record and self.active_record[1]==self.depth:
            self.records.append(self.active_record[0]);self.active_record=None
        if tag=='li' and self.active_card and self.active_card[1]==self.depth:
            self.cards.append(self.active_card[0]);self.active_card=None
        if self._ledger_depth==self.depth:
            self.events.append(('ledger_end',self.depth));self._ledger_depth=None
        self.depth=max(0,self.depth-1)

# Each Atlas card must retain its own primary-source boundary (not a disclaimer
# inserted elsewhere on the page). The index is intentionally NOT geospatial.
CARD_LIMITS=(
 'test setting does not identify the specific cause of ignition',
 'oxygen-rich environment explains propagation risk',
 'recorded markers are not a frame-by-frame simulation',
 'safety-design constraint should not be treated',
 'do not present one proposed ignition site',
 'later deliberate fire tests cannot retroactively identify',
)

def compare(original_html: str, rendered_html: str, *, original_blob: str | None = None,
            allow_synthetic_fixture: bool = False) -> dict:
    """Compare six genuine template records to the rendered, namespaced instances.

    Passing `original_blob` is permitted only for local synthetic unit tests; this
    option does not authorize production, and CLI never exposes it.
    """
    expected=r409.EXPECTED_ORIGINAL_BLOB
    real_blob=r409.git_blob(original_html.encode('utf-8'))
    if allow_synthetic_fixture and original_blob:
        expected=original_blob
    errors=[]
    if real_blob!=expected:errors.append('original_git_blob_mismatch')
    if allow_synthetic_fixture is False and original_blob is not None:errors.append('test_bypass_disallowed')
    a=Extract();a.feed(original_html);a.close()
    b=Extract();b.feed(rendered_html);b.close()
    if len(a.records)!=6:errors.append('original_record_count')
    if len(b.records)!=6:errors.append('rendered_record_count')
    if len(b.cards)!=6:errors.append('atlas_count')
    if len(a.records)==len(b.records)==6:
        for idx,(one,two) in enumerate(zip(a.records,b.records),1):
            if norm(' '.join(one.text)) != norm(' '.join(two.text)):
                errors.append(f'record_{idx:02d}_historical_text_drift')
            if one.headings!=two.headings:errors.append(f'record_{idx:02d}_heading_drift')
            if one.links!=two.links:errors.append(f'record_{idx:02d}_source_link_drift')
            if len(set(two.links))!=len(two.links):errors.append(f'record_{idx:02d}_duplicate_links')
            if two.flags:errors.append(f'record_{idx:02d}_concealed')
            if not two.id:errors.append(f'record_{idx:02d}_missing_id')
    if len(b.cards)==6 and len(b.records)==6:
        for idx,(card,record) in enumerate(zip(b.cards,b.records),1):
            n=f'{idx:02d}'
            if card.kind != r409.EXPECTED_ATLAS_CATEGORIES[idx-1]:errors.append('category_drift_'+n)
            if card.links.count('#'+record.id)!=1:errors.append('atlas_record_binding_'+n)
            if card.links.count(r409.LATER if idx==6 else r409.BOARD)!=1:
                errors.append('atlas_NASA_publication_'+n)
            if CARD_LIMITS[idx-1] not in norm(' '.join(card.text)).casefold():
                errors.append('atlas_evidence_limitation_'+n)
            if card.flags:errors.append('atlas_concealed_'+n)
        if b.events.count(('cta',0)):
            errors.append('invalid_cta_event')
        if not any(x[0]=='ledger_end' for x in b.events):errors.append('missing_ledger_boundary')
    if not allow_synthetic_fixture:
        parent=r409.check_rendered(rendered_html)
        if not parent['pass']:errors.append('R409_parent_contract:'+','.join(parent['errors']))
    return {'pass':not errors,'errors':sorted(set(errors)),'original_blob':real_blob,
            'expected_original_blob':expected,'record_count':len(b.records),'atlas_count':len(b.cards),
            'status':'SYNTHETIC_TEST_ONLY' if allow_synthetic_fixture else 'REVIEW_ONLY_NOT_RELEASE_AUTHORIZED'}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original',required=True,type=Path)
    parser.add_argument('--rendered',required=True,type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if not args.original.is_file() or not args.rendered.is_file():
        output={'pass':False,'errors':['required_input_missing'],'status':'HOLD'}
    else:
        output=compare(args.original.read_text(encoding='utf-8'),args.rendered.read_text(encoding='utf-8'))
    data=json.dumps(output,indent=2,sort_keys=True)+'\n'
    if args.output:args.output.write_text(data,encoding='utf-8')
    print(data)
    # Even an exact text match is a review input, never a deploy authorization.
    return 2 if not output['pass'] else 0
if __name__=='__main__':sys.exit(main())

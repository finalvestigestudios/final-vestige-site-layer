"""R171 Apollo archive caption readability: guarded, OFFLINE HTML-only candidate.

This deliberately does not edit WordPress and must be reviewed against R169/R170
release custody before any integration. Accepts only the three exact, witnessed
NASA figure captions in the original Page 2017 gallery.
"""
from __future__ import annotations
import hashlib
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser

FIG = re.compile(r'<figcaption class="fvx-chrono-gallery__caption">(?P<body>.*?)</figcaption>', re.DOTALL)
SPLIT = re.compile(r'^(<strong>[^<>]+</strong>)([^<>]+)(<small>.*</small>)$', re.DOTALL)
NASA_LINKS = (
    'https://www.nasa.gov/image-detail/amf-s66-58038/',
    'https://www.nasa.gov/image-detail/amf-s67-15717/',
    'https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129',
)
# SHA-256 of each complete original figcaption HTML, independently confirmed
# against the official WordPress Page 2017 editor export (Nov 5 modification).
# These are set from the source-verified excerpt; do not relax on source drift.
EXPECTED_SHA256 = (
    '4f61779802a66cf1323ad4a4fae2756f8ff751aea0c167635743154a0c01a291',
    '3bfebeff3f4ea158087e5122a26b43cafe696cdbca7badb90083dde8dee4b8d7',
    'c11afb5f436c4954e468515d20155b1c9b76b4918c5630a2f7f1ad28607ebd1c',
)

class _CaptionText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts=[]
    def handle_data(self, data):
        self.parts.append(data)
    def text(self):
        return ''.join(self.parts)


def digest(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def transform(html: str) -> tuple[str, dict]:
    matches=list(FIG.finditer(html))
    if len(matches)!=3:
        raise ValueError('HOLD: expected three archive captions, got '+str(len(matches)))
    modified=html
    receipt=[]
    for i, m in reversed(list(enumerate(matches))):
        original=m.group(0)
        if digest(original)!=EXPECTED_SHA256[i]:
            raise ValueError('HOLD: witnessed caption '+str(i)+' changed')
        if original.count(NASA_LINKS[i])!=1 or original.count('rel="noopener noreferrer"')!=1:
            raise ValueError('HOLD: NASA source custody mismatch')
        parts=SPLIT.fullmatch(m.group('body'))
        if not parts or '<a ' not in parts.group(3):
            raise ValueError('HOLD: unexpected caption structure')
        head,description,citation=parts.groups()
        # Explicit whitespace + block semantics; the text content and NASA
        # anchor remain identical even when CSS/JS do not execute.
        replacement=(f'<figcaption class="fvx-chrono-gallery__caption fvx-archive-caption">'
                     f'{head}\n  <span class="fvx-archive-caption__body">{description}</span>\n  '
                     f'<small class="fvx-archive-caption__source">{citation[7:-8]}</small>'
                     f'</figcaption>')
        a,b=_CaptionText(),_CaptionText()
        a.feed(original); b.feed(replacement)
        if ''.join(a.text().split())!=''.join(b.text().split()):
            raise ValueError('HOLD: caption text changed')
        if NASA_LINKS[i] not in replacement:
            raise ValueError('HOLD: source removed')
        modified=modified[:m.start()]+replacement+modified[m.end():]
        receipt.append({'index':i,'before_sha256':digest(original),'after_sha256':digest(replacement),
                        'source_url':NASA_LINKS[i],'text_preserved':True})
    receipt.reverse()
    if 'https://payhip.com/' in modified and 'https://payhip.com/' not in html:
        raise ValueError('HOLD: commercial URL added')
    return modified, {'status':'BUILT_STAGING_ONLY','before_sha256':digest(html),
                      'after_sha256':digest(modified),'captions':receipt,
                      'wordpress_writes':0,'commercial_activation':'HOLD',
                      'installed_wordpress_qa':'NOT_EXECUTED',
                      'r170_integrity_integration':'REVIEW_REQUIRED'}

if __name__=='__main__':
    import argparse
    from pathlib import Path
    cli=argparse.ArgumentParser()
    cli.add_argument('source',type=Path);cli.add_argument('output',type=Path)
    opts=cli.parse_args()
    out,receipt=transform(opts.source.read_text(encoding='utf-8'))
    opts.output.write_text(out,encoding='utf-8')
    opts.output.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(receipt,sort_keys=True))

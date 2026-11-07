#!/usr/bin/env python3
"""No-send, privacy-safe *draft* near-offer disclosure evidence preflight.

Designed as a narrow companion to R167/R168 received-EML checks, NOT a mail
renderer, native Jetpack preview, merchant-permission oracle, or legal opinion.
No network, subscriber data, or sending. Python standard library only.
"""
from html.parser import HTMLParser
from urllib.parse import urlparse
import re
import json
import argparse
from pathlib import Path

HOLD = 'HOLD_UNSENT'
MAX_CHARS = 100000
GUIDES = ('/mind/zen12-guide/', '/mind/hypnosis-live-guide/')
DISCLOSURE = re.compile(r'(?:final vestige|we)\s+may\s+(?:earn|receive)\s+(?:a\s+)?commission', re.I)
RISKY_CLAIM = re.compile(r'(?i)(guaranteed results|cures anxiety|12 minutes\s*=\s*1 hour|buy now before midnight|offer ends (?:today|tonight)|clinically proven to reprogram)')
PLACEHOLDER = re.compile(r'\[\[[^\]\n]+\]\]|\{\{[^}\n]+\}\}')
DIRECT_AFFILIATE = re.compile(r'(?i)(awin1\.com|clickbank|inspire3\.com/aff|[?&](?:aff|ref|affiliate_id|hop)=)')

class VisibleAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chunks = []
        self.links = []
        self.stack = []  # (tag, suppressed, anchor)
        self.depth = 0
        self.active_anchors = []

    def _pos(self):
        return sum(len(x) for x in self.chunks)

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        hide = tag in ('style', 'script', 'template', 'noscript') or 'hidden' in d or d.get('aria-hidden') == 'true' or bool(re.search(r'(?i)display\s*:\s*none|visibility\s*:\s*hidden', d.get('style','')))
        suppressed = self.depth > 0 or hide
        if hide:
            self.depth += 1
        is_anchor = tag == 'a' and not suppressed
        if is_anchor:
            self.active_anchors.append({'href':d.get('href',''), 'start':self._pos()})
        self.stack.append((tag, hide, is_anchor))
        if tag in ('p','div','li','h1','h2','h3','br') and not suppressed:
            self.chunks.append(' ')

    def handle_endtag(self, tag):
        # For standard, well-formed email-safe HTML; malformed markup fails readiness.
        if not self.stack or self.stack[-1][0] != tag:
            # Accept common non-matching optional container closes but mark malformed.
            self.malformed = True
            return
        _, hide, anchor = self.stack.pop()
        if anchor and self.active_anchors:
            a = self.active_anchors.pop()
            a['end'] = self._pos()
            self.links.append(a)
        if hide:
            self.depth -= 1
        if tag in ('p','div','li','h1','h2','h3') and not self.depth:
            self.chunks.append(' ')

    def handle_startendtag(self, tag, attrs):
        if tag in ('br','img','hr','input','meta','link'):
            if tag=='br' and not self.depth: self.chunks.append(' ')
            return
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        if not self.depth:
            self.chunks.append(data)

    @property
    def text(self):
        return ''.join(self.chunks)


def _firstparty_guide(href):
    u = urlparse(href)
    return u.scheme == 'https' and u.hostname in ('finalvestige.com','www.finalvestige.com') and u.path.lower() in GUIDES and not u.query and not u.fragment


def audit(html, plain, near_chars=220):
    if not isinstance(html,str) or not isinstance(plain,str) or max(len(html),len(plain))>MAX_CHARS:
        raise ValueError('bounded HTML and plaintext strings required')
    p = VisibleAudit(); p.malformed=False; p.feed(html)
    # Strictly require well-formed HTML in the candidate, not vendor-rendered email HTML.
    malformed = p.malformed or bool(p.active_anchors) or bool(p.stack)
    valid = [a for a in p.links if _firstparty_guide(a['href'])]
    direct = any(DIRECT_AFFILIATE.search(a['href']) for a in p.links)
    disclosures = [(m.start(),m.end()) for m in DISCLOSURE.finditer(p.text)]
    linked_near = [any(0 <= a['start']-e <= near_chars or 0 <= s-a['end'] <= near_chars or s<=a['start']<=e for s,e in disclosures) for a in valid]
    plain_near = bool(DISCLOSURE.search(plain))
    flags = {
        'html_is_well_formed_enough_for_preflight': not malformed,
        'exactly_one_firstparty_guide_cta': len(valid)==1,
        'disclosure_adjacent_to_every_qualifying_html_cta': bool(valid) and all(linked_near),
        'plain_text_contains_disclosure': plain_near,
        'no_direct_affiliate_or_tracking_links': not direct,
        'no_unresolved_bracket_placeholders': not bool(PLACEHOLDER.search(html+'\n'+plain)),
        'no_risky_unverified_claim_phrases': not bool(RISKY_CLAIM.search(p.text+'\n'+plain)),
    }
    return {'type':'R173_draft_near_offer_preflight','version':1,'release_decision':HOLD,
            'structural_draft_readiness':'INSPECTION_ONLY' if all(flags.values()) else 'FAIL_CLOSED',
            'checks':flags,'qualifying_offer_guide_count':len(valid),
            'human_reviewer_required':True,
            'limits':['No HTML layout or color inspection; proximity in extracted text is not visual adjacency.',
                      'No proof of Jetpack rendering, unsubscribe, valid mailing address, partner acceptance or email-channel permission.',
                      'No received-email evidence; never authorize publication, sending or affiliate activation.']}


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--html',type=Path,required=True); a.add_argument('--text',type=Path,required=True)
    a.add_argument('--out',type=Path,required=True)
    args=a.parse_args(); r=audit(args.html.read_text(),args.text.read_text())
    args.out.write_text(json.dumps(r,indent=2)+'\n'); print('HOLD_UNSENT: offline draft preflight only')

if __name__=='__main__': main()

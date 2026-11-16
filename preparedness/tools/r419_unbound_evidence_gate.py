#!/usr/bin/env python3
"""R419: orphaned visible evidence custody across all 35 draft article exports.

R418 secures original ordinary paragraph/list claims, but HTML text in a visible
<aside>, <div>, <section> or raw <span> outside a tracked block escaped its claim
and safety detectors. This additive gate conservatively inventories every
reader-visible text token not owned by R416's semantic block set and compares
its normalized occurrence multiset with EACH pinned original manuscript
candidate, separately for WordPress and private preview. New or removed orphan
text is a review failure, even when both exports agree. It never decides whether
any original or new instruction is safe, true, publishable, or monetizable.

Source files, source IDs, citations and original branches are never changed.
"""
from __future__ import annotations
import argparse
from collections import Counter
from html.parser import HTMLParser
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

_spec = spec_from_file_location('r418_uncited_claim_custody_gate',
                               Path(__file__).with_name('r418_uncited_claim_custody_gate.py'))
_r418 = module_from_spec(_spec)
sys.modules[_spec.name] = _r418
_spec.loader.exec_module(_r418)
_r416 = _r418._r416
_r409 = _r418._r409
_r412 = _r418._r412
_r414 = _r418._r414

# Only meaningful reader text is counted. Inline tags do NOT break a phrase.
WORDS = _r416.WORDS
SEMANTIC_BLOCKS = frozenset(_r416.BLOCKS)
CONTAINERS = frozenset({'article','main','div','section','aside','figure',
    'header','footer','nav','details','summary','ul','ol','table','tbody',
    'thead','tfoot','tr','form','address','hgroup','dialog'})
VOID = frozenset({'area','base','br','col','embed','hr','img','input','link',
    'meta','param','source','track','wbr'})
INERT = frozenset({'script','style','template','noscript'})
MAX_HTML_BYTES = 1_000_000
MAX_ORPHAN_GROUPS = 3000
MAX_ORPHAN_TOKENS = 12000


class OrphanInspector(HTMLParser):
    """Collect text whose nearest ancestor is NOT a semantic evidence block.

    A span/em/strong/a chain remains part of the same containing div/aside.
    HTML structure is otherwise inspected by the inherited R410/R411 gates;
    this inspector refuses malformed nesting and opaque inert-content changes.
    """
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.groups = []
        self.root_words = []
        self.tokens = 0
        self.covered_depth = 0
        self.inert_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.casefold()
        if tag in VOID:
            return
        frame = {'tag':tag, 'words':[]}
        self.stack.append(frame)
        if tag in SEMANTIC_BLOCKS:
            self.covered_depth += 1
        if tag in INERT:
            self.inert_depth += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.casefold() not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.casefold()
        if tag in VOID:
            raise ValueError('closing void tag in original/unbound inspector')
        if not self.stack or self.stack[-1]['tag'] != tag:
            raise ValueError('unbalanced original/unbound evidence HTML')
        frame = self.stack.pop()
        if tag in SEMANTIC_BLOCKS:
            self.covered_depth -= 1
        if tag in INERT:
            self.inert_depth -= 1
        if frame['words']:
            self.groups.append(tuple(frame['words']))
            if len(self.groups) > MAX_ORPHAN_GROUPS:
                raise ValueError('too many unbound evidence groups')

    def handle_data(self, data):
        if self.inert_depth or self.covered_depth:
            return
        words = [w.casefold() for w in WORDS.findall(data)]
        if not words:
            return
        self.tokens += len(words)
        if self.tokens > MAX_ORPHAN_TOKENS:
            raise ValueError('too many unbound evidence tokens')
        for frame in reversed(self.stack):
            if frame['tag'] in CONTAINERS:
                frame['words'].extend(words)
                return
        self.root_words.extend(words)

    def finish(self):
        self.close()
        if self.stack or self.covered_depth or self.inert_depth:
            raise ValueError('unclosed unbound evidence HTML')
        if self.root_words:
            self.groups.append(tuple(self.root_words))
        return tuple(self.groups)


def is_markdown_original(data):
    """Match R416's original-candidate format decision, no external reads."""
    if isinstance(data, bytes):
        data = data.decode('utf-8', 'strict')
    if not isinstance(data, str):
        raise ValueError('original candidate not text')
    # Broader than R416 deliberately: standalone <aside>/<figure> originals
    # were previously mistaken for Markdown and their prose left unguarded.
    return re.search(r'<(?:article|section|p|h[1-6]|div|aside|main|figure|header|footer|nav|details|summary|ul|ol|li|blockquote|table|address)\b', data[:2000], re.I) is None


def unbound_sequence(data, *, candidate=False):
    if isinstance(data, bytes):
        data = data.decode('utf-8', 'strict')
    if not isinstance(data, str) or not 0 < len(data.encode('utf-8')) <= MAX_HTML_BYTES:
        raise ValueError('invalid unbound evidence input')
    # Markdown originals are fully represented by the existing R416 block parser.
    # Their raw Markdown punctuation is NOT unbound rendered HTML prose.
    if candidate and is_markdown_original(data):
        return ()
    parser = OrphanInspector()
    parser.feed(data)
    return parser.finish()


def unbound_groups(data, *, candidate=False):
    return Counter(unbound_sequence(data, candidate=candidate))


def unbound_fidelity(original, rendered):
    """Return (source groups, missing groups, extra groups, missing tokens, extra tokens, order drift)."""
    old_order = unbound_sequence(original, candidate=True)
    new_order = unbound_sequence(rendered)
    old = Counter(old_order)
    new = Counter(new_order)
    missing = old - new
    added = new - old
    return (sum(old.values()), sum(missing.values()), sum(added.values()),
            sum(len(group)*n for group,n in missing.items()),
            sum(len(group)*n for group,n in added.items()),
            int(old == new and old_order != new_order))


def check(original, manifest, exports, candidates, *, raw_original=None, test_only=False):
    parent = _r418.check(original, manifest, exports, candidates,
                         raw_original=raw_original, test_only=test_only)
    errors = list(parent.get('errors', []))
    details = []
    try:
        for entry in original['original_articles']:
            slug = entry['slug']
            if not isinstance(slug,str) or not _r414.SLUG.fullmatch(slug):
                raise ValueError('unsafe original article slug')
            pair = exports[slug]
            if not isinstance(pair, (tuple,list)) or len(pair) != 2:
                raise ValueError('missing paired HTML exports')
            for pin in sorted(set(entry['body_candidate_git_blobs'])):
                source = candidates[(slug,pin)]
                if not isinstance(source,bytes) or _r409.blob(source)!=pin:
                    errors.append('R419 original Git blob mismatch: '+slug)
                    continue
                for index, export in enumerate(pair):
                    channel = ('wordpress','private_preview')[index]
                    count,missing,added,miss_tokens,add_tokens,order_drift = unbound_fidelity(source,export)
                    if missing or added or order_drift:
                        errors.append('R419 visible prose outside semantic evidence blocks changed or added: '
                                      +slug+' @ '+pin+' '+channel)
                    details.append({'slug':slug,'original_blob':pin,'channel':channel,
                        'original_unbound_groups':count,
                        'missing_original_unbound_groups':missing,
                        'new_unreviewed_unbound_groups':added,
                        'missing_unbound_words':miss_tokens,
                        'new_unreviewed_unbound_words':add_tokens,
                        'unbound_reading_order_drift':order_drift,
                        'human_source_and_safety_review_required':True})
    except (ValueError,TypeError,KeyError,IndexError,UnicodeError,OverflowError,
            AttributeError,RecursionError) as exc:
        errors.append('R419 missing or malformed original unbound evidence: '+str(exc))
    return {'release_state':'DRAFT_HARD_HOLD','eligible':False,
        'publication_approved':False,'qualified_safety_approved':False,
        'merchant_offer_verified':False,
        'integrity_ok':bool(parent.get('integrity_ok')) and not errors,
        'errors':sorted(set(errors)),'draft_checks':len(details),'details':details,
        'warnings':list(parent.get('warnings',[]))+[
            'Structural unbound-text custody is not a factual or medical safety adjudication',
            'Legitimate new standalone guidance and markup may require human review; this gate fails closed',
            'Unreviewed manuscript forks, original source disputes and sale validation remain HARD HOLD']}


def main():
    ap = argparse.ArgumentParser(description='R419 unbound visible evidence — NEVER PUBLISH')
    for name in ('original','manifest','export_root','private_candidate_root'):
        ap.add_argument(name,type=Path)
    args=ap.parse_args()
    try:
        raw = _r409.read_original(args.original)
        original = json.loads(raw.decode('utf-8'),object_pairs_hook=_r409.unique_pairs)
        manifest = json.loads(_r409.read_original(args.manifest).decode('utf-8'),
                              object_pairs_hook=_r409.unique_pairs)
        exports,candidates={},{}
        for entry in original['original_articles']:
            slug=entry['slug']
            if not isinstance(slug,str) or not _r414.SLUG.fullmatch(slug):
                raise ValueError('invalid article slug')
            exports[slug]=(_r409.read_original(args.export_root/'wordpress'/(slug+'.html')),
                           _r409.read_original(args.export_root/'preview'/(slug+'.html')))
            for pin in set(entry['body_candidate_git_blobs']):
                if not isinstance(pin,str) or not _r418.HEX40.fullmatch(pin):
                    raise ValueError('invalid original candidate pin')
                candidates[(slug,pin)]=_r412.checked_candidate_read(
                    args.private_candidate_root/slug/(pin+'.txt'),
                    root=args.private_candidate_root)
        result=check(original,manifest,exports,candidates,raw_original=raw)
    except (OSError,ValueError,TypeError,KeyError,IndexError,UnicodeError,
            OverflowError,RecursionError) as exc:
        result={'release_state':'DRAFT_HARD_HOLD','eligible':False,
            'publication_approved':False,'qualified_safety_approved':False,
            'integrity_ok':False,'errors':[str(exc)]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2

if __name__=='__main__':
    raise SystemExit(main())

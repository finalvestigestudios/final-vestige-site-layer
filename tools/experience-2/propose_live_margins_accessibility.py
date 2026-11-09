#!/usr/bin/env python3
"""REVIEW-ONLY Page 6 Margins accessibility preview. No CMS or network calls.

Accept an explicitly exported, read-only raw WordPress Page 6 JSON document.
Write ONLY the first Gutenberg HTML block as a disposable review candidate.
Never check production editor content, visitor records or original facts into Git.
"""
import argparse
import html
import json
import re
from pathlib import Path

SPAN = re.compile(r'<span class="fv-margin-strip__item" style="--i:(\d+)">([^<>]+)</span>')
WINDOW = re.compile(r'(<div class="fv-margin-strip__window"[^>]*>)([\s\S]*?)(</div>)')
CSS = """
/* Isolated EX2 review candidate — preserves all source words; adds no script. */
.fv-margin-strip__inner{grid-template-columns:auto minmax(0,1fr) auto}
.fv-margin-strip__window{min-width:0}
.fv-margin-strip__ledger{min-width:0;align-self:center;max-width:min(700px,100%)}
.fv-margin-strip__ledger summary{color:#ddbd82;cursor:pointer;font:700 12px/1.4 system-ui,sans-serif;text-decoration:underline;text-underline-offset:4px;min-height:26px;display:list-item;padding:5px 7px}
.fv-margin-strip__ledger summary:focus-visible{outline:3px solid #f4efe6;outline-offset:3px}
.fv-margin-strip__ledger[open]{grid-column:1/-1;grid-row:2;max-width:100%}
.fv-margin-strip__ledger ol{margin:12px 0 4px;padding:14px 18px 14px 42px;background:#181b19;border:1px solid #6d614f;max-height:min(55vh,440px);overflow-y:auto;overscroll-behavior:contain}
.fv-margin-strip__ledger li{font:400 14px/1.55 system-ui,sans-serif;margin:0 0 11px;color:#f4efe6}
@media(max-width:900px){.fv-margin-strip__inner{grid-template-columns:minmax(0,1fr) auto;gap:6px 12px}.fv-margin-strip__label{grid-column:1;grid-row:1;align-self:center}.fv-margin-strip__window{grid-column:1/-1;grid-row:2}.fv-margin-strip__ledger{grid-column:2;grid-row:1}.fv-margin-strip__ledger[open]{grid-column:1/-1;grid-row:3}}
@media(prefers-reduced-motion:reduce){.fv-margin-strip__ledger summary{transition:none}}
"""

def read_page(doc):
    if not isinstance(doc, dict):
        raise ValueError('BAD_JSON_OBJECT')
    page = doc.get('structuredContent', doc)
    page = page.get('data', page)
    if page.get('id') != 6 or page.get('status') != 'publish':
        raise ValueError('NOT_PUBLISHED_PAGE6')
    raw = page.get('content')
    if isinstance(raw, dict):
        raw = raw.get('raw')
    if not isinstance(raw, str):
        raise ValueError('MISSING_RAW_EDITOR_CONTENT')
    return raw

def build(raw):
    if not raw.startswith('<!-- wp:html -->'):
        raise ValueError('MARGINS_BLOCK_NOT_FIRST')
    boundary = raw.find('<!-- /wp:html -->')
    if boundary < 0:
        raise ValueError('MISSING_FIRST_BLOCK_END')
    block = raw[:boundary]
    matches = list(SPAN.finditer(block))
    if [int(m.group(1)) for m in matches] != list(range(72)):
        raise ValueError('NOT_EXACTLY_72_ORDERED_RECORDS')
    texts = [html.unescape(m.group(2)) for m in matches]
    if any(not t.strip() or '<' in t or '>' in t for t in texts):
        raise ValueError('UNSAFE_OR_EMPTY_NOTE')
    if block.count('<div class="fv-margin-strip__window"') != 1 or 'fv-margin-strip__ledger' in block:
        raise ValueError('MARGIN_WINDOW_DRIFT_OR_ALREADY_PATCHED')
    m = WINDOW.search(block)
    if not m or len(SPAN.findall(m.group(2))) != 72:
        raise ValueError('WINDOW_NOT_UNIQUE_AND_COMPLETE')
    if 'tabindex="0"' not in m.group(1) or 'aria-live="off"' not in m.group(1):
        raise ValueError('CURRENT_WINDOW_SEMANTICS_CHANGED')
    if 'prefers-reduced-motion:reduce' not in block or 'nth-child(1){display:block}' not in block:
        raise ValueError('REDUCED_MOTION_BASELINE_CHANGED')
    ledger = ('\n<details class="fv-margin-strip__ledger">'
              '<summary>Read all 72 source notes</summary>\n<ol>\n' +
              '\n'.join('<li>' + html.escape(t, quote=False) + '</li>' for t in texts) +
              '\n</ol>\n</details>\n')
    head = (m.group(1).replace(' tabindex="0"', '')
            .replace(' aria-live="off"', '')
            .replace(' aria-label="Rotating source and accountability notes"', ' aria-hidden="true"'))
    changed = block[:m.start()] + head + m.group(2) + m.group(3) + ledger + block[m.end():]
    if changed.count('</style>') != 1:
        raise ValueError('BASELINE_CSS_BLOCK_DRIFT')
    changed = changed.replace('</style>', CSS + '\n</style>', 1)
    if changed.count('<li>') != 72 or len(SPAN.findall(changed)) != 72:
        raise ValueError('PRESERVATION_COUNT_MISMATCH')
    return changed, {
        'notes': 72, 'changed_block_only': True, 'rest_of_page_untouched': True,
        'new_js': False, 'source_text_sha256': __import__('hashlib').sha256(
            '\n'.join(texts).encode()).hexdigest(),
        'runtime_accessibility_approved': False, 'release_authorized': False
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('page6_readonly_json', type=Path)
    parser.add_argument('--preview', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    changed, receipt = build(read_page(json.loads(args.page6_readonly_json.read_text(encoding='utf-8'))))
    args.preview.write_text(changed, encoding='utf-8')
    args.receipt.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()

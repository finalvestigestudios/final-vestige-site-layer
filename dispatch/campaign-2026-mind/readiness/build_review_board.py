"""Build a static, no-JavaScript decision board; it cannot send anything."""
from __future__ import annotations
from html import escape
import json
from pathlib import Path
import importlib.util
_spec=importlib.util.spec_from_file_location("per_issue_preflight",Path(__file__).with_name("per_issue_preflight.py"))
_gate=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gate)
inspect_campaign=_gate.inspect_campaign


def render(manifest:dict, evidence:dict, ledger:dict)->str:
    report=inspect_campaign(manifest,evidence,ledger)
    cards=[]
    for entry, row in zip(manifest['issues'],report['editions']):
        number=entry['number']
        ref=next(x for x in ledger['entries'] if x['number']==number)
        commercial=number in (3,5)
        cls='commercial' if commercial else 'editorial'
        source=', '.join(ref['source_titles'])
        disclosure='Product recommendation review held. No approved affiliate link.' if commercial else 'Original evidence-led editorial. No affiliate offer.'
        missing_items=''.join(f'<li>{escape(x)}</li>' for x in row['missing_evidence'])
        cards.append(f'''<article class="card {cls}" aria-labelledby="issue-{number}"><div class="eyebrow">FILE {number:02d} / {'OFFER REVIEW' if commercial else 'EDITORIAL'}</div><h2 id="issue-{number}">{escape(entry['subject'])}</h2><p class="preheader">{escape(entry['preheader'])}</p><p class="disclosure">{escape(disclosure)}</p><dl><dt>Destination</dt><dd>{escape(ref['destination_status'])}</dd><dt>Source trail</dt><dd>{escape(source)}</dd><dt>Approval</dt><dd><strong class="status">HELD — NOT SENT</strong></dd></dl><details><summary>View unresolved checks ({len(row['missing_evidence'])})</summary><ul>{missing_items}</ul></details></article>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Dispatch — six-issue release review | Internal draft</title><meta name="robots" content="noindex,nofollow"><style>
:root{{color-scheme:dark;--bg:#090b0b;--panel:#141716;--gold:#d6b57c;--fg:#f4efe6;--muted:#d0cbc1;--line:#47433c;}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 system-ui,-apple-system,sans-serif}}a{{color:var(--gold)}}.skip{{position:absolute;left:-9999px;top:0;background:var(--fg);color:var(--bg);padding:10px}}.skip:focus{{left:10px}}:focus-visible{{outline:3px solid var(--gold);outline-offset:4px}}header,main,footer{{max-width:1260px;margin:auto;padding:clamp(24px,4vw,58px)}}header{{border-bottom:1px solid var(--line)}}h1{{font:normal clamp(40px,6vw,75px)/1.08 Georgia,serif;max-width:900px;letter-spacing:-.015em;margin:.3em 0}}.kicker,.eyebrow{{text-transform:uppercase;color:var(--gold);font-weight:700;letter-spacing:.16em;font-size:.76rem}}.intro{{max-width:780px;color:var(--muted);font-size:1.1rem}}.warning{{border:1px solid var(--gold);padding:14px 20px;background:#212019;max-width:780px}}.cards{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}}.card{{border:1px solid var(--line);padding:clamp(20px,2.5vw,34px);background:var(--panel);min-width:0}}h2{{font:normal clamp(27px,2.9vw,36px)/1.17 Georgia,serif;margin:13px 0 18px}}.preheader{{color:var(--muted);font-size:1.05rem}}.disclosure{{border-left:3px solid var(--gold);padding:7px 0 7px 15px;line-height:1.5}}dl{{margin-top:24px;display:grid;grid-template-columns:110px 1fr;gap:12px}}dt{{color:var(--muted);font-weight:600}}dd{{margin:0;overflow-wrap:anywhere}}.status{{color:#f2c5a9}}details{{margin-top:22px;border-top:1px solid var(--line);padding-top:14px}}summary{{cursor:pointer;color:var(--gold);font-weight:700;min-height:44px}}details ul{{padding-left:24px;font-size:.91rem;overflow-wrap:anywhere}}.commercial{{border-color:#79604a}}footer{{border-top:1px solid var(--line);color:var(--muted)}}@media(max-width:750px){{.cards{{grid-template-columns:1fr}}dl{{grid-template-columns:1fr;gap:3px}}dd{{margin-bottom:10px}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}
</style></head><body><a class="skip" href="#main">Skip to campaign review</a><header><div class="kicker">Final Vestige Studios · Internal editorial proof</div><h1>Six dispatches.<br>One standard of evidence.</h1><p class="intro">The six editions are drafted. Four are historical/editorial. Two evaluate optional Inspire3 offers. Their review status is independent, so one unapproved merchant does not automatically prevent an editorial-only review. This board is an offline editorial fixture, never a live Jetpack email.</p><p class="warning"><strong>Nothing below is cleared to send.</strong> Verified recipient eligibility, actual WordPress email preview, commercial footer, opt-out and founder authorization are still required. No product link has been activated.</p></header><main id="main"><div class="cards">{''.join(cards)}</div></main><footer>Source-linked internal review · Read-only · No JS · No trackers · No subscriber data · No merchant earning links</footer></body></html>'''


def main()->None:
    root=Path(__file__).resolve().parents[1]
    def read(path):return json.loads(path.read_text(encoding='utf-8'))
    content=render(read(root/'manifest.json'),read(root/'readiness'/'edition_attestations.json'),read(root/'readiness'/'canonical_cta_ledger.json'))
    target=root/'readiness'/'review_board.html'
    target.write_text(content,encoding='utf-8')
    print(f'Wrote static review board: {target}, {len(content)} bytes')

if __name__=='__main__':main()

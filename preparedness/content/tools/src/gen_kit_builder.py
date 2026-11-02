#!/usr/bin/env python3
"""Generate content/tools/kit-builder.body.html and .meta.json from kit_builder_items.py.
Run from the repo root:  python -I preparedness/content/tools/src/gen_kit_builder.py
"""
import html, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
sys.path.insert(0, str(HERE))
import kit_builder_items as D  # noqa: E402

E = lambda s: html.escape(s, quote=False)

# ---------- scenario chooser ----------
sc = '<fieldset class="pa-tool-set kb-scenarios"><legend>Which of these describe your household?</legend>\n<p class="pa-tool-note">Choose all that apply. The list below shows only the groups you choose. Nothing you choose is stored or sent anywhere.</p>\n'
for sid, label, default, helptext in D.SCENARIOS:
    chk = ' checked' if default else ''
    hint = f'<span class="pa-tool-note kb-hint" id="kb-sh-{sid}">{E(helptext)}</span>' if helptext else ''
    desc = f' aria-describedby="kb-sh-{sid}"' if helptext else ''
    sc += f'<label class="pa-tool-check" for="kb-s-{sid}"><input type="checkbox" id="kb-s-{sid}" data-scenario="{sid}"{chk}{desc}> <span>{E(label)}{(" " + hint) if hint else ""}</span></label>\n'
sc += '</fieldset>\n'

# ---------- groups ----------
gsrc = {}
groups_html = ''
all_src = []
for gid, title, intro, scenario in D.GROUPS:
    items = [i for i in D.ITEMS if i[1] == gid]
    if not items:
        continue
    attr = f' data-scenario-group="{scenario}"' if scenario else ' data-always="1"'
    groups_html += f'<section class="kb-group"{attr} data-group="{gid}" aria-labelledby="kb-h-{gid}">\n<h3 id="kb-h-{gid}">{E(title)}</h3>\n'
    if intro:
        groups_html += f'<p class="kb-intro">{E(intro)}</p>\n'
    groups_html += '<ul class="kb-list">\n'
    for iid, _, label, why, srcs in items:
        cites = ''.join('{{cite:%s}}' % s for s in srcs)
        for s in srcs:
            if s not in all_src:
                all_src.append(s)
        groups_html += (f'<li class="kb-item"><label class="kb-label" for="kb-i-{iid}"><input type="checkbox" id="kb-i-{iid}" data-kb-item="{iid}" data-group="{gid}"> '
                        f'<span class="kb-text">{E(label)}</span></label>\n'
                        f'<p class="kb-why"><span class="kb-whylabel">Why it matters.</span> {E(why)}{cites}</p></li>\n')
    groups_html += '</ul>\n</section>\n'

css = '''<style>
.pa .kb-scenarios label{margin:0 0 8px}
.pa .kb-hint{display:block;margin:0}
.pa .kb-group{margin:0 0 26px}
.pa .kb-group[hidden]{display:none}
.pa .kb-group h3{margin:0 0 6px;font-size:20px}
.pa .kb-intro{margin:0 0 10px;color:var(--pa-muted);font-size:15px}
.pa .kb-list{margin:0;padding:0;list-style:none}
.pa .kb-item{margin:0 0 12px;padding:12px 14px;border:1px solid var(--pa-line);background:var(--pa-surface)}
.pa .kb-label{display:flex;gap:10px;align-items:flex-start;font-weight:600;color:var(--pa-text);cursor:pointer}
.pa .kb-label input{width:22px;height:22px;margin-top:2px;flex:none;accent-color:var(--pa-gold)}
.pa .kb-why{margin:6px 0 0 32px;font-size:15px;color:var(--pa-muted)}
.pa .kb-whylabel{color:var(--pa-gold);font-weight:600}
.pa .kb-bar{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 14px}
.pa .kb-btn{min-height:44px;padding:8px 16px;font:inherit;font-size:15px;font-weight:600;color:var(--pa-text);background:var(--pa-surface-2);border:1px solid var(--pa-gold-dim);border-radius:0;cursor:pointer}
.pa .kb-btn--main{background:var(--pa-gold);color:#101111;border-color:var(--pa-gold)}
.pa .kb-btn:focus-visible{outline:3px solid var(--pa-gold);outline-offset:3px}
.pa .kb-summary{margin:0 0 12px;font-weight:600;color:var(--pa-ok)}
.pa .kb-nojs{display:none}
html:not([data-kb-js]) .pa .kb-nojs{display:block}
.pa .kb-print-head{display:none}
@media (prefers-reduced-motion:reduce){.pa .kb-btn{transition:none}}
@media print{
 body[data-kb-print] .pa-head,body[data-kb-print] .pa-toc,body[data-kb-print] .pa-crumbs,body[data-kb-print] .pa-sources,body[data-kb-print] .pa-review,body[data-kb-print] .pa-related,body[data-kb-print] .pa-printbar,body[data-kb-print] .pa-skip,body[data-kb-print] .kb-screen{display:none!important}
 body[data-kb-print] .pa,body[data-kb-print] .pa-body{background:#fff!important;color:#000!important;max-width:none}
 body[data-kb-print] .kb-print-head{display:block}
 body[data-kb-print] .kb-item{break-inside:avoid;border:0;border-bottom:1px solid #999;background:#fff;padding:4pt 0;margin:0}
 body[data-kb-print] .kb-item *,body[data-kb-print] .kb-print-head *{color:#000!important;background:#fff}
 body[data-kb-print] .kb-why{font-size:9pt;margin-left:26px}
 body[data-kb-print] .kb-label input{width:12pt;height:12pt}
 body[data-kb-print] .kb-group h3{break-after:avoid;color:#000}
}
</style>'''

body = f'''<section class="pa-act kb-screen" aria-labelledby="act-h">
<h2 id="act-h">What this does</h2>
<ol>
<li><strong>Choose what describes your household.</strong> You see only the groups that apply.</li>
<li><strong>Tick what you already have.</strong> Each item says why it is on the list and which official source it comes from.</li>
<li><strong>Print the checklist or save it as a text file,</strong> then work through what is left, starting with water.</li>
</ol>
<p class="pa-act-note"><strong>Private by design.</strong> Your choices and ticks stay in this page, in memory. They are not sent anywhere or saved in cookies, browser storage or the address bar, and reloading the page clears them. The planner never asks which medicine or device anyone uses.</p>
</section>

<div class="kb-screen">
<ul class="pa-key" aria-label="About this tool">
<li><span class="pa-tag pa-tag--fact">Official guidance</span> Items come from the Ready.gov, FEMA and CDC lists cited beside them.</li>
<li><span class="pa-tag pa-tag--ed">Editor's note</span> Where a reason is our own reasoning, it begins with "Editor's note."</li>
</ul>
<p>This is a starting list, not a prescription. Ready.gov's own checklist calls its list only a starting point and asks you to consider your family's needs.{{{{cite:start-ready-supply-list}}}} The planner gives no quantities except the CDC and Ready.gov water baseline, and a completed checklist does not mean your household is ready for any event. If anyone is in danger, call 911 or your local emergency number.</p>
<p class="kb-nojs pa-tool-note">JavaScript is off, so every group is shown. Skip the groups that do not apply and use your browser's Print command to print the list.</p>

<h2 id="kb-plan">Choose your household</h2>
<div id="kb-app" class="pa-tool">
{sc}
<h2 id="kb-list-h">Your checklist</h2>
<p id="kb-summary" class="kb-summary" role="status" aria-live="polite"></p>
<div class="kb-bar" role="group" aria-label="Print, download or reset">
<button type="button" class="kb-btn kb-btn--main" data-kb-action="print">Print the checklist</button>
<button type="button" class="kb-btn" data-kb-action="download">Download as a text file</button>
<button type="button" class="kb-btn" data-kb-action="reset">Reset choices and ticks</button>
</div>
</div>
</div>

<div id="kb-checklist" class="kb-checklist">
<div class="kb-print-head"><h2>Emergency kit and go-bag checklist</h2><p>Prepared with the Final Vestige Preparedness Archive. A starting list: customize it to your household.</p></div>
{groups_html}
</div>

<div class="kb-screen">
<h2 id="kb-where">Where the items come from</h2>
<p>Each item cites the page it comes from. The full guides explain the reasoning and where the sources disagree: {{{{link:three-day-kit|the three-day kit}}}}, {{{{link:go-bags|go-bags}}}} and {{{{link:preparedness-real-households|preparedness for real households}}}}. To organize contacts, meeting places and practice dates, use the {{{{link:reunification-plan|household emergency plan builder}}}}.</p>
<h2 id="kb-limits">What this tool has and has not done</h2>
<p>It lists items from official kit lists and shows or hides them according to your choices. It does not know your hazards, your health, your building or your budget, and it cannot check what you have packed. Where the official sources disagree (how many days of medicine to keep, how often to review a kit, which mask suits which hazard) the items say to ask a professional or local officials instead of choosing a number. Nothing here is medical advice, and no item should be used to change how anyone takes a medicine. There are no product recommendations and no affiliate links. This tool is a draft awaiting human safety review.</p>
</div>
{css}
<script>
{{{{inline-js:kit_planner.js}}}}
{{{{inline-js:kit_planner_ui.js}}}}
</script>
'''
(OUT / 'kit-builder.body.html').write_text(body, encoding='utf-8', newline="\n")

source_use = {
    "start-ready-supply-list": "The checklist is only a starting point, and one full kit at home plus smaller portable kits elsewhere.",
}
meta = {
    "kind": "tool", "n": 103, "slug": "kit-builder",
    "title": "Emergency kit and go-bag planner",
    "h1": "Emergency kit and go-bag planner",
    "dek": "Choose what describes your household, tick what you already have, and print a checklist that shows why each item is there and where it comes from. It runs in your browser and keeps nothing.",
    "description": "A free, private checklist for emergency kits and go-bags: adults, children, infants, pets, mobility, powered equipment, limited storage and budget, with sources.",
    "section": "field-tools", "track": "modern",
    "tags": ["Checklist", "Printable", "Runs locally"],
    "updated": "2026-11-01", "last_checked": "2026-11-01",
    "recheck": "If Ready.gov, FEMA or the CDC revise their kit, infant, pet or disability pages, or at the next quarterly source sweep.",
    "status": {"editorial": "drafted", "publish": "draft"},
    "safety_review": {"state": "pending", "reviewer": None, "date": None},
    "related": ["three-day-kit", "go-bags", "household-emergency-plan", "preparedness-real-households", "water-planner"],
    "source_use": source_use,
}
for s in all_src:
    meta["source_use"].setdefault(s, "Items and reasons in the checklist that cite this source.")
(OUT / 'kit-builder.meta.json').write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8', newline="\n")
print('items', len(D.ITEMS), 'sources', len(all_src), 'body chars', len(body))

#!/usr/bin/env python3
"""Browser-only exact-published-exit excerpt, not full WordPress or actual hosted QA."""
import importlib.util
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('bridge', ROOT/'tools/experience-2/review_collection_bridge.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
OUTPUT = Path(os.getenv('FV_EX2_EVIDENCE_DIR', '/tmp/fv-ex2-bridge-evidence'))
OUTPUT.mkdir(parents=True, exist_ok=True)

BASE = '''<style>
*{box-sizing:border-box}
html,body{margin:0;background:#090a0a;color:#f6ebda;font:14px/1.5 system-ui,sans-serif}
.fv-hf{--hf-bg:#0a0a09;--hf-muted:#c3b49f;--hf-ink:#f6ebda;--hf-gold:#d4ad73;--hf-line:#4d4330;--hf-sans:Inter,ui-sans-serif,system-ui,sans-serif;--hf-mono:"Courier New",ui-monospace,monospace}
.fv-hf__exit{display:grid;grid-template-columns:1fr repeat(4,auto);align-items:center;gap:25px;padding:33px clamp(22px,7vw,125px);background:#151310;border-bottom:1px solid var(--hf-line)}
.fv-hf__exit p{font:700 10px/1.4 var(--hf-mono);letter-spacing:.08em;color:var(--hf-gold)}
.fv-hf__exit a{font-size:12px;font-weight:700;text-decoration:none;color:var(--hf-ink)}.fv-hf__exit a:hover{color:var(--hf-gold)}
@media(max-width:920px){.fv-hf__exit{grid-template-columns:repeat(2,minmax(0,1fr))}.fv-hf__exit p{grid-column:1/-1}}
@media(max-width:600px){.fv-hf__exit{gap:20px}}
</style>'''


def render(candidate):
    panel = mod.EXIT.replace('      </section>', mod.BRIDGE+'\n      </section>') if candidate else mod.EXIT
    return ('<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Source excerpt / offline QA</title>'+BASE+'<main class="fv-hf">'
            '<h1 style="font:28px Georgia;padding:30px 22px;margin:0">Review of the published archive exit</h1>'
            +panel+'</main>'+(mod.STYLE if candidate else '')+'</html>')


def main():
    rows=[]
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path=os.getenv('FV_CHROMIUM', '/usr/bin/chromium'), headless=True, args=['--no-sandbox'])
        for width in (320,360,390,768,1440,1920):
            for reduced in (False,True):
                for candidate in (False,True):
                    page=b.new_page(viewport={'width':width,'height':840}, java_script_enabled=False,
                                    reduced_motion='reduce' if reduced else 'no-preference')
                    page.set_content(render(candidate))
                    sizes=page.locator('html').evaluate('e=>({scroll:e.scrollWidth,client:e.clientWidth})')
                    found=page.locator('a[href="/mini-museum-history-collectibles/"]')
                    count=found.count()
                    bounds=found.bounding_box() if count else None
                    focused='NOT_APPLICABLE'
                    if count:
                        found.focus()
                        focused=found.evaluate('e=>document.activeElement===e')
                    passed=(sizes['scroll'] <= sizes['client']+1 and
                            (count == 1 if candidate else count == 0) and
                            (bool(focused) if candidate else True) and
                            (bounds['height'] >= 44 if candidate else True))
                    rows.append({'width':width,'reduced_motion':reduced,'candidate':candidate,'no_js':True,
                                 'bounds':bounds,'overflow':sizes,'keyboard_focus':focused,'pass':passed})
                    if width in (320,390,1440) and not reduced:
                        page.screenshot(path=str(OUTPUT/f'{"candidate" if candidate else "before"}_{width}.png'),full_page=True)
                    page.close()
        x=b.new_page(viewport={'width':390,'height':840},java_script_enabled=False)
        x.set_content(render(True))
        x.evaluate('document.documentElement.style.zoom="200%"')
        z=x.evaluate('({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})')
        rows.append({'width':390,'zoom':'CSS 200% simulation, NOT genuine browser zoom','overflow':z,
                     'pass':z['scroll']<=z['client']+1})
        x.screenshot(path=str(OUTPUT/'candidate_390_csszoom200.png'),full_page=True)
        x.close();b.close()
    result={'status':'PASS' if all(x['pass'] for x in rows) else 'FAIL',
            'scenarios':len(rows),'pass_count':sum(x['pass'] for x in rows),
            'scope':'Published source excerpt only; NOT live WordPress/Assembler',
            'actual_image_bytes':'NOT TESTED','hosted_lighthouse':'NOT TESTED',
            'real_jetpack':'NOT TESTED','wcag_22_aa':'NOT CERTIFIED','rows':rows}
    (OUTPUT/'chromium_review.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
    if result['status']!='PASS':raise SystemExit(1)


if __name__=='__main__':main()

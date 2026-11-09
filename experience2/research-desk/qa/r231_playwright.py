#!/usr/bin/env python3
"""R231: exact checked-out NASA Research Desk template + CSS + JS browser QA.
Requires a local clone of PR R231; never hits production, checkout or merchant.
Run: python experience2/research-desk/qa/r231_playwright.py --repo . --out /tmp/r231-qa
Optionally --axe-js /path/to/axe.min.js (real axe, not custom approximation).
"""
import argparse, hashlib, json, re, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS = (320, 390, 768, 1440, 1920)
CTA = "https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"
ROOT = "experience2/research-desk"

def checksum(data):
    if isinstance(data, Path): data=data.read_bytes()
    if isinstance(data, str): data=data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def php_case(repo, case):
    proc = subprocess.run(["php", str(repo/ROOT/"qa/r231_smoke.php"), case],
                          capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)

def verify_dom(page, js):
    return page.evaluate("""(js) => {
      const roots=[...document.querySelectorAll('[data-fvx-ledger]')];
      const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
      const refs=[...document.querySelectorAll('[aria-controls],[aria-labelledby],[for]')];
      const anchors=[...document.querySelectorAll('a[href]')];
      const idsOK=refs.every(el=>['aria-controls','aria-labelledby','for'].every(k=>{
        const val=el.getAttribute(k);
        return !val||val.split(/\\s+/).every(id=>!!document.getElementById(id));
      }));
      return {roots:roots.length, records:document.querySelectorAll('[data-fvx-record]').length,
        sourceScope:document.querySelectorAll('[data-fvx-source-scope]').length,
        duplicates:ids.length-new Set(ids).size, referencesOK:idsOK,
        overflowPx:document.documentElement.scrollWidth-document.documentElement.clientWidth,
        originalCtas:anchors.filter(a=>a.href==='"""+CTA+"""').length,
        hiddenRecords:[...document.querySelectorAll('[data-fvx-record]')].filter(e=>e.hidden).length,
        visibleSearch:document.querySelectorAll('[data-fvx-tools]:not([hidden])').length,
        fakePins:document.querySelectorAll('[data-lat],[data-lng],[data-longitude]').length};
    }""",js)

def run(repo, out, axe_path=None):
    repo=Path(repo).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    asset=repo/ROOT/"assets";style=(asset/"source-ledger-r231.css").read_text()
    script=(asset/"source-ledger-r231.js").read_text()
    results={k:php_case(repo,k) for k in ("normal","duplicate","tampered")}
    assert all(x["status"]=="PASS" for x in results.values())
    body=re.sub(r'<link rel="stylesheet"[^>]+>',"",results["normal"]["first"])
    html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+body+'</body></html>'
    hashes={};checks=[];network=[];axe_results=[]
    with sync_playwright() as p:
      browser=p.chromium.launch(headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox"])
      version=browser.version
      for width in WIDTHS:
        for js in (False,True):
          context=browser.new_context(viewport={"width":width,"height":840},
                 java_script_enabled=js, is_mobile=(width<=390),has_touch=(width<=390),
                 reduced_motion="reduce" if width==320 else "no-preference",
                 forced_colors="active" if width==768 else "none")
          page=context.new_page(); seen=[]
          page.on("request",lambda req:seen.append(req.url))
          page.set_content(html)
          page.add_style_tag(content=style)
          if js:page.add_script_tag(content=script)
          d=verify_dom(page,js)
          assert d["roots"]==1 and d["records"]==6 and d["sourceScope"]==3,d
          assert d["originalCtas"]==1 and d["duplicates"]==0 and d["referencesOK"],d
          assert d["fakePins"]==0 and d["overflowPx"]<=1,d
          assert not seen,seen
          if js:
            search=page.locator("input[data-fvx-search]")
            assert search.is_visible()
            search.fill("altitude-chamber")
            assert page.locator("[data-fvx-record]:visible").count()==1,"search failed to index new context"
            assert page.locator("[data-fvx-status]").inner_text()=="1 of 6 evidence records"
            search.fill("")
          else:
            assert d["visibleSearch"]==0 and d["hiddenRecords"]==0
          summary=page.locator("details > summary").first
          if width<=390:summary.tap()
          else:
            summary.focus();page.keyboard.press("Enter")
          assert summary.evaluate("(e)=>e.parentElement.open")
          if js and axe_path:
            page.add_script_tag(path=str(axe_path))
            issues=page.evaluate("""async()=>{const r=await axe.run(document,
               {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
               return r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}));}""")
            axe_results.append({"width":width,"violations":issues})
            assert not issues,issues
          filename=f"{width}-{'js' if js else 'nojs'}.png"
          shot=out/filename;page.screenshot(path=str(shot),full_page=True,animations="disabled")
          hashes[filename]=checksum(shot)
          checks.append({"width":width,"javascript":js,**d,"screenshot_sha256":hashes[filename]})
          context.close()
      browser.close()
    proof={"status":"PASS_LOCAL_EXACT_COMPONENT","source_git_blob":results["normal"]["template_git_blob"],
      "scope":"exact R231 HTML + inherited R158 CSS + R231 optional JS; local browser set_content, NOT installed WordPress",
      "chromium":version,"php_cases":["normal","duplicate","tampered"],"contexts":checks,
      "screenshot_sha256":hashes,"axe":("ACTUAL_AXE_EXECUTED" if axe_path else "NOT_EXECUTED"),
      "axe_results":axe_results,"http_navigation":"NOT_TESTED","screenreader":"NOT_TESTED",
      "LCP_CLS":"NOT_MEASURED_NOT_FIELD","external_requests":len(network),"release":"STAGING_HOLD"}
    (out/"receipt.json").write_text(json.dumps(proof,sort_keys=True,indent=2)+"\n")
    print("PASS: 3 PHP cases; 10 real Chromium contexts; receipt:",checksum(out/"receipt.json"))
    return proof

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--axe-js",type=Path)
    a=ap.parse_args();run(a.repo,a.out,a.axe_js)

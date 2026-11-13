#!/usr/bin/env python3
"""Actual Chromium print/source-custody release gate; offline fixture only."""
import json
import os
import re
import subprocess
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.getenv("FV_R344_OUT","/tmp/fv-apollo-r344"))
OUT.mkdir(parents=True,exist_ok=True)
PHP=ROOT/"apollo-r339/chronology-rail.php"
CSS=(ROOT/"apollo-r339/assets/chronology-rail.css").read_text()
html=subprocess.run(["php","-r","define('ABSPATH',true);require '"+str(PHP)+"';echo fv_apollo_r339_shortcode();"],check=True,text=True,capture_output=True).stdout
assert html.count('class="fv-apollo-r339__print-source" hidden')==6
assert html.count('data-fv-r339-source=')==6
assert html.count('data-fv-r339-cta="editorial"')==1
assert not any(t in html for t in ["data-geo-pin","<img","data-affiliate","utm_campaign","utm_content"])
assert re.search(r"@media print\s*\{",CSS)
assert ".fv-apollo-r339__print-source[hidden]{display:block!important}" in CSS
cases=[(320,16,True,False,False,False),(390,16,True,True,False,False),
       (768,16,True,False,True,False),(1440,16,True,False,False,False),
       (1920,16,True,False,False,False),(320,64,True,False,False,False),
       (320,32,False,False,False,False),(390,16,False,False,False,False),
       (1440,16,False,False,False,False),(768,16,True,False,False,True)]
screen=[]
pdfs=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=os.getenv("CHROMIUM","/usr/bin/chromium"),args=["--no-sandbox"])
 for width,font,js,touch,reduced,forced in cases:
  ctx=b.new_context(viewport={"width":width,"height":950},java_script_enabled=js,
                    has_touch=touch,is_mobile=touch,reduced_motion="reduce" if reduced else "no-preference",
                    forced_colors="active" if forced else "none")
  page=ctx.new_page()
  page.set_content('<html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>html{font-size:'+str(font)+'px}'+CSS+'</style></head><body>'+html+'</body></html>')
  assert page.locator(".fv-apollo-r339__event").count()==6
  assert page.locator(".fv-apollo-r339__print-source:visible").count()==0
  assert page.locator("[data-fv-r339-source]").count()==6
  assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
  source=page.locator(".fv-apollo-r339__source").first
  source.locator("summary").focus();page.keyboard.press("Enter")
  assert source.evaluate("(e)=>e.open")
  assert page.locator("[data-fv-r339-source]").first.is_visible()
  page.keyboard.press("Space");assert not source.evaluate("(e)=>e.open")
  if (width,font,js) in [(320,64,True),(1440,16,True)]:
   page.screenshot(path=str(OUT/f"r344-screen-{width}-{font}.png"),full_page=True)
  screen.append({"width":width,"font":font,"js":js,"result":"PASS"})
  ctx.close()
 def print_pdf(code,styles,width=390,js=True):
  page=b.new_page(viewport={"width":width,"height":900},java_script_enabled=js)
  page.set_content('<html lang="en"><head><style>'+styles+'</style></head><body>'+code+'</body></html>')
  raw=page.pdf(format="A4",print_background=True)
  page.close()
  doc=fitz.open(stream=raw,filetype="pdf")
  text="\n".join(x.get_text(sort=True) for x in doc)
  urls=[l.get("uri","") for x in doc for l in x.get_links() if l.get("kind")==2]
  return raw,doc,text,urls
 for width,js in [(320,False),(390,True),(1440,True)]:
  # A4 print geometry is deliberately fixed; viewport/JS variants must agree on source custody.
  raw,doc,text,urls=print_pdf(html,CSS,width,js)
  assert text.count("Evidence limit:")==6
  assert text.count("Record custody:")==6
  assert text.count("Primary source:")==5
  assert text.count("Later institutional source:")==1
  assert text.count("Read the complete Apollo 1 investigation")==1
  assert sum(u.startswith("https://www.nasa.gov/") for u in urls)>=6
  assert any(u=="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/" for u in urls)
  assert not any(("utm_" in u or "payhip" in u or "affiliate" in u) for u in urls)
  assert len(doc)<=8
  if width==390:
   (OUT/"r344-print-390.pdf").write_bytes(raw)
   doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(OUT/"r344-print-page1.png"))
   doc[-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(OUT/"r344-print-last.png"))
  pdfs.append({"width":width,"js":js,"pages":len(doc),"evidence_limits":6,"source_custody":6,"result":"PASS"})
  doc.close()
 # Two actual browser-negative controls: suppress one print record, suppress print unhide CSS.
 mutant=html.replace('class="fv-apollo-r339__print-source" hidden','class="fv-apollo-r339__print-source" hidden data-r344-suppressed',1)
 # A visible mutation only changes attributes, so instead remove the first print sibling entirely.
 mutant=re.sub(r'<div class="fv-apollo-r339__print-source" hidden>.*?</div>',"",html,count=1,flags=re.S)
 _,d,t,_=print_pdf(mutant,CSS);assert t.count("Evidence limit:")!=6;d.close()
 _,d,t,_=print_pdf(html,CSS.replace(".fv-apollo-r339__print-source[hidden]{display:block!important}",""))
 assert t.count("Evidence limit:")!=6;d.close()
 b.close()
result={"status":"PASS","real_chromium_screen_cases":len(screen),"native_print_pdf_cases":len(pdfs),
        "browser_negative_controls":2,"axe_core":"NOT_EXECUTED","installed_wordpress":"NOT_EXECUTED",
        "production_lcp_cls":"NOT_MEASURED","screen":screen,"pdf":pdfs}
(OUT/"r344-gate.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({k:v for k,v in result.items() if k not in ("screen","pdf")}))

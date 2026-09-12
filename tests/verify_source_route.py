from __future__ import annotations
import hashlib, os, re, shutil, subprocess, tempfile, threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PAYLOAD=ROOT/"payloads"/"source-route-wp-block-v1.txt"
EXPECTED_BYTES=15089
EXPECTED_SHA256="8ba39dbca28b99c8c555923cc0b8e42729fe80106efba624de87dea269cf6d3c"

def req(ok,msg):
    if not ok: raise SystemExit(f"FAIL: {msg}")

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass

def cite(s,i,n,wrapped=False):
    a=f'<a href="#fv-fn-{n}" class="fv-fn-ref" data-fv-fn="{n}" id="ref-{s}-{i}">{n}</a>'
    return f'<sup class="fv-fn-mark">{a}</sup>' if wrapped else a

def para(s,i,n=None,wrapped=False):
    c="" if n is None else cite(s,i,n,wrapped)
    return f'<p id="p-{s}-{i}">{s} narrative paragraph {i} carries enough published wording to establish a stable story context for Source Route. {c}</p>'

def sources(attrs=""):
    rows="".join(f'<li id="fv-fn-{i}"{attrs if i==2 else ""}>Published source note {i} with archive context <a href="https://example.org/{i}">Open source</a><span class="fv-fn-backlinks"><a href="#ref-opening-1">↩</a></span></li>' for i in range(1,8))
    return '<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2><ul class="fv-source-list" data-fv-footnotes>'+rows+'</ul>'

def article(wrapped=False,attrs=""):
    return f"""<main><article><h1>Six Miles an Hour</h1>
{para("opening",1,1,wrapped)}{para("opening",2)}{para("opening",3,3,wrapped)}
<h2>The curve under Malbone Street</h2>{para("curve",1,1,wrapped)}{para("curve",2,3,wrapped)}{para("curve",3,1,wrapped)}
<h2>Why the wooden cars made the wreck worse</h2>{para("cars",1,5,wrapped)}{para("cars",2,3,wrapped)}{para("cars",3,1,wrapped)}
<h2>The switch upstairs</h2>{para("switch",1,2,wrapped)}{para("switch",2)}{para("switch",3,2,wrapped)}{sources(attrs)}</article></main>"""

INVALID={"mixed-id","mixed-class","partial","duplicate-exact","reversed","duplicate-root","missing-note","few-cites"}

def page(payload,mode):
    a=article(mode=="wrapped",' tabindex="-7" class="publisher-state fvsr-flash"' if mode=="preowned" else "")
    if mode=="mixed-id": a=a.replace('<h2 class="wp-block-heading fv-source-heading" id="sources">','<h2 id="sources">False marker</h2><h2 class="wp-block-heading fv-source-heading" id="sources">',1)
    elif mode=="mixed-class": a=a.replace('<h2 class="wp-block-heading fv-source-heading" id="sources">','<h2 class="fv-source-heading">False marker</h2><h2 class="wp-block-heading fv-source-heading" id="sources">',1)
    elif mode=="partial": a=a.replace('class="wp-block-heading fv-source-heading" id="sources"','class="wp-block-heading" id="sources"',1)
    elif mode=="duplicate-exact": a=a.replace('<h2 class="wp-block-heading fv-source-heading" id="sources">','<h2 class="wp-block-heading fv-source-heading" id="sources">Sources A</h2><h2 class="wp-block-heading fv-source-heading" id="sources">',1)
    elif mode=="reversed":
        b=sources(); h='<h2 class="wp-block-heading fv-source-heading" id="sources">Sources &amp; Further Reading</h2>'; notes=b.split("</h2>",1)[1]
        a=article().replace(b,h).replace("<h1>Six Miles an Hour</h1>","<h1>Six Miles an Hour</h1>"+notes,1)
    elif mode=="duplicate-root": a=a.replace(sources(),sources()+'<ul data-fv-footnotes><li id="fv-fn-30">Duplicate</li></ul>')
    elif mode=="missing-note": a=a.replace('href="#fv-fn-3" class="fv-fn-ref" data-fv-fn="3"','href="#fv-fn-30" class="fv-fn-ref" data-fv-fn="30"',1)
    elif mode=="few-cites": a=re.sub(r'<a href="#fv-fn-\d+" class="fv-fn-ref" data-fv-fn="\d+" id="[^"]+">\d+</a>',"",a,count=7)
    elif mode not in {"bare","wrapped","preowned","scroll-fail","focus-fail"}: raise ValueError(mode)
    js=r"""
<script>
const report=(ok,msg='')=>parent.postMessage({mode:MODE,ok,msg},location.origin);
const later=(fn,ms=80)=>setTimeout(()=>{try{fn()}catch(e){report(false,e.message||String(e))}},ms);
const run=()=>{
 try{
  const band=document.querySelector('[data-fvsr-band]');
  if(INVALID.includes(MODE)) return report(!band,band?'invalid fixture activated':'');
  if(!band)return report(false,'launcher missing');
  if(!band.textContent.includes('10 published citations')||!band.textContent.includes('4 cited sources'))return report(false,'counts wrong');
  const launch=band.querySelector('.fvsr-button'),src=document.getElementById('fv-fn-2');
  const cls=src.getAttribute('class'),tab=src.getAttribute('tabindex');
  if(MODE==='scroll-fail')src.scrollIntoView=()=>{throw Error('forced')};
  if(MODE==='focus-fail')src.focus=()=>{};
  launch.click();later(()=>{
   const d=document.querySelector('.fvsr-dialog');if(!d||!d.open)return report(false,'dialog missing');
   if(!d.textContent.includes('does not rate evidence'))return report(false,'disclosure missing');
   if(d.querySelector('.fvsr-context p').textContent.trim().endsWith('1'))return report(false,'citation leaked');
   d.querySelector('[data-mode="first"]').click();d.dispatchEvent(new KeyboardEvent('keydown',{key:'End',bubbles:true}));
   if(!d.querySelector('.fvsr-status').textContent.includes('Citation 4 of 4 · Source 2'))return report(false,'keyboard transport failed');
   d.querySelector('[data-jump="source"]').click();later(()=>{
    if(d.open)return report(false,'dialog stayed open');
    if(MODE==='scroll-fail'||MODE==='focus-fail'){
      if(src.getAttribute('class')!==cls||src.getAttribute('tabindex')!==tab)return report(false,'failure mutated publisher state');
      return report(document.activeElement===launch,'failure focus recovery');
    }
    if(document.activeElement!==src)return report(false,'story focus missing');
    if(MODE==='preowned'){
      if(src.getAttribute('tabindex')!=='-7'||src.getAttribute('class')!=='publisher-state fvsr-flash')return report(false,'preowned state changed');
    }else if(src.getAttribute('tabindex')!=='-1'||!src.classList.contains('fvsr-flash'))return report(false,'temporary state missing');
    launch.focus();later(()=>{
      if(src.getAttribute('class')!==cls||src.getAttribute('tabindex')!==tab)return report(false,'blur restore failed');
      launch.click();later(()=>{d.querySelector('[data-mode="first"]').click();d.dispatchEvent(new KeyboardEvent('keydown',{key:'End',bubbles:true}));d.querySelector('[data-jump="source"]').click();later(()=>{launch.focus();later(()=>{
        if(src.getAttribute('class')!==cls||src.getAttribute('tabindex')!==tab)return report(false,'repeat drift');
        launch.click();later(()=>{d.querySelector('.fvsr-close').click();later(()=>report(document.activeElement===launch,'close focus return'))})
      })})})
    })
   },150)
  })
 }catch(e){report(false,e.message||String(e))}
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run();
</script>"""
    js=js.replace("MODE",repr(mode)).replace("INVALID",repr(sorted(INVALID)))
    return "<!doctype html><html><body>"+a+payload+js+"</body></html>"

def browser(payload):
    chrome=next((shutil.which(x) for x in ("google-chrome","chromium","chromium-browser") if shutil.which(x)),None);req(chrome,"Chrome/Chromium unavailable")
    modes=("bare","wrapped","preowned","scroll-fail","focus-fail","mixed-id","mixed-class","partial","duplicate-exact","reversed","duplicate-root","missing-note","few-cites")
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        for m in modes:(root/f"{m}.html").write_text(page(payload,m),encoding="utf-8")
        frames="".join(f'<iframe src="/{m}.html"></iframe>' for m in modes)
        runner=f"""<!doctype html><body>{frames}<script>
const need=new Set({list(modes)!r}),fails=[];
addEventListener('message',e=>{{if(e.origin!==location.origin||!e.data||!need.has(e.data.mode))return;if(!e.data.ok)fails.push(e.data.mode+': '+e.data.msg);need.delete(e.data.mode);if(!need.size){{document.body.dataset.fvTest=fails.length?'fail':'pass';document.body.dataset.fvReason=fails.join(' | ')}}}});
</script></body>"""
        (root/"runner.html").write_text(runner,encoding="utf-8")
        server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(root)));t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
        try:
            proc=subprocess.run([chrome,"--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage","--window-size=360,800","--virtual-time-budget=9000","--dump-dom",f"http://127.0.0.1:{server.server_port}/runner.html"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=35)
            req(proc.returncode==0,f"browser failed: {proc.stderr[-500:]}")
            if 'data-fv-test="pass"' not in proc.stdout:
                m=re.search(r'data-fv-reason="([^"]*)"',proc.stdout);raise SystemExit("FAIL: browser: "+(m.group(1) if m else "fixtures incomplete"))
        finally:
            server.shutdown();server.server_close();t.join(timeout=3)

def main():
    raw=PAYLOAD.read_bytes();text=raw.decode();req(len(raw)==EXPECTED_BYTES,f"bytes drifted: {len(raw)}");req(hashlib.sha256(raw).hexdigest()==EXPECTED_SHA256,"SHA drifted")
    checks=(
      (text.count("<!-- wp:html -->")==1 and text.count("<!-- /wp:html -->")==1,"one WP block"),
      ("querySelectorAll('#sources,.fv-source-heading')" in text and "boundaryCandidates.length!==1" in text,"Sources ambiguity gate"),
      ("querySelectorAll('.fv-fn-ref[data-fv-fn]')" in text and "sup.fv-fn-mark" not in text,"live citation contract"),
      ("clone.querySelectorAll('.fv-fn-ref,.fv-fn-backlinks,script,style')" in text,"citation cleaning"),
      ("hadTabindex" in text and "priorTabindex" in text and "ownsTabindex" in text,"tabindex ownership"),
      ("hadClassAttr" in text and "hadFlash" in text and "ownsFlash" in text,"class ownership"),
      ("if(!hadClassAttr&&!el.getAttribute('class'))el.removeAttribute('class')" in text,"absent class restoration"),
      ("document.activeElement!==el" in text and "activeJumpCleanup" in text and "el.addEventListener('blur'" in text,"focus/repeat cleanup"),
      ("try{el.scrollIntoView" in text and "recoverFocus();return false" in text,"failure atomicity"),
      ("min-height:44px" in text and "@media(max-width:680px)" in text and "@media(max-width:360px)" in text,"responsive targets"),
      ("prefers-reduced-motion:reduce" in text and "forced-colors:active" in text and "@media print" in text,"accessible media"),
      ("This follows existing source links; it does not rate evidence or claim a source proves the passage." in text,"evidence disclosure"),
    )
    for ok,msg in checks:req(ok,msg)
    for token in ("fetch(","XMLHttpRequest","sendBeacon","WebSocket","localStorage","sessionStorage","indexedDB","document.cookie","posthog","gtag(","<iframe","<script src=","navigator.clipboard","history.pushState","history.replaceState"):req(token.lower() not in text.lower(),"forbidden token "+token)
    m=re.search(r'<script id="fv-source-route-v1-js">\n(.*?)\n</script>',text,re.S);req(m is not None,"JS extraction")
    with tempfile.NamedTemporaryFile("w",suffix=".js",delete=False) as h:h.write(m.group(1));p=Path(h.name)
    try:subprocess.run(["node","--check",str(p)],check=True)
    finally:p.unlink(missing_ok=True)
    if os.environ.get("FV_BROWSER_RUNTIME")=="1":browser(text)
    print("PASS: Source Route exact identity, live citations, canonical provenance, nondestructive jump state, accessibility/privacy contracts verified")

if __name__=="__main__":main()

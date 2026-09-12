from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

import verify_case_delta_r1 as base


def runtime_fixture(payload: str, mode: str) -> str:
    article, prelude = base.article_for(mode)
    invalid = {
        "id-only",
        "class-only",
        "duplicate-exact",
        "exact-plus-id-earlier",
        "exact-plus-class-earlier",
        "exact-plus-id-later",
        "exact-plus-class-later",
        "reversed-footnotes",
        "too-short",
        "too-few-sources",
    }
    invalid_js = "true" if mode in invalid else "false"
    script = f'''
<script>
(()=>{{
 const mode={mode!r};
 const invalid={invalid_js};
 const fail=m=>{{document.body.dataset.fvTest='fail';document.body.dataset.fvReason=m}};
 const pass=()=>{{document.body.dataset.fvTest='pass'}};
 try{{
   const band=document.querySelector('[data-fvcd-band]');
   if(invalid){{
     if(band||document.querySelector('.fvcd-dialog'))return fail('invalid Sources fixture did not fail closed');
     return pass();
   }}
   if(!band)return fail('launcher missing');
   const primary=band.querySelector('.fvcd-primary');
   primary.click();
   setTimeout(()=>{{
     try{{
       if(mode==='storage-fail'){{
         if(!band.textContent.includes('storage is unavailable'))return fail('storage failure not surfaced');
         if(document.querySelector('.fvcd-dialog'))return fail('dialog opened after failed save');
         return pass();
       }}
       const stored=JSON.parse(localStorage.getItem('fv_case_delta_v1')||'{{}}')[location.pathname];
       if(!stored)return fail('snapshot missing');
       if(stored.sections.length!==4||stored.sources.length!==4||stored.figures.length!==2)return fail('snapshot structure wrong');
       if(JSON.stringify(stored).includes('#ref-1'))return fail('citation backlink leaked');
       document.getElementById('curve-2').textContent+=' Updated story wording.';
       document.getElementById('fv-fn-2').firstChild.textContent='Archive source 2 revised wording ';
       document.querySelector('#fig-2 figcaption').textContent='Published caption 2 revised';
       primary.click();
       setTimeout(()=>{{
         try{{
           const dialog=document.querySelector('.fvcd-dialog');
           if(!dialog||!dialog.open)return fail('comparison dialog missing');
           if(dialog.querySelector('[data-fvcd-stat="all"] strong').textContent!=='3')return fail('comparison total wrong');
           if(mode==='valid'){{
             if(dialog.querySelector('[data-fvcd-stat="story"] strong').textContent!=='1')return fail('story total wrong');
             if(dialog.querySelector('[data-fvcd-stat="source"] strong').textContent!=='1')return fail('source total wrong');
             if(dialog.querySelector('[data-fvcd-stat="figure"] strong').textContent!=='1')return fail('figure total wrong');
             return pass();
           }}
           const target=[...document.querySelectorAll('h2')].find(h=>h.textContent==='The curve under Malbone Street');
           if(!target)return fail('jump target missing');
           const expectedTab=mode==='jump-preowned'?'0':null;
           const expectedFocusClass=mode==='jump-preowned';
           const jump=[...dialog.querySelectorAll('.fvcd-row')].find(r=>r.textContent.includes('The curve under Malbone Street'))?.querySelector('.fvcd-jump');
           if(!jump)return fail('jump control missing');
           jump.click();
           setTimeout(()=>{{
             try{{
               if(target.getAttribute('tabindex')!==expectedTab)return fail('jump changed tabindex ownership');
               if(target.classList.contains('fvcd-story-focus')!==expectedFocusClass)return fail('jump changed focus-class ownership');
               if(mode==='jump-preowned'&&!target.classList.contains('publisher-class'))return fail('jump removed publisher class');
               primary.click();
               setTimeout(()=>{{
                 try{{
                   const d2=document.querySelector('.fvcd-dialog');
                   if(!d2||!d2.open)return fail('repeat dialog missing');
                   const jump2=[...d2.querySelectorAll('.fvcd-row')].find(r=>r.textContent.includes('The curve under Malbone Street'))?.querySelector('.fvcd-jump');
                   if(!jump2)return fail('repeat jump missing');
                   jump2.click();
                   setTimeout(()=>{{
                     if(target.getAttribute('tabindex')!==expectedTab)return fail('repeat jump drifted tabindex');
                     if(target.classList.contains('fvcd-story-focus')!==expectedFocusClass)return fail('repeat jump drifted focus class');
                     if(mode==='jump-preowned'&&!target.classList.contains('publisher-class'))return fail('repeat jump removed publisher class');
                     return pass();
                   }},1750);
                 }}catch(e){{fail(e&&e.message?e.message:String(e))}}
               }},100);
             }}catch(e){{fail(e&&e.message?e.message:String(e))}}
           }},1750);
         }}catch(e){{fail(e&&e.message?e.message:String(e))}}
       }},100);
     }}catch(e){{fail(e&&e.message?e.message:String(e))}}
   }},80);
 }}catch(e){{fail(e&&e.message?e.message:String(e))}}
}})();
</script>
'''
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Case Delta R1 runtime</title></head>"
        f"<body>{prelude}{article}{payload}{script}</body></html>"
    )


def main() -> None:
    browser = next(
        (shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser") if shutil.which(name)),
        None,
    )
    base.require(browser is not None, "headless Chrome/Chromium not available")
    payload = base.PAYLOAD.read_text(encoding="utf-8")
    modes = (
        "valid",
        "id-only",
        "class-only",
        "duplicate-exact",
        "exact-plus-id-earlier",
        "exact-plus-class-earlier",
        "exact-plus-id-later",
        "exact-plus-class-later",
        "reversed-footnotes",
        "too-short",
        "too-few-sources",
        "storage-fail",
        "jump-absent",
        "jump-preowned",
    )
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        handler = partial(base.QuietHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        origin = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for mode in modes:
                page = root / f"case-delta-r1-runtime-{mode}.html"
                page.write_text(runtime_fixture(payload, mode), encoding="utf-8")
                proc = subprocess.run(
                    [
                        browser,
                        "--headless=new",
                        "--no-sandbox",
                        "--disable-gpu",
                        "--disable-dev-shm-usage",
                        "--virtual-time-budget=4500",
                        "--dump-dom",
                        f"{origin}/{page.name}",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=40,
                )
                base.require(proc.returncode == 0, f"browser fixture {mode} failed: {proc.stderr[-500:]}")
                if 'data-fv-test="pass"' not in proc.stdout:
                    reason = re.search(r'data-fv-reason="([^"]*)"', proc.stdout)
                    raise SystemExit(
                        f"FAIL: browser fixture {mode}: "
                        f"{reason.group(1) if reason else 'runtime assertions failed'}"
                    )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
    print(
        "PASS: Case Delta R1 browser runtime verified across canonical, partial, mixed, duplicate, "
        "reversed, storage-failure, and repeated nondestructive story-jump fixtures"
    )


if __name__ == "__main__":
    main()

import json, re, sys, time, hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
D = Path("verify_out")
acc = json.load(open(D/"source_accessibility.json", encoding="utf-8"))
todo = [a["url"] for a in acc if not a["ok"]]
res = {}
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    for u in todo:
        pg = ctx.new_page(); rec = {"url": u, "ok": False}
        try:
            r = pg.goto(u, wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(1500)
            st = r.status if r else None
            ctype = (r.headers.get("content-type", "") if r else "")
            txt = ""
            if "pdf" in ctype.lower(): rec.update(ok=True, kind="pdf", status=st, final_url=pg.url, note="PDF not parsed")
            else:
                txt = re.sub(r"\s+", " ", pg.inner_text("body"))
                blocked = bool(re.search(r"access denied|captcha|verify you are human|are you a robot|unusual traffic", txt[:600], re.I)) or len(txt) < 400
                if not blocked and len(txt) < 1500: pg.wait_for_timeout(2500); txt = re.sub(r"\s+", " ", pg.inner_text("body"))
                rec.update(ok=(st is not None and st < 400 and not blocked), kind="html", status=st, final_url=pg.url, title=pg.title()[:160], chars=len(txt), blocked_or_thin=blocked, text=txt, sha256=hashlib.sha256(txt.encode()).hexdigest())
                if blocked: rec["note"] = "page looked like a block page or was nearly empty; not used as evidence"
        except Exception as e:
            rec.update(error=f"{type(e).__name__}: {str(e)[:120]}")
        finally:
            pg.close()
        res[u] = rec; time.sleep(0.4)
    b.close()
json.dump(res, open(D/"browser_fetch.json", "w", encoding="utf-8"), ensure_ascii=False)
ok = [r for r in res.values() if r["ok"] and r.get("kind") == "html"]
print(f"retried {len(todo)} | usable via browser: {len(ok)} | pdf: {sum(1 for r in res.values() if r.get('kind')=='pdf')} | still failed/blocked: {len(res)-len(ok)-sum(1 for r in res.values() if r.get('kind')=='pdf')}")
for u, r in res.items():
    if not r["ok"]: print("  FAIL", (r.get("status") or r.get("error") or "")  , u[:100])

import json, re, hashlib, fitz
from pathlib import Path
from playwright.sync_api import sync_playwright
D = Path("verify_out"); urls = [
 "https://bookstore.ksre.ksu.edu/pubs/dehydrating-meat-safely-at-home_MF3173.PDF",
 "https://nchfp.uga.edu/papers/guide/GUIDE01_HomeCan_rev0715.pdf",
 "https://ussconstitutionmuseum.org/wp-content/uploads/dlm_uploads/2019/05/Food-and-Drink-in-the-US-Navy.pdf",
 "https://www.ready.gov/sites/default/files/2021-11/are-you-ready-guide.pdf",
 "https://www.ready.gov/sites/default/files/2024-03/ready.gov_power-outage_hazard-info-sheet.pdf",
 "https://www.ready.gov/sites/default/files/2024-05/ready_supply-kit-checklist.pdf"]
out = {}
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge"); ctx = b.new_context()
    for u in urls:
        rec = {"url": u, "ok": False}
        try:
            r = ctx.request.get(u, timeout=90000)
            rec["status"] = r.status
            body = r.body()
            rec["bytes"] = len(body); rec["sha256"] = hashlib.sha256(body).hexdigest()
            if r.status < 400 and body[:5] == b"%PDF-":
                doc = fitz.open(stream=body, filetype="pdf")
                txt = " ".join(pg.get_text() for pg in doc); txt = re.sub(r"\s+", " ", txt)
                rec.update(ok=True, pages=doc.page_count, chars=len(txt), text=txt, meta={k: str(v)[:40] for k, v in (doc.metadata or {}).items() if v and k in ("title", "creationDate", "modDate")})
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {str(e)[:120]}"
        out[u] = rec
    b.close()
json.dump(out, open(D/"pdf_text.json", "w", encoding="utf-8"), ensure_ascii=False)
for u, r in out.items(): print(("OK " if r["ok"] else "FAIL"), r.get("status"), "pages", r.get("pages"), "chars", r.get("chars"), "|", u.split("/")[-1][:60], r.get("error", ""))

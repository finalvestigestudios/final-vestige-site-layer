"""AI-assisted figure-to-source triage. NOT independent human verification.
For every article block that carries a {{cite:..}} and a quantified figure, fetch the cited URL(s) and test whether the figure
appears in the page text. Records source accessibility (status, final URL, title, dates). Output: JSON in the scratch dir."""
import sys, re, json, html, hashlib, time, concurrent.futures as cf, urllib.request, urllib.error, ssl
from pathlib import Path
from html.parser import HTMLParser

REPO = Path(sys.argv[1]); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(REPO / "preparedness" / "tools"))
import build

UA = "FinalVestigePreparednessVerifier/1.0 (read-only source check; finalvestige.com)"
FIG = re.compile(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?|\d+/\d+|[½⅛¼¾⅓⅔])\s*(?:-|to)?\s*(?:(?:°\s?[FC])|degrees?|percent|%|feet|foot|ft|hours?|hrs?|minutes?|mins?|seconds?|days?|weeks?|months?|years?|drops?|teaspoons?|tsp|tablespoons?|gallons?|quarts?|liters?|litres?|ounces?|oz|pounds?|lbs?|inch(?:es)?|micron|mL|ml|cups?|miles?|mph|psi|pounds? of pressure|feet away)\b", re.I)
BLOCK = re.compile(r"<(p|li|td|th|blockquote|dd)\b[^>]*>(.*?)</\1>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")

class Txt(HTMLParser):
    def __init__(s): super().__init__(); s.t = []; s.skip = 0; s.title = ""; s.intitle = False; s.meta = {}
    def handle_starttag(s, tag, a):
        if tag in ("script", "style", "noscript", "svg"): s.skip += 1
        if tag == "title": s.intitle = True
        if tag == "meta":
            d = dict(a); k = (d.get("name") or d.get("property") or "").lower()
            if k and d.get("content") and any(x in k for x in ("date", "modified", "published", "updated", "reviewed")): s.meta[k] = d["content"][:40]
    def handle_endtag(s, tag):
        if tag in ("script", "style", "noscript", "svg") and s.skip: s.skip -= 1
        if tag == "title": s.intitle = False
    def handle_data(s, d):
        if s.intitle: s.title += d
        if not s.skip: s.t.append(d)

def fetch(url):
    rec = {"url": url, "ok": False}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.8,*/*;q=0.5"})
        with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as r:
            rec.update(status=r.status, final_url=r.geturl(), ctype=r.headers.get("Content-Type", ""))
            raw = r.read(6_000_000)
        rec["bytes"] = len(raw)
        if "pdf" in rec["ctype"].lower() or raw[:5] == b"%PDF-":
            rec.update(ok=True, kind="pdf", text="", note="PDF not parsed by this checker; figures NOT tested against it")
        else:
            txt = raw.decode("utf-8", "replace"); p = Txt(); p.feed(txt)
            body = html.unescape(" ".join(p.t)); body = re.sub(r"\s+", " ", body)
            if len(body) < 400:
                rec.update(ok=False, kind="html", error=f"thin page ({len(body)} chars): likely JavaScript-rendered; retry in browser", text=""); return rec
            rec.update(ok=True, kind="html", text=body, title=re.sub(r"\s+", " ", p.title).strip()[:160], dates=p.meta, sha256=hashlib.sha256(raw).hexdigest())
    except urllib.error.HTTPError as e:
        rec.update(status=e.code, error=f"HTTP {e.code}")
    except Exception as e:
        rec.update(error=f"{type(e).__name__}: {str(e)[:120]}")
    return rec

def norm(s):
    s = s.lower().replace("½", "1/2").replace("⅛", "1/8").replace("¼", "1/4").replace("¾", "3/4").replace("–", "-").replace("’", "'")
    return re.sub(r"\s+", " ", s)

lib = build.Library()
claims = []
for slug, meta in lib.articles.items():
    if meta.get("kind") == "tool": continue
    body, order = build.resolve_tokens(lib, meta) if False else (meta["_body"], None)
    for m in BLOCK.finditer(meta["_body"]):
        raw = m.group(2)
        ids = CITE.findall(raw)
        if not ids: continue
        text = norm(html.unescape(TAG.sub(" ", CITE.sub(" ", raw))))
        figs = sorted({re.sub(r"\s+", " ", f.group(0)).strip() for f in FIG.finditer(text)})
        if figs: claims.append({"slug": slug, "track": meta["track"], "text": text[:400], "figs": figs, "cites": ids})
urls = {}
for c in claims:
    for i in c["cites"]:
        r = lib.register.get(i)
        if r: urls[i] = r["url"]
distinct = sorted(set(urls.values()))
print(f"claim blocks with figures: {len(claims)} | distinct cited URLs: {len(distinct)}", flush=True)

fetched = {}
with cf.ThreadPoolExecutor(max_workers=6) as ex:
    for rec in ex.map(fetch, distinct):
        fetched[rec["url"]] = rec
        time.sleep(0.05)
pf = OUT / "pdf_text.json"
if pf.exists():
    for u, r in json.loads(pf.read_text(encoding="utf-8")).items():
        if u in fetched and r.get("ok"):
            fetched[u] = {"url": u, "ok": True, "kind": "html", "text": r["text"], "via": "edge-browser+pymupdf", "pdf_pages": r["pages"]}
bf = OUT / "browser_fetch.json"
if bf.exists():
    for u, r in json.loads(bf.read_text(encoding="utf-8")).items():
        if u in fetched and not fetched[u]["ok"] and r.get("ok"):
            r = dict(r); r["via"] = "edge-browser"; fetched[u] = r
ok = sum(1 for r in fetched.values() if r["ok"]); pdf = sum(1 for r in fetched.values() if r.get("kind") == "pdf")
print(f"fetched ok: {ok}/{len(fetched)} (pdf not parsed: {pdf})", flush=True)

results = []
for c in claims:
    srcs = [(i, urls.get(i)) for i in c["cites"]]
    pages = [(i, fetched.get(u)) for i, u in srcs if u]
    testable = [p for p in pages if p[1] and p[1]["ok"] and p[1].get("kind") == "html"]
    status = "NO_TESTABLE_SOURCE"
    missing = []
    if testable:
        corpus = " || ".join(norm(p[1]["text"]) for p in testable)
        for f in c["figs"]:
            num = re.match(r"[\d,\.]+|\d+/\d+", f.replace("½", "1/2"))
            token = norm(num.group(0)) if num else norm(f)
            if token not in corpus: missing.append(f)
        status = "ALL_FIGURES_FOUND" if not missing else ("SOME_FIGURES_NOT_FOUND" if len(missing) < len(c["figs"]) else "NO_FIGURES_FOUND")
    results.append({**c, "status": status, "missing": missing, "tested_sources": [p[0] for p in testable], "untested_sources": [p[0] for p in pages if p not in testable]})

import collections
print(collections.Counter(r["status"] for r in results), flush=True)
(OUT / "figure_checks.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
acc = [{k: v for k, v in r.items() if k != "text"} for r in fetched.values()]
(OUT / "source_accessibility.json").write_text(json.dumps(acc, indent=1, ensure_ascii=False), encoding="utf-8")

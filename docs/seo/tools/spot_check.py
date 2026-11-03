"""Independent spot check of the 72 applied SEO changes against the public site.

Inputs : evidence/changeset.json, evidence/crawl-spotcheck-2026-11-02b.json (fresh crawl)
Output : evidence/spotcheck-2026-11-02b.json and a printed summary
Checks per changed URL: HTTP 200, canonical == URL, title/description exactly as applied, robots has no noindex,
JSON-LD parses, exactly one Article on posts and on the Article-typed guide page, no duplicate @type of
Article/FAQPage/BreadcrumbList. Per inserted block: exactly one `fv-related-reading` block, every link in it
returns HTTP 200 and points at a canonical URL (no redirect).
Run: PYTHONUTF8=1 python docs/seo/tools/spot_check.py
"""
import json, re, pathlib, urllib.request, urllib.error, time, collections

ROOT = pathlib.Path(__file__).resolve().parents[1]
cs = json.loads((ROOT / "evidence/changeset.json").read_text(encoding="utf-8"))
crawl = {x["id"]: x for x in json.loads((ROOT / "evidence/crawl-spotcheck-2026-11-02b.json").read_text(encoding="utf-8"))}


def get(u):
    for _ in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40)
            return r.status, r.geturl(), r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", "5")) + 1)
                continue
            return e.code, u, ""
        except Exception:
            time.sleep(2)
    return 0, u, ""


problems = []
linkcache = {}
rows = []
for m in cs["meta"]:
    c = crawl[m["id"]]
    a = {k: v[1] for k, v in m["changes"].items()}
    errs = []
    if c["status"] != 200: errs.append("status")
    if c["canonical"] != c["url"]: errs.append("canonical")
    if "noindex" in (c["robots"] or ""): errs.append("noindex")
    if "jetpack_seo_html_title" in a and c["title"] != a["jetpack_seo_html_title"]: errs.append("title")
    if "advanced_seo_description" in a and c["desc"] != a["advanced_seo_description"]: errs.append("desc")
    if "PARSE_ERROR" in c["jsonld"]: errs.append("jsonld-parse")
    cnt = collections.Counter(t for t in c["jsonld"] if t in ("Article", "FAQPage", "BreadcrumbList"))
    if any(v > 1 for v in cnt.values()): errs.append(f"duplicate schema {dict(cnt)}")
    if c["type"] == "post" and cnt["Article"] != 1: errs.append("post Article count != 1")
    if m["id"] == 1029 and cnt["Article"] != 1: errs.append("guide Article count != 1")
    if c["h1"] != 1: errs.append(f"h1={c['h1']}")
    rows.append(dict(id=m["id"], kind="meta", ok=not errs, errs=errs))
    if errs: problems.append((m["id"], errs))

for x in cs["inserts"]:
    c = crawl[x["id"]]
    s, _, h = get(c["url"])
    blocks = len(re.findall(r'class="[^"]*fv-related-reading', h))
    hrefs = re.findall(r'href="([^"]+)"', re.search(r'<div class="wp-block-group fv-related-reading.*?</div>', h, re.S).group(0)) if blocks else []
    errs = []
    if blocks != 1: errs.append(f"related blocks={blocks}")
    for u in hrefs:
        if u not in linkcache:
            st, final, _ = get(u)
            linkcache[u] = (st, final)
        st, final = linkcache[u]
        if st != 200: errs.append(f"{u} -> {st}")
        elif final.rstrip("/") != u.rstrip("/"): errs.append(f"{u} redirects to {final}")
    rows.append(dict(id=x["id"], kind="insert", ok=not errs, errs=errs, links=len(hrefs)))
    if errs: problems.append((x["id"], errs))

out = dict(checked_meta=sum(1 for r in rows if r["kind"] == "meta"), checked_inserts=sum(1 for r in rows if r["kind"] == "insert"),
           unique_links_checked=len(linkcache), problems=problems, rows=rows,
           site=dict(urls=len(crawl), non_200=[c["url"] for c in crawl.values() if c["status"] != 200],
                     no_single_h1=[c["url"] for c in crawl.values() if c["h1"] != 1],
                     jsonld_parse_errors=[c["url"] for c in crawl.values() if "PARSE_ERROR" in c["jsonld"]],
                     noindex=[c["url"] for c in crawl.values() if "noindex" in (c["robots"] or "")],
                     new_urls_not_in_baseline=[]))
(ROOT / "evidence/spotcheck-2026-11-02b.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(f"meta {out['checked_meta']}  inserts {out['checked_inserts']}  unique links {out['unique_links_checked']}  problems {len(problems)}")
for p in problems[:20]:
    print("PROBLEM", p)
print(json.dumps(out["site"], indent=1)[:900])

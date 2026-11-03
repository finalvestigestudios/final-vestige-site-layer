"""Verify the applied SEO change set against the public site and write the ledger.

Inputs : evidence/seo-prestate-2026-11-02.json, evidence/changeset.json,
         evidence/execution-results.json, evidence/crawl-after-2026-11-02.json
Output : SEO_IMPLEMENTATION_LEDGER.md, evidence/verification-2026-11-02.json
Run    : PYTHONUTF8=1 python docs/seo/tools/build_ledger.py
"""
import json, hashlib, html, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
E = ROOT / "evidence"
pre = {x["id"]: x for x in json.loads((E / "seo-prestate-2026-11-02.json").read_text(encoding="utf-8"))}
cs = json.loads((E / "changeset.json").read_text(encoding="utf-8"))
ex = json.loads((E / "execution-results.json").read_text(encoding="utf-8"))
after = {x["id"]: x for x in json.loads((E / "crawl-after-2026-11-02.json").read_text(encoding="utf-8"))}
before_crawl = {x["id"]: x for x in json.loads((E / "crawl-baseline-2026-11-02.json").read_text(encoding="utf-8"))}


def h(o):
    return hashlib.sha1(json.dumps(o, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def norm(l):
    l = l.split("#")[0].split("?")[0]
    if l.startswith("/"):
        l = "https://finalvestige.com" + l
    return l if l.endswith("/") else l + "/"


NAME = {"jetpack_seo_html_title": "title", "advanced_seo_description": "description", "jetpack_seo_schema_type": "schema"}
rows, results = [], {"meta": [], "inserts": [], "failures": []}

for m in cs["meta"]:
    i = m["id"]
    a = after[i]
    s = pre[i]
    b_vals = {k: v[0] for k, v in m["changes"].items()}
    a_vals = {k: v[1] for k, v in m["changes"].items()}
    ok = True
    notes = []
    if "jetpack_seo_html_title" in a_vals:
        t = a["title"]
        good = t == a_vals["jetpack_seo_html_title"]
        ok &= good
        notes.append(f"title {'OK' if good else 'MISMATCH: ' + str(t)}")
    if "advanced_seo_description" in a_vals:
        d = a["desc"]
        good = d == a_vals["advanced_seo_description"]
        ok &= good
        notes.append(f"desc {'OK' if good else 'MISMATCH: ' + str(d)}")
    if "jetpack_seo_schema_type" in a_vals:
        good = "Article" in a["jsonld"]
        ok &= good
        notes.append(f"Article JSON-LD {'present' if good else 'ABSENT'}")
    ok &= a["status"] == 200
    ok &= a["h1"] >= 1 if "h1" in a else True
    rec = dict(id=i, url=m["url"], fields=sorted(NAME[k] for k in m["changes"]), before_meta_sha1=h(b_vals), after_meta_sha1=h(a_vals),
               content_sha1_unchanged_by_meta_edit=s["content_sha1"], verified=bool(ok), notes="; ".join(notes))
    results["meta"].append(rec)
    if not ok:
        results["failures"].append(rec)
    rows.append(rec)

for x in cs["inserts"]:
    i = x["id"]
    a = after[i]
    hrefs = [norm(u) for u in re.findall(r'href="([^"]+)"', html.unescape(x["block_markup"]))]
    targets = {norm(t) for t in a["internal_targets"]}
    missing = [u for u in hrefs if u not in targets]
    r = ex["inserts"][str(i)]
    rec = dict(id=i, url=pre[i]["link"], op=x["op"], index=x["index"], content_hash_before=x["expected_content_hash"],
               content_hash_after=r["content_hash_after"], modified_before=x["expected_modified"], modified_after=r["modified_after"],
               links_added=len(hrefs), links_found_on_public_page=len(hrefs) - len(missing), missing=missing,
               internal_links_before=before_crawl[i]["internal_links"], internal_links_after=a["internal_links"],
               verified=(not missing and a["status"] == 200))
    results["inserts"].append(rec)
    if not rec["verified"]:
        results["failures"].append(rec)

# whole-site regression checks
reg = dict(urls_after=len(after), non_200=[u["url"] for u in after.values() if u["status"] != 200],
           no_h1=[u["url"] for u in after.values() if u["h1"] != 1],
           canonical_mismatch=[u["url"] for u in after.values() if u["canonical"] != u["url"]],
           untouched_pages_changed_title_or_desc=[u["url"] for i, u in after.items() if i in before_crawl and i not in {m["id"] for m in cs["meta"]}
                                                  and (u["title"] != before_crawl[i]["title"] or u["desc"] != before_crawl[i]["desc"])],
           new_since_baseline=sorted(set(after) - set(before_crawl)))
results["regression"] = reg
(E / "verification-2026-11-02.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")

nm = len(results["meta"]); ni = len(results["inserts"])
vm = sum(r["verified"] for r in results["meta"]); vi = sum(r["verified"] for r in results["inserts"])
L = ["# SEO implementation ledger - 2026-11-02", "",
     "Branch `feature/seo-competitor-implementation` (cut from `feature/experience-2-living-archive-sprint5` @ `9a74ecda`). Companion to `docs/experience-2.0/IMPLEMENTATION_LEDGER.md`.", "",
     "## Summary", "",
     f"- Applied to finalvestige.com through the WordPress.com content tools after explicit user approval in the session: **{nm} meta edits** and **{ni} appended link blocks**.",
     f"- Verified on the public site by re-crawl (`evidence/crawl-after-2026-11-02.json`): meta {vm}/{nm}, inserts {vi}/{ni}. Failures: {len(results['failures'])}.",
     f"- Whole-site check after the change: {reg['urls_after']} URLs crawled, non-200: {len(reg['non_200'])}, canonical mismatches: {len(reg['canonical_mismatch'])}, pages not in the change set whose title or description changed: {len(reg['untouched_pages_changed_title_or_desc'])}.",
     "- **Homepage (page 6) was not edited.** Re-read after the change set via `page-sections.list`: modified `2026-11-02T17:48:13`, content_hash `1207973a80fb6618dcc91bd56131140a82854979`, block 1 SHA-1 `8c0dd5c3adce073fd58f5001e0f90d523ffad277` (unchanged).",
     "- No Preparedness Archive content was published; no safety claims were added (only navigation links and title/description wording drawn from existing text).",
     "- No plugin, theme, menu or setting change. Schema comes from the existing Jetpack SEO `jetpack_seo_schema_type` field.", "",
     "## Known gaps (stated, not hidden)", "",
     "- **Ahrefs returned `Insufficient plan` for every data call**, so there is no keyword, traffic, ranking or Search Console number anywhere in this work. Competitors are SERP-observed and unverified by a tool (`01-COMPETITORS-AND-GAPS.md`). The keyword work can be redone from an Ahrefs/Semrush export or Search Console access.",
     "- Effect on rankings is **unknown**. `05-GSC-MEASUREMENT-PLAN.md` defines how to measure it.",
     "- The wp-admin browser session expired mid-task and I cannot sign in for you; the pre-edit snapshot was taken before that. Post-edit state is verified from the public site and the tools' own returned hashes, not from a second wp-admin snapshot.",
     "- The 5 posts published by the content-packages session (IDs 1917-1926) appeared during this work; they are not in the change set and were not touched. The crawl takes its URL list from the public REST API, which did not list them yet (140 URLs both before and after), so they are also outside the before/after crawl comparison.", "",
     "## Rollback (applies to every row below)", "",
     "- **Meta edit:** `pages.update` / `posts.update` with `meta` set to the raw *before* values in `04-CHANGESET-DIFFS.md` (an empty before-value means set the field to an empty string). Success = the public `<title>`/description return to the baseline in `evidence/crawl-baseline-2026-11-02.json`.",
     "- **Link block:** `post-sections.list` / `page-sections.list`, find the top-level `core/group` with class `fv-related-reading` (last block; index = the *index* column), then `post-sections.remove` / `page-sections.remove` with its `block_hash` and the fresh lock tokens. Success = `content_hash` equals the *content_hash before* column.",
     "- **Full revert of a body:** the pre-edit raw content of every post and page is in `Projects/fv-release-backups/seo-2026-11-02/raw-content-2026-11-02.json` (outside the repo, keyed by ID), and WordPress keeps a revision for each save.",
     "- **Schema test (page 1029):** set `jetpack_seo_schema_type` back to an empty string.", "",
     "## A. Link-block inserts", "",
     "| ID | URL path | Op @ index | content_hash before | content_hash after | In-content internal links before / after | Links added / found live | Verified |",
     "|---|---|---|---|---|---|---|---|"]
for r in results["inserts"]:
    L.append(f"| {r['id']} | {r['url'].replace('https://finalvestige.com','')} | {r['op']} @ {r['index']} | `{r['content_hash_before'][:12]}` | `{r['content_hash_after'][:12]}` | {r['internal_links_before']} / {r['internal_links_after']} | {r['links_added']} / {r['links_found_on_public_page']} | {'yes' if r['verified'] else 'NO'} |")
L += ["", "Full 40-character hashes are in `evidence/verification-2026-11-02.json` and `evidence/changeset.json`.", "",
      "## B. Meta edits", "",
      "| ID | URL path | Fields | meta SHA-1 before | meta SHA-1 after | Verified on public page | Detail |", "|---|---|---|---|---|---|---|"]
for r in results["meta"]:
    L.append(f"| {r['id']} | {r['url'].replace('https://finalvestige.com','')} | {', '.join(r['fields'])} | `{r['before_meta_sha1'][:12]}` | `{r['after_meta_sha1'][:12]}` | {'yes' if r['verified'] else 'NO'} | {r['notes']} |")
L += ["", "`meta SHA-1` is the SHA-1 of the JSON object of the edited fields (sorted keys, UTF-8). Body content is unchanged by meta edits, so each page's content SHA-1 (in `evidence/seo-prestate-2026-11-02.json`) is the same before and after.", "",
      "## Findings not acted on", "",
      "- Homepage structured data lists `Organization` twice (one from the theme/plugin, one from block 5 of page 6). Block 5 is inside the protected page-6 content, so it was not edited. Owner decision.",
      "- 22 of the 24 method guides (`the-...`) still have one inbound content link; they need posts that genuinely use their method (see `03-INTERNAL-LINK-MAP.md`).",
      "- Header/footer navigation was not changed.", ""]
(ROOT / "SEO_IMPLEMENTATION_LEDGER.md").write_text("\n".join(L), encoding="utf-8")
print(f"meta {vm}/{nm}  inserts {vi}/{ni}  failures {len(results['failures'])}")
print(json.dumps(reg, indent=1)[:1500])
for f in results["failures"][:12]:
    print("FAIL", f)

"""QA-ONLY simulation of the custody-record update the integrated tree would need. NOT a re-baseline.

Copies the repository's preparedness/ directory to DEST, regenerates sources/crosswalk.json and
sources/article-evidence-lock.json **in the copy only** from the current bytes, and writes a delta report.
The repository's own custody records, pins and gates are never modified. The copy lets validate/build/QA run
on the integrated content; the real tree stays fail-closed (HOLD) until a reviewer re-baselines.
Usage: python simulate_custody_update.py DEST_DIR REPORT.json [ACTIONS.json]   (run from the repo root)
"""
import hashlib, json, shutil, sys
from pathlib import Path

ROOT = Path("preparedness")
dest = Path(sys.argv[1]); report_path = Path(sys.argv[2])
actions = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8")) if len(sys.argv) > 3 else {"clusters": {}}


def blob(p: Path) -> str:
    raw = p.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


if dest.exists():
    shutil.rmtree(dest)
shutil.copytree(ROOT, dest / "preparedness", ignore=shutil.ignore_patterns("build", "__pycache__", "qa", "qa-shots", "r48", "r49", "rc", "audit"))
R = dest / "preparedness"
cw = json.loads((R / "sources/crosswalk.json").read_text(encoding="utf-8"))
lock = json.loads((R / "sources/article-evidence-lock.json").read_text(encoding="utf-8"))
before = {"raw_rows": cw["raw_source_rows"], "unique_urls": cw["unique_source_urls"], "dup_url_groups": cw["duplicate_url_groups"], "dup_id_groups": cw["duplicate_id_groups"], "tools": lock["local_tool_count"], "longform": lock["longform_article_count"]}

files = [("base", "preparedness/sources/register.json", R / "sources/register.json")] + [(p.stem, f"preparedness/sources/fragments/{p.name}", p) for p in sorted((R / "sources/fragments").glob("*.json"))]
by_url, by_id, sf = {}, {}, []
for origin, rel, p in files:
    srcs = json.loads(p.read_text(encoding="utf-8"))["sources"]
    sf.append({"origin": origin, "path": rel, "git_blob_sha": blob(p), "count": len(srcs)})
    for i, s in enumerate(srcs):
        by_url.setdefault(s["url"], []).append({"origin": origin, "source_file": rel, "row_index": i, "source": s})
        by_id.setdefault(s["id"], []).append(origin)
old_groups = {g["url"]: g for g in cw["groups"]}
groups, new_groups, changed_groups = [], [], []
for url, vs in by_url.items():
    if len(vs) < 2:
        continue
    old = old_groups.get(url)
    g = {"url": url, "review_status": "pending-human-source-and-reading-scope-review", "reviewer": None, "reviewed_on": None, "canonical_url": url}
    if old:
        g.update({k: old[k] for k in ("review_status", "reviewer", "reviewed_on", "canonical_url") if k in old})
        if old["variants"] != vs:
            changed_groups.append(url)
    else:
        new_groups.append(url)
    g["identities"] = [{"origin": v["origin"], "id": v["source"]["id"], "row_index": v["row_index"]} for v in vs]
    g["variants"] = vs
    groups.append(g)
cw.update(source_files=sf, raw_source_rows=sum(len(v) for v in by_url.values()), unique_source_urls=len(by_url), duplicate_url_groups=len(groups), duplicate_id_groups=sum(1 for v in by_id.values() if len(v) > 1), groups=groups)

new_origin = {}
for name, v in actions.get("clusters", {}).items():
    for r in v["files"]:
        parts = r["path"].split("/")
        if r["action"] == "add" and len(parts) == 5 and parts[2] == "content" and parts[3] in ("articles", "tools") and parts[4].endswith(".meta.json"):
            new_origin[parts[4][: -len(".meta.json")]] = name
new_origin["family-reunification-card"] = "shelter"  # renamed after integration (slug collision with Start Here's reunification-plan)
slugs = {}
for d in ("articles", "tools"):
    for f in sorted((R / "content" / d).glob("*.meta.json")):
        slugs[f.name[: -len(".meta.json")]] = d
for s, o in new_origin.items():
    if s in slugs:
        cw["article_origins"].setdefault(s, o)
recs = {r["slug"]: r for r in lock["records"]}
changed_articles, added_articles = [], []
for slug, d in slugs.items():
    body, meta = R / "content" / d / f"{slug}.body.html", R / "content" / d / f"{slug}.meta.json"
    row = {"slug": slug, "origin": cw["article_origins"].get(slug), "body": {"path": f"preparedness/content/{d}/{slug}.body.html", "git_blob_sha": blob(body), "bytes": body.stat().st_size},
           "metadata": {"path": f"preparedness/content/{d}/{slug}.meta.json", "git_blob_sha": blob(meta), "bytes": meta.stat().st_size}}
    old = recs.get(slug)
    if old is None:
        added_articles.append(slug); lock["records"].append(row)
    elif old["body"]["git_blob_sha"] != row["body"]["git_blob_sha"] or old["metadata"]["git_blob_sha"] != row["metadata"]["git_blob_sha"]:
        changed_articles.append(slug); recs[slug].update(row)
lock["longform_article_count"] = sum(1 for d in slugs.values() if d == "articles")
lock["local_tool_count"] = sum(1 for d in slugs.values() if d == "tools")
for obj in (cw, lock):
    obj["SIMULATED_FOR_QA_ONLY_NOT_A_BASELINE_NOT_A_REVIEW"] = True
(R / "sources/crosswalk.json").write_text(json.dumps(cw, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
(R / "sources/article-evidence-lock.json").write_text(json.dumps(lock, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
after = {"raw_rows": cw["raw_source_rows"], "unique_urls": cw["unique_source_urls"], "dup_url_groups": cw["duplicate_url_groups"], "dup_id_groups": cw["duplicate_id_groups"], "tools": lock["local_tool_count"], "longform": lock["longform_article_count"]}
rep = {"authority": "QA_SIMULATION_ONLY", "before": before, "after": after, "new_shared_url_groups": new_groups, "changed_shared_url_groups": changed_groups, "changed_articles": changed_articles, "added_articles_and_tools": added_articles, "new_article_origins": new_origin}
report_path.write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({k: rep[k] for k in ("before", "after", "new_shared_url_groups", "added_articles_and_tools")}, indent=1))

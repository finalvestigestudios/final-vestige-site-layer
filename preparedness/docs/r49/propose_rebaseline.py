"""Read-only: compute what a reviewed re-baseline of the custody pins would have to change for the merged tree.
Writes nothing to the frozen records. Usage: python propose_rebaseline.py OUT.json (run from the repo root)."""
import hashlib, json, re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path("preparedness")


def blob(p: Path) -> str:
    raw = p.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


lock = json.loads((ROOT / "sources/article-evidence-lock.json").read_text(encoding="utf-8"))
cw = json.loads((ROOT / "sources/crosswalk.json").read_text(encoding="utf-8"))
out = {"authority": "PROPOSAL_ONLY_NOT_A_BASELINE_NOT_A_REVIEW", "articles": [], "source_files": [], "counts": {}, "pins_in_code_and_tests": {}}

recorded = {r["slug"]: r for r in lock["records"]}
actual = {}
for d in ("articles", "tools"):
    for f in sorted((ROOT / "content" / d).glob("*.meta.json")):
        slug = f.name[: -len(".meta.json")]
        actual[slug] = (d, f, f.with_name(slug + ".body.html"))
for slug, (d, mf, bf) in sorted(actual.items()):
    row = recorded.get(slug)
    new = {"body": {"git_blob_sha": blob(bf), "bytes": bf.stat().st_size}, "metadata": {"git_blob_sha": blob(mf), "bytes": mf.stat().st_size}}
    if row is None:
        out["articles"].append({"slug": slug, "change": "ADDED", "kind_dir": d, "new": new})
    else:
        ch = [k for k in ("body", "metadata") if row[k]["git_blob_sha"] != new[k]["git_blob_sha"]]
        if ch:
            out["articles"].append({"slug": slug, "change": "MODIFIED " + "+".join(ch), "old": {k: {"git_blob_sha": row[k]["git_blob_sha"], "bytes": row[k]["bytes"]} for k in ch}, "new": {k: new[k] for k in ch}})
for slug in sorted(set(recorded) - set(actual)):
    out["articles"].append({"slug": slug, "change": "REMOVED"})

rows_all = []
for r in cw["source_files"]:
    p = Path(r["path"]); cur = json.loads(p.read_text(encoding="utf-8"))["sources"]
    out["source_files"].append({"path": r["path"], "origin": r["origin"], "old_blob": r["git_blob_sha"], "new_blob": blob(p), "old_count": r["count"], "new_count": len(cur), "changed": r["git_blob_sha"] != blob(p)})
for p in sorted((ROOT / "sources/fragments").glob("*.json")):
    if f"preparedness/sources/fragments/{p.name}" not in {r["path"] for r in cw["source_files"]}:
        out["source_files"].append({"path": f"preparedness/sources/fragments/{p.name}", "change": "ADDED"})
by_url = defaultdict(list)
for r in cw["source_files"]:
    for i, s in enumerate(json.loads(Path(r["path"]).read_text(encoding="utf-8"))["sources"]):
        by_url[s["url"]].append((r["origin"], s["id"]))
known = {g["url"] for g in cw["groups"]}
cur_dups = {u: v for u, v in by_url.items() if len(v) > 1}
out["counts"] = {"raw_rows": {"recorded": cw["raw_source_rows"], "now": sum(len(v) for v in by_url.values())}, "unique_urls": {"recorded": cw["unique_source_urls"], "now": len(by_url)},
                 "duplicate_url_groups": {"recorded": cw["duplicate_url_groups"], "now": len(cur_dups)}, "longform_articles": {"recorded": lock["longform_article_count"], "now": sum(1 for s, v in actual.items() if v[0] == "articles")},
                 "tools": {"recorded": lock["local_tool_count"], "now": sum(1 for s, v in actual.items() if v[0] == "tools")}}
out["new_shared_url_groups_needing_human_scope_review"] = {u: v for u, v in cur_dups.items() if u not in known}
out["article_origins_missing"] = sorted(s for s in actual if s not in cw["article_origins"])
pins = defaultdict(list)
for p in list((ROOT / "tools").glob("*.py")) + list((ROOT / "tests").glob("*.py")):
    t = p.read_text(encoding="utf-8")
    for pat, label in ((r"\b224\b", "224 raw rows"), (r"\b186\b", "186 unique URLs"), (r"FROZEN_BLOBS", "FROZEN_BLOBS pins"), (r"35\s*\+\s*1|35-article|seventy[_ -]two|\b72\b", "35+1 / 72-file inventory"), (r"\b81\b", "81-file manifest")):
        if re.search(pat, t): pins[label].append(p.name)
out["pins_in_code_and_tests"] = {k: sorted(set(v)) for k, v in pins.items()}
Path(sys.argv[1]).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"articles": [(a["slug"], a["change"]) for a in out["articles"]], "counts": out["counts"], "new_groups": list(out["new_shared_url_groups_needing_human_scope_review"]), "origins_missing": out["article_origins_missing"], "pin_files": {k: len(v) for k, v in out["pins_in_code_and_tests"].items()}}, indent=1))

#!/usr/bin/env python3
"""R152: read-only, fail-closed historical-food citation alias custody.

This validates bytes and discloses source-record differences. It does NOT decide
which preservation instructions are safe, approve source readings or publish.
Requires a complete trusted local Git checkout with frozen commits available.
"""
import argparse
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{40}\Z")
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
OLD, NEW = "hist-food-nchfp-jerky", "nchfp-jerky"
CANDIDATE = "2826612f9caf327dff3ef00b242e4e67a3491200"
UPSTREAM = "67e116e536c7410bed30f8f3b1bb8c166f3c223d"
BODIES = {"pemmican-and-dried-meats": (7, 46), "pioneer-travel-rations": (1, 39)}
SOURCES = {
    "preparedness/sources/register.json": "b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77",
    "preparedness/sources/fragments/food.json": "a1f73c8170932d6b3192e9cd506686d516d23d30",
    "preparedness/sources/fragments/hist-food.json": "d10628342fea5f177a8d1be00dd906d0c9c7850e",
}
BLOBS = {
    "pemmican-and-dried-meats": ("0b3319cc85ea2bc6d069b46d13a40e12ddbd5bc5", "1febc8929f8b90c81a3fcef1e46a2811778b7e06"),
    "pioneer-travel-rations": ("058c90b763d8cd6dec0731a7b0a9cee4dd5a57c7", "a658481d828dc4c5ba85f296adbfbee0514f0611"),
}


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def read_git(repo, commit, path):
    if not SHA.fullmatch(commit) or not path.startswith("preparedness/") or ".." in path.split("/"):
        raise ValueError("unsafe Git commit or file path")
    return subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"],
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def source_tokens(raw):
    data = raw.decode("utf-8", errors="strict")
    found = CITE.findall(data)
    if data.count("{{cite:") != len(found) or data.count("{{cite") != len(found):
        raise ValueError("malformed source citation marker")
    return found


def review_contexts(raw, limit=320):
    out = []
    for line_no, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        for m in CITE.finditer(line):
            if m.group(1) == OLD:
                start, end = max(0, m.start() - limit // 2), min(len(line), m.end() + limit // 2)
                excerpt = re.sub(r"<[^>]+>", " ", line[start:end])
                out.append({"line": line_no, "excerpt": " ".join(html.unescape(excerpt).split())[:limit]})
    return out


def assess_article(pinned, upstream, expected, total):
    a, b = source_tokens(pinned), source_tokens(upstream)
    if len(a) != total or len(b) != total:
        raise ValueError("citation occurrence count has changed")
    if a.count(OLD) != expected or b.count(NEW) < expected:
        raise ValueError("source alias count is not the frozen eight-occurrence docket")
    if OLD in b:
        raise ValueError("upstream retains a partly migrated source id")
    if [NEW if tok == OLD else tok for tok in a] != b:
        raise ValueError("an unrelated citation identity changed")
    expected_text = pinned.decode("utf-8").replace("{{cite:" + OLD + "}}", "{{cite:" + NEW + "}}")
    if upstream.decode("utf-8").replace("\r\n", "\n") != expected_text.replace("\r\n", "\n"):
        raise ValueError("reading text or markup changed beyond source-id substitution or CRLF-only normalization")
    details = review_contexts(pinned)
    if len(details) != expected:
        raise ValueError("context docket is incomplete")
    return {"substitutions": expected, "citations": total, "contexts": details, "eol_only_variation": upstream.decode("utf-8") != expected_text,
            "decision": "PENDING_HUMAN_SOURCE_REVIEW"}


def canon_for_grouping(url):
    # Used only to GROUP possible aliases for human review, never to approve equivalence.
    if not isinstance(url, str) or not url.startswith("https://nchfp.uga.edu/"):
        raise ValueError("unexpected jerky authority URL")
    if url.rstrip("/") != "https://nchfp.uga.edu/how/dry/recipes/jerky":
        raise ValueError("source points to a different path")
    return url.rstrip("/")


def review_sources(source_docs):
    rows = {}
    for origin, (path, sid) in {
        "base": ("preparedness/sources/register.json", NEW),
        "food": ("preparedness/sources/fragments/food.json", NEW),
        "hist-food": ("preparedness/sources/fragments/hist-food.json", OLD),
    }.items():
        if path not in source_docs:
            raise ValueError("missing original source register")
        doc = json.loads(source_docs[path].decode("utf-8"))
        records = doc.get("sources")
        if not isinstance(records, list):
            raise ValueError("source register has no source array")
        matches = [r for r in records if r.get("id") == sid]
        if len(matches) != 1 or sum(r.get("id") == sid for r in records) != 1:
            raise ValueError("missing or duplicated source identifier")
        r = matches[0]
        if r.get("human_link_check") is not False:
            raise ValueError("source record contains unexpected verification status")
        canon_for_grouping(r.get("url"))
        rows[origin] = {key: r.get(key) for key in ("id", "url", "title", "publisher", "supports", "notes", "verified_on", "human_link_check")}
    if len({json.dumps(row, sort_keys=True) for row in rows.values()}) != 3:
        raise ValueError("original source variants unexpectedly collapsed")
    if not rows["hist-food"].get("supports") or not rows["food"].get("supports"):
        raise ValueError("missing author-specific supporting reading")
    if rows["base"].get("supports") is not None:
        raise ValueError("original base placeholder's reading unexpectedly changed")
    return {"origins": rows, "canonical_group_only": canon_for_grouping(rows["base"]["url"]),
            "same_url_is_not_same_evidence": True,
            "review": "PENDING_INDEPENDENT_HUMAN_SOURCE_AND_FOOD_SAFETY_REVIEW"}


def run(repo, read=read_git):
    dossier = {"schema": "fv-preparedness-r152-v1", "candidate_commit": CANDIDATE,
               "upstream_commit": UPSTREAM, "decision": "DRAFT_HARD_HOLD",
               "qualified_food_safety_approval": False, "qd_pass": False,
               "articles": {}, "source_variants": None,
               "release_authorized": False}
    for slug, (count, total) in BODIES.items():
        path = f"preparedness/content/articles/{slug}.body.html"
        a, b = read(repo, CANDIDATE, path), read(repo, UPSTREAM, path)
        if (git_blob(a), git_blob(b)) != BLOBS[slug]:
            raise ValueError(f"unrecognized Git body blob: {slug}")
        dossier["articles"][slug] = assess_article(a, b, count, total)
    original_docs = {}
    for path, expected_blob in SOURCES.items():
        raw = read(repo, CANDIDATE, path)
        if git_blob(raw) != expected_blob:
            raise ValueError("original source provenance changed: " + path)
        original_docs[path] = raw
    dossier["source_variants"] = review_sources(original_docs)
    if sum(row["substitutions"] for row in dossier["articles"].values()) != 8:
        raise ValueError("incomplete eight-occurrence source substitution docket")
    return dossier


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, default=Path("."))
    p.add_argument("--report", type=Path, default=None,
                   help="optional local reviewer JSON outside the repository (no automatic output)")
    args = p.parse_args(argv)
    try:
        result = run(args.repo)
        if args.report:
            if args.report.exists() or args.report.resolve().is_relative_to(args.repo.resolve()):
                raise ValueError("refuse to overwrite any file or write into repository")
            args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"decision": "DRAFT_HARD_HOLD", "article_substitutions": 8,
                          "source_variants": 3, "qualification": "PENDING"}, sort_keys=True))
    except (ValueError, OSError, subprocess.SubprocessError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"decision": "INVALID_HARD_HOLD", "error": str(exc)}))
    return 2  # Never signal human approval or a release PASS.


if __name__ == "__main__":
    raise SystemExit(main())

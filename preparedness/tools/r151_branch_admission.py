#!/usr/bin/env python3
"""Read-only R151 three-way contributor drift gate. Structural integrity is never QD/safety approval.

Run in an authenticated complete git checkout. The frozen candidate is not changed.
No network, WordPress, checkout, push, source remapping or writes are performed.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
WORD = re.compile(r"[A-Za-z0-9_’-]+")


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def normalize_eol(data):
    # Normalize line ending only: never collapse spaces, HTML or citations.
    return data.replace(b"\r\n", b"\n")


def source_tokens(data):
    value = data.decode("utf-8", errors="strict")
    tokens = CITE.findall(value)
    if value.count("{{cite:") != len(tokens):
        raise ValueError("malformed or unclosed citation token")
    return tokens


def word_count(data):
    value = CITE.sub(" ", data.decode("utf-8"))
    value = re.sub(r"<[^>]*>", " ", value)
    return len(WORD.findall(value))


def read_git(repo, ref, path):
    if not SHA.fullmatch(ref):
        raise ValueError("ref must be an exact 40-hex commit")
    if not path.startswith("preparedness/") or ".." in path.split("/"):
        raise ValueError("unsafe git object path")
    return subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{path}"],
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def git_query(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()


def require_blob(repo, commit, path, expected_blob):
    if not SHA.fullmatch(expected_blob):
        raise ValueError("invalid expected Git blob identity")
    raw = read_git(repo, commit, path)
    if git_blob(raw) != expected_blob:
        raise ValueError(f"original Git blob changed: {path}@{commit}")
    return raw


def classify(candidate, pinned, upstream, expected):
    if expected == "UPSTREAM_EXACT" and candidate == upstream and pinned != upstream:
        return expected
    if (expected == "UPSTREAM_EOL_ONLY" and candidate != upstream
            and normalize_eol(candidate) == normalize_eol(upstream) and pinned != upstream):
        return expected
    if expected == "PINNED_SUBSTITUTION_PENDING" and candidate == pinned and candidate != upstream:
        old, new = source_tokens(pinned), source_tokens(upstream)
        replacement = ["nchfp-jerky" if v == "hist-food-nchfp-jerky" else v for v in old]
        if new == replacement and len(old) == len(new) and old != new:
            return expected
    raise ValueError("three-way drift is different from pinned review custody")


def check_row(row, fetch):
    slug = row["slug"]
    if not SLUG.fullmatch(slug):
        raise ValueError("unsafe article slug")
    path = f"preparedness/content/articles/{slug}.body.html"
    blobs = {}
    for key in ("pinned", "upstream", "candidate"):
        v = row[key]
        raw = fetch(v["commit"], path)
        if git_blob(raw) != v["blob"]:
            raise ValueError(f"{slug} {key} Git blob mismatch")
        if len(source_tokens(raw)) != v["citations"] or word_count(raw) != v["words"]:
            raise ValueError(f"{slug} {key} citation/reading-depth mismatch")
        blobs[key] = raw
    state = classify(blobs["candidate"], blobs["pinned"], blobs["upstream"], row["resolution"])
    return {"slug": slug, "resolution": state, "article_words": word_count(blobs["candidate"]),
            "article_citations": len(source_tokens(blobs["candidate"])), "review": "PENDING"}


def check_manifest(m):
    if m.get("schema") != "fv-preparedness-r151-v1" or m.get("decision") != "DRAFT_HARD_HOLD":
        raise ValueError("unexpected release state or schema")
    if m.get("qualified_safety_review") is not False or m.get("qd_pass") is not False:
        raise ValueError("forged human safety or QD approval")
    if not SHA.fullmatch(m.get("candidate_commit", "")):
        raise ValueError("missing exact candidate head")
    rows = m.get("articles")
    if not isinstance(rows, list) or len(rows) != 7:
        raise ValueError("expected precisely seven changed historical article identities")
    slugs = [r.get("slug") for r in rows]
    if len(set(slugs)) != 7:
        raise ValueError("duplicate article identity")
    allowed = {"UPSTREAM_EXACT": 1, "UPSTREAM_EOL_ONLY": 4, "PINNED_SUBSTITUTION_PENDING": 2}
    actual = {k: sum(r.get("resolution") == k for r in rows) for k in allowed}
    if actual != allowed:
        raise ValueError(f"expected admission buckets {allowed}, received {actual}")
    if set(m.get("source_head_commits", {})) != {"start", "shelter", "food", "health", "hist-food", "hist-home", "hist-field"}:
        raise ValueError("seven contributor crosswalk pins required")
    for ref in m["source_head_commits"].values():
        if not SHA.fullmatch(ref):
            raise ValueError("invalid source pin")
    metadata_blobs = m.get("metadata_blobs")
    if not isinstance(metadata_blobs, dict) or len(metadata_blobs) != 35:
        raise ValueError("all 35 original metadata Git blobs must be pinned")
    if any(not SLUG.fullmatch(slug) or not SHA.fullmatch(blob)
           for slug, blob in metadata_blobs.items()):
        raise ValueError("malformed metadata identity/blob custody")
    for row in rows:
        if row.get("origin") not in m["source_head_commits"] or row["pinned"]["commit"] != m["source_head_commits"][row["origin"]]:
            raise ValueError("incorrect frozen source provenance")
        for part in ("pinned", "upstream", "candidate"):
            d = row[part]
            if not SHA.fullmatch(d.get("commit", "")) or not SHA.fullmatch(d.get("blob", "")):
                raise ValueError("invalid commit / blob identity")
            if not isinstance(d.get("words"), int) or d["words"] < 1500:
                raise ValueError("reading-depth floor violated")
            if not isinstance(d.get("citations"), int) or d["citations"] < 20:
                raise ValueError("citation-count floor violated")
            if part == "candidate" and d["commit"] != m["candidate_commit"]:
                raise ValueError("candidate head not pinned")
    return True


def audit(repo, m):
    check_manifest(m)
    candidate = m["candidate_commit"]
    crosswalk = json.loads(require_blob(repo, candidate, "preparedness/sources/crosswalk.json", m["crosswalk_blob"]))
    if crosswalk["source_head_commits"] != m["source_head_commits"] or "UNRESOLVED" not in crosswalk["status"]:
        raise ValueError("frozen crosswalk or human review state changed")
    tree = git_query(repo, "ls-tree", "-r", "--name-only", candidate, "--", "preparedness/content/articles/").splitlines()
    base = "preparedness/content/articles/"
    bodies = {x[len(base):-len(".body.html")] for x in tree if x.startswith(base) and x.endswith(".body.html")}
    metas = {x[len(base):-len(".meta.json")] for x in tree if x.startswith(base) and x.endswith(".meta.json")}
    if len(bodies) != 35 or bodies != metas or set(m["metadata_blobs"]) != metas:
        raise ValueError("35-body/35-meta article census failed")
    for slug in sorted(metas):
        if not SLUG.fullmatch(slug):
            raise ValueError("invalid article census identity")
        meta = json.loads(require_blob(repo, candidate, f"{base}{slug}.meta.json", m["metadata_blobs"][slug]))
        if meta.get("slug") != slug or meta.get("status", {}).get("publish") != "draft":
            raise ValueError(f"article not draft: {slug}")
        if meta.get("safety_review", {}).get("state") not in ("pending", "not-required", "approved"):
            raise ValueError(f"unexpected human safety review state: {slug}")
    for origin, branch in m["branches"].items():
        local = git_query(repo, "rev-parse", "--verify", f"refs/remotes/origin/{branch}")
        if local != m["branch_heads"][origin]:
            raise ValueError(f"moving or unfetched contributor ref: {branch}")
    result = [check_row(row, lambda ref, path: read_git(repo, ref, path)) for row in m["articles"]]
    return {"status": "DRAFT_HARD_HOLD", "articles_examined": len(result), "articles_total": 35,
            "results": result, "human_source_review": "PENDING", "medical_safety": "NOT_APPROVED",
            "independent_qd": "NOT_APPROVED", "publication": "PROHIBITED"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        m = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = audit(args.repo, m)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "INVALID_HOLD", "reason": str(exc), "publication": "PROHIBITED"}))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    # Even a structurally correct review artifact cannot clear safety or QD.
    return 2


if __name__ == "__main__":
    sys.exit(main())

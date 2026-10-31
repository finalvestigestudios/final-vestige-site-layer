#!/usr/bin/env python3
"""R16: attest and stage exactly two PR157 wording repairs, never source/taxonomy rollback.

Inputs must be the real R15-integrated 35-article checkout plus the recorded,
unreviewed PR157 manifest. This writes review-only files outside the checkout.
HOLD is unconditional: no claimed fact, medical, source, QD, or CMS approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re
import sys

BASE_SHA = "2492be67054ca1228752df64368ad75dec8dc586"
QA_SHA = "7d1ae6b8ef93d10cfb6810987672360885e9c1aa"
FOOD_SHA = "e9cd7766dac59d47ab467d8945269b9146c2aef5"
EXPECTED = {
    "preparedness/content/articles/household-emergency-plan.body.html":
        ("8ca5c261dba56eeaf79c445332381a74867233de",
         "6407a31a882211e62c00f4e07ec7dc4d5abf99c6", "li"),
    "preparedness/content/articles/three-day-kit.body.html":
        ("ef5463ca668166766ca3d868908bc0bcb6040a23",
         "f578cdbae602c1ad58a9237c8dea0fd74c99f7da", "p"),
}
PROTECTED = {
    "preparedness/taxonomy.json": "eea601e53e16e36cd4fc890876bc249b39632370",
    "preparedness/sources/fragments/start.json": "29574c328cbab0548e6e5d4a026694857d56b6b4",
}
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
LINK = re.compile(r"\{\{link:([^}]+)\}\}")
FORBIDDEN = re.compile(r"QD\s*PASS|safety[\s_-]*approved|medically\s+safe|approved\s+for\s+publish", re.I)


class HoldError(ValueError):
    pass


def demand(condition, message):
    if not condition:
        raise HoldError(message)


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def manifest_check(m):
    demand(type(m) is dict, "manifest must be a JSON object")
    demand(set(m) == {"schema_version", "issue", "base_commit", "qa_pr", "qa_head",
                      "food_fixture_pr", "food_fixture_head", "release_state",
                      "may_publish", "review_state", "human_claim_checks",
                      "qualified_safety_clearance", "source_changes_allowed",
                      "protected_blobs", "edits"}, "unknown/missing manifest fields")
    demand(type(m["schema_version"]) is int and m["schema_version"] == 1 and
           type(m["issue"]) is int and m["issue"] == 136, "invalid schema / issue")
    demand(m["base_commit"] == BASE_SHA and m["qa_head"] == QA_SHA and
           m["food_fixture_head"] == FOOD_SHA, "stale QA or integration SHA")
    demand(type(m["qa_pr"]) is int and m["qa_pr"] == 157 and
           type(m["food_fixture_pr"]) is int and m["food_fixture_pr"] == 169,
           "wrong independent QA references")
    demand(m["release_state"] == "HOLD" and m["may_publish"] is False and
           m["review_state"] == "PENDING_INDEPENDENT_SAFETY_AND_SOURCE_REVIEW",
           "review/publish state escalated")
    demand(type(m["human_claim_checks"]) is int and m["human_claim_checks"] == 0 and
           m["qualified_safety_clearance"] is False and
           m["source_changes_allowed"] is False, "unearned verification/approval")
    demand(m["protected_blobs"] == PROTECTED, "taxonomy or source identity changed")
    edits = m["edits"]
    demand(type(edits) is list and len(edits) == 2, "exactly two candidate edits required")
    seen = set()
    for edit in edits:
        demand(type(edit) is dict and set(edit) ==
               {"path", "integrated_blob_sha", "qa_blob_sha", "old_line",
                "new_line", "reason", "review_status"}, "invalid edit fields")
        path = edit["path"]
        demand(type(path) is str and path in EXPECTED and path not in seen,
               "unknown/repeated article edit")
        seen.add(path)
        original_sha, qa_sha, tag = EXPECTED[path]
        demand(edit["integrated_blob_sha"] == original_sha and
               edit["qa_blob_sha"] == qa_sha, "unattested contributor or QA blob")
        demand(edit["review_status"] == "UNREVIEWED_QA_CANDIDATE", "QA safety falsely approved")
        reason = edit["reason"]
        demand(type(reason) is str and 15 <= len(reason) <= 500 and
               not FORBIDDEN.search(reason), "unreviewed or unsafe edit rationale")
        before, after = edit["old_line"], edit["new_line"]
        for line in (before, after):
            demand(type(line) is str and 40 < len(line) < 5000 and
                   not any(ch in line for ch in "\r\n\0") and
                   line.startswith("<" + tag + ">") and line.endswith("</" + tag + ">"),
                   "not a complete one-line HTML element")
            demand(not FORBIDDEN.search(line), "spurious content approval")
            demand("{{" not in CITE.sub("", LINK.sub("", line)), "unknown template tokens")
        demand(before != after, "no actual changed copy")
        demand(Counter(CITE.findall(before)) == Counter(CITE.findall(after)),
               "citation identity or occurrence changed")
        demand(Counter(LINK.findall(before)) == Counter(LINK.findall(after)),
               "article links changed")
        demand(len(re.findall(r"<span\b", before)) == len(re.findall(r"<span\b", after)),
               "safety labels changed")
        demand(not re.search(r"https?://|href\s*=|src\s*=|onload\s*=|onerror\s*=", after, re.I),
               "unreviewed URL or HTML attribute")
        if tag == "li":
            demand("Keep the household electricity on" in after and
                   "main breaker" in after.lower(), "missing household breaker caution")
        else:
            demand("pharmacist or prescriber" in after.lower() and
                   "product-specific" in after.lower(), "missing medication-specific caution")
    demand(seen == set(EXPECTED), "incomplete proposed repairs")
    return edits


def read_bound(root, relative, max_bytes=250000):
    path = root / relative
    demand(root.is_dir() and not root.is_symlink() and
           path.is_file() and not path.is_symlink() and
           path.resolve().is_relative_to(root.resolve()), "missing/linked/outside source")
    data = path.read_bytes()
    demand(0 < len(data) <= max_bytes, "source length outside bound")
    return data


def word_count(markup):
    return len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b",
                          html.unescape(re.sub(r"<[^>]*>", " ", markup))))


def exact_transplant(content, edit):
    before, after = edit["old_line"], edit["new_line"]
    demand(type(content) is str and content.count(before) == 1,
           "missing/repeated exact original wording")
    lines = content.splitlines(keepends=True)
    indexes = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == before]
    demand(len(indexes) == 1, "repair not aligned to one complete source line")
    i = indexes[0]
    suffix = lines[i][len(before):]
    demand(suffix in ("", "\n", "\r\n"), "unsupported line delimiter")
    lines[i] = after + suffix
    updated = "".join(lines)
    demand(Counter(CITE.findall(content)) == Counter(CITE.findall(updated)) and
           Counter(LINK.findall(content)) == Counter(LINK.findall(updated)),
           "citation/link conservation failed")
    demand(word_count(content) >= 1800 and word_count(updated) >= 1800 and
           word_count(updated) >= 0.95 * word_count(content),
           "reading depth changed materially")
    demand(updated.replace(after, before, 1) == content,
           "unapproved collateral article mutation")
    return updated


def stage(root, out, manifest):
    edits = manifest_check(manifest)
    root = root.resolve(strict=True)
    out = out.expanduser().absolute()
    demand(not out.exists() and not out.is_symlink() and
           not out.resolve().is_relative_to(root), "review destination unsafe or preexisting")
    for path, sha in PROTECTED.items():
        demand(git_blob(read_bound(root, path)) == sha,
               "stale taxonomy or contributor-specific source evidence: " + path)
    article_dir = root / "preparedness/content/articles"
    bodies = sorted(article_dir.glob("*.body.html"))
    metas = sorted(article_dir.glob("*.meta.json"))
    body_names = {p.name.removesuffix(".body.html") for p in bodies}
    meta_names = {p.name.removesuffix(".meta.json") for p in metas}
    demand(len(bodies) == len(metas) == 35 and body_names == meta_names,
           "original 35 article pairs changed")
    taxonomy = json.loads(read_bound(root, "preparedness/taxonomy.json").decode("utf-8"))
    slate = taxonomy.get("slate")
    demand(type(slate) is list and len(slate) == 35 and
           {s.get("slug") for s in slate if type(s) is dict} == body_names,
           "article URL slate changed")
    copies = []
    for edit in edits:
        raw = read_bound(root, edit["path"])
        demand(git_blob(raw) == edit["integrated_blob_sha"],
               "integrated article blob changed: " + edit["path"])
        old = raw.decode("utf-8", errors="strict")
        new_bytes = exact_transplant(old, edit).encode("utf-8")
        copies.append((Path(edit["path"]).name, new_bytes, {
            "article_path": edit["path"], "original_git_blob": edit["integrated_blob_sha"],
            "qa_git_blob": edit["qa_blob_sha"],
            "review_copy_sha256": hashlib.sha256(new_bytes).hexdigest(),
            "citation_occurrences": len(CITE.findall(old)),
            "word_count_before": word_count(old),
            "word_count_candidate": word_count(new_bytes.decode("utf-8")),
            "review_state": "UNREVIEWED_QA_CANDIDATE"}))
    receipt = {
        "schema_version": 1, "issue": 136, "baseline": BASE_SHA,
        "qa_pr": 157, "qa_head": QA_SHA, "food_fixture_pr": 169,
        "release_state": "HOLD", "may_publish": False,
        "human_claim_checks": 0, "qualified_safety_clearance": False,
        "source_changes_merged": False, "taxonomy_changes_merged": False,
        "total_articles_preserved": 35,
        "review_copies": [row[2] for row in copies],
        "notice": "Reviewer-only candidate texts, not publishable WordPress exports or verified safety guidance."}
    out.mkdir(mode=0o700, parents=False)
    for name, data, _ in copies:
        with (out / name).open("xb") as target:
            target.write(data)
    (out / "HOLD-review-receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--review-out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        print(json.dumps(stage(args.repo_root, args.review_out, manifest), indent=2))
        return 0  # Success in preparing review copies; publication remains HOLD.
    except (HoldError, OSError, ValueError, UnicodeError, TypeError) as exc:
        print("INVALID / HOLD: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

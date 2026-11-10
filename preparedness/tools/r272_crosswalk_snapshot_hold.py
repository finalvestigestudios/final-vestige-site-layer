#!/usr/bin/env python3
"""R272: frozen eight-origin source crosswalk custody, NEVER a release approval.

Source identity is (origin, row index, ID, exact URL). A terminal-path slash
may group reviews but must never silently merge URLs, citations or reading scopes.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

HOLD = "DRAFT_HARD_HOLD"
INVALID = "INVALID_HARD_HOLD"
CROSSWALK = "sources/crosswalk.json"
CROSSWALK_BLOB = "d62e493a67dedd23e04cfdf3cce762ef933c6bf9"
ORIGINS = (
    ("base", "sources/register.json", "b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77", 34),
    ("food", "sources/fragments/food.json", "a1f73c8170932d6b3192e9cd506686d516d23d30", 30),
    ("health", "sources/fragments/health.json", "cc29c439372b9d49debf78e63020ffe4d62baeb8", 21),
    ("hist-field", "sources/fragments/hist-field.json", "3dafa9425f3829c0be2e6fea00889aff95124031", 28),
    ("hist-food", "sources/fragments/hist-food.json", "d10628342fea5f177a8d1be00dd906d0c9c7850e", 28),
    ("hist-home", "sources/fragments/hist-home.json", "8d85fd868508c5caba14a839d119d55f31f14f72", 29),
    ("shelter", "sources/fragments/shelter.json", "2a3f1a7ddeab2782add875be1e0e378513504aa1", 45),
    ("start", "sources/fragments/start.json", "96140d6d1872588e5d20d9052445c9157e88934d", 29),
)
CENSUS = {"rows": 244, "exact_urls": 202, "alias_urls": 201,
          "shared_groups": 32, "duplicate_id_groups": 15,
          "alias_variants": 1, "article_origins": 36}
FLAGS = ("independent_QD_PASS", "safety_approved", "medical_safety_verified",
         "may_publish", "may_merge", "merchant_offer_verified")


def blob(data: bytes) -> str:
    if type(data) is not bytes:
        raise ValueError("expected unmodified file bytes")
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\\0" + data).hexdigest()


def decode(data: bytes):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("duplicate JSON key: " + key)
            out[key] = value
        return out
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def alias(url: str) -> str:
    if not isinstance(url, str) or url != url.strip():
        raise ValueError("invalid URL")
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.netloc or parts.username or parts.password:
        raise ValueError("not a supported https source URL")
    return urlunsplit((parts.scheme, parts.netloc,
                       (parts.path or "/").rstrip("/") or "/", parts.query, parts.fragment))


def inspect(x: dict, origins: dict, census=None):
    """Validate all 244 original readings and 32 review groups, without rewrites."""
    census = CENSUS if census is None else census
    if (x.get("schema_version") != 1
        or x.get("status") != "DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED"
        or "UNREVIEWED" not in x.get("warning", "")):
        raise ValueError("crosswalk approval/identity status drift")
    files = x["source_files"]
    if len(files) != len(origins) or len(set(f["origin"] for f in files)) != len(files):
        raise ValueError("origin roster modified")
    rows = []
    for entry in files:
        origin = entry["origin"]
        if origin not in origins or not re.fullmatch("[0-9a-f]{40}", entry["git_blob_sha"]):
            raise ValueError("unknown origin or invalid blob identity")
        source_rows = origins[origin]
        if entry["count"] != len(source_rows):
            raise ValueError("origin reading-count change")
        for index, source in enumerate(source_rows):
            if not isinstance(source.get("id"), str) or not source["id"]:
                raise ValueError("missing original source ID")
            alias(source["url"])
            rows.append((origin, entry["path"], index, source))
    exact, grouped, by_id = defaultdict(list), defaultdict(list), defaultdict(list)
    for entry in rows:
        origin, path, index, src = entry
        exact[src["url"]].append(entry)
        grouped[alias(src["url"])].append(entry)
        by_id[src["id"]].append(entry)
    shared = {k: v for k, v in grouped.items() if len(v) > 1}
    groups = x["groups"]
    if len(groups) != len(shared):
        raise ValueError("missing or invented shared-URL review groups")
    seen, alias_count = set(), 0
    for group in groups:
        url = group["url"]
        if url != alias(url) or url in seen or url not in shared:
            raise ValueError("unrecognized canonical shared-source group")
        seen.add(url)
        if (group.get("canonical_url") != url
            or group.get("review_status") != "pending-human-source-and-reading-scope-review"
            or group.get("reviewer", "__MISSING__") is not None
            or group.get("reviewed_on", "__MISSING__") is not None):
            raise ValueError("unauthorized group adjudication")
        want = {(o, p, i): src for o, p, i, src in shared[url]}
        got = {}
        for item in group["variants"]:
            identity = (item["origin"], item["source_file"], item["row_index"])
            if identity in got or identity not in want or item["source"] != want[identity]:
                raise ValueError("variant lost, duplicated, or changed reading scope")
            if alias(item["source"]["url"]) != url:
                raise ValueError("invalid terminal-slash review equivalent")
            alias_count += item["source"]["url"] != url
            got[identity] = item["source"]
        if got != want:
            raise ValueError("source variant omitted from review")
        expected_ids = sorted((o, i, src["id"]) for o, p, i, src in shared[url])
        actual_ids = sorted((it["origin"], it["row_index"], it["id"]) for it in group["identities"])
        if actual_ids != expected_ids:
            raise ValueError("source identity joined across distinct reading scopes")
    if seen != set(shared):
        raise ValueError("shared-source docket incomplete")
    candidate = x["candidate_reconciliation_20261104"]
    if candidate.get("status") != "DRAFT_UNREVIEWED_HOLD":
        raise ValueError("unapproved candidate status changed")
    if any(candidate.get(flag) is not False for flag in FLAGS):
        raise ValueError("false source, medical, commerce or publication approval")
    if any(k in x for k in FLAGS + ("publication_authorized", "independent_qd_pass")):
        raise ValueError("top-level approval flag added")
    heads = x["source_head_commits"]
    if set(heads) != set(origins) or not all(re.fullmatch("[0-9a-f]{40}", head) for head in heads.values()):
        raise ValueError("frozen seven-contributor heads missing")
    article_origins = x["article_origins"]
    if any(origin not in origins for origin in article_origins.values()):
        raise ValueError("article reading origin missing")
    actual = {"rows": len(rows), "exact_urls": len(exact), "alias_urls": len(grouped),
              "shared_groups": len(shared),
              "duplicate_id_groups": sum(len(items) > 1 for items in by_id.values()),
              "alias_variants": alias_count, "article_origins": len(article_origins)}
    if actual != census:
        raise ValueError("frozen exact/alias census drift: " + repr(actual))
    if (x.get("raw_source_rows") != actual["rows"]
        or x.get("unique_source_urls") != actual["exact_urls"]
        or x.get("duplicate_url_groups") != actual["shared_groups"]
        or x.get("duplicate_id_groups") != actual["duplicate_id_groups"]):
        raise ValueError("advertised source census inconsistent with actual rows")
    return {"state": HOLD, "counts": actual, "unreviewed_groups": len(shared),
            "source_snapshot_parity": True, "independent_qd_pass": False,
            "medical_safety_verified": False, "publication_authorized": False}


def audit(root: Path, read=None) -> dict:
    """No network, source writes, QD PASS, render, commerce or public mutation."""
    read = read or (lambda root, rel: (root / rel).read_bytes())
    out = {"state": INVALID, "errors": [], "independent_qd_pass": False,
           "publication_authorized": False}
    try:
        raw = read(root, CROSSWALK)
        if blob(raw) != CROSSWALK_BLOB:
            raise ValueError("authenticated historical crosswalk changed")
        x = decode(raw)
        manifest = {(it["origin"], it["path"], it["git_blob_sha"], it["count"])
                    for it in x["source_files"]}
        expected = {(o, "preparedness/" + path, sha, count) for o, path, sha, count in ORIGINS}
        if manifest != expected:
            raise ValueError("origin file/commit/source roster drift")
        originals = {}
        for origin, path, sha, count in ORIGINS:
            data = read(root, path)
            if blob(data) != sha:
                raise ValueError("unreviewed origin snapshot change: " + origin)
            originals[origin] = decode(data)["sources"]
            if len(originals[origin]) != count:
                raise ValueError("origin source row count changed: " + origin)
        out.update(inspect(x, originals))
    except (ValueError, KeyError, TypeError, AttributeError, OSError, UnicodeError) as exc:
        out["errors"].append(str(exc))
    return out


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, type=Path)
    args = p.parse_args()
    result = audit(args.root)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(2 if result["state"] == HOLD else 3)

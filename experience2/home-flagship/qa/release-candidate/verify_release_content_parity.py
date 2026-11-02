#!/usr/bin/env python3
"""Fail-closed, offline #604 production -> #609 WordPress source-custody contract.

The fixture began as proposed page-6 block PR #604 but is explicitly revised on this review branch,
NOT a production WordPress read, deployment instruction or rights clearance.
Only the seven-chapter editorial interior is expected to match byte-for-byte:
WordPress retains its single native header/main/footer and excludes the
standalone design-study banner. Executed inside exact-head isolated staging.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HOME = Path("experience2/home-flagship")
SOURCE = HOME / "index.html"
RELEASE_FIXTURE = HOME / "qa/release-candidate/fixtures/proposed-production-block-pr604.html"
PRODUCTION_RELEASE_HEAD = "5f87f1b0a48ed2f17ecca49a60c44a482ca530de"  # historical origin only, not current blob
PRODUCTION_SOURCE_BLOB = "978e25e69cd6b077863515158a9e696a5c4e9a8c"
PRODUCTION_BLOCK_BLOB = "ebe62f4b145fddf6925efc1b8502abef4a2177a8"
OPENING = '<section class="fv-hf__opening"'
CLOSING = "</section>"
RIGHTS = {
    "apollo": "NASA does not endorse Final Vestige or any product or service.",
    "franklin": "The displayed scan is the Wikimedia Commons file marked public domain",
    "malbone": "From The New York Public Library. Reuse rights for this exact digital capture are pending verification; a 1903 map date alone does not establish image-use clearance.",
}
MIND_NOTICE = "this section makes no health, performance or product claims"

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()

def chapter_interior(source: str, *, inline_block: bool) -> str:
    # Intentionally strict and deterministic: changing the wrapper contract
    # requires a new review, not a permissive HTML normalization that could
    # erase attribution or alter semantic content.
    end_marker = "<style>" if inline_block else "</main>"
    end = source.find(end_marker)
    if end < 0:
        raise ValueError("RELEASE_PARITY_WRAPPER_MISSING")
    first = source.find(OPENING)
    last = source.rfind(CLOSING, 0, end)
    if first < 0 or last < first or source.find(OPENING, first + 1) != -1:
        raise ValueError("RELEASE_PARITY_CHAPTER_BOUNDARY")
    interior = source[first:last + len(CLOSING)]
    if not interior or interior.count('class="fv-hf__opening"') != 1:
        raise ValueError("RELEASE_PARITY_EMPTY_OR_DUPLICATED")
    return interior

def compare_interiors(source: str, production: str) -> dict:
    a = chapter_interior(source, inline_block=False)
    b = chapter_interior(production, inline_block=True)
    if a != b:
        raise ValueError("RELEASE_PARITY_CHAPTER_BYTES_DIFFER")
    # The former item-level public-domain assertion must remain prohibited
    # even if someone edits BOTH staging and proposed production together.
    if "NYPL believes this item is in the public domain under United States law." in a:
        raise ValueError("RELEASE_PARITY_UNVERIFIED_NYPL_RIGHTS_CLAIM")
    # The 1903 record remains CATALOGED but its exact digital capture is NOT
    # licensed for display: refuse silent image reintroduction even if a
    # contributor edits both editorial sources to match.
    malbone_figure = a.split('data-fv-case="malbone"', 1)[-1].split(
        '<div class="fv-hf__case-body">', 1)[0]
    if (a.count('data-fv-case="malbone"') != 1
            or 'fv-hf__source-plate' not in malbone_figure
            or '<img' in malbone_figure
            or 'edit-017-v02-nypl-5003296-original.jpg' in a):
        raise ValueError("RELEASE_PARITY_NYPL_UNCLEARED_IMAGE_REPRODUCTION")
    # Source and proposed WordPress block must retain a real image even when
    # JavaScript is disabled. The script-enabled <img> remains lazy; the
    # <noscript> sibling is eager, decorative (avoids duplicate announced alt),
    # and references the SAME reviewed image URL. Neither branch may add NYPL.
    normal = re.findall(r'<img\b[^>]*\bdata-fv-archive-img>', a)
    fallback = re.findall(r'<noscript>\s*(<img\b[^>]*>)\s*</noscript>', a)
    attr = lambda tag, key: (re.search(r'\b'+key+r'="([^"]*)"', tag) or [None, None])[1]
    if (len(normal) != 2 or len(fallback) != 2
            or a.count('<noscript>') != 2
            or a.count('data-fv-noscript-archive') != 2):
        raise ValueError("RELEASE_PARITY_NOJS_ARCHIVE_FALLBACK_UNSAFE")
    for normal_tag, fallback_tag in zip(normal, fallback):
        if (attr(normal_tag, 'src') != attr(fallback_tag, 'src')
                or attr(normal_tag, 'loading') != 'lazy'
                or attr(fallback_tag, 'loading') != 'eager'
                or attr(fallback_tag, 'alt') != ''
                or attr(fallback_tag, 'role') != 'presentation'
                or attr(fallback_tag, 'aria-hidden') != 'true'
                or 'data-fv-noscript-archive' not in fallback_tag
                or 'data-fv-archive-img' in fallback_tag):
            raise ValueError("RELEASE_PARITY_NOJS_ARCHIVE_FALLBACK_UNSAFE")
    if 'data-fv-noscript-archive' in malbone_figure:
        raise ValueError("RELEASE_PARITY_NOJS_ARCHIVE_FALLBACK_UNSAFE")
    for case, text in RIGHTS.items():
        if a.count(text) != 1:
            raise ValueError("RELEASE_PARITY_RIGHTS_" + case.upper())
    # The case source drawer and evidence inquiry each link the official map.
    if a.count("https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0") != 2:
        raise ValueError("RELEASE_PARITY_NYPL_ORIGINAL_LINK")
    if a.count(MIND_NOTICE) != 1:
        raise ValueError("RELEASE_PARITY_MIND_DISCLOSURE")
    if "DESIGN CANDIDATE" in production or "DESIGN CANDIDATE" in a:
        raise ValueError("RELEASE_PARITY_STUDY_BANNER_LEAK")
    if '<div class="fv-hf fv-hf--wp alignfull" data-fv-home-flagship>' not in production:
        raise ValueError("RELEASE_PARITY_WORDPRESS_WRAPPER")
    if '<div class="fv-hf" data-fv-home-flagship>' not in source:
        raise ValueError("RELEASE_PARITY_STUDY_WRAPPER")
    return {
        "status": "CHAPTER_BYTES_AND_EDITORIAL_NOTICES_IDENTICAL",
        "historical_proposal_head": PRODUCTION_RELEASE_HEAD,
        "nypl_capture_rights": "UNVERIFIED_NOT_REPRODUCED",
        "chapter_sha256": hashlib.sha256(a.encode("utf-8")).hexdigest(),
        "chapter_characters": len(a),
        "attribution_notices": sorted(RIGHTS),
        "commercial_notice": "PRESENT",
        "wordpress_com_host_parity": "NOT_ESTABLISHED",
        "publication": "HOLD",
    }

def verify_bytes(source: bytes, production: bytes) -> dict:
    if git_blob(source) != PRODUCTION_SOURCE_BLOB:
        raise ValueError("RELEASE_PARITY_SOURCE_BLOB_MISMATCH")
    if git_blob(production) != PRODUCTION_BLOCK_BLOB:
        raise ValueError("RELEASE_PARITY_PROPOSED_BLOCK_BLOB_MISMATCH")
    return compare_interiors(source.decode("utf-8"), production.decode("utf-8"))

def verify_repo(repo: Path) -> dict:
    repo = repo.resolve(strict=True)
    for path in (SOURCE, RELEASE_FIXTURE):
        candidate = repo / path
        if candidate.is_symlink() or not candidate.is_file() or not candidate.resolve().is_relative_to(repo):
            raise ValueError("RELEASE_PARITY_UNSAFE_SOURCE")
    return verify_bytes((repo / SOURCE).read_bytes(), (repo / RELEASE_FIXTURE).read_bytes())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify_repo(args.repo), sort_keys=True))

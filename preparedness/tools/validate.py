#!/usr/bin/env python3
"""Editorial, safety-governance and accessibility gates for the Preparedness Archive.

Exit code 0 only when there are no errors. Warnings are printed but do not fail.
These checks cannot prove an article is *correct*. They enforce that it is traceable, labelled,
gated and structurally sound. Correctness still needs the human safety review recorded in each article's meta.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402
import evidence_freeze  # noqa: E402
import r122_reader_visible_citation_gate as reader_visible_citations  # noqa: E402

REQUIRED_META = ["n", "slug", "title", "h1", "dek", "description", "section", "track", "updated", "last_checked", "status", "safety_review"]
MIN_WORDS_CORNERSTONE = 1800
ALLOWED_KINDS = {"regulator", "extension", "nonprofit", "professional-body", "museum", "museum-study", "museum-object",
                 "archive", "primary-digitized", "scholarship", "journal"}
NONPROFIT_MARKERS = ("Red Cross", "Red Crescent", "Salvation Army", "Foundation", "Association", "Society")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BANNED = [
    (r"(?<!not )(?<!n't )(?<!never )\bguarantee[sd]?\b[^.]{0,40}\bsafe", "promises safety"),
    (r"\b100\s?%\s*safe\b", "claims 100% safe"),
    (r"\bancient secret", "'ancient secret' framing"),
    (r"\bdoomsday\b|\bcollapse is coming\b|\bSHTF\b", "fear-selling language"),
    (r"\bbuy now\b|\bact now\b!", "sales language"),
]
# Contrast pairs (foreground token, background token) that must reach WCAG AA for normal text (4.5:1)
CONTRAST_PAIRS = [
    ("--pa-text", "--pa-bg"), ("--pa-muted", "--pa-bg"), ("--pa-gold", "--pa-bg"), ("--pa-gold", "--pa-surface"),
    ("--pa-muted", "--pa-surface"), ("--pa-text", "--pa-surface-2"), ("--pa-muted", "--pa-surface-2"),
    ("--pa-ink", "--pa-paper"), ("--pa-ink-soft", "--pa-paper"),
    ("--pa-ok", "--pa-surface"), ("--pa-warn", "--pa-surface"), ("--pa-bad", "--pa-surface"), ("--pa-info", "--pa-surface"),
    ("--pa-warn", "--pa-surface-2"), ("--pa-info", "--pa-surface-2"), ("--pa-ok", "--pa-bg"),
]


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(fg: str, bg: str) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def css_tokens(css: str) -> dict[str, str]:
    return dict(re.findall(r"(--pa-[a-z0-9\-]+):\s*(#[0-9A-Fa-f]{6})\s*;", css))


def validate(lib: build.Library | None = None) -> tuple[list[str], list[str]]:
    lib = lib or build.Library()
    errors: list[str] = []
    warns: list[str] = []

    # Every source and 35+1 original article input is pinned to a Git blob.
    errors.extend(evidence_freeze.verify(lib))

    # --- full source provenance, repeated URL crosswalk and source safety ---
    # Inspect ALL fragment variants, not merely a winning global dictionary
    # entry. Different branches may have read only a catalogue or a PDF section.
    url_variants: dict[str, list[dict]] = {}
    alias_variants: dict[str, list[dict]] = {}
    raw_count = 0
    for sid, variants in lib.source_variants.items():
        for s in variants:
            raw_count += 1
            origin = s["_origin"]
            url = s["url"]
            url_variants.setdefault(url, []).append(s)
            alias_variants.setdefault(build.review_alias_key(url), []).append(s)
            tag = f"register:{sid}@{origin}"
            if not url.startswith("https://"):
                errors.append(f"{tag}: url must be https")
            if s.get("verified_on") and not DATE_RE.match(s["verified_on"]):
                errors.append(f"{tag}: bad verified_on")
            if s.get("verified_on") and not s.get("supports"):
                errors.append(f"{tag}: verified source must say what it supports")
            if s.get("kind") not in ALLOWED_KINDS:
                errors.append(f"{tag}: unknown source kind '{s.get('kind')}' (allowed: {sorted(ALLOWED_KINDS)})")
            if s.get("kind") == "regulator" and any(w in s.get("publisher", "") for w in NONPROFIT_MARKERS):
                errors.append(f"{tag}: '{s.get('publisher')}' is not a regulator")
            if s.get("human_link_check") not in (True, False, None):
                errors.append(f"{tag}: human_link_check must be a Boolean")

    # Compatibility with in-memory synthetic tests: manually supplied sources
    # must still pass the same type/authority checks, without posing as actual
    # raw source-fragment provenance or changing the signed crosswalk counts.
    for sid, s in lib.register.items():
        if sid in lib.source_variants:
            continue
        if s.get("kind") not in ALLOWED_KINDS:
            errors.append(f"register:{sid}: unknown source kind '{s.get('kind')}'")
        if s.get("kind") == "regulator" and any(
            w in s.get("publisher", "") for w in NONPROFIT_MARKERS
        ):
            errors.append(f"register:{sid}: '{s.get('publisher')}' is not a regulator")
        if not s.get("url", "").startswith("https://"):
            errors.append(f"register:{sid}: url must be https")
        if s.get("verified_on") and not s.get("supports"):
            errors.append(f"register:{sid}: verified source must say what it supports")

    def scope_snapshot(s: dict) -> dict:
        # _origin is provenance metadata from the loader, NOT original data.
        return {"origin": s["_origin"], "source": {k: v for k, v in s.items() if k != "_origin"}}

    exact_collisions = {url: rows for url, rows in url_variants.items() if len(rows) > 1}
    # URL aliases group records for REVIEW only, never for claim-source substitution.
    declared = {build.review_alias_key(url): group
                for url, group in lib.crosswalk_groups.items()}
    if len(declared) != len(lib.crosswalk_groups):
        errors.append("register: duplicate canonical alias crosswalk groups")
    observed_collisions = {url: rows for url, rows in alias_variants.items()
                           if len(rows) > 1}
    unresolved = 0
    for url, rows in observed_collisions.items():
        item = declared.get(url)
        if item is None:
            # One unverified base placeholder may be upgraded once by one
            # fragment of exactly the same id and URL (the original contract).
            harmless_upgrade = (
                len(rows) == 2 and len({s["id"] for s in rows}) == 1
                and sum(bool(s.get("verified_on")) for s in rows) == 1
                and any(s["_origin"] == "base" and not s.get("verified_on") for s in rows)
            )
            if not harmless_upgrade:
                errors.append(f"register: duplicate url without source crosswalk: {url}")
            continue
        expected = sorted(
            [{"origin": row["origin"], "source": row["source"]} for row in item["variants"]],
            key=lambda obj: json.dumps(obj, sort_keys=True),
        )
        observed = sorted(
            [scope_snapshot(s) for s in rows],
            key=lambda obj: json.dumps(obj, sort_keys=True),
        )
        if expected != observed:
            errors.append(f"register: source crosswalk mismatch for {url} (scope/metadata/verification changed)")
        status = item.get("review_status")
        if status == "pending-human-source-and-reading-scope-review":
            unresolved += 1
        elif status == "resolved":
            record = item.get("resolution") or {}
            if not (record.get("reviewer") and DATE_RE.fullmatch(record.get("date", "")) and record.get("scope_notes")):
                errors.append(f"register: marked-resolved shared source lacks reviewer/date/scope notes: {url}")
        else:
            errors.append(f"register: unknown shared-source review status {status!r}: {url}")
    for url in declared:
        if url not in observed_collisions:
            errors.append(f"register: stale source crosswalk URL not present in actual collisions: {url}")
    if lib.crosswalk:
        if lib.crosswalk.get("raw_source_rows") != raw_count:
            errors.append(f"register: raw row count changed from crosswalk baseline ({raw_count})")
        if lib.crosswalk.get("unique_source_urls") != len(url_variants):
            errors.append("register: unique URL count changed from crosswalk baseline")
        if set(lib.crosswalk.get("article_origins", {})) != set(lib.articles):
            errors.append("taxonomy: source crosswalk article origin map must contain every article and tool")
        if lib.crosswalk.get("duplicate_url_groups") != len(exact_collisions):
            errors.append("register: collision count differs from crosswalk")
    if unresolved:
        warns.append(f"register: {unresolved} source URL collision groups have NOT received human source-scope review")

    # --- taxonomy ---
    slugs = [a["slug"] for a in lib.taxonomy["slate"]]
    if len(slugs) != len(set(slugs)):
        errors.append("taxonomy: duplicate slate slug")
    if [a["n"] for a in lib.taxonomy["slate"]] != list(range(1, 36)):
        errors.append("taxonomy: slate must be numbered 1..35")
    for a in lib.taxonomy["slate"]:
        if a["section"] not in lib.sections:
            errors.append(f"taxonomy:{a['slug']}: unknown section")

    # --- articles ---
    for slug, meta in lib.articles.items():
        p = f"article:{slug}"
        for k in REQUIRED_META:
            if k not in meta:
                errors.append(f"{p}: missing meta '{k}'")
        if errors and any(e.startswith(p) and "missing meta" in e for e in errors):
            continue
        is_tool = meta.get("kind") == "tool"
        if is_tool:
            slate = next((x for x in lib.taxonomy["tools"] if x["slug"] == slug), None)
            if not slate:
                errors.append(f"{p}: tool slug not in taxonomy tools (add it first)")
            elif meta["section"] != "field-tools":
                errors.append(f"{p}: tools live in the field-tools section")
        else:
            slate = lib.slate.get(slug)
            if not slate:
                errors.append(f"{p}: slug not in taxonomy slate (add it first)")
            else:
                if slate["section"] != meta["section"] or slate["track"] != meta["track"]:
                    errors.append(f"{p}: section/track disagree with taxonomy")
                if slate["n"] != meta["n"]:
                    errors.append(f"{p}: n disagrees with taxonomy")
        if meta["section"] not in lib.sections:
            errors.append(f"{p}: unknown section")
        if meta["track"] not in lib.taxonomy["tracks"]:
            errors.append(f"{p}: unknown track")
        for k in ("updated", "last_checked"):
            if not DATE_RE.match(meta[k]):
                errors.append(f"{p}: {k} must be YYYY-MM-DD")
        if len(meta["description"]) > 165:
            errors.append(f"{p}: description over 165 chars ({len(meta['description'])})")
        if len(meta["title"]) > 60:
            warns.append(f"{p}: title over 60 chars")

        # Visible citation custody is an editorial release gate, not a QD or
        # scientific source approval. Reject hidden/comment/attribute/script citations
        # BEFORE build.resolve_tokens can turn them into apparently valid footnotes.
        try:
            placement = reader_visible_citations.check_body(meta["_body"], slug)
        except reader_visible_citations.Hold as exc:
            errors.append(f"{p}: reader-visible citation integrity: {exc}")
            continue
        if placement["concealed"]:
            errors.append(
                f"{p}: citation token not reader-visible "
                f"(raw={len(placement['raw'])}, visible={len(placement['visible'])}); "
                "check HTML comments, attributes, scripts, and hidden regions"
            )
            continue

        try:
            body, order = build.resolve_tokens(lib, meta)
        except (KeyError, ValueError) as e:
            errors.append(f"{p}: {e}")
            continue
        # sources are evaluated at the reading depth of this article's author.
        for sid in order:
            if not lib.source_for(meta, sid).get("verified_on"):
                errors.append(f"{p}: cites unverified source '{sid}'")
        # Each cited source must have an explicit, origin-scoped reading-purpose note.
        # A known URL or another contributor's scope is not sufficient evidence.
        missing_usage = set(order) - set(meta.get("source_use", {}))
        if missing_usage:
            errors.append(f"{p}: cited source lacks article-specific source_use reading-scope note: {sorted(missing_usage)}")
        # A present but empty/non-string statement is not a reading-scope
        # explanation. Prevent blank notes from being treated as source QA.
        blank_usage = [
            sid for sid in order if sid in meta.get("source_use", {})
            and (not isinstance(meta["source_use"][sid], str)
                 or not meta["source_use"][sid].strip())
        ]
        if blank_usage:
            errors.append(f"{p}: cited source has blank or invalid article-specific source_use note: {sorted(blank_usage)}")
        extra = set(meta.get("source_use", {})) - set(order)
        if extra:
            errors.append(f"{p}: source_use lists sources never cited in the body: {sorted(extra)}")
        kinds = {lib.source_for(meta, s)["kind"] for s in order}
        if len(order) < (2 if is_tool else 3):
            errors.append(f"{p}: needs {2 if is_tool else 3}+ checked sources (has {len(order)})")
        if meta["track"] == "lost-ways" and not (kinds & {"primary-digitized", "museum-study", "museum", "museum-object", "archive"}):
            errors.append(f"{p}: history piece needs a primary or museum/archive source")
        if meta["track"] == "lost-ways" and not (kinds & {"regulator", "extension"}):
            errors.append(f"{p}: history piece needs a modern regulator/extension source for its safety verdict")
        if meta["track"] == "modern" and not (kinds & {"regulator", "extension"}):
            errors.append(f"{p}: modern piece needs a regulator/extension source")
        # stray external links (everything must be via the register)
        reg_urls = {s["url"] for s in lib.register.values()}
        for href in re.findall(r'href="(https?://[^"]+)"', body):
            if href not in reg_urls:
                errors.append(f"{p}: external link not in source register: {href}")
        # structure
        if re.search(r"<h1[\s>]", body):
            errors.append(f"{p}: body must not contain an h1 (template provides it)")
        ids = re.findall(r'<h2 id="([^"]+)"', body)
        if len(ids) != len(set(ids)):
            errors.append(f"{p}: duplicate h2 ids")
        for img in re.findall(r"<img\b[^>]*>", body):
            if not re.search(r'\balt="[^"]+"', img):
                errors.append(f"{p}: <img> without alt text")
        for tbl in re.findall(r"<table\b[\s\S]*?</table>", body):
            if "<caption" not in tbl or 'scope="col"' not in tbl:
                errors.append(f"{p}: table needs <caption> and scope=col headers")
        for wrap in re.findall(r'<div class="pa-tablewrap"[^>]*>', body):
            if 'tabindex="0"' not in wrap or "aria-label" not in wrap:
                errors.append(f"{p}: scrollable table wrapper needs tabindex=0 and aria-label")
        if "pa-act" not in body:
            errors.append(f"{p}: missing the top action/read-first box")
        if meta["track"] == "lost-ways" and "pa-verdict" not in body:
            errors.append(f"{p}: history piece needs a safety-verdict panel")
        if meta["track"] == "lost-ways" and "pa-thennow" not in body:
            warns.append(f"{p}: history piece has no Then/Now panel")
        words = build.word_count(body)
        floor = 450 if is_tool else MIN_WORDS_CORNERSTONE
        if words < floor:
            errors.append(f"{p}: {words} words is under the minimum of {floor}")
        plain = re.sub(r"<[^>]+>", " ", body)
        for pat, why in BANNED:
            if re.search(pat, plain, flags=re.I):
                errors.append(f"{p}: banned language ({why})")
        # governance
        sr = meta["safety_review"]
        if sr["state"] not in ("pending", "approved", "not-required"):
            errors.append(f"{p}: safety_review.state invalid")
        if slate and slate["gate"] and sr["state"] == "not-required":
            errors.append(f"{p}: taxonomy marks this high-consequence; safety review cannot be 'not-required'")
        if sr["state"] == "approved" and not (sr.get("reviewer") and sr.get("date") and DATE_RE.match(sr["date"] or "")):
            errors.append(f"{p}: approved safety review needs reviewer name and date")
        if not is_tool and meta["track"] == "modern":
            if slate and not slate["gate"]:
                errors.append(f"{p}: every modern-track guide gives actionable guidance and must be gated in taxonomy.json")
            if sr["state"] == "not-required":
                errors.append(f"{p}: a modern-track guide cannot be exempt from safety review")
        if meta["status"]["publish"] == "published":
            # A name/date alone cannot grandfather an old review over edited
            # article copy, citations, source reading depth or link-check state.
            current_fingerprint = evidence_freeze.fingerprint(lib, meta)
            if sr["state"] == "approved" and sr.get("review_fingerprint") != current_fingerprint:
                errors.append(f"{p}: CANNOT be published; human safety review is not bound to current article/source fingerprint")
            rr = meta.get("release_review") or {}
            if rr.get("state") == "approved" and rr.get("review_fingerprint") != current_fingerprint:
                errors.append(f"{p}: CANNOT be published; release review is not bound to current article/source fingerprint")
            # A source collision remains a publication HOLD even if an author
            # or editor marks the article reviewed. Scoped reading matters.
            for sid in order:
                source = lib.source_for(meta, sid)
                group = lib.crosswalk_member_groups.get(
                    (source.get("_origin"), sid, source["url"]))
                if group and group.get("review_status") != "resolved":
                    errors.append(f"{p}: CANNOT be published with unresolved shared-source scope '{sid}'")
            for sid in order:
                source = lib.source_for(meta, sid)
                if source.get("human_link_check") is not True:
                    errors.append(f"{p}: CANNOT be published before human source-link verification of '{sid}'")
            release = meta.get("release_review") or {}
            if not (
                release.get("state") == "approved"
                and release.get("reviewer")
                and DATE_RE.fullmatch(release.get("date") or "")
                and release.get("evidence_url", "").startswith("https://")
            ):
                errors.append(f"{p}: CANNOT be published without documented independent QD/release sign-off")
            # Editorial review and safety approval are separate gates; a pending safety review blocks publication whatever the taxonomy says.
            if sr["state"] == "pending":
                errors.append(f"{p}: CANNOT be published while a safety review is pending")
            if slate and slate["gate"] and sr["state"] != "approved":
                errors.append(f"{p}: CANNOT be published without an approved human safety review")
            if meta["status"]["editorial"] != "reviewed":
                errors.append(f"{p}: CANNOT be published before editorial review")
        elif meta["status"]["publish"] != "draft":
            errors.append(f"{p}: status.publish must be 'draft' or 'published'")
        for rel in meta.get("related", []):
            if rel not in lib.slate and rel not in lib.articles:
                errors.append(f"{p}: related slug '{rel}' not in taxonomy")

    # --- design tokens: WCAG AA ---
    tokens = css_tokens(lib.css)
    for fg, bg in CONTRAST_PAIRS:
        if fg not in tokens or bg not in tokens:
            errors.append(f"css: missing token for contrast pair {fg}/{bg}")
            continue
        ratio = contrast(tokens[fg], tokens[bg])
        if ratio < 4.5:
            errors.append(f"css: contrast {fg} on {bg} is {ratio:.2f}:1 (<4.5)")
    for needed in ("prefers-reduced-motion", "@media print", "focus-visible", "forced-colors"):
        if needed not in lib.css:
            errors.append(f"css: missing '{needed}' support")
    return errors, warns


def main() -> int:
    errors, warns = validate()
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

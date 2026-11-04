#!/usr/bin/env python3
"""Assemble the REAL source-controlled seven-chapter flagship in a SYNTHETIC
Gutenberg wrapper for disposable local WordPress editor persistence tests.

Not the WordPress.com page 6 export. Never publish, store subscriber data,
copy production DB/settings, or treat a Playground Save as hosted acceptance.
"""
from __future__ import annotations

import argparse
from html import escape
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HOME / "rights"))

from build_combined_page6_offline import (  # noqa: E402
    CSS_PATH, MARKER, build_candidate, structural_inventory,
)
from test_build_combined_page6_offline import source_fixture  # noqa: E402
from withhold_unverified_nypl_capture import NYPL_FILE, NYPL_RECORD  # noqa: E402

CSS_FILES = (
    "flagship.css", "chronicle.css", "chronicle-lens.css",
    "inquiry.css", "observer-lab.css", "reading-trail.css",
)
JS_FILES = ("flagship.js", "observer-lab.js", "chronicle-lens.js", "reading-trail.js")
NAV_TARGETS = (
    "fv-hf-title", "fv-hf-chronicle", "fv-hf-evidence", "fv-hf-inquiry",
    "fv-hf-method-title", "fv-hf-observer", "fv-hf-mind-title",
)
STAGING_ONLY = "FV EX2 SOURCE-CONTROLLED FULL FLAGSHIP — ISOLATED REVIEW ONLY"
ASSEMBLER_STAGE_CSS = HERE / "assembler_saved_layout_playground_only.css"
PUBLIC_MARGINS_JSON = HERE / "public_page6_margins_20261102.json"
STAGING_ASSEMBLER_STYLE = 'data-fv-stage-only="assembler-saved-layout"'
SECOND_BLOCK = '<!-- wp:html --><div class="fv-hf"'
END_BLOCK = "<!-- /wp:html -->"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_sources(home: Path) -> tuple[str, dict[str, str], dict[str, str]]:
    # Names are explicit; never read files from user input or arbitrary paths.
    index = (home / "index.html").read_text(encoding="utf-8")
    css = {name: (home / name).read_text(encoding="utf-8") for name in CSS_FILES}
    js = {name: (home / name).read_text(encoding="utf-8") for name in JS_FILES}
    return index, css, js



def load_public_margins(path: Path = PUBLIC_MARGINS_JSON) -> tuple[list[str], dict]:
    """Import only the publicly visible page-6 Margins spans; never a site dump."""
    raw = path.read_bytes()
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid public Margins provenance JSON") from exc
    if (not isinstance(data, dict) or data.get("source_site_id") != 256784396 or
            data.get("source_page_id") != 6 or
            data.get("source_url") != "https://finalvestige.com/" or
            data.get("status") != "ISOLATED_WORDPRESS_PLAYGROUND_ONLY" or
            data.get("fragment_count") != 72 or
            not re.fullmatch(r"20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d",
                             str(data.get("source_modified", "")))):
        raise ValueError("Untrusted public Margins source provenance")
    rows = data.get("items")
    if not isinstance(rows, list) or len(rows) != 72:
        raise ValueError("Public Margins record count drift")
    texts = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"index", "text"} or row["index"] != i:
            raise ValueError("Public Margins indices or structure drift")
        value = row["text"]
        if (not isinstance(value, str) or not value or len(value) > 550 or
                "<" in value or ">" in value or
                re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", value)):
            raise ValueError("Unsafe published Margins text at index " + str(i))
        texts.append(value)
    if len(set(texts)) != 72:
        raise ValueError("Public Margins duplicate text")
    return texts, {
        "source_modified": data["source_modified"],
        "public_fragment_fixture_sha256": digest(raw),
    }


def compose(index: str, css: dict[str, str], js: dict[str, str],
            assembler_css: str | None = None) -> tuple[str, dict]:
    if set(css) != set(CSS_FILES) or set(js) != set(JS_FILES):
        raise ValueError("One or more source-controlled assets missing or unexpected")
    matches = re.findall(r"<body(?:\s[^>]*)?>(.*?)</body>", index, re.S | re.I)
    if len(matches) != 1:
        raise ValueError("Require exactly one complete source-controlled HTML body")
    body = matches[0].strip()
    if body.count('data-fv-home-flagship') != 1 or body.count('class="fv-hf__chapter-nav"') != 1:
        raise ValueError("Full flagship root or chapter navigation drift")
    if any(body.count('id="' + name + '"') != 1 for name in NAV_TARGETS):
        raise ValueError("Seven evidence chapter targets missing or duplicated")
    if any(body.count('href="#' + name + '"') < 1 for name in NAV_TARGETS):
        raise ValueError("Seven evidence chapter links missing")
    if body.count('<script') or body.count('</style') or END_BLOCK in body or SECOND_BLOCK in body:
        raise ValueError("Unexpected executable/WordPress block breakout in original HTML")
    head_css = re.findall(r'<link\s+rel="stylesheet"\s+href="\./([^"]+)"\s*/?>', index)
    head_js = re.findall(r'<script\s+src="\./([^"]+)"\s+defer></script>', index)
    if head_css != list(CSS_FILES) or head_js != list(JS_FILES):
        raise ValueError("Unreviewed external stylesheet/script link or asset order drift")
    if NYPL_FILE in body or 'NYPL believes this item is in the public domain' in body:
        raise ValueError("Unverified capture or unsupported public-domain assertion")
    if body.count(NYPL_RECORD) != 2:
        raise ValueError("Require the real original NYPL primary-source reference")
    for name, value in [*css.items(), *js.items()]:
        if not value.strip() or "</style" in value.lower() or "</script" in value.lower():
            raise ValueError("Empty or HTML-breakout CSS/JS: " + name)
        if END_BLOCK in value or "<!-- wp:" in value:
            raise ValueError("Unexpected Gutenberg block delimiter in " + name)

    # The fixture contains *invented synthetic Margins text*, not real page-6
    # records. First apply the previously tested rights + contrast transforms.
    # Then replace only its tiny simulated flagship with the real source code.
    public_margins, public_receipt = load_public_margins()
    tiny, _ = build_candidate(source_fixture(), CSS_PATH.read_text(encoding="utf-8"))
    if tiny.count(SECOND_BLOCK) != 1:
        raise ValueError("Synthetic Gutenberg flagship boundary drift")
    prefix, rest = tiny.split(SECOND_BLOCK, 1)
    if rest.count(END_BLOCK) != 1:
        raise ValueError("Synthetic Gutenberg block closing boundary drift")
    _old_stub, suffix = rest.split(END_BLOCK, 1)
    if not suffix.endswith('<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->'):
        raise ValueError("Synthetic Focus/Jetpack tail drift")

    # Replace only the 72 invented synthetic text nodes with text already
    # publicly published on page 6. Keep the synthetic Gutenberg wrapper,
    # mock Jetpack block and all protected release gates separate.
    for i, value in enumerate(public_margins):
        needle = ">Historic fragment " + str(i) + "</span>"
        if prefix.count(needle) != 1:
            raise ValueError("Synthetic Margins source boundary drift at " + str(i))
        prefix = prefix.replace(needle, ">" + escape(value, quote=False) + "</span>", 1)
    if "Historic fragment " in prefix:
        raise ValueError("Unreplaced synthetic Margins placeholder")
    # Give the published text a labeled, keyboard-focusable scroll region.
    # This does NOT reproduce the live Margins rotator, styling, or JS.
    # This is only a development fixture; never treat it as hosted DOM parity.
    opening = '<div class="fv-margin-strip">'
    ending = '</div><style>'
    if prefix.count(opening) != 1 or prefix.count(ending) != 1:
        raise ValueError("Synthetic Margins block structure changed")
    prefix = prefix.replace(
        opening, opening +
        '<div class="fv-margin-strip__inner">'
        '<span class="fv-margin-strip__label">72 PUBLISHED MARGINS · TEST FIXTURE</span>'
        '<div class="fv-margin-strip__window" role="region" '
        'aria-label="72 published historical fragments in isolated review" tabindex="0">', 1
    ).replace(ending, '</div></div>' + ending, 1)

    # This CSS is actually saved in Gutenberg, NOT pasted into Chromium.
    # It is deliberately disjoint from the eleven authentic flagship assets.
    # Fail closed on HTML breakout or external/unreviewed CSS fetches.
    if assembler_css is None:
        assembler_css = ASSEMBLER_STAGE_CSS.read_text(encoding="utf-8")
    if (not assembler_css.startswith("/* EX2 ISOLATED PLAYGROUND ONLY") or
            any(x in assembler_css.lower()
                for x in ("</style", "<script", "@import", "url(", "javascript:",
                          "<!-- wp:", "https://", "http://")) or
            ".wp-block-post-content > .fv-hf" not in assembler_css or
            ".fv-margin-strip__window" not in assembler_css or
            "@supports selector(body:has(" not in assembler_css):
        raise ValueError("Unreviewed or unsafe isolated Assembler saved CSS")
    inline_css = "\n".join("/* SOURCE: " + name + " */\n" + css[name] for name in CSS_FILES)
    inline_js = "\n".join(
        '<script data-fv-source="' + name + '">\n' + js[name] + '\n</script>'
        for name in JS_FILES
    )
    section = (
        '<style ' + STAGING_ASSEMBLER_STYLE + '>\n' + assembler_css + '\n</style>\n'
        + '<style data-fv-stage-only="source-css">\n' + inline_css + '\n</style>\n'
        + '<!-- ' + STAGING_ONLY + ' -->\n' + body + '\n'
        + inline_js
    )
    candidate = prefix + '<!-- wp:html -->\n' + section + '\n' + END_BLOCK + suffix
    inv = structural_inventory(candidate)
    if inv["margin_indices"] != list(range(72)):
        raise ValueError("Synthetic 72-item Margins/contrast source drift")
    if inv["jetpack_subscription_blocks"] != 1 or inv["chapter_nav_marker"] != 1:
        raise ValueError("Synthetic Jetpack block or actual seven-chapter nav missing")
    if inv["nypl_catalog_links"] != 2 or inv["focus_fieldbook_occurrences"] < 1:
        raise ValueError("NYPL catalog provenance or Focus Fieldbook missing")
    if inv["html_blocks"] != 2 or inv["html_block_ends"] != 2:
        raise ValueError("Serialized Gutenberg custom HTML boundaries drifted")
    if inv["inline_scripts"] != 0 or candidate.count('<script data-fv-source=') != 4:
        raise ValueError("Executable script source changed or duplicated")
    if candidate.count(MARKER) != 1 or NYPL_FILE in candidate:
        raise ValueError("Contrast repair or NYPL rights guard missing")
    if candidate.count(STAGING_ONLY) != 1 or candidate.count(STAGING_ASSEMBLER_STYLE) != 1:
        raise ValueError("Missing isolated saved-styling or synthetic marker")
    if (candidate.count('class="fv-margin-strip__window"') != 1 or
            candidate.count('aria-label="72 published historical fragments in isolated review" tabindex="0"') != 1):
        raise ValueError("Synthetic no-JS Margins scroll region not accessible")
    sources = {"index.html": index, **css, **js}
    fingerprints = {
        name: digest(value.encode("utf-8")) for name, value in sorted(sources.items())
    }
    return candidate, {
        "data_classification": "PUBLIC_PAGE6_MARGINS_WITH_SYNTHETIC_JETPACK_FIXTURE",
        "release": "HOLD",
        "page6_live_content_included": "72_PUBLIC_MARGINS_TEXTS_ONLY",
        "published_margins_source_modified": public_receipt["source_modified"],
        "public_fragment_fixture_sha256": public_receipt["public_fragment_fixture_sha256"],
        "other_page6_content_included": False,
        "real_source_controlled_flagship": True,
        "source_sha256": fingerprints,
        "assembler_saved_stage_css_sha256": digest(assembler_css.encode("utf-8")),
        "candidate_sha256": digest(candidate.encode("utf-8")),
        "candidate_bytes": len(candidate.encode("utf-8")),
        "margin_items": 72,
        "gutenberg_custom_html_blocks": inv["html_blocks"],
        "jetpack_block_comments": 1,
        "focus_occurrences": inv["focus_fieldbook_occurrences"],
        "nypl_record_links": 2,
        "chapter_targets": list(NAV_TARGETS),
        "style_source_count": len(CSS_FILES),
        "script_source_count": len(JS_FILES),
        "wordpress_theme_parity": "NOT_TESTED",
        "production_source_or_subscribers": "ONLY_PUBLIC_MARGINS_NO_PRIVATE_DATA",
        "accessibility_performance_approval": "NOT_GRANTED",
    }


def write(home: Path, output: Path, manifest: Path) -> dict:
    output, manifest = output.resolve(), manifest.resolve()
    if output == manifest or output.exists() or manifest.exists():
        raise ValueError("Require distinct, unused output and manifest paths")
    page, css, js = read_sources(home)
    candidate, receipt = compose(page, css, js)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output.open("xb") as f:
            f.write(candidate.encode("utf-8"))
        with manifest.open("x", encoding="utf-8") as f:
            json.dump(receipt, f, sort_keys=True, indent=2)
            f.write("\n")
    except BaseException:
        output.unlink(missing_ok=True)
        manifest.unlink(missing_ok=True)
        raise
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    report = write(HOME, args.output, args.manifest)
    # Deliberately do not print candidate/source HTML to logs.
    print(json.dumps({
        "result": "OFFLINE_STAGE_ONLY", "release": "HOLD",
        "source_file_count": len(report["source_sha256"]),
        "candidate_bytes": report["candidate_bytes"],
        "candidate_sha256": report["candidate_sha256"],
        "production_content_included": False,
    }, sort_keys=True))

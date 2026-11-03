#!/usr/bin/env python3
"""R98 PRIVATE HOLD: print/offline CSS visibility and source-link custody.

R93-R97 protect authored HTML, citations, visible review shell, metadata and
routes. They do not establish that generated footnotes or safety warnings
remain readable after stylesheet application or browser print rendering.

This deliberately conservative static CSS gate protects the source/review
surfaces and printed outbound-link URL annotation. It is NOT a browser engine,
human source review, emergency/medical safety assessment, or release approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = "r98-print-offline-source-review-css-hold-v1"
PRINT_ALLOW_HIDDEN = frozenset({
    ".pa-tool", ".pa-toc", ".pa-filter", ".pa-printbar",
    ".pa-skip", ".pa-card h3 a::after",
})
DYNAMIC_ALLOW_HIDDEN = frozenset({".pa-card[hidden]", ".pa-empty[hidden]"})
# Exactly five existing decorative heading flourishes; never extend this
# exemption to real source text, warnings, review blocks or print output.
DECORATIVE_PSEUDO_HIDE_ALLOWLIST = frozenset({
    ".pa-act h2::before", ".pa-verdict-head h2::before",
    ".pa-sources h2::before", ".pa-review h2::before",
    ".pa-related h2::before",
})
SOURCE_SELECTORS = (
    ".pa-sources", ".pa-src-meta", ".pa-src-use", ".pa-cite",
    ".pa-review", ".pa-alert", ".pa-act", ".pa-verdict",
    ".pa-body", ".pa-head", ".pa-article", ".pa-shell",
)
MAX_CSS = 300_000
SITE_PRINT_HREF_SELECTOR = '.pa a[href^="http"]::after'


class Hold(ValueError):
    """A private offline source/citation/print visibility invariant failed."""


def need(condition, message):
    if not condition:
        raise Hold(message)


def seal(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def remove_comments(css):
    need(type(css) is str and 0 < len(css.encode("utf-8")) <= MAX_CSS,
         "missing or oversized original CSS")
    # Fail closed for unmatched comments, rather than normalizing malformed CSS.
    need(css.count("/*") == css.count("*/"), "unbalanced CSS comments")
    cleaned = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    need("/*" not in cleaned and "*/" not in cleaned,
         "unterminated or overlapping CSS comment")
    # CSS escape handling is deliberately not silently approximated: encoded
    # selector/property spellings could evade an ASCII safety comparison.
    need("\\" not in cleaned, "CSS escape requires manual source-visibility review")
    need(not re.search(r"@import\b|@font-face\b|@namespace\b|url\s*\(", cleaned, re.I),
         "external or opaque stylesheet dependency requires manual review")
    return cleaned


def split_top(source):
    """Parse bounded, balanced CSS blocks; never claim to be a browser CSSOM."""
    position = 0
    length = len(source)
    while position < length:
        while position < length and source[position].isspace():
            position += 1
        if position >= length:
            break
        begin = position
        quote = None
        depth = 0
        while position < length:
            ch = source[position]
            if quote:
                if ch == quote:
                    quote = None
            elif ch in ("'", '"'):
                quote = ch
            elif ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
                need(depth >= 0, "unbalanced CSS selector or declaration")
            elif depth == 0 and ch in "{;}":
                break
            position += 1
        need(position < length, "CSS statement without terminating delimiter")
        head = source[begin:position].strip()
        char = source[position]
        need(char == "{" and bool(head), "unexpected CSS statement or brace")
        position += 1
        body_begin = position
        braces = 1
        quote = None
        while position < length and braces:
            ch = source[position]
            if quote:
                if ch == quote:
                    quote = None
            elif ch in ("'", '"'):
                quote = ch
            elif ch == "{":
                braces += 1
            elif ch == "}":
                braces -= 1
            position += 1
        need(braces == 0 and quote is None,
             "unbalanced CSS rule or unterminated string")
        yield head, source[body_begin:position - 1]


def declarations(body):
    need("{" not in body and "}" not in body, "nested or unparsed CSS declaration")
    result = {}
    for item in body.split(";"):
        item = item.strip()
        if not item:
            continue
        need(":" in item, "CSS declaration without property/value")
        key, value = item.split(":", 1)
        key = key.strip().lower()
        value = re.sub(r"\s*!important\s*$", "", value.strip(), flags=re.I)
        need(bool(re.fullmatch(r"(?:--[a-z][a-z0-9-]*|-?[a-z][a-z0-9-]*)", key)) and bool(value),
             "unknown CSS declaration or empty value")
        need(key not in result, "duplicate CSS property requires manual inspection: " + key)
        result[key] = value.lower()
    need(bool(result), "empty CSS rule")
    return result


def selectors(head):
    # The current stylesheet uses only ordinary selectors; commas within
    # functional selectors cannot be trusted to make a concealment exception.
    # Splitting them conservatively still recognizes dangerous declarations.
    return [s.strip() for s in head.split(",") if s.strip()]


def dangerous_declaration(selector, key, value, in_print):
    v = re.sub(r"\s+", "", value).lower()
    # Existing print-only removal of ancillary widgets is not evidence that
    # their content is safe to omit; report the calculator exception separately.
    if key == "display" and v == "none":
        allowed = (PRINT_ALLOW_HIDDEN if in_print else
                   DYNAMIC_ALLOW_HIDDEN | DECORATIVE_PSEUDO_HIDE_ALLOWLIST)
        need(selector in allowed,
             "CSS hides non-exempt source, review or article content: " + selector)
        return
    if key == "display" and v == "contents":
        need(not any(s in selector for s in SOURCE_SELECTORS),
             "CSS strips evidence region semantics: " + selector)
    if key in ("visibility", "content-visibility") and v in ("hidden", "collapse", "auto"):
        raise Hold("CSS can conceal review/source content: " + selector + " " + key)
    if key == "opacity" and v != "1":
        raise Hold("non-opaque or computed evidence text requires human review: " + selector)
    if key in ("scale", "zoom") and (v in ("0", "0.0", "0%", ".0", "calc(0)") or
                                      v.startswith(("var(", "env(", "clamp(", "min(", "max("))):
        raise Hold("opaque computed scale cannot prove evidence visibility: " + selector)
    if key.startswith(("mask", "-webkit-mask", "clip", "filter", "-webkit-filter")):
        if v not in ("none", "auto"):
            raise Hold("CSS clipping or masking requires human review: " + selector)
    if key in ("overflow", "overflow-x", "overflow-y") and v in ("hidden", "clip"):
        raise Hold("CSS clips possible source/review content: " + selector)
    if key in ("font-size", "height", "max-height", "max-width", "width",
               "block-size", "inline-size", "max-block-size", "max-inline-size"):
        if re.fullmatch(r"(?:0+(?:\.0+)?)(?:px|pt|em|rem|%|vw|vh)?", v):
            raise Hold("CSS collapses possible source/review content: " + selector)
    if key == "line-height" and v in ("0", "0px", "0em", "0%"):
        need(selector == ".pa-body sup.pa-cite",
             "unexpected zero-height text near evidence: " + selector)
    if key in ("color", "-webkit-text-fill-color"):
        if (v == "transparent" or re.fullmatch(r"#[0-9a-f]{3,6}00", v) or
                "rgba(" in v or "hsla(" in v or re.search(r"/0(?:\.0+)?\)", v)):
            raise Hold("CSS text color opacity requires human print/screen review: " + selector)
    if key in ("transform", "translate") and ("scale(0" in v or "translate(-9999" in v):
        raise Hold("CSS moves or scales evidence out of view: " + selector)
    if key == "text-indent" and v.startswith("-"):
        raise Hold("CSS could shift review text offscreen: " + selector)
    if key in ("top", "bottom", "left", "right") and v.startswith("-9999"):
        need(selector == ".pa .pa-skip" and key == "left" and not in_print,
             "CSS moves source or review content offscreen: " + selector)
    if key == "position" and v == "fixed":
        raise Hold("fixed overlay can occlude source/review content: " + selector)
    if key == "pointer-events" and v != "auto":
        raise Hold("CSS removes interactions needed for source access: " + selector)
    if key in ("animation", "animation-name", "animation-timeline"):
        if v not in ("none", "auto"):
            raise Hold("dynamic CSS cannot prove critical evidence visibility: " + selector)


def audit_stylesheet(css):
    text = remove_comments(css)
    rules = []
    print_rules = []
    href_print = []
    hidden_print = []
    print_palette = []
    seen_rules = 0

    def visit(chunk, in_print=False, print_unconditional=True, depth=0):
        nonlocal seen_rules
        need(depth <= 8, "CSS nesting exceeds trusted review bound")
        for head, body in split_top(chunk):
            if head.startswith("@"):
                name = head.split(maxsplit=1)[0].lower()
                need(name in ("@media", "@container"),
                     "unreviewed CSS at-rule: " + head[:60])
                exact_print = bool(re.fullmatch(r"@media\s+print", head, re.I))
                next_print = in_print or exact_print
                # A print citation under screen/width/container conditions
                # cannot prove it will appear on a printed page.
                unconditional = print_unconditional and name == "@media" and exact_print
                visit(body, next_print, unconditional, depth + 1)
                continue
            options = selectors(head)
            need(options, "empty CSS selector")
            props = declarations(body)
            for selector in options:
                need(bool(re.match(r"^\.pa(?:\b|[-\w])", selector)),
                     "unscoped CSS selector could affect another site pillar: " + selector)
                # Functional/relational selectors can select ancestors or
                # non-archive elements despite a .pa mention inside them.
                need(not re.search(r":(?:has|is|where|not|host|global)\s*\(", selector, re.I),
                     "complex selector requires manual scope audit: " + selector)
                seen_rules += 1
                need(seen_rules <= 2000, "stylesheet exceeds audited selector budget")
                for key, value in props.items():
                    dangerous_declaration(selector, key, value, in_print)
                if in_print:
                    print_rules.append(selector)
                    for background_key in ("background", "background-color"):
                        if background_key in props:
                            need(props[background_key] in (
                                "transparent", "none", "#fff", "#ffffff"),
                                "print background may obscure dark evidence text: " + selector)
                    if "color" in props:
                        need(props["color"] in ("#000", "#000000"),
                             "print text must remain ink-black: " + selector)
                    if print_unconditional and selector in (".pa", ".pa *", ".pa a"):
                        print_palette.append((selector, props))
                    if selector in PRINT_ALLOW_HIDDEN and props.get("display") == "none":
                        hidden_print.append(selector)
                    if selector == SITE_PRINT_HREF_SELECTOR and print_unconditional:
                        href_print.append(props)
                else:
                    rules.append(selector)

    visit(text)
    need(len(href_print) == 1,
         "print view must expose each external source hyperlink's full URL")
    content = re.sub(r"\s+", "", href_print[0].get("content", ""))
    need(content == '"("attr(href)")"',
         "printed source URL annotation must use the exact, non-editorial href formatter")
    need(len(print_rules) > 0 and len(rules) > 0,
         "stylesheet lacks print or regular scoped content rules")
    need(any(selector == ".pa" and props.get("color") in ("#000", "#000000")
             and props.get("background") in ("#fff", "#ffffff")
             for selector, props in print_palette),
         "print root ink/paper palette missing")
    need(any(selector == ".pa *" and props.get("color") in ("#000", "#000000")
             and props.get("background") == "transparent"
             for selector, props in print_palette),
         "print evidence descendants must retain opaque black text")
    need(set(hidden_print) <= PRINT_ALLOW_HIDDEN,
         "non-exempt content hidden in printed archive")
    return {
        "stylesheet_sha256": hashlib.sha256(css.encode("utf-8")).hexdigest(),
        "scoped_selectors_audited": seen_rules,
        "print_selectors_audited": len(print_rules),
        "print_external_source_url_annotation": True,
        "print_hidden_ancillary_selectors": sorted(set(hidden_print)),
        "screen_only_decorative_pseudo_hide_exceptions_NOT_SAFETY_APPROVAL":
            sorted(DECORATIVE_PSEUDO_HIDE_ALLOWLIST),
        "calculator_hidden_on_print_REVIEW_REQUIRED": ".pa-tool" in hidden_print,
        "static_css_diagnostics_only": True,
        "browser_print_QA": "NOT_REVIEWED",
        "release_state": "HOLD",
        "may_publish": False,
    }


def audit_library(lib, render, prior_audit, r96_audit, r95_audit, r93_document, r94_body):
    prior = prior_audit(lib, render, r96_audit, r95_audit, r93_document, r94_body)
    need(prior["release_state"] == "HOLD" and prior["may_publish"] is False,
         "upstream R97 route/source custody no longer fail-closed")
    need(prior["private_draft_pages"] == 36 and prior["article_drafts"] == 35
         and prior["tool_drafts"] == 1, "private 35+1 draft inventory changed")
    css_report = audit_stylesheet(lib.css)
    report = {
        "schema": SCHEMA, "issue": 136,
        "release_state": "HOLD", "may_publish": False,
        "human_source_claim_review": "NOT_REVIEWED",
        "qualified_emergency_safety_review": "NOT_REVIEWED",
        "independent_QD": "NOT_REVIEWED",
        "actual_browser_print_check": "NOT_REVIEWED",
        "limitations": "CSS static custody, not CSSOM/browser print, external-link verification, clinical/food/water safety or publication permission.",
        "private_wordpress_ready_drafts_NOT_PUBLISHED": prior["private_draft_pages"],
        "protected_article_drafts": prior["article_drafts"],
        "protected_real_tool_drafts": prior["tool_drafts"],
        "planned_tools_without_drafts_NOT_IMPORTABLE": prior["unbuilt_tools_NOT_IMPORTABLE"],
        "prior_citation_occurrences_preserved_R93_R97": prior[
            "prior_rendered_citations_conserved_R96"],
        "prior_canonical_draft_destinations_preserved_R97": prior[
            "unique_canonical_draft_routes"],
        "css_custody": css_report,
        "print_content_exception_workorder_NOT_APPROVED": (
            "Water-planner .pa-tool calculator is hidden by pre-existing print CSS. "
            "Qualified human review must confirm whether instructions, limits, "
            "and interactive outputs require an alternate printable representation."
            if css_report["calculator_hidden_on_print_REVIEW_REQUIRED"] else None
        ),
    }
    report["sha256_seal"] = seal(report)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--private-json-stdout", action="store_true")
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    for name in ("build.py", "r93_rendered_citation_fidelity.py",
                 "r94_body_custody.py", "r95_dom_attribute_custody.py",
                 "r96_visible_source_safety_shell.py",
                 "r97_structured_data_route_custody.py"):
        target = root / "tools" / name
        need(target.is_file() and not target.is_symlink(),
             "trusted upstream gate missing: " + name)
    sys.path.insert(0, str(root / "tools"))
    import build
    import r93_rendered_citation_fidelity as r93
    import r94_body_custody as r94
    import r95_dom_attribute_custody as r95
    import r96_visible_source_safety_shell as r96
    import r97_structured_data_route_custody as r97
    report = audit_library(build.Library(), build.build_article,
                           r97.audit_library, r96.audit_library,
                           r95.audit_library, r93.audit_document, r94.audit_body)
    if args.private_json_stdout:
        print(json.dumps(report, sort_keys=True, ensure_ascii=False))
    else:
        print(json.dumps({key: value for key, value in report.items()
                          if key not in ("css_custody",)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Hold, ValueError, KeyError, OSError) as error:
        print(json.dumps({"schema": SCHEMA, "release_state": "HOLD",
                          "may_publish": False, "gate": "R98_FAILED",
                          "reason": str(error)}), file=sys.stderr)
        raise SystemExit(2)

"""Shared helpers for the Experience 2.0 builders: URL safety, data validation, asset bundling.

Standard library only. Nothing here writes outside the paths it is given and nothing touches the network.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

EX2 = Path(__file__).resolve().parent.parent
DATA = EX2 / "data"
CSS_SRC = EX2 / "design-system" / "src" / "css"
JS_SRC = EX2 / "design-system" / "src" / "js"

LINK_HOSTS = {"www.nasa.gov", "nasa.gov", "images.nasa.gov", "finalvestige.com", "www.finalvestige.com"}
IMAGE_HOSTS = {"images-assets.nasa.gov", "finalvestige.com"}
VALID_KINDS = {
    "DOCUMENTED CONTEXT", "PRIMARY REVIEW BOARD RECORD", "INSTRUMENT CHRONOLOGY",
    "HARDWARE AND DESIGN FINDING", "EVIDENCE BOUNDARY", "ENGINEERING RESPONSE",
}
VALID_ROLES = {"context", "document", "exhibit"}
VALID_CROSSWALK = {"verified", "partial", "article-only", "editorial-note"}
INSTANCE_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
INSTANCE_PLACEHOLDER = "{{fvx-instance}}"


class BadRecord(ValueError):
    """Raised when editorial data would produce unsafe or unreviewed output."""


def safe_https(url, hosts=LINK_HOSTS) -> str:
    """Return `url` only when it is plain HTTPS to an approved host with no credentials or control characters."""
    if not isinstance(url, str) or not url:
        raise BadRecord("URL must be a non-empty string")
    parts = urlsplit(url)
    if (parts.scheme != "https" or parts.hostname not in hosts or parts.username or parts.password
            or not parts.path or any(ord(ch) < 32 or ch in " \"'<>" for ch in url)):
        raise BadRecord(f"Unsafe or unapproved URL: {url!r}")
    return url


def esc(value) -> str:
    return escape(str(value), quote=True)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _need(obj: dict, keys, where: str):
    for key in keys:
        value = obj.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            raise BadRecord(f"{where}: missing required field {key!r}")


def load_apollo1(data: dict | None = None) -> dict:
    """Load and validate the canonical Apollo 1 data. Every record needs a limitation and rights-reviewed imagery.

    Passing `data` validates an in-memory copy instead of the file (used by the rejection tests)."""
    data = load_json(DATA / "apollo1.json") if data is None else data
    _need(data, ["investigation", "primary_report", "rights_policy", "records", "chronology"], "apollo1")
    safe_https(data["investigation"]["url"])
    safe_https(data["primary_report"]["url"])
    safe_https(data["rights_policy"]["basis_url"])
    seen = set()
    if len(data["records"]) != 6:
        raise BadRecord("Apollo 1 experience requires exactly six records")
    for rec in data["records"]:
        rid = rec.get("id", "")
        if rid in seen:
            raise BadRecord(f"Duplicate record id {rid}")
        seen.add(rid)
        _need(rec, ["title", "dek", "detail", "caution", "kind", "image", "report", "crosswalk"], rid)
        if rec["kind"] not in VALID_KINDS:
            raise BadRecord(f"{rid}: unreviewed evidence classification {rec['kind']!r}")
        img = rec["image"]
        _need(img, ["role", "role_label", "nasa_id", "src", "width", "height", "alt", "caption", "credit", "date_text", "record_url", "identity_note"], f"{rid}.image")
        if img["role"] not in VALID_ROLES:
            raise BadRecord(f"{rid}: unknown image role")
        if not isinstance(img.get("depicts_event"), bool):
            raise BadRecord(f"{rid}: image.depicts_event must be an explicit boolean")
        safe_https(img["src"], IMAGE_HOSTS)
        safe_https(img["record_url"])
        for variant in img.get("variants", []):
            safe_https(variant["url"], IMAGE_HOSTS)
        safe_https(rec["report"])
        for row in rec["crosswalk"]:
            if row.get("status") not in VALID_CROSSWALK:
                raise BadRecord(f"{rid}: crosswalk status must be one of {sorted(VALID_CROSSWALK)}")
            _need(row, ["claim", "source"], f"{rid}.crosswalk")
    chrono = data["chronology"]
    last = -1.0
    lo, hi = chrono["range"]
    for marker in chrono["markers"]:
        if not (lo <= marker["t"] <= hi) or marker["t"] < last:
            raise BadRecord("Chronology markers must be ordered and inside the declared range")
        last = marker["t"]
    safe_https(chrono["source_url"])
    return data


# ---- tokens and contrast ------------------------------------------------------

def read_tokens() -> dict[str, str]:
    """Colour tokens (`--fvx-name: #hex`) from 00-tokens.css."""
    text = (CSS_SRC / "00-tokens.css").read_text(encoding="utf-8")
    return {m.group(1): m.group(2).lower() for m in re.finditer(r"--fvx-([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})\b", text)}


def _lum(hex_color: str) -> float:
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(fg: str, bg: str) -> float:
    a, b = sorted((_lum(fg), _lum(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


# Pairs actually used in the CSS, with the WCAG 2.2 AA minimum that applies (4.5 text, 3 for UI boundaries).
CONTRAST_PAIRS = [
    ("text", "surface", 4.5), ("text", "ink", 4.5), ("text", "raised", 4.5), ("text-muted", "surface", 4.5), ("text-muted", "raised", 4.5),
    ("gold", "surface", 4.5), ("gold", "ink", 4.5), ("gold", "raised", 4.5), ("amber", "surface", 4.5),
    ("paper-ink", "paper", 4.5), ("paper-ink", "gold", 4.5), ("line-strong", "surface", 3.0), ("line-strong", "raised-2", 3.0),
    ("text", "raised-2", 4.5),
]


# ---- asset bundle -----------------------------------------------------------

def _minify_css(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*([{};,])\s*", r"\1", text)
    return text.strip() + "\n"


def bundle_css() -> str:
    parts = [_minify_css(p.read_text(encoding="utf-8")) for p in sorted(CSS_SRC.glob("*.css"))]
    return "/* Final Vestige Experience 2.0 design system. Generated by tools/build_all.py - do not edit. */\n" + "".join(parts)


def bundle_js() -> str:
    return (JS_SRC / "fv-ex2.js").read_text(encoding="utf-8")


def bundle_manifest(css: str, js: str, extra: dict | None = None) -> dict:
    def entry(text: str) -> dict:
        raw = text.encode("utf-8")
        return {"bytes": len(raw), "gzip_bytes": len(gzip.compress(raw, 9, mtime=0)), "sha256": hashlib.sha256(raw).hexdigest()}
    manifest = {"css": entry(css), "js": entry(js), "version": "0.5.0-sprint5"}
    manifest.update(extra or {})
    return manifest


# ---- page shell for standalone previews --------------------------------------

def page_shell(*, title: str, description: str, body: str, css_href: str, js_src: str, root_class: str = "fv-ex2") -> str:
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="robots" content="noindex, nofollow">\n'
        f"<title>{esc(title)}</title>\n<meta name=\"description\" content=\"{esc(description)}\">\n"
        f'<link rel="stylesheet" href="{esc(css_href)}">\n'
        "<style>html{background:#0c0d0d}body{margin:0;background:#0c0d0d}</style>\n"
        "</head>\n"
        f"<body>\n{body}\n<script src=\"{esc(js_src)}\" defer></script>\n</body>\n</html>\n"
    )

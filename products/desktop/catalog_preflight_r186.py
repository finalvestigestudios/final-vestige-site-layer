"""Offline fail-closed Gutenberg catalog preflight for six UNRELEASED desktop apps.

This checks one tracked static draft, not the served WordPress page, binary
integrity, malware, entitlement, QD approval, or authorization to publish.
No network access, customer data, download URLs, or emitted document text.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import stat
import sys

MAX_CATALOG_BYTES = 80 * 1024
CONTACT_URL = "https://finalvestige.com/contact/"
APPS = (
    ("LedgerDiff Lite", "FREE · IN DEVELOPMENT"),
    ("Invoice Twin Scout", "FREE · IN DEVELOPMENT"),
    ("SpendMap Lite", "FREE · IN DEVELOPMENT"),
    ("Policy Delta Desk", "FREE · IN DEVELOPMENT"),
    ("GrantAudit Studio Pro", "PREMIUM · PRIVATE DEVELOPMENT PREVIEW"),
    ("ProcureGuard Studio Pro", "PREMIUM · PRIVATE DEVELOPMENT PREVIEW"),
)
# There is deliberately no allowlist for scripts, images, forms, embeds,
# externally loaded fonts, download attributes, data attributes, or redirects.
_TAG_ATTRIBUTES = {
    "div": frozenset(("class",)), "p": frozenset(("class",)),
    "h1": frozenset(("class",)), "h2": frozenset(("class",)),
    "h3": frozenset(("class",)), "hr": frozenset(("class",)),
    "strong": frozenset(), "a": frozenset(("href",)),
}
_VOID_TAGS = frozenset(("hr",))
_BIDI = frozenset(chr(n) for n in (
    0x200E, 0x200F, 0x202A, 0x202B, 0x202C, 0x202D, 0x202E,
    0x2066, 0x2067, 0x2068, 0x2069,
))


def _identity(info) -> tuple[int, ...]:
    """Exclude access time, which a harmless first read is allowed to change."""
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


class CatalogPreflightError(ValueError):
    """Draft requires independent review; never publish from this preflight."""


def _reject() -> None:
    # Never return private pathnames, hidden markup, token strings, or URLs.
    raise CatalogPreflightError("Catalog violates static pre-release privacy/accessibility policy")


class _Catalog(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.heading_text: list[str] = []
        self.heading_tag: str | None = None
        self.headings: list[tuple[str, str]] = []
        self.strong_text: list[str] = []
        self.strong_active = False
        self.pending_app: str | None = None
        self.statuses: list[tuple[str, str]] = []
        self.visible: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.current_link: list[str] | None = None
        self.comments = 0

    def handle_starttag(self, tag, attrs):
        if tag not in _TAG_ATTRIBUTES or tag in _VOID_TAGS:
            _reject()
        keys = [name for name, _ in attrs]
        if (len(keys) != len(set(keys))
                or any(name not in _TAG_ATTRIBUTES[tag] for name in keys)):
            _reject()
        for key, value in attrs:
            if value is None or any(char in _BIDI or ord(char) < 32 for char in value):
                _reject()
            if key == "class" and not re.fullmatch(r"[A-Za-z0-9_ -]{1,160}", value):
                _reject()
        if tag == "a":
            if keys != ["href"] or attrs[0][1] != CONTACT_URL:
                _reject()
            if self.current_link is not None:
                _reject()
            self.current_link = []
        if tag in ("h1", "h2", "h3"):
            if self.heading_tag is not None:
                _reject()
            self.heading_tag, self.heading_text = tag, []
        if tag == "strong":
            if self.strong_active:
                _reject()
            self.strong_active, self.strong_text = True, []
        self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        if tag not in _VOID_TAGS:
            _reject()
        self.handle_starttag_for_void(tag, attrs)

    def handle_starttag_for_void(self, tag, attrs):
        if tag != "hr" or len(attrs) != 1 or attrs[0][0] != "class":
            _reject()
        value = attrs[0][1]
        if value is None or not re.fullmatch(r"[A-Za-z0-9_ -]{1,160}", value):
            _reject()

    def handle_endtag(self, tag):
        if not self.stack or tag != self.stack[-1]:
            _reject()
        if tag in ("h1", "h2", "h3"):
            heading = " ".join("".join(self.heading_text).split())
            self.headings.append((tag, heading))
            if tag == "h3" and heading in dict(APPS):
                if self.pending_app is not None:
                    _reject()
                self.pending_app = heading
            self.heading_tag, self.heading_text = None, []
        if tag == "strong":
            strong = " ".join("".join(self.strong_text).split())
            if self.pending_app is not None:
                self.statuses.append((self.pending_app, strong))
                self.pending_app = None
            self.strong_active, self.strong_text = False, []
        if tag == "a":
            if self.current_link is None:
                _reject()
            self.links.append((CONTACT_URL, " ".join("".join(self.current_link).split())))
            self.current_link = None
        self.stack.pop()

    def handle_data(self, data):
        if any(char in _BIDI or (ord(char) < 32 and char not in "\r\n\t") for char in data):
            _reject()
        self.visible.append(data)
        if self.heading_tag is not None:
            self.heading_text.append(data)
        if self.strong_active:
            self.strong_text.append(data)
        if self.current_link is not None:
            self.current_link.append(data)

    def handle_comment(self, data):
        # WordPress Gutenberg serialization only. Reject hidden hand-coded
        # comments that could disguise downloads or executable markup.
        self.comments += 1
        if (len(data) > 600 or self.comments > 100
                or not re.fullmatch(r"\s*/?wp:[A-Za-z0-9_-]+(?:\s+\{[^<>]*\})?\s*", data)):
            _reject()

    def handle_decl(self, decl):
        _reject()

    def unknown_decl(self, data):
        _reject()


def verify_catalog(raw: bytes) -> dict[str, object]:
    """Verify unreleased catalog markup only, without network or side effects."""
    if type(raw) is not bytes or len(raw) > MAX_CATALOG_BYTES or not raw:
        _reject()
    try:
        markup = raw.decode("utf-8", errors="strict")
    except UnicodeError:
        _reject()
    # HTMLParser deliberately accepts unfinished or unusual angle-bracket
    # sequences; make any unparsed raw delimiter a hard failure first.
    uncommented = re.sub(r"<!--.*?-->", "", markup, flags=re.DOTALL)
    outside_tags = re.sub(r"</?[A-Za-z][^<>]*>", "", uncommented)
    if "\x00" in markup or "<" in outside_tags or ">" in outside_tags:
        _reject()
    parser = _Catalog()
    try:
        parser.feed(markup)
        parser.close()
    except (ValueError, AssertionError):
        _reject()
    if parser.stack or parser.heading_tag or parser.strong_active or parser.pending_app:
        _reject()
    expected_headings = [
        ("h1", "Tools for work that cannot afford guesswork."),
        ("h2", "Free desktop utilities"),
        *(("h3", app) for app, _ in APPS[:4]),
        ("h2", "Professional editions"),
        *(("h3", app) for app, _ in APPS[4:]),
        ("h2", "Pilot with us"),
    ]
    if parser.headings != expected_headings or parser.statuses != list(APPS):
        _reject()
    if parser.links != [(CONTACT_URL, "Contact Final Vestige about a pilot")]:
        _reject()
    visible = " ".join(" ".join(parser.visible).split())
    for marker in (
        "No downloads are available until builds pass testing, security review and verification.",
        "Do not use pre-release builds with sensitive production data.",
        "not a substitute for accountants, auditors, attorneys or organizational approvals",
    ):
        if marker not in visible:
            _reject()
    return {
        "schema": "fvs-catalog-static-preflight-r186",
        "result": "PASS_STATIC_DRAFT_ONLY",
        "apps": len(APPS), "free": 4, "premium": 2,
        "contact_links": len(parser.links),
        "downloads_verified": False, "premium_access_verified": False,
        "site_publication_authorized": False, "qd_approved": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path, help="Tracked Gutenberg source draft")
    args = parser.parse_args(argv)
    try:
        info = args.catalog.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > MAX_CATALOG_BYTES:
            _reject()
        data = args.catalog.read_bytes()
        if len(data) != info.st_size or _identity(args.catalog.lstat()) != _identity(info):
            _reject()
        result = verify_catalog(data)
    except (OSError, CatalogPreflightError):
        print("HOLD: catalog preflight rejected (no publication approval)", file=sys.stderr)
        return 1
    print(f"{result['result']}: six unreleased apps, one contact link; QD/launch HOLD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

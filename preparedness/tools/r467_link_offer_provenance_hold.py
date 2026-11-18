#!/usr/bin/env python3
"""R467: read-only citation-link and commercial-offer boundary, never QD approval."""
import argparse
import hashlib
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

HOLD = "DRAFT_HARD_HOLD"
FREE = "https://finalvestige.com/preparedness/"
ORIGINS = ("base", "food", "health", "hist_field", "hist_food",
           "hist_home", "shelter", "start")
FORBIDDEN_TAGS = {"script", "iframe", "form", "input", "object", "embed",
                  "meta", "base", "link", "template", "style", "button"}
COMMERCE = {"payhip.com", "gumroad.com", "stripe.com", "paypal.com",
            "amazon.com", "shopify.com", "etsy.com", "patreon.com"}
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
CTRL = re.compile(r"[\x00-\x20\x7f\\]")

class Hold(ValueError):
    pass

def require(condition, reason):
    if not condition:
        raise Hold(reason)

def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def unique(pairs):
    obj = {}
    for k, v in pairs:
        require(k not in obj, "duplicate JSON property " + k)
        obj[k] = v
    return obj

def read_pinned(root, path, sha):
    p = Path(path)
    require(not p.is_absolute() and ".." not in p.parts and "\\" not in path,
            "unsafe relative evidence path")
    file = root / p
    require(file.is_file() and not file.is_symlink()
            and file.resolve().is_relative_to(root.resolve()), "missing evidence " + path)
    raw = file.read_bytes()
    require(len(raw) <= 220000 and blob(raw) == sha, "evidence blob changed " + path)
    return raw

def https_host(url):
    require(isinstance(url, str) and url and len(url) <= 4096
            and not CTRL.search(url) and not any(c in url for c in "\"'<>"),
            "unsafe URL")
    try:
        p = urlsplit(url)
        require(p.scheme == "https" and p.netloc and not p.username
                and not p.password and "%" not in p.netloc and p.port in (None, 443),
                "HTTPS authority invalid")
        host = p.hostname
        require(host and host not in ("localhost", "localhost.localdomain")
                and not host.startswith(".") and not host.endswith(".")
                and ".." not in host, "hostname invalid")
        try:
            require(ipaddress.ip_address(host).is_global, "nonpublic IP")
        except ValueError as err:
            if str(err) == "nonpublic IP":
                raise
            require("." in host, "unqualified hostname")
        return host
    except ValueError as exc:
        if isinstance(exc, Hold):
            raise
        raise Hold("malformed URL") from exc

def registry(source_families):
    require(set(source_families) == set(ORIGINS), "missing source origin")
    urls = {}
    for origin, rows in sorted(source_families.items()):
        ids = set()
        for s in rows:
            sid, url = s["id"], s["url"]
            require(sid not in ids, "duplicate source ID inside origin")
            ids.add(sid)
            https_host(url)
            # Distinct source IDs/read scopes remain distinct; never auto-canonicalize.
            urls.setdefault(url, []).append({"origin": origin, "id": sid,
                                               "verified_on": s.get("verified_on"),
                                               "kind": s.get("kind")})
    return urls

class LinkReader(HTMLParser):
    def __init__(self, known):
        super().__init__(convert_charrefs=True)
        self.known = known
        self.errors = []
        self.outbound = []
        self.unmatched = []
        self.commerce = []

    def handle_starttag(self, tag, attrs):
        names = [k for k, v in attrs]
        if tag in FORBIDDEN_TAGS or len(set(names)) != len(names):
            self.errors.append("unsafe tag/duplicate attribute " + tag)
        props = dict(attrs)
        if any(k.startswith("on") or k in ("srcdoc", "ping", "srcset",
                                         "action", "formaction") for k in names):
            self.errors.append("active or tracking attribute " + tag)
        if "style" in props and re.search(r"url\s*\(|expression\s*\(|@import",
                                          props["style"] or "", re.I):
            self.errors.append("active inline CSS")
        if props.get("target") == "_blank" and not {"noopener", "noreferrer"} <= set(
                (props.get("rel") or "").split()):
            self.errors.append("missing new-window protections")
        if tag == "a" and not props.get("href"):
            self.errors.append("anchor missing href")
        for k, v in attrs:
            if k not in ("href", "src", "poster", "xlink:href") or not v:
                continue
            if v.startswith("#"):
                continue
            if v.startswith("/") and not v.startswith("//"):
                if not v.startswith("/preparedness/"):
                    self.errors.append("relative link escaped Archive")
                continue
            try:
                host = https_host(v)
            except Hold as exc:
                self.errors.append(str(exc))
                continue
            witness = self.known.get(v, [])
            event = {"url": v, "source_witnesses": witness, "tag": tag}
            self.outbound.append(event)
            if not witness:
                self.unmatched.append(event)
            if any(host == c or host.endswith("." + c) for c in COMMERCE):
                self.commerce.append(event)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

def inspect_article(meta, html, source_families):
    require(meta["status"]["publish"] == "draft", "article no longer draft")
    citations = CITE.findall(html)
    require(citations and set(citations) == set(meta["source_use"]),
            "citation/source-use bijection broken")
    parser = LinkReader(registry(source_families))
    parser.feed(html)
    parser.close()
    require(not parser.errors, "; ".join(parser.errors))
    require(not parser.commerce, "commercial checkout link needs independent acceptance")
    return {"state": HOLD, "may_publish": False, "qd_pass": False,
            "source_supported": False, "citation_occurrences": len(citations),
            "outbound_witnesses": parser.outbound,
            "unmatched_outbound_links": parser.unmatched}

def inspect_campaign(c):
    required = {"topic", "free_destination", "published_grok_asset_id",
                "social_asset_verification", "optional_tool_state",
                "optional_tool_live_url", "paid_sku_verified", "paid_product_url",
                "commerce_review_state", "release_state", "site_cta_production_enabled",
                "tracking_script_added"}
    require(set(c) == required, "campaign fields changed")
    require(c["topic"] == "household-emergency-contact-reunification", "topic drift")
    require(c["free_destination"] == FREE, "free guide replaced")
    require(c["published_grok_asset_id"] is None
            and c["social_asset_verification"] == "UNMATCHED", "Grok asset invented")
    require(c["optional_tool_state"] == "DRAFT_QD_HOLD"
            and c["optional_tool_live_url"] is None, "draft tool misrepresented")
    require(c["paid_sku_verified"] is False and c["paid_product_url"] is None
            and c["commerce_review_state"] == "UNVERIFIED", "paid offer invented")
    require(c["release_state"] == HOLD and not c["site_cta_production_enabled"]
            and not c["tracking_script_added"], "unapproved live activation")
    return {"state": HOLD, "revenue_per_1000_qualified_humans": None,
            "merchant_confirmed_orders": None, "paid_conversion_verified": False}

def native(root):
    # R460/R462 immutable source inputs. Do not overwrite authors' records.
    snapshot = json.loads(read_pinned(root, "audits/R460_ORIGIN_BRANCH_BLOB_SNAPSHOT.json",
                        "056d14cd97d29b843d52912383c237b9122e73ef"),
                        object_pairs_hook=unique)
    crosswalk = json.loads(read_pinned(root, "sources/crosswalk.json",
                         "d62e493a67dedd23e04cfdf3cce762ef933c6bf9"),
                         object_pairs_hook=unique)
    require(snapshot["release_state"] == HOLD
            and crosswalk["status"] ==
            "DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED", "custody drift")
    families = {}
    for entry in crosswalk["source_files"]:
        raw = read_pinned(root, entry["path"].removeprefix("preparedness/"),
                          entry["git_blob_sha"])
        families[entry["origin"]] = json.loads(raw, object_pairs_hook=unique)["sources"]
    articles = snapshot["candidate"]["articles"]
    require(len(articles) == 35, "original 35-slate missing")
    reviews = {}
    for slug, blobs in sorted(articles.items()):
        base = "content/articles/" + slug + "."
        meta = json.loads(read_pinned(root, base + "meta.json", blobs["meta"]),
                          object_pairs_hook=unique)
        html = read_pinned(root, base + "body.html", blobs["body"]).decode()
        require(meta["slug"] == slug, "article identity drift")
        reviews[slug] = inspect_article(meta, html, families)
    manifest = json.loads((root / "audits/R467_CAMPAIGN_SOURCE_BOUNDARIES.json").read_bytes(),
                          object_pairs_hook=unique)
    return {"articles": reviews, "campaign": inspect_campaign(manifest),
            "release_state": HOLD, "qualified_qd_pass": False, "may_publish": False}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    try:
        report = native(args.root)
    except (Hold, OSError, ValueError, KeyError, TypeError) as exc:
        report = {"release_state": HOLD, "may_publish": False, "error": str(exc)}
    print(json.dumps(report, indent=2, sort_keys=True))
    sys.exit(2)  # Structural success is ALWAYS review HOLD, never QD PASS.

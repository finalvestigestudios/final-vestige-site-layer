#!/usr/bin/env python3
"""R408: E399/E400 source-and-reading-depth custody supplement; ALWAYS HOLD.

No clinical, food-safety, child-privacy, merchant or publication approval.
Reported original SHA256 pins are immutable on CLI; tests may inject fixtures.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import stat
from urllib.parse import urlsplit, parse_qsl

E399_SHA = "75ed08831c138ad3057220df060897e1efe518f1156ea68bb2400c06db898661"
E400_SHA = "7bf191f816da04027ad440e77e0898345c63caabc0edfae733965cebd8f9a107"
LIMIT = 8 * 1024 * 1024
HOSTS = frozenset({"nchfp.uga.edu", "www.cdc.gov", "cdc.gov", "www.fda.gov",
                   "fda.gov", "www.foodsafety.gov", "foodsafety.gov",
                   "extension.umn.edu", "www.fsis.usda.gov", "fsis.usda.gov"})
BLOCK = frozenset({"script", "iframe", "object", "embed", "form", "input", "button",
                   "textarea", "select", "video", "audio", "source", "link",
                   "meta", "base", "svg", "math", "template", "canvas"})
TRACK = frozenset({"gclid", "fbclid", "msclkid", "ref", "affiliate", "aff",
                   "token", "email", "session", "user", "clickid", "mc_cid", "mc_eid"})

def read_bounded(file):
    p = Path(file)
    before = p.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > LIMIT:
        raise ValueError("unsafe file identity or size")
    fd = os.open(p, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or (st.st_ino, st.st_dev) != (before.st_ino, before.st_dev):
            raise ValueError("file identity changed")
        data = b""
        while len(data) <= LIMIT:
            block = os.read(fd, min(65536, LIMIT + 1 - len(data)))
            if not block: break
            data += block
        end = os.fstat(fd)
        if len(data) > LIMIT or (st.st_size, st.st_mtime_ns, st.st_ctime_ns) != (end.st_size, end.st_mtime_ns, end.st_ctime_ns):
            raise ValueError("oversized or changed while reading")
        return data
    finally:
        os.close(fd)

def check_url(value):
    try:
        if any(ord(c) <= 32 for c in value) or any(c in value for c in "\\\"'<>"):
            return "invalid URL characters"
        u = urlsplit(value)
        if u.scheme != "https" or (u.hostname or "").lower() not in HOSTS or u.username or u.password or u.port not in (None, 443):
            return "unapproved citation URL"
        if u.fragment: return "source fragment requires independent review"
        if any(k.lower().startswith("utm_") or k.lower() in TRACK for k, _ in parse_qsl(u.query, keep_blank_values=True)):
            return "tracking or identifying URL query"
        return None
    except (ValueError, UnicodeError, TypeError):
        return "malformed URL"

class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors, self.urls, self.words, self.headings = [], [], [], []
        self.ids = set()
        self.hidden = self.heading = 0
    def handle_starttag(self, tag, attrs):
        if tag in BLOCK: self.errors.append("prohibited element " + tag)
        if len(dict(attrs)) != len(attrs): self.errors.append("duplicate attribute")
        if tag in {"style", "template", "script"}: self.hidden += 1
        if re.fullmatch("h[1-6]", tag): self.heading += 1
        for key, value in attrs:
            v = value or ""
            if key.startswith("on") or key in {"src","srcset","ping","action","formaction","srcdoc"}:
                self.errors.append("active attribute " + key)
            if key == "style" and re.search(r"@import|url\s*\(|expression\s*\(",v,re.I):
                self.errors.append("remote or active CSS")
            if key == "id":
                if not v or v in self.ids: self.errors.append("duplicate/empty HTML id")
                self.ids.add(v)
            if key == "href":
                err = check_url(v)
                if err: self.errors.append(err)
                else: self.urls.append(v)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)
    def handle_endtag(self, tag):
        if tag in {"style", "template", "script"}: self.hidden = max(0, self.hidden - 1)
        if re.fullmatch("h[1-6]", tag): self.heading = max(0, self.heading - 1)
    def handle_data(self, data):
        if self.hidden: return
        value = " ".join(data.split())
        if value:
            self.words.extend(value.split())
            if self.heading: self.headings.append(value)

def audit(e399, e400, *, pins=(E399_SHA, E400_SHA)):
    result = {"decision":"DRAFT_HARD_HOLD", "eligible":False,
              "publication_approved":False, "qualified_food_safety":"NOT_GRANTED",
              "qualified_privacy":"NOT_GRANTED", "receiver_hash_match":False,
              "integrity_ok":False, "errors":[], "review_warnings":[]}
    try:
        if type(pins) is not tuple or len(pins)!=2 or not all(isinstance(x,str) and re.fullmatch("[0-9a-f]{64}",x) for x in pins):
            raise ValueError("invalid digest pin contract")
        originals = [read_bounded(p) for p in (e399,e400)]
        digests = [hashlib.sha256(v).hexdigest() for v in originals]
        result["sha256"] = dict(zip(("E399","E400"),digests))
        if tuple(digests)!=pins: raise ValueError("reported original SHA256 mismatch")
        if digests[0]==digests[1]: raise ValueError("E400 must remain a separate candidate")
        scans=[]
        for name, value in zip(("E399","E400"), originals):
            try: html = value.decode("utf-8","strict")
            except UnicodeError as exc: raise ValueError(name + " is not UTF-8") from exc
            s=Scan(); s.feed(html); s.close(); scans.append(s)
            result["errors"].extend(name+": "+e for e in s.errors)
        old, new = scans
        old_links,new_links=set(old.urls),set(new.urls)
        removed,added=sorted(old_links-new_links),sorted(new_links-old_links)
        result["comparison"]={
            "source_counts":{"E399":len(old_links),"E400":len(new_links)},
            "rendered_words":{"E399":len(old.words),"E400":len(new.words)},
            "removed_source_urls":removed,"added_source_urls":added,
            "duplicate_source_urls_E399":sorted(u for u,n in Counter(old.urls).items() if n>1),
            "duplicate_source_urls_E400":sorted(u for u,n in Counter(new.urls).items() if n>1),
            "headings_E399":old.headings,"headings_E400":new.headings,
            "visible_sha256_E399":hashlib.sha256(" ".join(old.words).encode()).hexdigest(),
            "visible_sha256_E400":hashlib.sha256(" ".join(new.words).encode()).hexdigest()}
        if not old_links or not new_links: result["errors"].append("edition with no source links")
        if removed: result["errors"].append("source citation removed in E400, human review required")
        if added: result["review_warnings"].append("added source URLs need source-to-claim review")
        if len(new.words)<len(old.words): result["review_warnings"].append("reading depth shortened; manual claim/context review required")
        if new.headings!=old.headings: result["review_warnings"].append("headings changed; manual context review required")
        result["receiver_hash_match"]=True
        result["integrity_ok"]=not result["errors"]
    except (ValueError,OSError,TypeError,OverflowError) as exc:
        result["errors"].append(str(exc))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--e399",required=True);p.add_argument("--e400",required=True)
    a=p.parse_args()
    print(json.dumps(audit(a.e399,a.e400),indent=2,sort_keys=True))
    return 2

if __name__=="__main__":
    raise SystemExit(main())

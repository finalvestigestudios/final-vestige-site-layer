#!/usr/bin/env python3
"""Read-only first-party HTML fragment audit. Never equate HTML with browser behavior."""
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

URL = "https://finalvestige.com/focus/"
FRAGMENT = "subscribe-blog"
MAX_BYTES = 1024 * 1024


class FragmentParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.targets = set()
        self.ctas = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("id"):
            self.targets.add(attributes["id"])
        if tag == "a" and attributes.get("name"):
            self.targets.add(attributes["name"])
        if tag == "a" and attributes.get("href") == "#" + FRAGMENT:
            self.ctas.append(attributes.get("data-fv-location", "unlabeled"))


def audit(html):
    """Source check: a client script could still create an anchor after loading."""
    parser = FragmentParser()
    parser.feed(html)
    count = len(parser.ctas)
    present = FRAGMENT in parser.targets
    if count and present:
        verdict = "PASS_SOURCE"
    elif count:
        verdict = "REVIEW_RENDERED_ANCHOR"
    else:
        verdict = "REVIEW_NO_FRAGMENT_CTAS"
    return {"verdict": verdict, "fragment": FRAGMENT, "cta_count": count,
            "cta_locations": parser.ctas, "target_in_html": present,
            "browser_verified": False, "form_submit_tested": False}


class FirstPartyRedirect(HTTPRedirectHandler):
    def __init__(self):
        super().__init__()
        self.hops = 0

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        self.hops += 1
        parsed = urlsplit(newurl)
        if self.hops > 3 or parsed.scheme != "https" or parsed.hostname != "finalvestige.com":
            raise ValueError("Non-first-party, insecure, or excessive redirect")
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def fetch():
    opener = build_opener(FirstPartyRedirect())
    request = Request(URL, headers={"User-Agent": "FinalVestige-QA-FragmentProbe/1.0"})
    with opener.open(request, timeout=10) as response:
        if response.status != 200:
            raise ValueError("Unexpected HTTP response: " + str(response.status))
        if "text/html" not in response.headers.get("Content-Type", "").lower():
            raise ValueError("Expected an HTML document")
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError("HTML exceeds bounded maximum")
        return body.decode("utf-8", errors="replace")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html-file", type=Path, help="Use a sanitized local HTML fixture, not the website")
    args = parser.parse_args(argv)
    try:
        html = args.html_file.read_text(encoding="utf-8") if args.html_file else fetch()
    except (OSError, URLError, HTTPError, ValueError) as exc:
        print(json.dumps({"verdict": "INCONCLUSIVE_FETCH", "reason": str(exc),
                          "browser_verified": False}))
        return 2
    result = audit(html)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["verdict"] == "PASS_SOURCE" else 2


if __name__ == "__main__":
    raise SystemExit(main())

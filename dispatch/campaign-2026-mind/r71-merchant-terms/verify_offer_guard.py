#!/usr/bin/env python3
"""R71 public seller evidence + offline buyer-protection previews. Always fail closed."""
from __future__ import annotations
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
OFFICIAL_HOSTS = {"zen12.com", "hypnosislive.com", "inspire3.com", "affiliates.inspire3.com",
                  "wordpress.com", "www.ftc.gov"}
HARD_HOLDS = {"HOLD_UNSENT", "HOLD_MERCHANT"}

class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags, self.links, self.words = [], [], []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "a":
            self.links.append(dict(attrs).get("href", ""))
    def handle_data(self, data):
        self.words.extend(re.findall(r"\b[\w’-]+\b", data))

def inspect(root: Path = ROOT) -> dict:
    record = json.loads((root / "offer-evidence.json").read_text(encoding="utf-8"))
    assert record["schema_version"] == "r71-public-seller-evidence-v1"
    assert record["status"] == "HOLD_UNSENT"
    assert [x["number"] for x in record["issues"]] == [3, 5]
    assert record["permission_gate"]["final_founder_send_approval"] == "NOT_GRANTED"
    assert all(x == "UNVERIFIED" for k, x in record["permission_gate"].items()
               if k != "final_founder_send_approval")
    sources = record["source_provenance"]
    assert len(sources) >= 10
    for source in sources:
        p = urlparse(source["url"])
        host = (p.hostname or "").lower()
        assert p.scheme == "https" and (host in OFFICIAL_HOSTS or host == "www.nccih.nih.gov"), source["name"]
    z, h = record["issues"]
    assert z["seller_described"]["premium_mp3s"] == 48
    assert z["seller_described"]["beginner_mp3s"] == 24
    assert z["seller_described"]["advanced_mp3s"] == 24
    assert z["seller_terms"]["refund_days"] == 365
    assert "90 days" in z["seller_terms"]["card_refunds_over_90_days"]
    assert h["seller_described"]["duration_minutes"] == 33
    assert h["seller_terms"]["refund_days"] == 14
    assert h["seller_terms"]["refund_album_cap_per_twelve_months"] == 5
    for offer in record["issues"]:
        assert offer["permission"] == "UNVERIFIED"
        assert offer["route"].startswith("[[APPROVED_") and offer["route"].endswith("_REQUIRED]]")
        assert offer["observed_prices_internal_only"]["do_not_quote_in_email"] is True
        for ext in (".txt", ".html"):
            body = (root / f'issue-{offer["number"]:02d}-preview{ext}').read_text(encoding="utf-8")
            assert "HOLD_UNSENT" in body and "HOLD_MERCHANT" in body
            assert "may earn a commission" in body
            assert "DISABLED" in body and "UNVERIFIED" in body
            assert not re.search(r"\$\s*\d", body)
            assert not re.search(r"\[\[APPROVED_", body)
            assert "one-year" in body.lower() or offer["number"] == 5
            assert "five albums" in body.lower() or offer["number"] == 3
            if ext == ".html":
                s = Scan()
                s.feed(body)
                assert body.lstrip().lower().startswith("<!doctype html>")
                assert '<html lang="en">' in body
                assert "role=\"presentation\"" in body
                assert not (set(s.tags) & {"script", "iframe", "img", "form", "button"})
                assert not s.links  # plain seller research URLs, never a CTA
                assert "commission" in [w.lower() for w in s.words[:55]]
    return {"status":"HOLD_UNSENT","commercial":["HOLD_MERCHANT","HOLD_MERCHANT"],"preview_count":4,"sources":len(sources)}

if __name__ == "__main__":
    print(json.dumps(inspect(), sort_keys=True))

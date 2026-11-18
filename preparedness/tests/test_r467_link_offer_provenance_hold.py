"""R467 adversarial review-only link, citation, checkout and source custody tests."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1] / "tools/r467_link_offer_provenance_hold.py"
SPEC = importlib.util.spec_from_file_location("r467", SRC)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)

def families():
    return {**{k: [] for k in gate.ORIGINS},
            "base": [{"id": "agency", "url": "https://ready.gov/plan",
                      "kind": "government", "verified_on": "2026-10-29"}]}

def article(body="<p>Official {{cite:agency}}.</p>"):
    return {"slug": "guide", "status": {"publish": "draft"},
            "source_use": {"agency": "original reading scope"}}, body

def campaign():
    path = Path(__file__).resolve().parents[1] / "audits/R467_CAMPAIGN_SOURCE_BOUNDARIES.json"
    return json.loads(path.read_text())

class Custody(unittest.TestCase):
    def test_free_hold_not_a_merchant_claim(self):
        r = gate.inspect_campaign(campaign())
        self.assertIsNone(r["merchant_confirmed_orders"])
        self.assertIsNone(r["revenue_per_1000_qualified_humans"])
    def test_authored_guide_never_certified(self):
        m, h = article()
        r = gate.inspect_article(m, h, families())
        self.assertFalse(r["qd_pass"])
        self.assertFalse(r["may_publish"])
    def test_literal_source_witness_preserved(self):
        m, h = article('<a href="https://ready.gov/plan">Agency</a>{{cite:agency}}')
        r = gate.inspect_article(m, h, families())
        self.assertEqual(r["outbound_witnesses"][0]["source_witnesses"][0]["id"], "agency")
    def test_outbound_unregistered_is_docketed(self):
        m, h = article('<a href="https://cdc.gov/">CDC</a>{{cite:agency}}')
        r = gate.inspect_article(m, h, families())
        self.assertEqual(len(r["unmatched_outbound_links"]), 1)
    def test_same_url_preserves_two_distinct_witnesses(self):
        f = families()
        f["start"].append({"id": "second", "url": "https://ready.gov/plan"})
        self.assertEqual(len(gate.registry(f)["https://ready.gov/plan"]), 2)
    def test_slash_variant_not_merged(self):
        f = families()
        f["start"].append({"id": "second", "url": "https://ready.gov/plan/"})
        self.assertEqual(len(gate.registry(f)), 2)
    def test_json_duplicate_properties_rejected(self):
        with self.assertRaises(gate.Hold):
            json.loads('{"pay":false,"pay":true}', object_pairs_hook=gate.unique)
    def test_missing_native_checkout_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(gate.Hold):
                gate.native(Path(root))
    def test_reject_dropped_citation(self):
        m, _ = article()
        with self.assertRaises(gate.Hold):
            gate.inspect_article(m, "<p>Uncited.</p>", families())
    def test_reject_false_publication(self):
        m, h = article()
        m["status"]["publish"] = "published"
        with self.assertRaises(gate.Hold):
            gate.inspect_article(m, h, families())

BAD_URLS = {
 "javascript": "javascript:alert(1)",
 "mixed_javascript": "JaVaScRiPt:alert(1)",
 "data": "data:text/html,x",
 "http": "http://ready.gov/plan",
 "protocol_relative": "//ready.gov/plan",
 "userinfo": "https://user@ready.gov/plan",
 "password": "https://user:pw@ready.gov/plan",
 "private_ipv4": "https://192.168.1.1/",
 "loopback_ipv4": "https://127.0.0.1/",
 "metadata_server": "https://169.254.169.254/",
 "private_ipv6": "https://[fd00::1]/",
 "loopback_ipv6": "https://[::1]/",
 "localhost": "https://localhost/",
 "localdomain": "https://localhost.localdomain/",
 "space": "https://ready.gov/ bad",
 "tab": "https://ready.gov/\tbad",
 "newline": "https://ready.gov/\nbad",
 "backslash": "https://ready.gov\\evil.test/",
 "percent_authority": "https://ready%2egov/",
 "port": "https://ready.gov:8888/",
 "bad_port": "https://ready.gov:99999/",
 "no_tld": "https://local/",
 "trailing_dot": "https://ready.gov./",
 "double_dot": "https://ready..gov/",
 "html": "https://ready.gov/<script>",
 "quote": 'https://ready.gov/"x',
 "empty": ""
}
GOOD_URLS = {
 "official": "https://ready.gov/plan",
 "trailing_slash": "https://ready.gov/plan/",
 "query": "https://ready.gov/plan?x=1",
 "fragment": "https://ready.gov/plan#contact",
 "port_443": "https://ready.gov:443/plan",
 "subdomain": "https://www.redcross.org/",
 "global_ipv4": "https://8.8.8.8/",
 "global_ipv6": "https://[2606:4700:4700::1111]/"
}
BAD_HTML = {
 "script": "<script>alert(1)</script>",
 "iframe": '<iframe src="https://ready.gov/plan"></iframe>',
 "form": '<form action="https://ready.gov/plan"></form>',
 "input": '<input name="email">',
 "meta_refresh": '<meta http-equiv="refresh" content="0">',
 "embed": '<embed src="https://ready.gov/plan">',
 "object": '<object data="https://ready.gov/plan"></object>',
 "onclick": '<a href="https://ready.gov/plan" onclick="track()">Link</a>',
 "data_href": '<a href="data:text/html,x">Link</a>',
 "script_href": '<a href="javascript:alert(1)">Link</a>',
 "out_of_scope_link": '<a href="/admin/">Link</a>',
 "checkout_payhip": '<a href="https://payhip.com/b/x">Buy</a>',
 "checkout_gumroad": '<a href="https://gumroad.com/l/x">Buy</a>',
 "checkout_stripe": '<a href="https://checkout.stripe.com/pay/x">Buy</a>',
 "checkout_paypal": '<a href="https://paypal.com/pay/x">Buy</a>',
 "checkout_amazon": '<a href="https://amazon.com/dp/x">Buy</a>',
 "checkout_subdomain": '<a href="https://shop.payhip.com/b/x">Buy</a>',
 "duplicate_href": '<a href="https://ready.gov/plan" href="https://evil.test/">Link</a>',
 "unsafe_blank": '<a href="https://ready.gov/plan" target="_blank">Link</a>',
 "noreferrer_only": '<a href="https://ready.gov/plan" target="_blank" rel="noreferrer">Link</a>',
 "noopener_only": '<a href="https://ready.gov/plan" target="_blank" rel="noopener">Link</a>',
 "srcdoc": '<p srcdoc="x">text</p>',
 "tracking_ping": '<a href="https://ready.gov/plan" ping="https://evil.test">x</a>',
 "css_import": '<p style="@import url(https://evil.test)">x</p>',
 "css_expression": '<p style="width:expression(x)">x</p>',
 "css_url": '<p style="background:url(https://evil.test)">x</p>',
 "missing_href": '<a>Link</a>'
}
BAD_CAMPAIGN = {
 "fictitious_grok_asset": ("published_grok_asset_id", "fake123"),
 "fictitious_social_verification": ("social_asset_verification", "VERIFIED"),
 "wrong_free_destination": ("free_destination", "https://finalvestige.com/checkout/"),
 "retired_water_campaign": ("topic", "water-resilience-manual"),
 "tool_misrepresented_live": ("optional_tool_state", "LIVE"),
 "tool_linked": ("optional_tool_live_url", "https://example.com/tool.pdf"),
 "fictitious_paid_sku": ("paid_sku_verified", True),
 "fictitious_checkout": ("paid_product_url", "https://payhip.com/b/fiction"),
 "false_merchant_approval": ("commerce_review_state", "VERIFIED"),
 "false_qd_pass": ("release_state", "QD_PASS"),
 "unauthorized_site_cta": ("site_cta_production_enabled", True),
 "unauthorized_tracking": ("tracking_script_added", True)
}

def register(name, samples, tester):
    for title, value in samples.items():
        def case(self, sample=value):
            tester(self, sample)
        setattr(Custody, "test_" + name + "_" + title, case)

def bad_url(self, value):
    with self.assertRaises(gate.Hold):
        gate.https_host(value)

def good_url(self, value):
    self.assertTrue(gate.https_host(value))

def bad_html(self, value):
    meta, _ = article()
    with self.assertRaises(gate.Hold):
        gate.inspect_article(meta, value + "{{cite:agency}}", families())

def bad_campaign(self, field):
    obj = campaign()
    obj[field[0]] = field[1]
    with self.assertRaises(gate.Hold):
        gate.inspect_campaign(obj)

register("reject_url", BAD_URLS, bad_url)
register("valid_url", GOOD_URLS, good_url)
register("reject_html", BAD_HTML, bad_html)
register("reject_campaign", BAD_CAMPAIGN, bad_campaign)

if __name__ == "__main__":
    unittest.main()

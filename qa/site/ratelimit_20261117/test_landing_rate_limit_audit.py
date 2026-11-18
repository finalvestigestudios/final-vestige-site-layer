"""Read-only, synthetic sample tests; no production requests, logs or PII."""
import unittest

from landing_rate_limit_audit import audit, category, normalize_path, ua_claim


def row(path="/focus/", code=429, agent="Mozilla/5.0"):
    return {"request_path": path, "status": code, "request_type": "GET", "user_agent": agent}


def page(rows, **kwargs):
    return {"type": "web", "total": len(rows), "entries": rows,
            "window_start": "2026-11-18T06:00:00Z", "window_end": "2026-11-18T07:00:00Z", **kwargs}


class TestRateLimitQA(unittest.TestCase):
    def test_focus_flags_review(self):
        r = audit(page([row()]))
        self.assertEqual(r["admission"], "REVIEW")
        self.assertEqual(r["rate_limited_conversion_entries"], {"/focus/": 1})

    def test_homepage_flags_review(self):
        self.assertEqual(audit(page([row("/")]))["rate_limited_conversion_entries"], {"/": 1})

    def test_dispatch_collection(self):
        r = audit(page([row("/dispatch/"), row("/collection/")]))
        self.assertEqual(set(r["rate_limited_conversion_entries"]), {"/dispatch/", "/collection/"})

    def test_robots_sitemap_are_discovery(self):
        r = audit(page([row("/robots.txt"), row("/news-sitemap.xml")]))
        self.assertEqual(len(r["rate_limited_discovery_paths"]), 2)

    def test_bot_claim_not_verified_crawler(self):
        r = audit(page([row(agent="CLAUDEBOT/1.0")]))
        self.assertIn("claims_claudebot", r["unverified_user_agent_claims_on_429"])
        self.assertIn("crawler authentication, search ranking loss, or cause of throttling", r["not_established"])

    def test_probe_not_conversion(self):
        r = audit(page([row("/.git/config"), row("/composer.lock")]))
        self.assertEqual(r["admission"], "NO_REVIEW_TRIGGER_IN_SUPPLIED_SAMPLE")
        self.assertEqual(r["path_categories_in_supplied_sample"]["sensitive_probe_pattern"], 2)

    def test_sensitive_success_triggers_manual_review(self):
        r = audit(page([row("/.env", code=200)]))
        self.assertEqual(r["sensitive_probe_2xx_needing_manual_review"], 1)
        self.assertEqual(r["admission"], "REVIEW")

    def test_mismatched_pagination_windows_not_complete(self):
        p1 = page([row()], total=2, next_cursor="opaque")
        p2 = page([row("/robots.txt")], total=2)
        p2["window_end"] = "2026-11-18T08:00:00Z"
        self.assertFalse(audit([p1,p2])["log_enumeration_complete"])

    def test_vendor_is_probe(self):
        self.assertEqual(category("/vendor/autoload.php"), "sensitive_probe_pattern")

    def test_browser_ua_not_human_proof(self):
        self.assertEqual(ua_claim("Mozilla/5.0 Chrome/99.0"), "other_or_unknown")

    def test_ignore_non429_entries_for_trigger(self):
        self.assertEqual(audit(page([row(code=200)]))["admission"], "NO_REVIEW_TRIGGER_IN_SUPPLIED_SAMPLE")

    def test_incomplete_cursor(self):
        self.assertFalse(audit(page([row()], total=20, next_cursor="opaque"))["log_enumeration_complete"])

    def test_incomplete_hidden_cap(self):
        self.assertFalse(audit(page([row()], total=20))["log_enumeration_complete"])

    def test_lower_bound(self):
        self.assertFalse(audit(page([row()], total_is_lower_bound=True))["log_enumeration_complete"])

    def test_wrapped_payload(self):
        self.assertEqual(audit({"structuredContent": page([row()])})["records_examined"], 1)

    def test_multiple_pages(self):
        self.assertEqual(audit([page([row()], total=2, next_cursor="opaque"), page([row("/robots.txt")], total=2)])["records_examined"], 2)
        self.assertTrue(audit([page([row()], total=2, next_cursor="opaque"), page([row("/robots.txt")], total=2)])["log_enumeration_complete"])

    def test_bad_method_fails_closed(self):
        bad = row(); bad["request_type"] = "GARBAGE"
        with self.assertRaises(ValueError): audit(page([bad]))

    def test_missing_status_fails_closed(self):
        bad = row(); del bad["status"]
        with self.assertRaises(ValueError): audit(page([bad]))

    def test_bad_path_fails_closed(self):
        with self.assertRaises(ValueError): audit(page([row("https://example.com/focus/")]))

    def test_null_path_fails_closed(self):
        with self.assertRaises(ValueError): normalize_path(None)

    def test_paths_normalized(self):
        self.assertEqual(normalize_path("/Focus/?utm_source=x"), "/focus/")

    def test_no_ip_or_email_in_aggregate(self):
        r = row(); r["ip_address"]="203.0.113.10"; r["email"]="someone@example.com"
        result = str(audit(page([r])))
        self.assertNotIn("203.0.113.10", result)
        self.assertNotIn("someone@example.com", result)

    def test_no_sales_inferred(self):
        x = str(audit(page([row()])))
        self.assertIn("not_established", x)
        self.assertIn("realized revenue", x)

    def test_zero_rows_is_explicitly_sample_only(self):
        r = audit(page([]))
        self.assertEqual(r["records_examined"], 0)
        self.assertEqual(r["admission"], "NO_REVIEW_TRIGGER_IN_SUPPLIED_SAMPLE")


if __name__ == "__main__":
    unittest.main()

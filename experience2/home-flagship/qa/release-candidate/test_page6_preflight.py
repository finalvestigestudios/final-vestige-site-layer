"""Adversarial offline tests for the live-homepage readback/rollback contract."""
import hashlib
import unittest

from page6_preflight import SHA1, audit, split_top_level


def fixture():
    blocks = [
        '<!-- wp:html -->\n' + ''.join(f'<span class="fv-margin-strip__item">{i}</span>' for i in range(72)) + '\n<!-- /wp:html -->',
        '<!-- wp:html -->\n<section class="fv-studios-hero">Old hero</section>\n<!-- /wp:html -->',
        '<!-- wp:html -->\n<section class="fv-focus-cta"><a href="/focus/">Free fieldbook</a></section>\n<!-- /wp:html -->',
        '<!-- wp:group {"className":"fv-home-shell"} -->\n<div class="fv-home-shell"><a href="/focus/">Guide</a><!-- wp:jetpack/subscriptions {"className":"is-style-split"} /--></div>\n<!-- /wp:group -->',
        '<!-- wp:html -->\n<section>Enter the record</section>\n<!-- /wp:html -->',
        '<!-- wp:html -->\n<script type="application/ld+json">{}</script>\n<!-- /wp:html -->',
    ]
    raw = ''.join(blocks)
    lock = {"id": 6, "status": "publish", "modified": "2026-10-30T09:14:14",
            "content_hash": SHA1(raw),
            "blocks": tuple(("core/group" if i == 3 else "core/html", SHA1(b)) for i, b in enumerate(blocks))}
    page = {"data": {"id": 6, "status": "publish", "modified": lock["modified"], "content": {"raw": raw}}}
    sections = {"data": {"id": 6, "modified": lock["modified"], "content_hash": lock["content_hash"],
             "classic_content": False, "sections": [
                 {"index": i, "name": kind, "block_hash": hash_}
                 for i, (kind, hash_) in enumerate(lock["blocks"]) ]}}
    replacement = '<!-- wp:html -->\n<div data-fv-home-flagship><style>body{color:white}</style><script>0</script></div>\n<!-- /wp:html -->'
    return page, sections, replacement, lock


class Page6PreflightTests(unittest.TestCase):
    def test_synthetic_exact_readbacks_have_provable_rollback(self):
        p, s, r, lock = fixture()
        out = audit(p, s, r, lock=lock)
        self.assertEqual(out["status"], "PREVIEW_ROLLBACK_BYTE_VERIFIED_NOT_PUBLISHED")
        self.assertEqual(out["publication"], "HOLD")
        self.assertEqual(out["margins_records"], 72)
        self.assertEqual(out["preserved_block_indices"], [0, 2, 3, 4, 5])
        self.assertEqual(out["rollback_full_page_sha256"], hashlib.sha256(p["data"]["content"]["raw"].encode()).hexdigest())

    def test_live_hero_mutation_fails_even_if_sections_snapshot_stale(self):
        p, s, r, lock = fixture()
        p["data"]["content"]["raw"] = p["data"]["content"]["raw"].replace('Old hero', 'Injected hero')
        with self.assertRaisesRegex(ValueError, 'HOLD_LIVE_PAGE_CONTENT_DRIFT'):
            audit(p, s, r, lock=lock)

    def test_modified_token_mismatch_is_rejected(self):
        p, s, r, lock = fixture()
        s["data"]["modified"] = '2026-11-02T09:00:00'
        with self.assertRaisesRegex(ValueError, 'HOLD_SECTION_ID_OR_MODIFIED_DRIFT'):
            audit(p, s, r, lock=lock)

    def test_redistributed_block_hashes_are_rejected(self):
        p, s, r, lock = fixture()
        s["data"]["sections"][0]["block_hash"] = s["data"]["sections"][1]["block_hash"]
        with self.assertRaisesRegex(ValueError, 'HOLD_BLOCK_0_DRIFT'):
            audit(p, s, r, lock=lock)

    def test_one_more_root_section_fails(self):
        p, s, r, lock = fixture()
        s["data"]["sections"].append({"index": 6, "name": "core/html", "block_hash": "a" * 40})
        with self.assertRaisesRegex(ValueError, 'HOLD_TOP_LEVEL_BLOCK_COUNT_DRIFT'):
            audit(p, s, r, lock=lock)

    def test_subscription_loss_fails_even_with_new_self_consistent_lock(self):
        p, s, r, _ = fixture()
        raw = p["data"]["content"]["raw"].replace('<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->', '')
        self._expect_semantic_hold(raw, r, 'HOLD_JETPACK_SUBSCRIPTION_MISSING_OR_DUPLICATED')

    def test_margins_count_loss_fails_even_with_new_self_consistent_lock(self):
        p, s, r, _ = fixture()
        raw = p["data"]["content"]["raw"].replace('<span class="fv-margin-strip__item">71</span>', '')
        self._expect_semantic_hold(raw, r, 'HOLD_MARGINS_COUNT')

    def test_focus_loss_fails_even_with_new_self_consistent_lock(self):
        p, s, r, _ = fixture()
        raw = p["data"]["content"]["raw"].replace('href="/focus/"', 'href="/removed/"', 1)
        self._expect_semantic_hold(raw, r, 'HOLD_FOCUS_LINKS_NOT_PRESERVED')

    def _expect_semantic_hold(self, raw, replacement, reason):
        p, s, _, lock = fixture()
        blocks = split_top_level(raw)
        p["data"]["content"]["raw"] = raw
        s["data"]["content_hash"] = lock["content_hash"] = SHA1(raw)
        lock["blocks"] = tuple((k, SHA1(b)) for k, b in blocks)
        s["data"]["sections"] = [{"index": i, "name": k, "block_hash": SHA1(b)} for i, (k, b) in enumerate(blocks)]
        with self.assertRaisesRegex(ValueError, reason):
            audit(p, s, replacement, lock=lock)

    def test_second_replacement_block_rejected(self):
        p, s, r, lock = fixture()
        with self.assertRaisesRegex(ValueError, 'HOLD_REPLACEMENT_NOT_ONE_HTML_BLOCK'):
            audit(p, s, r + r, lock=lock)

    def test_missing_inline_interactive_payload_rejected(self):
        p, s, r, lock = fixture()
        with self.assertRaisesRegex(ValueError, 'HOLD_FLAGSHIP_DELIVERY_INCOMPLETE'):
            audit(p, s, '<!-- wp:html -->\n<div data-fv-home-flagship></div>\n<!-- /wp:html -->', lock=lock)

    def test_unbalanced_nested_gutenberg_comments_rejected(self):
        with self.assertRaisesRegex(ValueError, 'HOLD_BLOCK_NESTING_INVALID'):
            split_top_level('<!-- wp:group --><!-- wp:paragraph --><!-- /wp:group -->')

    def test_script_or_trailing_text_outside_root_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'HOLD_UNOWNED_PAGE_CONTENT'):
            split_top_level('<script>alert(1)</script><!-- wp:html -->ok<!-- /wp:html -->')


if __name__ == '__main__':
    unittest.main()

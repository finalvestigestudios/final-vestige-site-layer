import unittest
from offer_proximity_gate import audit

URL = 'https://finalvestige.com/mind/zen12-guide/'
LINK = '<a href="'+URL+'">Read our evidence review</a>'
DISC = 'If you buy through the linked guide, Final Vestige may earn a commission.'

def fixture(body=None, plain=None):
    return audit('<html><body><main><p>'+(body if body is not None else DISC+' '+LINK)+'</p></main></body></html>', plain if plain is not None else DISC+' Read our evidence review (link pending).')

class Tests(unittest.TestCase):
    def test_honest_draft_is_still_held(self):
        a=fixture(); self.assertEqual(a['release_decision'],'HOLD_UNSENT'); self.assertEqual(a['structural_draft_readiness'],'INSPECTION_ONLY')
    def test_footer_only_disclosure_is_not_adjacent(self):
        a=fixture(LINK+'<p>'+'x'*350+'</p><footer>'+DISC+'</footer>');self.assertFalse(a['checks']['disclosure_adjacent_to_every_qualifying_html_cta'])
    def test_hidden_disclosure_rejected(self):
        a=fixture('<span hidden>'+DISC+'</span>'+LINK);self.assertFalse(a['checks']['disclosure_adjacent_to_every_qualifying_html_cta'])
    def test_aria_hidden_disclosure_rejected(self):
        a=fixture('<span aria-hidden="true">'+DISC+'</span>'+LINK);self.assertFalse(a['checks']['disclosure_adjacent_to_every_qualifying_html_cta'])
    def test_style_hidden_disclosure_rejected(self):
        a=fixture('<span style="display:none">'+DISC+'</span>'+LINK);self.assertFalse(a['checks']['disclosure_adjacent_to_every_qualifying_html_cta'])
    def test_near_but_not_linked_to_merchants_still_hold(self):
        a=fixture('<a href="https://zen12.com/">Buy now</a> '+DISC);self.assertFalse(a['checks']['exactly_one_firstparty_guide_cta'])
    def test_two_qualifying_links_fail_single_cta(self):
        a=fixture(DISC+LINK+LINK);self.assertFalse(a['checks']['exactly_one_firstparty_guide_cta'])
    def test_unverified_price_or_offer_claims_fail(self):
        a=fixture(DISC+' Offer ends tonight. '+LINK);self.assertFalse(a['checks']['no_risky_unverified_claim_phrases'])
    def test_bracket_placeholder_fails(self):
        a=fixture(DISC+LINK+' [[APPROVED_POSTAL_REQUIRED]]');self.assertFalse(a['checks']['no_unresolved_bracket_placeholders'])
    def test_direct_merchant_earning_link_rejected(self):
        a=fixture(DISC+LINK+'<a href="https://www.awin1.com/cread.php">BUY</a>');self.assertFalse(a['checks']['no_direct_affiliate_or_tracking_links'])
    def test_no_plaintext_disclosure_fails(self):
        a=fixture(plain='Please read the guide.');self.assertFalse(a['checks']['plain_text_contains_disclosure'])
    def test_unpublished_relative_guide_not_a_link(self):
        a=fixture(DISC+'<a href="/mind/zen12-guide/">Guide</a>');self.assertEqual(a['qualifying_offer_guide_count'],0)
    def test_hypnosis_guide_detected(self):
        a=fixture(DISC+'<a href="https://finalvestige.com/mind/hypnosis-live-guide/">Review</a>');self.assertEqual(a['qualifying_offer_guide_count'],1)
    def test_non_vetted_guide_not_accepted(self):
        a=fixture(DISC+'<a href="https://finalvestige.com/focus/">Fieldbook</a>');self.assertEqual(a['qualifying_offer_guide_count'],0)
    def test_link_tracking_query_not_accepted(self):
        a=fixture(DISC+'<a href="'+URL+'?utm_source=dispatch">Guide</a>');self.assertEqual(a['qualifying_offer_guide_count'],0)
    def test_malformed_html_fails(self):
        a=audit('<p>'+DISC+LINK+'</p><p>forgot to close',DISC);self.assertFalse(a['checks']['html_is_well_formed_enough_for_preflight'])
    def test_html_script_disclosure_not_counted(self):
        a=fixture('<script>'+DISC+'</script>'+LINK);self.assertFalse(a['checks']['disclosure_adjacent_to_every_qualifying_html_cta'])

if __name__ == '__main__': unittest.main(verbosity=2)

import unittest
from guest_snapshot_classifier import analyze_markup, classify_subscriber_aggregates

class SnapshotTests(unittest.TestCase):
    def test_real_email_form(self):
        v=analyze_markup('<form action="/subscribe"><label>Email<input type="email" name="email"></label><button>Subscribe</button></form>')
        self.assertEqual(v['form_status'],'EMAIL_SUBMIT_CONTROL_OBSERVED_NOT_TESTED')
        self.assertFalse(v['browser_guest_verified'])
        self.assertIsNone(v['confirmed_signup'])
    def test_self_link_from_wp_view_is_not_proof_of_guest_failure(self):
        v=analyze_markup('<a class="wp-block-jetpack-subscriptions" href="https://finalvestige.com/?post_type=page&amp;p=523">Subscribe</a>')
        self.assertEqual(v['form_status'],'SELF_LINK_FALLBACK_OBSERVED_GUEST_UNKNOWN')
        self.assertIsNone(v['eligible_recipients'])
    def test_email_input_but_no_submit(self):
        self.assertEqual(analyze_markup('<form><input type="email"></form>')['form_status'],'EMAIL_INPUT_WITHOUT_SUBMIT_OBSERVED')
    def test_ordinary_link_no_evidence(self):
        self.assertEqual(analyze_markup('<a href="/focus/">Read</a>')['form_status'],'NO_EMAIL_CONTROL_OBSERVED_GUEST_UNKNOWN')
    def test_submit_input(self):
        self.assertEqual(analyze_markup('<form><input type="email"><input type="submit"></form>')['submit_control_count'],1)
    def test_submit_not_in_form(self):
        self.assertEqual(analyze_markup('<form><input type="email"></form><button>subscribe</button>')['submit_control_count'],0)
    def test_email_input_outside_form_not_counted(self):
        self.assertEqual(analyze_markup('<input type="email"><a href="/">Sub</a>')['email_form_count'],0)
    def test_script_without_html_unverified(self):
        self.assertEqual(analyze_markup('<script>document.write("<form>")</script>')['form_status'],'NO_EMAIL_CONTROL_OBSERVED_GUEST_UNKNOWN')
    def test_invalid_html_type(self):
        with self.assertRaises(ValueError):analyze_markup(None)
    def test_oversized(self):
        with self.assertRaises(ValueError):analyze_markup('x'*2_000_001)
    def test_all_inferred_events_unknown(self):
        x=analyze_markup('<form><input type="email"><button></button></form>')
        for k in ('confirmed_signup','welcome_received','eligible_recipients','unsubscribe_functional','paid_orders'):
            self.assertIsNone(x[k])
    def test_no_submissions_ever(self):
        self.assertFalse(analyze_markup('<form method="post"><input type="email"><button></button></form>')['submission_performed'])
    def test_original_overlapping_counters(self):
        x=classify_subscriber_aggregates({'total':3,'confirmed':3,'unconfirmed':2},{'wpcom':3,'email':0})
        self.assertTrue(x['overlapping_or_nonexclusive'])
        self.assertIsNone(x['distinct_eligible_inboxes'])
    def test_even_apparently_clean_counters_no_lead(self):
        x=classify_subscriber_aggregates({'total':3,'confirmed':3,'unconfirmed':0},{'wpcom':3,'email':0})
        self.assertFalse(x['overlapping_or_nonexclusive']);self.assertIsNone(x['verified_confirmed_signup_events'])
    def test_bogus_bool_as_counter(self):
        with self.assertRaises(ValueError):classify_subscriber_aggregates({'total':True,'confirmed':1,'unconfirmed':0},{'wpcom':0,'email':1})
    def test_negative_counters(self):
        with self.assertRaises(ValueError):classify_subscriber_aggregates({'total':-1,'confirmed':1,'unconfirmed':0},{'wpcom':0,'email':0})
    def test_no_audience_addition(self):
        x=classify_subscriber_aggregates({'total':3,'confirmed':3,'unconfirmed':2},{'wpcom':3,'email':0})
        self.assertTrue(x['count_addition_forbidden']);self.assertFalse(x['send_authorized'])

if __name__=='__main__': unittest.main()

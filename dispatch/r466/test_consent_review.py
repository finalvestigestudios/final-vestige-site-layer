import unittest
from consent_review import summarize

A = ('youtube', 'history_2026_11', 'asset_001')
B = ('tiktok', 'history_2026_11', 'asset_002')


def receipt(**changes):
    return dict(kind='provider_transition', key='synthetic-one', before='pending',
                after='confirmed', proof='confirmation_receipt', email_verified=True,
                consent=True, prior_confirmed=False, source=A[0], campaign=A[1],
                asset=A[2], join_verified=True) | changes


class ConsentReview(unittest.TestCase):
    def run_model(self, *events, complete=True):
        return summarize(events, (A, B), complete)

    def test_pending_confirmed(self):
        self.assertEqual(self.run_model(receipt())['confirmed_signup'], 1)

    def test_verified_wp_account_path(self):
        self.assertEqual(self.run_model(receipt(before='absent', proof='verified_account_subscription_receipt'))['confirmed_signup'], 1)

    def test_direct_path_without_receipt(self):
        self.assertEqual(self.run_model(receipt(before='absent'))['confirmed_signup'], 0)

    def test_reader_only(self):
        self.assertEqual(self.run_model(receipt(after='reader'))['confirmed_signup'], 0)

    def test_prior_subscriber(self):
        self.assertEqual(self.run_model(receipt(prior_confirmed=True))['confirmed_signup'], 0)

    def test_unknown_prior(self):
        self.assertEqual(self.run_model(receipt(prior_confirmed=None))['confirmed_signup'], 0)

    def test_consent_missing(self):
        self.assertEqual(self.run_model(receipt(consent=False))['confirmed_signup'], 0)

    def test_unverified_email(self):
        self.assertEqual(self.run_model(receipt(email_verified=False))['confirmed_signup'], 0)

    def test_form_and_pdf_not_leads(self):
        self.assertEqual(self.run_model(*[{'kind': k} for k in ('form_start', 'signup_submit', 'pdf_download', 'welcome_received', 'email_click')])['confirmed_signup'], 0)

    def test_duplicate(self):
        self.assertEqual(self.run_model(receipt(), receipt())['confirmed_signup'], 1)

    def test_distinct(self):
        self.assertEqual(self.run_model(receipt(), receipt(key='synthetic-two'))['confirmed_signup'], 2)

    def test_incomplete(self):
        r = self.run_model(receipt(), complete=False)
        self.assertIsNone(r['confirmed_signup'])
        self.assertEqual(r['observed_confirmations'], 1)

    def test_unverified_join(self):
        self.assertEqual(self.run_model(receipt(join_verified=False))['source_attributed'], 0)

    def test_unknown_asset(self):
        self.assertEqual(self.run_model(receipt(asset='unknown'))['source_attributed'], 0)

    def test_verified_join(self):
        self.assertEqual(self.run_model(receipt())['source_attributed'], 1)

    def test_conflicting_join(self):
        r = self.run_model(receipt(), receipt(source=B[0], campaign=B[1], asset=B[2]))
        self.assertEqual((r['confirmed_signup'], r['source_attributed'], r['attribution_conflicts']), (1, 0, 1))

    def test_late_join(self):
        self.assertEqual(self.run_model(receipt(join_verified=False), receipt())['source_attributed'], 1)

    def test_reject_unknown_field(self):
        with self.assertRaises(ValueError):
            self.run_model(receipt(email='example@example.invalid'))

    def test_reject_real_alias(self):
        with self.assertRaises(ValueError):
            self.run_model(receipt(key='provider-123'))

    def test_reject_unknown_event(self):
        with self.assertRaises(ValueError):
            self.run_model({'kind': 'purchase'})


if __name__ == '__main__':
    unittest.main()

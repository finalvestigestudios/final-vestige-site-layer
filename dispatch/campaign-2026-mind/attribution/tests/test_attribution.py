import csv
import io
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import attribution as a


def csvtext(**kw):
    row = dict(issue="01",wp_recipients="20",wp_unique_email_clickers="3",first_party_page_views="",
               outbound_merchant_clicks="",verified_merchant_purchases="",send_approval_ref="FVREV-20261030#01",
               merchant_report_ref="")
    row.update(kw)
    f = io.StringIO()
    w = csv.DictWriter(f, fieldnames=a.COLUMNS)
    w.writeheader();w.writerow(row)
    return f.getvalue()


class AttributionTests(unittest.TestCase):
    def test_six_unique_plan(self):
        self.assertEqual([v['issue'] for v in a.plan()['editions']], [f'{i:02d}' for i in range(1,7)])

    def test_all_unsent(self):
        self.assertTrue(all(v['state']=='HOLD_UNSENT' for v in a.plan()['editions']))

    def test_all_merchant_urls_null(self):
        self.assertTrue(all(v['merchant_affiliate_url'] is None for v in a.plan()['editions']))

    def test_four_editorial_two_commercial(self):
        x = [v['kind'] for v in a.plan()['editions']]
        self.assertEqual(x.count('editorial'),4); self.assertEqual(x.count('commercial_review_pending'),2)

    def test_commercial_guide_urls_blocked(self):
        self.assertIsNone(a.proposed_first_party_url('03')); self.assertIsNone(a.proposed_first_party_url('05'))

    def test_first_party_utm_nocloak(self):
        z=a.proposed_first_party_url('01')
        self.assertIn('finalvestige.com/free-resources/',z)
        self.assertIn('utm_content=issue_01',z)
        self.assertNotIn('inspire3.com',z)

    def test_unknown_issue_fails(self):
        with self.assertRaises(ValueError): a.proposed_first_party_url('99')

    def test_absent_csv_no_fabrication(self):
        r=a.summarize([])
        self.assertEqual(r['observed_issues'],0)
        self.assertTrue(all(v['wp_recipients'] is None for v in r['issues']))

    def test_valid_aggregate(self):
        r=a.parse_rows(csvtext()); self.assertEqual(r[0]['wp_unique_email_clickers'],3)

    def test_no_rate_under_twenty(self):
        r=a.summarize(a.parse_rows(csvtext(wp_recipients='2',wp_unique_email_clickers='1')))
        self.assertIsNone(r['issues'][0]['descriptive_click_rate'])

    def test_descriptive_rate_not_infer_sales(self):
        r=a.summarize(a.parse_rows(csvtext())); self.assertEqual(r['issues'][0]['descriptive_click_rate'],'15.0%')
        self.assertIsNone(r['issues'][0]['verified_merchant_purchases'])

    def test_recipient_count_not_delivered(self):
        self.assertIn('not necessarily delivered',a.summarize([])['caveat'])

    def test_raw_emails_rejected(self):
        with self.assertRaises(ValueError):a.parse_rows(csvtext().replace('issue,','email,issue,'))

    def test_extra_raw_columns_rejected(self):
        with self.assertRaises(ValueError):a.parse_rows(csvtext().replace('send_approval_ref,','subscriber_address,send_approval_ref,'))

    def test_non_integer_rejected(self):
        for value in ('-1','1.1','x','=SUM(A1:A2)','01','1e3'):
            with self.subTest(value=value),self.assertRaises(ValueError): a.parse_rows(csvtext(wp_recipients=value))

    def test_clickers_above_recipients_rejected(self):
        with self.assertRaises(ValueError): a.parse_rows(csvtext(wp_unique_email_clickers='21'))

    def test_unknown_issue_rejected(self):
        with self.assertRaises(ValueError):a.parse_rows(csvtext(issue='07'))

    def test_duplicate_issue_rejected(self):
        with self.assertRaises(ValueError):a.parse_rows(csvtext()+csvtext().splitlines()[-1]+'\n')

    def test_without_send_approval_proof_fails(self):
        with self.assertRaises(ValueError):a.parse_rows(csvtext(send_approval_ref=''))

    def test_fake_send_approval_proof_fails(self):
        with self.assertRaises(ValueError):a.parse_rows(csvtext(send_approval_ref='fake123456'))

    def test_identifying_proof_fails(self):
        with self.assertRaises(ValueError):a.parse_rows(csvtext(send_approval_ref='someone@example.com'))

    def test_unverified_sale_fails(self):
        with self.assertRaises(ValueError):a.parse_rows(csvtext(issue='03',verified_merchant_purchases='1'))

    def test_editorial_affiliate_sale_fails(self):
        with self.assertRaises(ValueError):a.parse_rows(csvtext(verified_merchant_purchases='1',merchant_report_ref='FVCONF-123456'))

    def test_commercial_with_merchant_proof_does_not_unlock_guide(self):
        x=a.parse_rows(csvtext(issue='03',verified_merchant_purchases='1',merchant_report_ref='FVCONF-123456'))
        self.assertEqual(x[0]['verified_merchant_purchases'],1)
        self.assertIsNone(a.proposed_first_party_url('03'))

    def test_script_has_no_network_imports(self):
        src=pathlib.Path(a.__file__).read_text()
        for bad in ('import requests','import smtplib','import urllib.request','import subprocess','import socket','wpcom_site','mail.send'):
            self.assertNotIn(bad,src)

    def test_preview_six_issues_and_accessibility(self):
        z=a.html_report(a.summarize([]));self.assertEqual(z.count("<tr><th scope='row'>"),6)
        self.assertIn("lang='en'",z);self.assertIn('scope=\'col\'',z);self.assertIn('Not measured',z)
        self.assertNotIn('mailto:',z);self.assertNotIn('<script',z)

    def test_template_is_only_header(self):
        rows=(pathlib.Path(a.__file__).parent/'aggregate_template.csv').read_text().splitlines()
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0],','.join(a.COLUMNS))

if __name__ == '__main__':unittest.main()

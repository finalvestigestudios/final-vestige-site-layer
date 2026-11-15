"""Native offline QA: exact original source, MIME safety and adversarial release gates."""
from email import policy
from email.parser import BytesParser
import importlib.util
from pathlib import Path
import json
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r367m', HERE/'build_review_mime.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
MASTER = HERE.parent/'campaign-2026-mind'
if not MASTER.exists():
    MASTER = HERE.parent/'master'/'dispatch'/'campaign-2026-mind'


class ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        cls.summaries = mod.generate(MASTER, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_six_exact_issues(self):
        self.assertEqual([x['issue'] for x in self.summaries], [1,2,3,4,5,6])

    def test_four_editorial_two_commercial(self):
        self.assertEqual([x['kind'] for x in self.summaries].count('commercial-review-pending'),2)

    def test_manifest_all_hold(self):
        self.assertTrue(all(x['release']=='HOLD_UNSENT' for x in self.summaries))

    def test_merchants_two_only(self):
        self.assertEqual([x['issue'] for x in self.summaries if x['merchant']=='HOLD_MERCHANT'],[3,5])

    def test_mime_no_addressing_headers(self):
        for i in range(1,7):
            e=BytesParser(policy=policy.default).parsebytes((self.out/f'issue-{i:02d}.eml').read_bytes())
            for k in ('To','From','Cc','Bcc','Date','Reply-To'):
                self.assertNotIn(k,e)
            self.assertEqual(e['X-FV-Release-Gate'], 'HOLD_UNSENT')

    def test_mime_two_alternatives(self):
        for i in range(1,7):
            e=BytesParser(policy=policy.default).parsebytes((self.out/f'issue-{i:02d}.eml').read_bytes())
            self.assertEqual([p.get_content_type() for p in e.iter_parts()], ['text/plain','text/html'])

    def test_utf8_roundtrip(self):
        m=BytesParser(policy=policy.default).parsebytes((self.out/'issue-04.eml').read_bytes())
        self.assertIn('Apollo 1',m.get_body(preferencelist=('html',)).get_content())

    def test_original_body_preserved(self):
        for i,fn,kind in mod.EXPECTED:
            text=(MASTER/'issues'/fn).read_text(encoding='utf-8')
            b=mod.parse_source(text,i,kind)['body']
            self.assertIn(b,(self.out/f'issue-{i:02d}.txt').read_text())

    def test_blocking_tokens_all(self):
        for i in range(1,7):
            t=(self.out/f'issue-{i:02d}.txt').read_text()
            for marker in mod.LEGAL:self.assertIn(marker,t)

    def test_commercial_token_unmodified(self):
        for i,marker in mod.DISABLED.items():
            t=(self.out/f'issue-{i:02d}.txt').read_text()
            self.assertIn(marker,t)

    def test_no_affiliate_active(self):
        for i in mod.DISABLED:
            h=(self.out/f'issue-{i:02d}.html').read_text()
            self.assertNotIn('affiliates.inspire3.com/?',h)
            self.assertIn('APPROVED',h)

    def test_review_banner_visible(self):
        for i in range(1,7):self.assertIn(mod.REVIEW_BANNER,(self.out/f'issue-{i:02d}.html').read_text())

    def test_no_executable_markup(self):
        for i in range(1,7):
            h=(self.out/f'issue-{i:02d}.html').read_text().lower()
            for marker in ('<script','<iframe','<form','<img','onload=','onclick='):
                self.assertNotIn(marker,h)

    def test_mutation_no_disclosure(self):
        s=(MASTER/'issues'/mod.EXPECTED[2][1]).read_text().replace('**Commercial disclosure:**','**No disclosure:**')
        with self.assertRaises(AssertionError):mod.parse_source(s,3,mod.EXPECTED[2][2])

    def test_mutation_activated_offer(self):
        s=(MASTER/'issues'/mod.EXPECTED[4][1]).read_text().replace(mod.DISABLED[5],'https://hypnosislive.com/mental-skills/total-focus?affid=123')
        with self.assertRaises(AssertionError):mod.parse_source(s,5,mod.EXPECTED[4][2])

    def test_mutation_missing_legal(self):
        s=(MASTER/'issues'/mod.EXPECTED[0][1]).read_text().replace(mod.LEGAL[0],'123 Any Street')
        with self.assertRaises(AssertionError):mod.parse_source(s,1,mod.EXPECTED[0][2])

    def test_mutation_wrong_class(self):
        s=(MASTER/'issues'/mod.EXPECTED[2][1]).read_text().replace('commercial-review-pending','editorial')
        with self.assertRaises(AssertionError):mod.parse_source(s,3,mod.EXPECTED[2][2])

    def test_mime_records_no_spoofed_send(self):
        for i in range(1,7):
            m=BytesParser(policy=policy.default).parsebytes((self.out/f'issue-{i:02d}.eml').read_bytes())
            self.assertIn('REVIEW ONLY',str(m['Subject']))

    def test_no_remote_assets(self):
        for i in range(1,7):
            h=(self.out/f'issue-{i:02d}.html').read_text()
            self.assertNotIn('<link ',h)
            self.assertNotIn('<style',h)

    def test_generated_manifest(self):
        self.assertEqual(len(json.loads((self.out/'manifest-review.json').read_text())),6)


if __name__ == '__main__':unittest.main()

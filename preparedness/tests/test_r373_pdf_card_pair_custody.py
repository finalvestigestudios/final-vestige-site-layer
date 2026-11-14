"""R373 offline synthetic card pairing and PDF pagination regressions (not safety approval)."""
import importlib.util
from pathlib import Path
import unittest
import fitz

spec=importlib.util.spec_from_file_location('r373',Path(__file__).resolve().parents[1]/'tools'/'r373_pdf_card_pair_custody.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def make_pdf(copies=4, *, omit=None, duplicate=None, split=None, edge=None):
    d=fitz.open(); d.new_page(width=612,height=792);d.new_page(width=612,height=792)
    for i,token in enumerate(t for pair in m.markers(copies) for t in pair):
        if token==omit:continue
        page=d[1 if token==split else 0]
        pos=(1,90+22*i) if token==edge else (100,90+22*i)
        page.insert_text(pos,token,fontsize=12)
        if token==duplicate:page.insert_text((340,90+22*i),token,fontsize=12)
    return d.tobytes()

class PairChecks(unittest.TestCase):
    def test_one_pair(self):self.assertEqual(m.check_pdf_pairs(make_pdf(1),copies=1)['verified_pairs'],1)
    def test_four_pairs(self):self.assertEqual(m.check_pdf_pairs(make_pdf(4),copies=4)['verified_pairs'],4)
    def test_no_pdf(self):self.assertTrue(m.check_pdf_pairs(b'',copies=1)['errors'])
    def test_bad_pdf(self):self.assertTrue(m.check_pdf_pairs(b'not-pdf',copies=1)['errors'])
    def test_oversized_pdf(self):self.assertTrue(m.check_pdf_pairs(b'x'*8000001,copies=1)['errors'])
    def test_more_than_max(self):self.assertTrue(m.check_pdf_pairs(make_pdf(1),copies=5)['errors'])
    def test_zero_cards(self):self.assertTrue(m.check_pdf_pairs(make_pdf(1),copies=0)['errors'])
    def test_bool_count(self):self.assertTrue(m.check_pdf_pairs(make_pdf(1),copies=True)['errors'])
    def test_bad_margin(self):self.assertTrue(m.check_pdf_pairs(make_pdf(1),copies=1,margin_pt=-1)['errors'])
    def test_large_margin(self):self.assertTrue(m.check_pdf_pairs(make_pdf(1),copies=1,margin_pt=80)['errors'])
    def test_missing_checkout(self):self.assertTrue(m.review(Path('/nonexistent/r373/checkout'))['errors'])
    def test_no_publishing(self):self.assertTrue(all(not v for v in m.RELEASE.values()))
    def test_one_marker_deterministic(self):self.assertEqual(m.markers(1)[0][0],'FVTESTCARD01FRONT')
    def test_card_four_marker(self):self.assertEqual(m.markers(4)[3][1],'FVTESTCARD04BACK')
    def test_sha_git(self):self.assertEqual(m.git_blob(b'x'),'c1b0730e0133447badcfd47fd144e254807b06e1')
    def test_no_real_data_in_fixture(self):self.assertNotIn('123-45',m.synthetic_print_html(4))
    def test_missing_browser_fails(self):
        with self.assertRaises(ValueError):m.print_pdf_fixture('<p>test</p>',chromium='/unavailable/chromium')
    def test_status_still_hold_on_pass(self):self.assertFalse(m.check_pdf_pairs(make_pdf(1),copies=1)['may_publish'])

class BrowserChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proofs=[m.check_pdf_pairs(m.print_pdf_fixture(m.synthetic_print_html(n)),copies=n) for n in (1,2,3,4)]
    def test_browser_one(self):self.assertFalse(self.proofs[0]['errors'])
    def test_browser_two(self):self.assertFalse(self.proofs[1]['errors'])
    def test_browser_three(self):self.assertFalse(self.proofs[2]['errors'])
    def test_browser_four(self):self.assertFalse(self.proofs[3]['errors'])
    def test_browser_missing_back(self):
        b=m.print_pdf_fixture(m.synthetic_print_html(1,hide_back=True))
        self.assertTrue(m.check_pdf_pairs(b,copies=1)['errors'])
    def test_browser_still_hard_hold(self):self.assertFalse(self.proofs[3]['qd_pass'])

def add_mutation_tests():
    for n in range(1,5):
        for side in ('FRONT','BACK'):
            token=f'FVTESTCARD{n:02d}{side}'
            for variant,needle in [('omit','MISSING'),('duplicate','DUPLICATE'),
                                    ('split','PAGE_SPLIT'),('edge','OUTSIDE')]:
                def case(self, token=token, variant=variant, needle=needle):
                    result=m.check_pdf_pairs(make_pdf(4,**{variant:token}),copies=4)
                    self.assertTrue(any(needle in error for error in result['errors']),result)
                setattr(PairChecks,f'test_{variant}_{n}_{side.lower()}',case)
add_mutation_tests()

if __name__=='__main__':unittest.main()

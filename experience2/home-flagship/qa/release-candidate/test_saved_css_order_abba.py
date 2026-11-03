"""Adversarial checks for the CSS order A/B/B/A source-custody contract."""
import unittest
from pathlib import Path
from verify_saved_css_order_abba import make_css_late_variant, summarize_pairs, ORDER, STYLE

FIXTURE = Path(__file__).resolve().parent / 'fixtures' / 'proposed-production-block-pr604.html'


class CSSOrderABBATests(unittest.TestCase):
    def sample(self):
        return ('<!-- wp:html -->\n<style>p{color:red}</style>\n'
                '<div data-fv-home-flagship><p>Editorial source</p></div>\n'
                '<script>void 0</script>\n<!-- /wp:html -->')

    def test_only_stylesheet_moved_and_editorial_content_identical(self):
        early = self.sample()
        late = make_css_late_variant(early)
        style = STYLE.search(early).group(0)
        self.assertNotEqual(late, early)
        self.assertLess(late.index('data-fv-home-flagship'), late.index(style))
        self.assertLess(late.index(style), late.index('<script>'))
        self.assertEqual(late.replace(style, '', 1), early.replace(style, '', 1))
        self.assertEqual(late.count('Editorial source'), 1)

    def test_reject_wrong_initial_order_and_additional_styles(self):
        for value in ('X' + self.sample(),
                      self.sample().replace('<style>', '<style type="text/css">'),
                      self.sample().replace('</style>', '</style><style>x</style>'),
                      self.sample().replace('<script>void 0</script>', ''),
                      self.sample().replace('<!-- /wp:html -->', '')):
            with self.subTest(value=value[:70]):
                with self.assertRaises(ValueError):
                    make_css_late_variant(value)

    def test_real_candidate_single_style_and_rights_source_custody(self):
        candidate = FIXTURE.read_text(encoding='utf-8')
        late = make_css_late_variant(candidate)
        style = STYLE.search(candidate).group(0)
        self.assertEqual(late.replace(style, '', 1), candidate.replace(style, '', 1))
        self.assertEqual(candidate.count('data-fv-home-flagship'), late.count('data-fv-home-flagship'))
        self.assertEqual(candidate.count('s67-19766.webp'), late.count('s67-19766.webp'))
        self.assertEqual(candidate.count('Franklinexpeditionnote.jpg'), late.count('Franklinexpeditionnote.jpg'))
        self.assertEqual(candidate.count('<!-- wp:html -->'), late.count('<!-- wp:html -->'))
        self.assertLess(late.index('</style>'), late.index('<script'))

    def test_valid_abba_medians(self):
        data = [{'variant': v, 'samples': [{'viewport': 390, 'lcp_ms': n}
                                          for n in nums]}
                for v, nums in zip(ORDER, [(3100, 3200), (4100, 4200),
                                            (3900, 4000), (3000, 3300)])]
        result = summarize_pairs(data)
        self.assertEqual(result['early_median_mobile_lcp_ms'], 3150)
        self.assertEqual(result['late_median_mobile_lcp_ms'], 4050)
        self.assertEqual(result['late_minus_early_median_ms'], 900)

    def test_order_missing_and_invalid_measurements_fail_closed(self):
        for data in ([], [{'variant': 'early', 'samples': []}] * 4,
                     [dict(variant=v, samples=[{'viewport': 390, 'lcp_ms': 0}] * 2)
                      for v in ORDER]):
            with self.assertRaises(ValueError):
                summarize_pairs(data)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Read-only, offline WCAG contrast diagnostic for a WordPress editor-source snapshot.

No HTTP requests, tracking, WordPress writes or assertions about actual live rendering.
Pass an authorized, local plaintext HTML/editor-source file; never embed credentials.
"""
import argparse
import json
import re
import unittest
from pathlib import Path

SELECTOR = '.fv-affiliate-note'
DARK_REFERENCES = ('#090A0A', '#101111', '#161816')
NORMAL_TEXT_MIN = 4.5

def luminance(color):
    if not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
        raise ValueError('Requires a six-digit CSS hex color')
    channels = [int(color[n:n+2], 16) / 255 for n in (1, 3, 5)]
    linear = [v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4 for v in channels]
    return sum(a*b for a, b in zip((0.2126, 0.7152, 0.0722), linear))

def contrast(color_a, color_b):
    lighter, darker = sorted((luminance(color_a), luminance(color_b)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)

def source_properties(editor_source):
    match = re.search(r'\.fv-affiliate-note\s*\{([^}]+)\}', editor_source, re.I)
    if not match:
        raise ValueError('Source does not contain the expected affiliate disclosure CSS selector')
    rules = match.group(1)
    color = re.search(r'(?<![\w-])color\s*:\s*(#[0-9a-fA-F]{6})\b', rules, re.I)
    size = re.search(r'font-size\s*:\s*(\d+(?:\.\d+)?)px\b', rules, re.I)
    if not color or not size:
        raise ValueError('Expected literal color and font-size not found; require browser review')
    return color.group(1).upper(), float(size.group(1))

def audit(editor_source, backgrounds=DARK_REFERENCES):
    fg, size = source_properties(editor_source)
    return {'state': 'SOURCE_ONLY_CONDITIONAL_NOT_LIVE_BROWSER_VERIFIED',
            'foreground': fg, 'declared_font_px': size,
            'backgrounds_are_reference_values_not_verified_computed_colors': True,
            'reference_ratios': [{'background': bg, 'ratio': round(contrast(fg, bg), 4),
                                  'below_normal_text_4_5': contrast(fg, bg) < NORMAL_TEXT_MIN}
                                 for bg in backgrounds],
            'next_step': 'In a real signed-out browser inspect computed background, foreground, opacity, overrides, 360/390/768/1440 responsive layout, and keyboard order.'}

class OfflineTests(unittest.TestCase):
    def test_black_white(self):
        self.assertAlmostEqual(contrast('#000000', '#FFFFFF'), 21, places=5)
    def test_same_color(self):
        self.assertAlmostEqual(contrast('#101111', '#101111'), 1, places=5)
    def test_current_101111(self):
        self.assertAlmostEqual(contrast('#77736C', '#101111'), 4.0107, places=3)
    def test_current_090a0a(self):
        self.assertLess(contrast('#77736C', '#090A0A'), 4.5)
    def test_candidate_101111(self):
        self.assertGreater(contrast('#908A80', '#101111'), 4.5)
    def test_literal_rule_source(self):
        self.assertEqual(source_properties('.fv-affiliate-note{color:#77736C!important;font-size:12px!important}'), ('#77736C', 12))
    def test_reject_missing_selector(self):
        with self.assertRaises(ValueError): source_properties('body { color:#77736C; }')
    def test_reject_bad_color(self):
        with self.assertRaises(ValueError): contrast('red', '#000000')
    def test_audit_is_explicitly_conditional(self):
        output=audit('.fv-affiliate-note{color:#77736C!important;font-size:12px!important}')
        self.assertIn('NOT_LIVE_BROWSER_VERIFIED', output['state'])
        self.assertEqual(len(output['reference_ratios']), 3)
        self.assertTrue(all(x['below_normal_text_4_5'] for x in output['reference_ratios']))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', help='Authorized offline WordPress raw editor source')
    parser.add_argument('--test', action='store_true')
    args=parser.parse_args()
    if args.test:
        unittest.main(argv=['offline_probe'], exit=False, verbosity=2)
    elif args.source:
        print(json.dumps(audit(Path(args.source).read_text(encoding='utf-8')), indent=2))
    else:
        parser.print_help()

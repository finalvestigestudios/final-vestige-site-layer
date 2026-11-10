#!/usr/bin/env python3
"""Regression: never mistake data-href or data-class for native HTML attributes.

Only the actual browser href on the preserved external Focus Fieldbook CTA
may satisfy Page 6 admission. Offline synthetic fixtures; no WordPress writes.
Run: python -m unittest discover -s tests/experience-2 -p test_native_focus_attribute_custody.py
"""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPOSER = ROOT / 'tools/experience-2/compose_page6_flagship.py'
spec = importlib.util.spec_from_file_location('fv_ex2_focus_composer', COMPOSER)
c = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = c
spec.loader.exec_module(c)


def fixture(attrs, section_attrs='class="fv-focus-cta"', tag='a'):
    return (f'<section {section_attrs} aria-label="Free reader resource">'
            f'<div><{tag} class="fv-focus-cta__button" {attrs}>'
            f'Get the free Focus Fieldbook</{tag}></div>'
            '</section>')


class NativeFocusAttributeCustody(unittest.TestCase):
    def test_approved_root_relative(self):
        self.assertEqual(c.native_focus_action(fixture('href="/focus/"')), '/focus/')

    def test_approved_canonical_https(self):
        self.assertEqual(c.native_focus_action(
            fixture('href="https://finalvestige.com/focus/"')), 'https://finalvestige.com/focus/')

    def test_browser_destination_spoofed_by_data_href(self):
        # Old greedy regex accepted trailing data-href="/focus/" while actual
        # href was an external destination.
        with self.assertRaises(c.AdmissionError):
            c.native_focus_action(fixture('href="https://unapproved.invalid/path" data-href="/focus/"'))

    def test_javascript_href_spoofed_by_data_href(self):
        with self.assertRaises(c.AdmissionError):
            c.native_focus_action(fixture('href="javascript:alert(1)" data-href="/focus/"'))

    def test_data_class_cannot_masquerade_as_button(self):
        with self.assertRaises(c.AdmissionError):
            c.native_focus_action(
                '<section class="fv-focus-cta"><a data-class="fv-focus-cta__button" href="/focus/">Go</a></section>')

    def test_data_class_cannot_masquerade_as_section(self):
        with self.assertRaises(c.AdmissionError):
            c.native_focus_action(fixture('href="/focus/"', 'data-class="fv-focus-cta"'))

    def test_duplicate_href_rejected(self):
        with self.assertRaises(c.AdmissionError):
            c.native_focus_action(fixture('href="/focus/" href="https://unapproved.invalid/"'))

    def test_duplicate_class_rejected(self):
        with self.assertRaises(c.AdmissionError):
            c.native_focus_action(
                '<section class="fv-focus-cta"><a class="fv-focus-cta__button" class="other" href="/focus/">Go</a></section>')

    def test_duplicate_section_class_rejected(self):
        with self.assertRaises(c.AdmissionError):
            c.native_focus_action(fixture('href="/focus/"', 'class="fv-focus-cta" class="other"'))

    def test_click_handler_cannot_override_approved_href(self):
        with self.assertRaises(c.AdmissionError):
            c.native_focus_action(fixture('href="/focus/" onclick="location.href=&#39;https://unapproved.invalid/&#39;"'))

    def test_touch_handler_rejected(self):
        with self.assertRaises(c.AdmissionError):
            c.native_focus_action(fixture('href="/focus/" ontouchstart="location.href=&#39;https://unapproved.invalid/&#39;"'))

    def test_multiple_real_buttons_rejected(self):
        html = ('<section class="fv-focus-cta">'
                '<a class="fv-focus-cta__button" href="/focus/">One</a>'
                '<a class="fv-focus-cta__button" href="/focus/">Two</a></section>')
        with self.assertRaises(c.AdmissionError):
            c.native_focus_action(html)

    def test_duplicate_sections_rejected(self):
        with self.assertRaises(c.AdmissionError):
            c.native_focus_action(fixture('href="/focus/"') * 2)

    def test_nested_section_retains_real_button(self):
        html = ('<section class="fv-focus-cta"><section>'
                '<a class="fv-focus-cta__button" href="/focus/">Go</a>'
                '</section></section>')
        self.assertEqual(c.native_focus_action(html), '/focus/')

    def test_malformed_external_destination_rejected(self):
        for href in ('//unapproved.invalid/focus/',
                     'https://finalvestige.com/focus/?via=spam',
                     'http://finalvestige.com/focus/',
                     'https://unapproved.invalid/focus/'):
            with self.subTest(href=href), self.assertRaises(c.AdmissionError):
                c.native_focus_action(fixture(f'href="{href}"'))

    def test_non_anchor_class_rejected(self):
        with self.assertRaises(c.AdmissionError):
            c.native_focus_action(fixture('href="/focus/"', tag='div'))


if __name__ == '__main__':
    unittest.main()

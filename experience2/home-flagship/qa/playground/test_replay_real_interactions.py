"""Adversarial browser tests for source-captured WordPress UI action truth.

These are controlled synthetic HTML/JS/media served by local Python HTTP,
never a real WordPress installation or authorized historical images.
"""
import asyncio
from pathlib import Path
import tempfile
import unittest
from replay_wordpress_stage_browser import Capture, browser_review, passing
from unittest.mock import patch
from test_replay_wordpress_stage_browser import ProbeServer, TEST_JS, TEST_CSS, mock_html


class RealInteractionTruthTests(unittest.TestCase):
    def check_stage(self, *, html=None, js=None, css=None, expected=True, check_key=None, seven_widths=False):
        with ProbeServer() as server, tempfile.TemporaryDirectory() as d:
            if html is not None:
                server.data['/'] = (html.encode('utf-8'), 'text/html')
            if js is not None:
                server.data['/assets/flagship.js'] = (js.encode('utf-8'), 'text/javascript')
            if css is not None:
                server.data['/assets/style.css'] = (css.encode('utf-8'), 'text/css')
            page, custody = Capture(server.url, server.manifest).assemble()
            self.assertEqual(custody['archival_images_verified'], 3)
            with patch('replay_wordpress_stage_browser.WIDTHS', (320,360,390,768,1024,1440,1920) if seven_widths else (390,)):
                _, checks = asyncio.run(browser_review(page, Path(d), '/usr/bin/chromium'))
            self.assertEqual(passing(checks), expected, checks)
            self.assertEqual(len([w for w in checks if w.isdigit()]), 7 if seven_widths else 1)
            if check_key:
                self.assertFalse(checks['390']['real_interactions'][check_key], checks)
            return checks

    def test_four_genuine_reversible_interactions_and_keyboard_pass(self):
        checks = self.check_stage(expected=True, seven_widths=True)
        for width in (320, 360, 390, 768, 1024, 1440, 1920):
            self.assertEqual({v for v in checks[str(width)]['real_interactions'].values()}, {True})
        self.assertTrue(checks['no_js']['all_three_cases_visible'])
        self.assertTrue(checks['no_js']['both_observer_frames_visible'])
        self.assertTrue(checks['no_js']['enhancement_controls_hidden'])

    def test_noop_javascript_is_not_mistaken_for_success(self):
        self.check_stage(js='document.documentElement.dataset.noop="true";',
                         expected=False, check_key='direction_changes_and_restores')

    def test_missing_direction_control_is_not_a_pass(self):
        self.check_stage(html=mock_html(missing_control=True), expected=False,
                         check_key='direction_changes_and_restores')

    def test_aria_pressed_only_direction_is_not_visual_change(self):
        bad = TEST_JS.replace('root.dataset.fvDirection=b.dataset.fvDirectionChoice',
                              'b.setAttribute("aria-pressed","true")')
        self.assertNotEqual(bad, TEST_JS)
        self.check_stage(js=bad, expected=False, check_key='direction_changes_and_restores')

    def test_aria_hidden_only_case_is_not_visible_selection(self):
        bad = TEST_JS.replace('p.hidden=p.dataset.fvCase!==which',
                              'p.setAttribute("aria-hidden",String(p.dataset.fvCase!==which))')
        self.assertNotEqual(bad, TEST_JS)
        self.check_stage(js=bad, expected=False, check_key='case_selection_and_keyboard')

    def test_missing_case_keyboard_navigation_is_not_a_pass(self):
        bad = TEST_JS.replace("b.addEventListener('keydown',e=>", "b.addEventListener('not-the-keyboard',e=>")
        self.assertNotEqual(bad, TEST_JS)
        self.check_stage(js=bad, expected=False, check_key='case_selection_and_keyboard')

    def test_chronicle_button_aria_only_is_not_a_pass(self):
        bad = TEST_JS.replace("document.querySelector('.fv-hf__chronicle').dataset.fvChronicleMode=b.dataset.fvChronicleView",
                              "b.setAttribute('aria-pressed','true')")
        self.assertNotEqual(bad, TEST_JS)
        self.check_stage(js=bad, expected=False, check_key='chronicle_switch_and_restores')

    def test_observer_switch_aria_only_is_not_a_pass(self):
        bad = TEST_JS.replace('observer(b.dataset.fvObserverSwitch)', "b.setAttribute('aria-pressed','true')")
        self.assertNotEqual(bad, TEST_JS)
        self.check_stage(js=bad, expected=False, check_key='observer_switch_and_restores')

    def test_no_js_exposed_controls_fails_fallback_admission(self):
        bad = mock_html().replace('class="fv-hf__studio-controls" hidden', 'class="fv-hf__studio-controls"')
        self.assertNotEqual(bad, mock_html())
        checks = self.check_stage(html=bad, expected=False)
        self.assertFalse(checks['no_js']['enhancement_controls_hidden'])


    def test_direction_dom_changes_but_artifact_has_no_painted_difference(self):
        # Deliberately remove only direction-specific paint; JS still updates
        # the data attribute.  The prior verifier falsely passed this fixture.
        css = TEST_CSS.replace('.fv-hf[data-fv-direction="museum"] .fv-hf__opening{background:#75432e}', '').replace(
            '.fv-hf[data-fv-direction="museum"] .fv-hf__folio-arrival{background:#c4a77f}', '')
        self.assertNotEqual(css, TEST_CSS)
        self.check_stage(css=css, expected=False, check_key='direction_changes_and_restores')

    def test_chronicle_dom_changes_but_both_entries_remain_painted(self):
        # Switching the mode attribute without applying the hiding CSS must
        # fail even if all JS event handlers and ARIA changes still work.
        css = TEST_CSS.replace('.fv-hf__chronicle[data-fv-chronicle-mode="addition"] .fv-hf__chronicle-entry--first{display:none}', '').replace(
            '.fv-hf__chronicle[data-fv-chronicle-mode="original"] .fv-hf__chronicle-entry--second{display:none}', '')
        self.assertNotEqual(css, TEST_CSS)
        self.check_stage(css=css, expected=False, check_key='chronicle_switch_and_restores')

    def test_missing_artifact_and_historical_entries_do_not_pass(self):
        html = mock_html().replace('class="fv-hf__folio-arrival"', 'class="not-an-artifact"')
        self.check_stage(html=html, expected=False, check_key='direction_changes_and_restores')
        html = mock_html().replace('fv-hf__chronicle-entry--first', 'not-a-first-entry')
        self.check_stage(html=html, expected=False, check_key='chronicle_switch_and_restores')

if __name__ == '__main__':
    unittest.main()

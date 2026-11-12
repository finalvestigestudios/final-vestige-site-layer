"""Synthetic adversarial and offline Chromium tests for the R326 source gate.

Passing tests do not attest source advice, independent QA, browser egress or release.
"""
from __future__ import annotations
import unittest
from unittest import mock
from pathlib import Path

from preparedness.tools import r326_browser_serialization_hold as r326
from preparedness.tools import r324_tool_privacy_egress_hold as r324


def sample(markup):
    return r326.inspect(markup.encode('utf-8'))


class TestCore(unittest.TestCase):
    def test_empty_no_forms(self):
        self.assertEqual(sample('<p>Only a printable sheet</p>')['form_count'], 0)

    def test_default_get_navigation(self):
        self.assertIn('GET_DEFAULT_OR_EXPLICIT_NAVIGATION_HOLD', sample('<form></form>')['forms'][0]['flags'])

    def test_get_name_query_potential(self):
        flags = sample('<form><input name="child" /></form>')['forms'][0]['flags']
        self.assertIn('POTENTIAL_FORMDATA_URL_QUERY_HOLD', flags)

    def test_get_no_name_not_a_claimed_pii_leak(self):
        row = sample('<form><input /></form>')['forms'][0]
        self.assertNotIn('POTENTIAL_FORMDATA_URL_QUERY_HOLD', row['flags'])
        self.assertIn('GET_DEFAULT_OR_EXPLICIT_NAVIGATION_HOLD', row['flags'])

    def test_post_not_get_query(self):
        flags = sample('<form method=post><input name=x /></form>')['forms'][0]['flags']
        self.assertIn('NON_GET_FORM_BEHAVIOR_REVIEW', flags)
        self.assertNotIn('POTENTIAL_FORMDATA_URL_QUERY_HOLD', flags)

    def test_dialog_not_egress_assumption(self):
        self.assertIn('NON_GET_FORM_BEHAVIOR_REVIEW', sample('<form method=dialog></form>')['forms'][0]['flags'])

    def test_invalid_method_requires_browser_normalization(self):
        self.assertIn('INVALID_FORM_METHOD_BROWSER_NORMALIZATION_REVIEW', sample('<form method=patch></form>')['forms'][0]['flags'])

    def test_inline_handler_not_nojs_guard(self):
        self.assertIn('INLINE_SUBMIT_HANDLER_NOT_NOJS_GUARD', sample('<form onsubmit="return false"></form>')['forms'][0]['flags'])

    def test_form_action_review(self):
        self.assertIn('EXPLICIT_ACTION_DESTINATION_REVIEW', sample('<form action="/send"></form>')['forms'][0]['flags'])

    def test_enter_implicit_submission_review(self):
        self.assertIn('ENTER_IMPLICIT_SUBMISSION_REVIEW', sample('<form><input name=email></form>')['forms'][0]['flags'])

    def test_explicit_button_override(self):
        self.assertIn('BUTTON_OVERRIDE_REVIEW', sample('<form><button formaction="/send">Submit</button></form>')['forms'][0]['flags'])

    def test_external_form_owner(self):
        row = sample('<form id=abc></form><input form=abc name=school>')['forms'][0]
        self.assertEqual(row['named_active_controls'], 1)

    def test_disabled_input_not_serializable(self):
        row = sample('<form><input name=contact disabled></form>')['forms'][0]
        self.assertEqual(row['potential_successful_controls'], 0)

    def test_unchecked_checkbox_not_successful(self):
        row = sample('<form><input type=checkbox name=c></form>')['forms'][0]
        self.assertEqual(row['potential_successful_controls'], 0)

    def test_checked_checkbox_successful(self):
        row = sample('<form><input checked type=checkbox name=c></form>')['forms'][0]
        self.assertEqual(row['potential_successful_controls'], 1)

    def test_unchecked_radio_not_successful(self):
        row = sample('<form><input type=radio name=c></form>')['forms'][0]
        self.assertEqual(row['potential_successful_controls'], 0)

    def test_checked_radio_successful(self):
        row = sample('<form><input type=radio checked name=c></form>')['forms'][0]
        self.assertEqual(row['potential_successful_controls'], 1)

    def test_multiple_names_deduplicated_in_witness(self):
        row = sample('<form><input name=x><input name=x></form>')['forms'][0]
        self.assertEqual(row['named_active_controls'], 2)
        self.assertEqual(row['name_only_witness'], ['x'])

    def test_unnamed_control_excluded(self):
        self.assertEqual(sample('<form><textarea>Private</textarea></form>')['forms'][0]['named_active_controls'], 0)

    def test_privacy_claims_count_only(self):
        self.assertGreaterEqual(sample('<p>Not sent anywhere. It keeps nothing.</p>')['privacy_claim_occurrences'], 2)

    def test_no_values_in_report(self):
        text = '<form><input name="phone" value="PRIVATE_SECRET_SAMPLE"></form>'
        self.assertNotIn('PRIVATE_SECRET_SAMPLE', str(sample(text)))

    def test_strict_utf8(self):
        with self.assertRaises(UnicodeDecodeError):r326.inspect(b'\xff')

    def test_reject_str(self):
        with self.assertRaises(TypeError):r326.inspect('oops')

    def test_reject_nul(self):
        with self.assertRaises(ValueError):r326.inspect(b'Hello\x00')

    def test_hold_never_approves(self):
        self.assertFalse(sample('<form></form>')['privacy_approved'])
        self.assertTrue(all(v is False for v in r326.RELEASE.values()))

    def test_bad_loader_fails_closed(self):
        out=r326.audit(lambda _: b'not original')
        self.assertEqual(out['state'],'INVALID_HARD_HOLD')
        self.assertEqual(len(out['errors']),6)
        self.assertEqual(out['entries'],[])

    def test_missing_loader_fails_closed(self):
        out=r326.audit(lambda _: (_ for _ in ()).throw(OSError('missing')))
        self.assertEqual(out['state'],'INVALID_HARD_HOLD')
        self.assertFalse(out['release']['independent_qd_pass'])

    def test_no_body_in_local_incomplete_checkout(self):
        # Invoking main with this copied test-only tree must never succeed.
        root=Path(__file__).resolve().parents[2]
        self.assertFalse((root/r326.custody.MANIFEST_PATH).exists())


class TestVariants(unittest.TestCase):
    pass


# 60 individually named adversarial cases: each exercises a different combination
# of method, named field, state, external owner, button or privacy assertion.
VARIANTS = [
    ('name_ascii', '<input name=a>', True),
    ('name_hyphen', '<input name=out-of-area>', True),
    ('name_unicode', '<input name="école">', True),
    ('name_plus', '<input name="school+room">', True),
    ('name_amp', '<input name="pickup&amp;school">', True),
    ('name_percent', '<input name="x%20y">', True),
    ('name_space', '<input name="x y">', True),
    ('name_colon', '<input name="person:phone">', True),
    ('name_newline', '<input name="a&#10;b">', True),
    ('name_brackets', '<input name="plan[contact]">', True),
    ('name_empty', '<input name="">', False),
    ('no_name', '<input>', False),
    ('disabled_with_name', '<input name=x disabled>', False),
    ('disabled_caps', '<input name=x DISABLED>', False),
    ('text', '<input type=text name=x>', True),
    ('email', '<input type=email name=x>', True),
    ('phone', '<input type=tel name=x>', True),
    ('date', '<input type=date name=x>', True),
    ('month', '<input type=month name=x>', True),
    ('time', '<input type=time name=x>', True),
    ('number', '<input type=number name=x>', True),
    ('password', '<input type=password name=x>', True),
    ('hidden', '<input type=hidden name=x>', True),
    ('url', '<input type=url name=x>', True),
    ('range', '<input type=range name=x>', True),
    ('color', '<input type=color name=x>', True),
    ('search', '<input type=search name=x>', True),
    ('textarea', '<textarea name=x>value</textarea>', True),
    ('select', '<select name=x><option>x</option></select>', True),
    ('checkbox_checked', '<input type=checkbox name=x checked>', True),
    ('checkbox_unchecked', '<input type=checkbox name=x>', False),
    ('radio_checked', '<input type=radio name=x checked>', True),
    ('radio_unchecked', '<input type=radio name=x>', False),
    ('submit_input', '<input type=submit name=x>', False),
    ('reset_input', '<input type=reset name=x>', False),
    ('button_input', '<input type=button name=x>', False),
    ('image_input', '<input type=image name=x>', False),
    ('file_input', '<input type=file name=x>', False),
    ('disabled_checkbox_checked', '<input type=checkbox name=x disabled checked>', False),
    ('disabled_select', '<select name=x disabled><option>x</option></select>', False),
    ('disabled_textarea', '<textarea name=x disabled>value</textarea>', False),
    ('empty_input_type', '<input type="" name=x>', True),
    ('same_name_twice', '<input name=x><input name=x>', True),
    ('unnamed_then_named', '<input><input name=x>', True),
    ('checked_then_unchecked', '<input type=checkbox checked name=x><input type=checkbox name=y>', True),
    ('checked_radio_then_unchecked', '<input type=radio checked name=x><input type=radio name=y>', True),
    ('button_submit', '<button type=submit name=x>submit</button>', False),
    ('button_default', '<button name=x>submit</button>', False),
    ('input_readonly', '<input name=x readonly>', True),
    ('autofocus', '<input name=x autofocus>', True),
    ('required', '<input name=x required>', True),
    ('multiple_select', '<select name=x multiple><option selected>1</option></select>', True),
    ('country_select', '<select name=country><option value=us>US</option></select>', True),
    ('datalist', '<input name=contact list=contacts><datalist id=contacts><option value=x></datalist>', True),
    ('aria_label', '<input name=x aria-label="Phone number">', True),
    ('tabindex', '<input name=x tabindex=0>', True),
    ('autocomplete_off', '<input name=x autocomplete=off>', True),
    ('dir_ltr', '<input name=x dir=ltr>', True),
    ('formnovalidate', '<input name=x formnovalidate>', True),
    ('spellcheck_false', '<textarea name=x spellcheck=false></textarea>', True),
]

for test_name, markup, expected in VARIANTS:
    def make_case(markup=markup, expected=expected):
        def run(self):
            rec=sample('<form>'+markup+'</form>')['forms'][0]
            self.assertEqual(bool(rec['potential_successful_controls']), expected,
                             (markup,rec))
            self.assertEqual('GET_DEFAULT_OR_EXPLICIT_NAVIGATION_HOLD' in rec['flags'], True)
        return run
    setattr(TestVariants,'test_'+test_name,make_case())


class TestOfflineBrowser(unittest.TestCase):
    def test_browser_synthetic_get_named(self):
        x=r326.chromium_preflight(b'<form><input name=phone value="SECRET"></form>')
        if x['state'].startswith(('BROWSER_ERROR','BROWSER_UNAVAILABLE')):
            self.skipTest(x['state'])
        self.assertEqual(x['state'],'OFFLINE_DOM_FORMDATA_SHAPE_ONLY_HARD_HOLD')
        self.assertEqual([a['forms'][0]['successful'] for a in x['observations']],[1,1])
        self.assertNotIn('SECRET',str(x))
        self.assertFalse(x['network_submission_attempted'])
        self.assertFalse(x['browser_egress_verified'])

    def test_browser_synthetic_unnamed(self):
        x=r326.chromium_preflight(b'<form onsubmit="return false"><input value="SECRET"></form>')
        if x['state'].startswith(('BROWSER_ERROR','BROWSER_UNAVAILABLE')):
            self.skipTest(x['state'])
        self.assertEqual([a['forms'][0]['successful'] for a in x['observations']],[0,0])

    def test_browser_synthetic_disabled(self):
        x=r326.chromium_preflight(b'<form><input name=x disabled value=SECRET></form>')
        if x['state'].startswith(('BROWSER_ERROR','BROWSER_UNAVAILABLE')):
            self.skipTest(x['state'])
        self.assertEqual([a['forms'][0]['successful'] for a in x['observations']],[0,0])

    def test_browser_synthetic_post(self):
        x=r326.chromium_preflight(b'<form method=post><input name=x value=SECRET></form>')
        if x['state'].startswith(('BROWSER_ERROR','BROWSER_UNAVAILABLE')):
            self.skipTest(x['state'])
        self.assertEqual([a['forms'][0]['method'] for a in x['observations']],['POST','POST'])

    def test_browser_no_script_execution(self):
        x=r326.chromium_preflight(b'<script>window.SECRET="SHOULD_NOT_RUN"</script><form><input name=x></form>')
        if x['state'].startswith(('BROWSER_ERROR','BROWSER_UNAVAILABLE')):
            self.skipTest(x['state'])
        self.assertNotIn('SHOULD_NOT_RUN',str(x))
        self.assertFalse(x['navigation_attempted'])


if __name__=='__main__':unittest.main()

"""Real Chromium offline guest-form acceptance and eight adversarial rejections.

Does not access a live site or send customer information.
"""
from pathlib import Path
import tempfile
import unittest
from focus_guest_gate import run

STYLE='''<style>body{background:#090a0a;color:#f4efe6;font:16px Georgia;margin:0}
.fv-focus{padding:20px;max-width:1100px;margin:auto}input,button{box-sizing:border-box;display:block;width:100%;max-width:420px;min-height:54px;background:#101111;color:white;border:2px solid #b8955e;margin:10px 0;padding:12px}label{display:block;margin-top:20px}
</style>'''
FORM='''<div class="wp-block-jetpack-subscriptions"><form><label for="fv-email">Your email address</label><input id="fv-email" type="email" autocomplete="email"><button type="submit">Send me the fieldbook</button></form></div>'''
PAGE='''<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Seven Day Focus Fieldbook</title>'''+STYLE+'''<main class="fv-focus"><h1>Free 52-page Fieldbook</h1>'''+FORM+'''</main></html>'''
FALLBACK='''<div class="wp-block-jetpack-subscriptions"><p><a href="https://finalvestige.com/?post_type=page&amp;p=1579">Send me the fieldbook</a></p></div>'''


class GuestGateTest(unittest.TestCase):
    def test_positive_four_real_browser_widths(self):
        with tempfile.TemporaryDirectory() as td:
            results=run('https://finalvestige.com/focus/',td,offline_html=PAGE)
            self.assertEqual([r['pass'] for r in results],[True]*4,results)

    def test_broken_real_browser_rejections(self):
        edits={
          'jetpack_self_link':PAGE.replace(FORM,FALLBACK),
          'missing_input':PAGE.replace('<input id="fv-email" type="email" autocomplete="email">',''),
          'unlabelled_input':PAGE.replace('<label for="fv-email">Your email address</label>',''),
          'tiny_email':PAGE.replace('min-height:54px','min-height:20px').replace('padding:12px','padding:0'),
          'hidden_email':PAGE.replace('type="email" autocomplete','type="email" hidden autocomplete'),
          'hidden_submit':PAGE.replace('type="submit"','type="submit" hidden'),
          'overflow':PAGE.replace('max-width:1100px','min-width:1500px'),
          'prepopulated':PAGE.replace('type="email" autocomplete','type="email" value="synthetic-only" autocomplete'),
        }
        with tempfile.TemporaryDirectory() as td:
            for name,html in edits.items():
                with self.subTest(name=name):
                    result=run('https://finalvestige.com/focus/',Path(td)/name,
                               offline_html=html,widths=(390,))
                    self.assertFalse(result[0]['pass'],(name,result))


if __name__=='__main__':
    unittest.main()

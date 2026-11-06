#!/usr/bin/env python3
"""Fail-closed mutation tests for the local-only EXACT Blueprint visual probe."""
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from exact_blueprint_visual_probe import extract_blueprint, build_preview, CHAPTERS

def fixture():
    css = "body{color:#f6ebda;background:#12120f;min-height:100vh;font-family:Georgia,serif}" + "/* accessible archival shell */" * 3
    js = "(()=>{document.documentElement.dataset.js='enabled';})();" + "/* no tracking or remote calls */" * 4
    html = "<div>" + ''.join(f'<span class="fv-margin-strip__item">Historical fragment {i}</span>' for i in range(72))
    html += ''.join(f'<h2 id="{chapter}">Record</h2>' for chapter in CHAPTERS)
    html += '<img src="data:," alt="first"><img src="data:," alt="second">'
    html += '<a href="https://finalvestige.com/focus/">Free Focus Fieldbook</a></div>'
    plugin = "<?php\nif (get_option('fv_ex2_playground_review_only', '') !== 'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1') { return; }\n"
    for tag, value in (('FVPG_CSS_END',css),('FVPG_JS_END',js),('FVPG_HTML_END',html)):
        plugin += "<<<'" + tag + "'\n" + value + "\n" + tag + ";\n"
    return {'steps':[{'step':'installTheme','options':{'targetFolderName':'assembler'}},{'step':'mkdir'},
                      {'step':'writeFile','path':'/wordpress/wp-content/mu-plugins/fv-ex2-playground-review.php','data':plugin},
                      {'step':'runPHP'},{'step':'runPHP'}]}

def raw(bp):
    return json.dumps(bp).encode('utf8')

class AdversarialBlueprintTests(unittest.TestCase):
    def test_realistic_positive_synthetic_only(self):
        css, js, html = extract_blueprint(raw(fixture()))
        preview = build_preview(css, js, html)
        self.assertIn('noindex,nofollow,noarchive', preview)
        self.assertEqual(html.count('class="fv-margin-strip__item"'),72)
    def test_missing_margins(self):
        b=fixture();b['steps'][2]['data']=b['steps'][2]['data'].replace('class="fv-margin-strip__item"', 'class="broken"',1)
        with self.assertRaises(ValueError): extract_blueprint(raw(b))
    def test_missing_chapter(self):
        b=fixture();b['steps'][2]['data']=b['steps'][2]['data'].replace('id="fv-hf-observer"', 'id="gone"')
        with self.assertRaises(ValueError): extract_blueprint(raw(b))
    def test_duplicate_chapter(self):
        b=fixture();b['steps'][2]['data']=b['steps'][2]['data'].replace('id="fv-hf-evidence"','id="fv-hf-title"')
        with self.assertRaises(ValueError): extract_blueprint(raw(b))
    def test_wrong_theme_folder(self):
        b=fixture();b['steps'][0]['options']['targetFolderName']='wrong'
        with self.assertRaises(ValueError): extract_blueprint(raw(b))
    def test_guard_removed(self):
        b=fixture();b['steps'][2]['data']=b['steps'][2]['data'].replace('fv_ex2_playground_review_only','broken')
        with self.assertRaises(ValueError): extract_blueprint(raw(b))
    def test_no_focus(self):
        b=fixture();b['steps'][2]['data']=b['steps'][2]['data'].replace('https://finalvestige.com/focus/','https://invalid.test/')
        with self.assertRaises(ValueError): extract_blueprint(raw(b))
    def test_unexpected_subscription(self):
        b=fixture();b['steps'][2]['data']=b['steps'][2]['data'].replace('Free Focus Fieldbook','wp:jetpack/subscriptions')
        with self.assertRaises(ValueError): extract_blueprint(raw(b))
    def test_html_script_injection(self):
        b=fixture();b['steps'][2]['data']=b['steps'][2]['data'].replace('Free Focus Fieldbook','<script>alert(1)</script>')
        with self.assertRaises(ValueError): extract_blueprint(raw(b))
    def test_truncated_css(self):
        b=fixture();b['steps'][2]['data']=b['steps'][2]['data'].replace("<<<'FVPG_CSS_END'", "<<<'NO_CSS'")
        with self.assertRaises(ValueError): extract_blueprint(raw(b))
    def test_unsafe_js_tag_end(self):
        with self.assertRaises(ValueError): build_preview("body{display:block}", "x='</script>'", "<div>test</div>")

if __name__=="__main__":
    unittest.main()

"""Offline regression controls for the UNAPPROVED R249 reader-copy proposal."""
import importlib.util
import re
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('r249', BASE / 'tools/r249_reader_disclosure_preview_hold.py')
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
GOOD = (BASE / mod.PREVIEW).read_text(encoding='utf-8')


class ReaderSafety(unittest.TestCase):
    def test_canonical_draft_is_held(self):
        x = mod.inspect(GOOD)
        self.assertEqual(x['state'], mod.HOLD)
        self.assertEqual((x['printed_full_fields'],x['printed_shorter_fields'],x['excluded_shorter_fields']), (13,6,7))
        for key in ('source_and_medical_safety_approved','browser_print_verified','privacy_certified',
                    'independent_qd_pass','commerce_approved','release_authorized'):
            self.assertIs(x[key], False)
        self.assertEqual(x, mod.inspect(GOOD))

    def test_read_only_io(self):
        class Fake:
            def __init__(self):self.calls=[]
            def __call__(self,root,path):
                self.calls.append(path)
                return GOOD.encode()
        f=Fake();out=mod.audit(Path('/never-written'),f)
        self.assertEqual(f.calls,[mod.PREVIEW])
        self.assertEqual(out['state'], mod.HOLD)

    def test_invalid_sizes(self):
        for s in (None, '', '\x00' + GOOD, GOOD * 100):
            with self.subTest(s=repr(s)[:20]),self.assertRaises(ValueError):mod.inspect(s)


def negative(name,original,replacement):
    def run(self):
        match = re.search(re.escape(original), GOOD, re.I)
        if not match:
            raise AssertionError('fixture witness missing ' + original)
        bad=GOOD[:match.start()]+replacement+GOOD[match.end():]
        with self.assertRaisesRegex(ValueError,'R249|invalid'):mod.inspect(bad)
    setattr(ReaderSafety,'test_reject_'+name,run)


for ix,frag in enumerate(mod.REQUIRED):
    negative('omitted_claim_%02d'%ix,frag,('retracted_%02d'%ix))
for ix,frag in enumerate(mod.PROHIBITED_COPY):
    negative('unsafe_claim_%02d'%ix,'Review copy only.',frag+' Review copy only.')
for ix,frag in enumerate((
    '<script>alert(1)</script>', '<form action="/preparedness/"></form>', '<input value="x">',
    '<img src="https://tracker.example/test.png">', '<iframe src="/preparedness/"></iframe>',
    '<svg onload="alert(1)"></svg>', '<style>.x{display:none}</style>',
    '<button disabled>Buy</button>', '<picture></picture>', '<video></video>',
    '<meta http-equiv="refresh" content="0">', '<a href="https://seller.example/buy">buy</a>',
    '<a href="javascript:alert(1)">click</a>', '<a href="data:text/html,hello">click</a>',
    '<a href="/preparedness/?utm_source=fake">click</a>', '<textarea>Enter home address</textarea>',
    '<section id="copy"><p>hidden</p></section>', '<details><summary>Pay</summary></details>',
    '<div onclick="alert(1)">text</div>', '<div style="display:none">text</div>',
    '<div aria-hidden="true">hide</div>', '<div class="hidden">hide</div>',
    '<div id="r249-title">duplicate</div>', '<div class="x" class="y">duplicate</div>',
    '<div srcset="https://x/y">test</div>', '<div contenteditable="true">text</div>',
    '<a href="//seller.example/buy">buy</a>', '<a href="#r249-title">inside</a>',
    '<a href="/focus/">subscribe</a>', '<a target="_blank">new</a>',
    '<div onload="alert(1)">x</div>', '<!-- <script>alert(1)</script> -->',
    '<div hidden>Invisible</div>', '<select><option>Choice</option></select>',
    '<canvas></canvas>', '<object data="/x"></object>',
    '<div><p>broken</div>', '<a href="mailto:test@example.com">mail</a>',
    '<a href="https://finalvestige.com/preparedness/">link</a>',
    '<a href="/preparedness/">second free link</a>',
)):
    negative('injected_markup_%02d'%ix,'  <h3>Choose what to carry</h3>',
             '  <h3>Choose what to carry</h3>'+frag)

for ix,(old,new) in enumerate((
    ('href="/preparedness/"','href="/checkout/"'),
    ('aria-labelledby="r249-title"','aria-labelledby="nonexistent"'),
    ('<h2 id="r249-title">','<h2 id="unlabeled">'),
    ('<h3>Choose what to carry</h3>','<h4>Choose what to carry</h4>'),
    ('<section class=', '<article class='),
    ('</section>', '</article>'),
    ('<p>This is a proposed', '<p><span>This is a proposed'),
)):
    negative('structural_%02d'%ix, old,new)


if __name__ == '__main__':unittest.main()

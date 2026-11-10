"""R251: fail-closed reader-context mutants (isolated; not native build).

R249 upstream result is modeled, not a claim of a native execution here.
The preview fixture is the authentic R249 Git blob, read without mutation.
"""
import copy
import hashlib
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('r251', ROOT/'tools/r251_reader_visible_context_hold.py')
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
HTML = (ROOT/'audits/r249_family_card_reader_disclosure_draft.html').read_text()
assert hashlib.sha1((b'blob '+str(len(HTML.encode())).encode()+b'\0'+HTML.encode())).hexdigest() == 'ce5c363786deb0296f78598818af1fd7abefae65'


def receipt(markup=HTML):
    prior = {'state':mod.HOLD, 'issue':136, 'conversion_issue':820,
             'preview_sha256':hashlib.sha256(markup.encode()).hexdigest(),
             'visible_free_destinations':['/preparedness/'],
             'human_review_required':True}
    prior.update({k:False for k in mod.FALSE_FLAGS})
    return prior


class VisibilityTest(unittest.TestCase):
    def test_original_byte_identical_preview(self):
        r=mod.inspect(HTML,receipt())
        self.assertEqual(r['state'],mod.HOLD)
        self.assertEqual(r['visible_paragraph_count'],7)
        self.assertFalse(r['release_authorized'])
        self.assertEqual(r,mod.inspect(HTML,receipt()))

    def test_whitespace_around_markup_allowed(self):
        markup=HTML.replace('  <h3>', '\n  <h3>')
        self.assertEqual(mod.inspect(markup,receipt(markup))['visible_paragraph_count'],7)

    def test_false_gate_provenance(self):
        for k in mod.FALSE_FLAGS:
            for bad in (None, True, 0, 'false'):
                with self.subTest(k=k,bad=bad):
                    p=receipt();p[k]=bad
                    with self.assertRaisesRegex(ValueError,'HARD HOLD'):
                        mod.inspect(HTML,p)

    def test_malformed_upstream(self):
        for k,v in (('issue',999),('conversion_issue',819),('state','PASS'),
                    ('preview_sha256','0'*64),('visible_free_destinations',[]),
                    ('human_review_required',False)):
            with self.subTest(k=k):
                p=receipt();p[k]=v
                with self.assertRaisesRegex(ValueError,'HARD HOLD'):
                    mod.inspect(HTML,p)

    def test_type_guards(self):
        for bad in (None,123,{},b'html',[],False):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError,'HARD HOLD'):
                    mod.inspect(bad,receipt())
                with self.assertRaisesRegex(ValueError,'HARD HOLD'):
                    mod.inspect(HTML,bad)

    def test_comment_can_not_replace_visible_notice(self):
        phrase='The interactive form is hidden when JavaScript is off.'
        s=HTML.replace(phrase,'<!-- '+phrase+' -->')
        with self.assertRaisesRegex(ValueError,'HARD HOLD'):
            mod.inspect(s,receipt(s))

    def test_disclosures_can_not_migrate_to_heading(self):
        phrase='No paid kit and no paid checkout'
        s=HTML.replace(phrase,'No kit').replace('Choose what to carry','Choose what to carry '+phrase)
        with self.assertRaisesRegex(ValueError,'HARD HOLD'):
            mod.inspect(s,receipt(s))


def generate(case, name, mutate):
    def run(self):
        html=mutate(HTML)
        self.assertNotEqual(html,HTML)
        with self.assertRaisesRegex(ValueError, 'R251 HARD HOLD'):
            mod.inspect(html,receipt(html))
    setattr(VisibilityTest,'test_adversarial_%03d_%s'%(case,name),run)

idx=0
# R249 accepts popover attributes and counts their text; R251 must not.
for attribute in ('popover','popover="auto"','popover="manual"','inert',
                  'data-hidden="true"','data-visibility="collapsed"',
                  'aria-hidden="false"','hidden','style="display:block"',
                  'class="visible"','contenteditable="false"','tabindex="-1"',
                  'role="presentation"','translate="no"','onmouseenter="void 0"',
                  'onclick="void 0"', 'accesskey="p"', 'title="notice"',
                  'dir="rtl"', 'lang="en"', 'id="replacement"',
                  'name="x"', 'aria-expanded="false"','aria-controls="hidden"',
                  'itemprop="text"','itemscope','data-analytics="track"'):
    def mutate(s,attr=attribute):
        return s.replace('<p>The current shorter', '<p '+attr+'>The current shorter')
    generate(idx,'paragraph_attr',mutate);idx+=1
for attr in ('popover','popover="auto"','inert','hidden','aria-hidden="true"',
             'style="display:none"','data-hidden="yes"',
             'id="wrap"','contenteditable="true"'):
    def mutate(s,attr=attr):
        return s.replace('<section class=', '<section '+attr+' class=')
    generate(idx,'section_attr',mutate);idx+=1
for tag in ('div','span','template','dialog','details','summary','fieldset',
            'script','noscript','iframe','style','svg','math','form','button',
            'table','blockquote','audio','video','picture','h4'):
    def mutate(s,tag=tag):
        return s.replace('<p>The current shorter', '<'+tag+'><p>The current shorter').replace(
            'These details may be visible if a printed card is lost or shared.</p>',
            'These details may be visible if a printed card is lost or shared.</p></'+tag+'>')
    generate(idx,'foreign_wrapper',mutate);idx+=1
for label in ('six filled-in fields:', 'household name','household phone number',
              'out-of-area contact','out-of-area phone number','first meeting place',
              'review date','lost or shared','thirteen filled-in fields',
              'excludes seven fields', 'interactive form is hidden when JavaScript is off',
              'written plan at home','No paid kit','no paid checkout'):
    def mutate(s,label=label):return s.replace(label,'REDACTED',1)
    generate(idx,'disclosure_redacted',mutate);idx+=1
for old,new in (('<h2 id="r249-title">','<h2>'),
                ('<h3>Choose','<h4>Choose'),
                ('<a href="/preparedness/">','<a href="https://example.org/">'),
                ('<a href="/preparedness/">','<a href="javascript:void(0)">'),
                ('<a href="/preparedness/">','<a href="/preparedness/" target="_blank">'),
                ('<p class="pa-review-hold">','<p>'),
                ('<section class="pa-act pa-r249-review"','<section class="pa-r249-review pa-act"'),
                ('</section>','</section><p>Additional false clearance</p>'),
                ('<!-- UNPUBLISHED EDITORIAL OPTION B.','<!-- PUBLISHED OPTION B.'),
                ('<h3>Choose what to carry</h3>','<p>Choose what to carry</p>')):
    def mutate(s,old=old,new=new):return s.replace(old,new,1)
    generate(idx,'structural_drift',mutate);idx+=1

if __name__=='__main__':unittest.main()

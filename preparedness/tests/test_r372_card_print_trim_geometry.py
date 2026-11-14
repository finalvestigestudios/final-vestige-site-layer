"""R372 fail-closed synthetic CSS/PDF geometry tests; NOT authentic QD evidence."""
from __future__ import annotations
import contextlib
import copy
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load(folder,name):
    path=ROOT/folder/(name+'.py')
    spec=importlib.util.spec_from_file_location('r372_'+name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
m=load('tools','r372_card_print_trim_geometry')
prior=load('tests','test_r371_detached_card_print_custody')


def sample():
    original=prior.fixture()
    r371=prior.candidate()
    return original,r371,m.proposed_trim_fix(r371,original)


def row():
    face={'notice_count':1,'notice_text':m.NOTICE,'visible':True,'inside':True,
          'legible_size':True,'clipped':False,'overflow':False,'fold_fit':True}
    return {'width':m.EXPECTED_CARD_WIDTH_CSS_PX,
            'height':m.EXPECTED_CARD_HEIGHT_CSS_PX,
            'faces':[copy.deepcopy(face),copy.deepcopy(face)]}


class PureGeometry(unittest.TestCase):
    def test_good(self):self.assertEqual(m.classify_faces([row()],expected_cards=1),[])
    def test_four_cards(self):self.assertEqual(m.classify_faces([row() for _ in range(4)],expected_cards=4),[])
    def test_missing_card(self):self.assertIn('PRINT_CARD_COUNT_MISMATCH',m.classify_faces([],expected_cards=1))
    def test_extra_card(self):self.assertIn('PRINT_CARD_COUNT_MISMATCH',m.classify_faces([row(),row()],expected_cards=1))
    def test_invalid_rows(self):self.assertIn('PRINT_CARD_COUNT_MISMATCH',m.classify_faces(None,expected_cards=1))
    def test_missing_faces(self):self.assertIn('FACE_COUNT:0',m.classify_faces([{}],expected_cards=1))
    def test_one_face(self):self.assertIn('FACE_COUNT:0',m.classify_faces([{'faces':[{}]}],expected_cards=1))
    def test_bad_width(self):
        r=row();r['width']=333
        self.assertIn('CARD_WIDTH_DRIFT:0',m.classify_faces([r],expected_cards=1))
    def test_bad_height(self):
        r=row();r['height']=115
        self.assertIn('CARD_HEIGHT_DRIFT:0',m.classify_faces([r],expected_cards=1))
    def test_bad_width_type(self):
        r=row();r['width']='672'
        self.assertIn('CARD_WIDTH_DRIFT:0',m.classify_faces([r],expected_cards=1))
    def test_warning_not_found(self):
        r=row();r['faces'][0]['notice_count']=0
        self.assertIn('NOTICE_MISSING_OR_CHANGED:0:0',m.classify_faces([r],expected_cards=1))
    def test_warning_duplicated(self):
        r=row();r['faces'][0]['notice_count']=2
        self.assertIn('NOTICE_MISSING_OR_CHANGED:0:0',m.classify_faces([r],expected_cards=1))
    def test_warning_changed(self):
        r=row();r['faces'][0]['notice_text']='all safe'
        self.assertIn('NOTICE_MISSING_OR_CHANGED:0:0',m.classify_faces([r],expected_cards=1))
    def test_warning_hidden(self):
        r=row();r['faces'][1]['visible']=False
        self.assertIn('NOTICE_OUTSIDE_TRIM_OR_HIDDEN:0:1',m.classify_faces([r],expected_cards=1))
    def test_warning_outside_face(self):
        r=row();r['faces'][0]['inside']=False
        self.assertIn('NOTICE_OUTSIDE_TRIM_OR_HIDDEN:0:0',m.classify_faces([r],expected_cards=1))
    def test_font_too_small(self):
        r=row();r['faces'][1]['legible_size']=False
        self.assertIn('NOTICE_FONT_BELOW_FLOOR:0:1',m.classify_faces([r],expected_cards=1))
    def test_text_clipped(self):
        r=row();r['faces'][0]['clipped']=True
        self.assertIn('FACE_CONTENT_OVERFLOW:0:0',m.classify_faces([r],expected_cards=1))
    def test_scroll_overflow(self):
        r=row();r['faces'][1]['overflow']=True
        self.assertIn('FACE_CONTENT_OVERFLOW:0:1',m.classify_faces([r],expected_cards=1))
    def test_fold_overlap(self):
        r=row();r['faces'][1]['fold_fit']=False
        self.assertIn('FACE_FOLD_OVERLAP:0:1',m.classify_faces([r],expected_cards=1))
    def test_second_card(self):
        rows=[row(),row()];rows[1]['faces'][0]['fold_fit']=False
        self.assertIn('FACE_FOLD_OVERLAP:1:0',m.classify_faces(rows,expected_cards=2))
    def test_two_faults(self):
        r=row();r['faces'][0]['visible']=False;r['faces'][0]['clipped']=True
        self.assertEqual(len(m.classify_faces([r],expected_cards=1)),2)
    def test_card_dimension_epsilon_accepted(self):
        r=row();r['width']+=1.5;r['height']-=1.5
        self.assertEqual(m.classify_faces([r],expected_cards=1),[])
    def test_card_dimension_epsilon_rejected(self):
        r=row();r['width']+=2.1
        self.assertIn('CARD_WIDTH_DRIFT:0',m.classify_faces([r],expected_cards=1))


class CandidateCustody(unittest.TestCase):
    def test_original_is_untouched(self):
        a,b,c=sample();self.assertIn(m.FACE_CSS,a);self.assertIn(m.FACE_CSS,b)
    def test_new_candidate_has_box_sizing(self):
        a,b,c=sample();self.assertIn(m.FACE_CSS_FIXED,c)
    def test_new_candidate_reverts_to_original_proposal(self):
        a,b,c=sample();self.assertEqual(c.replace(m.FACE_CSS_FIXED,m.FACE_CSS,1),b)
    def test_deterministic(self):
        a,b,c=sample();self.assertEqual(c,m.proposed_trim_fix(b,a))
    def test_preserves_source_citation_sequence(self):
        a,b,c=sample();self.assertEqual(c.count('{{cite:'),a.count('{{cite:'))
    def test_preserves_sources_links_sequence(self):
        a,b,c=sample();self.assertEqual(c.count('{{link:'),a.count('{{link:'))
    def test_preserves_source_form_count(self):
        a,b,c=sample();self.assertEqual(c.count('<form'),a.count('<form'))
    def test_nojs_cautions_preserved(self):
        a,b,c=sample();self.assertEqual(c.count('<p class="pa-card-caution">'+m.NOTICE+'</p>'),2)
    def test_js_card_factory_preserved(self):
        a,b,c=sample();self.assertIn("d.appendChild(el('p', 'pa-card-caution'",c)
    def test_original_warning_not_removed(self):
        a,b,c=sample();self.assertIn('Anyone who finds it can read it.',c)
    def test_print_css_anchor_exactly_once(self):
        a,b,c=sample();self.assertEqual(c.count(m.FACE_CSS_FIXED),1)
    def test_refuse_double_anchor(self):
        a,b,c=sample()
        with self.assertRaises(ValueError):m.proposed_trim_fix(b.replace(m.FACE_CSS,m.FACE_CSS*2),a)
    def test_refuse_missing_anchor(self):
        a,b,c=sample()
        with self.assertRaises(ValueError):m.proposed_trim_fix(b.replace(m.FACE_CSS,''),a)
    def test_refuse_original_change(self):
        a,b,c=sample()
        with self.assertRaises(ValueError):m.proposed_trim_fix(b,a.replace(m.FACE_CSS,''))
    def test_refuse_already_patched(self):
        a,b,c=sample()
        with self.assertRaises(ValueError):m.proposed_trim_fix(c,a)
    def test_refuse_missing_card_notice(self):
        a,b,c=sample()
        with self.assertRaises(ValueError):m.proposed_trim_fix(b.replace('pa-card-caution','lost',1),a)
    def test_refuse_missing_citation(self):
        a,b,c=sample()
        with self.assertRaises(ValueError):m.proposed_trim_fix(b.replace('{{cite:shelter-cdc-reunification}}',''),a)
    def test_refuse_extra_citation(self):
        a,b,c=sample()
        with self.assertRaises(ValueError):m.proposed_trim_fix(b+'{{cite:invented}}',a)
    def test_refuse_form_loss(self):
        a,b,c=sample()
        with self.assertRaises(ValueError):m.proposed_trim_fix(b.replace('<form','<section',1),a)
    def test_refuse_type_none(self):
        a,b,c=sample()
        with self.assertRaises(ValueError):m.proposed_trim_fix(None,a)
    def test_refuse_type_dict(self):
        a,b,c=sample()
        with self.assertRaises(ValueError):m.proposed_trim_fix({},a)
    def test_source_git_blob_function(self):self.assertEqual(m.blob(b'x'),'c1b0730e0133447badcfd47fd144e254807b06e1')
    def test_original_source_sha_pinned(self):self.assertEqual(m.PIN_BODY,'be8698ac5d020476ff649d85813810e2000c6f98')
    def test_original_metadata_sha_pinned(self):self.assertEqual(m.PIN_META,'47da1e7e20e39f0ea85e26d54a8d58301f6e0a15')
    def test_all_release_flags_false(self):self.assertTrue(all(x is False for x in m.RELEASE.values()))


class BrowserProbes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.a,cls.unfixed,cls.fixed=sample()
    def test_unfixed_nojs_detects_actual_box_bleed(self):
        result=m.inspect(self.unfixed,js=False)
        self.assertIn('FACE_FOLD_OVERLAP:0:0',result['errors'],result)
    def test_fixed_nojs_pdf_preserves_two_face_warnings(self):
        result=m.inspect(self.fixed,js=False)
        self.assertEqual(result['errors'],[],result)
        self.assertGreaterEqual(result['pdf_notice_count'],2)
    def test_fixed_js_single(self):
        result=m.inspect(self.fixed,js=True,copies=1)
        self.assertEqual(result['errors'],[],result)
    def test_fixed_js_four_dense(self):
        result=m.inspect(self.fixed,js=True,copies=4,dense=True)
        self.assertEqual(result['errors'],[],result)
        self.assertEqual(result['faces'],8)
    def test_missing_browser_rejected(self):
        self.assertIn('CHROMIUM_MISSING',m.inspect(self.fixed,chromium='/unavailable')['errors'])
    def test_missing_warning_rejected(self):
        broken=self.fixed.replace('<p class="pa-card-caution">'+m.NOTICE+'</p>','',2)
        r=m.inspect(broken,js=False)
        self.assertTrue(any('NOTICE_MISSING' in x for x in r['errors']),r)
    def test_very_small_font_rejected(self):
        broken=self.fixed.replace('font-size: 6.5pt;','font-size: 3pt;',1)
        r=m.inspect(broken,js=False)
        self.assertTrue(any('NOTICE_FONT_BELOW_FLOOR' in x for x in r['errors']),r)
    def test_bad_input_rejected(self):self.assertEqual(m.inspect('')['errors'],['BAD_HTML_INPUT'])
    def test_oversized_html_rejected(self):self.assertEqual(m.inspect('x'*250001)['errors'],['BAD_HTML_INPUT'])
    def test_unsafe_card_count_rejected(self):self.assertEqual(m.inspect(self.fixed,copies=200)['errors'],['BAD_BOUNDED_BROWSER_INPUT'])
    def test_no_card_count_rejected(self):self.assertEqual(m.inspect(self.fixed,copies=0)['errors'],['BAD_BOUNDED_BROWSER_INPUT'])


class Entrypoint(unittest.TestCase):
    def test_no_checkout(self):self.assertEqual(m.review(Path('/_missing_root_'))['status'],'INVALID_HARD_HOLD')
    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn('SOURCE_OR_METADATA_MISSING',str(m.review(Path(d))['errors']))
    def test_exit_two(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.main(['--root',d]),2)
    def test_no_publication_grant(self):self.assertFalse(m.RELEASE['may_publish'])
    def test_no_merchant_claim(self):self.assertFalse(m.RELEASE['merchant_sale_verified'])
    def test_no_child_privacy_approval(self):self.assertFalse(m.RELEASE['child_privacy_approved'])
    def test_no_paper_approval(self):self.assertFalse(m.RELEASE['paper_trim_verified'])
    def test_true_scale_measurement_constants(self):
        self.assertEqual(m.EXPECTED_CARD_WIDTH_CSS_PX,672)
        self.assertEqual(m.EXPECTED_CARD_HEIGHT_CSS_PX,204)

if __name__=='__main__':unittest.main()

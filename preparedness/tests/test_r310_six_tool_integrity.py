"""Isolated synthetic R310 regressions; never write to source repository."""
from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('prep_r310',HERE/'tools'/'r310_six_tool_identity_citation_privacy_hold.py')
r310=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r310)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='prep-r310-isolated-')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/'preparedness/content/tools'
        self.source.mkdir(parents=True)
        self.pred=self.root/r310.PREDECESSOR
        self.pred.parent.mkdir(parents=True,exist_ok=True)
        self.pred.write_text('R309 committed predecessor test fixture\n',encoding='utf-8')
        self.taxonomy_path=self.root/r310.TAXONOMY
        self.taxonomy_path.parent.mkdir(parents=True,exist_ok=True)
        self.taxonomy={'tools':[{'slug':s,'gate':True,'status':'drafted-pending-safety-review'} for s in r310.SLUGS],
                       'slate':[{'slug':'household-emergency-plan'}]}
        self.save_taxonomy()
        self.paths={}
        for i,slug in enumerate(r310.SLUGS,101):
            b,m=self.paths[slug]=(self.source/(slug+'.body.html'),self.source/(slug+'.meta.json'))
            b.write_text('<div id="main"><p>{{cite:source-one}} {{link:household-emergency-plan|read guide}}</p><noscript>Printable blank worksheet</noscript><script>let a=1;</script></div>',encoding='utf-8')
            m.write_text(json.dumps({'kind':'tool','slug':slug,'n':i,'section':'field-tools','track':'modern',
                                     'status':{'editorial':'drafted','publish':'draft'},
                                     'safety_review':{'state':'pending','reviewer':None,'date':None},
                                     'source_use':{'source-one':'Source claim, synthetic fixture'}}),encoding='utf-8')

    def save_taxonomy(self):
        self.taxonomy_path.write_text(json.dumps(self.taxonomy),encoding='utf-8')

    def pins(self):
        return {s:tuple(r310.oid(p.read_bytes()) for p in self.paths[s]) for s in r310.SLUGS if all(p.is_file() for p in self.paths[s])}

    def run_audit(self,*,baseline=None,pins=None,taxo=None,pred=None):
        return r310.audit(self.root,pins=self.pins() if pins is None else pins,
                          predecessor_oid=r310.oid(self.pred.read_bytes()) if pred is None else pred,
                          taxonomy_oid=r310.oid(self.taxonomy_path.read_bytes()) if taxo is None else taxo)

    def edit_meta(self,slug,fn):
        p=self.paths[slug][1];m=json.loads(p.read_text());fn(m);p.write_text(json.dumps(m),encoding='utf-8')

    def edit_body(self,slug,fn):
        p=self.paths[slug][0];p.write_text(fn(p.read_text()),encoding='utf-8')

    def assert_error(self,code,r=None):
        r=r or self.run_audit()
        self.assertTrue(any(e.startswith(code) for e in r['errors']),r)


class Baseline(Fixture):
    def test_clean_fixture_holds_without_certification(self):
        out=self.run_audit()
        self.assertEqual(out['errors'],[])
        self.assertEqual(out['state'],'DRAFT_HARD_HOLD')
        self.assertEqual(out['source_blobs_verified'],12)
        self.assertEqual(out['tool_count'],6)
        self.assertIsNone(out['verified_paid_orders'])
        self.assertFalse(out['privacy_verified'])
        self.assertFalse(out['actual_41_wordpress_drafts_verified'])

    def test_original_pinned_six_tools_cover_12_sources(self):
        self.assertEqual(set(r310.BLOBS),set(r310.SLUGS))
        self.assertEqual(len({p for v in r310.BLOBS.values() for p in v}),12)

    def test_meta_review_changed(self):
        self.edit_meta(r310.SLUGS[0],lambda m: m['safety_review'].update(state='approved'))
        self.assert_error('TOOL_UNAPPROVED_SAFETY_CHANGE')

    def test_missing_predecessor(self):
        self.pred.unlink();self.assert_error('R309_PREDECESSOR_NOT_AUTHENTIC',self.run_audit(pred='0'*40))

    def test_modified_predecessor(self):
        old=r310.oid(self.pred.read_bytes());self.pred.write_text('not approved')
        self.assert_error('R309_PREDECESSOR_NOT_AUTHENTIC',self.run_audit(pred=old))

    def test_missing_taxonomy(self):
        self.taxonomy_path.unlink()
        self.assert_error('TAXONOMY_MISSING_OR_CHANGED',r310.audit(self.root,pins=self.pins()))

    def test_changed_taxonomy_bytes(self):
        old=r310.oid(self.taxonomy_path.read_bytes());self.taxonomy_path.write_text('{}')
        self.assert_error('TAXONOMY_MISSING_OR_CHANGED',self.run_audit(taxo=old))

    def test_duplicate_taxonomy_tool_slug(self):
        self.taxonomy['tools'].append(dict(self.taxonomy['tools'][0]));self.save_taxonomy()
        self.assert_error('DUPLICATE_TAXONOMY_TOOL_SLUG')

    def test_wrong_taxonomy_gate(self):
        self.taxonomy['tools'][0]['gate']=False;self.save_taxonomy()
        self.assert_error('TAXONOMY_SAFETY_GATE_OR_ROUTE_MISSING')

    def test_wrong_taxonomy_status(self):
        self.taxonomy['tools'][0]['status']='published';self.save_taxonomy()
        self.assert_error('TAXONOMY_SAFETY_GATE_OR_ROUTE_MISSING')

    def test_unexpected_tool_body_file(self):
        (self.source/'unexpected.body.html').write_text('<b>not reviewed</b>')
        self.assert_error('TOOL_SOURCE_SET_CHANGED')

    def test_unexpected_tool_metadata_file(self):
        (self.source/'unexpected.meta.json').write_text('{}')
        self.assert_error('TOOL_SOURCE_SET_CHANGED')

    def test_missing_manifest_member(self):
        p=self.pins();p.pop(r310.SLUGS[0]);self.assert_error('SIX_TOOL_MANIFEST_INCOMPLETE_OR_EXTRA',self.run_audit(pins=p))

    def test_symlink_rejected(self):
        b=self.paths[r310.SLUGS[0]][0];real=self.root/'readable.html';real.write_bytes(b.read_bytes());b.unlink()
        b.symlink_to(real);self.assert_error('SOURCE_MISSING_OR_SYMLINK',self.run_audit(pins=r310.BLOBS))

    def test_metadata_wrong_sha(self):
        p=self.pins();self.edit_meta(r310.SLUGS[0],lambda m:m.update(title='unreviewed'))
        self.assert_error('SOURCE_BLOB_CHANGED',self.run_audit(pins=p))

    def test_body_wrong_sha(self):
        p=self.pins();self.edit_body(r310.SLUGS[0],lambda s:s+'extra')
        self.assert_error('SOURCE_BLOB_CHANGED',self.run_audit(pins=p))

    def test_duplicate_tool_number(self):
        slug=r310.SLUGS[3]
        self.edit_meta(slug,lambda m:m.update(n=101))
        out=self.run_audit();self.assert_error('DUPLICATE_TOOL_NUMBER:101',out)
        self.assertEqual(out['number_collisions']['101'],sorted((r310.SLUGS[0],slug)))

    def test_authentic_snapshot_number_and_nojs_conflicts_fail_closed(self):
        # Reproduces only the independently observed source facts, not the
        # complete authentic 12-file checkout or a qualified QA decision.
        values={'family-reunification-card':104,'home-fire-escape-worksheet':102,
                'kit-builder':103,'power-outage-planner':103,
                'reunification-plan':102,'water-planner':101}
        for slug,number in values.items():
            self.edit_meta(slug,lambda m,n=number:m.update(n=n))
        for slug in ('kit-builder','water-planner'):
            self.edit_body(slug,lambda s:s.replace('<noscript>Printable blank worksheet</noscript>',''))
        out=self.run_audit()
        self.assertEqual(set(out['number_collisions']),{'102','103'})
        self.assert_error('NO_NOSCRIPT_FALLBACK_WITNESS:kit-builder',out)
        self.assert_error('NO_NOSCRIPT_FALLBACK_WITNESS:water-planner',out)
        self.assertEqual(out['state'],'INVALID_HARD_HOLD')
        self.assertIs(out['publication_authorized'],False)

    def test_duplicate_citations_do_not_require_duplicate_declarations(self):
        self.edit_body(r310.SLUGS[0],lambda s:s.replace('{{cite:source-one}}','{{cite:source-one}}{{cite:source-one}}'))
        self.assertEqual(self.run_audit()['errors'],[])

    def test_missing_declared_citation(self):
        self.edit_body(r310.SLUGS[0],lambda s:s.replace('{{cite:source-one}}','no cite'))
        self.assert_error('CITATION_SOURCE_USE_PARITY')

    def test_undeclared_citation(self):
        self.edit_body(r310.SLUGS[0],lambda s:s.replace('{{cite:source-one}}','{{cite:other}}'))
        self.assert_error('CITATION_SOURCE_USE_PARITY')

    def test_missing_source_use(self):
        self.edit_meta(r310.SLUGS[0],lambda m:m.pop('source_use'))
        self.assert_error('SOURCE_USE_MISSING_OR_INVALID')

    def test_wrong_source_use_value(self):
        self.edit_meta(r310.SLUGS[0],lambda m:m['source_use'].update({'source-one':''}))
        self.assert_error('SOURCE_USE_MISSING_OR_INVALID')

    def test_unknown_link(self):
        self.edit_body(r310.SLUGS[0],lambda s:s.replace('household-emergency-plan','nonexistent-target'))
        self.assert_error('UNKNOWN_ARTICLE_OR_TOOL_DESTINATION')

    def test_no_noscript_with_script(self):
        self.edit_body(r310.SLUGS[0],lambda s:s.replace('<noscript>Printable blank worksheet</noscript>',''))
        self.assert_error('NO_NOSCRIPT_FALLBACK_WITNESS')

    def test_external_script(self):
        self.edit_body(r310.SLUGS[0],lambda s:s.replace('<script>','<script src="https://cdn.example/test.js">'))
        self.assert_error('EXTERNAL_SCRIPT_IN_TOOL')

    def test_form_action(self):
        self.edit_body(r310.SLUGS[0],lambda s:s+'<form action="/send"></form>')
        self.assert_error('NETWORK_FORM_ACTION')

    def test_unreviewed_event_handler(self):
        self.edit_body(r310.SLUGS[0],lambda s:s+'<button onmouseover="evil()">x</button>')
        self.assert_error('UNREVIEWED_EVENT_HANDLER')

    def test_js_word_in_prose_does_not_trigger(self):
        self.edit_body(r310.SLUGS[0],lambda s:s.replace('<p>','<p>Do not fetch( data using this tool; '))
        self.assertEqual(self.run_audit()['errors'],[])

    def test_wrong_tool_section(self):
        self.edit_meta(r310.SLUGS[0],lambda m:m.update(section='start-here'))
        self.assert_error('TOOL_IDENTITY_DRIFT')

    def test_wrong_tool_track(self):
        self.edit_meta(r310.SLUGS[0],lambda m:m.update(track='lost-ways'))
        self.assert_error('TOOL_TRACK_CHANGED')

    def test_fabricated_safety_reviewer(self):
        self.edit_meta(r310.SLUGS[0],lambda m:m['safety_review'].update(reviewer='someone'))
        self.assert_error('TOOL_UNAPPROVED_SAFETY_CHANGE')

    def test_published_meta_refused(self):
        self.edit_meta(r310.SLUGS[0],lambda m:m['status'].update(publish='published'))
        self.assert_error('TOOL_PUBLICATION_OR_EDITORIAL_STATUS_CHANGED')

    def test_bad_json(self):
        self.paths[r310.SLUGS[0]][1].write_text('not-json')
        self.assert_error('SOURCE_PARSE_FAILURE')

    def test_malformed_number_string(self):
        self.edit_meta(r310.SLUGS[0],lambda m:m.update(n='102'))
        self.assert_error('TOOL_NUMBER_INVALID')

    def test_bool_number_refused(self):
        self.edit_meta(r310.SLUGS[0],lambda m:m.update(n=True))
        self.assert_error('TOOL_NUMBER_INVALID')

    def test_no_approval_even_success(self):
        out=self.run_audit()
        for f in ('publication_authorized','independent_qd_pass','medical_safety_verified','privacy_verified','actual_41_wordpress_drafts_verified','paid_offer_approved'):
            self.assertIs(out[f],False)
        self.assertIsNone(out['net_revenue_per_1000_qualified_sessions'])


class Mutations(Fixture):
    pass


def _make_mutation(slug,variant,expected):
    def case(self):
        if variant=='remove_cite': self.edit_body(slug,lambda s:s.replace('{{cite:source-one}}',''))
        elif variant=='add_unknown_cite': self.edit_body(slug,lambda s:s.replace('{{cite:source-one}}','{{cite:source-two}}'))
        elif variant=='remove_nojs': self.edit_body(slug,lambda s:s.replace('<noscript>Printable blank worksheet</noscript>',''))
        elif variant=='set_published': self.edit_meta(slug,lambda m:m['status'].update(publish='published'))
        elif variant=='approve_safety': self.edit_meta(slug,lambda m:m['safety_review'].update(state='approved'))
        elif variant=='tamper_slug': self.edit_meta(slug,lambda m:m.update(slug='renamed-tool'))
        elif variant=='tamper_number': self.edit_meta(slug,lambda m:m.update(n=101))
        elif variant=='network': self.edit_body(slug,lambda s:s.replace('let a=1;','fetch("/collect");'))
        elif variant=='storage': self.edit_body(slug,lambda s:s.replace('let a=1;','localStorage.setItem("x","y");'))
        elif variant=='external_script': self.edit_body(slug,lambda s:s.replace('<script>','<script src="https://assets.example/tool.js">'))
        elif variant=='unknown_link': self.edit_body(slug,lambda s:s.replace('household-emergency-plan','missing-page'))
        else: raise AssertionError(variant)
        self.assert_error(expected)
    return case

MUTANTS=[('remove_cite','CITATION_SOURCE_USE_PARITY'),('add_unknown_cite','CITATION_SOURCE_USE_PARITY'),
         ('remove_nojs','NO_NOSCRIPT_FALLBACK_WITNESS'),('set_published','TOOL_PUBLICATION_OR_EDITORIAL_STATUS_CHANGED'),
         ('approve_safety','TOOL_UNAPPROVED_SAFETY_CHANGE'),('tamper_slug','TOOL_IDENTITY_DRIFT'),
         ('network','NETWORK_FETCH'),('storage','LOCAL_STORAGE'),('external_script','EXTERNAL_SCRIPT_IN_TOOL'),
         ('unknown_link','UNKNOWN_ARTICLE_OR_TOOL_DESTINATION')]
for _slug in r310.SLUGS:
    for _variant,_expected in MUTANTS:
        setattr(Mutations,'test_'+_slug.replace('-','_')+'_'+_variant,_make_mutation(_slug,_variant,_expected))


if __name__=='__main__':unittest.main()

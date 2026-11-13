"""R330 synthetic full 41-pair export and adversarial evidence tests; no writes to source."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import tempfile
import unittest
from preparedness.tools import r330_native_export_parity_hold as gate


def fixtures():
    articles=[f"article-{i:02d}" for i in range(1,36)]
    tools=[f"tool-{i:02d}" for i in range(1,7)]
    all_slugs=articles+tools
    sections=["start-here","water","food","shelter-power","health-sanitation",
              "family-communication","lost-ways","field-tools"]
    taxonomy={"sections":[{"slug":s} for s in sections],
              "slate":[{"n":i,"slug":slug,"section":sections[(i-1)%7]}
                        for i,slug in enumerate(articles,1)]}
    manifest={"expected":{"article_bodies":35,"tool_bodies":6},"records":[]}
    for kind,slugs in (("articles",articles),("tools",tools)):
        for slug in slugs:
            for suff in ("body.html","meta.json"):
                manifest["records"].append({"path":f"preparedness/content/{kind}/{slug}.{suff}"})
    routes=gate.expected_from_source(manifest,taxonomy)
    report={"release_evidence":{"state":"HOLD","article_drafts":41,"article_published":0,
                                "independent_qa_verified":False,"wordpress_publication_performed":False,
                                "unresolved_collisions":3},
            "articles":[{"slug":slug,"canonical":routes[slug],"words":525,"minutes":3,
                         "sources":["agency-a","agency-b","agency-c"]} for slug in all_slugs],
            "hubs":[{"section":s,"guides":6} for s in sections],
            "landing":{"article_cards":41,"populated_sections":sections}}
    outputs={}
    for slug in all_slugs + ["hub-"+s for s in sections]+["landing"]:
        body=f'<div class="pa pa-article" data-slug="{slug}"><p>Research material</p></div>'
        outputs[f"wp/{slug}.html"]=("<!-- wp:html -->\n<style>.pa{padding:1px}</style>\n"+body+"\n<!-- /wp:html -->\n").encode()
        outputs[f"preview/{slug}.html"]=(
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="robots" content="noindex,nofollow"></head><body><main>'
            +body+'</main></body></html>').encode()
    return manifest,taxonomy,routes,report,outputs


class NativeExportParity(unittest.TestCase):
    def setUp(self):
        self.manifest,self.taxonomy,self.routes,self.report,self.outputs=fixtures()

    def result(self):
        return gate.scan(self.report,self.routes,self.outputs)

    def assertHeld(self, signal=None):
        response=self.result()
        self.assertEqual(response['state'],'INVALID_HARD_HOLD',response)
        self.assertIs(response['release']['independent_qd_pass'],False)
        self.assertIs(response['release']['public_release_authorized'],False)
        if signal: self.assertTrue(any(signal in x for x in response['errors']),response['errors'])

    def test_complete_synthetic_41_plus_hubs_landing_remains_draft(self):
        r=self.result()
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD',r['errors'])
        self.assertEqual(r['expected_article_tool_pairs'],41)
        self.assertEqual(r['tested_export_pairs'],50)
        self.assertEqual(len(r['witnesses']),50)
        self.assertFalse(r['release']['source_claim_support_verified'])

    def test_no_test_runtime_modifies_actual_repo(self):
        before=copy.deepcopy(self.outputs)
        gate.scan(self.report,self.routes,self.outputs)
        self.assertEqual(self.outputs,before)

    def test_expected_source_crosswalk_35_plus_6(self):
        self.assertEqual(len(self.routes),41)
        self.assertEqual(len(set(self.routes.values())),41)
        self.assertEqual(self.routes['tool-01'],gate.SITE+'/preparedness/field-tools/tool-01/')

    def test_manifest_missing_article_body(self):
        self.manifest['records'].pop(0)
        with self.assertRaises(ValueError): gate.expected_from_source(self.manifest,self.taxonomy)

    def test_manifest_duplicate_meta(self):
        self.manifest['records'].append(self.manifest['records'][1].copy())
        with self.assertRaises(ValueError): gate.expected_from_source(self.manifest,self.taxonomy)

    def test_manifest_tool_number_drift(self):
        self.manifest['expected']['tool_bodies']=7
        with self.assertRaises(ValueError): gate.expected_from_source(self.manifest,self.taxonomy)

    def test_manifest_tool_slug_collision(self):
        self.manifest['records'][-1]['path']='preparedness/content/tools/article-01.meta.json'
        with self.assertRaises(ValueError): gate.expected_from_source(self.manifest,self.taxonomy)

    def test_taxonomy_fake_section(self):
        self.taxonomy['slate'][0]['section']='fake-section'
        with self.assertRaises(ValueError): gate.expected_from_source(self.manifest,self.taxonomy)

    def test_taxonomy_missing_slate(self):
        self.taxonomy['slate'].pop()
        with self.assertRaises(ValueError): gate.expected_from_source(self.manifest,self.taxonomy)

    def test_taxonomy_duplicate_slug(self):
        self.taxonomy['slate'][1]['slug']='article-01'
        with self.assertRaises(ValueError): gate.expected_from_source(self.manifest,self.taxonomy)

    def test_duplicate_json_keys_not_accepted(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):
            gate.strict_json(b'{"a":1,"a":2}')

    def test_invalid_utf8_json_not_accepted(self):
        with self.assertRaises(UnicodeError): gate.strict_json(b'\xff')

    def test_top_level_json_list_not_accepted(self):
        with self.assertRaises(ValueError): gate.strict_json(b'[]')

    def test_missing_release_evidence(self):
        del self.report['release_evidence'];self.assertHeld('BUILD_REPORT_FALSE_RELEASE')

    def test_forged_independent_qd(self):
        self.report['release_evidence']['independent_qa_verified']=True;self.assertHeld('BUILD_REPORT_FALSE_RELEASE')

    def test_forged_wordpress_publish(self):
        self.report['release_evidence']['wordpress_publication_performed']=True;self.assertHeld('BUILD_REPORT_FALSE_RELEASE')

    def test_forged_source_collision_resolution(self):
        self.report['release_evidence']['unresolved_collisions']=0;self.assertHeld('BUILD_REPORT_FALSE_RELEASE')

    def test_forged_article_published(self):
        self.report['release_evidence']['article_published']=1;self.assertHeld('BUILD_REPORT_FALSE_RELEASE')

    def test_forged_source_ready_state(self):
        self.report['release_evidence']['state']='REQUIRES_INDEPENDENT_QA';self.assertHeld('BUILD_REPORT_FALSE_RELEASE')

    def test_forged_draft_zero(self):
        self.report['release_evidence']['article_drafts']=0;self.assertHeld('BUILD_REPORT_FALSE_RELEASE')

    def test_forged_bool_as_article_count(self):
        self.report['release_evidence']['article_drafts']=True;self.assertHeld('BUILD_REPORT_FALSE_RELEASE')

    def test_duplicate_canonical_in_build_report(self):
        self.report['articles'][0]['canonical']=self.report['articles'][1]['canonical'];self.assertHeld('DUPLICATE_REPORTED_CANONICAL')

    def test_duplicate_article_in_build_report(self):
        self.report['articles'][0]['slug']=self.report['articles'][1]['slug'];self.assertHeld('DUPLICATE_REPORTED_SLUG')

    def test_report_forged_canonical(self):
        self.report['articles'][0]['canonical']='https://wrong.example/';self.assertHeld('CANONICAL_ROUTE_DRIFT')

    def test_report_no_sources(self):
        self.report['articles'][0]['sources']=[];self.assertHeld('READING_DEPTH_OR_SOURCE_REPORT')

    def test_report_duplicate_sources(self):
        self.report['articles'][0]['sources']=['a','a'];self.assertHeld('READING_DEPTH_OR_SOURCE_REPORT')

    def test_report_no_reading_depth(self):
        self.report['articles'][0]['words']=0;self.assertHeld('READING_DEPTH_OR_SOURCE_REPORT')

    def test_report_duplicate_hub(self):
        self.report['hubs'].append(self.report['hubs'][0].copy());self.assertHeld('DUPLICATE_HUB')

    def test_report_empty_hub(self):
        self.report['hubs'][0]['guides']=0;self.assertHeld('EMPTY_OR_INVALID_HUB')

    def test_report_bad_landing_count(self):
        self.report['landing']['article_cards']=40;self.assertHeld('LANDING_CARD_COUNT_DRIFT')

    def test_report_missing_populated_section(self):
        self.report['landing']['populated_sections'].pop();self.assertHeld('LANDING_HUB_COVERAGE_DRIFT')

    def test_report_missing_article(self):
        self.report['articles'].pop();self.assertHeld('BUILD_REPORT_MISSING_41_ARTICLES')

    def test_export_extra_stale_html(self):
        self.outputs['wp/old-safety-article.html']=b'<p>stale</p>';self.assertHeld('MISSING_OR_EXTRA_WORDPRESS_PREVIEW_OUTPUTS')

    def test_wp_preview_unexpected_extra_asset(self):
        self.outputs['preview/random.html']=b'x';self.assertHeld('MISSING_OR_EXTRA_WORDPRESS_PREVIEW_OUTPUTS')

    def test_unresolved_citation_in_wp(self):
        k='wp/article-01.html';self.outputs[k]=self.outputs[k].replace(b'Research material',b'Research {{cite:unreviewed}} material');self.assertHeld('UNRESOLVED_TEMPLATE_TOKEN')

    def test_unresolved_link_in_preview(self):
        k='preview/article-01.html';self.outputs[k]=self.outputs[k].replace(b'Research material',b'Research {{link:bad}} material');self.assertHeld('UNRESOLVED_TEMPLATE_TOKEN')

    def test_corrupt_utf8_output(self):
        self.outputs['preview/article-01.html']=b'\xff';self.assertHeld('INVALID_UTF8_PAIR')

    def test_wrong_page_in_preview(self):
        k='preview/article-01.html';self.outputs[k]=self.outputs[k].replace(b'Research material',b'Wrong material');self.assertHeld('WORDPRESS_PREVIEW_BODY_MISMATCH')

    def test_wrong_article_identity(self):
        for typ in ('wp','preview'):
            k=f'{typ}/article-01.html';self.outputs[k]=self.outputs[k].replace(b'data-slug="article-01"',b'data-slug="article-02"')
        self.assertHeld('WRONG_ARTICLE_EXPORT_IDENTITY')

    def test_preview_indexable(self):
        k='preview/article-01.html';self.outputs[k]=self.outputs[k].replace(b'noindex,nofollow',b'index,follow');self.assertHeld('PREVIEW_NOT_PRIVATE_NOINDEX')

    def test_preview_no_language(self):
        k='preview/article-01.html';self.outputs[k]=self.outputs[k].replace(b'<html lang="en">',b'<html>');self.assertHeld('PREVIEW_NOT_PRIVATE_NOINDEX')

    def test_wordpress_block_missing_close(self):
        k='wp/article-01.html';self.outputs[k]=self.outputs[k].replace(b'<!-- /wp:html -->',b'');self.assertHeld('INVALID_OUTPUT_WRAPPER')

    def test_wordpress_html_wrapped_wrong(self):
        k='wp/article-01.html';self.outputs[k]=b'<!doctype html>'+self.outputs[k];self.assertHeld('INVALID_OUTPUT_WRAPPER')

    def test_no_real_native_checkout_is_held(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises((OSError,ValueError)):
                gate.read_native(Path(td))


# Each of the 41 source identities independently fails closed if its WP export
# disappears or its paired preview changes. These are 82 distinct cases/paths.
def _missing_wp(slug):
    def test(self):
        self.outputs.pop(f'wp/{slug}.html'); self.assertHeld('MISSING_OR_EXTRA_WORDPRESS_PREVIEW_OUTPUTS')
    return test

def _drifted_preview(slug):
    def test(self):
        p=f'preview/{slug}.html'
        self.outputs[p]=self.outputs[p].replace(b'Research material',b'UNREVIEWED_CHANGED_SOURCE')
        self.assertHeld('WORDPRESS_PREVIEW_BODY_MISMATCH')
    return test

for _slug in [f'article-{i:02d}' for i in range(1,36)]+[f'tool-{i:02d}' for i in range(1,7)]:
    setattr(NativeExportParity,'test_missing_wp_'+_slug.replace('-','_'),_missing_wp(_slug))
    setattr(NativeExportParity,'test_preview_mismatch_'+_slug.replace('-','_'),_drifted_preview(_slug))

if __name__=='__main__':unittest.main()

"""R10 deterministic adversarial tests with *synthetic* Preparedness corpora.

These are NOT the real 35 articles or source-link verification. The local fixture
simulates the real 35+1 count and preserves seven-contributor collision semantics.
"""
import copy
from datetime import date
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import claim_corpus_release_gate as gate


class FakeLib:
    def __init__(self):
        self.taxonomy = {'base_path': '/preparedness/', 'sections':
                         [{'slug': 'start-here'}, {'slug': 'lost-ways'}, {'slug': 'field-tools'}],
                         'slate': [], 'tools': [{'slug': 'water-planner'}]}
        self.articles = {}
        for n in range(1, 36):
            historical = n > 20
            slug = f'article-{n:02d}'
            section = 'lost-ways' if historical else 'start-here'
            track = 'lost-ways' if historical else 'modern'
            self.taxonomy['slate'].append({'n': n, 'slug': slug, 'section': section, 'track': track})
            self.articles[slug] = {'n': n, 'slug': slug, 'section': section,
                                   'track': track, 'status': {'publish': 'draft'},
                                   'safety_review': {'state': 'not-required' if historical and n % 4 == 0 else 'pending'},
                                   '_body': '<p>' + ('carefully sourced explanatory passage ' * 550) + '</p>'}
        self.articles['water-planner'] = {'n': 101, 'slug': 'water-planner', 'section': 'field-tools',
                                         'track': 'modern', 'kind': 'tool', 'status': {'publish': 'draft'},
                                         'safety_review': {'state': 'pending'},
                                         '_body': '<div>' + ('planning inputs and cautions ' * 165) + '</div>'}

    def url_path(self, slug):
        meta = self.articles[slug]
        return f"/preparedness/{meta['section']}/{slug}/"


def rows():
    return [{'row_key':'start:0:alpha','origin':'start','source_id':'alpha',
             'url':'https://example.org/evidence','supports':'Original passage alpha', 'reading_limits':'pp. 1-2'},
            {'row_key':'food:0:beta','origin':'food','source_id':'beta',
             'url':'https://example.org/evidence','supports':'Distinct passage beta', 'reading_limits':'pp. 3-4'},
            {'row_key':'hist:0:gamma','origin':'hist','source_id':'gamma',
             'url':'https://example.org/different','supports':'Third source passage', 'reading_limits':'section 2'}]


def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,default=str).encode()).hexdigest()


def canonicalize(lib, *, rows, fingerprint, expect):
    states = {}
    claims = []
    for slug, meta in sorted(lib.articles.items()):
        state = meta['safety_review']['state']
        states[state] = states.get(state, 0)+1
        claims.append({'article':slug,'inherited_safety_state':state,
                       'body_sha256':digest(meta['_body']), 'source_id':'alpha',
                       'source_row_key':'start:0:alpha',
                       'context_excerpt':'Original claim was not medically assessed',
                       'heading':'Source section', 'ordinal':1, 'source_url':rows[0]['url']})
    counts = {'draft_items':len(lib.articles),'physical_source_rows':len(rows),
              'shared_url_groups':sum(n>1 for n in __import__('collections').Counter(x['url'] for x in rows).values()),
              'citation_occurrences':len(claims),'article_source_pairs':len(claims)}
    return {'release_state':'HOLD','may_publish':False,'counts':counts,
            'inherited_safety_states':dict(sorted(states.items())),
            'evidence_digest_sha256':digest(claims), 'claims':claims,
            'source_row_digest':digest(rows), 'authority':'MACHINE_ONLY'}


def review_audit(report, bundle, *, today, expected_counts, source_rows):
    if bundle.get('schema_version') != 1 or bundle.get('parent_evidence_digest_sha256') != report['evidence_digest_sha256']:
        raise ValueError('stale, malformed reviewer packet')
    reports = bundle.get('claim_responses')
    if not isinstance(reports,list) or reports:
        raise ValueError('fixture: cannot invent a human review')
    return {'release_state':'HOLD','may_publish':False, 'independent_human_source_checks_verified':0,
            'qualified_safety_approvals':0, 'response_digest_sha256':digest(bundle),
            'counts':{'claim_occurrences':len(report['claims']),'unreported_occurrences':len(report['claims']),
                      'shared_url_groups_unresolved_from_parent':report['counts']['shared_url_groups']},
            'articles':{k:{'pending':1} for k in sorted({x['article'] for x in report['claims']})}}


def subject():
    return FakeLib(),rows()


def run(lib=None, source=None, **kw):
    if lib is None:lib = FakeLib()
    if source is None:source = rows()
    return gate.audit_corpus(lib, source, lambda l,m:'a'*64,
                             make_report=kw.pop('make_report',canonicalize),
                             review_audit=kw.pop('review_audit',review_audit),
                             baseline=kw.pop('baseline',{}),
                             expected_rows=3, expected_url_groups=1, expected_urls=2, **kw)


class R10PositiveTests(unittest.TestCase):
    def test_synthetic_35_article_one_tool_corpus(self):
        result=run();self.assertEqual(result['editorial']['draft_items'],36)
    def test_genuine_drafts_only(self):
        self.assertEqual(run()['editorial']['article_drafts'],35)
    def test_planner_remains_separate(self):
        self.assertEqual(run()['editorial']['tool_drafts'],1)
    def test_unique_routes(self):
        self.assertEqual(run()['editorial']['unique_routes'],36)
    def test_modern_track_retained(self):
        self.assertEqual(run()['editorial']['track_counts']['modern'],21)
    def test_historical_track_retained(self):
        self.assertEqual(run()['editorial']['track_counts']['lost-ways'],15)
    def test_article_depth_retained(self):
        self.assertGreater(run()['editorial']['shortest_article_words'],1800)
    def test_planner_depth_retained(self):
        self.assertGreater(run()['editorial']['planner_words'],450)
    def test_two_contributors_one_url_preserved(self):
        z=run();self.assertEqual(z['sources']['physical_source_records'],3)
        self.assertEqual(z['sources']['literal_urls'],2)
    def test_repeated_url_unresolved(self):
        self.assertEqual(run()['sources']['repeated_url_groups_UNRESOLVED'],1)
    def test_auto_empty_report_is_hold(self):
        self.assertEqual(run()['release_state'],'HOLD')
    def test_auto_empty_report_no_publish(self):
        self.assertIs(run()['may_publish'],False)
    def test_no_claim_safety_approval(self):
        self.assertEqual(run()['qualified_safety_approvals'],0)
    def test_no_independent_link_check(self):
        self.assertEqual(run()['independent_human_source_checks_verified'],0)
    def test_separate_digest_for_entire_corpus(self):
        self.assertEqual(len(run()['source_content_digest_sha256']),64)
    def test_successful_identical_supplied_report(self):
        lib,source=subject();report=canonicalize(lib,rows=source,fingerprint=None,expect={})
        self.assertEqual(run(lib,source,supplied_report=report)['release_state'],'HOLD')
    def test_modern_approved_label_is_not_authority(self):
        lib,source=subject();lib.articles['article-01']['safety_review']['state']='approved'
        z=run(lib,source);self.assertFalse(z['may_publish'])
    def test_historical_not_required_is_not_authority(self):
        self.assertGreater(run()['editorial']['safety_state_labels_not_independent_approval']['not-required'],0)
    def test_word_count_ignores_html_tag_names(self):
        self.assertEqual(gate.word_count('<p>three tokens here</p>'),3)
    def test_word_count_strips_script_and_style(self):
        self.assertEqual(gate.word_count('<p>one two</p><style>not counted</style><script>nor counted</script>'),2)
    def test_word_count_decodes_entities(self):
        self.assertEqual(gate.word_count('water &amp; food'),2)
    def test_deterministic_repeat(self):
        self.assertEqual(run(),run())


class R10EditorialFailures(unittest.TestCase):
    def reject(self,fn,why=None):
        lib,source=subject();fn(lib)
        with self.assertRaisesRegex(ValueError,why or 'corpus|taxonomy|draft|slug|section|route|depth|safety|track|tool|body'):
            run(lib,source)
    def test_missing_article(self):self.reject(lambda l:l.articles.pop('article-01'),'corpus')
    def test_added_article(self):self.reject(lambda l:l.articles.__setitem__('rogue',copy.deepcopy(l.articles['article-01'])),'corpus')
    def test_duplicate_slate_slug(self):self.reject(lambda l:l.taxonomy['slate'][1].__setitem__('slug','article-01'),'duplicate')
    def test_slate_missing_item(self):self.reject(lambda l:l.taxonomy['slate'].pop(),'slate drift')
    def test_missing_slate_structure(self):self.reject(lambda l:l.taxonomy.pop('slate'),'slate drift')
    def test_wrong_taxonomy_base(self):self.reject(lambda l:l.taxonomy.__setitem__('base_path','/'), 'base path')
    def test_taxonomy_article_collision(self):self.reject(lambda l:l.taxonomy['tools'][0].__setitem__('slug','article-01'),'planner')
    def test_taxonomy_tool_missing(self):self.reject(lambda l:l.taxonomy.__setitem__('tools',[]),'planner')
    def test_duplicate_tools(self):self.reject(lambda l:l.taxonomy['tools'].append({'slug':'water-planner'}),'duplicate tool')
    def test_duplicate_sections(self):self.reject(lambda l:l.taxonomy['sections'].append({'slug':'start-here'}),'duplicate')
    def test_removed_section(self):self.reject(lambda l:l.taxonomy['sections'].pop(0),'section')
    def test_metadata_slug_changed(self):self.reject(lambda l:l.articles['article-01'].__setitem__('slug','other'),'slug')
    def test_metadata_section_changed(self):self.reject(lambda l:l.articles['article-01'].__setitem__('section','field-tools'),'section')
    def test_metadata_section_unknown(self):self.reject(lambda l:l.articles['article-01'].__setitem__('section','unsafe'),'section')
    def test_metadata_track_changed(self):self.reject(lambda l:l.articles['article-01'].__setitem__('track','lost-ways'),'track')
    def test_metadata_ordinal_changed(self):self.reject(lambda l:l.articles['article-01'].__setitem__('n',99),'track')
    def test_one_published(self):self.reject(lambda l:l.articles['article-01']['status'].__setitem__('publish','published'),'draft')
    def test_publish_unknown(self):self.reject(lambda l:l.articles['article-01']['status'].__setitem__('publish','approved'),'draft')
    def test_modern_review_bypassed(self):self.reject(lambda l:l.articles['article-01']['safety_review'].__setitem__('state','not-required'),'cannot bypass')
    def test_unknown_review_state(self):self.reject(lambda l:l.articles['article-01']['safety_review'].__setitem__('state','medically-safe'),'unknown safety')
    def test_tool_kind_removed(self):self.reject(lambda l:l.articles['water-planner'].pop('kind'),'tool identity')
    def test_tool_published(self):self.reject(lambda l:l.articles['water-planner']['status'].__setitem__('publish','published'),'draft')
    def test_missing_body(self):self.reject(lambda l:l.articles['article-01'].pop('_body'),'body')
    def test_null_body(self):self.reject(lambda l:l.articles['article-01'].__setitem__('_body',None),'body')
    def test_short_article(self):self.reject(lambda l:l.articles['article-01'].__setitem__('_body','<p>Brief</p>'),'reading-depth')
    def test_short_tool(self):self.reject(lambda l:l.articles['water-planner'].__setitem__('_body','No longer useful'),'reading-depth')
    def test_disallowed_nul_body(self):self.reject(lambda l:l.articles['article-01'].__setitem__('_body','a\x00b'),'NUL')
    def test_duplicate_routes(self):
        lib,source=subject();lib.url_path=lambda slug:'/preparedness/start-here/same/'
        with self.assertRaisesRegex(ValueError,'route'):run(lib,source)
    def test_route_changed(self):
        lib,source=subject();lib.url_path=lambda slug:f'/preparedness/{slug}/'
        with self.assertRaisesRegex(ValueError,'route'):run(lib,source)
    def test_malformed_slate_entry(self):self.reject(lambda l:l.taxonomy['slate'].__setitem__(2,[]),'malformed')
    def test_slate_track_collapse(self):
        lib,source=subject()
        for item in lib.taxonomy['slate'][20:]:
            item['track']='modern';lib.articles[item['slug']]['track']='modern';lib.articles[item['slug']]['safety_review']['state']='pending'
        with self.assertRaisesRegex(ValueError,'tracks'):run(lib,source)


class R10PhysicalSourceFailures(unittest.TestCase):
    def bad(self,mutation,regex='source'):
        lib,source=subject();mutation(source)
        with self.assertRaisesRegex(ValueError,regex):run(lib,source)
    def test_row_removed(self):self.bad(lambda r:r.pop())
    def test_row_added(self):self.bad(lambda r:r.append(copy.deepcopy(r[0])))
    def test_row_duplicate_key(self):self.bad(lambda r:r[1].__setitem__('row_key',r[0]['row_key']))
    def test_row_unknown_origin(self):self.bad(lambda r:r[0].__setitem__('origin','bogus'))
    def test_row_http_scheme(self):self.bad(lambda r:r[0].__setitem__('url','http://example.org/evidence'))
    def test_row_space_url(self):self.bad(lambda r:r[0].__setitem__('url','https://example.org/evidence x'))
    def test_row_backslash_url(self):self.bad(lambda r:r[0].__setitem__('url','https://example.org\\evidence'))
    def test_row_no_support(self):self.bad(lambda r:r[0].__setitem__('supports',''))
    def test_row_no_source_id(self):self.bad(lambda r:r[0].__setitem__('source_id',''))
    def test_row_no_origin(self):self.bad(lambda r:r[0].__setitem__('origin',''))
    def test_row_not_dictionary(self):self.bad(lambda r:r.__setitem__(0,[]))
    def test_row_missing_url(self):self.bad(lambda r:r[0].pop('url'))
    def test_row_missing_key(self):self.bad(lambda r:r[0].pop('row_key'))
    def test_row_missing_host(self):self.bad(lambda r:r[0].__setitem__('url','https://'))
    def test_row_url_credentials(self):self.bad(lambda r:r[0].__setitem__('url','https://user:pw@example.org/a'))
    def test_row_url_wrong_port(self):self.bad(lambda r:r[0].__setitem__('url','https://example.org:8080/a'))
    def test_row_url_embedded_newline(self):self.bad(lambda r:r[0].__setitem__('url','https://example.org/a\n'))
    def test_row_url_bogus_port(self):self.bad(lambda r:r[0].__setitem__('url','https://example.org:notaport/a'))
    def test_repeated_urls_merged(self):self.bad(lambda r:r[1].__setitem__('url','https://example.org/something-new'))
    def test_collision_introduced(self):self.bad(lambda r:r[2].__setitem__('url',r[0]['url']))


class R10TamperFailures(unittest.TestCase):
    def tamper(self,fn,needle='canonical corpus/report divergence'):
        lib,source=subject();candidate=canonicalize(lib,rows=source,fingerprint=None,expect={})
        fn(candidate)
        with self.assertRaisesRegex(ValueError,needle):run(lib,source,supplied_report=candidate)
    def test_inherited_claim_safety_label_mutation(self):
        self.tamper(lambda x:x['claims'][0].__setitem__('inherited_safety_state','approved'))
    def test_inherited_global_state_counts_mutation(self):
        self.tamper(lambda x:x['inherited_safety_states'].__setitem__('approved',99))
    def test_heading_rewrite_outside_identity_sha(self):self.tamper(lambda x:x['claims'][0].__setitem__('heading','Changed headline'))
    def test_context_rewrite_outside_identity_sha(self):self.tamper(lambda x:x['claims'][0].__setitem__('context_excerpt','New context'))
    def test_source_url_redirect_without_ledger(self):self.tamper(lambda x:x['claims'][0].__setitem__('source_url','https://changed.example.org'))
    def test_source_row_ref_changed(self):self.tamper(lambda x:x['claims'][0].__setitem__('source_row_key','other:1:alpha'))
    def test_citation_id_changed(self):self.tamper(lambda x:x['claims'][0].__setitem__('source_id','beta'))
    def test_context_ordinal_changed(self):self.tamper(lambda x:x['claims'][0].__setitem__('ordinal',2))
    def test_body_hash_changed(self):self.tamper(lambda x:x['claims'][0].__setitem__('body_sha256','0'*64))
    def test_whole_evidence_digest_changed(self):self.tamper(lambda x:x.__setitem__('evidence_digest_sha256','0'*64))
    def test_claim_removed(self):self.tamper(lambda x:x['claims'].pop())
    def test_claim_reordered(self):self.tamper(lambda x:x['claims'].reverse())
    def test_fake_claim_appended(self):self.tamper(lambda x:x['claims'].append(copy.deepcopy(x['claims'][0])))
    def test_authority_changed(self):self.tamper(lambda x:x.__setitem__('authority','CLINICALLY_VERIFIED'))
    def test_false_publication(self):self.tamper(lambda x:x.__setitem__('may_publish',True))
    def test_report_schema_removed(self):self.tamper(lambda x:x.pop('source_row_digest'))
    def test_new_publisher_override(self):self.tamper(lambda x:x.__setitem__('approval',True))
    def test_claim_count_changed(self):self.tamper(lambda x:x['counts'].__setitem__('citation_occurrences',999))
    def test_physical_source_count_changed(self):self.tamper(lambda x:x['counts'].__setitem__('physical_source_rows',999))
    def test_source_row_digest_changed(self):self.tamper(lambda x:x.__setitem__('source_row_digest','0'*64))
    def test_live_article_edited_after_receipt(self):
        lib,source=subject();candidate=canonicalize(lib,rows=source,fingerprint=None,expect={})
        lib.articles['article-01']['_body']+=' new appended source guidance'
        with self.assertRaisesRegex(ValueError,'canonical corpus/report divergence'):
            run(lib,source,supplied_report=candidate)
    def test_live_safety_status_edited_after_receipt(self):
        lib,source=subject();candidate=canonicalize(lib,rows=source,fingerprint=None,expect={})
        lib.articles['article-01']['safety_review']['state']='approved'
        with self.assertRaisesRegex(ValueError,'canonical corpus/report divergence'):
            run(lib,source,supplied_report=candidate)
    def test_live_physical_source_scope_edited_after_receipt(self):
        lib,source=subject();candidate=canonicalize(lib,rows=source,fingerprint=None,expect={})
        source[0]['supports']='Revised interpretation and reading scope'
        with self.assertRaisesRegex(ValueError,'canonical corpus/report divergence'):
            run(lib,source,supplied_report=candidate)
    def test_rejected_unsafe_canonical(self):
        def published(l,**kwargs):
            x=canonicalize(l,**kwargs);x['may_publish']=True;return x
        with self.assertRaisesRegex(ValueError,'canonical: publishing'):run(make_report=published)
    def test_rejected_wrong_claim_safety_metadata(self):
        def wrong(l,**kwargs):
            x=canonicalize(l,**kwargs);x['claims'][0]['inherited_safety_state']='approved';return x
        with self.assertRaisesRegex(ValueError,'claim inherited safety state'):
            run(make_report=wrong)
    def test_rejected_inconsistent_aggregate_safety(self):
        def wrong(l,**kwargs):
            x=canonicalize(l,**kwargs);x['inherited_safety_states']={'pending':36};return x
        with self.assertRaisesRegex(ValueError,'inherited safety labels'):run(make_report=wrong)
    def test_rejected_unsafe_intake(self):
        def bad(report,bundle,**kwargs):
            x=review_audit(report,bundle,**kwargs);x['may_publish']=True;return x
        with self.assertRaisesRegex(ValueError,'intake: unexpected approval'):run(review_audit=bad)
    def test_rejected_false_link_checks(self):
        def bad(report,bundle,**kwargs):
            x=review_audit(report,bundle,**kwargs);x['independent_human_source_checks_verified']=1;return x
        with self.assertRaisesRegex(ValueError,'intake: unexpected approval'):run(review_audit=bad)
    def test_rejected_false_clinical_approval(self):
        def bad(report,bundle,**kwargs):
            x=review_audit(report,bundle,**kwargs);x['qualified_safety_approvals']=1;return x
        with self.assertRaisesRegex(ValueError,'intake: unexpected approval'):run(review_audit=bad)
    def test_rejected_stale_review_digest(self):
        with self.assertRaisesRegex(ValueError,'stale'):
            run(response_bundle={'schema_version':1,'parent_evidence_digest_sha256':'0'*64,'claim_responses':[]})
    def test_rejected_fabricated_review(self):
        lib,source=subject();a=canonicalize(lib,rows=source,fingerprint=None,expect={})
        with self.assertRaisesRegex(ValueError,'invent'):
            run(lib,source,response_bundle={'schema_version':1,'parent_evidence_digest_sha256':a['evidence_digest_sha256'],
                                            'claim_responses':[{'reviewer':'not real'}]})
    def test_first_diff_type(self):self.assertIn('type',gate.first_diff({'a':1},{'a':'1'}))
    def test_first_diff_nested(self):self.assertIn('$.x.y',gate.first_diff({'x':{'y':9}},{'x':{'y':1}}))
    def test_first_diff_array_length(self):self.assertIn('length',gate.first_diff([1],[1,2]))
    def test_first_diff_array_order(self):self.assertIn('$[0]',gate.first_diff([2,1],[1,2]))
    def test_first_diff_missing_key(self):self.assertIn('keys changed',gate.first_diff({}, {'a':1}))
    def test_first_diff_boolean_vs_integer(self):self.assertIn('type',gate.first_diff(True,1))
    def test_first_diff_dict_order_irrelevant(self):self.assertIsNone(gate.first_diff({'z':1,'a':2},{'a':2,'z':1}))
    def test_first_diff_equal(self):self.assertIsNone(gate.first_diff({'k':[1,2]},{'k':[1,2]}))


class R10PrivateInputTests(unittest.TestCase):
    def test_private_json_direct_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'private.json';p.write_text('{"hold":true}')
            self.assertEqual(gate.read_private_json(p,Path(tmp))['hold'],True)
    def test_reject_private_json_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'file.json';p.write_text('{}')
            s=Path(tmp)/'link.json';s.symlink_to(p)
            with self.assertRaisesRegex(ValueError,'symlink'):gate.read_private_json(s,Path(tmp))
    def test_reject_outside_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);(d/'build').mkdir();p=d/'outside.json';p.write_text('{}')
            with self.assertRaisesRegex(ValueError,'direct file'):gate.read_private_json(p,d/'build')
    def test_reject_nested_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);(d/'nested').mkdir();p=d/'nested'/'review.json';p.write_text('{}')
            with self.assertRaisesRegex(ValueError,'direct file'):gate.read_private_json(p,d)
    def test_reject_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'unavailable'):gate.read_private_json(Path(tmp)/'none.json',Path(tmp))
    def test_reject_oversized_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'large.json';p.write_text('{} '+'x'*30)
            with self.assertRaisesRegex(ValueError,'oversized'):gate.read_private_json(p,Path(tmp),max_bytes=8)
    def test_reject_json_array(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'array.json';p.write_text('[]')
            with self.assertRaisesRegex(ValueError,'JSON object'):gate.read_private_json(p,Path(tmp))
    def test_reject_json_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'null.json';p.write_text('null')
            with self.assertRaisesRegex(ValueError,'JSON object'):gate.read_private_json(p,Path(tmp))
    def test_reject_empty_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'empty.json';p.write_text('')
            with self.assertRaisesRegex(ValueError,'unavailable'):gate.read_private_json(p,Path(tmp))


class R10OriginalPlaceholderTests(unittest.TestCase):
    def test_preserves_original_unread_base_record_without_claimed_support(self):
        src = rows()+[{'row_key':'base:4:unread','origin':'base','source_id':'unread',
                       'url':'https://example.org/not-yet-read', 'supports':None,
                       'verified_on':None,'human_link_check':False,
                       'reading_limits':'Listed in issue; not yet read for a specific claim.'}]
        report = gate.verify_physical_source_custody(src,expected_count=4,
                          expected_repeated_url_groups=1,expected_distinct_urls=3)
        self.assertEqual(report['unread_base_placeholders_NOT_VERIFIED'],1)
    def test_never_accepts_verified_placeholder_without_support(self):
        src=rows();src[0]['supports']=None;src[0]['origin']='base';src[0]['row_key']='base:0:alpha'
        src[0]['reading_limits']='not yet read';src[0]['verified_on']='2026-10-29'
        with self.assertRaisesRegex(ValueError,'placeholder'):
            gate.verify_physical_source_custody(src,3,1,2)
    def test_never_accepts_fragment_placeholder_without_support(self):
        src=rows();src[0]['supports']=None;src[0]['reading_limits']='not yet read'
        with self.assertRaisesRegex(ValueError,'placeholder'):
            gate.verify_physical_source_custody(src,3,1,2)
    def test_never_accepts_phantom_human_check_on_unread_placeholder(self):
        src=rows();src[0]['supports']=None;src[0]['origin']='base';src[0]['row_key']='base:0:alpha'
        src[0]['reading_limits']='not yet read';src[0]['human_link_check']=True
        with self.assertRaisesRegex(ValueError,'placeholder'):
            gate.verify_physical_source_custody(src,3,1,2)


if __name__ == '__main__':unittest.main()

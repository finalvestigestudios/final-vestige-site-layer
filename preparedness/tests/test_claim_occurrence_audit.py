"""Offline synthetic/adversarial checks for source-specific claim *occurrences*.
No fixture is described as an independent human or clinical source review.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import claim_occurrence_audit as audit


def fixture():
    meta = {
        'slug':'sample', 'n':1, 'status':{'publish':'draft'},
        'safety_review':{'state':'pending','reviewer':None,'date':None},
        'source_use':{'one':'Article explicitly asserts a specific fact',
                      'two':"Second fact's scope with independent support"},
        '_body':'<section><h2>Emergency water facts</h2><p>A reported claim needs checking {{cite:one}} and context.</p><ul><li>A second reported claim {{cite:two}} follows.</li></ul></section>'}
    sources = {
        'one':{'_origin':'start', 'url':'https://example.org/source','supports':'Source one section A','notes':'Pages 1–2'},
        'two':{'_origin':'base', 'url':'https://example.org/source','supports':'Source two section B','notes':'Pages 3–4'}}
    rows = [
        {'origin': 'start', 'source_id': 'one', 'url': 'https://example.org/source',
         'row_key':'start:0:one', 'supports':'Source one section A', 'reading_limits':'Pages 1–2'},
        {'origin': 'base', 'source_id': 'two', 'url': 'https://example.org/source',
         'row_key':'base:0:two', 'supports':'Source two section B', 'reading_limits':'Pages 3–4'},
    ]
    return meta, sources, rows


def article(meta=None, sources=None, rows=None, fingerprint='a'*64):
    m,s,r = fixture()
    if meta is not None:m=meta
    if sources is not None:s=sources
    if rows is not None:r=rows
    return audit.scan_article('sample',m,lambda meta,sid:s[sid],audit.physical_row_index(r),fingerprint)


class ParserChecks(unittest.TestCase):
    def parse(self, content):
        return audit.parse_visible_claims(content)

    def test_single_claim(self):
        self.assertEqual(len(self.parse('<p>This is a claim {{cite:one}}</p>')),1)
    def test_two_claims_same_paragraph(self):
        self.assertEqual([c['ordinal'] for c in self.parse('<p>First claim {{cite:one}} next claim {{cite:two}}</p>')],[1,2])
    def test_repeated_source_tokens_preserved(self):
        self.assertEqual([c['source_id'] for c in self.parse('<p>First claim {{cite:one}} and another {{cite:one}}</p>')],['one','one'])
    def test_nested_strong_context(self):
        c=self.parse('<p>Check <strong>this claim</strong> {{cite:one}}</p>')[0]
        self.assertIn('Check this claim',c['context_excerpt'])
    def test_list_item_context_isolated(self):
        c=self.parse('<ul><li>First item {{cite:one}}</li><li>Second item {{cite:two}}</li></ul>')
        self.assertNotIn('Second item',c[0]['context_excerpt'])
    def test_table_cell_context(self):
        self.assertEqual(self.parse('<table><tr><td>Specific reading {{cite:one}}</td></tr></table>')[0]['block_tag'],'td')
    def test_heading_is_recorded(self):
        self.assertEqual(self.parse('<h2>Source review</h2><p>Read the claim {{cite:one}}</p>')[0]['heading'],'Source review')
    def test_html_entities_are_decoded(self):
        self.assertIn('A & B',self.parse('<p>A &amp; B {{cite:one}}</p>')[0]['context_excerpt'])
    def test_whitespace_collapsed(self):
        self.assertIn('Many spaces',self.parse('<p>Many   spaces\n {{cite:one}}</p>')[0]['context_excerpt'])
    def test_original_body_line_preserved(self):
        self.assertEqual(self.parse('<p>First line\nSecond claim {{cite:one}}</p>')[0]['body_line'],1)
    def test_no_claim_yields_empty(self):
        self.assertEqual(self.parse('<p>A factual sentence.</p>'),[])
    def test_empty_body_fails(self):
        with self.assertRaisesRegex(ValueError,'missing'):self.parse('')
    def test_nul_fails(self):
        with self.assertRaisesRegex(ValueError,'NUL'):self.parse('<p>xx\x00{{cite:one}}</p>')
    def test_attribute_fake_citation_fails(self):
        with self.assertRaisesRegex(ValueError,'nonvisible'):self.parse('<p title="{{cite:one}}">A claim</p>')
    def test_comment_fake_citation_fails(self):
        with self.assertRaisesRegex(ValueError,'nonvisible'):self.parse('<!-- {{cite:one}} --><p>Claim {{cite:two}}</p>')
    def test_script_fake_citation_fails(self):
        with self.assertRaisesRegex(ValueError,'nonvisible'):self.parse('<script>"{{cite:one}}"</script>')
    def test_style_fake_citation_fails(self):
        with self.assertRaisesRegex(ValueError,'nonvisible'):self.parse('<style>{{cite:one}}</style>')
    def test_template_fake_citation_fails(self):
        with self.assertRaisesRegex(ValueError,'nonvisible'):self.parse('<template><p>{{cite:one}}</p></template>')
    def test_noscript_fake_citation_fails(self):
        with self.assertRaisesRegex(ValueError,'nonvisible'):self.parse('<noscript><p>{{cite:one}}</p></noscript>')
    def test_visible_token_outside_paragraph_fails(self):
        with self.assertRaisesRegex(ValueError,'outside'):self.parse('intro prose {{cite:one}}')
    def test_lone_cite_fails(self):
        with self.assertRaisesRegex(ValueError,'surrounding'):self.parse('<p>{{cite:one}}</p>')
    def test_unclosed_paragraph_fails(self):
        with self.assertRaisesRegex(ValueError,'unclosed'):self.parse('<p>A claim {{cite:one}}')
    def test_extra_end_tag_fails(self):
        with self.assertRaisesRegex(ValueError,'unmatched'):self.parse('</p><p>A claim {{cite:one}}</p>')
    def test_misnested_end_tag_fails(self):
        with self.assertRaisesRegex(ValueError,'unmatched'):self.parse('<section><p>Claim {{cite:one}}</section></p>')
    def test_long_excerpt_is_marked_not_silently_cut(self):
        c=self.parse('<p>'+('Long phrase '*300)+'{{cite:one}}</p>')[0]
        self.assertTrue(c['context_is_excerpt'])
        self.assertIn('EXCERPT',c['context_excerpt'])
        self.assertGreater(c['context_chars'],1000)
    def test_identical_text_stable_context_sha(self):
        s='<p>One fact {{cite:one}}</p>'
        self.assertEqual(self.parse(s)[0]['context_sha256'],self.parse(s)[0]['context_sha256'])
    def test_context_change_updates_hash(self):
        a=self.parse('<p>A factual reading {{cite:one}}</p>')[0]['context_sha256']
        b=self.parse('<p>A different reading {{cite:one}}</p>')[0]['context_sha256']
        self.assertNotEqual(a,b)
    def test_citation_inside_nested_paragraph_bound_to_paragraph(self):
        c=self.parse('<section><div><p>Nested fact {{cite:one}}</p></div></section>')[0]
        self.assertEqual(c['block_tag'],'p')


class ArticleChecks(unittest.TestCase):
    def test_proper_article_has_two_claims(self):
        claims,used=article()
        self.assertEqual(len(claims),2)
        self.assertEqual(used,{'one','two'})
    def test_all_claims_pending(self):
        self.assertTrue(all(x['claim_review']=='PENDING_INDEPENDENT_HUMAN_CHECK' for x in article()[0]))
    def test_all_claims_hold(self):
        self.assertTrue(all(x['release_state']=='HOLD' and x['may_publish'] is False for x in article()[0]))
    def test_contributor_origin_preserved(self):
        self.assertEqual([x['source_origin'] for x in article()[0]],['start','base'])
    def test_same_url_keeps_separate_rows(self):
        self.assertNotEqual(*[x['source_row_key'] for x in article()[0]])
    def test_source_use_not_mutated(self):
        meta,_,_=fixture();copy0=copy.deepcopy(meta)
        article(meta=meta)
        self.assertEqual(meta,copy0)
    def test_slug_mismatch_fails(self):
        meta,_,_=fixture();meta['slug']='another'
        with self.assertRaisesRegex(ValueError,'slug'):article(meta=meta)
    def test_non_draft_fails(self):
        meta,_,_=fixture();meta['status']['publish']='publish'
        with self.assertRaisesRegex(ValueError,'non-draft'):article(meta=meta)
    def test_unknown_safety_state_fails(self):
        meta,_,_=fixture();meta['safety_review']['state']='CLINICALLY_VERIFIED'
        with self.assertRaisesRegex(ValueError,'unknown safety'):article(meta=meta)
    def test_legacy_approved_does_not_clear_claim(self):
        meta,_,_=fixture();meta['safety_review']['state']='approved'
        claims,_=article(meta=meta)
        self.assertTrue(all(x['claim_review'].startswith('PENDING') for x in claims))
    def test_missing_source_use_fails(self):
        meta,_,_=fixture();meta.pop('source_use')
        with self.assertRaisesRegex(ValueError,'source'):article(meta=meta)
    def test_extra_source_use_fails(self):
        meta,_,_=fixture();meta['source_use']['ghost']='Another note'
        with self.assertRaisesRegex(ValueError,'parity'):article(meta=meta)
    def test_missing_cited_source_use_fails(self):
        meta,_,_=fixture();meta['source_use'].pop('two')
        with self.assertRaisesRegex(ValueError,'parity'):article(meta=meta)
    def test_whitespace_source_use_fails(self):
        meta,_,_=fixture();meta['source_use']['one']='   '
        with self.assertRaisesRegex(ValueError,'evidence use note'):article(meta=meta)
    def test_nonstring_source_use_fails(self):
        meta,_,_=fixture();meta['source_use']['one']=None
        with self.assertRaisesRegex(ValueError,'evidence use note'):article(meta=meta)
    def test_oversize_source_use_fails(self):
        meta,_,_=fixture();meta['source_use']['one']='x'*6001
        with self.assertRaisesRegex(ValueError,'evidence use note'):article(meta=meta)
    def test_missing_physical_row_fails(self):
        _,_,rows=fixture()
        with self.assertRaisesRegex(ValueError,'physical contributor row'):article(rows=rows[:1])
    def test_resolver_origin_borrow_fails(self):
        _,sources,_=fixture();sources['one']['_origin']='food'
        with self.assertRaisesRegex(ValueError,'physical contributor row'):article(sources=sources)
    def test_resolver_url_drift_fails(self):
        _,sources,_=fixture();sources['one']['url']='https://other.example.org/'
        with self.assertRaisesRegex(ValueError,'physical contributor row'):article(sources=sources)
    def test_missing_support_assertion_fails(self):
        _,_,rows=fixture();rows[0]['supports']=''
        with self.assertRaisesRegex(ValueError,'support assertion'):article(rows=rows)
    def test_sha_must_be_64_lowercase_hex(self):
        with self.assertRaisesRegex(ValueError,'SHA256'):article(fingerprint='NO')
    def test_duplicate_row_identity_fails(self):
        _,_,rows=fixture();rows.append(copy.deepcopy(rows[0]))
        with self.assertRaisesRegex(ValueError,'duplicate'):article(rows=rows)
    def test_duplicate_key_fails(self):
        _,_,rows=fixture();rows[1]['row_key']=rows[0]['row_key']
        with self.assertRaisesRegex(ValueError,'duplicate'):article(rows=rows)
    def test_http_source_fails(self):
        _,_,rows=fixture();rows[1]['url']='http://example.org/source'
        with self.assertRaisesRegex(ValueError,'non-HTTPS'):article(rows=rows)
    def test_token_ordinal_distinguishes_repeat(self):
        meta,_,_=fixture();meta['_body']=meta['_body'].replace('{{cite:one}}','{{cite:one}} still one {{cite:one}}')
        values=[x['claim_request_sha256'] for x in article(meta=meta)[0]]
        self.assertEqual(len(values),len(set(values)))
    def test_body_edit_invalidates_fingerprint(self):
        meta,_,_=fixture()
        orig=article(meta=meta)[0][0]['claim_request_sha256']
        meta['_body']=meta['_body'].replace('A reported claim','A different claim')
        self.assertNotEqual(orig,article(meta=meta)[0][0]['claim_request_sha256'])
    def test_source_use_edit_invalidates_fingerprint(self):
        meta,_,_=fixture();a=article(meta=meta)[0][0]['claim_request_sha256']
        meta['source_use']['one']='Different described article usage'
        self.assertNotEqual(a,article(meta=meta)[0][0]['claim_request_sha256'])
    def test_support_drift_invalidates_fingerprint(self):
        _,_,rows=fixture();a=article(rows=rows)[0][0]['claim_request_sha256']
        rows[0]['supports']='Different claimed scope'
        self.assertNotEqual(a,article(rows=rows)[0][0]['claim_request_sha256'])
    def test_reading_limits_drift_invalidates_fingerprint(self):
        _,_,rows=fixture();a=article(rows=rows)[0][0]['claim_request_sha256']
        rows[0]['reading_limits']='Different pages read'
        self.assertNotEqual(a,article(rows=rows)[0][0]['claim_request_sha256'])
    def test_stale_evidence_fingerprint_invalidates_claim(self):
        a=article(fingerprint='a'*64)[0][0]['claim_request_sha256']
        b=article(fingerprint='b'*64)[0][0]['claim_request_sha256']
        self.assertNotEqual(a,b)


class ReportChecks(unittest.TestCase):
    class FakeLib:
        def __init__(self, meta, source):self.articles={'sample':meta};self.sources=source
        def source_for(self, meta, source_id):return self.sources[source_id]
        def url_path(self, slug):return '/preparedness/'+slug+'/'
    def get(self, **changes):
        meta,source,rows=fixture();meta.update(changes)
        return audit.make_report(self.FakeLib(meta,source),rows=rows,
            fingerprint=lambda lib,meta:'a'*64,
            expect={'draft_items':1,'article_source_pairs':2,'physical_source_rows':2,'shared_url_groups':1})
    def test_report_contains_every_citation(self):
        self.assertEqual(self.get()['counts']['citation_occurrences'],2)
    def test_report_deterministic(self):
        self.assertEqual(audit.digest(self.get()),audit.digest(self.get()))
    def test_report_explicit_hold(self):
        r=self.get();self.assertFalse(r['may_publish']);self.assertEqual(r['release_state'],'HOLD')
    def test_report_not_human_verified(self):
        r=self.get();self.assertEqual(r['verified_citation_claims'],0)
        self.assertEqual(r['human_link_checks_documented_by_tool'],0)
    def test_report_preserves_legacy_safety_pending(self):
        self.assertEqual(self.get()['inherited_safety_states'],{'pending':1})
    def test_baseline_drift_fails(self):
        meta,source,rows=fixture()
        with self.assertRaisesRegex(ValueError,'baseline drift'):
            audit.make_report(self.FakeLib(meta,source),rows=rows,
                fingerprint=lambda lib,meta:'a'*64,expect={'draft_items':35})
    def test_duplicate_route_fails(self):
        meta,source,rows=fixture()
        alt=copy.deepcopy(meta);alt['slug']='other'
        fake=self.FakeLib(meta,source);fake.articles['other']=alt
        fake.url_path=lambda slug:'/preparedness/same/'
        with self.assertRaisesRegex(ValueError,'duplicate article route'):
            audit.make_report(fake,rows=rows,fingerprint=lambda lib,meta:'a'*64)
    def test_uncited_sources_not_deleted(self):
        r=self.get();self.assertEqual(r['counts']['physical_source_rows'],2)


class ExportChecks(unittest.TestCase):
    def test_csv_headers_present(self):
        self.assertIn('claim_request_sha256',audit.csv_export(ReportChecks().get()).splitlines()[0])
    def test_csv_formula_equals_escaped(self):
        self.assertEqual(audit.csv_safe('=IMPORTXML(1)'),"'=IMPORTXML(1)")
    def test_csv_formula_plus_escaped(self):
        self.assertEqual(audit.csv_safe('+SUM(2,3)'),"'+SUM(2,3)")
    def test_csv_formula_minus_escaped(self):
        self.assertEqual(audit.csv_safe('-1+2'),"'-1+2")
    def test_csv_formula_at_escaped(self):
        self.assertEqual(audit.csv_safe('@DDE'),"'@DDE")
    def test_csv_formula_leading_spaces_escaped(self):
        self.assertTrue(audit.csv_safe('  =SUM(2)').startswith("'"))
    def test_csv_tab_escaped(self):
        self.assertTrue(audit.csv_safe('\t=SUM(2)').startswith("'"))
    def test_csv_safe_plain_text_unchanged(self):
        self.assertEqual(audit.csv_safe('Plain text'),'Plain text')
    def test_csv_quote_escaped_by_writer(self):
        r=ReportChecks().get();r['claims'][0]['context_excerpt']='Context "quoted", with comma'
        self.assertIn('"Context ""quoted"", with comma"',audit.csv_export(r))
    def test_export_success_in_private_build(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);target=root/'report.json'
            audit.safe_export(target,'test',root)
            self.assertEqual(target.read_text(),'test')
    def test_export_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'build';root.mkdir()
            with self.assertRaisesRegex(ValueError,'direct path'):
                audit.safe_export(root/'../leak.json','test',root)
    def test_export_rejects_nested_directory(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'build';root.mkdir();(root/'nested').mkdir()
            with self.assertRaisesRegex(ValueError,'direct path'):
                audit.safe_export(root/'nested/x.json','test',root)
    def test_export_rejects_file_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'build';root.mkdir();(Path(d)/'other').write_text('safe')
            (root/'report').symlink_to(Path(d)/'other')
            with self.assertRaisesRegex(ValueError,'symlink'):
                audit.safe_export(root/'report','bad',root)
            self.assertEqual((Path(d)/'other').read_text(),'safe')
    def test_export_rejects_nonexistent_build_root(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):audit.safe_export(Path(d)/'x', 'x',Path(d)/'no-build')

if __name__=='__main__':unittest.main()

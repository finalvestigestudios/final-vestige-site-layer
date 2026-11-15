"""R386 adversarial synthetic private-export tests, NOT authenticated article QA."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

TOOLS=Path(__file__).resolve().parents[1]/'tools'
spec=importlib.util.spec_from_file_location('r386',TOOLS/'r386_rendered_citation_parity.py')
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
spec384=importlib.util.spec_from_file_location('r384',TOOLS/'r384_variant_review_packet.py')
R384=importlib.util.module_from_spec(spec384);spec384.loader.exec_module(R384)
A='8'*40;M='9'*40
SRC='<li id="src-1"><a href="https://example.gov/guide" rel="noopener">Official reference</a> used for this claim</li>'
ORIGINAL='<p>Keep a working household contact plan {{cite:ref-a}} for your family.</p><p>Review the backup plan {{cite:ref-a}} every year.</p>'
RENDERED='<p>Keep a working household contact plan <sup class="pa-cite"><a href="#src-1" aria-label="Source 1: Official reference">[1]</a></sup> for your family.</p><p>Review the backup plan <sup class="pa-cite"><a href="#src-1" aria-label="Source 1: Official reference">[1]</a></sup> every year.</p>'
DRAFT='<p>Draft: not public</p><p>Independent safety/source and QD verification pending</p>'
REVIEW='<p>Human source/safety review and independent QD are required before publication.</p>'

def packet():
    variants=[]
    blocks=R384.paragraphs(ORIGINAL.encode())
    for i in range(35):
        variants.append({'slug':f'article-{i:02d}','variants':[{'branch':'claude/prep-start-bbfeb8',
            'body_sha':A,'meta_sha':M,'safety_state':'pending',
            'blocks':blocks,'words':sum(b['words'] for b in blocks),'missing_reading_scopes':[],
            'source_use':{'ref-a':'Household communication plan'}}]})
    return {'status':'REVIEW_PACKET_HARD_HOLD','publication_approved':False,
            'qualified_safety_approved':False,'articles':variants,
            'unselected_conflicts':[{'path':f'conflict-{i}'} for i in range(9)]}

def article(slug):
    return ('<div class="pa pa-article" data-slug="'+slug+'"><header>'+DRAFT+'</header>'
            '<div class="pa-shell"><div class="pa-body" id="pa-main">'+RENDERED+'</div></div>'
            '<section class="pa-sources"><ol>'+SRC+'</ol></section><section class="pa-review">'+REVIEW+'</section>'
            '<script type="application/ld+json">'+json.dumps({'mainEntityOfPage':f'https://finalvestige.com/preparedness/family-communication/{slug}/'})+'</script></div>')

def wp(a):return '<!-- wp:html -->\n<style>.pa {color: black}</style>\n'+a+'\n<!-- /wp:html -->'
def prev(a):return '<!doctype html><html lang="en"><head><meta name="robots" content="noindex,nofollow"></head><body><main>'+a+'</main></body></html>'

class ExportParityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.wp=self.root/'wp';self.pr=self.root/'preview'
        self.wp.mkdir();self.pr.mkdir()
        self.manifest=packet()
        for i in range(35):
            s=f'article-{i:02d}';a=article(s)
            (self.wp/(s+'.html')).write_text(wp(a));(self.pr/(s+'.html')).write_text(prev(a))
    def runaudit(self):return G.audit(self.manifest,self.wp,self.pr,source_urls={'claude/prep-start-bbfeb8':{'ref-a':'https://example.gov/guide'},'claude/prep-shelter-variant':{'ref-a':'https://example.gov/guide'}})
    def update(self,old,new,slug='article-00',where='both'):
        for folder in (self.wp,self.pr) if where=='both' else (self.wp,) if where=='wp' else (self.pr,):
            path=folder/(slug+'.html')
            data=path.read_text();self.assertIn(old,data)
            path.write_text(data.replace(old,new,1))
    def assertFails(self,reason):
        result=self.runaudit()
        self.assertEqual(result['status'],'INVALID_HARD_HOLD')
        self.assertIn(reason,'\n'.join(result['errors']))
        self.assertFalse(result['publication_approved'])
    def test_complete_35_export_pair_review_hold(self):
        r=self.runaudit();self.assertEqual(r['status'],'RENDER_PARITY_REVIEW_HARD_HOLD',r['errors'][:10])
        self.assertEqual(r['counts']['original_articles'],35)
        self.assertEqual(r['counts']['matched_exports'],35)
        self.assertEqual(r['counts']['candidate_matches'],35)
        self.assertEqual(r['counts']['unselected_original_forks'],9)
        self.assertFalse(r['publication_approved'])
    def test_deterministic_digest(self):self.assertEqual(self.runaudit()['report_sha256'],self.runaudit()['report_sha256'])
    def test_no_mutation(self):
        before={p:str(p.stat().st_mtime_ns) for d in (self.wp,self.pr) for p in d.iterdir()}
        self.runaudit();after={p:str(p.stat().st_mtime_ns) for d in (self.wp,self.pr) for p in d.iterdir()}
        self.assertEqual(before,after)
    def test_no_real_repo_cli_hard_hold(self):
        p=subprocess.run(['python','-I',str(TOOLS/'r386_rendered_citation_parity.py'),
                          '--repo','/no/such/repo','--wp',str(self.wp),'--preview',str(self.pr)],capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertIn('INVALID_HARD_HOLD',p.stdout)
    def test_slugs_from_original_packet(self):
        self.manifest['articles'].pop();self.assertFails('ORIGINAL_ARTICLE_OR_FORK_INVENTORY_INVALID')
    def test_unselected_forks_stay_nine(self):
        self.manifest['unselected_conflicts'].pop();self.assertFails('ORIGINAL_ARTICLE_OR_FORK_INVENTORY_INVALID')
    def test_cannot_convert_packet_to_approval(self):
        self.manifest['publication_approved']=True;self.assertFails('UNAUTHENTIC_OR_APPROVED_PACKET')
    def test_safety_approval_spoof_rejected(self):
        self.manifest['qualified_safety_approved']=True;self.assertFails('UNAUTHENTIC_OR_APPROVED_PACKET')
    def test_duplicate_article_slug(self):
        self.manifest['articles'][1]['slug']='article-00';self.assertFails('DUPLICATE_OR_INVALID_ORIGINAL_SLUG')
    def test_unexpected_article_slug(self):
        self.manifest['articles'][1]['slug']='bad/slug';self.assertFails('DUPLICATE_OR_INVALID_ORIGINAL_SLUG')
    def test_no_wordpress_directory(self):
        for p in self.wp.iterdir():p.unlink()
        self.wp.rmdir();self.assertFails('MISSING_ORIGINAL_ARTICLE_EXPORTS')
    def test_missing_preview_file(self):
        (self.pr/'article-09.html').unlink();self.assertFails('WP_PREVIEW_FILE_SET_MISMATCH')
    def test_missing_wp_file(self):
        (self.wp/'article-12.html').unlink();self.assertFails('WP_PREVIEW_FILE_SET_MISMATCH')
    def test_wrong_extra_export(self):
        (self.wp/'surprise.html').write_text('X');(self.pr/'surprise.html').write_text('X');self.assertFails('UNRECOGNIZED_EXTRA_EXPORT')
    def test_extra_landing_requires_separate_review(self):
        (self.wp/'landing.html').write_text('fake');(self.pr/'landing.html').write_text('fake')
        self.assertEqual(self.runaudit()['counts']['nonarticle_exports_needing_independent_review'],1)
    def test_symlink_export_rejected(self):
        (self.wp/'article-00.html').unlink();(self.wp/'article-00.html').symlink_to(self.wp/'article-01.html')
        self.assertFails('EXPORT_READ_OR_PARSE_ERROR')
    def test_cannot_use_blank_sources(self):
        self.update('Official reference','');self.assertFails('CITATION_LABEL_MISMATCH')
    def test_different_wp_preview_subtrees(self):
        self.update('Official reference','Altered title',where='wp');self.assertFails('WP_PREVIEW_ARTICLE_BYTES_MISMATCH')
    def test_no_unreviewed_text_deletion(self):
        self.update('working household contact plan','working contact plan');self.assertFails('ORIGINAL_PROSE_BLOCK_MISMATCH')
    def test_no_unreviewed_extra_advice(self):
        self.update('for your family.','for your family. Trust us completely.');self.assertFails('ORIGINAL_PROSE_BLOCK_MISMATCH')
    def test_repeated_citation_custody(self):
        self.update('Review the backup plan <sup','Review the backup plan without source <sup');self.assertFails('ORIGINAL_PROSE_BLOCK_MISMATCH')
    def test_missing_citation_sup(self):
        self.update('<sup class="pa-cite"><a href="#src-1" aria-label="Source 1: Official reference">[1]</a></sup>','');self.assertFails('CITATION_OCCURRENCE_ORDER_MISMATCH')
    def test_duplicate_citation_sup(self):
        c='<sup class="pa-cite"><a href="#src-1" aria-label="Source 1: Official reference">[1]</a></sup>'
        self.update(c,c+c);self.assertFails('CITATION_OCCURRENCE_ORDER_MISMATCH')
    def test_footnote_href_missing(self):
        self.update('href="#src-1"','href="#src-99"');self.assertFails('CITATION_OCCURRENCE_ORDER_MISMATCH')
    def test_footnote_href_javascript(self):
        self.update('href="#src-1"','href="javascript:alert(1)"');self.assertFails('MALFORMED_CITATION')
    def test_citation_accessibility_label(self):
        self.update('aria-label="Source 1: Official reference"','aria-label="Citation"');self.assertFails('CITATION_LABEL_MISMATCH')
    def test_citation_visible_number(self):
        self.update('>[1]</a></sup>', '>[7]</a></sup>');self.assertFails('CITATION_LABEL_MISMATCH')
    def test_citation_hidden_css(self):
        self.update('<sup class="pa-cite">','<sup class="pa-cite" style="display:none">');self.assertFails('HIDDEN_CITATION')
    def test_citation_hidden_aria(self):
        self.update('<sup class="pa-cite">','<sup class="pa-cite" aria-hidden="true">');self.assertFails('HIDDEN_CITATION')
    def test_citation_hidden_opacity(self):
        self.update('<sup class="pa-cite">','<sup class="pa-cite" style="opacity: 0">');self.assertFails('HIDDEN_CITATION')
    def test_citation_hidden_font(self):
        self.update('<sup class="pa-cite">','<sup class="pa-cite" style="font-size:0">');self.assertFails('HIDDEN_CITATION')
    def test_source_anchor_missing(self):
        self.update('id="src-1"','id="src-2"');self.assertFails('SOURCE_ANCHOR_SET_MISMATCH')
    def test_source_anchor_duplicate(self):
        self.update('<li id="src-1">','<li id="src-1"><li id="src-1">');self.assertFails('DUPLICATE_SOURCE_ANCHOR')
    def test_source_link_other_https_not_original(self):
        self.update('https://example.gov/guide','https://different.gov/guide');self.assertFails('SOURCE_URL_NOT_ORIGINAL_ORIGIN')
    def test_origin_registry_required(self):
        r=G.audit(self.manifest,self.wp,self.pr)
        self.assertIn('SOURCE_ORIGIN_REGISTRY_UNAVAILABLE',r['errors'])
    def test_source_link_http(self):
        self.update('https://example.gov/guide','http://example.gov/guide');self.assertFails('UNSAFE_SOURCE_HREF')
    def test_source_link_javascript(self):
        self.update('https://example.gov/guide','javascript:alert(1)');self.assertFails('UNSAFE_SOURCE_HREF')
    def test_source_link_data(self):
        self.update('https://example.gov/guide','data:text/html,x');self.assertFails('UNSAFE_SOURCE_HREF')
    def test_source_link_credentials(self):
        self.update('https://example.gov/guide','https://user:pass@example.gov/guide');self.assertFails('UNSAFE_SOURCE_HREF')
    def test_source_link_rel(self):
        self.update('rel="noopener"','rel="noreferrer"');self.assertFails('SOURCE_REL_MISSING')
    def test_source_link_hidden(self):
        self.update('<li id="src-1">','<li id="src-1" style="display:none">');self.assertFails('HIDDEN_OR_EMPTY_SOURCE')
    def test_source_link_duplicate(self):
        self.update('</a> used for this claim','</a><a href="https://second.gov" rel="noopener">Second</a> used for this claim')
        self.assertFails('SOURCE_OUTBOUND_COUNT')
    def test_no_draft_banner(self):
        self.update('Draft: not public','Reviewed and published');self.assertFails('DRAFT_WARNING_ABSENT')
    def test_no_independent_warning(self):
        self.update('Independent safety/source and QD verification pending','All checks passed')
        self.assertFails('DRAFT_WARNING_ABSENT')
    def test_no_review_record(self):
        self.update(REVIEW,'');self.assertFails('INDEPENDENT_REVIEW_WARNING_ABSENT')
    def test_no_unresolved_tokens(self):
        self.update('every year.','every year. {{cite:not-sourced}}');self.assertFails('UNRESOLVED_BODY_TOKENS')
    def test_no_fake_published_canonical(self):
        self.update('https://finalvestige.com/preparedness/family-communication/article-00/','https://example.net/article-00/')
        self.assertFails('CANONICAL_URL_INVALID')
    def test_canonical_wrong_article_path(self):
        self.update('family-communication/article-00/','family-communication/article-33/')
        self.assertFails('CANONICAL_URL_INVALID')
    def test_invalid_data_slug(self):
        self.update('data-slug="article-00"','data-slug="article-01"');self.assertFails('ARTICLE_DATA_SLUG_MISMATCH')
    def test_noindex_removed(self):
        self.update('<meta name="robots" content="noindex,nofollow">','',where='preview')
        self.assertFails('PRIVATE_PREVIEW_ROBOTS_MISSING')
    def test_wp_wrapper_removed(self):
        self.update('<!-- wp:html -->','',where='wp');self.assertFails('EXPORT_WRAPPER_INVALID')
    def test_original_variant_tamper_sha(self):
        self.manifest['articles'][0]['variants'][0]['body_sha']='not-sha';self.assertFails('INVALID_ORIGINAL_VARIANT')
    def test_original_variant_safety_tamper(self):
        self.manifest['articles'][0]['variants'][0]['safety_state']='passed';self.assertFails('INVALID_ORIGINAL_VARIANT')
    def test_source_scope_does_not_autofill(self):
        self.manifest['articles'][0]['variants'][0]['missing_reading_scopes']=['ref-a']
        self.assertFails('ORIGINAL_READING_SCOPE_MISSING')
    def test_original_variant_cannot_be_silently_selected(self):
        v=copy.deepcopy(self.manifest['articles'][0]['variants'][0]);v['branch']='claude/prep-shelter-variant'
        self.manifest['articles'][0]['variants'].append(v)
        r=self.runaudit();self.assertEqual(r['status'],'RENDER_PARITY_REVIEW_HARD_HOLD')
        self.assertEqual(len(r['articles'][0]['matching_variant_candidates']),2)
    def test_paragraph_hashes_dont_contain_raw_advice_in_report(self):
        self.assertNotIn('Keep a working household contact plan',json.dumps(self.runaudit()))
    def test_variant_loss_detected(self):
        self.manifest['articles'][0]['variants'][0]['blocks'].pop()
        self.assertFails('NO_MATCHING_ORIGINAL_VARIANT')
    def test_filename_stem_enforced(self):
        (self.wp/'article-00.html').rename(self.wp/'renamed.html');self.assertFails('MISSING_ORIGINAL_ARTICLE_EXPORTS')


if __name__=='__main__':unittest.main()

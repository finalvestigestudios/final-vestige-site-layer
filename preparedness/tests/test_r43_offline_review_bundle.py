"""R43 offline review desk: synthetic adversarial source/citation custody tests."""
import copy
from html.parser import HTMLParser
import hashlib
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from test_r42_article_review_dossiers import fixtures, run as r42
import reviewer_offline_html_gate as gate

H=lambda n:format(n,'064x')

def example(uncited=False):
    original,tax,counts=fixtures(uncited=uncited)
    return r42(original,tax,counts),counts

def view(packet,counts,pin=None):
    return gate.build_offline_html(packet,trusted_r42_sha256=(
        packet['fingerprint_sha256'] if pin is None else pin),expected=counts)

def restamp(packet):
    for article in packet['article_dossiers']:
        article['fingerprint_sha256']=gate.digest(
            {k:v for k,v in article.items() if k!='fingerprint_sha256'})
    packet['fingerprint_sha256']=gate.digest(
        {k:v for k,v in packet.items() if k!='fingerprint_sha256'})
    return packet

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]
        self.url_attrs=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append(tag)
        self.url_attrs.extend(v for k,v in attrs if k in ('src','href','action'))

class Positive(unittest.TestCase):
    def setUp(self):
        self.packet,self.counts=example()
        self.out=view(self.packet,self.counts)
    def test_three_original_dossiers_preserved(self):
        self.assertEqual(len(self.packet['article_dossiers']),3)
    def test_five_offline_files(self):
        self.assertEqual(len(self.out['html_files']),5)
    def test_index(self):
        self.assertIn('index.html',self.out['html_files'])
    def test_global_groups(self):
        self.assertIn('global-source-variants.html',self.out['html_files'])
    def test_two_scopes_one_url_not_merged(self):
        self.assertIn('Full article-specific reading note 1',
                      self.out['html_files']['articles/first-guide.html'])
        self.assertIn('Full article-specific reading note 2',
                      self.out['html_files']['articles/old-ways.html'])
    def test_all_five_citations(self):
        self.assertEqual(sum(page.count('exact_original_context')
            for name,page in self.out['html_files'].items()
            if name.startswith('articles/')),5)
    def test_all_three_source_readings(self):
        self.assertEqual(sum(page.count('full_original_article_source_use')
            for name,page in self.out['html_files'].items()
            if name.startswith('articles/')),3)
    def test_caseids_present(self):
        self.assertIn(H(611),self.out['html_files']['articles/first-guide.html'])
    def test_uncited_variant_kept(self):
        p,c=example(uncited=True)
        o=view(p,c)
        self.assertIn('unused-shared-source',o['html_files']['global-source-variants.html'])
    def test_original_taxonomy_status_not_approval(self):
        self.assertIn('safety-approved-draft',self.out['html_files']['articles/first-guide.html'])
        self.assertIn('NOT human safety or publication approval',
                      self.out['html_files']['articles/first-guide.html'])
    def test_no_external_loading(self):
        for page in self.out['html_files'].values():
            h=Tags();h.feed(page)
            self.assertFalse(set(h.tags)&{'script','img','form','iframe','object','embed','base'})
            self.assertTrue(all(not x.startswith(('http:','https:','//','javascript:','data:'))
                                for x in h.url_attrs))
    def test_csp_offline(self):
        self.assertTrue(all("connect-src 'none'" in x
                            for x in self.out['html_files'].values()))
    def test_plain_text_urls(self):
        self.assertIn('https://example.org/contributor-shared-source',
                      self.out['html_files']['global-source-variants.html'])
    def test_all_pages_explicit_hold(self):
        self.assertTrue(all('PRIVATE / UNVERIFIED / HOLD' in page
                            for page in self.out['html_files'].values()))
    def test_evidence_is_escaped(self):
        b=copy.deepcopy(self.packet)
        b['article_dossiers'][0]['original_review_records']['scopes'][0][
          'full_original_article_source_use']='<script>alert("x")</script>&unsafe'
        restamp(b)
        html=view(b,self.counts)['html_files']['articles/first-guide.html']
        self.assertIn('&lt;script&gt;',html)
        self.assertNotIn('<script>',html)
        self.assertIn('&amp;unsafe',html)
    def test_deterministic(self):
        self.assertEqual(self.out,view(self.packet,self.counts))
    def test_source_packet_unmodified(self):
        b=copy.deepcopy(self.packet);view(self.packet,self.counts)
        self.assertEqual(self.packet,b)
    def test_manifest_hashes_every_file(self):
        for path,content in self.out['html_files'].items():
            self.assertEqual(self.out['manifest']['files'][path]['sha256_utf8'],
                             hashlib.sha256(content.encode()).hexdigest())
    def test_manifest_self_fingerprint(self):
        m=self.out['manifest']
        self.assertEqual(m['fingerprint_sha256'],
                         gate.digest({k:v for k,v in m.items()
                                      if k!='fingerprint_sha256'}))
    def test_all_manifest_release_flags_false(self):
        self.assertTrue(all(self.out['manifest'][f] is False for f in gate.FLAGS))
    def test_tool_separate(self):
        self.assertIn('articles/water-planner.html',self.out['html_files'])

class Negative(unittest.TestCase):
    def reject(self,change,repin=True):
        b,c=example()
        pin=b['fingerprint_sha256'];change(b);restamp(b)
        with self.assertRaises((gate.OfflineHold,ValueError,TypeError,KeyError)):
            view(b,c,pin=b['fingerprint_sha256'] if repin else pin)
    def test_wrong_external_pin(self):
        b,c=example()
        with self.assertRaises(gate.OfflineHold):view(b,c,pin='a'*64)
    def test_missing_pin(self):
        b,c=example()
        with self.assertRaises(gate.OfflineHold):view(b,c,pin='')
    def test_mutation_breaks_original_pin(self):
        self.reject(lambda b:b['article_dossiers'][0].update(title='changed'),False)
    def test_root_wrong_census(self):
        self.reject(lambda b:b['counts'].update(claim_reviews=17))
    def test_root_wrong_machine_authority(self):
        self.reject(lambda b:b.update(machine_authority='VERIFIED_APPROVAL'))
    def test_root_nonhold(self):
        self.reject(lambda b:b.update(release_state='PASS'))
    def test_root_created_approval(self):
        self.reject(lambda b:b.update(publication_authorized=True))
    def test_root_safety_claim(self):
        self.reject(lambda b:b.update(qualified_hazard_safety_check_completed=True))
    def test_root_human_review_claim(self):
        self.reject(lambda b:b.update(all_human_reviews_completed=True))
    def test_missing_article(self):
        self.reject(lambda b:b['article_dossiers'].pop())
    def test_duplicate_slug(self):
        self.reject(lambda b:b['article_dossiers'][1].update(slug='first-guide'))
    def test_path_traversal(self):
        self.reject(lambda b:b['article_dossiers'][1].update(slug='../site'))
    def test_bad_tool_class(self):
        self.reject(lambda b:b['article_dossiers'][1].update(is_tool=True))
    def test_missing_claim(self):
        self.reject(lambda b:b['article_dossiers'][0]['original_review_records']['claims'].pop())
    def test_extra_duplicate_claim(self):
        self.reject(lambda b:b['article_dossiers'][0]['original_review_records']['claims'].append(
            copy.deepcopy(b['article_dossiers'][0]['original_review_records']['claims'][0])))
    def test_zero_claim_count(self):
        self.reject(lambda b:b['article_dossiers'][0]['counts'].update(claims=0))
    def test_bad_priority_count(self):
        self.reject(lambda b:b['article_dossiers'][0].update(high_priority_claim_cases=100))
    def test_missing_scope(self):
        self.reject(lambda b:b['article_dossiers'][0]['original_review_records']['scopes'].pop())
    def test_claim_moves_to_unknown_article(self):
        self.reject(lambda b:b['article_dossiers'][0]['original_review_records']['claims'][0].update(slug='other'))
    def test_scope_moves_to_unknown_article(self):
        self.reject(lambda b:b['article_dossiers'][0]['original_review_records']['scopes'][0].update(slug='other'))
    def test_wrong_relationship(self):
        self.reject(lambda b:b['article_dossiers'][0]['original_review_records']['claims'][0].update(relationship_sha256=H(999)))
    def test_wrong_impacted_claims(self):
        self.reject(lambda b:b['article_dossiers'][0]['original_review_records']['scopes'][0].update(impacted_claims='5'))
    def test_non_numeric_impacted_claims(self):
        self.reject(lambda b:b['article_dossiers'][0]['original_review_records']['scopes'][0].update(impacted_claims='NaN'))
    def test_forged_reviewer_progress(self):
        self.reject(lambda b:b['article_dossiers'][0]['original_review_records']['claims'][0].update(review_state='APPROVED'))
    def test_forged_human_notes(self):
        self.reject(lambda b:b['article_dossiers'][0]['original_review_records']['claims'][0].update(human_claim_support_assessment='PASS'))
    def test_global_group_conflicting_url(self):
        self.reject(lambda b:b['article_dossiers'][1]['original_review_records']['groups'][0].update(source_url='https://example.org/different'))
    def test_global_group_conflicting_text(self):
        self.reject(lambda b:b['article_dossiers'][1]['original_review_records']['groups'][0].update(full_original_crosswalk_group_json='changed'))
    def test_duplicate_global_group(self):
        self.reject(lambda b:b['article_dossiers'][0]['original_review_records']['groups'].append(
            copy.deepcopy(b['article_dossiers'][0]['original_review_records']['groups'][0])))
    def test_nul_evidence(self):
        self.reject(lambda b:b['article_dossiers'][0]['original_review_records']['scopes'][0].update(full_original_article_source_use='\0'))
    def test_missing_group_in_both_articles(self):
        self.reject(lambda b:[d['original_review_records']['groups'].clear() for d in b['article_dossiers']])
    def test_bad_expected_census_type(self):
        b,c=example()
        with self.assertRaises(gate.OfflineHold):
            gate.build_offline_html(b,trusted_r42_sha256=b['fingerprint_sha256'],
                                    expected=list(c))

# The six review/release flags are independently forbidden in both envelopes.
for layer in ('root','article'):
    for flag in gate.FLAGS:
        def make(layer,flag):
            def check(self):
                self.reject(lambda b:(b if layer=='root' else
                    b['article_dossiers'][0]).update({flag:True}))
            return check
        setattr(Negative,'test_matrix_'+layer+'_'+flag,make(layer,flag))

if __name__=='__main__':unittest.main()

"""R454: synthetic claim-anchor drift tests; not clinical/editorial sign-off."""
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'tools'))
import r452_qa157_semantic_custody as custody
import r454_claim_anchor_integrity as gate

P = custody.PATHS
C1 = 'start-redcross-older-adults'
C2 = 'start-cdc-pyh-prescriptions'
CITE1 = '{{cite:'+C1+'}}'
CITE2 = '{{cite:'+C2+'}}'


def fixture():
    household = ('<h2>Practice</h2><p>Do not switch off the main breaker; smoke and '
                 'carbon monoxide alarms and medical systems need power '+CITE1+'</p>'
                 '<h2>Supplies</h2><p>Keep a contact list for the family '+CITE1+'</p>')
    medicine = ('<h2>Medicine</h2><p>Refrigerated medicine requires a pharmacist '
                'interim-use replacement plan '+CITE2+'</p>')
    sources = {'sources': [
        {'id':C1,'kind':'nonprofit','url':'https://example.org/old',
         'publisher':'American Red Cross','supports':'Original narrow scope'},
        {'id':C2,'kind':'agency','url':'https://example.gov/cdc',
         'publisher':'CDC','supports':'Product-specific advice'}]}
    slate = [{'slug':f'article-{i}', 'n':i, 'title':f'Article {i}', 'track':'modern',
              'section':'start-here', 'status':'drafted-pending-safety-review', 'gate':True}
             for i in range(35)]
    for i, critical in enumerate(sorted(custody.CRITICAL)):
        slate[i]['slug']=critical
    return {P[0]:household.encode(),P[1]:medicine.encode(),
            P[2]:json.dumps(sources).encode(),P[3]:json.dumps({'slate':slate}).encode()}


def call(qa=None, candidate=None):
    qa = fixture() if qa is None else qa
    candidate = dict(qa) if candidate is None else candidate
    return gate.anchored_review_packet(qa, candidate,
        [custody.git_blob(qa[k]) for k in P],
        [custody.git_blob(candidate[k]) for k in P])


def alter(qa, path, before, after):
    updated = dict(qa)
    updated[path] = updated[path].replace(before.encode(), after.encode())
    return updated


class AnchorTests(unittest.TestCase):
    def test_baseline_not_approved(self):
        result = call()
        self.assertEqual(result['release_state'], 'DRAFT_HARD_HOLD')
        self.assertFalse(result['qd_pass'])
        self.assertEqual(result['articles'][0]['source_ids_with_context_drift'],0)
    def test_equivalent_whitespace_not_retargeted(self):
        qa=fixture(); b=alter(qa,P[0],'Keep a contact list', 'Keep   a contact list')
        self.assertEqual(call(qa,b)['articles'][0]['source_ids_with_context_drift'],0)
    def test_retarget_same_citation_count_detected(self):
        qa=fixture(); b=alter(qa,P[0], 'Keep a contact list for the family',
                                          'Sleep near a running generator')
        r=call(qa,b)['articles'][0]
        self.assertEqual(r['citation_occurrences_before'],r['citation_occurrences_after'])
        self.assertEqual(r['source_ids_with_context_drift'],1)
        self.assertEqual(r['citation_anchor_changes_requiring_review'][0]['citation_count_before'],2)
    def test_heading_change_retargets(self):
        qa=fixture();b=alter(qa,P[0],'<h2>Supplies</h2>','<h2>Field guidance</h2>')
        self.assertEqual(call(qa,b)['articles'][0]['source_ids_with_context_drift'],1)
    def test_citation_removed_detected(self):
        qa=fixture(); b=alter(qa,P[0],'family '+CITE1,'family')
        self.assertEqual(call(qa,b)['articles'][0]['citation_occurrences_after'],1)
    def test_repeated_citations_retained(self):
        qa=fixture();b=alter(qa,P[0],CITE1+'</p>',CITE1+' '+CITE1+'</p>')
        self.assertEqual(call(qa,b)['articles'][0]['citation_occurrences_after'],4)
    def test_html_entities_normalize(self):
        self.assertEqual(gate.claim_units('<p>A &amp; B {{cite:test}}</p>')[0]['text_excerpt'],'A & B')
    def test_unsupported_outside_block_rejected(self):
        with self.assertRaises(custody.CustodyError):gate.claim_units('OUT {{cite:test}}<p>safe</p>')
    def test_hidden_citation_rejected(self):
        with self.assertRaises(custody.CustodyError):gate.claim_units('<script>{{cite:test}}</script>')
    def test_malformed_citation_rejected(self):
        with self.assertRaises(custody.CustodyError):gate.claim_units('<p>{{ cite:test }}</p>')
    def test_unclosed_paragraph_rejected(self):
        with self.assertRaises(custody.CustodyError):gate.claim_units('<p>{{cite:test}}')
    def test_excerpts_are_bounded(self):
        u=gate.claim_units('<p>'+('long '*200)+'{{cite:a}}</p>')[0]
        self.assertLessEqual(len(u['text_excerpt']),150)
    def test_nested_formatting_citation_captured(self):
        u=gate.claim_units('<p>Something <strong>important {{cite:a}}</strong></p>')[0]
        self.assertEqual(u['source_ids'], ['a'])
    def test_semantic_table_unit_captured(self):
        u=gate.claim_units('<table><tr><td>Safe detail {{cite:a}}</td></tr></table>')[0]
        self.assertEqual(u['kind'],'td')
    def test_nested_list_units_captured(self):
        u=gate.claim_units('<ul><li>one <p>two {{cite:a}}</p> three {{cite:b}}</li></ul>')
        self.assertEqual(sum(len(x['source_ids']) for x in u),2)
    def test_unpinned_real_mode_rejects_fixtures(self):
        with self.assertRaises(custody.CustodyError):gate.anchored_review_packet(fixture(),fixture())
    def test_url_reassignment_rejected(self):
        a=fixture();b=dict(a);sources=json.loads(b[P[2]]);sources['sources'][0]['url']='https://malicious.invalid'
        b[P[2]]=json.dumps(sources).encode()
        with self.assertRaises(custody.CustodyError):call(a,b)
    def test_safety_state_advance_rejected(self):
        a=fixture();b=dict(a);slate=json.loads(b[P[3]]);slate['slate'][0]['status']='published'
        b[P[3]]=json.dumps(slate).encode()
        with self.assertRaises(custody.CustodyError):call(a,b)
    def test_reading_scope_change_is_identified(self):
        a=fixture(); b=dict(a); s=json.loads(b[P[2]]); s['sources'][0]['supports']='New scope'
        b[P[2]]=json.dumps(s).encode()
        r=call(a,b)['articles'][0]['citation_anchor_changes_requiring_review']
        # No anchor movement with scope change; existing R453 separately flags changed scope.
        self.assertEqual(r,[])
    def test_source_scope_excluded_from_fragment_marked_unknown(self):
        qa=fixture();b=alter(qa,P[0],CITE1+'</p>',CITE1+' {{cite:from-main-register}}</p>')
        changed=call(qa,b)['articles'][0]['citation_anchor_changes_requiring_review']
        matches=[x for x in changed if x['source_id']=='from-main-register']
        self.assertEqual(matches[0]['documented_source_scope']['status'],
                         'NOT_IN_START_FRAGMENT_REQUIRES_FULL_REGISTER_LOOKUP')
    def test_no_write_functions(self):
        import inspect
        source=inspect.getsource(gate)
        self.assertNotIn('write_text(',source)
        self.assertNotIn('unlink(',source)


def generate(i):
    def test(self):
        qa=fixture()
        # Adversarial same-count edits across two different textual contexts.
        phrase='Keep a contact list for the family'
        replacement='Claim variation '+str(i)+' with different source context'
        b=alter(qa,P[0],phrase,replacement)
        r=call(qa,b)
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
        self.assertFalse(r['qd_pass'])
        self.assertEqual(r['articles'][0]['citation_occurrences_before'],2)
        self.assertEqual(r['articles'][0]['citation_occurrences_after'],2)
        drift=r['articles'][0]['citation_anchor_changes_requiring_review']
        self.assertEqual(len(drift),1)
        self.assertEqual(drift[0]['source_id'],C1)
        self.assertEqual(len(drift[0]['removed_contexts']),1)
        self.assertEqual(len(drift[0]['added_contexts']),1)
    test.__name__=f'test_same_count_retarget_{i:02}'
    return test

for i in range(1,53):
    setattr(AnchorTests,f'test_same_count_retarget_{i:02}',generate(i))

if __name__=='__main__':unittest.main()

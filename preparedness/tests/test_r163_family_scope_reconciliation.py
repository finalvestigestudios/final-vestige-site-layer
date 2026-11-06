"""Synthetic tests: no independent source or safety approvals are simulated as real."""
import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'tools/r163_family_scope_reconciliation.py'
spec = importlib.util.spec_from_file_location('r163', MODULE)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def fixture():
    names = sorted(M.EXPECTED_BLOCKED | M.EXPECTED_SUPPORT | set(M.EXPECTED_SCOPE))
    obs = []
    for sid in names:
        if sid in M.EXPECTED_SCOPE:
            scope, access = M.EXPECTED_SCOPE[sid], 'RETRIEVED_TEXT'
        elif sid in M.EXPECTED_BLOCKED:
            scope, access = 'NOT_OBSERVABLE', 'RETRIEVAL_BLOCKED'
        else:
            scope, access = 'CLAIM_MATCH_OBSERVED', 'RETRIEVED_TEXT'
        obs.append({'source_id':sid, 'source_url':'https://example.org/'+sid,
                    'access':access,'scope':scope,'observation':'Current automated observation only; qualified human source review still pending.',
                    'review_state':'PENDING','human_link_checked':False,'qualified_safety_review':False})
    record = {'schema':'fv-preparedness-r155-family-source-observation-v1',
              'tool':'family-reunification-card','observations':obs,
              'independent_review':False,'source_approval':False,
              'publication_authorized':False,'commercial_offer_verified':False}
    meta = {'kind':'tool','slug':'family-reunification-card','status':{'publish':'draft'},
            'safety_review':{'state':'pending'}, 'source_use':{sid:'Author-specific claim not reviewed.' for sid in names}}
    html = '<section><p>' + M.CHANGES[0][0] + '{{cite:shelter-ready-tech}}{{cite:shelter-fcc-comms}}</p>'
    html += '<p>' + M.CHANGES[1][0] + '{{cite:shelter-ncmec-hotline}}{{cite:shelter-cdc-reunification}}'
    html += M.CHANGES[2][0] + '{{cite:shelter-fema-reunification}}</p>'
    for sid in names:
        html += '<p>Supporting context {{cite:'+sid+'}}</p>'
    html += '<script>console.log("unchanged");</script></section>'
    assert len(M.CITES.findall(html)) == 16
    return html, meta, record


class Reconciliation(unittest.TestCase):
    def test_draft_receipt(self):
        html,meta,obs=fixture()
        edited,report=M.propose(html,meta,obs)
        self.assertEqual(report['state'],'DRAFT_HARD_HOLD')
        self.assertFalse(report['publication_authorized'])
        self.assertEqual(report['citations_preserved'],16)
        self.assertEqual(M.CITES.findall(html),M.CITES.findall(edited))
        self.assertEqual(M.BLOCKS.findall(html),M.BLOCKS.findall(edited))
        self.assertEqual(M.TAGS.findall(html),M.TAGS.findall(edited))

    def test_deterministic(self):
        args=fixture()
        self.assertEqual(M.propose(*args),M.propose(*args))

    def test_each_old_claim_removed(self):
        out,_=M.propose(*fixture())
        for old,_ in M.CHANGES:self.assertNotIn(old,out)

    def test_missing_correction_anchor_rejected(self):
        html,meta,rec=fixture()
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            M.propose(html.replace(M.CHANGES[1][0],'removed'),meta,rec)

    def test_duplicate_correction_anchor_rejected(self):
        html,meta,rec=fixture()
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            M.propose(html+M.CHANGES[0][0],meta,rec)

    def test_fake_approval_rejected(self):
        for key in ('independent_review','source_approval','publication_authorized','commercial_offer_verified'):
            html,meta,rec=fixture()
            rec[key]=True
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'forged approval'):
                M.propose(html,meta,rec)

    def test_forged_public_state_rejected(self):
        for state in ('published','live','public','pending'):
            html,meta,rec=fixture()
            meta['status']['publish']=state
            with self.subTest(state=state),self.assertRaisesRegex(ValueError,'hold violated'):
                M.propose(html,meta,rec)

    def test_mutate_each_evidence_record_rejected(self):
        for sid in sorted(M.EXPECTED_BLOCKED|M.EXPECTED_SUPPORT|set(M.EXPECTED_SCOPE)):
            html,meta,rec=fixture()
            next(x for x in rec['observations'] if x['source_id']==sid)['scope']='CLAIM_APPROVED'
            with self.subTest(sid=sid),self.assertRaisesRegex(ValueError,'reclassified|changed'):
                M.propose(html,meta,rec)

    def test_source_review_states_rejected(self):
        for sid in sorted(M.EXPECTED_BLOCKED|M.EXPECTED_SUPPORT|set(M.EXPECTED_SCOPE)):
            html,meta,rec=fixture()
            next(x for x in rec['observations'] if x['source_id']==sid)['review_state']='APPROVED'
            with self.subTest(sid=sid),self.assertRaisesRegex(ValueError,'forged'):
                M.propose(html,meta,rec)

    def test_source_uses_removal_rejected(self):
        for sid in sorted(M.EXPECTED_BLOCKED|M.EXPECTED_SUPPORT|set(M.EXPECTED_SCOPE)):
            html,meta,rec=fixture()
            del meta['source_use'][sid]
            with self.subTest(sid=sid),self.assertRaisesRegex(ValueError,'interpretations'):
                M.propose(html,meta,rec)

    def test_url_restrictions(self):
        for replacement in ('http://example.org/plain','javascript:alert(1)','https://x.org/a?x=1','https://x.org/#frag'):
            html,meta,rec=fixture()
            rec['observations'][0]['source_url']=replacement
            with self.subTest(replacement=replacement),self.assertRaisesRegex(ValueError,'URL'):
                M.propose(html,meta,rec)

    def test_duplicate_source_rejected(self):
        html,meta,rec=fixture()
        rec['observations'][0]['source_id']=rec['observations'][1]['source_id']
        with self.assertRaisesRegex(ValueError,'duplicate'):
            M.propose(html,meta,rec)

    def test_citation_swap_rejected(self):
        html,meta,rec=fixture()
        html=html.replace('{{cite:shelter-fema-reunification}}','{{cite:forged-src}}',1)
        with self.assertRaisesRegex(ValueError,'occurrence census'):
            M.propose(html,meta,rec)

    def test_extra_citation_rejected(self):
        html,meta,rec=fixture()
        with self.assertRaisesRegex(ValueError,'occurrence census'):
            M.propose(html+'{{cite:shelter-ready-tech}}',meta,rec)

    def test_missing_tool_review_rejected(self):
        html,meta,rec=fixture()
        rec['tool']='unrelated'
        with self.assertRaisesRegex(ValueError,'wrong reviewed tool'):
            M.propose(html,meta,rec)

    def test_safety_state_rejected(self):
        html,meta,rec=fixture()
        meta['safety_review']['state']='approved'
        with self.assertRaisesRegex(ValueError,'hold violated'):
            M.propose(html,meta,rec)

    def test_no_side_effects(self):
        args=fixture()
        freeze=deepcopy(args)
        M.propose(*args)
        self.assertEqual(args,freeze)


def build_mutation(n):
    def mutation(self):
        html,meta,rec=fixture()
        if n < 11:
            rec['observations'][n]['human_link_checked']=True
        elif n < 22:
            rec['observations'][n-11]['qualified_safety_review']=True
        elif n < 33:
            rec['observations'][n-22]['source_url']='http://untrusted.example/path'
        elif n < 44:
            del rec['observations'][n-33]
        with self.assertRaises(ValueError):
            M.propose(html,meta,rec)
    return mutation


for i in range(44):
    setattr(Reconciliation,'test_adversarial_%02d'%i,build_mutation(i))


if __name__=='__main__':unittest.main()

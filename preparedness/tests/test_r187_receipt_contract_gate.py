"""Synthetic regression/adversarial contracts; never real-source or QD approval."""
import copy
import unittest
from pathlib import Path
from importlib import util

MODULE = Path(__file__).resolve().parents[1] / "tools/r187_receipt_contract_gate.py"
if not MODULE.is_file():  # Local synthetic harness lives alongside its helper.
    MODULE = Path(__file__).resolve().with_name("r187_receipt_contract_gate.py")
spec = util.spec_from_file_location("fv_r187_receipt_contract", MODULE)
if spec is None or spec.loader is None:
    raise ImportError("R187 helper cannot be loaded")
gate = util.module_from_spec(spec)
spec.loader.exec_module(gate)


def good(label):
    v = {'state': gate.HOLD}
    if gate.SCHEMAS[label] is not None:
        v['schema'] = gate.SCHEMAS[label]
    v.update({key: False for key in gate.REQUIRED_FALSE[label]})
    v.update(gate.COUNTS[label])
    if label == 'r177':
        v['files'] = [dict(slug=slug, stage=stage, structural_status='REVIEW_HOLD')
                      for slug in ('household-emergency-plan', 'three-day-kit')
                      for stage in ('source', 'wordpress_draft')]
    if label == 'r178':
        v['legacy_approved_unverified'] = ['making-water-safer','salt-beef-salt-pork-age-of-sail']
        v['not_required_editorial_hold'] = [
            'navigation-before-gps','pioneer-supply-chains-failed',
            'root-cellars-cool-storage','sanitation-before-germ-theory']
    if label == 'r182':
        v['qa_prs'] = dict(gate.QA_HEADS)
        v['content_custody_sha256'] = 'a'*64
    return v


class StrictContracts(unittest.TestCase):
    def test_nine_contracts(self):
        self.assertEqual(len(gate.SCHEMAS), 9)
        self.assertEqual(set(gate.SCHEMAS), set(gate.REQUIRED_FALSE))
        self.assertEqual(set(gate.SCHEMAS), set(gate.COUNTS))

    def test_unknown_gate(self):
        with self.assertRaisesRegex(ValueError, 'unknown'):
            gate.verify_contract('r999', {'state':gate.HOLD})

    def test_nested_fake_approval(self):
        d = good('r185'); d['wrapper']=[{'source_claims_independently_adjudicated':True}]
        with self.assertRaisesRegex(ValueError,'explicit false'):
            gate.verify_contract('r185', d)

    def test_wrong_qa_head(self):
        d=good('r182');d['qa_prs']['973']='b'*40
        with self.assertRaisesRegex(ValueError,'unpinned'):
            gate.verify_contract('r182',d)

    def test_forged_r177_article(self):
        d=good('r177');d['files'][0]['slug']='another-article'
        with self.assertRaisesRegex(ValueError,'four safety'):
            gate.verify_contract('r177',d)


def create_mutations():
    for label in gate.SCHEMAS:
        for variant in ('valid','schema','state','missing_hold','positive_hold',
                        'missing_count','wrong_typed_count','nested_clearance'):
            def test(self, label=label, variant=variant):
                d=good(label)
                if variant=='schema': d['schema']='different-schema'
                elif variant=='state': d['state']='INVALID_HARD_HOLD'
                elif variant=='missing_hold': d.pop(gate.REQUIRED_FALSE[label][0])
                elif variant=='positive_hold': d[gate.REQUIRED_FALSE[label][0]]=True
                elif variant=='missing_count':
                    if gate.COUNTS[label]: d.pop(next(iter(gate.COUNTS[label])))
                    else: d['qa_prs'].pop('157')
                elif variant=='wrong_typed_count':
                    if gate.COUNTS[label]:
                        k=next(iter(gate.COUNTS[label]));d[k]=str(d[k])
                    else: d['content_custody_sha256']='not-a-digest'
                elif variant=='nested_clearance':
                    d['extra']={'merchant_offer_verified':True}
                if variant=='valid': gate.verify_contract(label,d)
                else:
                    with self.assertRaises(ValueError):gate.verify_contract(label,d)
            setattr(StrictContracts, f'test_{label}_{variant}', test)
create_mutations()

if __name__=='__main__':unittest.main()

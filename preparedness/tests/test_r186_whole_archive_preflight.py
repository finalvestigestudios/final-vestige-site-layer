"""R186 isolated synthetic verifier tests; never source, QD or revenue approval."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'tools/r186_whole_archive_preflight.py'
spec = importlib.util.spec_from_file_location('r186_whole_archive_preflight', MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def good(label):
    row = {'state': gate.HOLD, 'errors': [], 'publication_authorized': False,
           'independent_qd_pass': False, 'commercial_offer_verified': False}
    row.update({
        'r174': dict(article_count=35, rendered_citations=2000,
                     rendered_source_uses=385, draft_export_bytes_checked=True),
        'r175': dict(articles=35, export_compared=True),
        'r177': dict(review_only=True, errors_count=0),
        'r178': dict(article_count=35, citations=2000, source_use=385),
        'r179': dict(article_count=35, citation_occurrences=2000),
        'r180': dict(review_tickets_pending=21, family_source_decisions_pending=11,
                     jerky_claim_decisions_pending=10),
        'r182': {'qa_prs': {'157': 'abc', '169': 'abc', '973': 'abc'},
                 'independent_qa_prs_merge_authorized': False},
        'r184': dict(articles_checked=35, citation_occurrences_checked=2000),
        'r185': dict(tool_count=6, source_rows=67, citation_occurrences=173),
    }[label])
    return {'returncode': 2, 'stdout': json.dumps(row), 'stderr': ''}


def corpus(root, missing=None):
    prep = root / 'preparedness'
    inventory = {}
    for folder, names in [('articles', [f'article-{i:02}' for i in range(35)]),
                          ('tools', sorted(gate.TOOLS))]:
        (prep/'content'/folder).mkdir(parents=True, exist_ok=True)
        for slug in names:
            for ext in ('meta.json', 'body.html'):
                p = prep/'content'/folder/(slug+'.'+ext)
                if (folder,slug,ext)==missing: continue
                if ext == 'meta.json':
                    p.write_text(json.dumps({'slug':slug,'status':{'publish':'draft'},
                    'section': 'field-tools' if folder=='tools' else 'start-here'}))
                else: p.write_text('<p>original draft</p>')
                inventory[p.relative_to(prep).as_posix()] = 'sha'
    return prep,inventory


class PipelineSafety(unittest.TestCase):
    def test_production_gate_count(self):
        self.assertEqual(len(gate.GATES), 9)
        self.assertEqual(len({x[0] for x in gate.GATES}), 9)

    def test_all_synthetic_gates_remain_structural_holds(self):
        for label,*_ in gate.GATES:
            with self.subTest(label=label):
                self.assertEqual(gate.verify_gate(label,good(label))['status'],'STRUCTURAL_HOLD')

    def test_synthetic_full_census(self):
        with tempfile.TemporaryDirectory() as temp:
            prep,items=corpus(Path(temp))
            self.assertEqual(gate.check_census(prep,items),
                             {'articles':35, 'tools':6,'distinct_draft_canonicals':41,'published':0})

    def test_missing_tool_original_body(self):
        with tempfile.TemporaryDirectory() as temp:
            prep,items=corpus(Path(temp), ('tools','family-reunification-card','body.html'))
            with self.assertRaisesRegex(ValueError,'missing/duplicate'):
                gate.check_census(prep,items)

    def test_missing_article_source_body(self):
        with tempfile.TemporaryDirectory() as temp:
            prep,items=corpus(Path(temp), ('articles','article-01','body.html'))
            with self.assertRaisesRegex(ValueError,'missing/duplicate'):
                gate.check_census(prep,items)

    def test_changed_source_meta(self):
        with tempfile.TemporaryDirectory() as temp:
            prep,items=corpus(Path(temp))
            p=prep/'content/tools/kit-builder.meta.json';j=json.loads(p.read_text());j['status']['publish']='published';p.write_text(json.dumps(j))
            with self.assertRaisesRegex(ValueError,'non-draft'):
                gate.check_census(prep,items)

    def test_missing_qa_pr_custody(self):
        row=good('r182');x=json.loads(row['stdout']);x['qa_prs'].pop('169');row['stdout']=json.dumps(x)
        self.assertEqual(gate.verify_gate('r182',row)['status'],'FAIL')

    def test_missing_human_tickets(self):
        row=good('r180');x=json.loads(row['stdout']);x.pop('review_tickets_pending');row['stdout']=json.dumps(x)
        self.assertEqual(gate.verify_gate('r180',row)['status'],'FAIL')

    def test_unknown_gate_is_rejected(self):
        self.assertEqual(gate.verify_gate('new_optional',good('r185'))['status'],'FAIL')

    def test_recursively_false_flags(self):
        with self.assertRaisesRegex(ValueError,'publication_authorized'):
            gate.safe_false({'nested':[{'publication_authorized': True}]})

    def test_exit_two_ambiguous_but_packet_state_required(self):
        for label,*_ in gate.GATES:
            row=good(label);row['stdout']=json.dumps({'state':gate.INVALID,'errors':[]})
            self.assertEqual(gate.verify_gate(label,row)['status'],'FAIL')


def make_mutation_tests():
    for label,*_ in gate.GATES:
        for variant in ('exit_zero','exit_one','missing_json','false_state','smuggled_qd',
                        'positive_sale','reported_error','wrong_type'):
            def test(self, label=label, variant=variant):
                row=good(label)
                if variant == 'exit_zero': row['returncode']=0
                elif variant == 'exit_one': row['returncode']=1
                elif variant == 'missing_json': row['stdout']='not json'
                else:
                    document=json.loads(row['stdout'])
                    if variant == 'false_state': document['state']=gate.INVALID
                    if variant == 'smuggled_qd': document['independent_qd_pass']=True
                    if variant == 'positive_sale': document['nested']={'commercial_offer_verified':True}
                    if variant == 'reported_error': document['errors']=['source missing']
                    if variant == 'wrong_type': document['state']=['DRAFT_HARD_HOLD']
                    row['stdout']=json.dumps(document)
                self.assertEqual(gate.verify_gate(label,row)['status'],'FAIL')
            setattr(PipelineSafety,f'test_{label}_{variant}',test)
make_mutation_tests()

if __name__ == '__main__':
    unittest.main()

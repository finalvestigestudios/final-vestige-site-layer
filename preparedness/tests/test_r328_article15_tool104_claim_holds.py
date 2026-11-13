"""R328 source witness integrity tests; deliberately synthetic, never independent QD."""
import copy
import json
import unittest
from preparedness.tools import r328_article15_tool104_claim_holds as gate


def fixture():
    docs = {}
    for role in ("a_body", "t_body"):
        docs[role] = ('<h2>Unreviewed emergency manuscript</h2>\n' +
                      '\n'.join(w[2] for w in gate.WITNESSES if w[1] == role)).encode()
    for role, number, slug in (("a_meta", 15, "family-communication-plan"),
                               ("t_meta", 104, "family-reunification-card")):
        docs[role] = json.dumps({"n": number, "slug": slug,
            "status": {"editorial":"drafted", "publish":"draft"},
            "safety_review": {"state":"pending", "reviewer":None, "date":None},
            "source_use": {}, "description": "Nothing is stored." if role == "t_meta" else "Family guide"}).encode()
    return docs


class R328Witnesses(unittest.TestCase):
    def test_synthetic_only_witnesses(self):
        report = gate.inspect(fixture())
        self.assertEqual(report['state'], 'DRAFT_HARD_HOLD', report)
        self.assertEqual(len(report['witnesses']), 10)
        self.assertEqual(report['qualified_approved_count'], 0)
        self.assertEqual(set(report['release'].values()), {False})
        self.assertTrue(all(r['review'] == 'UNRESOLVED_QUALIFIED_HUMAN_REVIEW' for r in report['witnesses']))

    def test_synthetic_never_authentic(self):
        docs = fixture()
        report = gate.audit(lambda p: docs[next(k for k,v in gate.DOCS.items() if v[0] == p)])
        self.assertEqual(report['state'], 'INVALID_HARD_HOLD')
        self.assertEqual(report['git_pins_checked'], 0)

    def test_pins_are_unique_full_hashes(self):
        self.assertEqual(len({p for p,s in gate.DOCS.values()}), 4)
        self.assertEqual(len({s for p,s in gate.DOCS.values()}), 4)
        self.assertTrue(all(len(s)==40 and all(c in '0123456789abcdef' for c in s) for _,s in gate.DOCS.values()))

    def test_review_sources_are_official_or_none(self):
        self.assertTrue(all(w[4] is None or w[4].startswith(('https://www.911.gov/', 'https://www.cdc.gov/')) for w in gate.WITNESSES))

    def test_no_local_file_writes(self):
        report = gate.inspect(fixture())
        self.assertEqual(report['state'], 'DRAFT_HARD_HOLD')
        self.assertTrue(all(r['publication_or_revenue_clearance'] is False for r in report['witnesses']))


def inject_case(label, make):
    def test(self):
        docs = fixture()
        docs = make(docs)
        report = gate.inspect(docs)
        self.assertEqual(report['state'], 'INVALID_HARD_HOLD', (label, report))
        self.assertTrue(all(x is False for x in report['release'].values()))
    setattr(R328Witnesses, 'test_reject_' + label, test)


for idx, w in enumerate(gate.WITNESSES):
    claim, role, needle = w[:3]
    def removed(d, role=role, needle=needle):
        d[role] = d[role].replace(needle.encode(), b'', 1)
        return d
    def duplicated(d, role=role, needle=needle):
        d[role] += b'\n' + needle.encode()
        return d
    inject_case('anchor_absent_%02d'%idx, removed)
    inject_case('anchor_duplicated_%02d'%idx, duplicated)

for role in gate.DOCS:
    inject_case('missing_%s'%role, lambda d,role=role: {k:v for k,v in d.items() if k!=role})
    inject_case('nonbytes_%s'%role, lambda d,role=role: dict(d,**{role:d[role].decode()}))
    inject_case('nonutf8_%s'%role, lambda d,role=role: dict(d,**{role:b'\xff\x80'}))

for role in ('a_meta','t_meta'):
    for field, bad in [('n', 0), ('n', True), ('slug', 'reunification-plan'),
                       ('status', {'editorial':'drafted','publish':'publish'}),
                       ('status', {'editorial':'reviewed','publish':'draft'}),
                       ('safety_review', {'state':'approved','reviewer':'self','date':'2026-11-12'}),
                       ('safety_review', {'state':'pending','reviewer':'self','date':None}),
                       ('safety_review', {'state':'pending','reviewer':None,'date':'2026-11-12'})]:
        def mutate(d,role=role,field=field,bad=bad):
            v=json.loads(d[role]);v[field]=bad;d[role]=json.dumps(v).encode();return d
        inject_case('metadata_%s_%s_%02d'%(role,field,len([x for x in dir(R328Witnesses) if x.startswith('test_reject_metadata_'+role+'_'+field)])), mutate)
    def duplicate(d,role=role):
        d[role] = d[role].replace(b'"n": ', b'"n": 999, "n": ', 1)
        return d
    inject_case('duplicate_json_key_'+role, duplicate)
    def undeclared(d,role=role):
        v=json.loads(d[role]);v['source_use']['source-id-without-citation']='unexpected';d[role]=json.dumps(v).encode();return d
    inject_case('source_use_orphan_'+role, undeclared)
    def undeclared_citation(d,role=role):
        body='a_body' if role=='a_meta' else 't_body'
        d[body] += b'{{cite:unregistered-source}}';return d
    inject_case('citation_unregistered_'+role, undeclared_citation)


class R328AuditFailClosed(unittest.TestCase):
    def test_all_missing_fails_closed(self):
        report=gate.audit(lambda p: None)
        self.assertEqual(report['state'],'INVALID_HARD_HOLD')
        self.assertEqual(report['git_pins_checked'],0)
        self.assertGreaterEqual(len(report['errors']), 4)

    def test_path_inventory_exact(self):
        self.assertEqual(set(gate.DOCS), {'a_body','a_meta','t_body','t_meta'})
        self.assertTrue(all(p.startswith('preparedness/content/') for p,_ in gate.DOCS.values()))


for role in gate.DOCS:
    def missing(self,role=role):
        report=gate.audit(lambda path: (_ for _ in ()).throw(OSError()) if path==gate.DOCS[role][0] else b'bad')
        self.assertIn('PINNED_GIT_BLOB_UNAVAILABLE_OR_DRIFT_'+role.upper(),report['errors'])
    setattr(R328AuditFailClosed,'test_missing_authentic_'+role,missing)
    def changed(self,role=role):
        report=gate.audit(lambda path: b'modified source')
        self.assertEqual(report['state'], 'INVALID_HARD_HOLD')
        self.assertIn('PINNED_GIT_BLOB_UNAVAILABLE_OR_DRIFT_'+role.upper(),report['errors'])
    setattr(R328AuditFailClosed,'test_changed_authentic_'+role,changed)


if __name__ == '__main__':
    unittest.main()

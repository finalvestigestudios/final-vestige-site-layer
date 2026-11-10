"""R258 isolated synthetic tests ONLY: do not imply original source or safety approval."""
import copy
import importlib.util
from pathlib import Path
import re
import unittest

SRC = Path(__file__).resolve().parents[1] / 'tools/r258_complete_offline_claim_review_hold.py'
spec = importlib.util.spec_from_file_location('r258', SRC)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def build_fixture():
    positions = [(n, j) for n in range(1, 36)
                 for j in range(1, 63 if n == 35 else 58)]
    chosen = set(positions[:561])
    chosen.discard((7, 30)); chosen.discard((7, 48))
    # 561 desired shared records excluding two CDC disputes; guarantee Ready 20:55.
    chosen = set(p for p in positions if p not in ((7, 30), (7, 48), (20, 55)))
    chosen = set(sorted(chosen)[:561]); chosen.add((20, 55))
    assert len(positions) == 2000 and len(chosen) == 562
    ids = ['start-ready-plan'] + [f'shared-{i}' for i in range(55)]
    groups = [{'source_url': f'https://evidence.example/item-{i}',
               'source_ids': [], 'workorders': [], 'workorder_count': 0,
               'state': 'PENDING_HUMAN_SOURCE_AND_CLAIM_REVIEW',
               'source_scope_approved': False, 'claim_support_approved': False}
              for i in range(32)]
    for i, sid in enumerate(ids):
        groups[i // 2 if i < 48 else i - 24]['source_ids'].append(sid)
    match_id = {k: ids[i % 56] for i, k in enumerate(sorted(chosen))}
    match_id[20, 55] = 'start-ready-plan'
    other, ext = [], []
    for n, o in positions:
        is_shared = (n,o) in chosen
        sid = match_id[(n,o)] if is_shared else 'other-source-'+str(n)
        if (n,o) in ((7,30),(7,48)):
            sid = 'cdc-find-clean-water'
        excerpt = f'UNREVIEWED original example article={n} citation={o}.'
        entry = {'article_n':n,'article_slug':f'original-{n}',
                 'citation_ordinal':o,'source_id':sid,
                 'authored_context_excerpt':excerpt,
                 'context_sha256':r.sha(excerpt),
                 'author_source_use_note_sha256':r.sha('author '+sid),
                 'source_support_verified':False,'safety_approved':False}
        if is_shared:
            row = {**entry, 'review_terms':['requires_review'],
                   'disputed_original_citation':(n,o,sid) in r.DISPUTES}
            g = next(g for g in groups if sid in g['source_ids'])
            g['workorders'].append(row)
        else:
            row = {**entry, 'risk_terms':['requires_review'],
                   'original_dispute':(n,o,sid) in r.DISPUTES}
            other.append(row)
            if (n,o) in ((7,30),(7,48)):
                ext.append({**entry,'review_terms':['requires_review'],
                            'disputed_original_citation':True})
    for g in groups:
        g['workorders'].sort(key=lambda x:(x['article_n'],x['citation_ordinal']))
        g['workorder_count']=len(g['workorders'])
    work = {'schema':r.R254,'state':r.HOLD, 'article_count':35,
            'citation_count':2000,'source_review_groups':32,
            'shared_source_ids':56,'human_readable_workorders':562,
            'other_citation_occurrences_still_unreviewed':1438,
            'disputed_original_claims':3,'shared_disputed_claims':1,
            'outside_shared_disputed_claims':2,
            'outside_shared_disputed_workorders':ext,'review_queue':groups,
            **{flag:False for flag in r.FALSE}}
    part = {'schema':r.R257,'state':r.HOLD,'article_count':35,
            'citation_count':2000,'shared_workorders':562,
            'nonshared_workorders':1438,
            'total_unapproved_citation_occurrences':2000,
            'shared_disputes':1,'nonshared_disputes':2,
            'unreviewed_nonshared_queue':other,
            **{flag:False for flag in r.FALSE}}
    reseal(work); reseal(part)
    return work,part


def reseal(d):
    d['receipt_sha256'] = r.sha(r.encode({k:v for k,v in d.items() if k!='receipt_sha256'}))


BASE=build_fixture()


class TestR258(unittest.TestCase):
    def test_all_citations_rendered_and_accessible(self):
        a=r.render_full_review(*BASE)
        self.assertEqual((a['article_count'],a['citation_occurrences'],a['shared'],a['other']),(35,2000,562,1438))
        h=a['offline_review_html']
        self.assertEqual(h.count('<li id="cite-'),2000)
        self.assertEqual(h.count('<article id="article-'),35)
        self.assertEqual(h.count('UNREVIEWED SHARED citation '),562)
        self.assertEqual(h.count('UNREVIEWED OTHER citation '),1438)
        self.assertEqual(h.count('DISPUTED / HUMAN ADJUDICATION REQUIRED'),3)
        self.assertTrue(h.startswith('<!doctype html>'))
        self.assertNotIn('<a ',h)
        self.assertNotIn('<script',h)
        self.assertIn('Content-Security-Policy',h)
        self.assertEqual(a['offline_review_sha256'],r.sha(h))
        self.assertGreater(a['offline_review_utf8_bytes'],150000)

    def test_deterministic_no_mutation(self):
        base=copy.deepcopy(BASE)
        self.assertEqual(r.render_full_review(*BASE),r.render_full_review(*BASE))
        self.assertEqual(BASE,base)

    def test_html_escaped_untrusted_context_url_and_source(self):
        w,p=copy.deepcopy(BASE)
        x=w['review_queue'][0]['workorders'][0]
        x['authored_context_excerpt']='<img src=x onerror=alert(1)><script>bad</script> & "hi"'
        x['context_sha256']=r.sha(x['authored_context_excerpt'])
        w['review_queue'][0]['source_url']='https://evidence.example/?x=<iframe src=x>'
        reseal(w)
        h=r.render_full_review(w,p)['offline_review_html']
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;',h)
        self.assertIn('&lt;script&gt;bad&lt;/script&gt;',h)
        self.assertIn('&lt;iframe src=x&gt;',h)
        self.assertNotIn('<img ',h)
        self.assertNotIn('<iframe ',h)

    def test_no_trusted_approval_from_render(self):
        a=r.render_full_review(*BASE)
        for k in r.FALSE:
            self.assertIs(a[k],False)
        self.assertIs(a['review_approval'],False)


def mutant(name, change, reseal_work=True, reseal_part=True):
    def case(self):
        w,p=copy.deepcopy(BASE)
        change(w,p)
        if reseal_work:reseal(w)
        if reseal_part:reseal(p)
        with self.assertRaisesRegex((ValueError,KeyError,TypeError),'R258 DRAFT HARD HOLD'):
            r.render_full_review(w,p)
    setattr(TestR258,'test_mutation_'+name,case)

for src in ('work','part'):
    for fld,value in [('schema','OTHER'),('state','PASS'),('article_count',34),('citation_count',1999)]:
        mutant(src+'_'+fld,lambda w,p,s=src,f=fld,v=value:(w if s=='work' else p).__setitem__(f,v))
    for flag in r.FALSE:
        mutant(src+'_approved_'+flag,lambda w,p,s=src,f=flag:(w if s=='work' else p).__setitem__(f,True))
mutant('receipt_work',lambda w,p:w.__setitem__('receipt_sha256','0'*64),False)
mutant('receipt_part',lambda w,p:p.__setitem__('receipt_sha256','0'*64),True,False)
for fld,val in [('source_review_groups',31),('shared_source_ids',55),
                ('human_readable_workorders',561),('other_citation_occurrences_still_unreviewed',1439),
                ('disputed_original_claims',2),('shared_disputed_claims',2),
                ('outside_shared_disputed_claims',1)]:
    mutant('work_'+fld,lambda w,p,f=fld,v=val:w.__setitem__(f,v))
for fld,val in [('shared_workorders',563),('nonshared_workorders',1437),
                ('total_unapproved_citation_occurrences',1999),
                ('shared_disputes',2),('nonshared_disputes',1)]:
    mutant('part_'+fld,lambda w,p,f=fld,v=val:p.__setitem__(f,v))
for fld,val in [('state','APPROVED'),('source_scope_approved',True),
                ('claim_support_approved',True),('workorder_count',0),
                ('source_url','javascript:alert(1)'),('source_ids',['shared-1'])]:
    mutant('group_'+fld,lambda w,p,f=fld,v=val:w['review_queue'][0].__setitem__(f,v))
for fld,val in [('article_n',40),('citation_ordinal',0),('article_slug','Bad/Slug'),
                ('source_id','not-same'),('authored_context_excerpt','changed'),
                ('context_sha256','not-a-hash'),('author_source_use_note_sha256','0'),
                ('review_terms',['x','x']),('disputed_original_citation',True),
                ('source_support_verified',True),('safety_approved',True)]:
    mutant('shared_row_'+fld,lambda w,p,f=fld,v=val:w['review_queue'][0]['workorders'][0].__setitem__(f,v))
for fld,val in [('article_n',0),('citation_ordinal',0),('article_slug','bad slug'),
                ('source_id','Bad-id'),('authored_context_excerpt','<img>'),
                ('context_sha256','bad'),('author_source_use_note_sha256','bad'),
                ('risk_terms',['dup','dup']),('original_dispute',False),
                ('source_support_verified',True),('safety_approved',True)]:
    mutant('other_row_'+fld,lambda w,p,f=fld,v=val:p['unreviewed_nonshared_queue'][0].__setitem__(f,v))
mutant('duplicate_source_group_url',lambda w,p:w['review_queue'][1].__setitem__('source_url',w['review_queue'][0]['source_url']))
mutant('duplicate_source_id_group',lambda w,p:w['review_queue'][1]['source_ids'].append(w['review_queue'][0]['source_ids'][0]))
mutant('citation_group_mismatch',lambda w,p:w['review_queue'][0]['workorders'][0].__setitem__('source_id','shared-20'))
mutant('reassign_unmatched_to_shared_id',lambda w,p:p['unreviewed_nonshared_queue'][0].__setitem__('source_id','shared-1'))
mutant('missing_complement',lambda w,p:p['unreviewed_nonshared_queue'].pop())
mutant('duplicate_complement',lambda w,p:p['unreviewed_nonshared_queue'].append(copy.deepcopy(p['unreviewed_nonshared_queue'][-1])))
mutant('missing_shared',lambda w,p:w['review_queue'][0]['workorders'].pop())
mutant('reorder_complement',lambda w,p:p['unreviewed_nonshared_queue'].reverse())
mutant('missing_cdc_exception',lambda w,p:w['outside_shared_disputed_workorders'].pop())
mutant('corrupt_cdc_exception',lambda w,p:w['outside_shared_disputed_workorders'][0].__setitem__('authored_context_excerpt','changed'))
mutant('reclassify_article20_dispute',lambda w,p:w['review_queue'][0]['workorders'][0].__setitem__('disputed_original_citation',True))

if __name__=='__main__': unittest.main()

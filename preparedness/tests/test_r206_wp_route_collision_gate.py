"""Synthetic route-ownership, CMS snapshot, and publication-hold regressions."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1]/'tools/r206_wp_route_collision_gate.py'
spec=importlib.util.spec_from_file_location('r206',SOURCE)
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)


def sample():
    heads={f'cluster-{i}':str(i)*40 for i in range(1,8)}
    articles=[]
    for n in range(1,36):
        slug=f'article-{n}';section='start-here' if n<21 else 'historical-field'
        owner=f'cluster-{1+(n-1)%7}'
        articles.append({'n':n,'slug':slug,'section':section,
            'source_cluster':owner,'branch_sha':heads[owner],
            'route':f'/preparedness/{section}/{slug}/',
            'body_oid':'a'*40,'meta_oid':'b'*40})
    man={'schema':'fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1',
        'issue':136,'conversion_issue':820,'state':gate.HOLD,
        'publication_authorized':False,'independent_qd_pass':False,
        'artifact_count':35,'export_target_count_with_six_tools':41,
        'articles':articles,'branch_heads':heads}
    def page(id,slug,status,parent,link):
        return {'id':id,'slug':slug,'status':status,'parent':parent,
            'link':link,'modified':'2026-11-07T17:32:01','title':slug}
    snapshot={'site':'https://finalvestige.com','captured_at':'2026-11-08T02:14:46Z',
        'read_only':True,'complete':True,
        'pages':[page(1868,'preparedness','publish',0,'https://finalvestige.com/preparedness/'),
                 page(2150,'household-records-map','draft',1868,'https://finalvestige.com/?page_id=2150')],
        'posts':[],'totals':{'pages':2,'posts':0}}
    return man,snapshot

class RouteTests(unittest.TestCase):
    def setUp(self):self.m,self.s=sample()
    def check(self):return gate.audit(self.m,self.s)
    def reject(self):
        p=self.check();self.assertEqual(p['state'],gate.INVALID,p)
        self.assertFalse(p['publication_authorized'])
        self.assertEqual(p['confirmed_route_conflicts'],[])
    def test_original_draft_is_nonconflicting_and_never_live(self):
        p=self.check();self.assertEqual(p['state'],gate.HOLD,p)
        self.assertEqual(p['summary']['frozen_articles'],35)
        self.assertEqual(p['summary']['export_targets_not_verified'],41)
        self.assertEqual(p['summary']['confirmed_conflicts'],0)
        self.assertEqual(p['summary']['draft_routes_not_live'],1)
        self.assertEqual(p['nonconflicting_drafts'][0]['wp_id'],2150)
        self.assertFalse(p['independent_qd_pass'])
        self.assertIsNone(p['net_revenue_per_1000'])
    def test_deterministic(self):self.assertEqual(self.check(),self.check())
    def test_stale_archive_root(self):
        self.s['pages'][0]['status']='draft';self.reject()
    def test_archive_slug_move(self):
        self.s['pages'][0]['slug']='not-preparedness';self.reject()
    def test_archive_permalink_changed(self):
        self.s['pages'][0]['link']='https://finalvestige.com/preparedness-old/';self.reject()
    def test_incomplete_page_inventory(self):
        self.s['totals']['pages']=3;self.reject()
    def test_missing_parent(self):
        self.s['pages'][1]['parent']=1900;self.reject()
    def test_cycle_in_page_graph(self):
        self.s['pages'][0]['parent']=2150;self.reject()
    def test_duplicate_wp_record(self):
        self.s['pages'].append(copy.deepcopy(self.s['pages'][1]));self.s['totals']['pages']=3;self.reject()
    def test_missing_state(self):
        self.s['complete']=False;self.reject()
    def test_nonreadonly_input(self):
        self.s['read_only']=False;self.reject()
    def test_false_authorization(self):
        self.m['publication_authorized']=True;self.reject()
    def test_false_qd(self):
        self.m['independent_qd_pass']=True;self.reject()
    def test_seven_heads_required(self):
        self.m['branch_heads'].pop('cluster-7');self.reject()
    def test_unsafe_protocol(self):
        self.s['pages'][1]['link']='http://finalvestige.com/?page_id=2150';self.reject()
    def test_other_domain(self):
        self.s['pages'][1]['link']='https://elsewhere.invalid/?page_id=2150';self.reject()
    def test_unapproved_preview_query(self):
        self.s['pages'][1]['link']='https://finalvestige.com/?page_id=2150&preview=true';self.reject()
    def test_duplicate_post_canonical(self):
        p=lambda id:{'id':id,'slug':'other','status':'publish','parent':0,
          'link':'https://finalvestige.com/other/','modified':'now','title':'Other'}
        self.s['posts']=[p(7),p(8)];self.s['totals']['posts']=2;self.reject()
    def test_bad_route_slash(self):
        self.m['articles'][0]['route']='/preparedness//article-1/';self.reject()
    def test_one_missing_article(self):
        self.m['articles'].pop();self.reject()
    def test_replaced_body_oid(self):
        self.m['articles'][7]['body_oid']='not-a-sha';self.reject()
    def test_changed_cluster_sha(self):
        self.m['articles'][6]['branch_sha']='f'*40;self.reject()
    def test_duplicate_slate_slug(self):
        self.m['articles'][2]['slug']='article-2';self.reject()
    def test_unverified_published_page_detected(self):
        r=self.s['pages'][1];r['slug']='article-1';r['status']='publish'
        r['parent']=1868;r['link']='https://finalvestige.com/preparedness/article-1/'
        p=self.check();self.assertEqual(p['state'],gate.HOLD)
        self.assertEqual(p['summary']['possible_conflicts'],1)
        self.assertEqual(p['summary']['confirmed_conflicts'],0)
    def test_wp_live_page_on_exact_target_detected(self):
        self.s['pages'].append({'id':2152,'slug':'start-here','status':'draft',
          'parent':1868,'link':'https://finalvestige.com/?page_id=2152',
          'modified':'now','title':'start-here'})
        self.s['pages'].append({'id':2153,'slug':'article-1','status':'draft',
          'parent':2152,'link':'https://finalvestige.com/?page_id=2153',
          'modified':'now','title':'article-1'})
        self.s['totals']['pages']=4
        p=self.check();self.assertEqual(p['state'],gate.HOLD,p)
        self.assertEqual(p['summary']['confirmed_conflicts'],1)
        self.assertEqual(p['confirmed_route_conflicts'][0]['wp_id'],2153)
    def test_published_link_mismatch_cannot_pass(self):
        self.s['pages'][1]['status']='publish'
        self.s['pages'][1]['link']='https://finalvestige.com/not-canonical/'
        self.reject()
    def test_bad_snapshot_time(self):
        self.s['captured_at']='2026-11-08';self.reject()
    def test_cli_missing_checkout_invalid(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(gate.main(['--manifest',temp+'/unknown','--snapshot',temp+'/none']),3)


def collision(n):
    def fn(self):
        row=self.m['articles'][n-1]
        # Build a published WP post at the exact frozen destination.
        self.s['posts'].append({'id':n,'slug':row['slug'],'status':'publish',
          'parent':0,'link':'https://finalvestige.com'+row['route'],
          'modified':'now','title':row['slug']})
        self.s['totals']['posts']=1
        report=self.check()
        self.assertEqual(report['state'],gate.HOLD,report)
        self.assertEqual(report['summary']['confirmed_conflicts'],1)
        self.assertFalse(report['publication_authorized'])
    return fn

def drift(n):
    def fn(self):
        self.m['articles'][n-1]['route']='/preparedness/tampered/'
        self.reject()
    return fn
for n in range(1,36):
    setattr(RouteTests,f'test_all_35_collision_{n:02d}',collision(n))
    setattr(RouteTests,f'test_all_35_manifest_drift_{n:02d}',drift(n))

if __name__=='__main__':unittest.main()

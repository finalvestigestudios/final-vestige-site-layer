"""R338 synthetic adversarial cases. Neither fixtures nor tests are QD approval."""
from __future__ import annotations
import copy
import tempfile
from pathlib import Path
import unittest
from preparedness.tools import r338_frozen_link_graph_hold as gate
from preparedness.tests.test_r337_measured_source_integrity import make_fixture


def fixture():
    rows=[]
    for i in range(35):
        slug=f'article-{i+1:02d}'
        rows.append(dict(kind='articles',slug=slug,route=f'/preparedness/start-here/{slug}/',links={}))
    tools=['family-reunification-card','home-fire-escape-worksheet','kit-builder','power-outage-planner','reunification-plan','water-planner']
    for slug in tools: rows.append(dict(kind='tools',slug=slug,route=f'/preparedness/field-tools/{slug}/',links={}))
    rows[0]['links']={'article-02':2,'family-reunification-card':1}
    return rows


class GraphControls(unittest.TestCase):
    def setUp(self):self.rows=fixture()
    def errors(self,rows=None):return gate.graph(rows if rows is not None else self.rows)['errors']
    def test_clean_is_still_hard_hold(self):
        r=gate.graph(self.rows)
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD',r['errors'])
        self.assertEqual(r['internal_links_to_unpublished_tools'],1)
        for key in ['may_publish','may_merge','paid_preparedness_sku_verified','qualified_qd_pass','tool_104_emergency_privacy_approved','may_activate_commerce']:
            self.assertIs(r[key],False)
    def test_empty_graph_rejected(self):self.assertIn('GRAPH_REQUIRES_EXACTLY_41_ROWS',gate.graph([])['errors'])
    def test_wrong_row_type(self):
        self.rows[4]=None;self.assertIn('INVALID_ROW:4',self.errors())
    def test_duplicate_kind(self):
        self.rows[36]['slug']='article-01';self.assertIn('DUPLICATE_CROSS_KIND_SLUG:article-01',self.errors())
    def test_duplicate_route(self):
        self.rows[2]['route']=self.rows[1]['route'];self.assertIn('DUPLICATE_ROUTE:article-03',self.errors())
    def test_missing_tool104(self):
        self.rows[35]['slug']='other-tool';self.assertIn('TOOL_104_AND_102_IDENTITY_NOT_DISTINCT',self.errors())
    def test_missing_tool102(self):
        self.rows[39]['slug']='other-tool';self.assertIn('TOOL_104_AND_102_IDENTITY_NOT_DISTINCT',self.errors())
    def test_unknown_link(self):
        self.rows[0]['links']={'not-a-real-slug':2};self.assertIn('UNRESOLVED_INTERNAL_LINK:article-01:not-a-real-slug',self.errors())
    def test_count_float(self):
        self.rows[0]['links']={'article-02':1.0};self.assertIn('INVALID_LINK_OCCURRENCE_COUNT:article-01:article-02',self.errors())
    def test_count_bool(self):
        self.rows[0]['links']={'article-02':True};self.assertIn('INVALID_LINK_OCCURRENCE_COUNT:article-01:article-02',self.errors())
    def test_negative_count(self):
        self.rows[0]['links']={'article-02':-1};self.assertIn('INVALID_LINK_OCCURRENCE_COUNT:article-01:article-02',self.errors())
    def test_bad_target(self):
        self.rows[0]['links']={'../../secret':1};self.assertIn('INVALID_LINK_TARGET:article-01',self.errors())
    def test_not_a_dict(self):
        self.rows[0]['links']=['article-02'];self.assertIn('INVALID_LINK_COUNTER:article-01',self.errors())
    def test_authentic_counts_not_claimed_with_synthetic(self):
        self.assertTrue(any('AUTHENTIC_GRAPH_' in x for x in gate.graph(self.rows,require_authentic_counts=True)['errors']))
    def test_missing_checkout_rejects(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=gate.audit(Path(tmp));self.assertEqual(r['state'],'INVALID_HARD_HOLD')
            self.assertIn('R337_SOURCE_DEPTH_AND_CITATION_CUSTODY_FAILED',r['errors'])
    def test_synthetic_slate_does_not_fake_frozen_pins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);w,_=make_fixture(root)
            r=gate.audit(root,synthetic_witness=w)
            self.assertEqual(r['state'],'INVALID_HARD_HOLD')
            self.assertTrue(any('FROZEN_GRAPH_SOURCE_PART_CHANGED' in x for x in r['errors']))
    def test_synthetic_41_generic_tools_still_held_without_pins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);w,_=make_fixture(root)
            r=gate.audit(root,synthetic_witness=w,enforce_frozen_pins=False)
            self.assertEqual(r['state'],'INVALID_HARD_HOLD',r['errors'])
            self.assertIn('TOOL_104_AND_102_IDENTITY_NOT_DISTINCT',r['errors'])
            self.assertFalse(r['may_publish'])


def make_test_attr(index,field,value,expected):
    def check(self):
        a=fixture(); a[index][field]=value
        self.assertTrue(any(expected in err for err in gate.graph(a)['errors']), (field,index,expected))
    return check

for k in range(41):
    setattr(GraphControls,f'test_entry_{k+1:02d}_unsafe_slug',make_test_attr(k,'slug','../escape','INVALID_KIND_OR_SLUG'))
    setattr(GraphControls,f'test_entry_{k+1:02d}_bad_route',make_test_attr(k,'route',f'/preparedness/wrong-{k}/','ROUTE_SLUG_OR_SECTION_DRIFT'))
    setattr(GraphControls,f'test_entry_{k+1:02d}_unknown_link',make_test_attr(k,'links',{'missing-'+str(k):1},'UNRESOLVED_INTERNAL_LINK'))


if __name__=='__main__':unittest.main()

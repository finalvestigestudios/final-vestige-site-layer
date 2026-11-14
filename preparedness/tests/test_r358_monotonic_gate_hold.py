"""Adversarial synthetic QA taxonomy controls. NOT a native corpus or QD test."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import r358_monotonic_gate_hold as gate

SECTIONS=['start-here','water','food','shelter-power','health-sanitation',
          'family-communication','lost-ways','field-tools']
ESCALATIONS=set(gate.ESCALATED)


def fixtures():
    entries=[]
    for n in range(1,36):
        slug=next((s for s,v in gate.ESCALATED.items() if v==n),f'original-article-{n}')
        section='start-here' if slug in ESCALATIONS else SECTIONS[n%7]
        entries.append(dict(n=n,title=f'Authentic editorial slot {n}',slug=slug,
                            section=section,track='modern' if n<=20 else 'historical',
                            status='drafted-pending-safety-review',gate= n%2==0 and slug not in ESCALATIONS))
    tools=[dict(slug=s,title=f'Original {s}',gate=True,status='drafted-pending-safety-review')
           for s in ('water-planner','home-fire-escape-worksheet','power-outage-planner',
                     'family-reunification-card','reunification-plan','kit-builder')]
    base=dict(base_path='/preparedness/',sections=[dict(slug=s) for s in SECTIONS],
              slate=entries,tools=tools)
    qa=copy.deepcopy(base)
    for article in qa['slate']:
        if article['slug'] in ESCALATIONS:article['gate']=True
    integrated=copy.deepcopy(qa)
    for slug in ('pantry-worksheet','checklists','offline-reference'):
        integrated['tools'].append(dict(slug=slug,title=slug,status='not-started'))
    return base,qa,integrated


def run(base=None,qa=None,integrated=None,**kw):
    originals=fixtures()
    b,q,c=[copy.deepcopy(x) for x in originals]
    if base is not None: b=base
    if qa is not None: q=qa
    if integrated is not None:c=integrated
    return gate.adjudicate(json.dumps(b,sort_keys=True),json.dumps(q,sort_keys=True),
                           json.dumps(c,sort_keys=True),**kw)


class GateAuditTests(unittest.TestCase):
    def test_baseline_restricted_and_hard_held(self):
        result=run()
        self.assertEqual(result['status'],'SOURCE_REVIEW_REQUIRED_HARD_HOLD')
        self.assertEqual(len(result['review_docket']),3)
        for key,value in gate.HOLD.items(): self.assertIs(result[key],False)

    def test_synthetic_pin_is_not_authentic(self):
        result=run(require_authentic_pins=True)
        self.assertIn('GIT_BLOB_PIN_MISMATCH',result['errors'])

    def test_native_missing_checkout_holds(self):
        with tempfile.TemporaryDirectory() as root:
            result=gate.native_review(Path(root))
        self.assertEqual(result['status'],'INVALID_HARD_HOLD')
        self.assertTrue(result['errors'][0].startswith('NATIVE_SOURCE_UNAVAILABLE:'))

    def test_missing_repo_path_holds(self):
        result=gate.native_review(Path('/missing/r358/source-not-present'))
        self.assertEqual(result['status'],'INVALID_HARD_HOLD')

    def test_json_is_deterministic(self):
        self.assertEqual(run(),run())

    def test_public_disposition_remains_false(self):
        b,q,c=fixtures()
        for row in c['slate']:row['gate']=True
        result=run(b,q,c)
        self.assertFalse(result['may_publish'])
        self.assertFalse(result['qualified_qd_pass'])
        self.assertFalse(result['paid_offer_verified'])

    def test_extra_planned_tools_are_reviewed_not_silent(self):
        self.assertEqual(run()['review_docket'],[
            'ADDED_PLANNED_TOOL_REVIEW:checklists',
            'ADDED_PLANNED_TOOL_REVIEW:offline-reference',
            'ADDED_PLANNED_TOOL_REVIEW:pantry-worksheet'])

    def test_same_status_delta_is_a_review_not_release(self):
        b,q,c=fixtures();c['slate'][0]['status']='not-started'
        r=run(b,q,c)
        self.assertIn('EDITORIAL_STATUS_REVIEW:household-emergency-plan',r['review_docket'])
        self.assertEqual(r['status'],'SOURCE_REVIEW_REQUIRED_HARD_HOLD')

    def test_gate_blob_sha_deterministic(self):
        self.assertEqual(gate.git_blob(''), 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')
        self.assertEqual(gate.sha256('a'), 'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb')

    def test_empty_string_rejected(self):
        self.assertEqual(gate.adjudicate('','', '')['status'],'INVALID_HARD_HOLD')

    def test_null_is_rejected_without_crash(self):
        self.assertEqual(gate.adjudicate(None,None,None)['status'],'INVALID_HARD_HOLD')


def add_case(name,where,mutate,needle):
    def test(self):
        b,q,c=fixtures()
        target={'before':b,'qa':q,'merged':c}[where]
        mutate(target)
        report=run(b,q,c)
        self.assertEqual(report['status'],'INVALID_HARD_HOLD',name)
        self.assertTrue(any(needle in err for err in report['errors']),
                        f'{name}: {report["errors"]}')
        self.assertFalse(report['may_merge'])
        self.assertFalse(report['may_publish'])
    test.__name__='test_'+name
    setattr(GateAuditTests,test.__name__,test)

# Individually named adversarial controls, rather than a single loop passing once.
for slug in sorted(ESCALATIONS):
    i=gate.ESCALATED[slug]-1
    add_case('qa_escalation_reverted_'+slug.replace('-','_'),'qa',
             lambda t,j=i: t['slate'][j].update(gate=False),'QA_ESCALATION_UNAUTHENTICATED')
    add_case('merged_gate_reverted_'+slug.replace('-','_'),'merged',
             lambda t,j=i: t['slate'][j].update(gate=False),'INTEGRATION_GATE_DOWNGRADE')
    add_case('merged_gate_deleted_'+slug.replace('-','_'),'merged',
             lambda t,j=i: t['slate'][j].pop('gate'),'INTEGRATION_GATE_DOWNGRADE')
    add_case('qa_escalation_number_forged_'+slug.replace('-','_'),'qa',
             lambda t,j=i: t['slate'][j].update(n=35+j),'DUPLICATE_OR_INVALID_ARTICLE_NUMBER')

add_case('qa_changes_article_title','qa',lambda t:t['slate'][0].update(title='unsafe edit'),
         'QA_UNEXPECTED_ARTICLE_MUTATION')
add_case('qa_changes_article_status','qa',lambda t:t['slate'][0].update(status='safety-approved-draft'),
         'QA_UNEXPECTED_ARTICLE_MUTATION')
add_case('qa_changes_section_metadata','qa',lambda t:t['sections'][0].update(label='Unapproved'),
         'QA_NONSLATE_MUTATION')
add_case('qa_adds_tool','qa',lambda t:t['tools'].append(dict(slug='new-tool',status='not-started')),
         'QA_NONSLATE_MUTATION')
add_case('qa_changes_existing_gate','qa',lambda t:t['slate'][1].update(gate=False),
         'QA_ESCALATION_UNAUTHENTICATED')
add_case('qa_weaken_existing_gate','qa',lambda t:t['slate'][3].update(gate=False),
         'QA_WEAKENED_EXISTING_GATE')
add_case('qa_unauthorized_gate_increase','qa',lambda t:t['slate'][2].update(gate=True),
         'QA_UNEXPECTED_GATE_CHANGE')
add_case('qa_deletes_article','qa',lambda t:t['slate'].pop(), 'INVENTORY_DRIFT')
add_case('merged_drops_article','merged',lambda t:t['slate'].pop(1), 'INVENTORY_DRIFT')
add_case('merged_duplicate_article_n','merged',lambda t:t['slate'][0].update(n=2),
         'DUPLICATE_OR_INVALID_ARTICLE_NUMBER')
add_case('merged_duplicate_article_slug','merged',lambda t:t['slate'][0].update(slug=t['slate'][1]['slug']),
         'DUPLICATE_ARTICLE_SLUG')
add_case('merged_slug_with_slash','merged',lambda t:t['slate'][0].update(slug='../escape'),
         'UNSAFE_SLUG')
add_case('merged_slug_absolute_url','merged',lambda t:t['slate'][0].update(slug='https://attacker'),
         'UNSAFE_SLUG')
add_case('merged_slug_nonascii','merged',lambda t:t['slate'][0].update(slug='café'),
         'UNSAFE_SLUG')
add_case('merged_url_query','merged',lambda t:t['slate'][0].update(slug='plan?x=y'),
         'UNSAFE_SLUG')
add_case('merged_gate_is_string','merged',lambda t:t['slate'][0].update(gate='false'),
         'NONBOOLEAN_GATE')
add_case('merged_gate_is_number','merged',lambda t:t['slate'][0].update(gate=1),
         'NONBOOLEAN_GATE')
add_case('merged_approval_state','merged',lambda t:t['slate'][0].update(status='published'),
         'INVALID_PUBLICATION_STATE')
add_case('merged_unauthorized_section','merged',lambda t:t['slate'][0].update(section='news'),
         'ARTICLE_SECTION_DRIFT')
add_case('merged_article_into_tools_section','merged',lambda t:t['slate'][0].update(section='field-tools'),
         'ARTICLE_SECTION_DRIFT')
add_case('merged_identity_title_changed','merged',lambda t:t['slate'][0].update(title='changed'),
         'INTEGRATION_ARTICLE_IDENTITY_DRIFT')
add_case('merged_identity_track_changed','merged',lambda t:t['slate'][0].update(track='unknown'),
         'INTEGRATION_ARTICLE_IDENTITY_DRIFT')
add_case('merged_duplicate_tool','merged',lambda t:t['tools'][-1].update(slug=t['tools'][0]['slug']),
         'DUPLICATE_TOOL_SLUG')
add_case('merged_tool_removed','merged',lambda t:t['tools'].pop(0),
         'PLANNED_TOOL_REMOVED')
add_case('merged_tool_gate_downgraded','merged',lambda t:t['tools'][0].update(gate=False),
         'INTEGRATION_TOOL_GATE_DOWNGRADE')
add_case('merged_tool_gate_absent','merged',lambda t:t['tools'][0].pop('gate'),
         'INTEGRATION_TOOL_GATE_DOWNGRADE')
add_case('merged_tool_section_changed','merged',lambda t:t['tools'][0].update(slug='../x'),
         'UNSAFE_SLUG')
add_case('merged_status_none','merged',lambda t:t['slate'][0].update(status=None),
         'INVALID_PUBLICATION_STATE')
add_case('merged_tool_published','merged',lambda t:t['tools'][0].update(status='live'),
         'INVALID_PUBLICATION_STATE')
add_case('base_path_changed','merged',lambda t:t.update(base_path='/'),
         'INVALID_BASE_PATH')
add_case('base_path_external','merged',lambda t:t.update(base_path='https://external.tld/'),
         'INVALID_BASE_PATH')
add_case('sections_duplicate','merged',lambda t:t['sections'][0].update(slug='water'),
         'INVALID_SECTIONS')
add_case('sections_missing','merged',lambda t:t['sections'].pop(),
         'INVENTORY_DRIFT')
add_case('sections_protocol','merged',lambda t:t['sections'][0].update(slug='javascript:x'),
         'INVALID_SECTIONS')
add_case('sections_not_list','merged',lambda t:t.update(sections='oops'),
         'INVALID_COLLECTION')
add_case('articles_not_list','merged',lambda t:t.update(slate='oops'),
         'INVALID_COLLECTION')
add_case('tools_not_list','merged',lambda t:t.update(tools='oops'),
         'INVALID_COLLECTION')
add_case('tools_too_many','merged',lambda t:t['tools'].extend([
    dict(slug=f'planned-{x}',status='not-started') for x in range(4)]),
         'INVENTORY_DRIFT')
add_case('tools_too_few','merged',lambda t:t.update(tools=t['tools'][:5]),
         'INVENTORY_DRIFT')
add_case('article_not_object','merged',lambda t:t['slate'].__setitem__(0,'not-object'),
         'NONOBJECT_ENTRY')
add_case('tool_not_object','merged',lambda t:t['tools'].__setitem__(0,42),
         'NONOBJECT_ENTRY')
add_case('number_string','merged',lambda t:t['slate'][0].update(n='1'),
         'DUPLICATE_OR_INVALID_ARTICLE_NUMBER')
add_case('number_boolean','merged',lambda t:t['slate'][0].update(n=True),
         'DUPLICATE_OR_INVALID_ARTICLE_NUMBER')
add_case('nonascii_tool','merged',lambda t:t['tools'][0].update(slug='mañana'),
         'UNSAFE_SLUG')
add_case('blank_slug','merged',lambda t:t['tools'][0].update(slug=''),
         'UNSAFE_SLUG')
add_case('double_dash_slug','merged',lambda t:t['tools'][0].update(slug='odd--slug'),
         'UNSAFE_SLUG')

if __name__=='__main__':unittest.main()

#!/usr/bin/env python3
"""R47 synthetic, independent visible claim/source/URL evidence parity tests."""
import copy
import importlib.util
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / 'tools' / 'reviewer_visible_row_parity_gate.py'
spec = importlib.util.spec_from_file_location('preparedness_r47_visible_parity', SRC)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
r43 = gate.r45.r44.r43

def sample():
    data = {
        'slug':'r47-synthetic-article', 'title':'Synthetic citation review',
        'fingerprint_sha256':'a'*64,
        'counts':{'claims':2,'scopes':1,'fallbacks':1,'groups':1},
        'taxonomy_status_recorded_not_a_human_verdict':'drafted-pending-safety-review',
        'taxonomy_safety_gate_recorded_not_approval':True,
        'required_independent_checks':['Read the source independently',
                                        'Require independent safety review'],
    }
    records = {}
    marker_values = []
    for index, kind in enumerate(gate.KINDS):
        rows = []
        for nr in range(2 if kind == 'claims' else 1):
            row = {gate.IDS[index]: chr(98+index)*64,
                   'review_state':'NOT_STARTED',
                   'source_url':'https://example.org/'+kind+'/'+str(nr)}
            for n in range(10):
                token = 'R47_'+kind.upper()+'_'+str(nr)+'_EVIDENCE_'+str(n).zfill(2)+'_VALUE'
                row['source_field_'+str(n).zfill(2)] = token
                if nr == 0:
                    marker_values.append(token)
            rows.append(row)
        records[kind] = rows
    data['original_review_records'] = records
    return data, marker_values

def render_article(d):
    parts = ['<section><p>'+gate.DISCLAIMER+'</p>',
             '<h2>Evidence identity and review requirements</h2><dl>']
    for key in gate.IDENTITY_FIELDS:
        parts.append('<dt>'+r43.literal(key)+'</dt><dd><pre>'+
                     r43.literal(d[key])+'</pre></dd>')
    parts.append('</dl></section>')
    for kind in gate.KINDS:
        parts.append(r43.rows_html(kind,d['original_review_records'][kind]))
    return r43.page(d['title'],''.join(parts),'../index.html')

def sample_index(ds, expected):
    parts = ['<section><h2>All original article/tool reviews</h2>',
             '<p>Unreviewed citations: '+str(expected[2])+
             ', separate source reading relationships: '+str(expected[3])+
             ', fallbacks: '+str(expected[4])+
             ', repeated-source groups: '+str(expected[5])+'</p>',
             '<p><a href="global-source-variants.html">Review every shared URL group</a></p><ol>']
    for d in sorted(ds,key=lambda x:x['slug']):
        parts.append('<li><a href="articles/'+d['slug']+'.html">'+
                     r43.literal(d['title'])+'</a> — '+str(d['counts']['claims'])+
                     ' individual citation checks</li>')
    parts.append('</ol></section>')
    return r43.page('Preparedness PRIVATE review desk',''.join(parts))

class CompleteVisibleDossier(unittest.TestCase):
    def setUp(self):
        self.d, self.markers = sample()
        self.html = render_article(self.d)

    def check(self, html=None, dossier=None):
        return gate.check_dossier(dossier or self.d,
                                  gate.parse_page(html if html is not None else self.html))

    def test_original_full_field_census_is_readable(self):
        n = self.check()
        self.assertEqual(n, len(gate.IDENTITY_FIELDS)+
                         sum(len(row) for kind in gate.KINDS
                             for row in self.d['original_review_records'][kind]))

    def test_inert_html_escape_round_trips_literals(self):
        changed = copy.deepcopy(self.d)
        changed['original_review_records']['claims'][0]['source_field_00'] = (
            'Literal <b>&"\' url=https://example.org/?a=1&b=2')
        self.assertGreater(gate.check_dossier(changed,
             gate.parse_page(render_article(changed))),0)

    def test_original_claim_context_changed_in_document_fails(self):
        bad = self.html.replace(self.markers[0], 'fabricated review',1)
        with self.assertRaises(gate.VisibleEvidenceHold):
            self.check(bad)

    def test_evidence_row_missing_fails(self):
        fragment = r43.rows_html('fallbacks',
                                 self.d['original_review_records']['fallbacks'])
        self.assertIn(fragment,self.html)
        with self.assertRaises(gate.VisibleEvidenceHold):
            self.check(self.html.replace(fragment, '<section><h2>fallbacks: 1</h2></section>',1))

    def test_evidence_row_duplicated_fails(self):
        fragment = r43.rows_html('scopes',
                                 self.d['original_review_records']['scopes'])
        self.assertIn(fragment,self.html)
        with self.assertRaises(gate.VisibleEvidenceHold):
            self.check(self.html.replace(fragment,fragment+fragment,1))

    def test_reordered_source_fields_fail(self):
        row = self.d['original_review_records']['scopes'][0]
        pairs = gate.pairs(row)
        a,b = pairs[-2:]
        old = '<dt>'+r43.literal(a[0])+'</dt><dd><pre>'+r43.literal(a[1])+'</pre></dd>'
        nxt = '<dt>'+r43.literal(b[0])+'</dt><dd><pre>'+r43.literal(b[1])+'</pre></dd>'
        self.assertIn(old+nxt,self.html)
        with self.assertRaises(gate.VisibleEvidenceHold):
            self.check(self.html.replace(old+nxt,nxt+old,1))

    def test_original_taxonomy_status_cannot_be_rewritten_in_html(self):
        old = self.d['taxonomy_status_recorded_not_a_human_verdict']
        with self.assertRaises(gate.VisibleEvidenceHold):
            self.check(self.html.replace(old,'safety-approved',1))

    def test_title_mismatch_is_rejected(self):
        with self.assertRaises(gate.VisibleEvidenceHold):
            self.check(self.html.replace('<h1>'+r43.literal(self.d['title'])+'</h1>',
                                         '<h1>Wrong article</h1>',1))

    def test_warning_cannot_be_removed(self):
        with self.assertRaises(gate.VisibleEvidenceHold):
            self.check(self.html.replace(gate.WARNING,'Evidence already approved',1))

    def test_disclaimer_cannot_be_removed(self):
        with self.assertRaises(gate.VisibleEvidenceHold):
            self.check(self.html.replace(gate.DISCLAIMER,'Verified safety verdict',1))

    def test_metadata_source_record_is_not_interchangeable(self):
        wrong = copy.deepcopy(self.d)
        wrong['fingerprint_sha256'] = 'e'*64
        with self.assertRaises(gate.VisibleEvidenceHold):
            self.check(dossier=wrong)

    def test_original_review_field_must_not_be_lost_in_packet(self):
        wrong = copy.deepcopy(self.d)
        del wrong['original_review_records']['claims'][0]['source_field_01']
        with self.assertRaises(gate.VisibleEvidenceHold):
            self.check(dossier=wrong)

    def test_index_title_and_counts_visible(self):
        counts=(1,0,2,1,1,1)
        index=gate.parse_page(sample_index([self.d],counts))
        gate.check_index([self.d],index,counts)

    def test_index_lie_about_citation_count_is_rejected(self):
        counts=(1,0,2,1,1,1)
        html=sample_index([self.d],counts).replace(
            '2 individual citation checks','999 individual citation checks',1)
        with self.assertRaises(gate.VisibleEvidenceHold):
            gate.check_index([self.d],gate.parse_page(html),counts)

    def test_index_link_label_mismatch_is_rejected(self):
        counts=(1,0,2,1,1,1)
        html=sample_index([self.d],counts).replace(
            'Review every shared URL group','All URLs verified',1)
        with self.assertRaises(gate.VisibleEvidenceHold):
            gate.check_index([self.d],gate.parse_page(html),counts)

    def test_global_uncited_source_variants_visible(self):
        group=self.d['original_review_records']['groups'][0]
        groups={group['global_group_case_sha256']:group}
        page=r43.page('All shared URL variants',
                      r43.rows_html('Global cited and uncited source variants',[group]),
                      'index.html')
        self.assertEqual(gate.check_global(groups,gate.parse_page(page)),len(group))

    def test_global_group_cannot_be_truncated(self):
        group=self.d['original_review_records']['groups'][0]
        groups={group['global_group_case_sha256']:group}
        page=r43.page('All shared URL variants',
                      r43.rows_html('Global cited and uncited source variants',[group]),
                      'index.html')
        page=page.replace('R47_GROUPS_0_EVIDENCE_00_VALUE','Truncated source',1)
        with self.assertRaises(gate.VisibleEvidenceHold):
            gate.check_global(groups,gate.parse_page(page))

# Forty independent, deliberately reworded original evidence field tests:
# 10 independent fields * 4 distinct claim/scope/fallback/URL groups.
# Each test must reject a changed private cell, not merely count a SHA.
for _i, _kind in enumerate(gate.KINDS):
    for _n in range(10):
        def _case(self, kind=_kind, index=_n):
            original = 'R47_'+kind.upper()+'_0_EVIDENCE_'+str(index).zfill(2)+'_VALUE'
            self.assertEqual(self.html.count(original),1)
            altered = self.html.replace(original,
                original+'_APPROVED_OR_TRUNCATED',1)
            with self.assertRaises(gate.VisibleEvidenceHold):
                self.check(altered)
        _case.__name__ = 'test_reject_changed_'+_kind+'_field_'+str(_n).zfill(2)
        setattr(CompleteVisibleDossier,_case.__name__,_case)

if __name__ == '__main__':
    unittest.main()

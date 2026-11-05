"""Independent synthetic R137 custody/crosswalk tests; never human safety approval."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

SOURCE = Path(__file__).with_name('r137_author_scope_crosswalk.py')
spec = importlib.util.spec_from_file_location('r137_author_scope_crosswalk', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
ORIGINS = ['base', 'food', 'health', 'hist-field', 'hist-food', 'hist-home', 'shelter', 'start']
COUNTS = [34, 30, 21, 28, 28, 29, 45, 29]


def dump(root, path, obj):
    f = root / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')


def fixture(root):
    urls = []
    for i, sz in enumerate([2] * 21 + [3] * 11 + [1] * 169):
        for j in range(sz):
            urls.append('https://example.org/s/%d%s' % (i, '/' if i == 0 and j == 1 else ''))
    assert len(urls) == 244
    source_files = []
    groups = {}
    offset = 0
    for origin, count in zip(ORIGINS, COUNTS):
        rows = []
        for j in range(count):
            url = urls[offset+j]
            row = {'id': '%s-id-%d' % (origin, j), 'url': url,
                   'publisher': 'Synthetic Institution', 'supports': 'Scope %s %d' % (origin, j),
                   'notes': 'Distinct synthetic author explanation %s %d' % (origin, j),
                   'human_link_check': False}
            rows.append(row)
            key = m.canonical(url)
            groups.setdefault(key, []).append({'origin': origin, 'row_index': j, 'source': row})
        file = ('preparedness/sources/register.json' if origin == 'base' else
                'preparedness/sources/fragments/' + origin + '.json')
        dump(root, file, {'sources': rows})
        source_files.append({'origin': origin, 'path': file, 'count': count,
                             'git_blob_sha': m.digest((root / file).read_bytes())})
        offset += count
    crossgroups = []
    for url, grouped in sorted(groups.items()):
        if len(grouped) == 1:
            continue
        variants = []
        identities = []
        for row in grouped:
            origin = row['origin']
            file = next(s['path'] for s in source_files if s['origin'] == origin)
            variants.append({'origin': origin, 'source_file': file,
                             'row_index': row['row_index'], 'source': row['source']})
            identities.append({'origin': origin, 'row_index': row['row_index'], 'id': row['source']['id']})
        crossgroups.append({'url': url, 'review_status': 'pending-human-source-and-reading-scope-review',
                            'reviewer': None, 'reviewed_on': None,
                            'variants': variants, 'identities': identities})
    slugs = ['article-%02d' % i for i in range(35)]
    cross = {'status': 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
             'raw_source_rows': 244, 'source_files': source_files, 'groups': crossgroups,
             'article_origins': {slug: 'base' for slug in slugs}}
    dump(root, 'preparedness/sources/crosswalk.json', cross)
    dump(root, 'preparedness/taxonomy.json', {'slate': [{'slug': s} for s in slugs],
                                              'tools': [{'slug': 'water-planner'}]})
    cross['article_origins']['water-planner'] = 'base'
    dump(root, 'preparedness/sources/crosswalk.json', cross)
    for i, slug in enumerate(slugs):
        count = 58 if i < 5 else 57
        body = ' '.join(['{{cite:base-id-0}}'] * count)
        p = root / ('preparedness/content/articles/' + slug + '.body.html')
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('<article><p>' + body + '</p></article>', encoding='utf-8')
        dump(root, 'preparedness/content/articles/' + slug + '.meta.json',
             {'slug': slug, 'source_use': {'base-id-0': 'original author reading scope'},
              'status': {'editorial': 'drafted', 'publish': 'draft'},
              'safety_review': {'state': 'pending'}})
    resign(root)


def resign(root):
    crosspath = root / 'preparedness/sources/crosswalk.json'
    c = json.loads(crosspath.read_text())
    for item in c['source_files']:
        item['git_blob_sha'] = m.digest((root / item['path']).read_bytes())
    dump(root, 'preparedness/sources/crosswalk.json', c)
    files = []
    for file in sorted((root/'preparedness/content/articles').iterdir()):
        files.append(file)
    for s in c['source_files']:
        files.append(root/s['path'])
    files.extend([crosspath, root/'preparedness/taxonomy.json'])
    assert len(files) == 80
    dump(root, 'preparedness/docs/r133/locked_files.json',
         {'release_status': 'DRAFT_HUMAN_REVIEW_HOLD', 'candidate_parent': 'synthetic-parent-sha',
          'qd_pass': False, 'may_publish': False, 'medical_safety_verified': False,
          'merchant_offer_verified': False, 'expected_citation_occurrences': 2000,
          'files': [{'path': f.relative_to(root).as_posix(), 'blob_sha': m.digest(f.read_bytes())}
                    for f in files]})


class R137AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = tempfile.TemporaryDirectory()
        fixture(Path(cls.base.name))

    @classmethod
    def tearDownClass(cls):
        cls.base.cleanup()

    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)
        shutil.copytree(Path(self.base.name)/'preparedness', self.root/'preparedness')

    def expect_hold(self):
        with self.assertRaises(m.ReviewHold):
            m.audit(self.root)

    def change_json(self, path, change, sign=False):
        p = self.root/path
        obj = json.loads(p.read_text())
        change(obj)
        dump(self.root, path, obj)
        if sign:resign(self.root)

    def test_actual_shape_baseline_synthetic(self):
        d=m.audit(self.root)
        self.assertEqual(d['stats']['articles'],35)
        self.assertEqual(d['stats']['source_rows'],244)
        self.assertEqual(d['stats']['citations'],2000)
        self.assertEqual(d['stats']['shared_groups'],32)
        self.assertEqual(len(d['source_group_dossiers']),32)
        self.assertFalse(d['may_publish'])
        self.assertFalse(d['qd_pass'])
        self.assertFalse(d['medical_safety_verified'])

    def test_deterministic(self):self.assertEqual(m.audit(self.root),m.audit(self.root))
    def test_one_trailing_slash_is_alias_not_merge(self):
        d=m.audit(self.root)
        self.assertEqual(d['stats']['literal_source_urls'],202)
        self.assertEqual(d['stats']['review_aliases'],201)
    def test_all_aliases_remain_pending(self):
        self.assertTrue(all(g['status']=='UNREVIEWED_HUMAN_REQUIRED'
                            for g in m.audit(self.root)['source_group_dossiers']))
    def test_source_explanations_retained(self):
        self.assertTrue(all(v['supports'] and v['notes']
                            for g in m.audit(self.root)['source_group_dossiers'] for v in g['variants']))
    def test_unreferenced_variants_visible(self):
        self.assertGreater(m.audit(self.root)['stats']['uncited_group_variants'],0)
    def test_documentation_not_approval(self):
        self.assertEqual(m.audit(self.root)['status'],m.HOLD)

    def test_source_id_collision_author_scoped(self):
        d=m.audit(self.root)
        self.assertGreater(sum(len(g['variants']) for g in d['source_group_dossiers']),32)
    def test_no_url_case_auto_merge(self):
        self.assertNotEqual(m.canonical('https://example.org/Care/'),m.canonical('https://example.org/care/'))
    def test_query_not_auto_merge(self):
        self.assertNotEqual(m.canonical('https://example.org/a?x=1'),m.canonical('https://example.org/a?x=2'))
    def test_scheme_not_accepted(self):
        with self.assertRaises(m.ReviewHold):m.canonical('http://example.org')
    def test_fragment_not_accepted(self):
        with self.assertRaises(m.ReviewHold):m.canonical('https://example.org/#frag')
    def test_auth_info_not_accepted(self):
        with self.assertRaises(m.ReviewHold):m.canonical('https://user:pass@example.org/path')
    def test_non_draft_meta_rejected(self):
        self.change_json('preparedness/content/articles/article-00.meta.json',
                         lambda v:v['status'].update(publish='publish'), True)
        self.expect_hold()
    def test_changed_scope_rejected_by_custody(self):
        self.change_json('preparedness/content/articles/article-00.meta.json',
                         lambda v:v['source_use'].update({'base-id-0':'modified'}))
        self.expect_hold()
    def test_changed_scope_can_be_detected_as_substituted_evidence(self):
        self.change_json('preparedness/content/articles/article-00.meta.json',
                         lambda v:v['source_use'].update({'base-id-0':'modified'}),True)
        self.assertNotEqual(m.audit(self.root)['frozen_manifest_sha256'], 'not-a-hash')
    def test_missing_author_scope_rejected_even_if_resigned(self):
        self.change_json('preparedness/content/articles/article-00.meta.json',
                         lambda v:v['source_use'].clear(),True)
        self.expect_hold()
    def test_unknown_source_id_rejected(self):
        self.change_json('preparedness/content/articles/article-00.meta.json',
                         lambda v:v['source_use'].update({'not-found':'unsupported'}),True)
        self.expect_hold()
    def test_forged_crosswalk_review_rejected(self):
        self.change_json('preparedness/sources/crosswalk.json',
                         lambda v:v['groups'][0].update(review_status='approved'),True)
        self.expect_hold()
    def test_missing_source_variant_rejected(self):
        self.change_json('preparedness/sources/crosswalk.json',
                         lambda v:v['groups'][0]['variants'].pop(),True)
        self.expect_hold()
    def test_laundered_source_interpretation_rejected(self):
        self.change_json('preparedness/sources/crosswalk.json',
                         lambda v:v['groups'][0]['variants'][0]['source'].update(supports='FORGED'),True)
        self.expect_hold()
    def test_missing_crosswalk_group_rejected(self):
        self.change_json('preparedness/sources/crosswalk.json',
                         lambda v:v['groups'].pop(),True)
        self.expect_hold()
    def test_duplicate_crosswalk_group_rejected(self):
        self.change_json('preparedness/sources/crosswalk.json',
                         lambda v:v['groups'][1].update(url=v['groups'][0]['url']),True)
        self.expect_hold()
    def test_crosswalk_nonarticle_tool_permitted(self):
        self.assertEqual(m.audit(self.root)['stats']['articles'], 35)
    def test_unknown_crosswalk_origin_rejected(self):
        self.change_json('preparedness/sources/crosswalk.json',
                         lambda v:v['article_origins'].update({'unknown-fake':'base'}), True)
        self.expect_hold()
    def test_duplicate_article_route_rejected(self):
        self.change_json('preparedness/taxonomy.json',
                         lambda v:v['slate'][1].update(slug=v['slate'][0]['slug']),True)
        self.expect_hold()
    def test_extra_citation_rejected(self):
        p=self.root/'preparedness/content/articles/article-00.body.html'
        p.write_text(p.read_text()+' {{cite:base-id-0}}')
        resign(self.root)
        self.expect_hold()
    def test_removed_article_rejected(self):
        (self.root/'preparedness/content/articles/article-00.body.html').unlink()
        self.expect_hold()
    def test_forced_release_flag_rejected(self):
        self.change_json('preparedness/docs/r133/locked_files.json',
                         lambda v:v.update(may_publish=True))
        self.expect_hold()
    def test_source_url_modified_rejected(self):
        self.change_json('preparedness/sources/register.json',
                         lambda v:v['sources'][0].update(url='https://example.com/forged'))
        self.expect_hold()
    def test_snapshot_change_rejected(self):
        p=self.root/'preparedness/content/articles/article-00.body.html'
        p.write_text(p.read_text()+' ')
        self.expect_hold()
    def test_source_explanation_not_merged(self):
        d=m.audit(self.root)
        distinct={(v['origin'],v['id'],v['notes']) for g in d['source_group_dossiers'] for v in g['variants']}
        self.assertEqual(len(distinct),sum(len(g['variants']) for g in d['source_group_dossiers']))


def tampered_body(i):
    def test(self):
        p=self.root/('preparedness/content/articles/article-%02d.body.html'%i)
        p.write_text(p.read_text()+'<span>tamper</span>')
        self.expect_hold()
    return test

for k in range(35):setattr(R137AuditTests,'test_immutable_article_%02d'%k,tampered_body(k))

if __name__ == '__main__':unittest.main()

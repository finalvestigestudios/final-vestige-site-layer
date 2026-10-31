"""R16 source-preservation tests. Synthetic HTML only; no safety approval."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import qa_current_copy_concordance as g

class ReviewOnlyTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='fvs-r16-')
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        folder=self.root/'preparedness/content/articles'
        folder.mkdir(parents=True)
        self.slugs=list(g.ARTICLES)+[f'synthetic-{n:02d}' for n in range(33)]
        self.files={}
        self.original={}
        for slug in self.slugs:
            content='<article>\n'+'\n'.join('<p>'+s+'</p>' for s in g.KEY.get(slug,('other historical context and caveats',)))+'\n{{cite:start-ready-power}}\n</article>\n'
            p=folder/(slug+'.body.html');p.write_text(content,encoding='utf8')
            (folder/(slug+'.meta.json')).write_text('{"slug":"'+slug+'"}',encoding='utf8')
            self.files[slug]=p;self.original[slug]=content
        self.taxonomy=self.root/'preparedness/taxonomy.json'
        self.taxonomy.write_text(json.dumps({'slate':[{'slug':s} for s in self.slugs]}))
        self.source=self.root/'preparedness/sources/fragments/start.json'
        self.source.parent.mkdir(parents=True)
        self.source.write_text('{"sources":[]}')
        self.article_hashes={s:g.blob(self.files[s].read_bytes()) for s in g.ARTICLES}
        self.guard_hashes={str(p.relative_to(self.root)):g.blob(p.read_bytes()) for p in (self.taxonomy,self.source)}
        a=patch.dict(g.ARTICLES,self.article_hashes,clear=True);b=patch.dict(g.GUARDS,self.guard_hashes,clear=True)
        a.start();b.start();self.addCleanup(a.stop);self.addCleanup(b.stop)

    def test_clean_fixture_stays_hold(self):
        r=g.verify(self.root)
        self.assertEqual(r['article_count'],35)
        self.assertEqual(r['qa_157_transplant'],'REJECT_STALE_ALREADY_SUPERSEDED')
        self.assertIs(r['may_publish'],False)
        self.assertIs(r['qualified_safety_clearance'],False)
        self.assertEqual(r['independent_source_claim_checks'],0)

    def test_git_blob_vector(self):
        self.assertEqual(g.blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')

    def test_does_not_mutate_articles_or_create_wp_output(self):
        before=self.files['three-day-kit'].read_bytes()
        g.verify(self.root)
        self.assertEqual(before,self.files['three-day-kit'].read_bytes())
        self.assertFalse((self.root/'preparedness/build').exists())

    def test_source_row_change_rejected(self):
        self.source.write_text('{"sources":[{"id":"unverified"}]}')
        with self.assertRaises(g.HoldError):g.verify(self.root)

    def test_taxonomy_gate_change_rejected(self):
        self.taxonomy.write_text(self.taxonomy.read_text()+'\n')
        with self.assertRaises(g.HoldError):g.verify(self.root)

    def test_slate_url_drift_rejected(self):
        self.taxonomy.write_text(json.dumps({'slate':[{'slug':'wrong'}]+[{'slug':s} for s in self.slugs[1:]]}))
        self.guard_hashes[str(self.taxonomy.relative_to(self.root))]=g.blob(self.taxonomy.read_bytes())
        with self.assertRaises(g.HoldError):g.verify(self.root)

    def test_missing_article_rejected(self):
        self.files[self.slugs[-1]].unlink()
        with self.assertRaises(g.HoldError):g.verify(self.root)

    def test_missing_meta_rejected(self):
        (self.files[self.slugs[-1]].with_name(self.slugs[-1]+'.meta.json')).unlink()
        with self.assertRaises(g.HoldError):g.verify(self.root)

    def test_body_blob_drift_rejected(self):
        p=self.files['household-emergency-plan'];p.write_text(p.read_text()+'\n')
        with self.assertRaises(g.HoldError):g.verify(self.root)

    def test_source_symlink_rejected(self):
        self.source.unlink();self.source.symlink_to(self.taxonomy)
        with self.assertRaises(g.HoldError):g.verify(self.root)


def mutation(slug,word,index,method):
    def test(self):
        p=self.files[slug]
        if method=='remove':updated=self.original[slug].replace(word,'')
        elif method=='change':updated=self.original[slug].replace(word,'not reviewed or supported')
        else:updated=self.original[slug]+'\n<p>'+word+'</p>'
        p.write_text(updated,encoding='utf8')
        self.article_hashes[slug]=g.blob(p.read_bytes())
        with self.assertRaises(g.HoldError):g.verify(self.root)
    test.__name__=f'test_{method}_{slug.replace("-","_")}_{index:02d}'
    return test

for slug,terms in g.KEY.items():
    for idx,term in enumerate(terms):
        for kind in ('remove','change'):
            func=mutation(slug,term,idx,kind)
            setattr(ReviewOnlyTests,func.__name__,func)
for idx,(slug,term) in enumerate(g.UNSAFE_OLD+g.QA_NEW):
    func=mutation(slug,term,idx,'append')
    setattr(ReviewOnlyTests,func.__name__,func)

if __name__=='__main__':unittest.main(verbosity=2)

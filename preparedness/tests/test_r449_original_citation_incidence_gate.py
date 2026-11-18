"""R449: synthetic-only original candidate citation custody tests (no QD PASS)."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

TOOLS=Path(__file__).resolve().parents[1]/"tools"
spec=importlib.util.spec_from_file_location("r449",TOOLS/"r449_original_citation_incidence_gate.py")
r=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
oldspec=importlib.util.spec_from_file_location("r448_tests",
    Path(__file__).with_name("test_r448_article_readiness_matrix.py"))
old=importlib.util.module_from_spec(oldspec)
oldspec.loader.exec_module(old)

def corpus():
    """35 fake articles, nine fake roots, original *shape* but no actual source evidence."""
    tmp=tempfile.TemporaryDirectory()
    d,packet,heads=old.fixtures()
    roots={row["branch"]:str(Path(tmp.name)/str(i))
        for i,row in enumerate(d["branch_pins"])}
    sourceids=[row["source_id"] for row in d["all_original_source_id_crosswalk"]]
    for i,article in enumerate(d["original_articles"]):
        slug=article["slug"]
        branches=[d["branch_pins"][i%9]["branch"]]
        if i==0 or slug=="family-communication-plan":
            branches += [d["branch_pins"][(i+1)%9]["branch"],
                         d["branch_pins"][(i+2)%9]["branch"]]
        for j,branch in enumerate(branches):
            folder=Path(roots[branch])/r.ARTICLE_DIR
            folder.mkdir(parents=True,exist_ok=True)
            index=0 if i==0 else j
            source=sourceids[i]
            (folder/(slug+".body.html")).write_text(
                "<section><p>"+slug+" version "+str(index)+" {{cite:"+source+"}}</p></section>")
            (folder/(slug+".meta.json")).write_text(json.dumps({
                "slug":slug, "status":{"publish":"draft"},
                "safety_review":{"state":"pending"},
                "source_use":{source:"Read cited claim in context"}}))
    # R448 synthetic fork witnesses refer to invented blob SHAs. Create matching
    # synthetic bytes and replace their fake expected SHA pins for this test ONLY.
    for fork in d["original_fork_disputes"]:
        for candidate in fork["variants"]:
            branch=candidate["branch"]
            path=Path(roots[branch])/fork["path"]
            path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():
                if path.suffix==".html":
                    slug=path.name.removesuffix(".body.html")
                    path.write_text("<section><p>Added fork "+slug+" {{cite:"+
                       sourceids[0]+"}}</p></section>")
                    meta=path.with_name(slug+".meta.json")
                    if not meta.exists():
                        meta.write_text(json.dumps({"slug":slug,
                            "source_use":{sourceids[0]:"Scope"}, "status":{"publish":"draft"},
                            "safety_review":{"state":"pending"}}))
                elif path.name.endswith(".meta.json"):
                    slug=path.name.removesuffix(".meta.json")
                    path.write_text(json.dumps({"slug":slug,
                        "source_use":{sourceids[0]:"Scope"},
                        "status":{"publish":"draft"},
                        "safety_review":{"state":"pending"}}))
                    body=path.with_name(slug+".body.html")
                    if not body.exists():
                        body.write_text("<p>Generated metadata fork {{cite:"+sourceids[0]+"}}</p>")
                else:
                    path.write_text(json.dumps({"sources":[{"id":sourceids[0]}]}))
            candidate["git_blob_sha"]=r.git_blob(path.read_bytes())
    # Every generated body/meta candidate is now explicitly in our synthetic
    # candidate inventory, including legitimate repeated Git blobs.
    for article in d["original_articles"]:
        slug=article["slug"]
        article["body_candidate_git_blobs"]=[
            r.git_blob((Path(root)/r.ARTICLE_DIR/(slug+".body.html")).read_bytes())
            for branch,root in sorted(roots.items())
            if (Path(root)/r.ARTICLE_DIR/(slug+".body.html")).exists()]
    return tmp,d,packet,heads,roots

def check(edit=None):
    temp,d,p,h,roots=corpus()
    try:
        if edit:edit(d,p,h,roots)
        return r.audit_original_incidence(d,p,h,roots,test_only=True)
    finally:temp.cleanup()

class SourceIncidentTests(unittest.TestCase):
    def test_structural_synthetic_baseline(self):
        x=check()
        self.assertEqual(x["errors"],[],x["errors"])
        self.assertTrue(x["structural_evidence_pass"])
        self.assertEqual(x["original_article_identities"],35)
        self.assertGreaterEqual(x["candidate_appearances_loaded"],39)
        self.assertEqual(x["release_state"],r.STATE)
        self.assertTrue(x["synthetic_test_only"])
        self.assertFalse(x["qualified_safety_approved"])
        self.assertFalse(x["qd_pass"])
        self.assertFalse(x["publication_allowed"])
        self.assertFalse(x["cms_write_allowed"])
        self.assertIsNone(x["verified_paid_orders"])
        self.assertIsNone(x["net_revenue_per_1000_qualified_sessions"])
    def test_no_authentic_bytes_hard_hold(self):
        tmp,d,p,h,roots=corpus()
        try:
            x=r.audit_original_incidence(d,p,h,roots)
            self.assertIn("AUTHENTIC_R397_AND_R446_BYTES_REQUIRED",x["errors"])
        finally:tmp.cleanup()
    def test_git_blob_known_vector(self):
        self.assertEqual(r.git_blob(b"hello"),"b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")
    def test_duplicate_meta_json_key_denied(self):
        with self.assertRaises(ValueError):
            r.read_json(b'{"slug":"x","slug":"y"}')
    def test_comment_not_visible(self):
        p=r.CitationReader();p.feed("<!-- {{cite:x}} -->")
        self.assertIn("CITATION_IN_COMMENT",p.errors)
        self.assertEqual(p.citations,[])
    def test_visible_repeated_markers_preserved(self):
        p=r.CitationReader();p.feed("<p>{{cite:one}}{{cite:one}}</p>")
        self.assertEqual([x["source_id"] for x in p.citations],["one","one"])
    def test_safe_root_does_not_follow_symlinks(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name)
            (root/"link.txt").symlink_to("/etc/hosts")
            with self.assertRaises(ValueError):r.safe_read(root,"link.txt")

def alter_first(d,p,h,roots,transform):
    slug=d["original_articles"][0]["slug"]
    for branch,root in sorted(roots.items()):
        file=Path(root)/r.ARTICLE_DIR/(slug+".body.html")
        if file.exists():
            file.write_bytes(transform(file.read_bytes()))
            break

def meta_edit(d,p,h,roots,transform):
    slug=d["original_articles"][0]["slug"]
    for branch,root in sorted(roots.items()):
        file=Path(root)/r.ARTICLE_DIR/(slug+".meta.json")
        if file.exists():
            meta=json.loads(file.read_text())
            transform(meta)
            file.write_text(json.dumps(meta))
            break

def body_add(markup):
    return lambda d,p,h,roots:alter_first(d,p,h,lambda body:body+markup.encode())

def change_metadata(fn):
    return lambda d,p,h,roots:meta_edit(d,p,h,fn)

CASES=[
 ("unknown_citation",body_add("<p>{{cite:no-such-source}}</p>"),"CITATION_MISSING_FROM_R397_SOURCE_REGISTER"),
 ("missing_source_scope",body_add("<p>{{cite:source-99}}</p>"),"CITATION_LACKS_META_SOURCE_READING_SCOPE"),
 ("malformed_citation",body_add("<p>{{cite:no-close</p>"),"MALFORMED_CITATION_MARKER"),
 ("malformed_prefix",body_add("<p>{{cite foo}}</p>"),"MALFORMED_CITATION_MARKER"),
 ("html_attribute",body_add('<p title="{{cite:hidden}}">Hello</p>'),"CITATION_IN_HTML_ATTRIBUTE"),
 ("html_script",body_add("<script>{{cite:hidden}}</script>"),"CITATION_IN_HIDDEN_ELEMENT"),
 ("html_style",body_add("<style>{{cite:hidden}}</style>"),"CITATION_IN_HIDDEN_ELEMENT"),
 ("html_template",body_add("<template>{{cite:hidden}}</template>"),"CITATION_IN_HIDDEN_ELEMENT"),
 ("html_noscript",body_add("<noscript>{{cite:hidden}}</noscript>"),"CITATION_IN_HIDDEN_ELEMENT"),
 ("html_svg",body_add("<svg>{{cite:hidden}}</svg>"),"CITATION_IN_HIDDEN_ELEMENT"),
 ("html_comment",body_add("<!-- {{cite:hidden}} -->"),"CITATION_IN_COMMENT"),
 ("html_entity_decimal",body_add("<p>&#123;&#123;cite:x}}</p>"),"ENTITY_ENCODED_CITATION_REQUIRES_REVIEW"),
 ("html_entity_hex",body_add("<p>&#x7b;&#x7b;cite:x}}</p>"),"ENTITY_ENCODED_CITATION_REQUIRES_REVIEW"),
 ("meta_slug",change_metadata(lambda m:m.__setitem__("slug","wrong")),"META_ARTICLE_SLUG_DRIFT"),
 ("meta_published",change_metadata(lambda m:m["status"].__setitem__("publish","published")),"UNAPPROVED_PUBLISH_STATE"),
 ("meta_safety_pass",change_metadata(lambda m:m["safety_review"].__setitem__("state","approved")),"UNAPPROVED_SAFETY_REVIEW"),
 ("meta_safety_live",change_metadata(lambda m:m["safety_review"].__setitem__("state","LIVE")),"UNAPPROVED_SAFETY_REVIEW"),
 ("meta_scope_missing",change_metadata(lambda m:m.__setitem__("source_use",{})),"CITATION_LACKS_META_SOURCE_READING_SCOPE"),
 ("meta_scope_null",change_metadata(lambda m:m.__setitem__("source_use",{"source-2":None})),"INVALID_DECLARED_READING_SCOPE"),
 ("meta_scope_empty",change_metadata(lambda m:m.__setitem__("source_use",{"source-2":" "})),"INVALID_DECLARED_READING_SCOPE"),
 ("meta_scope_list",change_metadata(lambda m:m.__setitem__("source_use",[])),"INVALID_DECLARED_READING_SCOPE"),
 ("meta_source_unknown",change_metadata(lambda m:m["source_use"].__setitem__("not-registered","Text")),"META_SOURCE_USE_NOT_IN_ORIGINAL_REGISTER"),
 ("body_changed",body_add("<p>Additional text</p>"),"ORIGINAL_BODY_APPEARANCE_MULTIPLICITY_DRIFT"),
 ("body_deleted",lambda d,p,h,roots:next(
     (Path(root)/r.ARTICLE_DIR/(d["original_articles"][0]["slug"]+".body.html")).unlink()
     for root in roots.values() if (Path(root)/r.ARTICLE_DIR/(d["original_articles"][0]["slug"]+".body.html")).exists()),"BODY_META_PAIR_INCOMPLETE"),
 ("root_removed",lambda d,p,h,roots:roots.pop(next(iter(roots))),"ALL_NINE_ORIGINAL_BRANCH_ROOTS_REQUIRED"),
 ("root_wrong",lambda d,p,h,roots:roots.__setitem__(next(iter(roots)),"/missing/original/branch"),"ORIGINAL_BODY_APPEARANCE_MULTIPLICITY_DRIFT"),
 ("fork_sha_substitute",lambda d,p,h,roots:d["original_fork_disputes"][0]["variants"][0].__setitem__("git_blob_sha","a"*40),"ORIGINAL_BODY_META_OR_FRAGMENT_FORK_BLOB_DRIFT"),
 ("fork_bytes_delete",lambda d,p,h,roots:(
    Path(roots[d["original_fork_disputes"][0]["variants"][0]["branch"]])/
    d["original_fork_disputes"][0]["path"]).unlink(),"ORIGINAL_BODY_META_OR_FRAGMENT_FORK_BLOB_DRIFT"),
]
for title,edit,expect in CASES:
    def run(self,edit=edit,expect=expect,title=title):
        x=check(edit)
        self.assertTrue(any(expect in message for message in x["errors"]),
            title+": "+str(x["errors"]))
        self.assertEqual(x["release_state"],r.STATE)
        self.assertFalse(x["qd_pass"])
        self.assertFalse(x["publication_allowed"])
    setattr(SourceIncidentTests,"test_mutation_"+title,run)

# Additional distinct parser tests prove visible placement/hidden isolation.
SAMPLES=[
 "<p>Claim {{cite:safe-a}}</p>",
 "<li>Claim {{cite:safe-b}}</li>",
 "<strong>Claim {{cite:safe-c}}</strong>",
 "<blockquote>Claim {{cite:safe-d}}</blockquote>",
 "<td>Claim {{cite:safe-e}}</td>",
 "<th>Claim {{cite:safe-f}}</th>",
 "<figcaption>Claim {{cite:safe-g}}</figcaption>",
 "<span>Claim {{cite:safe-h}}</span>",
 "<h3>Claim {{cite:safe-i}}</h3>",
 "<caption>Claim {{cite:safe-j}}</caption>",
 "<em>Claim {{cite:safe-k}}</em>",
 "<div>Claim {{cite:safe-l}}</div>",
 "<p>Claim {{cite:safe-m}}{{cite:safe-m}}</p>",
 "<p>Claim {{cite:safe-n}} {{cite:safe-o}}</p>",
]
for index,markup in enumerate(SAMPLES):
    def run(self,markup=markup):
        parser=r.CitationReader();parser.feed(markup);parser.close()
        self.assertFalse(parser.errors,parser.errors)
        self.assertGreaterEqual(len(parser.citations),1)
        for occurrence in parser.citations:
            self.assertEqual(len(occurrence["visible_context_sha256"]),64)
    setattr(SourceIncidentTests,"test_visible_placement_"+str(index),run)

if __name__=="__main__":
    unittest.main()

"""R382 read-only citation visibility custody for 35 original Preparedness drafts.
A static check is not a browser, human source verification, or a release PASS.
"""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import argparse, hashlib, json, re, subprocess

MANIFEST="5e7d9a8972872c82b4bc46ac13aab18883d8149a"
REGISTER="b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77"
CITE=re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
INVISIBLE={"script","style","template","head","svg","iframe","object","canvas"}
VOID={"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
BLOCK={"p","li","td","th","blockquote","figcaption","dt","dd","h1","h2","h3","h4"}
ARTICLE=re.compile(r"preparedness/content/articles/([a-z0-9-]+)\.(body\.html|meta\.json)$")

class CitationDOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.frames=[(False,"root","root")]
        self.sequence=0
        self.visible=[]
        self.hidden=[]
        self.nontext=[]
        self.block_text={}
        self.block_cites={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); css=re.sub(r"\s+","",a.get("style") or "").lower()
        masked=(self.frames[-1][0] or tag in INVISIBLE or "hidden" in a or
                "inert" in a or (a.get("aria-hidden") or "").lower()=="true" or
                "display:none" in css or "visibility:hidden" in css)
        if "{{cite:" in (self.get_starttag_text() or ""):
            self.nontext.append("ATTRIBUTE")
        key=self.frames[-1][1]
        if tag in BLOCK:
            self.sequence+=1; key=str(self.sequence)
        if tag not in VOID:
            self.frames.append((masked,key,tag))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID: self.frames.pop()
    def handle_endtag(self,tag):
        for i in range(len(self.frames)-1,0,-1):
            if self.frames[i][2]==tag:
                del self.frames[i:]; break
    def handle_data(self,data):
        found=CITE.findall(data)
        if self.frames[-1][0]:
            self.hidden+=found
        else:
            self.visible+=found
            key=self.frames[-1][1]
            self.block_text[key]=self.block_text.get(key,"")+CITE.sub("",data)
            self.block_cites.setdefault(key,[]).extend(found)
    def handle_comment(self,data):
        if "{{cite:" in data: self.nontext.append("COMMENT")
    def handle_decl(self,data):
        if "{{cite:" in data: self.nontext.append("DECLARATION")

def examine(body:bytes,metadata:dict,source_ids:set[str])->dict:
    problems=[]; notes=["CSS_BROWSER_PRINT_SCREENREADER_UNVERIFIED"]
    try: html=body.decode("utf-8")
    except (AttributeError,UnicodeError): html=""; problems.append("NON_UTF8_BODY")
    if not isinstance(metadata,dict):
        metadata={}; problems.append("INVALID_METADATA")
    st=metadata.get("status")
    if not isinstance(st,dict) or st.get("publish")!="draft":
        problems.append("NOT_PRIVATE_DRAFT")
    sr=metadata.get("safety_review")
    if not isinstance(sr,dict) or sr.get("state") not in {"pending","approved","not-required"}:
        problems.append("INVALID_HISTORICAL_SAFETY_STATE"); sr={}
    if sr.get("state")=="approved":
        notes.append("FOUNDER_LABEL_NOT_INDEPENDENT_QD")
    parser=CitationDOM()
    try: parser.feed(html); parser.close()
    except (AssertionError,ValueError): problems.append("HTML_PARSER_ERROR")
    all_ids=CITE.findall(html)
    if html.count("{{cite:")!=len(all_ids):
        problems.append("MALFORMED_CITATION_TOKEN")
    if parser.hidden: problems.append("INVISIBLE_CITATION")
    if parser.nontext: problems.append("NON_TEXT_CITATION")
    if len(parser.visible)+len(parser.hidden)!=len(all_ids):
        problems.append("CITATION_DISAPPEARS_FROM_TEXT")
    scopes=metadata.get("source_use")
    if not isinstance(scopes,dict):
        scopes={}; problems.append("SOURCE_USE_NOT_OBJECT")
    for sid in sorted(set(all_ids)):
        if sid not in source_ids: problems.append("UNRESOLVED_ID:"+sid)
        if not isinstance(scopes.get(sid),str) or not scopes[sid].strip():
            problems.append("MISSING_READING_SCOPE:"+sid)
    for sid in sorted(set(scopes)-set(all_ids)):
        notes.append("UNUSED_SCOPE:"+sid)
    for key,ids in parser.block_cites.items():
        if len(parser.block_text.get(key,"").strip())<18:
            notes.append("CITATION_WITH_MINIMAL_CLAIM:"+key)
        if len(ids)!=len(set(ids)):
            notes.append("REPEATED_SOURCE_SAME_BLOCK:"+key)
    return dict(status="INVALID_HARD_HOLD" if problems else "STATIC_REVIEW_HARD_HOLD",
                errors=sorted(set(problems)),warnings=sorted(set(notes)),
                raw=len(all_ids),visible=len(parser.visible),hidden=len(parser.hidden),
                original_safety_state=sr.get("state"),publication_approved=False,
                qualified_safety_approved=False,verified_human_source=False)

def git_blob(root:Path,sha:str)->bytes:
    if not re.fullmatch(r"[0-9a-f]{40}",sha): raise ValueError("invalid git object")
    b=subprocess.run(["git","-C",str(root),"cat-file","blob",sha],
                     check=True,capture_output=True,timeout=20).stdout
    if hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b,usedforsecurity=False).hexdigest()!=sha:
        raise ValueError("git blob mismatch")
    return b

def audit_originals(manifest,register,read):
    errors=[]; reports=[]
    if not isinstance(manifest,dict) or not isinstance(register,dict):
        return dict(status="INVALID_HARD_HOLD",errors=["UNTRUSTED_INPUT"],publication_approved=False)
    pins=manifest.get("branch_pins",[])
    if (manifest.get("schema_version")!=1 or manifest.get("article_count")!=35 or
        manifest.get("conflict_count")!=9 or manifest.get("release_state")!="DRAFT_HARD_HOLD" or
        not isinstance(pins,list) or len(pins)!=9 or len({p.get("branch") for p in pins})!=9):
        errors.append("ORIGINAL_MANIFEST_CUSTODY_DRIFT")
    objects=manifest.get("objects",[])
    by_path={o.get("path"):o for o in objects if isinstance(o,dict)}
    conflicts=sum(len({v.get("sha") for v in o.get("variants",[])})>1 for o in objects)
    if len(objects)!=77 or len(by_path)!=77 or conflicts!=9:
        errors.append("ORIGINAL_77_OBJECT_NINE_FORK_CUSTODY_DRIFT")
    bodies={k[:-10]:v for k,v in by_path.items() if isinstance(k,str) and k.endswith(".body.html")}
    metas={k[:-10]:v for k,v in by_path.items() if isinstance(k,str) and k.endswith(".meta.json")}
    if len(bodies)!=35 or set(bodies)!=set(metas):
        errors.append("ORIGINAL_35_BODY_METADATA_PAIRS_DRIFT")
    ids={s.get("id") for s in register.get("sources",[]) if isinstance(s,dict)}
    for path,obj in by_path.items():
        variants=obj.get("variants",[])
        if obj.get("selected_sha") is not None:
            errors.append("UNREVIEWED_VERSION_SELECTED:"+path)
        if isinstance(path,str) and path.startswith("preparedness/sources/fragments/"):
            for v in variants:
                try: ids.update(x["id"] for x in json.loads(read(v["sha"]))["sources"])
                except (ValueError,KeyError,TypeError): errors.append("FRAGMENT_UNREADABLE:"+path)
    for name,body_obj in sorted(bodies.items()):
        metas_by_branch={v["branch"]:v for v in metas[name]["variants"]}
        if {v["branch"] for v in body_obj["variants"]}!=set(metas_by_branch):
            errors.append("BODY_METADATA_FORK_MISMATCH:"+name)
        for b in body_obj["variants"]:
            try:
                meta_v=metas_by_branch[b["branch"]]
                meta=json.loads(read(meta_v["sha"]))
                result=examine(read(b["sha"]),meta,ids)
                if meta.get("slug")!=name.rsplit("/",1)[-1]:
                    errors.append("ARTICLE_SLUG_DRIFT:"+name)
                result.update(slug=meta.get("slug"),branch=b["branch"],body_sha=b["sha"],meta_sha=meta_v["sha"])
                reports.append(result)
            except (ValueError,KeyError,TypeError,UnicodeError):
                errors.append("ORIGINAL_VARIANT_UNREADABLE:"+name)
    if len(reports)<35: errors.append("MISSING_ORIGINAL_VARIANTS")
    invalid=sum(bool(r["errors"]) for r in reports)
    return dict(status="INVALID_HARD_HOLD" if errors or invalid else "STATIC_REVIEW_HARD_HOLD",
                errors=errors,original_articles=len(bodies),variants=len(reports),
                invalid_variants=invalid,per_variant=reports,
                publication_approved=False,qualified_safety_approved=False)

def main():
    p=argparse.ArgumentParser();p.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[2])
    root=p.parse_args().repo
    try:
        m=json.loads(git_blob(root,MANIFEST));r=json.loads(git_blob(root,REGISTER))
        result=audit_originals(m,r,lambda sha:git_blob(root,sha))
    except (OSError,ValueError,TypeError,KeyError,subprocess.SubprocessError):
        result=dict(status="INVALID_HARD_HOLD",errors=["NATIVE_GIT_OBJECTS_UNAVAILABLE"],
                    publication_approved=False,qualified_safety_approved=False)
    print(json.dumps(result,indent=2,sort_keys=True));return 2

if __name__=="__main__":raise SystemExit(main())

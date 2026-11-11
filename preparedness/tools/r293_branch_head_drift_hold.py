#!/usr/bin/env python3
"""R293 live-branch parity review. Never approval or a live GitHub poll."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
HOLD="DRAFT_HARD_HOLD"
INVALID="INVALID_HARD_HOLD"
FROZEN={
"start":("claude/prep-start-bbfeb8","2122d856fce9f64887c16df3d52e64be9f59a55b"),
"shelter":("claude/prep-shelter-5e1e0e","5daeaf2dd5ab71806a6b73c91edfb1d8df5da976"),
"food":("claude/prep-food-ccdc55","e9cd7766dac59d47ab467d8945269b9146c2aef5"),
"health":("claude/prep-health-837444","d2212d0ca0750817d3929865d3069835980faf20"),
"hist-food":("claude/prep-hist-food-b81f19","2acf65ca3efa9b4b5db7976f379b9ea693be43a4"),
"hist-home":("claude/prep-hist-home-0e0e38","f654e600f89c321a480dd8f055be4d13d0673490"),
"hist-field":("claude/prep-hist-field-9db767","a5ce8a62f168db05c95232e3eb385dccd0d19e7f")}
def need(ok,why):
 if not ok: raise ValueError(why)
def no_dupes(pairs):
 obj={}
 for k,v in pairs:
  need(k not in obj,"duplicate key")
  obj[k]=v
 return obj
def load(raw):
 return json.loads(raw,object_pairs_hook=no_dupes,
   parse_constant=lambda v: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
def evaluate(snapshot):
 need(type(snapshot) is dict and set(snapshot)=={"schema","captured_on_utc","repository","clusters"},"snapshot structure")
 need(snapshot["schema"]=="fv-preparedness-r293-branch-drift-v1","schema")
 need(snapshot["repository"]=="finalvestigestudios/final-vestige-site-layer","repository")
 need(bool(re.fullmatch(r"20\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ",snapshot["captured_on_utc"])),"timestamp")
 need(type(snapshot["clusters"]) is dict and set(snapshot["clusters"])==set(FROZEN),"seven clusters")
 changed=[]; paths=[]; articles=set()
 for key in sorted(FROZEN):
  r=snapshot["clusters"][key]; ref,freeze=FROZEN[key]
  need(type(r) is dict and set(r)=={"branch","frozen","head","status","ahead","behind","paths"},"record keys")
  need(r["branch"]==ref and r["frozen"]==freeze,"frozen provenance")
  need(type(r["head"]) is str and re.fullmatch(r"[0-9a-f]{40}",r["head"]),"head sha")
  need(type(r["ahead"]) is int and type(r["behind"]) is int and 0<=r["ahead"]<=100 and 0<=r["behind"]<=100,"compare counts")
  need(r["status"] in ("identical","ahead","behind","diverged"),"status")
  need(type(r["paths"]) is list and len(r["paths"])<100,"path census")
  same=(r["head"]==freeze)
  need(same==(r["status"]=="identical") and
       same==(r["ahead"]==0 and r["behind"]==0 and not r["paths"]),"identity contradiction")
  if not same:
   need((r["status"]=="ahead" and r["ahead"]>0 and r["behind"]==0) or
        (r["status"]=="behind" and r["behind"]>0 and r["ahead"]==0) or
        (r["status"]=="diverged" and r["ahead"]>0 and r["behind"]>0),"comparison inconsistent")
   need(bool(r["paths"]),"drift without files")
   changed.append(key)
  need(len(r["paths"])==len(set(r["paths"])),"duplicate paths")
  for p in r["paths"]:
   need(type(p) is str and len(p)<250 and p.startswith("preparedness/") and
        "/../" not in p and "/./" not in p and "\\" not in p and "%" not in p and
        len(p.split("/"))>=3,"unsafe path")
   paths.append({"cluster":key,"path":p})
   if "/content/articles/" in p and (p.endswith(".body.html") or p.endswith(".meta.json")):
    articles.add(p.split("/")[-1].split(".body.html")[0].split(".meta.json")[0])
 return {"state":HOLD,"publication_authorized":False,"independent_qd_pass":False,
         "medical_safety_verified":False,"privacy_approved":False,
         "github_currentness_verified":False,"all_branches_identical":not changed,
         "drifted_clusters":changed,"changed_file_count":len(paths),
         "affected_article_slugs":sorted(articles),"changed_paths":paths,
         "word_press_draft_exports_verified":False,"full_native_build_verified":False}
def audit(root):
 try:
  root=Path(root)
  need(root.is_dir() and not root.is_symlink(),"unsafe root")
  p=root/"audits/r293_live_contributor_branch_crosswalk_UNAPPROVED.json"
  need(p.is_file() and not p.is_symlink(),"review snapshot unavailable")
  return evaluate(load(p.read_text(encoding="utf-8")))
 except (ValueError,OSError,UnicodeError,TypeError,KeyError) as e:
  return {"state":INVALID,"publication_authorized":False,
          "independent_qd_pass":False,"medical_safety_verified":False,
          "privacy_approved":False,"error":str(e)}
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
 r=a.parse_args();v=audit(r.root)
 print(json.dumps(v,indent=2,sort_keys=True))
 raise SystemExit(0 if v["state"]==HOLD else 3)

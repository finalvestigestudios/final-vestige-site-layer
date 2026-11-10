#!/usr/bin/env python3
"""R264/R265 offline wallet-card face/notice custody. NEVER privacy approval."""
from __future__ import annotations
import hashlib
import re
from html.parser import HTMLParser

SCHEMA="fv-preparedness-r264-minimal-wallet-card-draft-v1"
HOLD="DRAFT_HARD_HOLD"
ORIGINAL_PATH="content/tools/family-reunification-card.body.html"
DRAFT_PATH="audits/r264_minimal_wallet_card_REVIEW_ONLY.html"
ORIGINAL_BLOB="be8698ac5d020476ff649d85813810e2000c6f98"
REQUIRED_FALSE=("privacy_certified","medical_safety_verified","independent_qd_pass",
                "source_review_approved","merchant_approved","release_authorized","public_published")
NOTICES=(
 "Privacy: This card may be lost or photographed. Do not write child names, school details, home addresses, passwords, medical information or access codes.",
 "Privacy: A finder can read this card. Carry only non-sensitive contact details and review before sharing."
)
FIELDS=("Out-of-area contact:","Telephone:","Backup contact:","Backup telephone:","Plan reviewed:")

def git_blob(b:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

class Parser(HTMLParser):
    """Tag-and-depth structural check; no browser behavior is claimed."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[];self.card=0;self.faces=[];self.notes=[];self.note_owners=[];self.active_note=False
        self.css="";self.text=[];self.extra_notice=0
    def handle_starttag(self,tag,attrs):
        if tag not in ("section","div","p","h2","style"):raise ValueError("R264 unexpected/active tag")
        d=dict(attrs)
        if len(d)!=len(attrs) or any(k not in ("class","aria-label","role") or v is None for k,v in attrs):
            raise ValueError("R264 unexpected, duplicate or executable attributes")
        classes=d.get("class","").split()
        if "pa-foldcard" in classes:
            if tag!="div" or classes!=["pa-foldcard"] or self.card:raise ValueError("R264 card structure")
            self.card=1
        if "pa-face" in classes:
            if tag!="section" or classes!=["pa-face"] or not self.stack or self.stack[-1][1]!=["pa-foldcard"]:
                raise ValueError("R264 cutout face nesting")
            self.faces.append(d.get("aria-label",""))
        if "pa-privacy" in classes:
            if tag!="p" or classes!=["pa-privacy"]:raise ValueError("R264 privacy prose structure")
            owners=[e[2].get("aria-label") for e in self.stack if "pa-face" in e[1]]
            if len(owners)!=1:self.extra_notice+=1
            else:self.note_owners.append(owners[0])
            self.notes.append("")
            self.active_note=True
        self.stack.append((tag,classes,d))
    def handle_endtag(self,tag):
        if not self.stack or self.stack[-1][0]!=tag:raise ValueError("R264 unbalanced tags")
        if "pa-privacy" in self.stack[-1][1]:self.active_note=False
        self.stack.pop()
    def handle_data(self,s):
        if self.stack and self.stack[-1][0]=="style":self.css+=s
        else:
            self.text.append(s)
            if self.active_note and self.notes:self.notes[-1]+=s
    def handle_startendtag(self,tag,attrs):raise ValueError("R264 self-closing tag")
    def handle_comment(self,s):
        if "Unapproved R264 source-only review concept" not in s:
            raise ValueError("R264 unexpected comment")
    def unknown_decl(self,s):raise ValueError("R264 unknown declaration")

def inspect(original:bytes,draft:bytes,witness:dict,*,expected_original_blob:str=ORIGINAL_BLOB)->dict:
    if any(type(x) is not bytes or not x or b"\0" in x for x in (original,draft)):
        raise ValueError("R264 invalid byte inputs")
    if len(original)>3_000_000 or len(draft)>100_000:raise ValueError("R264 source size")
    if not re.fullmatch("[0-9a-f]{40}",expected_original_blob):raise ValueError("R264 source pin")
    if git_blob(original)!=expected_original_blob:raise ValueError("R264 original drift")
    if (type(witness) is not dict or witness.get("state")!=HOLD
        or witness.get("original_git_blob")!=expected_original_blob
        or witness.get("wallet_cutout_has_privacy_warning") is not False
        or witness.get("printed_card_privacy_resolved") is not False
        or witness.get("requires_editorial_resolution_before_publication") is not True
        or any(witness.get(k) is not False for k in REQUIRED_FALSE)):
        raise ValueError("R264 prior R263 negative safety state changed")
    s=draft.decode("utf-8","strict")
    if any(x in s.lower() for x in ("<script","<form","{{cite:","{{link:","http:","https:","utm_")):
        raise ValueError("R264 external, commercial or source/citation scope")
    p=Parser();p.feed(s);p.close()
    if p.stack or p.card!=1 or p.faces!=["Front","Back"] or p.notes!=list(NOTICES)
        or p.note_owners!=["Front","Back"] or p.extra_notice:
        raise ValueError("R264 on-card notices or two-face structure")
    if s.count('class="pa-privacy"')!=2 or s.count('class="pa-write"')!=len(FIELDS):
        raise ValueError("R264 unexpected privacy/field count")
    if any(s.count('<p class="pa-write">'+f+' __________________</p>')!=1 for f in FIELDS):
        raise ValueError("R264 field populated/renamed/omitted")
    if (s.count('class="pa-editor-note"')!=2 or "UNAPPROVED REVIEW CONCEPT" not in s
        or "Do not distribute" not in s):raise ValueError("R264 reviewer-only notice")
    css=re.sub(r"\s+"," ",p.css.lower())
    if (s.count("<style>")!=1 or "@media print" not in css
        or p.css.count("width:7in")!=2 or p.css.count("min-height:2.125in")!=4
        or any(x in css for x in ("overflow:","visibility:","opacity:","display:none",
                                  "display: none","@import","url(","content:","position:"))):
        raise ValueError("R264 print source/CSS hold")
    return {
      "schema":SCHEMA,"state":HOLD,"original_git_blob":expected_original_blob,
      "candidate_git_blob":git_blob(draft),"cutout_faces":2,
      "cautions_structurally_inside_both_faces":True,
      "r265_notice_owners_exactly_front_and_back":True,
      "r265_cutout_faces_are_direct_siblings":True,
      "original_source_unchanged":True,"citation_and_routes_unchanged":True,
      "real_browser_and_cutout_qa_completed":False,"qualified_child_privacy_review_completed":False,
      "safe_to_carry_certified":False,"ready_for_wordpress":False,
      "human_review_required":True,**{k:False for k in REQUIRED_FALSE},
    }

def audit(root,safe_read,r263_receipt):
    return inspect(safe_read(root,ORIGINAL_PATH),safe_read(root,DRAFT_PATH),r263_receipt)

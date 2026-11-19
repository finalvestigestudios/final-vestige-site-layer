#!/usr/bin/env python3
"""FV safe cloud API relay. Fixed fictional pilot only; no public publishing."""
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO="finalvestigestudios/final-vestige-site-layer"
ISSUE=3090
CAMPAIGN="fv_relay_handshake_2026_11"
SOURCE="FV-20261119-safe-claude-grok-draft-01"
SMOKE="FV-20261119-cloud-smoke-01"
CLAUDE="FV-20261119-cloud-claude-01"
GROK="FV-20261119-cloud-grok-01"
QA="FV-20261119-cloud-qa-01"
BASE=f"https://api.github.com/repos/{REPO}"
FENCE=chr(96)*3

def flag(name):
    return os.getenv(name,"").lower()=="true"

def allowed(role):
    return flag("FV_PAID_CALLS_ALLOWED") and flag("FV_CLOUD_RELAY_ENABLED") and flag("FV_"+role+"_API_ENABLED")

def github(method,path,data=None):
    if not path.startswith("/issues/3090/comments"):
        raise RuntimeError("Only issue 3090 comments allowed")
    token=os.getenv("GITHUB_TOKEN")
    if not token: raise RuntimeError("Missing GitHub Actions token")
    headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
             "X-GitHub-Api-Version":"2022-11-28","User-Agent":"fv-cloud-relay"}
    raw=json.dumps(data).encode() if data is not None else None
    if raw is not None: headers["Content-Type"]="application/json"
    req=urllib.request.Request(BASE+path,data=raw,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=15) as response:
            return json.loads(response.read(250000).decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError("GitHub returned HTTP "+str(e.code)) from None

def get_comments():
    result=[]
    for page in range(1,8):
        batch=github("GET",f"/issues/3090/comments?per_page=100&page={page}")
        if not isinstance(batch,list): raise RuntimeError("Unexpected GitHub response")
        result+=batch
        if len(batch)<100: return result
    raise RuntimeError("Too many comments; reconcile before processing")

def emit(body):
    return github("POST","/issues/3090/comments",{"body":body})

def author(c):
    return (c.get("user") or {}).get("login","")

def parsed(c):
    body=c.get("body") or ""
    if not isinstance(body,str) or len(body)>15000: return []
    records=[]
    for block in re.findall(r"["+chr(96)+r"]{3}json\s*([\s\S]*?)["+chr(96)+r"]{3}",body,re.I):
        try: value=json.loads(block)
        except ValueError: continue
        if isinstance(value,dict) and value.get("schema")=="fv-handoff-v1" and value.get("campaign_id")==CAMPAIGN:
            records.append(value)
    return records

def has_source(comments):
    return any(author(c)=="finalvestigestudios" and any(
        e.get("event_id")==SOURCE and e.get("actor")=="chatgpt" and
        e.get("action")=="CREATE" and e.get("status")=="READY_FOR_WORK"
        for e in parsed(c)) for c in comments)

def marker(comments,needle):
    return any(needle in (c.get("body") or "") for c in comments)

def claude_copy(comments):
    for c in comments:
        if author(c)!="github-actions[bot]": continue
        if not any(e.get("event_id")==CLAUDE and e.get("actor")=="claude" and e.get("status")=="READY_FOR_QA" for e in parsed(c)): continue
        m=re.search(r"FICTIONAL TEST COPY\n\n([^\n]{12,750})",c.get("body") or "")
        if m: return m.group(1)
    return None

def qa_ready(comments):
    return any(author(c)=="finalvestigestudios" and any(
        e.get("event_id")==QA and e.get("actor")=="chatgpt" and
        e.get("action")=="QA_RESULT" and e.get("status")=="READY_FOR_APPROVAL"
        and e.get("next_owner")=="grok" for e in parsed(c))
        for c in comments)

def stage(comments):
    if not has_source(comments): return "NO_TRUSTED_SOURCE"
    if not marker(comments,"FV_CLOUD_OUTPUT "+CLAUDE):
        return "CLAUDE_CLAIMED" if marker(comments,"FV_CLOUD_CLAIM "+CLAUDE) else "CLAUDE_PENDING"
    if not qa_ready(comments): return "QA_PENDING"
    if not marker(comments,"FV_CLOUD_OUTPUT "+GROK):
        return "GROK_CLAIMED" if marker(comments,"FV_CLOUD_CLAIM "+GROK) else "GROK_PENDING"
    return "DRAFT_COMPLETE"

def event(role,eventid,action,status,next_owner):
    return {"schema":"fv-handoff-v1","event_id":eventid,"campaign_id":CAMPAIGN,
            "actor":role,"action":action,"status":status,
            "updated_at_utc":dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
            "next_owner":next_owner,"asset_ids":[],"platforms":[],
            "rights_check":"not_applicable","source_check":"not_applicable",
            "approval_check":"not_applicable",
            "evidence_urls":[f"https://github.com/{REPO}/issues/{ISSUE}"]}

def call_model(url,headers,payload):
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),
      headers={**headers,"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=35) as response:
            value=json.loads(response.read(180000).decode())
            if not isinstance(value,dict): raise RuntimeError("Provider returned non-object")
            return value
    except urllib.error.HTTPError as e:
        raise RuntimeError("Model API returned HTTP "+str(e.code)) from None

def safe_copy(text):
    text=re.sub(r"\s+"," ",text or "").strip()
    if not 12<=len(text)<=750 or "http" in text.lower() or FENCE in text or "@finalvestige" in text.lower():
        raise RuntimeError("Generated text failed safe fictional-copy check")
    return text

def generate(role,claude_text=None):
    if role=="CLAUDE":
        key=os.environ["FV_ANTHROPIC_API_KEY"]
        model=os.environ["FV_CLAUDE_MODEL"]
        response=call_model("https://api.anthropic.com/v1/messages",
            {"x-api-key":key,"anthropic-version":"2026-10-21"},
            {"model":model,"max_tokens":160,"messages":[
                {"role":"user","content":"Write exactly two original sentences of fictional lighthouse teaser copy. A keeper finds a sealed envelope dated 1900 behind a lens housing. Fiction only, not historical evidence. No links or calls to action. Return just those two sentences."}]})
        return safe_copy(" ".join(x.get("text","") for x in response.get("content",[]) if isinstance(x,dict) and x.get("type")=="text"))
    key=os.environ["FV_XAI_API_KEY"]
    model=os.environ["FV_GROK_MODEL"]
    response=call_model("https://api.x.ai/v1/responses",
        {"Authorization":"Bearer "+key},
        {"model":model,"max_output_tokens":130,"store":False,
         "input":"Rewrite this fictional teaser as ONE intriguing sentence for an UNPUBLISHED social draft. No history claim, hashtag, link, or instruction: "+(claude_text or "")})
    raw=response.get("output_text","")
    if not raw:
        raw=" ".join(p.get("text","") for item in response.get("output",[]) if isinstance(item,dict)
           for p in item.get("content",[]) if isinstance(p,dict) and p.get("type")=="output_text")
    return safe_copy(raw)

def scheduled():
    comments=get_comments()
    current=stage(comments)
    print("FV_CLOUD_STAGE="+current)
    if current not in ("CLAUDE_PENDING","GROK_PENDING"): return
    role="CLAUDE" if current=="CLAUDE_PENDING" else "GROK"
    if not allowed(role):
        print("PAID_API_DISABLED: three explicit true gates required for "+role)
        return
    secret=("FV_ANTHROPIC_API_KEY" if role=="CLAUDE" else "FV_XAI_API_KEY")
    model=("FV_CLAUDE_MODEL" if role=="CLAUDE" else "FV_GROK_MODEL")
    if not os.getenv(secret) or not os.getenv(model):
        raise RuntimeError("Provider key/model not configured; no request attempted")
    previous=claude_copy(comments) if role=="GROK" else None
    if role=="GROK" and not previous: raise RuntimeError("Claude evidence not found")
    ident=CLAUDE if role=="CLAUDE" else GROK
    # One claim before any billable request; retries permanently held until reviewed.
    emit("**FV_CLOUD_CLAIM "+ident+"**\n\nSingle bounded API attempt claimed by github-actions[bot]. No automatic retry if interrupted.")
    try: result=generate(role,previous)
    except Exception:
        emit("**FV_CLOUD_HOLD "+ident+"**\n\nProvider call or output validation failed. Manual review required; never retry automatically.")
        raise
    ev=(event("claude",CLAUDE,"UPDATE","READY_FOR_QA","chatgpt") if role=="CLAUDE"
        else event("grok",GROK,"DRAFT_READY","READY_FOR_APPROVAL","chatgpt"))
    emit("**FV_CLOUD_OUTPUT "+ident+"**\n\nAPI-originated "+role+" fictional draft (NOT the desktop assistant).\n\nFICTIONAL TEST COPY\n\n"
         +result+"\n\n"+FENCE+"json\n"+json.dumps(ev,indent=2)+"\n"+FENCE+
         "\n\nNo media generated or social platform publication performed.")

def smoke():
    path=os.getenv("GITHUB_EVENT_PATH","")
    if not path: return
    try: payload=json.loads(Path(path).read_text())
    except (OSError,ValueError): return
    if payload.get("issue",{}).get("number")!=3090: return
    c=payload.get("comment") or {}
    if author(c)!="finalvestigestudios": return
    if not any(e.get("event_id")==SMOKE and e.get("action")=="HELLO" and e.get("actor")=="chatgpt" for e in parsed(c)): return
    previous=get_comments()
    mark="FV_CLOUD_RELAY_SMOKE "+SMOKE
    if marker(previous,mark): return
    emit("**"+mark+"**\n\nVerified automated cloud workflow execution against the safe fixed event. NO model API request, charge, social post, or newsletter send.\n\nSource: "+c.get("html_url",""))

def main():
    if os.getenv("GITHUB_REPOSITORY",REPO)!=REPO: raise RuntimeError("Wrong repository")
    if os.getenv("GITHUB_EVENT_NAME","")=="issue_comment": smoke()
    else: scheduled()
    print("FV_CLOUD_RELAY_RUN_COMPLETE")

if __name__=="__main__":
    try: main()
    except Exception as exc:
        print("FV_CLOUD_RELAY_ERROR="+str(exc),file=sys.stderr)
        sys.exit(1)

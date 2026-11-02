"""Dispatch R60: fail-closed, offline fact/permission consistency check. No I/O beyond this JSON."""
from __future__ import annotations
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent

def check(d: dict) -> list[str]:
    errors=[]
    def require(ok, message):
        if not ok: errors.append(message)
    require(d.get("purpose")=="SOURCE_REVIEW_NOT_SEND_AUTHORIZATION","scope changed")
    c=d.get("campaign",{})
    require(c.get("status")=="HOLD_UNSENT","campaign hold removed")
    require(c.get("founder_final_send_permission") is False,"founder permission fabricated")
    m=c.get("mix",{})
    require(m.get("editorial")==[1,2,4,6] and m.get("commercial")==[3,5],"original 4:2 mix altered")
    w=d.get("wordpress",{})
    require(w.get("auto_new_posts") is False,"new-post sending change detected")
    require(w.get("format")=="excerpt","excerpt assumption changed")
    require(w.get("subscriber_counts")=={"total":2,"confirmed":2,"unconfirmed":2},"refresh counts privately")
    for flag in ("welcome_received_verified","recipient_eligibility_verified","real_email_preview_verified",
                 "mailing_address_verified","unsubscribe_in_received_email_verified"):
        require(w.get(flag) is False,"unverified WordPress evidence changed: "+flag)
    o=d.get("offers",{})
    require(set(o)=={"zen12","total_focus"},"named offers changed")
    for name,num in (("zen12",3),("total_focus",5)):
        x=o.get(name,{})
        require(x.get("issue")==num,name+": wrong issue number")
        require(x.get("seller_url","").startswith("https://"),name+": named seller URL missing")
        require(x.get("readiness")=="HOLD_MERCHANT",name+": merchant hold changed")
        for flag in ("price_verified_at_transaction","partner_approved","email_promotion_approved"):
            require(x.get(flag) is False,name+": unverified "+flag)
        for flag in ("earning_url","live_approved_guide"):
            require(x.get(flag) is None,name+": activated "+flag)
    for k,v in d.get("constraints",{}).items():
        require(v is True,"safety constraint disabled: "+k)
    require(len(d.get("constraints",{}))==8,"safety constraints missing")
    return sorted(set(errors))

def decision(d: dict) -> dict:
    return {"campaign":"HOLD_UNSENT","commercial":"HOLD_MERCHANT","review_errors":check(d),
            "static_review_only":True,"send_authorized":False}

if __name__=="__main__":
    data=json.loads((ROOT/"evidence.json").read_text(encoding="utf-8"))
    print(json.dumps(decision(data),indent=2))
    raise SystemExit(1 if check(data) else 0)

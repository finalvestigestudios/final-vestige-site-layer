#!/usr/bin/env python3
"""R451 local-only adversarial checks, no external calls or browser staging claims."""
from pathlib import Path
import importlib.util, tempfile, shutil, json
spec=importlib.util.spec_from_file_location("gate",Path(__file__).with_name("release_guard.py"))
gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
checks=[]

def check(name,condition):
    if not condition:raise AssertionError(name)
    checks.append(name)

rows=gate.source_contract()
check("four pinned NASA records",len(rows)==4)
check("primary report limitation", "ignition source" in rows[1]["not_supported"])
check("later retrospective distinct",rows[3]["date"]=="2018-02-14")
with tempfile.TemporaryDirectory() as td:
    p=Path(td)/"mutated.json"
    for mutation in (b" ",b"\n",b"\n{}"):
        p.write_bytes(gate.SOURCE.read_bytes()+mutation)
        try:gate.source_contract(p)
        except ValueError:checks.append("source-byte-mutation blocked")
        else:raise AssertionError("mutated manifest accepted")
check("missing unpublished Grok asset rejected",bool(gate.creator_contract({"asset_id":"proposed"})))
check("nonplatform URL rejected", "authentic allowed platform URL" in gate.creator_contract({"platform_post_url":"https://example.com/post"}))
check("missing seller rejected",bool(gate.commerce_contract({})))
check("not enabling checkout from QA", "commercial CTA cannot be enabled from QA" in gate.commerce_contract({"commercial_cta_enabled":True}))
result=gate.run()
check("still hard hold",result["release"]=="HARD_HOLD")
check("no speculative revenue",result["net_revenue_per_1000_qualified_humans"] is None)
check("no fake axe",result["axe_core"]=="NOT_RUN")
check("source custody preserved",result["source_manifest_sha256"]==gate.PIN)
print(json.dumps({"status":"PASS","assertions":len(checks),"checks":checks,"actual_staging":"NOT_RUN","merchant_revenue":"NOT_VERIFIED"},sort_keys=True))

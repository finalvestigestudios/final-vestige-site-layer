#!/usr/bin/env python3
"""Throttled mobile load trace (Chrome DevTools throttling: ~Slow 4G + 4x CPU), N runs, medians.

Records FCP, every LCP candidate (element + time), font load timing and blocking resources.
LAB ONLY. When pointed at the local gzip/cache proxy it is a front-end measurement, not production.
  python perf_trace.py --url http://127.0.0.1:9401/ --runs 5 [--out file.json]
"""
import argparse, json, statistics as st
from playwright.sync_api import sync_playwright

OBS = """()=>{window.__lcp=[];window.__fcp=null;window.__ls=0;
new PerformanceObserver(l=>{for(const e of l.getEntries()){window.__lcp.push({t:Math.round(e.startTime),el:(e.element?e.element.tagName+'.'+(e.element.className||'').toString().slice(0,40):null),size:e.size,url:e.url||null})}}).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()){if(e.name==='first-contentful-paint')window.__fcp=Math.round(e.startTime)}}).observe({type:'paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()){if(!e.hadRecentInput)window.__ls+=e.value}}).observe({type:'layout-shift',buffered:true});
window.__lt=[];try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lt.push(Math.round(e.duration))}).observe({type:'longtask',buffered:true})}catch(e){}}"""


def run(b, url, w, h, dpr):
    ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=dpr, is_mobile=True, has_touch=True)
    pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg)
    cdp.send("Network.enable"); cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
    cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
    pg.add_init_script("(" + OBS + ")()")
    reqs = []
    cdp.on("Network.loadingFinished", lambda e: reqs.append(e["encodedDataLength"]))
    pg.goto(url, wait_until="load", timeout=120000)
    pg.wait_for_timeout(2500)
    r = pg.evaluate("({lcp:window.__lcp,fcp:window.__fcp,cls:window.__ls,lt:window.__lt})")
    fonts = pg.evaluate("performance.getEntriesByType('resource').filter(e=>/woff2?|font/i.test(e.name)).map(e=>({n:e.name.split('/').pop().slice(0,30),start:Math.round(e.startTime),end:Math.round(e.responseEnd),kb:Math.round(e.transferSize/1024)}))")
    r["fonts"] = fonts; r["transfer_kb"] = round(sum(reqs) / 1024)
    r["lcp_final"] = r["lcp"][-1] if r["lcp"] else None
    ctx.close()
    return r


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--url", default="http://127.0.0.1:9401/"); ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--out"); ap.add_argument("--w", type=int, default=390); ap.add_argument("--h", type=int, default=844); a = ap.parse_args()
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        run(b, a.url, a.w, a.h, 2.625)  # warm proxy cache
        rs = [run(b, a.url, a.w, a.h, 2.625) for _ in range(a.runs)]
        b.close()
    lcps = [r["lcp_final"]["t"] for r in rs if r["lcp_final"]]
    S = {"runs": a.runs, "LCP_ms_median": st.median(lcps), "LCP_ms_all": lcps, "FCP_ms_median": st.median(r["fcp"] for r in rs),
         "CLS_median": round(st.median(r["cls"] for r in rs), 3), "long_tasks_ms_run1": rs[0]["lt"], "lcp_element": rs[0]["lcp_final"]["el"] if rs[0]["lcp_final"] else None,
         "lcp_candidates_run1": rs[0]["lcp"], "fonts_run1": rs[0]["fonts"], "transfer_kb_median": st.median(r["transfer_kb"] for r in rs)}
    print(json.dumps(S, indent=1))
    if a.out: open(a.out, "w").write(json.dumps({"summary": S, "runs": rs}, indent=1))


if __name__ == "__main__":
    main()

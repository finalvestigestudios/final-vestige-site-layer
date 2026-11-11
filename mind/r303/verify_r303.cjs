"use strict";
/* R303 reproduce locally: node mind/r303/verify_r303.cjs (no network/dependencies). */
const fs=require("node:fs"),path=require("node:path");
function check(a){
 const e=[];const put=(b,k)=>{if(!b)e.push(k)};let m;try{m=JSON.parse(a.matrix)}catch{return ["JSON_PARSE"]}
 const ids=new Set(m.sources?.map(s=>s.id));
 put(m.status==="UNPUBLISHED_HARD_HOLD","RELEASE_STATUS");
 put(m.sources?.length===16&&ids.size===16,"SOURCE_INTEGRITY");
 put(m.claims?.length===30&&m.claims.every(c=>c.source_ids?.length&&c.source_ids.every(id=>ids.has(id))),"CLAIM_SOURCES");
 put(m.commercial_gates?.length===18&&m.commercial_gates.every(g=>g.status==="HARD_HOLD"&&g.evidence===null),"COMMERCIAL_HOLD");
 put(m.offer_selection?.publisher_approval===null&&m.offer_selection?.issued_affiliate_url===null&&m.offer_selection?.price_for_fv===null,"PUBLISHER_APPROVAL");
 put(m.paid_outcomes&&Object.values(m.paid_outcomes).every(v=>v===null),"PAID_OUTCOMES");
 put(m.creator_paths?.length===3&&m.creator_paths.every(p=>p.asset_id===null&&p.asset_url===null),"CREATOR_ATTRIBUTION");
 for(const name of ["guide","hub"]){const h=a[name]||"";
  put(/<main\b[^>]*id="main"/i.test(h)&&/href="#main"/i.test(h),"MAIN_SKIP_"+name);
  put(/:focus-visible/.test(h)&&/prefers-reduced-motion/.test(h)&&/@media\(max-width:/i.test(h),"A11Y_"+name);
  put(!/<(?:script|form|iframe|object|embed|video|input|textarea|select)\b/i.test(h),"ACTIVE_"+name);
  put(!/\bon[a-z]+\s*=/i.test(h),"INLINE_JS_"+name);
  put(!/<meta[^>]*http-equiv\s*=\s*["']?refresh/i.test(h),"REFRESH_"+name);
  put(!/\b(?:src|action)\s*=\s*["']?https?:\/\//i.test(h),"EXTERNAL_RESOURCE_"+name);
  put(!/style\s*=\s*["'][^"']*(?:display\s*:\s*none|visibility\s*:\s*hidden)/i.test(h),"HIDDEN_DISCLOSURE_"+name);
  const hrefs=[...h.matchAll(/\bhref\s*=\s*"([^"]+)"/gi)].map(v=>v[1]);
  put(hrefs.every(x=>x.startsWith("#")||/^https:\/\/(?:www\.)?finalvestige\.com(?:\/|$)/.test(x)),"OUTBOUND_LINK_"+name);
  put(hrefs.includes("https://finalvestige.com/focus/"),"EXISTING_FOCUS_"+name);
  const button=h.match(/<button\b([^>]*)>[\s\S]*?<\/button>([\s\S]{0,320})/i);
  put(Boolean(button&&/\bdisabled\b/.test(button[1])),"DISABLED_BUTTON_"+name);
  put(Boolean(button&&/id="commission-disclosure"/.test(button[2])&&/commission|affiliate/i.test(button[2])),"ADJACENT_DISCLOSURE_"+name);
 }
 put(a.guide.includes("STATIC STORYBOARD, NOT PLAYABLE")&&a.guide.includes("00:29–00:42")&&a.guide.includes("<details>"),"FILM_TRUTH");
 put(a.hub.includes("not the canonical hub PR #172")&&a.hub.includes("Four routes"),"HUB_SCOPE");
 put(a.article.includes("https://doi.org/10.1068/p090483")&&a.article.includes("https://pmc.ncbi.nlm.nih.gov/articles/PMC4191594/")&&a.article.includes("full text **restricted**"),"PRIMARY_SOURCE_SCOPE");
 put(a.memo.includes("NOT COMPUTABLE")&&a.memo.includes("HARD HOLD"),"REVENUE_HONESTY");
 return e
}
function clone(f){return JSON.parse(JSON.stringify(f))}
const paths={"guide":"ZEN12-CANONICAL-PRESELL-HYBRID-REVIEW-ONLY.html","hub":"MIND-ARCHIVE-FOUR-STREAM-WP-HTML-REVIEW-ONLY.html","matrix":"THATCHER-ZEN12-SOURCE-CLAIM-AUTHORIZATION.json","article":"THE-FACE-THAT-HID-ITS-DISTORTION-UNPUBLISHED.md","memo":"ONE-OFFER-CONVERSION-AND-RELEASE-ACCEPTANCE.md"};
const files=Object.fromEntries(Object.entries(paths).map(([k,p])=>[k,fs.readFileSync(path.join(__dirname,p),"utf8")]));
const baseline=check(files);if(baseline.length)throw Error("BASELINE: "+baseline.join(","));
const fixtures=[
["remove disabled","DISABLED_BUTTON_guide",a=>a.guide=a.guide.replace('type="button" disabled','type="button"')],
["remove disclosure","ADJACENT_DISCLOSURE_guide",a=>a.guide=a.guide.replace('id="commission-disclosure"','id="elsewhere"')],
["conceal disclosure","HIDDEN_DISCLOSURE_guide",a=>a.guide=a.guide.replace('id="commission-disclosure"','id="commission-disclosure" style="display:none"')],
["add merchant outbound","OUTBOUND_LINK_guide",a=>a.guide=a.guide.replace("</main>",'<a href="https://zen12.com/getstarted">buy</a></main>')],
["add external outbound","OUTBOUND_LINK_hub",a=>a.hub=a.hub.replace("</main>",'<a href="https://pixel.example.net/path">buy</a></main>')],
["inject form","ACTIVE_hub",a=>a.hub=a.hub.replace("</main>","<form></form></main>")],
["inject script","ACTIVE_guide",a=>a.guide=a.guide.replace("</main>","<script>alert(1)</script></main>")],
["inject iframe","ACTIVE_hub",a=>a.hub=a.hub.replace("</main>","<iframe></iframe></main>")],
["inject event handler","INLINE_JS_guide",a=>a.guide=a.guide.replace('<main id="main" class="wrap">','<main id="main" class="wrap" onclick="go()">')],
["inject redirect","REFRESH_hub",a=>a.hub=a.hub.replace("</head>",'<meta http-equiv="refresh" content="0;url=https://bad.example"></head>')],
["remote pixel","EXTERNAL_RESOURCE_hub",a=>a.hub=a.hub.replace("</main>",'<img src="https://bad.example/pixel"></main>')],
["break skip","MAIN_SKIP_guide",a=>a.guide=a.guide.replace('href="#main"','href="#junk"')],
["break focus CSS","A11Y_hub",a=>a.hub=a.hub.replaceAll(":focus-visible",":hover")],
["claim playable","FILM_TRUTH",a=>a.guide=a.guide.replace("STATIC STORYBOARD, NOT PLAYABLE","VIDEO IS PLAYABLE")],
["remove source","PRIMARY_SOURCE_SCOPE",a=>a.article=a.article.replace("https://doi.org/10.1068/p090483","https://bad.example")],
["approve gate","COMMERCIAL_HOLD",a=>{const m=JSON.parse(a.matrix);m.commercial_gates[0].status="APPROVED";a.matrix=JSON.stringify(m)}],
["invent earning link","PUBLISHER_APPROVAL",a=>{const m=JSON.parse(a.matrix);m.offer_selection.issued_affiliate_url="https://fake.example";a.matrix=JSON.stringify(m)}],
["invent sale","PAID_OUTCOMES",a=>{const m=JSON.parse(a.matrix);m.paid_outcomes.verified_paid_orders=1;a.matrix=JSON.stringify(m)}],
["invent creator ID","CREATOR_ATTRIBUTION",a=>{const m=JSON.parse(a.matrix);m.creator_paths[0].asset_id="fake";a.matrix=JSON.stringify(m)}],
["bad claim source","CLAIM_SOURCES",a=>{const m=JSON.parse(a.matrix);m.claims[0].source_ids=["MISSING"];a.matrix=JSON.stringify(m)}],
["delete source","SOURCE_INTEGRITY",a=>{const m=JSON.parse(a.matrix);m.sources.pop();a.matrix=JSON.stringify(m)}],
["release approval fabrication","RELEASE_STATUS",a=>{const m=JSON.parse(a.matrix);m.status="LIVE";a.matrix=JSON.stringify(m)}],
["remove Fieldbook","EXISTING_FOCUS_guide",a=>a.guide=a.guide.replaceAll("https://finalvestige.com/focus/","https://finalvestige.com/other/")],
["replace hub scope","HUB_SCOPE",a=>a.hub=a.hub.replace("not the canonical hub PR #172","replaces homepage")],
["replace net revenue","REVENUE_HONESTY",a=>a.memo=a.memo.replaceAll("NOT COMPUTABLE","VERIFIED REVENUE")]
];
for(const [name,expected,mutate] of fixtures){const copy=clone(files);mutate(copy);const errs=check(copy);if(!errs.includes(expected))throw Error(name+" expected "+expected+" got "+errs.join(","));}
console.log("R303 PASS baseline; deliberate unsafe mutations "+fixtures.length+"/"+fixtures.length+" rejected.");

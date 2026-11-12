'use strict';
// Run from any working directory: node /path/to/repo/mind/r308/verify_r308.cjs
// File-only regression harness. Does not invoke network, analytics or merchants.
const fs=require('node:fs');const path=require('node:path');
const names=["THE-NAME-THAT-CROSSED-THE-ROOM-UNPUBLISHED.md","ZEN12-A-TEXT-REVIEW-ONLY.html","ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html","MIND-FOUR-STREAM-ARCHIVE-WP-REVIEW-ONLY.html","EXACT-SELLER-SOURCES-CLAIMS-AND-COMMERCE-HOLDS.json","ONE-OFFER-CREATOR-ATTRIBUTION-AND-RELEASE-ACCEPTANCE.md"];
const F=Object.fromEntries(names.map(n=>[n,fs.readFileSync(path.join(__dirname,n),'utf8')]));
function validate(F){
 const err=[],must=(c,s)=>{if(!c)err.push(s)};
 const A=F["ZEN12-A-TEXT-REVIEW-ONLY.html"],B=F["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"],H=F["MIND-FOUR-STREAM-ARCHIVE-WP-REVIEW-ONLY.html"],R=F["THE-NAME-THAT-CROSSED-THE-ROOM-UNPUBLISHED.md"],D=F["ONE-OFFER-CREATOR-ATTRIBUTION-AND-RELEASE-ACCEPTANCE.md"];
 let J;try{J=JSON.parse(F["EXACT-SELLER-SOURCES-CLAIMS-AND-COMMERCE-HOLDS.json"])}catch(e){return["JSON integrity"]}
 for(const [label,s] of [["A",A],["B",B],["Hub",H]]){
 must(s.startsWith("<!doctype html>"),label+" doctype");
 must(s.includes('<html lang="en">')&&s.includes('name="viewport"'),label+" a11y basics");
 must(s.includes('name="robots" content="noindex,nofollow"'),label+" noindex");
 must((s.match(/<h1(?: |>) /g)||[]).length===1||(s.match(/<h1[ >]/g)||[]).length===1,label+" single H1");
 must(s.includes('type="button" disabled aria-disabled="true"'),label+" disabled purchase");
 must(/earn a commission at no additional cost|earn a commission if you purchase/.test(s),label+" near-link disclosure");
 must(!/<(?:script|iframe|form|input|video|audio)\b/i.test(s),label+" no scripts/forms/playing media");
 must(!/\b(?:onclick|onload|onerror)=/i.test(s),label+" no event handlers");
 must(!/href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com/i.test(s),label+" no seller outbound URLs");
 must(!/javascript:|data:text\/html/i.test(s),label+" no javascript URL");
 }
 const buyer=s=>s.slice(s.indexOf('<p class="eyebrow">Tools under review'),s.indexOf('</main>',s.indexOf('<p class="eyebrow">Tools under review')));
 must(buyer(A).length>100&&buyer(A)===buyer(B),"A B exact-copy-controlled");
 must(!A.includes('id="optional-film"')&&B.includes('id="optional-film"'),"single B film");
 must(B.includes('42-second')&&B.includes("not playable media")&&B.includes("00:36–00:42"),"film only static and timed");
 must(H.includes("https://finalvestige.com/focus/")&&A.includes("https://finalvestige.com/focus/"),"existing Focus funnel");
 must(H.includes("Puységur"),"history navigation");
 for(const s of ["34.6%","29%","1953","1959","1995","2021","not tests of any meditation recording","https://pubmed.ncbi.nlm.nih.gov/32833466/"]){must(R.toLowerCase().includes(s.toLowerCase()),"article "+s)}
 must(D.includes("NOT COMPUTABLE")&&D.includes("net_revenue_per_1000_qualified_human_sessions"),"revenue attribution not fabricated");
 must(D.includes("HARD HOLD")&&/No CMS writes|No CMS|no CMS/.test(D),"release hold");
 must(J.sources?.length===16&&J.claims?.length===30&&J.gates?.length===18,"registry counts");
 must(J.release_status==="HARD_HOLD"&&J.source_control_only===true,"global approval hold");
 must(J.authorization?.partner_link==="WITHHELD"&&J.authorization?.account_specific_inspire3_approval==="NOT_VERIFIED","unverified partner");
 must(J.attribution_contract?.value_status==="NOT_COMPUTABLE","unverified realized revenue");
 must(J.gates.every(g=>g.status==="HARD_HOLD"),"all gates held");
 const ids=new Set(J.sources.map(x=>x.id));must(ids.size===J.sources.length&&J.sources.every(x=>/^https:\/\//.test(x.url)),"valid source ids and URLs");
 must(J.claims.every(x=>ids.has(x.source_id)),"claim source lineage");
 for(const k of ["P04","P05","P06","P10","P12","C03","C06","C07","C08"]){must(J.claims.find(x=>x.id===k)?.decision==="reject","inference prohibition "+k)}
 must(J.creator_routes.filter(x=>x.grok_asset_id!==null).length===1&&J.creator_routes.find(x=>x.grok_asset_id!==null)?.grok_asset_id==="zctcIECAZ2s","no fabricated Grok asset");
 return err;
}
function clone(F){return JSON.parse(JSON.stringify(F))}
const changes=[["A enabled",x=>x["ZEN12-A-TEXT-REVIEW-ONLY.html"]=x["ZEN12-A-TEXT-REVIEW-ONLY.html"].replace('type="button" disabled aria-disabled="true"','type="button"')],
["B enabled",x=>x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"]=x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"].replace('type="button" disabled aria-disabled="true"','type="button"')],
["hub enabled",x=>x["MIND-FOUR-STREAM-ARCHIVE-WP-REVIEW-ONLY.html"]=x["MIND-FOUR-STREAM-ARCHIVE-WP-REVIEW-ONLY.html"].replace('type="button" disabled aria-disabled="true"','type="button"')],
["merchant A",x=>x["ZEN12-A-TEXT-REVIEW-ONLY.html"]+='<a href="https://zen12.com/hnp">Buy</a>'],
["merchant B",x=>x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"]+='<a href="https://brainwaveshots.com/focus-shot">Buy</a>'],
["merchant Hub",x=>x["MIND-FOUR-STREAM-ARCHIVE-WP-REVIEW-ONLY.html"]+='<a href="https://inspire3.com/">Buy</a>'],
["script A",x=>x["ZEN12-A-TEXT-REVIEW-ONLY.html"]+='<script>track()</script>'],
["iframe B",x=>x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"]+='<iframe src="x"></iframe>'],
["form Hub",x=>x["MIND-FOUR-STREAM-ARCHIVE-WP-REVIEW-ONLY.html"]+='<form><input></form>'],
["inline handler",x=>x["ZEN12-A-TEXT-REVIEW-ONLY.html"]+='<div onclick="track()">x</div>'],
["autoplay",x=>x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"]+='<video autoplay></video>'],
["javascript url",x=>x["ZEN12-A-TEXT-REVIEW-ONLY.html"]+='<a href="javascript:alert(1)">x</a>'],
["A disclosure",x=>x["ZEN12-A-TEXT-REVIEW-ONLY.html"]=x["ZEN12-A-TEXT-REVIEW-ONLY.html"].replace("earn a commission if you purchase","get paid if you purchase")],
["B disclosure",x=>x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"]=x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"].replace("earn a commission if you purchase","get paid if you purchase")],
["Hub disclosure",x=>x["MIND-FOUR-STREAM-ARCHIVE-WP-REVIEW-ONLY.html"]=x["MIND-FOUR-STREAM-ARCHIVE-WP-REVIEW-ONLY.html"].replace("earn a commission at no additional cost","get paid")],
["copy mismatch",x=>x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"]=x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"].replace("a self-paced collection","an amazing collection")],
["removed video",x=>x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"]=x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"].replace('id="optional-film"','id="gone-film"')],
["fake playable",x=>x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"]=x["ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html"].replace("not playable media","playable media")],
["wrong 29",x=>x["THE-NAME-THAT-CROSSED-THE-ROOM-UNPUBLISHED.md"]=x["THE-NAME-THAT-CROSSED-THE-ROOM-UNPUBLISHED.md"].replaceAll("29%","100%")],
["wrong 34.6",x=>x["THE-NAME-THAT-CROSSED-THE-ROOM-UNPUBLISHED.md"]=x["THE-NAME-THAT-CROSSED-THE-ROOM-UNPUBLISHED.md"].replaceAll("34.6%","95%")],
["claim transfer",x=>x["THE-NAME-THAT-CROSSED-THE-ROOM-UNPUBLISHED.md"]=x["THE-NAME-THAT-CROSSED-THE-ROOM-UNPUBLISHED.md"].replace("not tests of any meditation recording","proof of meditation recordings")],
["false revenue",x=>x["ONE-OFFER-CREATOR-ATTRIBUTION-AND-RELEASE-ACCEPTANCE.md"]=x["ONE-OFFER-CREATOR-ATTRIBUTION-AND-RELEASE-ACCEPTANCE.md"].replaceAll("NOT COMPUTABLE","$0.00")],
["invalid JSON",x=>x["EXACT-SELLER-SOURCES-CLAIMS-AND-COMMERCE-HOLDS.json"]+="["],
["source removed",x=>{const n="EXACT-SELLER-SOURCES-CLAIMS-AND-COMMERCE-HOLDS.json";const j=JSON.parse(x[n]);j.sources.splice(0,1);x[n]=JSON.stringify(j)}],
["gate open",x=>{const n="EXACT-SELLER-SOURCES-CLAIMS-AND-COMMERCE-HOLDS.json";const j=JSON.parse(x[n]);j.gates[0].status="APPROVED";x[n]=JSON.stringify(j)}],
["partner invented",x=>{const n="EXACT-SELLER-SOURCES-CLAIMS-AND-COMMERCE-HOLDS.json";const j=JSON.parse(x[n]);j.authorization.partner_link="https://tracking.example";x[n]=JSON.stringify(j)}],
["merchant claim promoted",x=>{const n="EXACT-SELLER-SOURCES-CLAIMS-AND-COMMERCE-HOLDS.json";const j=JSON.parse(x[n]);j.claims.find(c=>c.id==="P04").decision="permit";x[n]=JSON.stringify(j)}],
["fake creator",x=>{const n="EXACT-SELLER-SOURCES-CLAIMS-AND-COMMERCE-HOLDS.json";const j=JSON.parse(x[n]);j.creator_routes[0].grok_asset_id="fake";x[n]=JSON.stringify(j)}],
["false commercial KPI",x=>{const n="EXACT-SELLER-SOURCES-CLAIMS-AND-COMMERCE-HOLDS.json";const j=JSON.parse(x[n]);j.attribution_contract.value_status="VERIFIED_PAID";x[n]=JSON.stringify(j)}],
["A no h1",x=>x["ZEN12-A-TEXT-REVIEW-ONLY.html"]=x["ZEN12-A-TEXT-REVIEW-ONLY.html"].replace("<h1>","<h2>")]];
const baseline=validate(F);if(baseline.length){console.error('R308 baseline FAILED',baseline);process.exit(1)}
let rejected=0;const undetected=[];
for(const [n,fn]of changes){const f=clone(F);fn(f);if(validate(f).length)rejected++;else undetected.push(n)}
console.log('R308 baseline PASS; unsafe mutations rejected '+rejected+'/'+changes.length);
if(undetected.length){console.error('UNDETECTED',undetected);process.exit(1)}
// Source checks are not native browser/WordPress/media/payment/revenue acceptance.

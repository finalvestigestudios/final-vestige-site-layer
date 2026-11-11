/* Mind R294: native Node source QA. Run from repo root: node mind/r294/verify_r294.cjs
    Source checks only; NOT browser WCAG, WordPress sanitizer, merchant tracking, or paid revenue validation. */
"use strict";
const fs=require("node:fs"), assert=require("node:assert/strict");
const path=require("node:path");
const root=path.resolve(__dirname,"../..");
const F={article:"mind/r294/THE-MEMORY-THAT-ARRIVED-AFTER-THE-EVENT-UNPUBLISHED.md",hub:"mind/r294/MIND-THE-WITNESS-AND-THE-RECORD-WP-HTML-CANDIDATE.html",matrix:"mind/r294/MEMORY-MISINFORMATION-COMMERCE-GATES.json",plan:"mind/r294/CANONICAL-ONE-OFFER-AND-REVENUE-ACCEPTANCE.md",A:"mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html",B:"mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html"};
const read=()=>Object.fromEntries(Object.entries(F).map(([k,v])=>[k,fs.readFileSync(path.join(root,v),"utf8")]));
const allowed=new Set(["finalvestige.com","pubmed.ncbi.nlm.nih.gov","www.ftc.gov","journals.plos.org","portal.research.lu.se","onlinelibrary.wiley.com"]);
function decode(s){return s.replace(/&#x([0-9a-f]+);?|&#([0-9]+);?|&colon;?|&sol;?/gi,(z,h,d)=>h?String.fromCodePoint(parseInt(h,16)):d?String.fromCodePoint(+d):/^&colon/i.test(z)?":":"/");}
function htmlCheck(h,label){
 const s=decode(h).replace(/<!--[\s\S]*?-->/g,"");
 assert.match(s,/<!doctype html>/i,label+" doctype");
 assert.doesNotMatch(s,/<\s*(script|iframe|form|object|embed|link|base|input|textarea|select|canvas|audio|video|source|track|img|picture|svg)\b/i,label+" active element");
 assert.doesNotMatch(s,/<\s*meta\b[^>]*http-equiv\s*=\s*["']?refresh/i,label+" refresh");
 assert.doesNotMatch(s,/\son[a-z]+\s*=|\b(srcdoc|src|srcset|poster|action|formaction|ping|data-src|data-href)\s*=|@import\b|\burl\s*\(|\bexpression\s*\(/i,label+" remote attr");
 const btn=[...s.matchAll(/<button\b([^>]*)>/gi)];assert.equal(btn.length,1,label+" one disabled buying control");
 assert.match(btn[0][1],/(?:^|\s)disabled(?:\s|=|$)/i,label+" real disabled");
 const at=s.indexOf(btn[0][0]);const near=s.slice(Math.max(0,at-1000),at);
 assert.match(near,/may earn a commission/i,label+" adjacent earnings disclosure");
 assert.match(near,/no additional cost/i,label+" adjacent no-cost disclosure");
 assert.match(s,/https:\/\/finalvestige\.com\/focus\//i,label+" free alternative");
 const hrefs=[...s.matchAll(/<a\b([^>]*)>/gi)];
 assert.ok(hrefs.length>=5,label+" meaningful internal links");
 for(const [,attrs] of hrefs){
   const m=attrs.match(/(?:^|\s)href\s*=\s*(["'])(.*?)\1/i);
   assert.ok(m&&m[2],label+" quoted href");
   const url=m[2].trim();
   if(url.startsWith("#"))continue;
   assert.ok(/^https:\/\//i.test(url),label+" HTTPS");
   const host=new URL(url).hostname.toLowerCase();
   assert.ok(allowed.has(host),label+" authorized domain: "+host);
 }
 assert.doesNotMatch(s,/(?:https?:)?\/\/(?:www\.)?(?:zen12|hypnosislive|brainwaveshots|inspire3)\.com/i,label+" merchant in HTML");
 assert.match(s,/<meta\s+name="robots"\s+content="noindex,nofollow"/i,label+" noindex");
}
function validate(x){
 for(const k of Object.keys(F))assert.ok(typeof x[k]==="string"&&x[k].length>700,k+" full file");
 htmlCheck(x.hub,"hub");htmlCheck(x.A,"A");htmlCheck(x.B,"B");
 const m=JSON.parse(x.matrix);
 assert.equal(m.status,"UNPUBLISHED_HARD_HOLD");
 assert.equal(m.sources.length,18);assert.equal(m.claims.length,28);
 assert.equal(m.authorization_gates.length,18);assert.ok(m.authorization_gates.every(g=>g.status==="HARD_HOLD"&&g.verified_at===null&&g.evidence===null&&!g.override_allowed));
 const ids=new Set(m.sources.map(s=>s.id));assert.equal(ids.size,18);
 for(const c of m.claims){assert.ok(c.source_ids.length&&c.source_ids.every(id=>ids.has(id)));assert.ok(c.limits.length>=10)}
 const c=m.commercial_primary_hypothesis;
 assert.equal(c.affiliate_earning_url,null);assert.equal(c.cta_disabled,true);assert.equal(c.checkout_activated,false);assert.equal(c.price_to_quote,null);
 assert.deepEqual(c.canonical_variants,[F.A,F.B]);
 assert.equal(m.owned_fallback.verified_paid_mind_sku,null);
 assert.ok(m.creator_topic_fit.every(a=>a.asset_id===null&&a.post_url===null&&!a.campaign_live));
 assert.equal(m.measurement.live,false);assert.equal(m.measurement.utm_campaign_final,null);assert.ok(m.measurement.no_PII&&m.measurement.no_new_forms&&m.measurement.no_new_pixels);
 assert.ok(m.measurement.kpi.includes("settled_FV_affiliate_commissions"));
 assert.equal(m.experiment.variant_B_currently_playable,false);assert.equal(m.experiment.assignment_live,false);
 assert.ok(Object.values(m.release).every(v=>v===false));
 for(const k of ["A","B"]){assert.match(x[k],/fewer than half/i);assert.match(x[k],/14-day refund-request window/i);}
 assert.match(x.article,/72% of participants/);assert.match(x.article,/68 percentage points/);
 assert.match(x.plan,/NOT COMPUTABLE|cannot be computed/);
 return {sources:m.sources.length,claims:m.claims.length,commercial_gates:m.authorization_gates.length,canonical_guides:2};
}
function mutationTests(x){
 const cases=[
 ["hub refresh",y=>y.hub=y.hub.replace("</head>",'<meta http-equiv="refresh" content="0;url=https://evil.invalid"></head>')],
 ["hub merchant link",y=>y.hub=y.hub.replace("</main>",'<a href="https://zen12.com/getstarted">Buy</a></main>')],
 ["hub JS link",y=>y.hub=y.hub.replace("</main>",'<a href="javascript:alert(1)">x</a></main>')],
 ["hub extra form",y=>y.hub=y.hub.replace("</main>",'<form action="/subscribe"><input></form></main>')],
 ["hub enabled button",y=>y.hub=y.hub.replace(/disabled aria-describedby=/,"aria-describedby=")],
 ["hub remove disclosure",y=>y.hub=y.hub.replace("may earn a commission","could do something")],
 ["A refresh",y=>y.A=y.A.replace("</head>",'<meta http-equiv="refresh" content="0;url=https://evil.invalid"></head>')],
 ["B redirect link",y=>y.B=y.B.replace("</body>",'<a href="https://zen12.com/getstarted">x</a></body>')],
 ["B JS link",y=>y.B=y.B.replace("</body>",'<a href="javascript:alert(1)">x</a></body>')],
 ["A tracking pixel",y=>y.A=y.A.replace("</body>",'<img src="https://tracker.invalid/pixel"></body>')],
 ["B enabled button",y=>y.B=y.B.replace(/disabled aria-describedby=/,"aria-describedby=")],
 ["A disclosure erased",y=>y.A=y.A.replace("may earn a commission","can earn credits")],
 ["affiliate link invented",y=>{let j=JSON.parse(y.matrix);j.commercial_primary_hypothesis.affiliate_earning_url="https://zen12.com/?ref=FAKE";y.matrix=JSON.stringify(j)}],
 ["affiliate authorization invented",y=>{let j=JSON.parse(y.matrix);j.authorization_gates[0].status="APPROVED";y.matrix=JSON.stringify(j)}],
 ["SKU invented",y=>{let j=JSON.parse(y.matrix);j.owned_fallback.verified_paid_mind_sku="FAKE";y.matrix=JSON.stringify(j)}],
 ["fake asset id",y=>{let j=JSON.parse(y.matrix);j.creator_topic_fit[0].asset_id="fake";y.matrix=JSON.stringify(j)}],
 ["live tracking claimed",y=>{let j=JSON.parse(y.matrix);j.measurement.live=true;y.matrix=JSON.stringify(j)}],
 ["campaign silently chosen",y=>{let j=JSON.parse(y.matrix);j.measurement.utm_campaign_final="mind_proposed_2026_11";y.matrix=JSON.stringify(j)}],
 ["video magically hosted",y=>{let j=JSON.parse(y.matrix);j.experiment.variant_B_currently_playable=true;y.matrix=JSON.stringify(j)}],
 ["claim source unlinked",y=>{let j=JSON.parse(y.matrix);j.claims[0].source_ids=["missing_id"];y.matrix=JSON.stringify(j)}],
 ["source list shrunk",y=>{let j=JSON.parse(y.matrix);j.sources.pop();y.matrix=JSON.stringify(j)}],
 ["release toggled",y=>{let j=JSON.parse(y.matrix);j.release.wordpress_write=true;y.matrix=JSON.stringify(j)}]
 ];
 const failures=[];
 for(const [name,fn] of cases){
  const y={...x};let changed=false;try{fn(y);changed=Object.keys(F).some(k=>y[k]!==x[k]);}catch(e){throw Error("Mutation construction FAILED "+name+": "+e.message)}
  assert.ok(changed,"mutation did not change input: "+name);
  try{validate(y);failures.push(name)}catch(e){if(!(e instanceof Error))throw e}
 }
 assert.equal(failures.length,0,"mutations not rejected: "+failures.join(", "));
 return cases.length;
}
if(require.main===module){const x=read();const r=validate(x);const n=mutationTests(x);console.log("R294 PASS",JSON.stringify(r),n+"/"+n+" deliberate mutations rejected");}
module.exports={validate,mutationTests,htmlCheck,read};
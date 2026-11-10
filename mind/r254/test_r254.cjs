/* Mind R254 source-only fail-closed guard. From repository root:
   node mind/r254/test_r254.cjs
   Native run checks Git blob identities before any content validation.
   Isolated V8 callers can import validate and negativeSuite against independently retrieved files.
   This is NOT live browser, WP sanitization, payment or affiliate-account validation. */
"use strict";
const assert = require("node:assert/strict");
const PINS = {
 A:"c5277c7023ba97d68a9773f1711528c3169acdfc",
 B:"aa55277af94df571ececad38988f39e8b2c35a89",
 article:"d1b3d5c5a280de94403946fc3dcad781360b07be",
 matrix:"74ef68da7ced6d06e7b5439b00ea1238ab8a39c4",
 plan:"e3c52fd71f9886b6371657f3a1b44c7163c3b3e5",
 hub:"bd36192e05e2352554370ddb90e84d6b27faa406",
 inheritedB:"883b17e1b4759bd6acc1e99ca60b81a21a8d85db"
};
function validate(x){
 const {A,B,article,matrix:m,plan,hub,inheritedB}=x;
 assert.match(A, /<html lang="en">/);
 assert.match(B, /<html lang="en">/);
 assert.match(hub, /The Mind &amp; Perception Archive/);
 assert.match(hub, /four|Four|01 · Perception/);
 assert.match(hub, /https:\/\/finalvestige\.com\/2026\/11\/02\/change-blindness\//);
 assert.match(hub, /https:\/\/finalvestige\.com\/focus\//);
 assert.match(inheritedB, /An original gold-outlined clock and a large title reading 12 MINUTES IS A DURATION NOT A RESULT/);
 assert.doesNotMatch(inheritedB, /three archive cards labelled/);
 for (const page of [A,B,hub,inheritedB]){
   assert.match(page, /name="robots" content="noindex,nofollow"/);
   assert.doesNotMatch(page, /<script\b|<form\b|<iframe\b|<video\b|<source\b|<object\b|<embed\b|javascript:|<meta[^>]*http-equiv=["']refresh/i);
   assert.doesNotMatch(page, /\bon(?:click|load|error|focus|submit|change|pointerdown|mouseover)\s*=/i);
   assert.doesNotMatch(page, /<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3|brainwaveshots|hypnosislive)\./i);
   assert.equal((page.match(/<button\b/g)||[]).length,1);
   assert.match(page, /<button\b[^>]*\bdisabled\b/);
 }
 for(const page of [A,B]){
   assert.match(page,/data-variant="[AB]"/);
   assert.match(page,/If you purchase through an approved link, Final Vestige may earn a commission at no additional cost to you/);
   assert.match(page,/id="affiliate-disclosure"/);
   assert.match(page,/aria-describedby="affiliate-disclosure commercial-reason"/);
   assert.match(page,/intentionally disabled/);
   assert.match(page,/https:\/\/finalvestige\.com\/focus\//);
   assert.match(page,/\$87\.99/);
   assert.match(page,/one-year money-back guarantee/);
   assert.match(page,/12 progression levels and 48 MP3 recordings/);
   assert.match(page,/noindex,nofollow/);
   assert.match(page,/prefers-reduced-motion:reduce/);
   const disclosure=page.indexOf('id="affiliate-disclosure"');
   const button=page.indexOf('<button class="decision"');
   assert.ok(disclosure>=0 && button>disclosure && button-disclosure<800, "clear near-action disclosure");
   assert.ok((page.match(/https:\/\/finalvestige\.com\/focus\//g)||[]).length===1,"one Focus route only");
 }
 assert.doesNotMatch(A,/<section class="film"/);
 assert.match(B,/<section class="film"/);
 assert.match(B,/<details><summary>/);
 assert.match(B,/<desc id="film-desc">Original illustration: a stopwatch marked 12 minutes/);
 assert.match(B,/No original MP4, audio, WebVTT media file or synchronized playback exists yet/);
 const timePattern=/<time>(\d\d):(\d\d)–(\d\d):(\d\d)<\/time>/g;
 const times=[...B.matchAll(timePattern)].map(v=>[+v[1]*60+(+v[2]),+v[3]*60+(+v[4])]);
 assert.equal(times.length,7);
 for(let i=0;i<times.length;i++){
   assert.ok(times[i][1]>times[i][0],"positive caption duration");
   if(i)assert.equal(times[i][0],times[i-1][1],"caption segments continuous");
 }
 assert.equal(times[0][0],0);
 assert.equal(times.at(-1)[1],42);
 const removeFilm=s=>s.replace(/<section class="film"[\s\S]*?<\/section>/,"");
 assert.equal(removeFilm(B).replace('data-variant="B"','data-variant="A"'),A,"A/B buyer copy identical except optional film and variant identifier");
 const urls=[...A.matchAll(/<a\b[^>]*href="([^"]+)"/g)].map(v=>v[1]);
 assert.ok(urls.every(u=>u.startsWith("#")||/^https:\/\/finalvestige\.com\//.test(u)),"no external active CTA");
 assert.equal(m.source_count,m.sources.length);
 assert.equal(m.claim_count,m.claims.length);
 assert.ok(m.sources.length>=15&&m.claims.length>=20);
 const ids=new Set(m.sources.map(s=>s.id));
 assert.equal(ids.size,m.sources.length);
 assert.ok(m.sources.every(s=>/^https:\/\//.test(s.url)));
 assert.ok(m.claims.every(c=>c.source_ids.length&&c.source_ids.every(id=>ids.has(id))));
 assert.equal(m.authorization_gates.length,16);
 assert.ok(m.authorization_gates.every(g=>g.status==="HARD_HOLD"));
 assert.equal(m.release_status,"HARD_HOLD");
 assert.equal(m.affiliate.issued_earning_url,null);
 assert.equal(m.affiliate.named_approval,null);
 assert.equal(m.status.live,false);
 assert.equal(m.status.affiliate_active,false);
 assert.equal(m.status.payment_verified,false);
 assert.ok(Object.values(m.measurements).every(v=>v===null),"never invent revenue");
 assert.ok(article.length>12500 && /self-hypnosis/i.test(article));
 assert.match(article,/25958769/);
 assert.match(article,/30226009/);
 assert.match(article,/36536625/);
 assert.match(article,/2434085/);
 assert.match(article,/No commercial link or endorsement appears here/);
 assert.match(plan,/NOT_COMPUTABLE/);
 assert.match(plan,/Grok/);
 assert.match(plan,/HARD_HOLD/);
 assert.match(plan,/No affiliate href/);
 return true;
}
function negativeSuite(original){
 let count=0; const bad=(mutator)=>{
   const x=structuredClone(original);
   mutator(x);
   assert.throws(()=>validate(x));
   count++;
 };
 bad(x=>x.A=x.A.replace(' disabled aria-describedby',' aria-describedby'));
 bad(x=>x.B=x.B.replace(' disabled aria-describedby',' aria-describedby'));
 bad(x=>x.hub=x.hub.replace(' disabled aria-describedby',' aria-describedby'));
 bad(x=>x.inheritedB=x.inheritedB.replace(' disabled aria-describedby',' aria-describedby'));
 bad(x=>x.A=x.A.replace('may earn a commission','never earns a commission'));
 bad(x=>x.B=x.B.replace('may earn a commission','never earns a commission'));
 bad(x=>x.A=x.A.replace('id="affiliate-disclosure"','id="not-disclosure"'));
 bad(x=>x.B=x.B.replace('id="affiliate-disclosure"','id="not-disclosure"'));
 bad(x=>x.B=x.B.replace('aria-describedby="affiliate-disclosure commercial-reason"','aria-describedby="commercial-reason"'));
 bad(x=>x.A=x.A.replace('noindex,nofollow','index,follow'));
 bad(x=>x.hub=x.hub.replace('noindex,nofollow','index,follow'));
 bad(x=>x.B=x.B.replace('00:36–00:42','00:36–00:45'));
 bad(x=>x.B=x.B.replace('00:06–00:12','00:06–00:11'));
 bad(x=>x.B=x.B.replace('<details><summary>','<div><summary>'));
 bad(x=>x.B=x.B.replace('Original illustration: a stopwatch marked 12 minutes','Photo of original Zen12 buyer receipt'));
 bad(x=>x.inheritedB=x.inheritedB.replace('An original gold-outlined clock and a large title reading 12 MINUTES IS A DURATION NOT A RESULT','A gold-outlined clock and three archive cards labelled CLAIM, SOURCE and LIMIT'));
 bad(x=>x.A=x.A.replace('</main>','<form method="post"><input name="email"></form></main>'));
 bad(x=>x.B=x.B.replace('</main>','<script src="https://example.com/tracker.js"></script></main>'));
 bad(x=>x.hub=x.hub.replace('</main>','<script>alert(1)</script></main>'));
 bad(x=>x.inheritedB=x.inheritedB.replace('</main>','<form><input></form></main>'));
 bad(x=>x.A=x.A.replace('<button class="decision"','<a href="https://zen12.com/hnp">BUY</a><button class="decision"'));
 bad(x=>x.B=x.B.replace('<button class="decision"','<a href="https://affiliates.inspire3.com/secret">BUY</a><button class="decision"'));
 bad(x=>x.A=x.A.replace('</main>','<div onclick="buy()">Test</div></main>'));
 bad(x=>x.B=x.B.replace('</main>','<video autoplay></video></main>'));
 bad(x=>x.A=x.A.replace('https://finalvestige.com/focus/','https://example.com/subscribe'));
 bad(x=>x.B=x.B.replace('12 progression levels and 48 MP3 recordings','72 levels and 99 MP3s'));
 bad(x=>x.A=x.A.replace('$87.99','$0.99'));
 bad(x=>x.A=x.A.replace('one-year money-back guarantee','guaranteed refund fulfilled'));
 bad(x=>x.matrix.authorization_gates[0].status="APPROVED");
 bad(x=>x.matrix.authorization_gates.pop());
 bad(x=>x.matrix.affiliate.named_approval=true);
 bad(x=>x.matrix.affiliate.issued_earning_url="https://fake.example/affiliate");
 bad(x=>x.matrix.measurements.net_revenue=1);
 bad(x=>x.matrix.sources[0].url="javascript:alert(1)");
 bad(x=>x.matrix.claims[0].source_ids=["fabricated"]);
 bad(x=>x.matrix.claims.pop());
 bad(x=>x.article=x.article.replace(/25958769/g,"unverifiable"));
 bad(x=>x.article=x.article.slice(0,3000));
 bad(x=>x.plan=x.plan.replace("NOT_COMPUTABLE","conversion verified"));
 return count;
}
module.exports={validate,negativeSuite,PINS};
if(require.main===module){
 const fs=require("node:fs"), path=require("node:path"), crypto=require("node:crypto");
 const files={A:"zen12-decision-A-text-HOLD.html",B:"zen12-decision-B-film-concept-HOLD.html",article:"THE-VOICE-THAT-ISNT-A-COMMAND-UNPUBLISHED.md",matrix:"EVIDENCE-PRODUCT-COMMERCE-GATES.json",plan:"OFFER-FUNNEL-EDITORIAL-CONVERSION-ACCEPTANCE.md",hub:"../r253/MIND-ARCHIVE-UNPUBLISHED-WP-PREVIEW.html",inheritedB:"../r253/zen12-B-optional-video-UNPUBLISHED.html"};
 const x={};
 for (const [name,file] of Object.entries(files)){
   const body=fs.readFileSync(path.join(__dirname,file),"utf8");
   const sha=crypto.createHash("sha1").update("blob "+Buffer.byteLength(body)+"\0").update(body).digest("hex");
   assert.equal(sha,PINS[name],"Git blob SHA mismatch for "+name);
   x[name]=name==="matrix"?JSON.parse(body):body;
 }
 validate(x);
 const count=negativeSuite(x);
 console.log("R254 PASS: 7/7 pinned source blob identities, baseline valid; "+count+"/"+count+" deliberately unsafe mutations rejected. Native Node source-only test; NOT browser, CI, WP or paid-sale QA.");
}
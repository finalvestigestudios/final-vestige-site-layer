'use strict';
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const {test}=require('node:test');
const read=name=>fs.readFileSync(path.join(__dirname,name),'utf8');
const art=read('choice-blindness-investigation.md');
const guide=read('zen12-real-buyer-decision-guide.md');
const a=read('zen12-text-guide-draft.html');
const b=read('zen12-optional-40s-film-draft.html');
const memo=read('commercial-eligibility-conversion-acceptance.md');
const data=JSON.parse(read('claim-source-and-release-gates.json'));
const words=s=>s.trim().split(/\s+/).length;
const checkHTML=(s,film=false)=>{
 const forbidden=/<script\b|<iframe\b|<form\b|<input\b|<video\b|<audio\b|\bonclick\s*=|\bonload\s*=|\bautoplay\b\s*=|https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3)\.com\//i;
 if(forbidden.test(s))return false;
 if(!/<html lang="en">/.test(s)||!/<meta name="viewport"/.test(s)||!/<main id="content">/.test(s))return false;
 if(!/href="#content"/.test(s)||!/<button type="button" disabled aria-disabled="true">/.test(s))return false;
 if(!/If you purchase through a future approved link, Final Vestige may earn a commission at no additional cost to you\./.test(s))return false;
 if(!/href="https:\/\/finalvestige\.com\/focus\/"/.test(s))return false;
 if(!/noindex,nofollow/.test(s)||!/@media\(max-width:660px\)/.test(s))return false;
 if(film && (!/40-second film storyboard/.test(s)||!/Complete transcript:/.test(s)||!/00:33–00:40/.test(s)))return false;
 if(!film && /film storyboard/.test(s))return false;
 const disclosure=s.indexOf('class="disclosure"');const purchase=s.indexOf('<button type="button" disabled');
 if(!(disclosure>=0&&purchase>disclosure&&purchase-disclosure<300))return false;
 return true;
};
test('editorial researched and separated from commercial recommendation',()=>{
 assert.ok(words(art)>=1800);assert.match(art,/Johansson/);assert.match(art,/Hall/);
 assert.match(art,/not\\*\\* a replication/i);assert.match(art,/not hypnosis/i);
 assert.doesNotMatch(art,/affiliate|commission|zen12\.com|inspire3\.com/i);
 for(const u of ['pubmed.ncbi.nlm.nih.gov/16210542','pubmed.ncbi.nlm.nih.gov/20637455','10.1371/journal.pone.0045457'])assert.ok(art.includes(u));
});
test('buyer guide source grounding and non-endorsement',()=>{
 assert.ok(words(guide)>=1400);assert.match(guide,/not an endorsement/i);
 assert.match(guide,/does not independently establish/i);assert.match(guide,/\$87\.99/);
 assert.match(guide,/\$37/);assert.match(guide,/free twelve-minute/i);
 assert.match(guide,/not verified an approved affiliate relationship/i);
 assert.match(guide,/inspire3\.com\/privacy\//i);
});
test('machine-readable source traceability and every gate CLOSED',()=>{
 assert.equal(data.sources.length,19);assert.equal(data.claims.length,23);assert.equal(data.gates.length,21);
 assert.ok(data.gates.every(x=>x.status==='CLOSED'));
 const ids=new Set(data.sources.map(x=>x.id));
 for(const c of data.claims){assert.ok(c.id&&c.decision&&c.limits);assert.ok(c.source_ids.every(x=>ids.has(x)),c.id);}
 assert.ok(data.claims.some(x=>x.decision.includes('reject-unsubstantiated-product-efficacy')));
 assert.ok(data.claims.some(x=>x.decision==='unverified-not-zero'));
 assert.ok(data.sources.every(x=>/^https:\/\//.test(x.url)));
});
test('structural accessibility and strong merchant hold: A and B',()=>{
 assert.ok(checkHTML(a,false));assert.ok(checkHTML(b,true));
 for(const s of [a,b]){
 assert.match(s,/<h1>/);assert.match(s,/focus\/"/);assert.match(s,/Editorial Standards/);
 assert.doesNotMatch(s,/<form|<script|<iframe|<video/i);
 assert.match(s,/reduced-motion:reduce/);
 }
});
test('paired A/B guides keep same commercial information',()=>{
 const headings=s=>[...s.matchAll(/<h2(?: [^>]*)?>(.*?)<\/h2>/g)].map(x=>x[1]).filter(x=>!x.includes('Before you buy'));
 assert.deepEqual(headings(a),headings(b));
 for(const p of ['48 MP3','12 levels','$87.99','$37','one-year','privacy','free twelve-minute','merchant']){
 assert.ok(a.toLowerCase().includes(p.toLowerCase()));assert.ok(b.toLowerCase().includes(p.toLowerCase()));}
});
test('B film is optional storyboard with captions, poster and transcript but NO fake playable video',()=>{
 assert.match(b,/class="poster"/);assert.match(b,/<details>/);assert.match(b,/<summary>/);
 for(const t of ['00:00–00:06','00:06–00:12','00:12–00:19','00:19–00:26','00:26–00:33','00:33–00:40'])assert.ok(b.includes(t));
 assert.doesNotMatch(b,/<video/i);assert.match(b,/NOT yet a playable video/);
});
test('conversion memo keeps true paid-sale semantics and single existing lead route',()=>{
 for(const v of ['merchant_paid_conversion','affiliate_click','confirmed_signup','realized_net_revenue','qualified_human_session','NOT COMPUTABLE','TASK-008','360/390/768/1440','PR #172'])assert.ok(memo.includes(v),v);
 assert.match(memo,/no supplementary subscriber list/i);assert.match(memo,/no.*script/i);
});
test('negative mutation: activating seller CTA fails closed',()=>{
 assert.equal(checkHTML(a.replace('<button type="button" disabled aria-disabled="true">','<button type="button">')),false);
 assert.equal(checkHTML(b.replace('<button type="button" disabled aria-disabled="true">','<button type="button">'),true),false);
});
test('negative mutation: removed FTC disclosure fails closed',()=>{
 assert.equal(checkHTML(a.replace(/<p class="disclosure">[\s\S]*?<\/p>/,'').trim()),false);
});
test('negative mutation: unauthorized seller link/script is detected',()=>{
 assert.equal(checkHTML(a.replace('</body>','<a href="https://zen12.com/hnp">Buy Now</a></body>')),false);
 assert.equal(checkHTML(a.replace('</body>','<script src="https://example.org/track.js"></script></body>')),false);
});
test('negative mutation: the film cannot silently become autoplay',()=>{
 assert.equal(checkHTML(b.replace('</body>','<video autoplay src="x.mp4"></video></body>'),true),false);
});

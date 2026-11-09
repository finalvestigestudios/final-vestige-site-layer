/* FV Mind R240 self-contained source and disclosure gate tests.
 Run: node mind/r240/test_r240.cjs
 Execute before draft PR or commercial review; source-level only, NOT browser, checkout, merchant, or revenue QA. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.join(__dirname,'..');
const file={
 matrix:'r240/TOTAL-FOCUS-CLAIM-SOURCE-ELIGIBILITY.json',
 guide:'r240/TOTAL-FOCUS-33-MINUTE-BUYERS-EVIDENCE-GUIDE-UNPUBLISHED.md',
 html:'r240/TOTAL-FOCUS-OFFER-GUIDE-WP-SOURCE-PREVIEW-UNPUBLISHED.html',
 plan:'r240/CONVERSION-PROOF-MERCHANT-ELIGIBILITY-ACCEPTANCE.md',
 gorilla:'r239/GORILLA-IN-THE-SCAN-UNPUBLISHED.md',
 oldplan:'r239/OFFER-FUNNEL-BLOCKER-AB-ATTRIBUTION-ACCEPTANCE.md',
 a:'r237/zen12-presell-A.html',b:'r237/zen12-presell-B.html',vtt:'r237/zen12-42s-concept.vtt'
};
const frozen={"matrix":"de788bc2","guide":"b5aa48f8","html":"f5dcc27b","plan":"3e85c0ee","gorilla":"804fe95f","oldplan":"b20fe4d8","a":"1ad6e4c3","b":"4b264450","vtt":"fdd2559c"};
const matrixIdentity='fcada25e';
function fnv32(s){let h=2166136261;for(let i=0;i<s.length;i++)h=Math.imul((h^s.charCodeAt(i)),16777619)>>>0;return h.toString(16).padStart(8,'0');}
const read=k=>fs.readFileSync(path.join(root,file[k]),'utf8');
let text={};for(const k of Object.keys(file)){text[k]=read(k);assert.equal(fnv32(text[k]),frozen[k],k+' full source fingerprint');}
const m=JSON.parse(text.matrix);
function inspectMatrix(x){
 assert.equal(x.sources.length,16,'16 sources');assert.equal(x.claims.length,24,'24 claims');assert.equal(x.gates.length,16,'16 gates');
 assert.equal(fnv32(JSON.stringify(x)),matrixIdentity,'whole R240 matrix immutable including commercial and attribution fields');
 const ids=new Set(x.sources.map(s=>s.id));assert.equal(ids.size,x.sources.length);
 assert(x.sources.every(s=>/^https:\/\//.test(s.url)&&!/[\s<>]/.test(s.url)),'real https sources');
 assert(x.claims.every(c=>ids.has(c.source_id)),'claims map to valid sources');
 assert(x.gates.every(g=>g.status==='HARD_HOLD'),'all gates HARD HOLD');
 assert.equal(x.affiliate_url,null,'no earning URL');assert.equal(x.final_cart_price,null,'no false price');
 assert.equal(x.checkout_validated,false,'checkout untested');assert.equal(x.merchant_links_in_public_html,false,'no active merchant links');
 assert.equal(x.experiment.status,'NOT_LIVE');assert.equal(x.measurement.net_revenue_per_1000_qualified_humans,null);
 assert(x.creator_to_product.every(x=>x.asset_id===null),'never invent Grok asset IDs');
}
function inspectGuide(s){
 assert(s.trim().split(/\s+/).length>=2000,'deep 2k buyer guide');
 for(const t of ['33-minute','47 MB','five sessions per year','14-day','no product-specific trial','product-specific','not to state that it works as advertised','may earn a commission','UNPUBLISHED'])assert(s.toLowerCase().includes(t.toLowerCase()),'guide missing '+t);
 assert(!/https:\/\/(?:www\.)?(?:hypnosislive|zen12|inspire3|brainwaveshots|awin1)\.com/i.test(s),'no active seller URL in public-facing guide');
 assert(!/I (?:used|tested|purchased|listened to) (?:the |this )?(?:recording|product)/i.test(s),'no fake personal test');
}
function inspectHtml(s){
 assert(s.length>8000,'substantial buyer page');
 assert(!/<(?:script|iframe|form|input|video|audio)\b/i.test(s),'no scripts, embed, capture, or video');
 assert(!/\bon(?:click|load|error|focus|submit|mouseover)\s*=/i.test(s),'no inline handlers');
 assert(!/<a\b[^>]*href\s*=\s*["'](?:https?:)?\/\/(?:www\.)?(?:hypnosislive|zen12|inspire3|brainwaveshots|awin1)\.com/i.test(s),'no merchant click');
 assert(!/<a\b[^>]*href\s*=\s*["'](?:javascript:|data:|\/\/)/i.test(s),'no URL exploits');
 const buttons=[...s.matchAll(/<button\b([^>]*)>/gi)];assert.equal(buttons.length,1,'single disabled CTA');
 assert(/(?:^|\s)disabled(?:\s|=|$)/.test(buttons[0][1]),'native disable attribute, not CSS class');
 const d=s.indexOf('may earn a commission'),b=s.indexOf('<button');
 assert(d>0&&b>d&&b-d<600,'clear adjacent FTC disclosure before CTA');
 assert(s.includes('https://finalvestige.com/focus/'),'only existing Focus route');
 assert(s.includes('aria-labelledby="r240-title"')&&s.includes(':focus-visible'),'semantics and focus styling');
}
function inspectGorilla(s){
 assert(s.includes('**That between-group difference was not statistically significant.**'),'nonsignificant comparison caveat');
 assert(s.includes('**volume of the rectangular box enclosing the inserted gorilla**'),'correct 48x volume');
 assert(s.includes('**12 had fixated its location'),'correct gaze result');
 assert(s.includes('R227 manuscript'),'collision explicitly disclosed');
}
function inspectOldPlan(s){
 assert(s.includes('**minus** refunds')&&s.includes('only to the extent each has not already been withheld'),'accounting signs and double deduction');
 assert(s.includes('**Collision confirmed:** R227'),'specific duplicate article gate');
}
function inspectNewPlan(s){
 for(const t of ['NOT COMPUTABLE','HARD HOLD','R237','Grok','Praxxis','Jetpack','confirmed','cleared','7-day','30-day','utm_campaign','no duplicated tag','five sessions per year'])
 assert(s.toLowerCase().includes(t.toLowerCase()),'plan missing '+t);
 assert(s.length>8000);
}
function inspectA(s){
 assert(!/<(?:script|iframe|video|audio|form|input)\b/i.test(s));
 assert(!/<a\b[^>]*href\s*=\s*["'](?:https?:)?\/\/(?:www\.)?(?:zen12|inspire3|brainwaveshots|hypnosislive|awin1)\.com/i.test(s));
 assert(s.includes('may earn a commission')&&s.includes('<button')&&/\bdisabled\b/.test(s.slice(s.indexOf('<button'),s.indexOf('</button>'))));
}
function inspectVtt(s){assert(s.startsWith('WEBVTT'));const cues=[...s.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)];assert.equal(cues.length,7);let end=0;for(const v of cues){const n=v.slice(1).map(Number);let start=((n[0]*60+n[1])*60+n[2])*1000+n[3],stop=((n[4]*60+n[5])*60+n[6])*1000+n[7];assert.equal(start,end);assert(stop>start);end=stop;}assert.equal(end,42000);}
inspectMatrix(m);inspectGuide(text.guide);inspectHtml(text.html);inspectGorilla(text.gorilla);inspectOldPlan(text.oldplan);inspectNewPlan(text.plan);
inspectA(text.a);inspectA(text.b);inspectVtt(text.vtt);
assert.equal(text.b.replace(/<details class="card" id="optional-film">[\s\S]*?<\/details>/,''),text.a,'Zen12 A/B buyer text identical except optional film');
assert(text.b.includes('id="optional-film"')&&!text.a.includes('id="optional-film"'),'video B only');
let rejected=0;function reject(fn,label){let threw=false;try{fn();}catch(e){threw=true;}assert(threw,'UNDETECTED '+label);rejected++;}
for(const kind of ['sources','claims','gates'])for(let i=0;i<m[kind].length;i++){
 let x=JSON.parse(JSON.stringify(m));if(kind==='sources')x.sources[i].url+='?fake=1';else if(kind==='claims')x.claims[i].text+=' guaranteed focus';else x.gates[i].status='APPROVED';
 reject(()=>inspectMatrix(x),kind+'-'+i);
}
for(const [k,value] of [['affiliate_url','https://fake.invalid/aff=1'],['checkout_validated',true],['merchant_links_in_public_html',true],['final_cart_price',1]]){
 let x=JSON.parse(JSON.stringify(m));x[k]=value;reject(()=>inspectMatrix(x),k);
}
for(const [label,bad] of [
 ['enabled',text.html.replace(' disabled aria-disabled',' aria-disabled')],
 ['removed-disclosure',text.html.replace('may earn a commission','no fee ever')],
 ['merchant-link',text.html+'<a href="https://hypnosislive.com/mental-skills/total-focus">Buy</a>'],
 ['script',text.html+'<script src="//tracker.invalid/a.js"></script>'],
 ['form',text.html+'<form></form>'],
 ['handler',text.html+'<span onclick="sale()">Hi</span>']
])reject(()=>inspectHtml(bad),label);
reject(()=>inspectGorilla(text.gorilla.replace('was not statistically significant','proved familiarity made you worse')),'2010 nuance');
reject(()=>inspectGorilla(text.gorilla.replace('**volume of the rectangular box enclosing the inserted gorilla**','size')),'2013 volume');
reject(()=>inspectOldPlan(text.oldplan.replace('**minus** refunds','**plus** refunds')),'cost direction');
reject(()=>inspectOldPlan(text.oldplan.replace('**Collision confirmed:** R227','Other manuscripts')),'R227 specific');
reject(()=>inspectGuide(text.guide+'\nhttps://hypnosislive.com/mental-skills/total-focus'),'unexpected merchant link');
reject(()=>inspectNewPlan(''),'empty plan');
reject(()=>inspectVtt(text.vtt.replace('00:00:42.000','00:00:41.000')),'caption end');
assert.equal(rejected,69,'expected 56 individual identity mutations + 13 activation/content failures');
console.log('PASS R240 source-level exact-fingerprint matrix/guide/html/plans, R239 full-paper corrections, R237 Zen12 A/B no-JS disabled controls and 42s captions; '+rejected+'/'+rejected+' dangerous synthetic changes rejected. No real browser/merchant/affiliate/sale verification.');

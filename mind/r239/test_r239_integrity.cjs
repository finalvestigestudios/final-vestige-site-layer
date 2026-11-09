/* R239 complete-registry and source-integrity guard. Native command:
   node mind/r237/test_r237.cjs && node mind/r238/test_r238.cjs && node mind/r239/test_r239_integrity.cjs
   Zero npm/network dependencies. SOURCE ONLY; not browser, CMS, affiliate, or merchant QA. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const root=path.join(__dirname,'..');
const read=relative=>fs.readFileSync(path.join(root,relative),'utf8');
function fnv32(s){let h=2166136261;for(let i=0;i<s.length;i++)h=Math.imul((h^s.charCodeAt(i)),16777619)>>>0;return h.toString(16).padStart(8,'0');}
const EXPECTED={
 r238:{sources:'77fb0b42',claims:'7b2e2425',gates:'83f30948',counts:[15,20,16]},
 r239:{sources:'4434c150',claims:'01dd7703',gates:'b96bb701',counts:[14,22,16]}
};
const R238=JSON.parse(read('r238/R238-CLAIM-SOURCE-COMMERCE-HOLD.json'));
const R239=JSON.parse(read('r239/CLAIM-SOURCE-OFFER-AND-REVENUE-GATES.json'));
const article=read('r239/GORILLA-IN-THE-SCAN-UNPUBLISHED.md');
const plan=read('r239/OFFER-FUNNEL-BLOCKER-AB-ATTRIBUTION-ACCEPTANCE.md');
const A=read('r237/zen12-presell-A.html');
const B=read('r237/zen12-presell-B.html');
const V=read('r237/zen12-42s-concept.vtt');
function integrity(m,expected,label){
 assert.equal(m.sources.length,expected.counts[0],label+' source count');
 assert.equal(m.claims.length,expected.counts[1],label+' claim count');
 assert.equal(m.gates.length,expected.counts[2],label+' gate count');
 for(const kind of ['sources','claims','gates']){
  assert.equal(fnv32(JSON.stringify(m[kind])),expected[kind],label+' exact immutable '+kind+' identities, URLs, claim text, statuses');
  assert.equal(new Set(m[kind].map(x=>x.id)).size,m[kind].length,label+' unique '+kind+' IDs');
 }
 const sourceIds=new Set(m.sources.map(s=>s.id));
 assert(m.sources.every(s=>/^https:\/\//.test(s.url)&&!/[\s<>]/.test(s.url)),label+' correct source URLs');
 assert(m.claims.every(c=>sourceIds.has(c.source_id)),label+' all claim references resolve');
 assert(m.gates.every(g=>g.status==='HARD_HOLD'),label+' hold all gates');
 assert.equal(m.commercial_activation??m.merchant_activation,false,label+' activation must remain false');
 assert.equal(('account_issued_affiliate_url' in m)?m.account_issued_affiliate_url:m.affiliate_link,null,label+' no earning link');
 assert.equal(m.revenue.net_revenue_per_1000_qualified_human_sessions,null,label+' revenue unknowable');
 assert.equal(('confirmed_paid_orders' in m.revenue)?m.revenue.confirmed_paid_orders:m.revenue.merchant_verified_paid_orders,null,label+' no invented paid orders');
}
function inspectArticle(s){
 assert.equal(fnv32(s),'d430737c','original investigation exact research fingerprint');
 for(const term of ['24 radiologists','Eighty-three percent','forty-eight times','2010','1999','separate','inattentional blindness','Change Blindness','NOT','Fieldbook','https://doi.org/10.1177/0956797613479386']) assert(s.toLowerCase().includes(term.toLowerCase()),'research boundary '+term);
 assert(!/https:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com/i.test(s),'investigation has no seller/product links');
 assert(!/we (?:tested|used|recommend) zen12|guaranteed (?:mental|focus|cure)/i.test(s),'no fabricated product experience/effectiveness');
}
function inspectPlan(s){
 assert.equal(fnv32(s),'b4c1bffa','complete reviewed plan immutable');
 assert(s.length>6500,'substantive plan present');
 for(const term of ['NOT COMPUTABLE','HARD HOLD','utm_campaign','qualified_human_session','confirmed_lead','paid_order','cleared_commission','7-day','30-day','Grok','Praxxis','Jetpack','UNRENDERED','NOT LIVE','founder'])assert(s.toLowerCase().includes(term.toLowerCase()),'plan missing '+term);
}
function inspectArm(s){
 assert(!/<(?:script|iframe|video|audio|form|input)\b/i.test(s),'no JS/media/form');
 assert(!/\bon(?:click|load|error|focus|submit|mouseover)\s*=/i.test(s),'no events');
 assert(!/<a\b[^>]*href\s*=\s*["'](?:https?:)?\/\/(?:www\.)?(?:zen12|inspire3|brainwaveshots|hypnosislive|awin1)\.com/i.test(s),'no merchant link');
 assert(!/<a\b[^>]*href\s*=\s*["'](?:javascript:|data:|\/\/)/i.test(s),'no dangerous href');
 const buttons=[...s.matchAll(/<button\b([^>]*)>/gi)];assert.equal(buttons.length,1,'exactly one purchase placeholder');
 assert(/(?:^|\s)disabled(?:\s|=|$)/i.test(buttons[0][1]),'native disabled');
 const d=s.indexOf('may earn a commission'),btn=s.indexOf('<button');
 assert(d>0&&btn>d&&btn-d<600,'FTC disclosure must precede adjacent button');
}
function inspectVideo(v){
 assert(v.startsWith('WEBVTT'),'captions file');
 const cues=[...v.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)];
 assert.equal(cues.length,7,'seven captions');
 let end=0;for(const c of cues){let p=c.slice(1).map(Number);let start=((p[0]*60+p[1])*60+p[2])*1000+p[3];let stop=((p[4]*60+p[5])*60+p[6])*1000+p[7];assert.equal(start,end);assert(stop>start);end=stop;}assert.equal(end,42000,'42s exact');
}
integrity(R238,EXPECTED.r238,'R238');integrity(R239,EXPECTED.r239,'R239');
inspectArticle(article);inspectPlan(plan);inspectArm(A);inspectArm(B);inspectVideo(V);
assert.equal(B.replace(/<details class="card" id="optional-film">[\s\S]*?<\/details>/,''),A,'A/B buyer text exact parity');
assert(!A.includes('id="optional-film"')&&B.includes('id="optional-film"'),'optional video B only');
let mutations=0;
function rejects(fn,label){let caught=false;try{fn();}catch(err){caught=true;}assert(caught,'UNDETECTED mutation '+label);mutations++;}
for(const [label,original,expected] of [['R238',R238,EXPECTED.r238],['R239',R239,EXPECTED.r239]]){
 for(const kind of ['sources','claims','gates']) for(let i=0;i<original[kind].length;i++){
  const mutant=JSON.parse(JSON.stringify(original));
  const item=mutant[kind][i];
  if(kind==='sources')item.url+='?tamper=1';
  else if(kind==='claims')item.text+=' misleading claim';
  else item.status='APPROVED';
  rejects(()=>integrity(mutant,expected,label+' corrupted '+kind+' '+i),label+'-'+kind+'-'+i);
 }
 for(const [field,edited] of [
 ['commercial_activation',true],['merchant_activation',true],
 ['account_issued_affiliate_url','https://fake.invalid/?aff=1'],
 ['affiliate_link','https://fake.invalid/?aff=1']
 ]){
  if(Object.prototype.hasOwnProperty.call(original,field)){const mutant={...original,[field]:edited};rejects(()=>integrity(mutant,expected,label+' '+field),label+'-'+field);}
 }
 const withSale=JSON.parse(JSON.stringify(original));withSale.revenue.net_revenue_per_1000_qualified_human_sessions=900;
 rejects(()=>integrity(withSale,expected,label+' fabricated KPI'),label+'-money');
}
for(const [label,mutant] of [
 ['enabled-A',A.replace(' disabled aria-',' aria-')],
 ['merchant-root-A',A.replace('<code>inspire3.com</code>','<a href="https://inspire3.com/">merchant</a>')],
 ['removed-disclosure',A.replace('may earn a commission','no relationship')],
 ['injected-form',B+'<form method="post"></form>'],
 ['tracking',B+'<script src="https://example.org/pixel.js"></script>'],
 ['javascript-link',A+'<a href="javascript:alert(1)">click</a>']
 ])rejects(()=>inspectArm(mutant),label);
rejects(()=>inspectVideo(V.replace('00:00:42.000','00:00:40.000')),'clip-time');
rejects(()=>inspectArticle(article+'\nhttps://zen12.com/hnp'),'editorial seller insertion');
rejects(()=>inspectPlan(''),'empty plan');
rejects(()=>inspectPlan(plan.replaceAll('NOT COMPUTABLE','UNKNOWN')),'lost KPI status');
assert.equal(mutations,119,'expected synthetic mutation count');
console.log('PASS R239: frozen R238 and R239 registry identity/source URL/claim-status/gates; protected original investigation and full conversion plan; disabled A/B and seven 0–42s captions; '+mutations+' unsafe synthetic mutations rejected. SOURCE ONLY.');

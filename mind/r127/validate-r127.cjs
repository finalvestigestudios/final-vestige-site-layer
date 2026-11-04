/* FV Mind R127 offline guardrails. Run: node mind/r127/validate-r127.cjs
 * Read-only, no network, no credentials, no tests that manufacture checkout/sales.
 */
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const dir=__dirname;
const read=(p)=>fs.readFileSync(path.join(dir,p),'utf8');
const A=read('zen12-guide-A-text-only.html');
const B=read('zen12-guide-B-optional-film-concept.html');
const investigation=read('white-bear-thought-suppression-investigation.md');
const guide=read('zen12-evidence-first-buyer-guide.md');
const plan=read('conversion-gates-creator-mapping-and-measurement.md');
const evidence=JSON.parse(read('claim-source-and-commerce-gates.json'));
let n=0;
function test(name,fn){fn();n++;process.stdout.write('PASS '+String(n).padStart(2,'0')+' '+name+'\n');}
function demand(cond,msg){assert.ok(cond,msg);}
const normalize=(s)=>s.replace(/<!--[^]*?-->/g,'').replace(/\s+/g,' ').trim();
test('standalone draft status',()=>demand(/DRAFT.*NOT PUBLISHED/i.test(investigation)));
test('investigation cites 1987 primary experiment',()=>demand(/pubmed\.ncbi\.nlm\.nih\.gov\/3612492/.test(investigation)));
test('investigation cites 2000 review',()=>demand(/10\.1146\/annurev\.psych\.51\.1\.59/.test(investigation)));
test('investigation cites 2023 EEG review',()=>demand(/10\.1371\/journal\.pone\.0286023/.test(investigation)));
test('no invented first-person usage claims',()=>demand(!/I (used|bought|tested|purchased) Zen12/i.test(investigation+' '+guide+' '+A+' '+B)));
test('source ledger >= 12 traceable URLs',()=>demand(evidence.sources.length>=12&&evidence.sources.every(s=>/^https:\/\//.test(s.url))));
test('claims ledger >= 18 explicit decisions',()=>demand(evidence.claims.length>=18&&evidence.claims.every(c=>c.id&&c.decision)));
test('every source referenced in claims exists',()=>{const ids=new Set(evidence.sources.map(s=>s.id));demand(evidence.claims.every(c=>c.basis.every(i=>ids.has(i))));});
test('closed gates >= 20',()=>demand(evidence.closed_gates.length>=20));
test('merchant acceptance withheld',()=>demand(evidence.selected_offer.eligibility.includes('HOLD')&&evidence.selected_offer.authorized_affiliate_url===null));
test('paid orders and net revenue unknown',()=>demand(evidence.selected_offer.merchant_reported_paid_conversions===null&&evidence.selected_offer.verified_net_revenue===null));
test('no false numerical net revenue claim',()=>demand(evidence.experiment.session_denominator==='UNKNOWN'));
test('A and B guide share the same textual body except optional film',()=>{const film=/<section class="panel" aria-labelledby="film">[\s\S]*?<\/section>/;demand(normalize(B.replace(film,''))===normalize(A));});
for(const [name,s] of [['A',A],['B',B]]){
 test(name+' no script, iframe or active video embed',()=>demand(!/<(?:script|iframe|video)\b/i.test(s)));
 test(name+' only authorized existing Focus free resource',()=>demand(/href="https:\/\/finalvestige\.com\/focus\/"/.test(s)));
 test(name+' no duplicate signup form',()=>demand(!/<form\b/i.test(s)));
 test(name+' no clickable merchant URL',()=>demand(!/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com)(?:\/|["'])/i.test(s)));
 test(name+' disclosure adjacent to natively disabled CTA',()=>{const p=s.indexOf('Prospective affiliate disclosure:'),b=s.indexOf('<button type="button"');demand(p>=0&&b>p&&b-p<650&&/<button[^>]*\bdisabled\b/.test(s.slice(b,b+180)));});
 test(name+' support no JS and reduced motion',()=>demand(/prefers-reduced-motion/.test(s)&&/<h1>/.test(s)&&/focus-visible/.test(s)));
 test(name+' no real sales or medical promises',()=>demand(!/guaranteed (increase|cure|wealth)|clinically proven to fix/i.test(s)));
}
test('B film storyboard has transcript',()=>demand(/aria-labelledby="film"/.test(B)&&/View 40-second transcript/.test(B)));
test('B film captions from 00:00 to 00:40',()=>demand(/00:00–00:06/.test(B)&&/00:33–00:40/.test(B)));
test('B film has accessible non-image poster',()=>demand(/class="film-poster"/.test(B)&&/role="img"/.test(B)));
test('buyer guide names conflicting seller pages',()=>demand(guide.includes('zen12.com/hnp')&&guide.includes('zen12.com/secret/')));
test('buyer guide identifies seller claims vs evidence',()=>demand(/seller describes/i.test(guide)&&/not.*independent/i.test(guide)));
test('campaign mapping has three separate topic routes',()=>demand(/Change blindness/.test(plan)&&/Mesmerism/.test(plan)&&/Attentional blink/.test(plan)));
test('staging and production release are explicitly gated',()=>demand(/founder.*release/i.test(plan)&&/WCAG/i.test(plan)));
test('commercial metric is net revenue per thousand qualified visits',()=>demand(/net revenue per 1,000 qualified human/i.test(plan)));
test('measurement distinguishes affiliate click vs actual paid conversion',()=>demand(/affiliate_outbound_click/.test(plan)&&/merchant_confirmed_paid_conversion/.test(plan)));
test('no PII fields proposed for analytics',()=>demand(/Exclude name, email, IP/.test(plan)));
test('both candidate HTML pages have only one free Focus CTA',()=>demand((A.match(/href="https:\/\/finalvestige\.com\/focus\/"/g)||[]).length===1&&(B.match(/href="https:\/\/finalvestige\.com\/focus\/"/g)||[]).length===1));
function mutationGuard(s){return /<button[^>]*\bdisabled\b/.test(s)&&/Prospective affiliate disclosure:/.test(s)&&!/href\s*=\s*["']https:\/\/zen12\.com\//.test(s);}
test('adversarial enabled buy button is caught',()=>demand(!mutationGuard(A.replace(' disabled aria-disabled="true"',' aria-disabled="false"'))));
test('adversarial missing disclosure is caught',()=>demand(!mutationGuard(A.replace('Prospective affiliate disclosure:',''))));
test('adversarial live merchant URL is caught',()=>demand(!mutationGuard(A.replace('</button>','</button><a href="https://zen12.com/hnp">Buy</a>'))));
console.log('FV Mind R127: '+n+' PASS; static content checks only. Browser, Node CI and commercial outcomes require independent verification.');

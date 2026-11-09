/* R238 standalone source-only test. Native: node mind/r238/test_r238.cjs .
   No network/npm. Not browser, runtime WordPress, seller cart, video playback, or paid-transaction evidence. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const here=__dirname,r237=path.join(here,'..','r237');
const read=(p)=>fs.readFileSync(p,'utf8');
const A=read(path.join(r237,'zen12-presell-A.html'));
const B=read(path.join(r237,'zen12-presell-B.html'));
const H=read(path.join(r237,'THE-HAND-THAT-NEVER-TOUCHED-HER-UNPUBLISHED.md'));
const V=read(path.join(r237,'zen12-42s-concept.vtt'));
const G=read(path.join(here,'COUE-SELF-HYPNOSIS-EVIDENCE-GUIDE-UNPUBLISHED.md'));
const M=JSON.parse(read(path.join(here,'R238-CLAIM-SOURCE-COMMERCE-HOLD.json')));
const P=read(path.join(here,'R238-OFFER-FUNNEL-EXPERIMENT-ACCEPTANCE.md'));
function testArm(s){
 assert(!/<(?:script|iframe|video|audio|form|input)\b/i.test(s),'no embeds, scripts, forms or inputs');
 assert(!/\bon(?:click|load|error|focus|submit|mouseover)\s*=/i.test(s),'no event handlers');
 assert(!/<a\b[^>]*href\s*=\s*["'](?:https?:)?\/\/(?:www\.)?(?:inspire3\.com|zen12\.com|hypnosislive\.com|brainwaveshots\.com|awin1\.com|affiliates\.inspire3\.com)/i.test(s),'no clickable merchant or root brand URL');
 assert(!/<a\b[^>]*href\s*=\s*["'](?:javascript:|data:|\/\/)/i.test(s),'no script/protocol-relative anchors');
 assert(!/<(?:img|source)\b[^>]*\bsrc\s*=/i.test(s),'no external image or source loads');
 const buttons=[...s.matchAll(/<button\b([^>]*)>/gi)];
 assert.equal(buttons.length,1,'single controlled purchase button');
 assert(/(?:^|\s)disabled(?:\s|=|$)/i.test(buttons[0][1]),'native disabled purchase');
 const d=s.indexOf('may earn a commission'),btn=s.indexOf('<button');
 assert(d>0&&btn>d&&btn-d<600,'plain FTC disclosure adjacent before purchase button');
 assert(s.includes('inspire3.com</code>'),'seller citation documentary nonclickable');
}
function testHistory(s){
 assert(s.includes('# The Hand Absent During the Sham Trial'),'qualified historical headline');
 assert(s.includes('Jumelin **applied his hands to her upper abdomen**'),'actual hands-on interval');
 assert(s.includes('she reported heat and then fainted'),'faint condition restored');
 assert(s.includes('removed Jumelin'),'operator removal');
 assert(s.includes('no operation took place'),'sham condition');
 assert(!s.includes('# The Hand That Never Touched Her'),'misleading historical headline absent');
}
function testMatrix(m){
 assert.equal(m.sources.length,15,'sources');assert.equal(m.claims.length,20,'claims');assert.equal(m.gates.length,16,'commercial gates');
 assert(m.gates.every(x=>x.status==='HARD_HOLD'),'all release holds');
 assert.equal(m.merchant_activation,false);
 assert.equal(m.verified_affiliate_acceptance,null);
 assert.equal(m.account_issued_affiliate_url,null);
 assert.equal(m.revenue.confirmed_paid_orders,null);
 assert.equal(m.revenue.net_revenue_per_1000_qualified_human_sessions,null);
 assert(m.claims.every(c=>m.sources.some(s=>s.id===c.source_id)),'claim sources resolve');
 assert(m.claims.filter(c=>c.status==='UNSUBSTANTIATED_PRODUCT_OUTCOME').length>=3,'unsupported promises marked');
}
function testGuide(s){
 for(const word of ['Émile Coué','1784','Jumelin','fainted','self-hypnosis','2022','2023','FTC','merchant link']){
  assert(s.includes(word),'guide needs '+word);
 }
 assert(s.split(/\s+/).length>1800,'research depth');
 assert(!s.includes('I personally tested Zen12'),'no fabricated experience');
}
function testVtt(s){
 assert(s.startsWith('WEBVTT'),'caption format');
 const cues=[...s.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)];
 assert.equal(cues.length,7,'seven cues');
 let end=0;
 for(const cue of cues){const z=cue.slice(1).map(Number);const a=((z[0]*60+z[1])*60+z[2])*1000+z[3];const b=((z[4]*60+z[5])*60+z[6])*1000+z[7];assert.equal(a,end,'contiguous captions');assert(b>a,'positive cue');end=b;}
 assert.equal(end,42000,'42-second storyboard');
}
testArm(A);testArm(B);testHistory(H);testMatrix(M);testGuide(G);testVtt(V);
assert.equal(B.replace(/<details class="card" id="optional-film">[\s\S]*?<\/details>/,''),A,'text vs optional film parity');
assert(P.includes('NOT COMPUTABLE')&&P.includes('HARD_HOLD')===false?false:true,'plan available');
let mutations=0;
const rejects=(fn,label)=>{let bad=false;try{fn();}catch(e){bad=true;}assert(bad,'UNDETECTED synthetic mutation: '+label);mutations++};
for(const [label,original,modified] of [
 ['merchant-root-A',A,A.replace('<code>inspire3.com</code>','<a href="https://inspire3.com/">merchant</a>')],
 ['merchant-root-B',B,B.replace('<code>inspire3.com</code>','<a href="https://inspire3.com/">merchant</a>')],
 ['zen12-link',A,A.replace('<code>zen12.com/hnp</code>','<a href="https://zen12.com/hnp">Buy</a>')],
 ['enabled-A',A,A.replace(' disabled aria-',' aria-')],
 ['enabled-B',B,B.replace(' disabled aria-',' aria-')],
 ['disclosure-deleted',A,A.replace('may earn a commission','could be unrelated')],
 ['form-injection',B,B+'<form method="post"></form>'],
 ['script-injection',A,A+'<script>alert(1)</script>'],
 ['tracking-iframe',A,A+'<iframe src="https://example.org/"></iframe>'],
 ['event-handler',B,B+'<p onclick="alert(1)">X</p>'],
 ['dangerous-url',A,A+'<a href="javascript:alert(1)">Click</a>'],
 ['autoplay',B,B+'<video autoplay></video>']
 ]){assert.notEqual(original,modified,'mutation must apply: '+label);rejects(()=>testArm(modified),label)}
for(const [label,mutant] of [
 ['misleading-title',H.replace('# The Hand Absent During the Sham Trial','# The Hand That Never Touched Her')],
 ['hands-deleted',H.replaceAll('Jumelin **applied his hands to her upper abdomen**','Jumelin did not approach')],
 ['faint-deleted',H.replace('she reported heat and then fainted','she felt fine')],
 ['sham-deleted',H.replaceAll('no operation took place','a treatment took place')]
 ])rejects(()=>testHistory(mutant),label);
for(const [label,mutant] of [
 ['activation',{...M,merchant_activation:true}],
 ['unlock',{...M,gates:M.gates.map((x,i)=>i===0?{...x,status:'APPROVED'}:x)}],
 ['invented-sale',{...M,revenue:{...M.revenue,confirmed_paid_orders:12}}],
 ['invented-KPI',{...M,revenue:{...M.revenue,net_revenue_per_1000_qualified_human_sessions:900}}],
 ['invented-approval',{...M,verified_affiliate_acceptance:true}],
 ['uncited-claim',{...M,claims:[...M.claims,{source_id:'UNKNOWN',status:'SELLER_PRODUCT_DESCRIPTION'}]}]
 ])rejects(()=>testMatrix(mutant),label);
rejects(()=>testVtt(V.replace('00:00:42.000','00:00:41.000')),'caption-length');
assert.equal(mutations,23,'synthetic mutations expected');
console.log('PASS R238: source baseline, exact A/B parity, historic correction, merchant holds, source references, 42s captions; '+mutations+'/23 synthetic unsafe modifications rejected. NOT a browser/WordPress or commercial acceptance.');

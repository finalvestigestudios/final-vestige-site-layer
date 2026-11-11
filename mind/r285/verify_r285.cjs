'use strict';
// FV Mind R285: node mind/r285/verify_r285.cjs
// Static/source contract + synthetic mutation checks. Not a substitute for production QA.
const R='mind/r285/';
const PATHS={article:R+'THE-WITNESS-WHO-WAS-CERTAIN-THEY-WOULD-NOTICE-UNPUBLISHED.md',
a:'mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html',
b:R+'ZEN12-CANONICAL-VIDEO-VARIANT-B-LOCAL-UNPUBLISHED.html',
hub:R+'MIND-ARCHIVE-CANONICAL-HUB-INSERT-UNPUBLISHED.html',
source:R+'render_42sec.py',vtt:R+'mind_42sec_en.vtt',poster:R+'mind_42sec_poster.svg',
matrix:R+'PRODUCT-CLAIM-SOURCE-COMMERCE-AND-VIDEO-MATRIX.json',
plan:R+'CANONICAL-ONE-OFFER-VIDEO-AND-REVENUE-ACCEPTANCE.md'};
const need=(ok,msg)=>{if(!ok)throw Error('R285 FAIL '+msg)};
const clone=x=>JSON.parse(JSON.stringify(x));
function buyerBody(s){
 const start=s.indexOf('<section aria-labelledby="why">'),end=s.indexOf('</main>',start);
 need(start>=0&&end>start,'buyer section exists');
 return s.slice(start,end).replace(/<aside class="film"[\s\S]*?<\/aside>/i,'').replace(/\s+/g,' ');
}
function verify(d){
 for(const k of Object.keys(PATHS))need(typeof d[k]==='string'&&d[k].length>200,'blob '+k);
 const m=JSON.parse(d.matrix);
 need(m.revision==='r285'&&m.status==='DRAFT_UNPUBLISHED_COMMERCIAL_HARD_HOLD','draft status');
 need(!m.verified_account_permission&&!m.external_affiliate_urls_active,'account permission withheld');
 need(m.commercial_gates.length===16&&new Set(m.commercial_gates.map(g=>g.id)).size===16,'16 distinct gates');
 need(m.commercial_gates.every(g=>g.state==='HARD_HOLD'),'all authorization gates hard hold');
 need(m.source_register.length>=24&&new Set(m.source_register.map(x=>x.id)).size===m.source_register.length,'unique source register');
 need(m.claims.length>=32&&m.claims.every(c=>m.source_register.some(s=>s.id===c.source_id)),'claims with sources');
 need(m.canonical_offer_decision.chosen_candidate==='zen12_premium'&&!m.canonical_offer_decision.authorized_to_activate,'one held offer');
 need(m.canonical_offer_decision.canonical_a===PATHS.a&&m.canonical_offer_decision.canonical_b_candidate===PATHS.b,'canonical A/B paths');
 need(m.canonical_offer_decision.paid_fallback.startsWith('NO AUTHENTICATED'),'no invented paid fallback');
 need(m.original_media_proof.duration_seconds===42&&m.original_media_proof.deploy_or_host_approved===false,'rendered but not released');
 need(m.original_media_proof.source_control_status.includes('BINARY_NOT_IN_GITHUB'),'binary provenance truthful');
 need(m.measurement.status==='NOT_COMPUTABLE'&&m.measurement.numerator.includes('settled'),'verified revenue only');
 for(const [k,s] of [['a',d.a],['b',d.b],['hub',d.hub]]){
  need(!/<\s*(script|form|iframe|object|embed|audio)\b/i.test(s),'forbidden HTML '+k);
  need(!/\bon\w+\s*=|javascript:|data:text\/html/i.test(s),'event/js '+k);
  need(!/\bhref\s*=\s*['"]https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|payhip\.com|affiliates\.inspire3\.com)/i.test(s),'active paid href '+k);
  need(!/<img\b[^>]+src\s*=\s*['"]https?:/i.test(s),'remote pixel '+k);
  need(s.includes('https://finalvestige.com/focus/'),'single Focus path '+k);
  need(/affiliate/i.test(s)&&/commission/i.test(s),'nearby disclosure '+k);
  need(/<button\b[^>]*\bdisabled\b/i.test(s),'disabled commerce '+k);
 }
 need(!/<video\b/i.test(d.a),'A no film');
 need((d.b.match(/<video\b/gi)||[]).length===1,'B one video');
 need(/<video\b[^>]*\bcontrols\b[^>]*\bpreload="none"/i.test(d.b),'manual video');
 need(!/\bautoplay\b/i.test(d.b),'no autoplay');
 need(/src="fv_mind_r285_42s_silent\.mp4"/i.test(d.b),'relative video path');
 need(/kind="captions"/i.test(d.b)&&/src="mind_42sec_en\.vtt"/i.test(d.b),'caption track');
 need(/poster="mind_42sec_poster\.svg"/i.test(d.b),'poster');
 need(d.b.includes('Complete plain-text film transcript'),'transcript available');
 need(d.b.includes('NOT committed or hosted'),'no hosting misrepresentation');
 need(buyerBody(d.a)===buyerBody(d.b),'same buyer content outside film');
 need(d.poster.includes('<title')&&d.poster.includes('<desc'),'accessible poster');
 need(d.vtt.startsWith('WEBVTT'),'WebVTT signature');
 const cues=[...d.vtt.matchAll(/00:00:(\d\d)\.000 --> 00:00:(\d\d)\.000/g)];
 need(cues.length===7&&cues.every((x,i)=>+x[1]===i*6&&+x[2]===(i+1)*6),'seven contiguous 6s captions');
 need(d.source.includes('DURATION=42')&&d.source.includes('W,H,FPS=960,540,12'),'film source config');
 need(d.source.includes("'+faststart'")&&d.source.includes("'-an'"),'silent fast-start H264');
 need(d.article.split(/\s+/).length>=2400,'substantive investigation');
 for(const t of ['change-blindness blindness','https://doi.org/10.3758/BF03208840','https://pubmed.ncbi.nlm.nih.gov/12470620/','https://pubmed.ncbi.nlm.nih.gov/37205669/'])need(d.article.toLowerCase().includes(t.toLowerCase()),'science evidence '+t);
 need(/NOT_COMPUTABLE/.test(d.plan)&&/7-day/.test(d.plan)&&/Dispatch/.test(d.plan),'cohort+consent plan');
 return {status:'PASS',blobs:Object.keys(PATHS).length,sources:m.source_register.length,claims:m.claims.length,held_gates:m.commercial_gates.length};
}
function adversarial(d){
 const mutants=[
 ['permission',x=>{let m=JSON.parse(x.matrix);m.verified_account_permission=true;x.matrix=JSON.stringify(m)}],
 ['affiliate',x=>{let m=JSON.parse(x.matrix);m.external_affiliate_urls_active=true;x.matrix=JSON.stringify(m)}],
 ['gate',x=>{let m=JSON.parse(x.matrix);m.commercial_gates[0].state='PASS';x.matrix=JSON.stringify(m)}],
 ['missinggate',x=>{let m=JSON.parse(x.matrix);m.commercial_gates.pop();x.matrix=JSON.stringify(m)}],
 ['fakepaidsku',x=>{let m=JSON.parse(x.matrix);m.canonical_offer_decision.paid_fallback='VERIFIED';x.matrix=JSON.stringify(m)}],
 ['fakehosted',x=>{let m=JSON.parse(x.matrix);m.original_media_proof.deploy_or_host_approved=true;x.matrix=JSON.stringify(m)}],
 ['fakerevenue',x=>{let m=JSON.parse(x.matrix);m.measurement.status='CONFIRMED';x.matrix=JSON.stringify(m)}],
 ['buyerchange',x=>{x.b=x.b.replace('48 MP3 files','85 MP3 files')}],
 ['affiliatehref',x=>{x.b=x.b.replace('</main>','<a href="https://zen12.com/aff/fake">Buy</a></main>')}],
 ['videoautoplay',x=>{x.b=x.b.replace('<video controls','<video autoplay controls')}],
 ['novideo',x=>{x.b=x.b.replace('<video controls','<div controls')}],
 ['nocaption',x=>{x.b=x.b.replace('kind="captions"','kind="metadata"')}],
 ['noposter',x=>{x.b=x.b.replace('poster="mind_42sec_poster.svg"','')}],
 ['notranscript',x=>{x.b=x.b.replace('Complete plain-text film transcript','No transcript')}],
 ['missingcue',x=>{x.vtt=x.vtt.replace('00:00:36.000 --> 00:00:42.000','00:00:36.000 --> 00:00:41.000')}],
 ['longvideo',x=>{x.source=x.source.replace('DURATION=42','DURATION=60')}],
 ['sound',x=>{x.source=x.source.replace("'-an',str(out)","'-c:a','aac',str(out)")}],
 ['script',x=>{x.hub=x.hub.replace('</section>','<script>alert(1)</script></section>')}],
 ['signup',x=>{x.hub=x.hub.replace('</section>','<form><input type="email"></form></section>')}],
 ['pixel',x=>{x.hub=x.hub.replace('</section>','<img src="https://tracker.example/pixel"></section>')}],
 ['noarticle',x=>{x.article=x.article.replace('https://doi.org/10.3758/BF03208840','NO_SOURCE')}],
 ['disablegone',x=>{x.b=x.b.replace(/\bdisabled\b(?=\s+aria-describedby)/,'')}],
 ['disclosegone',x=>{x.b=x.b.replace('Prospective affiliate disclosure:','NO DISCLOSURE:')}]
 ];
 let blocked=0,escaped=[];
 for(const [n,fn] of mutants){const test=clone(d);fn(test);try{verify(test);escaped.push(n)}catch(e){blocked++}}
 need(!escaped.length,'escaped mutations '+escaped.join(','));
 return {blocked,total:mutants.length};
}
if(typeof module!=='undefined')module.exports={verify,adversarial,PATHS};
if(typeof require!=='undefined' && typeof module!=='undefined' && require.main===module){
 const fs=require('node:fs'),path=require('node:path'),root=path.resolve(__dirname,'../..');
 const data=Object.fromEntries(Object.entries(PATHS).map(([k,p])=>[k,fs.readFileSync(path.join(root,p),'utf8')]));
 console.log(JSON.stringify({baseline:verify(data),mutations:adversarial(data)},null,2));
}

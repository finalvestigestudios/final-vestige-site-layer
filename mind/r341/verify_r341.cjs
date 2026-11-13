// R341: native Node v22+ source-only release guard. No network, no real browser, no merchant calls.
// Run: node mind/r341/verify_r341.cjs from repository root.
const fs=require('node:fs'),assert=require('node:assert/strict');
const d='mind/r341/',a=fs.readFileSync(d+'zen12_A.html','utf8'),b=fs.readFileSync(d+'zen12_B.html','utf8');
const matrix=JSON.parse(fs.readFileSync(d+'claims.json','utf8'));
const attr=JSON.parse(fs.readFileSync(d+'attribution.json','utf8'));
let count=0;function check(ok,msg){assert.ok(ok,msg);count++;}
function safety(s,label){
check(/<html lang="en">/.test(s),label+' language');
check(/name="viewport"/.test(s),label+' viewport');
check(/noindex,nofollow/.test(s),label+' noindex');
check(/<main id="main"/.test(s),label+' main');
check(/<h1>/.test(s),label+' heading');
check(/button type="button" disabled aria-disabled="true"/.test(s),label+' native disabled CTA');
check(/If you purchase through an authorized link/.test(s),label+' adjacency disclosure');
check(!/<script\b/i.test(s),label+' no JavaScript');
check(!/<form\b/i.test(s),label+' no new forms');
check(!/\b(?:autoplay|onload|onclick|onerror)\s*=/i.test(s),label+' no autoplay/inline handlers');
check(!/href=["'][^"']*(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(s),label+' no merchant href');
check(!/\b(?:iframe|object|embed)\b/i.test(s),label+' no embedded vendor assets');
check(/https:\/\/finalvestige.com\/focus\//.test(s),label+' preserve Focus');
check(/--gold:#d1b47b/.test(s),label+' brand tokens');
check(/focus-visible/.test(s),label+' keyboard focus');
check(/prefers-reduced-motion/.test(s),label+' reduced motion');
check(!/href=["']https?:\/\/[^"']*payhip\.com/i.test(s),label+' no unknown Payhip CTA');
}
safety(a,'A');safety(b,'B');
const strip=(s)=>s.replace(/<section class="story"[\s\S]*?<\/section>/,'').replace(/Review [AB]<\/title>/,'Review X</title>');
check(strip(a)===strip(b),'A and B substantive text exact parity');
check(/<details>/.test(b)&&/42-second/.test(b),'B optional transcript');
check(!/<video\b/.test(b),'B does not claim broken playable video');
check(matrix.products.length===5,'5 exact seller package/offer records');
check(Object.values(matrix.gates).every(x=>x===false),'all merchant gates closed');
check(matrix.evidence.every(x=>typeof x.source==='string'&&x.source.startsWith('https://')),'every research claim source URL');
check(matrix.evidence.every(x=>x.product_proof===false),'no fabricated product trials');
check(attr.allowed_events.includes('affiliate_outbound')&&attr.allowed_events.includes('affiliate_confirmed_commission'),'click separate from money');
check(attr.kpi.includes('qualified_human_sessions'),'net revenue KPI');
const history=fs.readFileSync(d+'ARTICLE.md','utf8');check(history.split(/\s+/).length>1400,'substantive deep article');
check(/Puységur/.test(history),'evidence-history context');
const cap=fs.readFileSync(d+'original_42s.vtt','utf8');check((cap.match(/-->/g)||[]).length===6,'six 42-second caption segments');
const hub=fs.readFileSync(d+'mind-hub-review.html','utf8');check(/noindex,nofollow/.test(hub),'hub not publishable indexed');
console.log('PASS '+count+' R341 source checks; no browser/CI/merchant verification implied');
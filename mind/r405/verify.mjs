// R405 source-only offline regression tests.
// node mind/r405/verify.mjs (run from repository root; no packages, no network).
import fs from 'node:fs';
import assert from 'node:assert/strict';
const base='mind/r405/';
const read=p=>fs.readFileSync(base+p,'utf8');
const A=read('ZEN12_A_TEXT_GUIDE.html');
const B=read('ZEN12_B_OPTIONAL_STORYBOARD.html');
const hub=read('MIND_HUB_SOURCE_ONLY.html');
const matrix=JSON.parse(read('CLAIMS_AND_PERMISSION_MATRIX.json'));
const vtt=read('R405_SECOND_TARGET_42S.vtt');
const svg=read('R405_SECOND_TARGET_POSTER.svg');
const guide=read('ATTENTIONAL_BLINK_BUYER_INVESTIGATION.md');
const plan=read('CONVERSION_ACCEPTANCE_AND_CREATOR_MAP.md');
const tests=[];
const check=(name,fn)=>tests.push({name,fn});
check('separate A/B docs',()=>assert.notEqual(A,B));
check('same main substantive buyer text',()=>{
const main=s=>s.match(/<main id="main">([\s\S]*?)<\/main>/)?.[1]?.replace(/<section aria-labelledby="film"[\s\S]*?<\/section>/,'');
assert.equal(main(A),main(B));
});
for (const [name,html] of [['A',A],['B',B],['hub',hub]]) {
check(name+' lang and viewport',()=>{assert.match(html,/<html lang="en">/);assert.match(html,/name="viewport"/);});
check(name+' zero script tags and forms',()=>{assert.doesNotMatch(html,/<\s*(script|iframe|form)\b/i);});
check(name+' no merchant or affiliate URL in active link',()=>{assert.doesNotMatch(html,/<a\b[^>]*href=["'][^"']*(zen12|inspire3|hypnosislive|brainwaveshots)/i);});
check(name+' no external trackers',()=>assert.doesNotMatch(html,/gtag\(|dataLayer|fbq\(|pixel\.gif|googletagmanager/i));
check(name+' no autoplay',()=>assert.doesNotMatch(html,/\bautoplay\b/i));
check(name+' content independently readable without JS',()=>assert.match(html,/<main[\s>]/));
}
for(const [name,html] of [['A',A],['B',B]]) {
 check(name+' native-disabled commercial button',()=>assert.match(html,/<button\b(?=[^>]*\bdisabled\b)[^>]*>/));
 check(name+' disclosure beside offer',()=>assert.match(html,/<p class="disclosure">[\s\S]{0,550}<button type="button" disabled/));
 check(name+' keeps existing single Focus destination',()=>assert.match(html,/https:\/\/finalvestige\.com\/focus\//));
 check(name+' primary research',()=>assert.match(html,/1500880[\s\S]*17488185/));
 check(name+' no price promise',()=>assert.doesNotMatch(html,/\$\s?\d/));
}
check('B only has optional original poster',()=>{assert.doesNotMatch(A,/SECOND_TARGET_POSTER/);assert.match(B,/R405_SECOND_TARGET_POSTER\.svg/);assert.match(B,/Read the 42-second transcript/);});
check('original SVG valid structural root, no scripts, no external assets',()=>{assert.match(svg,/<svg[^>]+viewBox/);assert.match(svg,/<title/);assert.doesNotMatch(svg,/<script|<image|href=|onload=/i);});
check('VTT six exactly contiguous cues ending at 42s',()=>{
 const matches=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.\d{3} --> (\d\d):(\d\d):(\d\d)\.\d{3}/g)];
 assert.equal(matches.length,6);
 const secs=(h,m,s)=>Number(h)*3600+Number(m)*60+Number(s);
 matches.forEach((m,i)=>{assert.equal(secs(m[1],m[2],m[3]),i*7);assert.equal(secs(m[4],m[5],m[6]),(i+1)*7);});
});
check('32 claims and 27 held gates',()=>{assert.equal(matrix.claims.length,32);assert.equal(matrix.commercial_gates.length,27);assert.ok(matrix.commercial_gates.every(g=>g.status==='HOLD'));});
check('claims cite existing sources or deliberately null',()=>{const ids=new Set(matrix.sources.map(s=>s.id));matrix.claims.forEach(c=>(c.source_id||'').split(',').filter(Boolean).forEach(id=>assert.ok(ids.has(id))));});
check('research not substituted for SKU proof',()=>{assert.match(guide,/does not establish that twelve minutes/);assert.match(guide,/not a paid SKU|not a paid SKU/i);});
check('plan includes full measurement and withheld links',()=>{for(const term of ['qualified_session','confirmed_lead','affiliate_click','merchant_confirmed_purchase','refund','NOT COMPUTABLE','HARD HOLD'])assert.ok(plan.includes(term),term);});
let passed=0;for(const t of tests){try{t.fn();passed++;}catch(e){console.error('FAIL',t.name,e.message);process.exitCode=1;}}
console.log('R405 '+passed+'/'+tests.length+' offline checks passed');

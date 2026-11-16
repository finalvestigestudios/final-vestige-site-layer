// Mind R411 reproducible source checks. Run: node mind/r411/verify.mjs
// Static gates do not substitute for browser, CMS, checkout, partner authorization or paid-sales tests.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
const dir=dirname(fileURLToPath(import.meta.url));
const read=(name)=>readFileSync(join(dir,name),'utf8');
const A=read('ZEN12_A_TEXT.html');
const B=read('ZEN12_B_OPTIONAL_FILM.html');
const hub=read('MIND_ARCHIVE_SOURCE_ONLY.html');
const article=read('THE_HAND_THAT_WASNT_YOURS.md');
const vtt=read('ORIGINAL_42S_CAPTIONS.vtt');
const dossier=read('CONVERSION_ACCEPTANCE.md');
const matrix=JSON.parse(read('CLAIM_PERMISSION_MATRIX.json'));
const cases=[];
const check=(name,fn)=>cases.push({name,fn});
const assertHTML=(file,txt)=>{
  assert.match(txt,/^<!doctype html>/i,file);
  assert.match(txt,/<html lang="en">/,file);
  assert.match(txt,/<meta name="viewport"/,file);
  assert.match(txt,/<meta name="robots" content="noindex,nofollow">/,file);
  assert.doesNotMatch(txt,/<(?:script|iframe|form|audio|video|source)\b/i,file);
  assert.doesNotMatch(txt,/\bon(?:click|load|error|submit|mouseover)\s*=/i,file);
  assert.doesNotMatch(txt,/\b(?:autoplay|formaction|data-track|data-pixel)\s*=/i,file);
  assert.doesNotMatch(txt,/href=["'][^"']*(?:aff_id|affiliate_id|partner_id|referral_id|click_id)=/i,file);
};
check('A/B exact substantive copy parity',()=>assert.equal(B.replace(/<section id="optional-film"[\s\S]*?<\/section>/,''),A));
check('A complete valid static/no-index HTML',()=>assertHTML('A',A));
check('B complete valid static/no-index HTML',()=>assertHTML('B',B));
check('hub complete valid static/no-index HTML',()=>assertHTML('hub',hub));
for(const [name,txt] of [['A',A],['B',B]]){
check(name+' genuinely disabled commercial button',()=>{
  const m=txt.match(/<button\b[^>]*>/ig)||[];
  assert.equal(m.length,1);
  assert.match(m[0],/\sdisabled(?:\s|>)/i);
  assert.doesNotMatch(m[0],/\b(?:href|formaction)\s*=/i);
});
check(name+' affiliate disclosure immediately inside offer',()=>{
 const block=txt.match(/<section class="offer"[\s\S]*?<\/section>/);
 assert.ok(block);
 const disc=block[0].indexOf('Affiliate disclosure:');
 const button=block[0].indexOf('<button');
 assert.ok(disc>=0&&button>disc&&button-disc<550);
});
check(name+' free Focus is existing route',()=>assert.match(txt,/https:\/\/finalvestige\.com\/focus\//));
check(name+' no false personal usage testimony',()=>assert.doesNotMatch(txt,/I (?:personally )?(?:used|tested|bought) Zen12/i));
check(name+' seller efficacy qualified',()=>assert.match(txt,/seller claim/i));
}
check('B has one optional storyboard section',()=>assert.equal((B.match(/id="optional-film"/g)||[]).length,1));
check('B storyboard has accessible inline vector title+description',()=>{assert.match(B,/<svg[^>]*role="img"/);assert.match(B,/<title id="pt">/);assert.match(B,/<desc id="pd">/);});
check('B has visible transcript, no fake playable film claim',()=>{assert.match(B,/Original 42-second narration:/);assert.match(B,/not an encoded or playable video/i);});
check('VTT exact six cues / 42-second coverage',()=>{
 assert.match(vtt,/^WEBVTT/);
 const cues=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)].map(m=>[+m[1]*3600+ +m[2]*60+ +m[3]+ +m[4]/1000,+m[5]*3600+ +m[6]*60+ +m[7]+ +m[8]/1000]);
 assert.equal(cues.length,6);assert.equal(cues[0][0],0);assert.equal(cues.at(-1)[1],42);
 cues.forEach((c,i)=>{assert.equal(c[1]-c[0],7);if(i)assert.equal(c[0],cues[i-1][1]);});
});
check('original investigation scoped primary source and 2k+ words',()=>{
 assert.ok(article.trim().split(/\s+/).length>=2000);
 for(const s of ['https://doi.org/10.1038/35784','https://doi.org/10.1525/collabra.325','https://doi.org/10.1525/collabra.116190','https://doi.org/10.3389/fnhum.2022.834492'])assert.ok(article.includes(s));
});
check('matrix declared claim count',()=>assert.equal(matrix.claim_count,matrix.claims.length));
check('matrix declared source count',()=>assert.equal(matrix.source_count,matrix.sources.length));
check('matrix declared gate count',()=>assert.equal(matrix.commercial_gate_count,matrix.gates.length));
check('matrix 26 claims, 17 sources, 21 gates',()=>{assert.equal(matrix.claims.length,26);assert.equal(matrix.sources.length,17);assert.equal(matrix.gates.length,21);});
check('matrix links actual https sources and valid IDs',()=>{
 const s=new Set(matrix.sources.map(x=>x.id));
 assert.equal(s.size,matrix.sources.length);
 matrix.sources.forEach(x=>assert.match(x.url,/^https:\/\//));
 matrix.claims.forEach(x=>assert.ok(s.has(x.source_id)));
});
check('all permissions fail-closed',()=>{
 matrix.gates.forEach(x=>{assert.equal(x.state,'HOLD');assert.equal(x.proof_url,null);assert.equal(x.verified_on,null);});
 assert.equal(matrix.release_decision,'HARD_HOLD');assert.equal(matrix.net_revenue_per_1000_qualified_human_sessions,null);
});
check('three creator matches actual IDs not fabricated',()=>{
 assert.equal(matrix.media_map.length,3);
 matrix.media_map.forEach(x=>{assert.equal(x.asset_id,null);assert.equal(x.platform_url,null);assert.equal(x.verified_hook,null);});
});
check('dossier separates clicks and settled orders',()=>{for(const s of ['affiliate_click','merchant_confirmed_paid_order','settled_publisher_commission','NOT COMPUTABLE','Founder / Commerce','Praxxis / Grok'])assert.ok(dossier.includes(s));});
check('hub exactly four thematic streams',()=>{
 for(const s of ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'])assert.ok(hub.includes(s));
 assert.match(hub,/No live page/); // Must never present a source-only new article as live
});
check('CMS and email not touched in dossier',()=>assert.match(dossier,/No publication, menu\/settings changes, email sends/));
let passed=0;
for(const x of cases){try{x.fn();passed++;console.log('PASS '+x.name)}catch(err){console.error('FAIL '+x.name+': '+err.message);process.exitCode=1;}}
console.log('Mind R411 static source assertions: '+passed+'/'+cases.length+' passed; browser/WordPress/merchant/CI NOT tested');

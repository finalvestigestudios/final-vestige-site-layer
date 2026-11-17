// R452: reproducible, dependency-free SOURCE STATIC checks. Run: node --test mind/r452/check_r452.mjs
// This is not a replacement for real browser, WordPress, legal, merchant or revenue QA.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read = (n) => readFileSync(new URL(n, import.meta.url), 'utf8');
const A=read('ZEN12_A_EVIDENCE_GUIDE.html'), B=read('ZEN12_B_OPTIONAL_FILM_CONCEPT.html');
const HUB=read('MIND_HUB_WORDPRESS_SOURCE_ONLY.html'), SV=read('ZEN12_42S_POSTER.svg');
const VTT=read('ZEN12_42S_CAPTIONS.vtt'), DOC=read('CONVERSION_AND_CREATOR_ACCEPTANCE.md'), ART=read('THE_TABLE_MOVED_WHO_MOVED_IT.md');
const M=JSON.parse(read('CLAIM_SOURCE_PERMISSION_MATRIX.json'));
const main=(s) => s.match(/<main id="content"[^>]*>([\s\S]*?)<\/main>/i)?.[1];
for(const [name,html] of [['A',A],['B',B],['HUB',HUB]]) {
 test(name+' semantics and no production script',()=> {
  assert.match(html, /<!doctype html>/i);
  assert.match(html, /<html lang="en"/);
  assert.match(html, /name="viewport"/);
  assert.match(html, /name="robots" content="noindex,nofollow"/);
  assert.equal((html.match(/<main\b/g)||[]).length,1);
  assert.match(html,/\.skip:focus/);
  assert.match(html, /:focus-visible/);
  assert.match(html, /prefers-reduced-motion:reduce/);
  for(const re of [/<script\b/i,/<iframe\b/i,/<form\b/i,/<input\b/i,/on(click|load|error)\s*=/i,/<video\b/i,/<audio\b/i,/https:\/\/[^"']*\.(mp4|webm|mp3)([?"'])/i,/<link\b[^>]*stylesheet/i]) assert.doesNotMatch(html,re);
 });
}
test('A/B substantive main buyer copy same, not placebo variant',()=> {
 assert.ok(main(A) && main(B)); assert.equal(main(A),main(B));
 assert.equal((A.match(/<button\b/g)||[]).length,1);
 assert.equal((B.match(/<button\b/g)||[]).length,1);
});
for(const [name,html] of [['A',A],['B',B]]) {
 test(name+' hard-disables commercial path and discloses adjacent',()=>{
  assert.match(html,/<button type="button" disabled aria-describedby="commercial-hold">/);
  assert.match(html,/<p class="offer-note">[\s\S]*?may earn a commission[\s\S]*?<\/p><button type="button" disabled/);
  assert.match(html, /no affiliate purchase link active here/i);
  assert.match(html, /href="https:\/\/finalvestige.com\/focus\/"/);
  assert.doesNotMatch(html,/<a\b[^>]+href="https:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3|hypnosislive|brainwaveshots)\./i);
  assert.doesNotMatch(html,/(utm_content|utm_campaign|[?&](?:ref|aff|affiliate_id)=)/i);
  assert.match(html, /not a hands-on review/i);
  assert.match(html,/exact checkout/);
 });
}
test('B alone supplies an inert optional creative concept',()=>{
 assert.doesNotMatch(A, /42-second film concept/i);
 assert.match(B, /42-second film concept/i);
 assert.match(B,/<img src="ZEN12_42S_POSTER.svg"/);
 assert.match(B,/<details><summary>Read the 42-second transcript/);
 assert.match(B, /Film NOT yet encoded or playable/);
 assert.doesNotMatch(B,/<source\b|autoplay\b(?=\s|>)/i);
});
test('SVG is original inert image with title, no remote executable payload',()=>{
 assert.match(SV,/<svg xmlns="http:\/\/www.w3.org\/2000\/svg"/);
 assert.match(SV,/<title id="title">/);
 for(const re of [/<script\b/i,/<foreignObject\b/i,/<image\b/i,/<use\b/i,/(href|xlink:href)=/i,/<style\b/i,/on(click|load|error)\s*=/i]) assert.doesNotMatch(SV,re);
});
test('VTT six non-overlapping cues reach exactly 42 seconds',()=>{
 assert.match(VTT,/^WEBVTT/);
 const cues=Array.from(VTT.matchAll(/(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})/g));
 assert.equal(cues.length,6);
 const ms=t=>{const [h,m,sec]=t.split(':');return 3600000*+h+60000*+m+1000*+sec};
 assert.equal(ms(cues[0][1]),0);assert.equal(ms(cues.at(-1)[2]),42000);
 for(let i=0;i<cues.length;i++){assert.ok(ms(cues[i][2])>ms(cues[i][1]));if(i)assert.equal(ms(cues[i][1]),ms(cues[i-1][2]));}
});
test('Matrix schema sources evidence and closed release gates',()=>{
 assert.equal(M.run,'R452'); assert.equal(M.commercial_release,'HARD_HOLD');
 assert.equal(M.active_partner_link,false);assert.equal(M.verified_partner_approval,false);
 assert.equal(M.net_revenue_per_1000_qualified_sessions,null);
 assert.equal(M.gates.length,28);assert.ok(M.gates.every(g=>g.status==='HOLD'));
 assert.ok(M.sources.length>=18);assert.ok(M.claims.length>=30);
 const known=new Set(M.sources.map(x=>x.id)); assert.equal(known.size,M.sources.length);
 for(const c of M.claims){assert.ok(c.id&&c.statement&&c.editorial_action);for(const id of c.source_ids)assert.ok(known.has(id),c.id+': '+id)}
 assert.ok(M.claims.some(x=>x.evidence_type==='unsubstantiated-product-efficacy'));
});
test('No phantom social or sale, eligibility and revenue contract explicit',()=>{
 for(const phrase of ['NOT COMPUTABLE','Grok','asset ID','merchant','settled','refund','28','A/B','no active']) assert.match(DOC,new RegExp(phrase,'i'));
 assert.match(DOC, /qualified_human_sessions/);
 assert.match(DOC, /affiliate_click/);
 assert.match(DOC,/verified_paid_order/);
});
test('Original editorial primary sources and free demo retained',()=>{
 assert.ok(ART.split(/\s+/).length>=2000);
 for(const url of ['https://epsilon.ac.uk/view/faraday/letters/Faraday2691','https://pubmed.ncbi.nlm.nih.gov/22377138/','https://link.springer.com/article/10.1007/s11097-018-9585-8','https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/']) assert.ok(ART.includes(url));
 assert.match(ART,/twelve-minute demonstration/i); assert.match(ART,/Not established/i);
});

#!/usr/bin/env node
/**
 * R402 offline source safety gate. Run from repository root:
 * node mind/r402/verify.mjs
 * Requires Node >=18, built-ins only. Static checks do not certify WCAG/CWV,
 * CMS sanitization, live media, consent confirmation or paid transactions.
 */
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const dir = 'mind/r402/';
const read = path => readFileSync(dir + path, 'utf8');
const files = {
  article: read('FREQUENCY_THAT_PROMISED_FOCUS.md'),
  a: read('ZEN12_TEXT_A.html'),
  b: read('ZEN12_OPTIONAL_FILM_B.html'),
  hub: read('MIND_ARCHIVE_HUB_SOURCE.html'),
  vtt: read('ZEN12_STORYBOARD_42S.vtt'),
  matrix: JSON.parse(read('CLAIM_MODALITY_AND_RELEASE_MATRIX.json')),
  dossier: read('CONVERSION_ACCEPTANCE_CREATOR_HANDOFF.md')
};
let passed = 0;
function check(name, fn) {
  try { fn(); console.log('PASS ' + name); passed++; }
  catch(e) { console.error('FAIL ' + name + ': ' + e.message); process.exitCode = 1; }
}
const assertSafeHtml = h => {
  assert.match(h, /<html lang="en">/);
  assert.match(h, /<main id="main">/);
  assert.match(h, /<meta name="robots" content="noindex,nofollow">/);
  assert.doesNotMatch(h, /<script\b|<iframe\b|javascript:|onerror\s*=|onload\s*=/i);
  assert.doesNotMatch(h, /<form\b|<video\b|<audio\b/i);
  assert.doesNotMatch(h, /<a\b[^>]*href=["'][^"']*(?:zen12\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i);
  assert.match(h, /<button\b[^>]*\sdisabled(?:\s|>)/i);
  assert.match(h, /class="disclosure"/);
  assert.match(h, /may earn a commission at no extra cost/i);
  assert.doesNotMatch(h, /(?:\s|<)(?:data-affiliate|affiliate_url|onclick)\s*=/i);
};
const shared = h => {
  const id = '<div id="shared-buyers-guide">';
  assert(h.includes(id));
  return h.slice(h.indexOf(id));
};
const subtitleBlocks = files.vtt.trim().split(/\n\s*\n/).slice(1);
const transcript = (files.b.match(/<p id="film-transcript">([\s\S]*?)<\/p>/) || [,''])[1].trim();
check('UTF8 source and dates', () => { assert(files.article.length>12000); assert(files.dossier.includes('2026-11-15')); });
check('Article explicitly distinguishes stimulus modalities', () => {
 assert.match(files.article, /FAQ says its system uses isochronic tones/);
 assert.match(files.article, /binaural beats/);
 assert.match(files.article, /not a trial of a particular marketed isochronic soundtrack/);
 assert.match(files.article, /Focus Shot.*?12 and 18 Hz/s);
});
check('Primary source URL integrity', () => {
 for (const url of ['https://brainwaveshots.com/faq','https://brainwaveshots.com/focus-shot','https://pubmed.ncbi.nlm.nih.gov/37205669/','https://pubmed.ncbi.nlm.nih.gov/30073406/','https://finalvestige.com/focus/']) assert(files.article.includes(url));
});
check('Variant A safety', () => assertSafeHtml(files.a));
check('Variant B safety', () => assertSafeHtml(files.b));
check('Shared A/B buyer copy exact', () => assert.equal(shared(files.a),shared(files.b)));
check('No extra email or signup', () => { assert(!files.a.includes('<form')); assert(!files.b.includes('<form')); });
check('Existing Focus only active funnel', () => { assert(files.a.includes('https://finalvestige.com/focus/')); assert(files.b.includes('https://finalvestige.com/focus/')); });
check('No tracking scripts or media requests', () => {
 for(const h of [files.a,files.b,files.hub]) assert.doesNotMatch(h, /<script\b|<iframe\b|fetch\s*\(|<video\b/i);
});
check('Optional B poster is original accessible SVG', () => {
 assert.match(files.b, /<svg [^>]*viewBox="0 0 960 540"/);
 assert.match(files.b, /<title id="poster-title">/);
 assert.match(files.b, /<desc id="poster-desc">/);
});
check('B is honestly storyboard only', () => { assert.match(files.b, /storyboard concept only/); assert.match(files.b,/No player, audio, autoplay/); });
check('Transcript matches all WebVTT cue text', () => {
 const cueTexts=subtitleBlocks.map(b=>b.split('\n').slice(2).join(' ').trim());
 assert.equal(subtitleBlocks.length,6);
 assert.equal(cueTexts.join(' '),transcript);
});
check('VTT 6 contiguous seven-second cues', () => {
 const expected=[0,7,14,21,28,35,42];
 for(let i=0;i<6;i++){
   assert(subtitleBlocks[i].includes('00:00:'+String(expected[i]).padStart(2,'0')+'.000 --> 00:00:'+String(expected[i+1]).padStart(2,'0')+'.000'));
 }
});
check('No merchant purchase link in hub',()=>assert.doesNotMatch(files.hub,/<a\b[^>]+href=["'][^"']*(?:zen12|brainwaveshots|hypnosislive)/));
check('Hub sections and old links',()=>{for(const id of ['attention','history','practice','tools'])assert(files.hub.includes('id="'+id+'"'));assert(files.hub.includes('https://finalvestige.com/2026/11/02/change-blindness/'));});
check('Matrix 30-plus sourced claims',()=>{assert(files.matrix.claims.length>=30);for(const c of files.matrix.claims){assert(c.id&&c.verdict&&c.source.startsWith('https://'));}});
check('Matrix rejects illicit modality transfer',()=>{const x=files.matrix.claims.find(c=>c.id==='m01');assert.equal(x.verdict,'REJECT_MODALITY_MISMATCH');});
check('20 commercial gates are closed',()=>{assert.equal(files.matrix.gates.length,20); assert(files.matrix.gates.every(x=>x.status==='HOLD_UNVERIFIED'));});
check('No claimed payable SKU or revenue',()=>{assert.equal(files.matrix.findings.net_revenue_per_1000,'NOT_COMPUTABLE');assert.equal(files.matrix.findings.fv_owned_sellable_mind_sku,'NOT_VERIFIED');});
check('Dossier preserves one Jetpack/list and original Grok queue',()=>{assert(files.dossier.includes('existing Jetpack'));assert(files.dossier.includes('No asset_id, media ID'));});
check('Revenue contract requires settlement, not clicks',()=>{assert(files.dossier.includes('merchant_commission_settled'));assert(files.dossier.includes('NOT COMPUTABLE'));});
check('No unapproved CMS edits in scope',()=>{assert(files.dossier.includes('No merge, deploy, publish or affiliate activation'));});
console.log('Completed '+passed+' source safety checks; exitCode='+(process.exitCode||0));

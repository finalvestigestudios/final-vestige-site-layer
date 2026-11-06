'use strict';
/**
 * Exact WordPress Playground Blueprint source admission, LOCAL QA ONLY.
 * Checks the 72 record rail follows the opening promise before chapter 02.
 * This verifies structural parity, not WordPress runtime, WCAG or Lighthouse.
 */
const fs = require('node:fs');
const assert = require('node:assert/strict');
const ids = [
 'fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
 'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'
];
function parse(text) {
 const bp=JSON.parse(text);
 assert.equal(bp.$schema,'https://playground.wordpress.net/blueprint-schema.json');
 assert.equal(bp.steps[0].step,'installTheme');
 assert.equal(bp.steps[0].themeData.path,'assembler');
 assert.equal(bp.steps[0].themeData.ref,'75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f');
 const php=bp.steps[2].data;
 assert.ok(php.includes('FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1'));
 function grab(t) {
  const start="<<<'FVPG_"+t+"_END'\n", end="\nFVPG_"+t+"_END";
  assert.equal(php.split(start).length,2,'Missing '+t+' start');
  assert.equal(php.split(start)[1].split(end).length,2,'Missing '+t+' end');
  return php.split(start)[1].split(end)[0];
 }
 return {php, html:grab('HTML'),css:grab('CSS'),js:grab('JS')};
}
function count(s,needle) {return s.split(needle).length-1;}
function records(html) {
 return html.split('class="fv-margin-strip__item"').slice(1).map(t=>t.split('>')[1].split('</span>')[0]);
}
function verify(text, previous=null) {
 const p=parse(text), h=p.html;
 assert.equal(records(h).length,72,'72 historical source records');
 assert.equal(new Set(records(h)).size,72,'no duplicate historical source records');
 assert.equal(count(h,'class="fv-margin-strip fv-margin-strip--rotator"'),1,'unique rail');
 assert.equal(count(h,'class="fv-hf__chapter-nav"'),1);
 assert.equal(count(h,'href="https://finalvestige.com/focus/"'),5,'Focus CTA parity');
 assert.equal(count(h,'<img '),2,'Apollo and Franklin images only');
 assert.ok(h.includes('type="checkbox"'),'optional animation control');
 assert.ok(p.css.includes('prefers-reduced-motion: reduce'),'reduced motion preserved');
 assert.ok(p.css.includes('.fv-margin-strip__motion-check'));
 assert.ok(p.js.includes('source: flagship.js'));
 for (const id of ids) assert.ok(h.includes('id="'+id+'"'),'missing '+id);
 const root=h.indexOf('class="fv-hf" data-fv-home-flagship>');
 const content=h.indexOf('class="fv-hf__wp-content"');
 const hero=h.indexOf('class="fv-hf__opening"');
 const strip=h.indexOf('class="fv-margin-strip fv-margin-strip--rotator"');
 const chapter2=h.indexOf('class="fv-hf__chronicle"');
 assert.ok(root>=0 && root<content && content<hero && hero<strip && strip<chapter2,
  'rail must follow opening hero and precede chapter 02');
 if(previous!==null){
  const q=parse(previous);
  assert.equal(p.css,q.css,'no CSS changes');
  assert.equal(p.js,q.js,'no JS changes');
  assert.deepEqual(records(h),records(q.html),'72 public historical facts unchanged');
  assert.equal(count(h,'https://finalvestige.com/focus/'),count(q.html,'https://finalvestige.com/focus/'));
  assert.equal(count(h,'<img '),count(q.html,'<img '));
 }
 return {records:72,chapters:7,images:2,focusActions:5,positions:{root,hero,strip,chapter2}};
}
if(require.main===module){
 const path=process.argv[2]||'experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json';
 const old=process.argv[3]&&fs.readFileSync(process.argv[3],'utf8');
 console.log(JSON.stringify({status:'SOURCE_ADMISSION_PASS',...verify(fs.readFileSync(path,'utf8'),old||null)}));
}
module.exports={verify};

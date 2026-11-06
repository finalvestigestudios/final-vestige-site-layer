'use strict';
// Run: node --test experience2/home-flagship/playground/test_firstscreen_evidence_order.cjs
// Source admission only — actual WordPress/axe/Lighthouse still required.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {verify} = require('./verify_firstscreen_evidence_order.cjs');
const f=path.join(__dirname,'FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json');
const src=fs.readFileSync(f,'utf8');
const change = fn => {const o=JSON.parse(src);o.steps[2].data=fn(o.steps[2].data);return JSON.stringify(o);};
test('actual current blueprint passes source admission', () => {
 const a=verify(src);assert.equal(a.records,72);assert.equal(a.chapters,7);
});
const mutations=[
 ['missing chapter',s=>s.replace('id="fv-hf-mind-title"','id="missing-mind"')],
 ['missing source record',s=>s.replace('class="fv-margin-strip__item"','class="deleted-record"')],
 ['missing Focus CTA',s=>s.replaceAll('href="https://finalvestige.com/focus/"','href="/false/"')],
 ['rail no longer after hero',s=>s.replace('class="fv-hf__opening"','class="not-hero"')],
 ['missing image',s=>s.replace('<img ','<unverified-img ')],
 ['missing motion control',s=>s.replace('type="checkbox"','type="hidden"')],
 ['missing reduced motion',s=>s.replaceAll('prefers-reduced-motion: reduce','unknown-motion')],
 ['duplicate complete source record',s=>{ const rows=[...s.matchAll(/<span class="fv-margin-strip__item"[^>]*>([\s\S]*?)<\/span>/g)]; return s.replace(rows[0][1], rows[1][1]); }],
 ['changed CSS selector',s=>s.replaceAll('.fv-margin-strip__motion-check','.altered-check')]
];
for (const [name,mutator] of mutations) test('reject '+name,()=>{
  assert.throws(()=>verify(change(mutator)));
});

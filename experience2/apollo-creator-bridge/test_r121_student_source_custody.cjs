'use strict';
/* R121: exact-source offline custody invariants. Run: node test_r121_student_source_custody.cjs */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, 'landing-preview.html'), 'utf8');
const ids = ['01','02','03','04','05','06'];
const urlRE = /href="(https:\/\/www\.nasa\.gov\/image-detail\/[^"]+)"/;
function collect(html, regex) {
  const map = new Map();
  for (const match of html.matchAll(regex)) {
    assert(!map.has(match[1]), 'duplicate source id ' + match[1]);
    assert(urlRE.test(match[0]), 'missing official NASA URL in ' + match[1]);
    map.set(match[1], match[0].match(urlRE)[1]);
  }
  return map;
}
function validate(html) {
  const packet = html.match(/<article class="student-print-sheet"[\s\S]*?<\/article>/);
  assert(packet, 'student worksheet absent');
  const index = packet[0].match(/<section class="student-source-index"[\s\S]*?<\/section>/);
  assert(index, 'student-only source index absent');
  const rows = collect(html, /<tr id="photo-source-(\d\d)"[\s\S]*?<\/tr>/g);
  const refs = collect(index[0], /<li data-fv-student-photo="(\d\d)"[\s\S]*?<\/li>/g);
  assert.deepEqual([...rows.keys()].sort(), ids, 'main source register IDs');
  assert.deepEqual([...refs.keys()].sort(), ids, 'student handout IDs');
  for (const id of ids) {
    assert.equal(refs.get(id),rows.get(id), 'source link drift for ' + id);
  }
  assert.equal((index[0].match(/https:\/\/www\.nasa\.gov\/image-detail\//g)||[]).length,6,'exactly six photo links');
  assert(!/<(?:img|picture|iframe|video)\b/i.test(packet[0]),'no photo/media assets in student packet');
  assert(/not a fire-event timeline/i.test(index[0]),'source chronology must not become fire chronology');
  assert(/crew portrait's day in January 1967 and proposed S67-19766 association remain unconfirmed/.test(index[0]), 'crew portrait uncertainty required');
  assert(/<li data-fv-student-photo="04"><strong>Jan 24, 2017 · retrospective/i.test(index[0]),'2017 record 04 must be retrospective');
  assert(/<li data-fv-student-photo="06"><strong>Jan 24, 2017 · retrospective/i.test(index[0]),'2017 record 06 must be retrospective');
  assert((index[0].match(/NASA\/Kim Shiflett/g)||[]).length===2,'two retrospective credits');
  assert(packet[0].includes('The complete source register is available on the investigation page'), 'no fictitious printed preceding register');
  assert(!packet[0].includes('The dated source register and unresolved reuse limitations appear earlier'), 'obsolete false copy');
  assert(packet[0].includes('individually uncleared for reproduction (0/6)'), 'rights restriction missing');
  assert(packet[0].includes('not NASA-endorsed'),'endorsement limitation missing');
  assert(packet[0].includes('technical source; photographs are visual context'),'source roles missing');
  assert(/body\.fv-worksheet-only\s+#main>:not\(#classroom-preview\)/.test(html),'student-only print must hide the full record');
  assert(/body\.fv-worksheet-only\s+\.student-source-index\{/.test(html),'print source-index layout missing');
  assert(/\.student-print-sheet\{display:none\}/.test(html),'print-only material leaked to screen');
  assert(/@media print\{[\s\S]*?\.student-print-sheet\{display:block!important/.test(html),'normal print packet must retain student worksheet');
  assert(/data-fv-primary-cta/.test(html),'preserve free classroom action');
  assert(!/<form\b/i.test(html),'no new form or lead capture');
  assert(!/<img\b/i.test(html),'no unreviewed photograph embedding');
  return {main_records:rows.size,standalone_records:refs.size};
}
let checks=0;
validate(source); checks++;
const mutations = [
  s=>s.replace('data-fv-student-photo="05"','data-fv-student-photo="04"'),
  s=>s.replace('image-detail/amf-s67-21294/">NASA S67-21294 record</a>','image-detail/amf-s67-15717/">NASA S67-21294 record</a>'),
  s=>s.replace('data-fv-student-photo="06"','data-fv-student-photo="99"'),
  s=>s.replace('remain unconfirmed. No photograph is reproduced.','are verified. No photograph is reproduced.'),
  s=>s.replace('Jan 24, 2017 · retrospective hatch exhibit','Jan 24, 1967 · hatch exhibit'),
  s=>s.replace('individually uncleared for reproduction (0/6)','cleared for reproduction'),
  s=>s.replace('The complete source register is available on the investigation page','The six sources are provided above'),
  s=>s.replace(' body.fv-worksheet-only .student-source-index{',' body.fv-worksheet-only .missing-source-index{'),
  s=>s.replace('NASA/Kim Shiflett; not an image from 1967','NASA/JSC; not an image from 1967'),
  s=>s.replace('No photograph is reproduced.</p>','No photograph is reproduced.</p><img src="https://example.com/photo.jpg">'),
];
for (const [i,mutate] of mutations.entries()){
  const changed=mutate(source);
  assert.notEqual(changed,source,'mutation '+i+' must modify source');
  assert.throws(()=>validate(changed),'mutation '+i+' must be rejected');
  checks++;
}
console.log('Apollo R121 exact-source custody: '+checks+'/'+checks+' PASS (1 canonical + '+mutations.length+' adversarial).');

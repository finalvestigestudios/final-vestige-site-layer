'use strict';
/* node R237_SOURCE_TESTS.cjs — no network, no sends, no CMS writes. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { check } = require('./R237_GUARD.cjs');
const base = __dirname;
const read = n => fs.readFileSync(path.join(base,n),'utf8');
const a = read('ISSUE04_APOLLO_ALTERNATIVE_UNSENT.md');
const h = read('ISSUE04_REVIEW_ONLY.html');
const t = read('ISSUE04_REVIEW_ONLY.txt');
const d = read('SOURCE_TRUTH_AND_CONVERSION_REVIEW.md');
const manifest = fs.readFileSync(path.join(base,'..','campaign-2026-mind','manifest.json'),'utf8');
const files = [a,h,t,d,manifest];
assert.deepEqual(check(...files),[], 'clean baseline must pass');
const cases = [
 ['subject MD',0,"Apollo 1: the cause wasn't one neat spark","A single spark proved everything",'subject_mismatch'],
 ['heading HTML',1,'<h1','<h0','subject_mismatch'],
 ['preheader text',2,'NASA identified the dangers.','NASA proved the arc.','preheader_mismatch'],
 ['preheader HTML',1,'NASA identified the dangers.','NASA proved the arc.','preheader_mismatch'],
 ['draft hold',0,'OPTIONAL PRIMARY-SOURCE CORRECTION','LAUNCH READY','review_hold_missing'],
 ['plain hold',2,'HOLD_UNSENT','LAUNCH_READY','review_hold_missing'],
 ['NASA report MD',0,'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','','missing_md_source'],
 ['NASA safety HTML',1,'https://sma.nasa.gov/sma-disciplines/accllp/apollo-1','','missing_html_source'],
 ['NASA safety plain',2,'https://sma.nasa.gov/sma-disciplines/accllp/apollo-1','','missing_text_source'],
 ['timing MD',0,'approximately fifteen seconds','precisely fourteen seconds','timing_source_caution_missing'],
 ['timing HTML',1,'approximately fifteen seconds','precisely fourteen seconds','timing_source_caution_missing'],
 ['unknown ignition',2,'no single ignition source had been conclusively identified','the first spark was proven','causality_limit_missing'],
 ['postal MD',0,'[[VALID_POSTAL_ADDRESS_REQUIRED]]','','missing_md_legal_hold'],
 ['unsubscribe HTML',1,'[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]','','missing_html_legal_hold'],
 ['postal plain',2,'[[VALID_POSTAL_ADDRESS_REQUIRED]]','','missing_txt_legal_hold'],
 ['CTA plain',2,'READ THE INVESTIGATION (one primary CTA)','READ OUR ADS','wrong_primary_cta'],
 ['CTA HTML',1,'Read the Apollo 1 investigation','Buy the product','wrong_html_cta'],
 ['script HTML',1,'</body>','<script>alert(1)</script></body>','unsafe_html'],
 ['pixel HTML',1,'</body>',"<img src='pixel.gif'></body>",'unsafe_html'],
 ['unsafe link',1,'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/','javascript:alert(1)','unsafe_link'],
 ['affiliate tracker',1,'</body>',"<a href='https://affiliates.inspire3.com/track'>x</a></body>",'tracking_link_not_permitted'],
 ['vendor miracle claim',0,'That is the uncomfortable','Guaranteed result. That is the uncomfortable','unsupported_promotion'],
 ['merchant hold',3,'HOLD_MERCHANT','RELEASED','missing_business_restrictions'],
 ['delivery hold',3,'HOLD_DELIVERY','RELEASED','missing_business_restrictions'],
 ['Gmail negative proof',3,'not a denial or proof of absence','proven denied','gmail_negative_proof_missing'],
 ['editorial mix',4,'"editorial": 4','"editorial": 5','original_campaign_allocation_change']
];
for (const [label,i,needle,replacement,want] of cases){
 assert.ok(files[i].includes(needle),label+' mutation fixture absent');
 const changed = files.slice();
 changed[i] = i===3 ? changed[i].replaceAll(needle,replacement) : changed[i].replace(needle,replacement);
 const got = check(...changed);
 assert.ok(got.includes(want),label+' failed to block: '+JSON.stringify(got));
}
console.log('R237 PASS: 1 baseline + '+cases.length+' adversarial mutations = '+(1+cases.length)+' checks. No sends or network.');

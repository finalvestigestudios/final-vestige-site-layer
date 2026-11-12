// Static native Node QA for NON-SENDING R314 optional review manuscripts.
// Execute: node --test dispatch/r314/review.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const root = new URL('./', import.meta.url);
const manifest = JSON.parse(fs.readFileSync(new URL('manifest.json',root),'utf8'));
const file = (n,ext) => fs.readFileSync(new URL('issue'+n+'.'+ext,root),'utf8');
test('fail closed and preserve 4 editorial + 2 reserved commercial',()=>{
 assert.equal(manifest.status,'ALL_REVIEW_ONLY_HOLD_UNSENT');
 assert.equal(manifest.founder_adopted,false);
 assert.equal(manifest.draft_ratio,'4 editorial / 2 commercial — unchanged');
 assert.deepEqual(manifest.issues.map(x=>x.issue),[1,4,6]);
 assert.ok(manifest.issues.every(x=>!x.adopted&&!x.email_allowed));
 assert.ok(manifest.commercial.every(x=>x.status==='HOLD_MERCHANT'&&!x.email_permission_verified&&!x.issued_link_verified&&!x.approved_live_guide));
});
for(const n of ['01','04','06']) test('issue '+n+' safe exact claim/CTA/footer',()=>{
 const e=manifest.issues.find(x=>String(x.issue).padStart(2,'0')===n), md=file(n,'md'), html=file(n,'html');
 assert.ok(md.includes(e.subject)&&md.includes(e.preheader)&&md.includes(e.cta));
 assert.ok(html.includes(e.subject)&&html.includes(e.cta));
 assert.ok(md.includes('NOT ADOPTED')&&html.includes('NOT APPROVED'));
 for(const s of ['[[VALID_POSTAL_ADDRESS_REQUIRED]]','[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]']) assert.ok(md.includes(s)&&html.includes(s));
 assert.ok(html.includes('role="presentation"')&&html.includes('<html lang="en">'));
 assert.ok(!html.includes('<script')&&!html.includes('<form')&&!html.includes('utm_source='));
 assert.ok(!html.includes('javascript:')&&!html.includes('affiliates.inspire3.com')&&!html.includes('zen12.com/getstarted')&&!html.includes('hypnosislive.com/'));
});
test('01 actually serves change-blindness and not duplicate Puységur CTA',()=>{assert.ok(file('01','md').includes('/change-blindness/'));assert.ok(!file('01','md').includes('/puysegurs-animal-magnetism-files/'));});
test('04 cites final board, avoids fragile 14-second hook',()=>{assert.ok(file('04','md').includes('no single ignition source'));assert.ok(file('04','md').includes('nasa.gov'));assert.ok(!/Fourteen seconds|14-second/i.test(file('04','md')));});
test('06 existing subscriber gets direct PDF not duplicate subscribe CTA',()=>{assert.ok(file('06','md').includes('Complete_Edition.pdf'));assert.ok(!file('06','md').includes('](https://finalvestige.com/focus/)'));});
test('unverified recipient delivery and revenue are honestly null',()=>{assert.equal(manifest.actual_email_eligible_recipients,'UNKNOWN');assert.equal(manifest.actual_jetpack_preview,'NOT_TESTED');assert.equal(manifest.net_revenue_per_1000,'NOT_COMPUTABLE');});

'use strict';
// Run locally with: node --test dispatch/r190/test_r190.cjs
// Tests are STATIC SOURCE QA ONLY, not native Jetpack preview, legal signoff or product-approval proof.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = __dirname;
const file = (name) => fs.readFileSync(path.join(root, name),'utf8');
const ledger = JSON.parse(file('CONVERSION_RELEASE_LEDGER.json'));
test('preserves founder 4 editorial : 2 commercial pilot',()=>{
 assert.equal(ledger.master_campaign.editorial,4);assert.equal(ledger.master_campaign.commercial,2);
 assert.equal(ledger.issues.filter(x=>x.kind==='editorial').length,4);
 assert.equal(ledger.issues.filter(x=>x.kind==='commercial').length,2);
});
test('all six original issues held, with commercial gates isolated',()=>{
 assert.ok(ledger.issues.every(i=>i.status.startsWith('HOLD_')));
 assert.deepEqual(ledger.issues.filter(x=>x.kind==='commercial').map(x=>x.n),[3,5]);
 assert.ok(ledger.issues.filter(x=>x.kind==='commercial').every(x=>x.url===null));
});
test('provider-signed consent and delivery unknown, no additive counts',()=>{
 assert.equal(ledger.current_wp_read_only.counts_are_not_additive,true);
 assert.equal(ledger.current_wp_read_only.actual_email_subscribed_eligible,null);
 assert.equal(ledger.current_wp_read_only.welcome_received,null);
 assert.equal(ledger.current_wp_read_only.new_post_auto_mail,false);
});
test('authentic legal footers and merchant rights unavailable',()=>{
 assert.ok(Object.values(ledger.compliance_proof).every(v=>v===false));
 for(const sku of Object.values(ledger.merchant)){assert.equal(sku.named_fv_acceptance_verified,false);assert.equal(sku.email_channel_permission_verified,false);assert.equal(sku.approved_earning_url_verified,false);assert.equal(sku.live_approved_vetted_guide_verified,false);}
});
test('no fabricated revenue or paid sales',()=>{
 assert.equal(ledger.conversion.metric_value,null);assert.equal(ledger.conversion.verified_paid_orders,null);
 assert.equal(ledger.conversion.verified_qualified_human_sessions,null);assert.equal(ledger.conversion.manual_or_fake_values_forbidden,true);
});
test('source-led optional letter truthful and with one destination',()=>{
 const md=file('02_OPTIONAL_CLEVER_HANS_UNSENT.md'),html=file('02_EMAIL_SAFE_OFFLINE_REVIEW.html'),txt=file('02_PLAINTEXT_REVIEW.txt');
 for(const body of [md,txt,html]){assert.match(body,/The horse that knew when to stop/);assert.match(body,/finalvestige.com\\/2026\\/11\\/02\\/mesmerism/);assert.match(body,/DO NOT SEND|UNSENT/);}
 assert.match(md,/98%/);assert.match(md,/8%/);assert.match(md,/Pfungst/);assert.match(md,/1911/);
 assert.match(html,/role="presentation"/);assert.match(html,/lang="en"/);assert.match(html,/max-width:600px/);
});
test('unsendable footers are not substituted by platform addresses',()=>{
 for(const text of [file('02_OPTIONAL_CLEVER_HANS_UNSENT.md'),file('02_PLAINTEXT_REVIEW.txt'),file('02_EMAIL_SAFE_OFFLINE_REVIEW.html')]){
 assert.match(text,/\\[\\[VALID_POSTAL_ADDRESS_REQUIRED\\]\\]/);assert.match(text,/\\[\\[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED\\]\\]/);
 assert.doesNotMatch(text,/(https?:\\/\\/)?(www\\.)?awin1\\.com\\/cread/);
 }
});
test('no production writes represented',()=>{
 assert.ok(Object.values(ledger.production_changes).every(v=>v===false));
 assert.match(file('SUBSCRIBER_TO_CUSTOMER_IMPLEMENTATION.md'),/NOT COMPUTABLE/);
 assert.match(file('SUBSCRIBER_TO_CUSTOMER_IMPLEMENTATION.md'),/Grok/);
});

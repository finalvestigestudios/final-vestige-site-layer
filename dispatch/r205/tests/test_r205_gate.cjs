// Native Node test file for offline source review only. Run with node --test.
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const contract = JSON.parse(fs.readFileSync(path.join(root, 'R205_RELEASE_CONTRACT.json'), 'utf8'));
const plain = fs.readFileSync(path.join(root, 'ISSUE06_OPTIONAL_EDITORIAL.txt'), 'utf8');
const html = fs.readFileSync(path.join(root, 'ISSUE06_OPTIONAL_EDITORIAL.html'), 'utf8');
function qualifiesForSend(c) {
 const p=c.proofs,j=c.jetpack;
 const common=p.explicit_final_founder_approval && p.recipients_confirmed_provider_eligible &&
 j.received_commercial_email_verified && j.valid_publisher_physical_address_verified &&
 j.functional_unsubscribe_verified && j.received_welcome_verified;
 return !!common;
}
function qualifiesCommercial(c){
 return qualifiesForSend(c)&&c.proofs.partner_acceptance_named&&c.proofs.channel_email_affiliate_permission&&
 c.proofs.issued_earning_url&&c.proofs.approved_live_zen12_guide&&c.proofs.merchant_refund_checkout_verified;
}
test('master is fixed six with exactly two commercial',()=>{assert.equal(contract.master_head,'d57ccdba3aee8f065e143e101c2945f4f3d01647');assert.equal(contract.issues.length,6);assert.equal(contract.issues.filter(x=>x.category==='commercial').length,2);});
test('current evidence remains all HOLD',()=>{assert.ok(contract.issues.every(x=>x.hold.startsWith('HOLD')));assert.equal(contract.mode,'DRAFT_NOT_APPROVED');});
test('nonadditive subscriber counts cannot be inferred as eligibility',()=>{assert.equal(contract.counts.eligible_subscriber_count,null);assert.equal(contract.counts.nonadditive,true);assert.equal(contract.counts.stats_email_only,0);});
test('Jetpack new post auto email disabled',()=>{assert.equal(contract.jetpack.auto_new_post_send,false);});
test('no true partner/email privilege claims',()=>{assert.equal(contract.proofs.channel_email_affiliate_permission,false);assert.equal(contract.proofs.partner_acceptance_named,false);assert.equal(contract.proofs.issued_earning_url,false);});
test('publisher postal and opt-out must be actual',()=>{assert.equal(contract.jetpack.valid_publisher_physical_address_verified,false);assert.equal(contract.jetpack.functional_unsubscribe_verified,false);});
test('no false local eligibility',()=>{assert.equal(qualifiesForSend(contract),false);assert.equal(qualifiesCommercial(contract),false);});
test('fail closed with only merchant permission supplied',()=>{const c=structuredClone(contract);c.proofs.partner_acceptance_named=true;c.proofs.channel_email_affiliate_permission=true;c.proofs.issued_earning_url=true;assert.equal(qualifiesCommercial(c),false);});
test('fail closed with only founder approval',()=>{const c=structuredClone(contract);c.proofs.explicit_final_founder_approval=true;assert.equal(qualifiesForSend(c),false);});
test('optional text explicit non-send, honest subject+preheader',()=>{assert.match(plain,/UNSENT.*NOT APPROVED/);assert.match(plain,/Subject: The stranger who changed in front of them/);assert.match(plain,/Preheader:/);});
test('no secondary signup CTA',()=>{assert.ok(!plain.includes('https://finalvestige.com/focus/'));assert.match(plain,/subscribe a second time/);});
test('one published primary CTA, primary paper linked',()=>{assert.equal((plain.match(/https:\/\/finalvestige.com\/2026\/11\/02\/change-blindness\//g)||[]).length,1);assert.ok(plain.includes('https://doi.org/10.3758/BF03208840'));});
test('HTML has accessible structure and real primary CTA',()=>{assert.match(html,/<html lang="en">/);assert.match(html,/<h1 /);assert.match(html,/<table role="presentation"/);assert.match(html,/Read the source-led investigation<\/a>/);assert.match(html,/<div style="display:none/);});
test('HTML no JS or tracking pixel or remote image',()=>{assert.ok(!/<script|<img|utm_source=/i.test(html));});
test('HTML and plain keep non-send placeholders',()=>{for(const s of [plain,html]){assert.match(s,/\[\[FV_VALID_PHYSICAL_ADDRESS_REQUIRED\]\]/);assert.match(s,/\[\[JETPACK_RENDERED_UNSUBSCRIBE_URL_AND_OPERATION_REQUIRED\]\]/);}});
test('HTML has adjacent noncommercial disclosure and source link',()=>{assert.match(html,/No product recommendation appears in this issue/);assert.match(html,/https:\/\/doi.org\/10.3758\/BF03208840/);});
test('exact offer pages represented rather than catalog only',()=>{assert.equal(contract.merchant_sources.zen12,'https://zen12.com/hnp');assert.equal(contract.merchant_sources.total_focus,'https://hypnosislive.com/mental-skills/total-focus');assert.equal(contract.merchant_sources.total_focus_faq,'https://hypnosislive.com/faq');});
test('revenue cannot be computed when denominator/purchases unknown',()=>{assert.equal(contract.proofs.merchant_paid_conversion_reconciled,false);assert.equal(contract.proofs.qualified_human_session_denominator,false);assert.equal(contract.conversion_kpi,'NOT_COMPUTABLE');});

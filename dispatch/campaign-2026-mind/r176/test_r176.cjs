'use strict';
/* R176 offline source-contract checks. Never accesses WordPress, an email provider, or a subscriber list. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const read=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const md=read('ISSUE_03_CANDIDATE.md');
const txt=read('ISSUE_03_PLAINTEXT.txt');
const html=read('ISSUE_03_PREVIEW.html');
const ledger=JSON.parse(read('RELEASE_EVIDENCE.json'));
const root=path.resolve(__dirname,'..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
const issues=fs.readdirSync(path.join(root,'issues')).filter(n=>n.endsWith('.md'));
const tests=[
['canonical six original issues still present',()=>assert.equal(issues.length,6)],
['canonical campaign remains four editorial and two commercial',()=>{assert.equal(manifest.issues.filter(x=>x.kind==='editorial').length,4);assert.equal(manifest.issues.filter(x=>x.kind==='commercial-review-pending').length,2)}],
['original issue 03 remains canonical',()=>assert.match(fs.readFileSync(path.join(root,'issues','03-the-twelve-minute-question.md'),'utf8'),/The twelve-minute meditation question/)],
['optional proposed subject matches plain text',()=>assert.match(txt,/SUBJECT: Twelve minutes, two different claims/)],
['proposed preheader is not asserted as actual Jetpack preview',()=>assert.match(html,/not verified Jetpack inbox text/)],
['candidate contains original reader value exercise',()=>assert.match(md,/three ordinary days/)],
['NCCIH research boundaries remain explicit',()=>assert.match(md,/does not independently verify Zen12/)],
['merchant efficacy remains marked seller claim',()=>assert.match(html,/seller's statement, not independently verified/)],
['vendor feature descriptions have identified official source',()=>assert.equal(ledger.commercial_product.official_page,'https://zen12.com/')],
['no current price appears as an email claim',()=>{assert.ok(!md.includes('$87.99'));assert.ok(!html.includes('$87.99'))}],
['no active affiliate link in either email candidate format',()=>{for(const s of [md,html,txt])assert.doesNotMatch(s,/https?:\\/\\/(?:www\\.)?(?:zen12|affiliates\\.inspire3|hypnosislive)\\.com\\/[^\\s<>]*\\?(?:[^\\s<>]*)?/i)}],
['commercial CTA is visibly noninteractive in rendered reviewer',()=>{assert.match(html,/INACTIVE GUIDE CTA/);assert.match(html,/aria-disabled="true"/);assert.doesNotMatch(html,/<a[^>]+href="[^"]*APPROVED_ZEN12/)}],
['only one planned primary offer CTA',()=>assert.equal((html.match(/INACTIVE GUIDE CTA/g)||[]).length,1)],
['near-offer disclosure visible in HTML',()=>{const a=html.indexOf('INACTIVE GUIDE CTA'),b=html.indexOf('Commercial disclosure:');assert.ok(b>a&&b-a<700)}],
['plain text commercial disclosure present immediately after CTA',()=>{const a=txt.indexOf('PRIMARY CTA'),b=txt.indexOf('COMMERCIAL DISCLOSURE');assert.ok(b>a&&b-a<250)}],
['both variants and ledger remain unsent',()=>{assert.match(txt,/UNSENT INTERNAL REVIEW/);assert.equal(ledger.status,'HOLD_UNSENT')}],
['physical mailing address verification is mandatory',()=>{assert.match(html,/\\[\\[VALID_POSTAL_ADDRESS_REQUIRED\\]\\]/);assert.equal(ledger.legal.physical_postal_address,'NOT_VERIFIED')}],
['unsubscribe rendered and functional verification is mandatory',()=>{assert.match(html,/\\[\\[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED\\]\\]/);assert.equal(ledger.legal.real_footer_opt_out,'NOT_VERIFIED')}],
['no script, form, or tracking pixels in HTML',()=>{assert.doesNotMatch(html,/<(?:script|form|iframe|input)\\b/i);assert.doesNotMatch(html,/analytics\\.js|gtag\\(|pixel\\./i)}],
['HTML uses accessible language and email table layout',()=>{assert.match(html,/<html lang="en">/);assert.match(html,/role="presentation"/);assert.match(html,/<h1/)}],
['subscriber figures must not be summed',()=>{const s=ledger.provider_provenance;assert.equal(s.subscribers_total,3);assert.equal(s.subscribers_confirmed,3);assert.equal(s.unconfirmed,2);assert.equal(s.confirmed_subscriber_receipt_count,'UNKNOWN')}],
['Focus visual success is not a confirmed subscription',()=>{assert.equal(ledger.landing_page_provenance.focus_source_script_shows_gift_for_unrecognized_subscribe_query,true);assert.equal(ledger.landing_page_provenance.focus_confirmation_provider_status,'NOT_VERIFIED')}],
['Dispatch render mismatch requires guest verification',()=>{assert.equal(ledger.landing_page_provenance.dispatch_stored_jetpack_subscription_block,true);assert.equal(ledger.landing_page_provenance.dispatch_api_view_email_input,false);assert.equal(ledger.landing_page_provenance.dispatch_guest_page_form,'NOT_TESTED')}],
['Jetpack real received email not falsely verified',()=>assert.equal(ledger.legal.native_jetpack_preview,'NOT_OBTAINED')],
['publisher acceptance and email promotional rights not asserted',()=>{const n=ledger.commercial_product.not_verified.join(' ');assert.match(n,/affiliate account acceptance/);assert.match(n,/email-channel promotion permission/)}],
['no live commercial guide or affiliate link claimed',()=>{assert.equal(ledger.legal.affiliate_links_activated,false);assert.ok(ledger.commercial_product.not_verified.includes('live FV independent presell guide'))}],
['source links include official NIH FTC Jetpack and seller',()=>{const urls=ledger.research.map(x=>x.source);for(const host of ['nccih.nih.gov','ftc.gov','jetpack.com','zen12.com'])assert.ok(urls.some(x=>x.includes(host)))}],
['campaign activity remains entirely false',()=>{assert.ok(Object.values(ledger.release_attestations).every(x=>x===false));assert.equal(ledger.legal.posts_published,false);assert.equal(ledger.legal.email_test_authorized,false)}],
['no inferred paid sales from website traffic or email opens',()=>{assert.equal(ledger.attribution.paid_sales,'NOT_VERIFIED');assert.equal(ledger.attribution.net_revenue_per_1000,'NOT_COMPUTABLE')}],
['email campaign attribution is proposed only, not injected',()=>{assert.equal(ledger.attribution.email_utm.utm_source,'dispatch');assert.equal(ledger.attribution.utm_links_in_active_email,false)}],
['no private subscriber email addresses in proof packet',()=>{assert.equal(ledger.privacy.subscriber_email_addresses_in_package,false);assert.doesNotMatch(JSON.stringify(ledger),/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}/)}],
['fail-closed commercial classification even if content is educational',()=>assert.equal(ledger.legal.commercial_primary_purpose_review_required,true)]
];
for(const [name,fn] of tests)test(name,fn);

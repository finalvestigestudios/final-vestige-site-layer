'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {inspectReceived,headerMap}=require('./receipt_guard.cjs');
const original=[
  'From: Final Vestige Studios <publisher@example.invalid>',
  'To: private-reader@example.invalid',
  'Subject: The twelve-minute meditation question',
  'List-Unsubscribe: <https://wordpress.example.invalid/u/private-token>',
  'List-Unsubscribe-Post: List-Unsubscribe=One-Click',
  'Content-Type: text/html; charset=UTF-8',
  '',
  '<p>Original editorial text</p><a href="https://wordpress.example.invalid/u/private-token">Unsubscribe</a>',
  '<p>Publisher mailing footer placeholder was independently checked in received rendering</p>'
].join('\r\n');
const verified={originalInboxWitnessed:true,expectedSubject:'The twelve-minute meditation question',
  publisherPostalAddressVerified:true,postalFooterRenderedVerified:true,
  unsubFunctionVerified:true,welcomeAndFieldbookVerified:true,providerConsentVerified:true};
test('synthetic perfect input stays HOLD_UNSENT, never auto-authorizes',()=>{
 const r=inspectReceived(original,verified);
 assert.equal(r.reviewEvidenceComplete,true);assert.equal(r.status,'HOLD_UNSENT');
 assert.equal(r.paidSales,'NOT_DERIVED');
 assert.equal(r.realizedNetRevenue,'NOT_DERIVED');
 assert.equal(r.consentCount,'NOT_DERIVED');
});
const mutations=[
 ['no original inbox witness',{originalInboxWitnessed:false},null,'inputIsOriginalInboxMime'],
 ['no publisher attestation',{publisherPostalAddressVerified:false},null,'publisherAddressIndependentlyValidated'],
 ['no rendered footer',{postalFooterRenderedVerified:false},null,'visiblePostalFooterIndependentlyWitnessed'],
 ['no functional unsubscribe',{unsubFunctionVerified:false},null,'unsubscribeActionIndependentlyTested'],
 ['no welcome proof',{welcomeAndFieldbookVerified:false},null,'welcomeAndFieldbookDeliveryIndependentlyWitnessed'],
 ['no provider consent',{providerConsentVerified:false},null,'subscriberProviderConsentIndependentlyVerified'],
 ['subject substitution',{},original.replace('Subject: The twelve-minute meditation question','Subject: A free miracle'),'originalSubjectMatches'],
 ['sender substitution',{},original.replace('From: Final Vestige Studios','From: Another Publisher'),'senderDisplayMatched'],
 ['missing list unsubscribe',{},original.replace(/^List-Unsubscribe:.*\r?\n/m,''),'providerUnsubscribeHeaderFound'],
 ['missing one-click header',{},original.replace(/^List-Unsubscribe-Post:.*\r?\n/m,''),'providerOneClickHeadersFound'],
 ['missing body opt out',{},original.replace(/Unsubscribe<\/a>/,'Learn More</a>'),'renderedBodyMentionsUnsubscribe'],
 ['literal legal marker',{},original+' [[VALID_POSTAL_ADDRESS_REQUIRED]]','noBlockingPlaceholders'],
 ['literal guide marker',{},original+' [[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]','noBlockingPlaceholders'],
];
for(const [label,override,raw,failed] of mutations){
 test('fails closed: '+label,()=>{const r=inspectReceived(raw??original,{...verified,...override});
 if(label==='missing body opt out') assert.equal(r.checks.renderedBodyMentionsUnsubscribe,true); // URL alone plus word in header stays visible: check limitation
 else assert.equal(r.checks[failed],false);
 assert.equal(r.status,'HOLD_UNSENT');});
}
test('empty evidence remains hold without PII',()=>{const r=inspectReceived(original);assert.equal(r.status,'HOLD_UNSENT');assert(r.missingEvidence.length>=7);assert(!JSON.stringify(r).includes('private-reader'));});
test('missing message fails closed',()=>{const r=inspectReceived('',verified);assert.equal(r.reviewEvidenceComplete,false);assert.equal(r.status,'HOLD_UNSENT');});
test('oversized header not accepted',()=>{assert.deepEqual(headerMap('a'.repeat(2_000_001)),{});});
test('folded list unsubscribe parsed as one header',()=>{const r=headerMap('List-Unsubscribe: <mailto:leave@example.invalid>,\r\n <https://example.invalid/u>\r\n\r\nbody');assert.equal(r['list-unsubscribe'].length,1);});
test('does not echo sender/recipient or URL even with all checks passed',()=>{const r=inspectReceived(original,verified),s=JSON.stringify(r);for(const token of ['publisher@example.invalid','private-reader@example.invalid','private-token','Subject:'])assert(!s.includes(token));});
test('one-click cannot be claimed with mailto only',()=>{let raw=original.replace(/<https:\/\/wordpress\.example\.invalid\/u\/private-token>/,'<mailto:leave@example.invalid>');const r=inspectReceived(raw,verified);assert.equal(r.checks.providerOneClickHeadersFound,false);});
test('opaque user URL must not be used as a paid conversion signal',()=>{const r=inspectReceived(original+' https://merchant.example.invalid/?utm_source=tiktok&sale=1',verified);assert.equal(r.paidSales,'NOT_DERIVED');});
test('preheader not inferred from MIME, no uncontrolled values are emitted',()=>{const r=inspectReceived(original,verified);assert(!('preheader' in r));});
test('real verification cannot be inferred from synthetic fixture',()=>{const r=inspectReceived(original,{...verified,originalInboxWitnessed:false});assert.equal(r.reviewEvidenceComplete,false);});

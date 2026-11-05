'use strict';
/** Native Node regression suite for R136's OFFLINE conversion integrity gate. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {assess,cleanCampaign,cleanOffer,REQUIRED_SOURCES}=require('./r136_conversion_evidence_gate.cjs');
const src='<a data-fv-primary-cta href="#classroom-preview">Free source-analysis exercise</a>'+
 '<section id="classroom-preview">Free source-analysis exercise</section>'+
 REQUIRED_SOURCES.map(u=>'<a href="'+u+'">'+u+'</a>').join('');
const audit={routeAudit:{status:'PASS',primary_cta_count:1},
 mediaAudit:{status:'PASS_SOURCE_CUSTODY_ONLY',record_count:6,commercially_cleared_count:0},
 researchAudit:{status:'PASS'}};
const baseline=()=>assess({landingHtml:src,...audit});
// SYNTHETIC route, not a verified live WordPress permalink or Grok publication.
const reviewedLandingUrl='https://finalvestige.com/investigations/apollo-1/';
const candidateCampaign={source:'youtube',owner:'Grok',asset_id:'apollo_fall_2026_v001',
 public_url:'https://www.youtube.com/watch?v=abcdefghijk',youtube_video_id:'abcdefghijk',
 destination_url:reviewedLandingUrl+'?utm_source=youtube&utm_medium=organic_social'+
  '&utm_campaign=history_pilot_2026_11&utm_content=apollo_fall_2026_v001',
 destination_reviewed:true,destination_fragment:'#classroom-preview',publication_verified:true};
const candidateOffer={sku:'apollo_educator_pack',audience:'educators_grades_6_9',
 topic:'apollo1_source_analysis',rights_review:'SIGNED_OFF_BY_REVIEWER',
 original_materials_sha256:'a'.repeat(64),fulfillment_receipt:'MERCHANT_TEST_DELIVERY_VERIFIED',
 refund_policy_reviewed:true,founder_approval:true,nasa_media_embedded:false,
 merchant_url:'https://payhip.com/b/verified-reference'};
test('all green source audits still cannot approve a sale or release',()=>{
 const r=baseline();
 assert.equal(r.editorial_custody,'SOURCE_GATE_PASS_ONLY');
 assert.equal(r.release,'STAGING_HOLD');
 assert.equal(r.live,false);
 assert.equal(r.paid_cta_insertion_authorized,false);
 assert.equal(r.measurement.net_revenue_per_1000_qualified_sessions,'NOT_COMPUTABLE');
 assert.ok(r.blockers.includes('NO_VALID_PAID_EDUCATOR_OFFER_DOSSIER'));
});
test('missing one photograph prevents source gate',()=>{
 const r=assess({landingHtml:src.replace(REQUIRED_SOURCES[3],''),...audit});
 assert.equal(r.editorial_custody,'SOURCE_GATE_FAIL');
 assert.ok(r.blockers.includes('TECHNICAL_OR_PHOTO_PROVENANCE_MISSING'));
});
test('missing no-JS free worksheet prevents source gate',()=>{
 const r=assess({landingHtml:src.replace('id="classroom-preview"','id="different"'),...audit});
 assert.ok(r.blockers.includes('FREE_WORKSHEET_PATH_UNPROVEN'));
});
test('the direct route contract cannot pass a second primary CTA',()=>{
 const r=assess({landingHtml:src,...audit,routeAudit:{status:'PASS',primary_cta_count:2}});
 assert.ok(r.blockers.includes('ROUTE_SOURCE_GATE_NOT_PASS'));
});
test('NASA images marked cleared without review cannot pass',()=>{
 const r=assess({landingHtml:src,...audit,mediaAudit:{status:'PASS_SOURCE_CUSTODY_ONLY',record_count:6,commercially_cleared_count:6}});
 assert.ok(r.blockers.includes('NASA_MEDIA_CUSTODY_NOT_SOURCE_ONLY'));
});
test('editorially unreconciled Research Desk source cannot pass',()=>{
 const r=assess({landingHtml:src,...audit,researchAudit:{status:'FAIL'}});
 assert.ok(r.blockers.includes('RESEARCH_DESK_EDITORIAL_GATE_NOT_PASS'));
});
test('campaign IDs remain unassigned absent documented Grok publication',()=>{
 assert.equal(cleanCampaign(null).status,'NOT_SUBMITTED');
 assert.equal(cleanCampaign({...candidateCampaign,asset_id:'test'}).status,'INVALID');
 assert.equal(cleanCampaign({...candidateCampaign,publication_verified:false}).status,'INVALID');
});
test('candidate campaign has deterministic UTM plan but no verified attribution',()=>{
 const c=cleanCampaign(candidateCampaign,reviewedLandingUrl);
 assert.equal(c.status,'CANDIDATE_REQUIRES_INDEPENDENT_PLATFORM_CHECK');
 assert.equal(c.utm.utm_content,candidateCampaign.asset_id);
 const r=assess({landingHtml:src,...audit,campaign:candidateCampaign,reviewedLandingUrl});
 assert.equal(r.campaign.independently_verified,false);
 assert.equal(r.measurement.qualified_human_sessions,'UNOBSERVABLE');
});
test('R138 no reviewed first-party permalink, no candidate attribution',()=>{
 assert.equal(cleanCampaign(candidateCampaign).status,'INVALID');
 const r=assess({landingHtml:src,...audit,campaign:candidateCampaign});
 assert.ok(r.blockers.includes('NO_VERIFIED_GROK_CAMPAIGN_ROUTE'));
 assert.equal(r.measurement.qualified_human_sessions,'UNOBSERVABLE');
});
test('R138 reject disconnected Grok video, asset UTM and destination',()=>{
 for(const delta of [{youtube_video_id:'XXXXXXXXXXX'},
   {destination_url:candidateCampaign.destination_url.replace('apollo_fall_2026_v001','other_asset')},
   {destination_url:candidateCampaign.destination_url.replace('/apollo-1/','/crystal-skulls/')}])
  assert.equal(cleanCampaign({...candidateCampaign,...delta},reviewedLandingUrl).status,'INVALID');
});
test('fake asset URL and wrong social owner fail closed',()=>{
 assert.equal(cleanCampaign({...candidateCampaign,public_url:'https://evil.test/'}).status,'INVALID');
 assert.equal(cleanCampaign({...candidateCampaign,owner:'Apollo'}).status,'INVALID');
});
test('offer must be relevant and rights cleared',()=>{
 for(const change of [{audience:'mindfulness'},{topic:'crystal_skulls'},{nasa_media_embedded:true},
   {original_materials_sha256:'pending'},{refund_policy_reviewed:false},{founder_approval:false}]){
   assert.equal(cleanOffer({...candidateOffer,...change}).status,'BLOCKED',JSON.stringify(change));
 }
});
test('merchant URL must be safe HTTPS with no credentials',()=>{
 for(const u of ['javascript:alert(1)','http://payhip.com/b/abc',
  'https://user:password@payhip.com/b/abc','https://payhip.com/b/abc#token'])
  assert.equal(cleanOffer({...candidateOffer,merchant_url:u}).status,'BLOCKED',u);
});
test('plausible offer data is NEVER independent merchant proof',()=>{
 const r=assess({landingHtml:src,...audit,offer:candidateOffer,campaign:candidateCampaign,
  reviewedLandingUrl,merchantReceipts:[{paid:true}],browserReceipt:{browser_acceptance:'TESTED_LOCAL_ONLY',errors:[]}});
 assert.equal(r.proposed_offer.status,'DOCUMENT_ONLY_NOT_MERCHANT_ATTESTATION');
 assert.equal(r.proposed_offer.independently_verified,false);
 assert.ok(r.blockers.includes('MERCHANT_SETTLEMENT_NOT_INDEPENDENTLY_RECONCILED'));
 assert.ok(r.blockers.includes('PRODUCTION_RELEASE_APPROVAL_NOT_GIVEN'));
 assert.equal(r.live,false);
 assert.equal(r.paid_cta_insertion_authorized,false);
});
test('passing a malformed browser receipt never promotes acceptance',()=>{
 const r=assess({landingHtml:src,...audit,browserReceipt:{browser_acceptance:'TESTED_LOCAL_ONLY',errors:['axe failed']}});
 assert.ok(r.blockers.includes('REAL_BROWSER_ACCEPTANCE_MISSING'));
 assert.equal(r.qa.browser,'LOCAL_TEST_ONLY_NOT_LIVE');
});
test('no visitor identifiers leak into the structured receipt',()=>{
 const r=assess({landingHtml:src,...audit,
  offer:{...candidateOffer,buyer_email:'secret@example.com'},
  campaign:{...candidateCampaign,visitor_id:'sensitive-user'},
  merchantReceipts:[{buyer_email:'secret@example.com',paid:true}]});
 assert.ok(!JSON.stringify(r).includes('secret@example.com'));
 assert.ok(!JSON.stringify(r).includes('sensitive-user'));
});
test('gate receipts are deterministic and need no clock or network',()=>{
 assert.deepEqual(baseline(),baseline());
 assert.doesNotMatch(JSON.stringify(baseline()),/Date\.now|fetch\(|cookie|localStorage/);
});

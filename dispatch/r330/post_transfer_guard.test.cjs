'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),{inspectPostTransfer}=require('./post_transfer_guard.cjs');
const issue={number:3,subject:'The twelve-minute meditation question',kind:'commercial-review-pending'};
const disclosure='If you buy through a link in the guide, Final Vestige may earn a commission.';
const body='A buyer checklist. Read guide: https://finalvestige.com/mind/zen12-guide/ '+disclosure;
const draft={title:issue.subject,status:'draft',_jetpack_dont_email_post_to_subs:true,content:body,primaryCta:'https://finalvestige.com/mind/zen12-guide/',disclosure};
const good={siteEmailContentFormat:'full',actualNativeFooterVerified:true,actualInboxVerified:true,providerEligibilityVerified:true,founderFinalSendApproval:true,partnerEmailPermissionVerified:true,partnerIssuedEarningUrlVerified:true,ownedGuidePublishedVerified:true,checkoutTermsVerified:true};
test('always holds even when all booleans provided',()=>{const x=inspectPostTransfer(issue,draft,good);assert.equal(x.status,'HOLD_UNSENT');assert.equal(x.sendAuthorized,false);assert.equal(x.published,false);});
test('never infers subscribers or paid orders',()=>{const x=inspectPostTransfer(issue,draft,good);assert.equal(x.subscriberCount,'UNKNOWN');assert.equal(x.paidSales,'NOT_INFERRED');});
test('synthetic complete static example',()=>{const x=inspectPostTransfer(issue,draft,good);assert.equal(x.staticChecksComplete,true);});
for(const [name,patch,failed] of [
 ['wrong title',{title:'Extraordinary meditation guaranteed'},'titleExactlyMatchesIntendedSubject'],
 ['publish state',{status:'publish'},'postStillDraft'],
 ['missing opt-out',{_jetpack_dont_email_post_to_subs:false},'explicitEmailOptOut'],
 ['legal placeholder',{content:body+' [[VALID_POSTAL_ADDRESS_REQUIRED]]'},'noUnresolvedTokens'],
 ['affiliate placeholder',{content:body+' [[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]'},'noUnresolvedTokens'],
 ['internal instructions',{content:body+' UNSENT DRAFT DO NOT PUBLISH OR EMAIL'},'noInternalReviewInstructions'],
 ['unsupported claim',{content:body+' 100% concentration'},'noUnsupportedAbsoluteClaims'],
 ['direct merchant link',{content:body+' https://zen12.com/'},'noUnexpectedDirectMerchantLink'],
 ['insecure URL',{content:body+' http://insecure.example/'},'noInsecureOutboundLinks'],
 ['missing CTA',{primaryCta:''},'bodyHasOneRelevantCTA'],
 ['disclosure absent',{disclosure:''},'offerDisclosureAdjacentToCta'],
 ['false native preheader',{claimsNativePreheader:true},'noPreheaderPromisedAsJetpackControl']
]) test('reject '+name,()=>{const x=inspectPostTransfer(issue,{...draft,...patch},good);assert.equal(x.checks[failed],false);});
for(const [name,changed,failed] of [
 ['full email mode',{siteEmailContentFormat:'excerpt'},'fullContentModeAcknowledged'],
 ['native footer',{actualNativeFooterVerified:false},'senderFootersMustBeWitnessed'],
 ['received inbox',{actualInboxVerified:false},'actualInboxMustBeWitnessed'],
 ['consent and eligibility',{providerEligibilityVerified:false},'existingProviderOptInMustBeWitnessed'],
 ['final approval',{founderFinalSendApproval:false},'founderFinalCreativeAudienceScheduleApproval'],
 ['email rights',{partnerEmailPermissionVerified:false},'emailPromotionPermission'],
 ['earning link',{partnerIssuedEarningUrlVerified:false},'actualEarningLinkApproved'],
 ['owned guide',{ownedGuidePublishedVerified:false},'guidePublishedAndVetted'],
 ['seller checkout',{checkoutTermsVerified:false},'sellerCheckoutTermsCurrent']
])test('holds absent '+name,()=>{const x=inspectPostTransfer(issue,draft,{...good,...changed});assert.equal(x.checks[failed],false);assert.equal(x.status,'HOLD_UNSENT');});
test('editorial has independent rights gate',()=>{let x=inspectPostTransfer({number:1,subject:'Editorial',kind:'editorial'},{title:'Editorial',status:'draft',_jetpack_dont_email_post_to_subs:true,content:'Read https://finalvestige.com/focus/',primaryCta:'https://finalvestige.com/focus/'},{siteEmailContentFormat:'full'});assert.equal(x.kind,'editorial');assert.equal('emailPromotionPermission' in x.checks,false);assert.equal(x.checks.noCommercialPromotion,true);});
test('editorial promotion flagged',()=>{let x=inspectPostTransfer({number:4,subject:'Editorial',kind:'editorial'},{title:'Editorial',status:'draft',_jetpack_dont_email_post_to_subs:true,content:'Read https://finalvestige.com/focus/ and buy Zen12',primaryCta:'https://finalvestige.com/focus/'},{});assert.equal(x.checks.noCommercialPromotion,false)});
test('inspection result immutable',()=>{let x=inspectPostTransfer(issue,draft,good);assert.ok(Object.isFrozen(x.checks));assert.ok(Object.isFrozen(x))});

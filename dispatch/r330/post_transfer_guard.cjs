'use strict';
// READ-ONLY, offline: gates a proposed post-backed Jetpack email transformation.
// This library has no sender, WordPress, subscriber, merchant or network interfaces.
const PLACEHOLDER=/\[\[(?:APPROVED_|VALID_POSTAL_|JETPACK_|[^\]\n]{1,80}REQUIRED)[^\]\n]*\]\]/i;
const INTERNAL=/\b(?:UNSENT DRAFT|DO NOT PUBLISH OR EMAIL|Pre-send compliance block|editorial and affiliate review pending)\b/i;
const AD_CLAIMS=/\b(?:guaranteed (?:focus|results|income)|100% (?:focus|concentration)|clinically proven to reprogram|12 minutes equals an hour|buy now before midnight)\b/i;
const S=x=>typeof x==='string'?x:'';
function inspectPostTransfer(issue,draft={},evidence={}){
 const commercial=issue?.kind==='commercial-review-pending',body=S(draft.content),subject=S(issue?.subject);
 const urls=[...body.matchAll(/https?:\/\/[^\s<>"')]+/g)].map(m=>m[0]);
 const checks={
  canonicalIssueRecognized:Number.isInteger(issue?.number)&&issue.number>=1&&issue.number<=6,
  postStillDraft:draft.status==='draft',
  explicitEmailOptOut:draft._jetpack_dont_email_post_to_subs===true,
  titleExactlyMatchesIntendedSubject:!!subject&&S(draft.title)===subject,
  noPreheaderPromisedAsJetpackControl:draft.claimsNativePreheader!==true,
  fullContentModeAcknowledged:evidence.siteEmailContentFormat==='full',
  noInternalReviewInstructions:!INTERNAL.test(body),
  noUnresolvedTokens:!PLACEHOLDER.test(body),
  noUnsupportedAbsoluteClaims:!AD_CLAIMS.test(body),
  bodyHasOneRelevantCTA:typeof draft.primaryCta==='string'&&draft.primaryCta.length>0&&body.includes(draft.primaryCta),
  noInsecureOutboundLinks:urls.every(u=>/^https:\/\//.test(u)),
  noUnexpectedDirectMerchantLink:!urls.some(u=>/^https:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com)(?:\/|$)/i.test(u)),
  senderFootersMustBeWitnessed:evidence.actualNativeFooterVerified===true,
  actualInboxMustBeWitnessed:evidence.actualInboxVerified===true,
  existingProviderOptInMustBeWitnessed:evidence.providerEligibilityVerified===true,
  founderFinalCreativeAudienceScheduleApproval:evidence.founderFinalSendApproval===true
 };
 if(commercial)Object.assign(checks,{
  emailPromotionPermission:evidence.partnerEmailPermissionVerified===true,
  actualEarningLinkApproved:evidence.partnerIssuedEarningUrlVerified===true,
  guidePublishedAndVetted:evidence.ownedGuidePublishedVerified===true,
  sellerCheckoutTermsCurrent:evidence.checkoutTermsVerified===true,
  offerDisclosureAdjacentToCta:typeof draft.disclosure==='string'&&draft.disclosure.toLowerCase().includes('commission')&&body.includes(draft.disclosure)&&body.indexOf(draft.disclosure)>body.indexOf(draft.primaryCta||'')&&body.indexOf(draft.disclosure)-body.indexOf(draft.primaryCta||'')<350
 });else checks.noCommercialPromotion=!/\b(?:affiliate link|purchase through this link|buy (?:zen12|total focus))\b/i.test(body);
 const missing=Object.entries(checks).filter(([,v])=>!v).map(([k])=>k);
 return Object.freeze({issue:issue?.number??null,kind:commercial?'commercial-review-pending':'editorial',status:'HOLD_UNSENT',staticChecksComplete:missing.length===0,missingEvidence:missing,checks:Object.freeze(checks),sendAuthorized:false,published:false,subscriberCount:'UNKNOWN',paidSales:'NOT_INFERRED'});
}
module.exports={inspectPostTransfer};

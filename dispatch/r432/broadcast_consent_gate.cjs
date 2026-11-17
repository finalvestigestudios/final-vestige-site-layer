"use strict";
// Offline-only policy evaluator; never communicates with Jetpack, a merchant or a subscriber.
const ISSUE_KINDS = Object.freeze(["editorial", "editorial", "commercial", "editorial", "commercial", "editorial"]);
const REQUIRED_SHARED = Object.freeze(["providerRecipientEligibility", "consentForCommercialContent", "welcomeReceipt", "nativeJetpackPreview", "publisherPostalAddress", "workingUnsubscribe", "founderFinalApproval"]);
const REQUIRED_COMMERCIAL = Object.freeze(["accountAccepted", "emailChannelAllowed", "exactSkuApproved", "merchantClaimsReviewed", "approvedLiveGuide", "issuedEarningLink", "realReferredCheckout", "adjacentDisclosure", "refundTermsVerified"]);
const REQUIRED_REVENUE = Object.freeze(["independentSettlements", "qualifiedHumanSessions", "refundsAndFees", "joinedCreatorAssetIds"]);
function isTrue(obj,key){return obj != null && obj[key] === true;}
function evaluate(snapshot, proof, issueNumber, offers = []) {
  if (!Number.isInteger(issueNumber) || issueNumber < 1 || issueNumber > 6) throw new Error("issue number must be 1-6");
  if (!snapshot || !proof || typeof proof !== "object") throw new Error("missing evidence");
  if (Object.keys(proof).some(k => /email_address|subscriber_email|ip_address|phone_number/i.test(k))) throw new Error("PII forbidden in review gate");
  const settings = snapshot.settings || {}, subscribers = snapshot.subscribers || {}, followers = snapshot.followers || {};
  const factualFlags = {
    jetpackEnabled: settings.subscriptions === true,
    newPostAutoEmailOff: settings.email_new_posts_by_default === false,
    categoryTargetingOff: settings.newsletter_categories_enabled === false,
    receivingInboxCountVerified: isTrue(proof, "providerRecipientEligibility"),
    zeroDirectEmailFollowersReported: followers.email === 0,
    welcomeConfiguredNotReceipt: !!settings.welcome_message && !isTrue(proof,"welcomeReceipt")
  };
  const issues = [];
  if (!factualFlags.jetpackEnabled) issues.push("NEWSLETTER_DISABLED");
  if (!factualFlags.newPostAutoEmailOff) issues.push("AUTOMATIC_SENDING_DEFAULT_UNSAFE");
  if (!factualFlags.categoryTargetingOff) issues.push("CATEGORY_CONFIGURATION_DRIFT_REQUIRES_REVIEW");
  if (!Number.isInteger(subscribers.total) || !Number.isInteger(subscribers.confirmed) || !Number.isInteger(subscribers.unconfirmed)) issues.push("SUBSCRIBER_DATA_INCOMPLETE");
  else if (subscribers.total < subscribers.confirmed || subscribers.total < subscribers.unconfirmed || subscribers.confirmed + subscribers.unconfirmed > subscribers.total) issues.push("SUBSCRIBER_BUCKETS_NONADDITIVE");
  if (followers.email === 0) issues.push("NO_DIRECT_EMAIL_FOLLOWERS_REPORTED_NOT_ZERO_ELIGIBLE_PEOPLE_PROVEN");
  if (!isTrue(proof,"providerRecipientEligibility")) issues.push("ELIGIBLE_RECIPIENTS_UNVERIFIED");
  for (const field of REQUIRED_SHARED) if(!isTrue(proof, field)) issues.push("MISSING_" + field);
  const commercial = ISSUE_KINDS[issueNumber-1] === "commercial";
  if (commercial) {
    if (!Array.isArray(offers) || offers.length !== 1) issues.push("EXACTLY_ONE_APPROVED_OFFER_REQUIRED");
    else {
      const offer = offers[0];
      const expected = issueNumber === 3 ? "zen12" : "total_focus";
      if (!offer || offer.key !== expected) issues.push("OFFER_DOES_NOT_MATCH_EDITION");
      for (const field of REQUIRED_COMMERCIAL) if (!isTrue(offer,field)) issues.push("MERCHANT_MISSING_" + field);
    }
  } else if (offers.length > 0) issues.push("EDITORIAL_ISSUE_MUST_NOT_INCLUDE_AN_OFFER");
  const reviewEligible = issues.length === 0;
  // Never output a send instruction or a deliverable target. A human/WordPress witness is still required.
  return Object.freeze({issue:issueNumber,kind:ISSUE_KINDS[issueNumber-1],status:reviewEligible ? "HUMAN_REVIEW_ONLY" : "HOLD_UNSENT",sendAuthorized:false,
    actualTransportVerified:isTrue(proof,"nativeJetpackPreview"), targeting:"BROADCAST_ONLY_NO_SUBSCRIBER_SEGMENTS", analyticsSegmentation:"SOURCE_TAGGED_SITE_VISITS_ONLY",
    recipientCount:null, totalDashboardCount:subscribers.total ?? null, confirmedDashboardCount:subscribers.confirmed ?? null, unconfirmedDashboardCount:subscribers.unconfirmed ?? null,
    flags:factualFlags,issues:[...new Set(issues)]});
}
function revenueProof(proof) {const missing=REQUIRED_REVENUE.filter(k=>!isTrue(proof,k));return {status:missing.length ? "NOT_COMPUTABLE" : "SOURCE_DATA_READY_FOR_INDEPENDENT_ACCOUNTING",missing,netRevenuePer1000:null};}
function sourceAttribution(issueNumber) {
  if(!Number.isInteger(issueNumber)||issueNumber<1||issueNumber>6)throw Error("issue 1-6 required");
  // Review-only convention. Never append to a commercial link or deploy until privacy/landing QA.
  return Object.freeze({utm_source:"dispatch",utm_medium:"email",utm_campaign:"dispatch_pilot_2026_11",utm_content:`issue_${String(issueNumber).padStart(2,"0")}`,status:"PROPOSED_NOT_LIVE"});
}
module.exports={ISSUE_KINDS,REQUIRED_SHARED,REQUIRED_COMMERCIAL,evaluate,revenueProof,sourceAttribution};

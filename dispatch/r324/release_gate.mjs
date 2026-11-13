// R324: pure, non-sending evidence gate. No network, CMS, tracking or email actions.
export const REQUIRED = Object.freeze(["merchantAccountApproved","merchantEmailPermission","issuedEarningUrlVerified","approvedLiveGuide","specificSellerTermsVerified","providerEligibleRecipientsVerified","genuineWelcomeReceived","publisherAddressInReceivedEmail","nativeUnsubscribeInReceivedEmail","finalEmailPurposeReviewed","finalReceivedEmailPreview","founderFinalCampaignApproval"]);
export function assess(evidence = {}) {
  const missing = REQUIRED.filter(k => evidence[k] !== true);
  // Seller evidence and consent must be authenticated externally. This function cannot do it.
  if (evidence.affiliateClickAsPaidSale === true || evidence.merchantOptInAsFVLead === true ||
      evidence.pdfDownloadAsConfirmedSignup === true || evidence.browserParamAsConfirmedSignup === true) {
    return {state:"HOLD_UNSENT",merchant:"HOLD_MERCHANT",missing:[...missing,"INVALID_CONVERSION_CLASSIFICATION"],maySend:false};
  }
  return {state:missing.length?"HOLD_UNSENT":"FOUNDER_REVIEW_ONLY",
    merchant:missing.some(k=>["merchantAccountApproved","merchantEmailPermission","issuedEarningUrlVerified","approvedLiveGuide","specificSellerTermsVerified"].includes(k))?"HOLD_MERCHANT":"REVIEW_ONLY",
    missing,maySend:false};
}

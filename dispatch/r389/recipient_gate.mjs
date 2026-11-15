// Dispatch R389: audit-only release evidence, no subscriber import or network calls.
const statuses = new Set(['subscribed','not_subscribed','not_confirmed','bounced','emails_paused','not_sending']);
const isNonNegativeInt = x => Number.isSafeInteger(x) && x >= 0;

export function normalizeProviderSnapshot(s) {
  for (const k of ['total','confirmed','unconfirmed']) {
    if (!isNonNegativeInt(s?.[k])) throw Error(`INVALID_${k.toUpperCase()}`);
  }
  if (s.confirmed > s.total) throw Error('CONFIRMED_EXCEEDS_TOTAL');
  // Unconfirmed records are not necessarily part of total: do NOT sum the columns.
  return Object.freeze({
    confirmedSubscriptions: s.confirmed,
    pendingConfirmationRecords: s.unconfirmed,
    reportedTotal: s.total,
    recipientEligibleCount: null,
    countConflict: false,
    note: 'Unconfirmed is a separate status, not an additive audience count. Eligibility requires provider Email subscription filter.'
  });
}

export function eligibleFromPrivateReview(rows, evidence) {
  if (!Array.isArray(rows) || evidence?.complete !== true || evidence?.source !== 'jetpack_subscriber_tab') {
    return {status:'UNKNOWN',eligibleCount:null};
  }
  const seen = new Set(); let eligible = 0;
  for (const row of rows) {
    if (Object.hasOwn(row,'email') || Object.hasOwn(row,'name') || Object.hasOwn(row,'address')) throw Error('PII_NOT_PERMITTED');
    if (!/^[a-zA-Z0-9_-]{12,}$/.test(row.opaqueProviderId||'')) throw Error('INVALID_OPAQUE_ID');
    if (seen.has(row.opaqueProviderId)) throw Error('DUPLICATE_ID');
    seen.add(row.opaqueProviderId);
    if (!statuses.has(row.emailStatus)) throw Error('UNKNOWN_EMAIL_STATUS');
    if (row.emailStatus==='subscribed') eligible++;
  }
  return {status:'VERIFIED_PRIVATE_REVIEW',eligibleCount:eligible,checkedRecords:rows.length};
}

export function releaseGate(issue, evidence) {
  const blockers = [];
  if (!evidence?.founderFinalApproval) blockers.push('FOUNDER_APPROVAL');
  if (!evidence?.nativeJetpackPreview) blockers.push('NATIVE_PREVIEW');
  if (!evidence?.publisherPostalAddressVerified) blockers.push('PUBLISHER_POSTAL_ADDRESS');
  if (!evidence?.nativeUnsubscribeVerified) blockers.push('NATIVE_UNSUBSCRIBE');
  if (!evidence?.eligibleRecipientProof) blockers.push('ELIGIBLE_RECIPIENT_PROOF');
  if (!evidence?.welcomeFieldbookReceiptVerified) blockers.push('WELCOME_RECEIPT');
  if (issue?.kind === 'commercial') {
    if (!evidence?.namedPartnerEmailPermission) blockers.push('NAMED_EMAIL_PERMISSION');
    if (!evidence?.exactSkuAffiliateUrlVerified) blockers.push('EXACT_SKU_EARNING_URL');
    if (!evidence?.approvedLiveWarmupGuide) blockers.push('APPROVED_LIVE_GUIDE');
    if (!evidence?.offerDisclosureAdjacent) blockers.push('NEAR_OFFER_DISCLOSURE');
    if (!evidence?.merchantCheckoutAndTermsVerified) blockers.push('REFERRED_CHECKOUT_AND_TERMS');
  } else if (issue?.kind !== 'editorial') {
    blockers.push('UNKNOWN_ISSUE_KIND');
  }
  return {state:blockers.length?'HOLD_UNSENT':'READY_FOR_FOUNDER_RECHECK',blockers};
}

export function settledPublisherRevenue(input) {
  if (input?.denominatorAudited !== true || !isNonNegativeInt(input.qualifiedHumanSessions) || input.qualifiedHumanSessions===0 || input.ledgerComplete!==true || !Array.isArray(input.transactions)) {
    return {state:'NOT_COMPUTABLE',netRevenue:null,per1000:null};
  }
  let net = 0; const seen = new Set(); let orders = 0;
  for (const r of input.transactions) {
    if (Object.hasOwn(r,'retailTotal') || Object.hasOwn(r,'customerEmail')) throw Error('RETAIL_OR_PII_NOT_REVENUE');
    if (!/^[a-zA-Z0-9_-]{8,}$/.test(r.opaqueOrderId||'')) throw Error('INVALID_ORDER_ID');
    if (seen.has(r.opaqueOrderId)) throw Error('DUPLICATE_ORDER');
    seen.add(r.opaqueOrderId);
    if (r.status!=='settled' || r.merchantReported!==true) throw Error('UNSETTLED_OR_UNVERIFIED_ORDER');
    for (const k of ['publisherCommission','refundOrClawback','publisherFees']) {
      if (typeof r[k]!=='number' || !Number.isFinite(r[k]) || r[k]<0) throw Error(`INVALID_${k.toUpperCase()}`);
    }
    net += r.publisherCommission-r.refundOrClawback-r.publisherFees; orders++;
  }
  return {state:'COMPUTABLE_FROM_AUDITED_LEDGER',orders,netRevenue:Number(net.toFixed(2)),per1000:Number((net*1000/input.qualifiedHumanSessions).toFixed(2))};
}

/** R254: Offline QA only. Does not install tracking, subscribe users, or authorize mail. */
const PLATFORMS = new Set(['youtube','tiktok','instagram','facebook','pinterest','x','bluesky']);
const TOPICS = new Set(['mind','mysteries','history','preparedness']);
const QUERY_KEYS = new Set(['utm_source','utm_medium','utm_campaign','utm_content']);
const ASSET_ID = /^[a-z0-9][a-z0-9._-]{5,63}$/;
const EMAIL_CONTENT = /^issue0[1-6]_[a-z0-9_]{3,50}$/;
function fail(reason) {return Object.freeze({ok:false,reason});}
function normalizeURL(input) {
  try {
    const u = new URL(input);
    if(u.protocol !== 'https:' || u.hostname !== 'finalvestige.com' ||
       u.port || u.username || u.password || u.hash) return null;
    return u;
  } catch { return null; }
}
function validateQuery(u) {
  for (const [key] of u.searchParams)
    if(!QUERY_KEYS.has(key)) return 'unexpected query key';
  for (const key of QUERY_KEYS)
    if(u.searchParams.getAll(key).length!==1 || !u.searchParams.get(key)) return 'missing/duplicate UTM';
  return null;
}
export function validateSocialLanding(input) {
  const u=normalizeURL(input);
  if(!u) return fail('first-party HTTPS URL required; no URL credentials/fragment');
  if(u.pathname!=='/focus/' && u.pathname!=='/dispatch/' &&
     !u.pathname.startsWith('/mind/')) return fail('unapproved landing route');
  const q=validateQuery(u); if(q) return fail(q);
  const source=u.searchParams.get('utm_source');
  if(!PLATFORMS.has(source)) return fail('source must name actual creator platform, not agent grok');
  if(u.searchParams.get('utm_medium')!=='organic_social')
    return fail('canonical Issue #820 medium: organic_social');
  const campaign=u.searchParams.get('utm_campaign');
  const m=/^([a-z]+)_pilot_(20\d\d)_(0[1-9]|1[0-2])$/.exec(campaign);
  if(!m || !TOPICS.has(m[1])) return fail('topic_pilot_YYYY_MM required');
  const asset=u.searchParams.get('utm_content');
  if(!ASSET_ID.test(asset)) return fail('immutable shaped asset_id required');
  return Object.freeze({ok:true,classification:'TAG_SYNTAX_VALID_NOT_TRAFFIC_VERIFIED',
    platform:source,cluster:m[1],campaign,assetId:asset,route:u.pathname});
}
export function validateEmailGuideLink(input,context={}) {
  const u=normalizeURL(input);
  if(!u || !/^\/mind\/[a-z0-9-]+-guide\/$/.test(u.pathname))
    return fail('approved first-party warm-up guide required');
  const q=validateQuery(u); if(q) return fail(q);
  if(u.searchParams.get('utm_source')!=='dispatch' ||
     u.searchParams.get('utm_medium')!=='email') return fail('Dispatch medium/source required');
  if(u.searchParams.get('utm_campaign')!=='dispatch_pilot_2026_11')
    return fail('versioned campaign required');
  if(!EMAIL_CONTENT.test(u.searchParams.get('utm_content')))
    return fail('issue-specific content required');
  if(context.guideLiveAndEditoriallyApproved!==true) return fail('guide not approved LIVE');
  if(context.partnerEmailPermissionVerified!==true) return fail('named merchant email rights missing');
  if(context.founderApprovedFinalCampaign!==true) return fail('founder final approval missing');
  return Object.freeze({ok:true,classification:'LINK_SYNTAX_AND_ATTESTATIONS_ONLY_NOT_SEND_AUTHORIZATION',
    route:u.pathname});
}
export function evaluateSignupEvidence(e={}) {
  const keys=['gift_ui_shown','focus_pdf_click','focus_signup_click',
    'signup_form_visible','signup_form_submitted'];
  const diagnosticOnly=keys.filter(k=>e[k]===true);
  const confirmed=e.providerSubscriptionStatus==='Subscribed' &&
    e.providerConfirmedTransition===true && e.consentForDispatchVerified===true &&
    e.deduplicatedProviderTransition===true && e.providerSourceAuthenticated===true;
  return Object.freeze({confirmed_signup:confirmed,
    classification:confirmed?'PROVIDER_VERIFIED_PENDING_PRIVACY_REVIEW':'OBSERVATION_ONLY',
    diagnosticOnly,mayEmail:false,verifiedPaidSale:false});
}
export function reportCommercialKPI(e={}) {
  const countOK=Number.isSafeInteger(e.qualifiedHumanSessions)&&e.qualifiedHumanSessions>0;
  const amountOK=Number.isSafeInteger(e.netRevenueCents);
  const independent=e.settlementIndependentlyAuthenticated===true &&
    e.refundsAndFeesReconciled===true && e.qualifiedSessionSourceVerified===true;
  const cohortOK=e.cohortDays===7||e.cohortDays===30;
  if(!countOK||!amountOK||!independent||!cohortOK)
    return Object.freeze({status:'NOT_COMPUTABLE',value:null,
      reason:'independent session and settled revenue evidence required'});
  return Object.freeze({status:'PROVISIONAL_CALCULATION_ONLY',
    value:Number((1000*e.netRevenueCents/100/e.qualifiedHumanSessions).toFixed(2)),
    reason:'arithmetic only: provenance still requires independent human audit'});
}

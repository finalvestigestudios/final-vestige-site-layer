'use strict';
/** Source-only, non-sending Jetpack rehearsal. No network, API, email or subscriber writes. */
const assert = require('node:assert/strict');
const ALLOWED = Object.freeze([1,2,3,4,5,6]);
const COMMERCIAL = new Set([3,5]);
const HARD_STOPS = Object.freeze(['[[VALID_POSTAL_ADDRESS_REQUIRED]]','[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]']);
const MARKETING_HOSTS = new Set(['zen12.com','www.zen12.com','hypnosislive.com','www.hypnosislive.com','inspire3.com','www.inspire3.com','affiliates.inspire3.com']);
function nonnegativeInt(n){ return Number.isSafeInteger(n) && n >= 0; }
function readOnlyAudience(status,followers){
  const s=status?.subscribers||{}, f=followers||{};
  const valid=[s.total,s.confirmed,s.unconfirmed,s.suppressed,s.paid].every(nonnegativeInt);
  if(!valid) return {status:'INVALID_PROVIDER_AGGREGATES',eligible_recipients:null};
  return {status:'AGGREGATES_ONLY_NOT_A_SENDABLE_LIST',reported_total:s.total,reported_confirmed:s.confirmed,
    reported_unconfirmed:s.unconfirmed,reported_wpcom_followers:nonnegativeInt(f.wpcom)?f.wpcom:null,
    reported_legacy_email_followers:nonnegativeInt(f.email)?f.email:null,
    eligible_recipients:null,provider_confirmed_signup_events:null,
    warning:'Provider aggregate groups are overlapping/nonadditive; inspect native Email subscription state privately.'};
}
function firstPartyHref(url){
  try {let u=new URL(url);return u.protocol==='https:'&&u.hostname==='finalvestige.com'&&u.username===''&&u.password==='';}
  catch {return false;}
}
function urlSafety(text){
  if(/(?:\?|&)(?:email|subscriber|uid|user_id|token|address)=/i.test(text))return false;
  if(/https?:\/\/[^\s)\]<>"']+/.test(text)){
    for(const match of text.matchAll(/https?:\/\/[^\s)\]<>"']+/g)){
      try {let h=new URL(match[0].replace(/[.,;]+$/,'')).hostname.toLowerCase();if(MARKETING_HOSTS.has(h))return false;}
      catch{return false;}
    }
  }
  return true;
}
function reviewDraft(number,body,entry){
  const failures=[];
  if(!ALLOWED.includes(number)||entry?.number!==number)failures.push('edition_identity');
  if(typeof body!=='string'||body.length<200){failures.push('missing_manuscript');return {status:'HOLD_UNSENT',failures};}
  if(!body.includes('UNSENT DRAFT')||!body.includes('DO NOT PUBLISH'))failures.push('canonical_draft_banner_missing');
  for(const token of HARD_STOPS)if(!body.includes(token))failures.push('missing_hard_stop:'+token);
  if(!entry?.subject||!body.includes('**Subject:** '+entry.subject))failures.push('subject_manifest_mismatch');
  if(!entry?.preheader||!body.includes('**Preheader:** '+entry.preheader))failures.push('preheader_manifest_mismatch');
  const kind=COMMERCIAL.has(number)?'commercial-review-pending':'editorial';
  if(entry?.kind!==kind||!body.includes('**Content type:** '+kind))failures.push('commercial_identity_mismatch');
  if(COMMERCIAL.has(number)){
    if(!body.includes('**Commercial disclosure:**'))failures.push('commercial_disclosure_missing');
    if(!String(entry?.editorial_cta||'').startsWith('[[APPROVED_'))failures.push('premature_merchant_cta');
    if(!body.includes(entry?.editorial_cta||'__MISSING__'))failures.push('offer_placeholder_mismatch');
  }else if(!firstPartyHref(entry?.editorial_cta))failures.push('unverified_editorial_destination');
  if(entry?.merchant_affiliate_url!==null)failures.push('affiliate_link_activated');
  if(!urlSafety(body))failures.push('unapproved_vendor_or_pii_url');
  return {status:'HOLD_UNSENT',kind,failures,metadata_valid:failures.length===0,send_allowed:false};
}
function nativeJetpackChecklist(manifest,settings){
  assert.equal(manifest?.status,'DRAFT_UNSENT_NO_SCHEDULING');
  const es=manifest?.issues||[];
  if(es.length!==6||new Set(es.map(x=>x.number)).size!==6)throw Error('Six unique canonical editions required');
  const st=settings?.settings||{};
  const config={newsletter_enabled:st.subscriptions===true,auto_send_off:st.email_new_posts_by_default===false,
    full_text_configured:st.email_content_format==='full',sender_name:st.from_name||null,
    welcome_configured:typeof st.welcome_message==='string'&&st.welcome_message.includes('Fieldbook')};
  return {status:'REHEARSAL_NOT_A_EMAIL_PREVIEW',configuration:config,notes:[
    'Jetpack newsletters are delivered from newly published POSTS, not pages or updates to existing posts.',
    'The email subject follows the post title; a manuscript Preheader field is NOT a verified Jetpack inbox preheader.',
    'A WordPress editor Preview email is a visual, non-sending inspection. Send test email contacts a mailbox and is NOT authorized.',
    'Full-text setting is configured, but actual received body, footers, address and unsubscribe remain UNKNOWN.',
    'Do not create, schedule, publish or enable the per-post Send this post to subscribers option before final founder approval.'
  ],editions:es.map(e=>({number:e.number,subject:e.subject,preheader_delivery:'UNVERIFIED',
    commercial:COMMERCIAL.has(e.number),cta:e.editorial_cta,send_status:'HOLD_UNSENT'})),
  founder_send_approval:false,live_jetpack_preview_verified:false,received_welcome_verified:false,
  postal_and_unsubscribe_verified:false,merchant_email_permission_verified:false};
}
module.exports={ALLOWED,COMMERCIAL,HARD_STOPS,nonnegativeInt,readOnlyAudience,firstPartyHref,urlSafety,reviewDraft,nativeJetpackChecklist};

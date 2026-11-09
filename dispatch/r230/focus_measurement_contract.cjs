'use strict';
/** Offline evidence classifier only. NOT installed, NOT a tracking script.
 * Never consider query parameters, page classes, clicks, or download events
 * authoritative evidence of Jetpack email eligibility or commerce.
 */
const ALLOWED_TYPES=new Set(['subscribed','not_confirmed','bounced','emails_paused','not_sending','reader_only']);
function evaluateFocusRecord(record){
  if(!record||typeof record!=='object'||Array.isArray(record))return {confirmed_signup:false,reason:'NO_RECORD'};
  const forbid=['email','ip','address','phone','cookie','ua','user_agent','subscriber_id','name'];
  if(forbid.some(k=>Object.prototype.hasOwnProperty.call(record,k)))return {confirmed_signup:false,reason:'PII_IN_AGGREGATE'};
  if(!record.provider_authenticated||record.provider!=='jetpack'||record.site!=='finalvestige.com')return {confirmed_signup:false,reason:'NO_AUTHENTICATED_PROVIDER'};
  if(!ALLOWED_TYPES.has(record.email_subscription_status))return {confirmed_signup:false,reason:'INVALID_PROVIDER_STATUS'};
  if(record.email_subscription_status!=='subscribed')return {confirmed_signup:false,reason:'NOT_EMAIL_ELIGIBLE'};
  if(record.dispatch_consent!==true)return {confirmed_signup:false,reason:'CONSENT_UNPROVEN'};
  if(record.provider_confirmation_time===undefined|| !/^[0-9]{4}-[0-9]{2}-[0-9]{2}T/.test(String(record.provider_confirmation_time)))return {confirmed_signup:false,reason:'CONFIRMATION_TIME_MISSING'};
  // Self-supplied provider records are NEVER authoritative.
  return {confirmed_signup:false,reason:'PROVIDER_RECORD_REQUIRES_INDEPENDENT_AUTHENTICATION'};
}
function evaluatePageSignal(record){
 const reasons=[];
 if(record?.subscribe_query)reasons.push('QUERY_NOT_CONFIRMATION');
 if(record?.gift_visible)reasons.push('GIFT_NOT_CONFIRMATION');
 if(record?.pdf_clicked)reasons.push('PDF_CLICK_NOT_CONFIRMATION');
 if(record?.subscriber_css)reasons.push('CSS_NOT_EMAIL_ELIGIBILITY');
 return {confirmed_signup:false,paid_customer:false,signal_reasons:reasons};
}
module.exports={evaluateFocusRecord,evaluatePageSignal};

'use strict';
/**
 * R335: synthetic-only provider signup/Fieldbook attribution acceptance gate.
 * No network, no persistent identities, no sender, no connection to Jetpack.
 * Inputs are intentionally restricted to test tokens so real subscriber data
 * must never be copied into source control or this tool.
 */
const MODES = new Set(['email_link_verified', 'preverified_wp_account']);
const ALLOWED = new Set(['kind','synthetic_key','origin','newsletter_consent','email_subscription_status',
 'confirmation_mode','wp_account_preverified','source_surface','proof_id','campaign_id',
 'external_seller','merchant_settlement_confirmed','refund_status']);
const SOURCES = new Set(['focus','dispatch','wordpress_subscribe','post']);
const FORBIDDEN = /email|mailbox|recipient|phone|street|address|ip_address|user_agent|cookie|fingerprint|email_hash|phone_hash|full_name/i;
function checkEvent(e) {
 if (!e || typeof e !== 'object' || Array.isArray(e)) return 'INVALID_OBJECT';
 for (const [key,value] of Object.entries(e)) {
   if (!ALLOWED.has(key)) return 'PII_OR_UNKNOWN_FIELD';
   if (typeof value === 'object' && value !== null) return 'NESTED_PAYLOAD_REJECTED';
 }
 if (typeof e.synthetic_key !== 'string' || !/^synthetic-[a-z0-9_-]{1,36}$/.test(e.synthetic_key)) return 'NOT_SYNTHETIC';
 return null;
}
function signupDecision(e) {
 const err=checkEvent(e);
 if(err) return Object.freeze({accepted:false, reason:err});
 if(e.kind!=='provider_signup') return Object.freeze({accepted:false,reason:'NOT_PROVIDER_SIGNUP'});
 if(e.origin!=='authenticated_wp_provider') return Object.freeze({accepted:false,reason:'PROVIDER_ORIGIN_MISSING'});
 if(e.email_subscription_status!=='Subscribed') return Object.freeze({accepted:false,reason:'NOT_EMAIL_SUBSCRIBED'});
 if(e.newsletter_consent!==true) return Object.freeze({accepted:false,reason:'CONSENT_UNPROVEN'});
 if(!SOURCES.has(e.source_surface)) return Object.freeze({accepted:false,reason:'UNRECOGNIZED_SOURCE'});
 if(typeof e.proof_id!=='string'|| !/^synthetic-proof-[a-z0-9_-]{1,36}$/.test(e.proof_id)) return Object.freeze({accepted:false,reason:'CONFIRMATION_PROOF_ABSENT'});
 if(!MODES.has(e.confirmation_mode)) return Object.freeze({accepted:false,reason:'CONFIRMATION_MODE_UNKNOWN'});
 if(e.confirmation_mode==='preverified_wp_account' && e.wp_account_preverified!==true)
   return Object.freeze({accepted:false,reason:'WP_ACCOUNT_VERIFICATION_NOT_PROVEN'});
 if(e.confirmation_mode==='email_link_verified' && e.wp_account_preverified===true)
   return Object.freeze({accepted:false,reason:'CONFLICTING_CONFIRMATION_MODE'});
 return Object.freeze({accepted:true,reason:'SYNTHETIC_CONFIRMED_SIGNUP'});
}
function evaluateSynthetic(events, dashboard={}) {
 if(!Array.isArray(events) || events.length>1000) throw Error('Expected <=1000 synthetic events');
 const accepted=new Set(); const proofs=new Set(); const rejectionReasons={};
 let syntheticDownloads=0, syntheticWelcomeReceipts=0, syntheticMerchantOptins=0;
 for (const event of events) {
   const err=checkEvent(event);
   if(err){rejectionReasons[err]=(rejectionReasons[err]??0)+1;continue;}
   if(event.kind==='provider_signup') {
     const result=signupDecision(event);
     if(result.accepted) {
       // Synthetic duplicate attempts count at most once per *provider* subject.
       const dedupe=event.synthetic_key;
       if (accepted.has(dedupe)) rejectionReasons.DUPLICATE_PROVIDER_SUBJECT=(rejectionReasons.DUPLICATE_PROVIDER_SUBJECT??0)+1;
       else if(proofs.has(event.proof_id)) rejectionReasons.REUSED_PROVIDER_PROOF=(rejectionReasons.REUSED_PROVIDER_PROOF??0)+1;
       else {accepted.add(dedupe);proofs.add(event.proof_id);}
     } else rejectionReasons[result.reason]=(rejectionReasons[result.reason]??0)+1;
   } else if(event.kind==='fieldbook_download') syntheticDownloads++;
   else if(event.kind==='welcome_received') {
     // Witnessed welcome is a distinct event, never proof of provider eligibility on its own.
     if(event.origin==='independent_recipient_witness' && typeof event.proof_id==='string' && /^synthetic-proof-/.test(event.proof_id)) syntheticWelcomeReceipts++;
     else rejectionReasons.WELCOME_WITNESS_MISSING=(rejectionReasons.WELCOME_WITNESS_MISSING??0)+1;
   } else if(event.kind==='merchant_optin') syntheticMerchantOptins++;
   else rejectionReasons.UNSUPPORTED_EVENT=(rejectionReasons.UNSUPPORTED_EVENT??0)+1;
 }
 // 3 total / 3 confirmed / 2 unconfirmed are *overlapping* provider classifications;
 // follower counts are a different source. NEVER derive deliverable recipients here.
 const snapshotInconsistent= dashboard.total===3 && dashboard.confirmed===3 && dashboard.unconfirmed===2;
 return Object.freeze({status:'HOLD_UNSENT',data_scope:'SYNTHETIC_ONLY',
   synthetic_confirmed_signup_events:accepted.size, synthetic_downloads:syntheticDownloads,
   synthetic_welcome_receipts:syntheticWelcomeReceipts, synthetic_merchant_optins:syntheticMerchantOptins,
   rejected:rejectionReasons, overlapping_counts_observed:snapshotInconsistent,
   actual_confirmed_signups:null, actually_eligible_email_recipients:null,
   verified_paid_orders:null, net_revenue:null, revenue_per_1000_qualified_humans:null,
   sender_authorized:false, merchant_email_permission_verified:false});
}
module.exports={checkEvent,signupDecision,evaluateSynthetic};

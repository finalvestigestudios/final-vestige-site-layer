'use strict';
/**
 * Dispatch R165 — fail-closed POST TRANSPORT AND REVIEW diagnostic.
 * Never connects to WordPress, publishes posts, contacts subscribers, or sends mail.
 * The data argument must be a redacted provider status and canonical campaign manifest.
 */
const RESERVED=/\[\[(?:APPROVED_|VALID_POSTAL_ADDRESS_REQUIRED|JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED)/i;
const PRIVACY=/(?:[\w.+-]+)@(?:[\w-]+\.)+[\w-]+|confirmation[_ -]?token|raw[_ -]?subscriber[_ -]?list|access[_ -]?token/i;
const isSafeCount=n=>Number.isSafeInteger(n)&&n>=0;
function inspectSnapshot(s){
 if(!s||typeof s!=='object'||PRIVACY.test(JSON.stringify(s))) throw Error('Unsafe or absent snapshot');
 const p=s.newsletter_provider;
 if(!p)throw Error('Newsletter provider evidence missing');
 for(const k of ['reported_total','reported_confirmed','reported_unconfirmed','reported_suppressed','recent_observed_posts_not_sent'])
   if(!isSafeCount(p[k])) throw Error('Invalid provider count: '+k);
 if(p.reported_confirmed>p.reported_total)throw Error('Contradictory provider confirmed total');
 if(!Array.isArray(s.issues)||s.issues.length!==6)throw Error('Expected six canonical editions');
 const kinds=s.issues.map(x=>x.kind);
 if(kinds.filter(x=>x==='editorial').length!==4||kinds.filter(x=>x==='commercial-review-pending').length!==2)throw Error('4:2 mix violated');
 const numbers=new Set(s.issues.map(x=>x.edition));
 if(numbers.size!==6||[1,2,3,4,5,6].some(n=>!numbers.has(n))) throw Error('Issue identities drift');
 if(s.issues.some(x=>x.canonical_draft_warning!==true||x.legal_placeholders_present!==true||x.merchant_link_present!==false))throw Error('Original hold safeguards drift');
 return Object.freeze({reported_total:p.reported_total,reported_confirmed:p.reported_confirmed,reported_unconfirmed:p.reported_unconfirmed,verified_email_eligible:null,confirmed_leads:null,delivered_welcomes:null,financial_conversions:null,subscriber_counts_additive:false,status:'HOLD_UNSENT'});
}
function inspectProposedWordPressPost(payload, evidence){
 if(!payload||typeof payload!=='object')throw Error('Missing post');
 // Even an otherwise perfect draft requires human WordPress preview and final founder approval.
 const failures=[];
 if(payload.type!=='post')failures.push('Jetpack newsletters must use WordPress post transport, not a page');
 if(payload.status!=='draft')failures.push('Publication/scheduling is prohibited at this stage');
 if(payload.send_subscription!==false)failures.push('Per-post send flag must be explicitly false');
 if(payload.publish_at!==null)failures.push('Scheduled publication forbidden');
 if(typeof payload.title!=='string'||payload.title.length<8||payload.title.length>160)failures.push('Unsafe/missing title');
 if(typeof payload.body!=='string'||payload.body.length<80)failures.push('Missing email body');
 const b=payload.body||'';
 if(RESERVED.test(b)||/UNSENT DRAFT|DO NOT PUBLISH|Pre-send compliance block/i.test(b))failures.push('Canonical proof and legal placeholders must never enter rendered post body');
 if(/<script\b|<form\b|<iframe\b|<link\b|javascript:/i.test(b))failures.push('Email-unsafe markup');
 if(PRIVACY.test(JSON.stringify(payload)))failures.push('PII or tokens prohibited');
 if(!evidence||evidence.provider_email_preview_verified!==true)failures.push('Genuine non-sending Jetpack preview not attested');
 if(!evidence||evidence.publisher_address_verified!==true)failures.push('FV physical postal address not verified in actual commercial rendering');
 if(!evidence||evidence.unsubscribe_verified!==true)failures.push('Functional native unsubscribe not verified');
 if(!evidence||evidence.email_eligibility_verified!==true)failures.push('Native email-eligible subscriber statuses not verified');
 if(!evidence||evidence.welcome_delivery_verified!==true)failures.push('Actual fieldbook welcome receipt unverified');
 if(payload.issue_kind==='commercial-review-pending'){
  if(!evidence||evidence.named_affiliate_accepted!==true||evidence.email_promotion_allowed!==true||evidence.earning_link_approved!==true||evidence.live_warmup_guide_verified!==true)
   failures.push('Commercial link and email-specific authorization missing');
  if(!/Commercial disclosure:/i.test(b))failures.push('Missing nearby commercial disclosure');
 }
 // No set of data/flags grants permission to send; this is only an offline review gate.
 return Object.freeze({status:'HOLD_UNSENT',preview_candidate:failures.length===0,failures:Object.freeze(failures),send_authorized:false,publish_authorized:false,provider_verified_in_this_test:false});
}
function canReportRevenue(m){
 if(!m||m.qualified_human_sessions_verified!==true||m.provider_paid_orders_verified!==true||m.attribution_verified!==true||m.fees_refunds_reconciled!==true)return Object.freeze({net_per_1000:null,reason:'NOT_COMPUTABLE'});
 if(!Number.isSafeInteger(m.sessions)||m.sessions<=0||![m.receipts,m.fees,m.refunds].every(x=>typeof x==='number'&&Number.isFinite(x)&&x>=0))throw Error('Invalid settled ledger');
 // Receipts must represent FV's actual settled value, not merchant retail order totals.
 if(m.receipts<m.refunds+m.fees)throw Error('Negative net requires explicit reconciled loss policy');
 return Object.freeze({net_per_1000:Math.round((m.receipts-m.fees-m.refunds)*100000/m.sessions)/100,reason:'ONLY_IF_INDEPENDENTLY_ATTESTED'});
}
module.exports={inspectSnapshot,inspectProposedWordPressPost,canReportRevenue};

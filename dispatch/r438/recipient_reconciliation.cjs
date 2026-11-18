"use strict";
/** Offline-only proof evaluator. Not connected to WordPress, commerce or email transports.
 * Keeps dashboard, WordPress.com Reader, direct email followers and filtered recipient status separate.
 * No subscriber emails, names, tokens, IPs or tracking identifiers are accepted or stored.
 */
const evaluate = function evaluate(w) {
  const errors=[];
  const isCount=v=>Number.isSafeInteger(v)&&v>=0;
  const rec=w?.recipient||{}, nl=rec.newsletter||{}, f=rec.followers||{};
  const providerNumbers=["total","confirmed","unconfirmed","suppressed"].filter(k=>!isCount(nl[k]));
  if(providerNumbers.length) errors.push("provider_count_invalid:"+providerNumbers.join(","));
  if(!isCount(f.email)||!isCount(f.wpcom)) errors.push("follower_count_invalid");
  if(!rec.snapshot_id||!rec.newsletter_as_of||!rec.followers_as_of) errors.push("provider_provenance_missing");
  if(isCount(nl.total)&&isCount(nl.confirmed)&&nl.confirmed>nl.total) errors.push("confirmed_exceeds_total");
  const filter=rec.subscribed_filter||{};
  const filtered=filter.source==="jetpack_subscribers_email_status_subscribed" && filter.snapshot_id===rec.snapshot_id && filter.no_addresses_recorded===true && isCount(filter.count) && typeof filter.witness_ref==="string" && filter.witness_ref.length>=8;
  if(!filtered) errors.push("no_same_snapshot_provider_subscribed_filter_witness");
  if(filtered&&f.email===0&&filter.count>0) errors.push("follower_subscribed_disagreement_requires_platform_review");
  const eligible=filtered&&!errors.some(x=>x.startsWith("provider_")||x==="follower_count_invalid"||x==="confirmed_exceeds_total"||x==="provider_provenance_missing"||x==="follower_subscribed_disagreement_requires_platform_review")?filter.count:null;
  const receipt=w?.welcome||{};
  const welcomeEvidence=receipt.authoritative_confirmation===true&&receipt.received_full_fieldbook_welcome===true&&typeof receipt.redacted_witness_ref==="string"&&receipt.redacted_witness_ref.length>=8;
  if(!welcomeEvidence) errors.push("no_actual_welcome_and_double_optin_witness");
  const legal=w?.email||{};
  for(const k of ["native_jetpack_preview","from_identity_checked","publisher_postal_verified","unsub_functionality_verified","subject_and_first_paint_checked","founder_final_send_approval"]){
    if(legal[k]!==true) errors.push("email_gate_missing:"+k);
  }
  const commercial=w?.commercial||{};
  for(const k of ["named_affiliate_approval","email_channel_permission","specific_sku_and_claims_checked","merchant_issued_earning_url","approved_live_warmup_guide","price_refund_checkout_checked","near_offer_disclosure_checked"]){
    if(commercial[k]!==true) errors.push("commercial_gate_missing:"+k);
  }
  const sales=w?.revenue||{}, reported=sales.settled_report||{}, denom=sales.audited_human_sessions;
  const reportOk=reported.complete_7d===true&&reported.complete_30d===true&&reported.independent_merchant_source===true&&isCount(reported.paid_orders)&&Number.isFinite(reported.gross_usd)&&reported.gross_usd>=0&&Number.isFinite(reported.refunds_usd)&&reported.refunds_usd>=0&&Number.isFinite(reported.fees_usd)&&reported.fees_usd>=0&&reported.refunds_usd+reported.fees_usd<=reported.gross_usd;
  const denominatorOk=isCount(denom)&&denom>0&&sales.source_asset_ids_verified===true&&sales.nonhuman_excluded===true;
  if(!reportOk) errors.push("settled_revenue_not_independently_verified");
  if(!denominatorOk) errors.push("qualified_human_denominator_missing");
  const kpi=reportOk&&denominatorOk?Math.round(((reported.gross_usd-reported.refunds_usd-reported.fees_usd)*1000/denom)*100)/100:null;
  const editorialPreviewCandidate=eligible!==null&&eligible>0&&welcomeEvidence&&["native_jetpack_preview","from_identity_checked","publisher_postal_verified","unsub_functionality_verified","subject_and_first_paint_checked"].every(k=>legal[k]===true);
  const commercialPreviewCandidate=editorialPreviewCandidate&&["named_affiliate_approval","email_channel_permission","specific_sku_and_claims_checked","merchant_issued_earning_url","approved_live_warmup_guide","price_refund_checkout_checked","near_offer_disclosure_checked"].every(k=>commercial[k]===true);
  return {status:"HOLD_UNSENT",send_allowed:false,email_follower_count:isCount(f.email)?f.email:null,wpcom_reader_follower_count:isCount(f.wpcom)?f.wpcom:null,newsletter_confirmed:isCount(nl.confirmed)?nl.confirmed:null,not_confirmed_excluded_from_total:isCount(nl.unconfirmed)?nl.unconfirmed:null,verified_receiving_email_subscribers:eligible,editorial_human_review_candidate_only:editorialPreviewCandidate,commercial_human_review_candidate_only:commercialPreviewCandidate,realized_net_usd_per_1000_qualified_sessions:kpi,revenue_status:kpi===null?"NOT_COMPUTABLE":"INDEPENDENTLY_REPORTED",issues:[...new Set(errors)]};
};
module.exports={evaluate};
if(require.main===module){const fs=require("node:fs");const input=process.argv[2];if(!input)throw Error("Provide aggregate-only JSON fixture path");const result=evaluate(JSON.parse(fs.readFileSync(input,"utf8")));process.stdout.write(JSON.stringify(result,null,2)+"\n");}

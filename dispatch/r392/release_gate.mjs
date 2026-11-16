/* Source-only R392 gate. No network, sends, tracking, or PII. */
export const REQUIRED_KEYS=[
"founder_approval","provider_eligible_recipients","fieldbook_welcome_received",
"physical_address_in_actual_email","real_jetpack_preview","real_unsubscribe_test",
"merchant_named_approval","merchant_specific_sku_rights","merchant_email_rights",
"merchant_issued_link","merchant_referral_price_refund_verified","mind_guide_published_approved",
"settled_commission_ledger","qualified_human_session_audit"];
export const MERCHANT_KEYS=REQUIRED_KEYS.filter(x=>x.startsWith("merchant_")||x==="mind_guide_published_approved");
export function auditRelease(d){
 const reasons=[];
 if(d?.status!=="HOLD_UNSENT")reasons.push("draft_status");
 if(d?.canonical?.untouched!==true||d?.canonical?.editorial!==4||d?.canonical?.commercial!==2)reasons.push("4_2_mix_integrity");
 if(d?.candidate?.adopted!==true)reasons.push("not_adopted");
 if(d?.candidate?.cta!=="APPROVED_URL")reasons.push("cta_inert");
 // Every proof is explicitly required. Omitted keys must never mean "not applicable".
 for(const k of REQUIRED_KEYS)if(!Object.hasOwn(d?.attestation??{},k)||d.attestation[k]!==true)reasons.push("missing_proof:"+k);
 if(typeof d?.candidate?.approved_live_guide_url!=="string"||!d.candidate.approved_live_guide_url.startsWith("https://"))reasons.push("guide_url_missing");
 if(typeof d?.candidate?.authorized_earning_url!=="string"||!d.candidate.authorized_earning_url.startsWith("https://"))reasons.push("earning_url_missing");
 // Even after all proofs are supplied, an explicit human and platform send gate remains outside this verifier.
 return {send_authorized:false,can_enter_human_review:reasons.length===0,reasons};
}
export function confirmedLeadCount(items){
 if(!Array.isArray(items))return null;
 const ids=new Set(),transitions=new Map();
 for(const e of items){
  // A historical confirmed snapshot, download-panel click or pending attempt is NOT a new signup.
  if(!e||e.provider!=="JETPACK"||e.status!=="confirmed"||e.transition!=="newly_confirmed"||
     typeof e.opaque_id!=="string"||!/^[-_a-zA-Z0-9]{8,100}$/.test(e.opaque_id)||
     typeof e.transition_id!=="string"||!/^[-_a-zA-Z0-9]{8,100}$/.test(e.transition_id))return null;
  // Repeated provider-event IDs cannot represent different subscriber identities.
  if(transitions.has(e.transition_id)&&transitions.get(e.transition_id)!==e.opaque_id)return null;
  transitions.set(e.transition_id,e.opaque_id);
  ids.add(e.opaque_id);
 }
 return ids.size;
}
export function netRevenuePerThousand(x){
 if(x?.commission_ledger_verified!==true||x?.sessions_audited!==true||!Number.isFinite(x?.net_commission)||!Number.isSafeInteger(x?.human_sessions)||x.human_sessions<=0)return {status:"NOT_COMPUTABLE",value:null};
 return {status:"COMPUTABLE",value:1000*x.net_commission/x.human_sessions};
}
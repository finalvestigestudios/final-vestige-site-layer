/* Source-only R392 gate. Intentionally cannot authorize sending. */
export const MERCHANT_KEYS=["merchant_named_approval","merchant_specific_sku_rights","merchant_email_rights","merchant_issued_link","merchant_referral_price_refund_verified","mind_guide_published_approved"];
export function auditRelease(d){
 const reasons=[];
 if(d?.status!=="HOLD_UNSENT")reasons.push("draft_status");
 if(d?.canonical?.untouched!==true||d?.canonical?.editorial!==4||d?.canonical?.commercial!==2)reasons.push("4_2_mix_integrity");
 if(d?.candidate?.adopted!==true)reasons.push("not_adopted");
 if(d?.candidate?.cta!=="APPROVED_URL")reasons.push("cta_inert");
 for(const k of Object.keys(d?.attestation||{}))if(d.attestation[k]!==true)reasons.push("missing_proof:"+k);
 for(const k of MERCHANT_KEYS)if(d?.attestation?.[k]!==true&&!reasons.includes("missing_proof:"+k))reasons.push("missing_proof:"+k);
 if(typeof d?.candidate?.approved_live_guide_url!=="string"||!d.candidate.approved_live_guide_url.startsWith("https://"))reasons.push("guide_url_missing");
 if(typeof d?.candidate?.authorized_earning_url!=="string"||!d.candidate.authorized_earning_url.startsWith("https://"))reasons.push("earning_url_missing");
 return {send_authorized:false,can_enter_human_review:reasons.length===0,reasons};
}
export function confirmedLeadCount(items){
 if(!Array.isArray(items))return null;
 const ids=new Set();
 for(const e of items){
 if(!e||e.provider!=="JETPACK"||e.status!=="confirmed"||typeof e.opaque_id!=="string"||!/^[-_a-zA-Z0-9]{8,100}$/.test(e.opaque_id))return null;
 ids.add(e.opaque_id);
 }
 return ids.size;
}
export function netRevenuePerThousand(x){
 if(x?.commission_ledger_verified!==true||x?.sessions_audited!==true||!Number.isFinite(x?.net_commission)||!Number.isSafeInteger(x?.human_sessions)||x.human_sessions<=0)return {status:"NOT_COMPUTABLE",value:null};
 return {status:"COMPUTABLE",value:1000*x.net_commission/x.human_sessions};
}
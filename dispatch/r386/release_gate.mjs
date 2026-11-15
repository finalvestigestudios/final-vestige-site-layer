/** Offline evidence-only release gate. Never contacts subscribers or network. */
export function releaseGate(issue,proof){
 const commercial=issue===3||issue===5, blockers=[];
 const requireKeys=["founder_final_approval","native_jetpack_preview","valid_final_vestige_postal","working_unsubscribe","provider_confirmed_eligible_inboxes","confirmed_consent_scope","fieldbook_welcome_received","jetpack_subject_verified","native_preheader_verified","research_claims_checked"];
 for(const k of requireKeys)if(proof?.[k]!==true)blockers.push(k);
 if(commercial)for(const k of ["publisher_account_accepted","sku_email_rights","approved_creative","issued_earning_url","mind_guide_live","referred_checkout_verified","refund_qualifications","disclosure_next_to_offer","product_claims_qualified"])if(proof?.merchant?.[k]!==true)blockers.push("merchant_"+k);
 return {issue,type:commercial?"commercial":"editorial",verdict:blockers.length?"HOLD_UNSENT":"REVIEW_READY_NOT_AUTHORIZED_TO_SEND",blockers};
}
export function confirmedSignups(events,coverage){
 if(coverage?.authoritative_provider_export_complete!==true||!Array.isArray(events))return {status:"NOT_COMPUTABLE",count:null};
 const dedup=new Set();
 for(const e of events)if(e?.provider==="jetpack"&&e.status==="confirmed"&&e.double_optin_verified===true&&e.email_eligible===true&&e.provider_verified===true&&typeof e.provider_subscriber_id==="string"&&e.provider_subscriber_id.trim())dedup.add(e.provider_subscriber_id);
 return {status:"PROVIDER_CONFIRMED_AGGREGATE",count:dedup.size};
}
export function revenuePer1000(data){
 if(!data||data.merchant_export_complete!==true||data.adjustments_complete!==true||data.sessions_audited!==true||!Array.isArray(data.orders)||!Number.isSafeInteger(data.qualified_human_sessions)||data.qualified_human_sessions<=0)return {status:"NOT_COMPUTABLE",net:null,per_1000:null};
 let net=0;const ids=new Set();
 for(const o of data.orders){
  if(o?.source!=="merchant_settlement"||o.status!=="paid_settled"||typeof o.id!=="string"||!o.id||ids.has(o.id))continue;
  const v=[o.publisher_commission_paid,o.refunds,o.clawbacks,o.fees];
  if(!v.every(x=>Number.isFinite(x)&&x>=0))return {status:"NOT_COMPUTABLE",net:null,per_1000:null};
  ids.add(o.id);net+=v[0]-v[1]-v[2]-v[3];
 }
 return {status:"VERIFIED_AGGREGATE",settled_orders:ids.size,net:+net.toFixed(2),per_1000:+(1000*net/data.qualified_human_sessions).toFixed(2)};
}

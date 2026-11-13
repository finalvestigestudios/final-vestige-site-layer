/** R318: pure source-evidence classifier; non-sending, non-collecting, no network or DOM. Counts are ONLY as reliable as provider-issued inputs. */
export function auditProof(events, options={}){
 if(!Array.isArray(events))throw Error("EVENTS_ARRAY_REQUIRED");
 const sessions=new Map(),signups=new Set(),orders=new Map(),rejected=[];
 let clicks=0,downloads=0,attempts=0;
 const safe=v=>typeof v==="number"&&Number.isFinite(v)&&v>=0;
 for(const e of events){
  if(!e||typeof e!=="object"||Array.isArray(e))throw Error("BAD_EVENT");
  if(Object.keys(e).some(k=>/(^email$|_email$|email_address|^phone$|^address$|^full_name$|^first_name$|^last_name$)/i.test(k)))throw Error("PII_FIELD_REJECTED");
  const t=Date.parse(e.at);
  if(!Number.isFinite(t)||(options.start&&t<Date.parse(options.start))||(options.end&&t>Date.parse(options.end)))continue;
  if(e.kind==="cta_click"){clicks++;continue}
  if(e.kind==="pdf_download"){downloads++;continue}
  if(e.kind==="signup_attempt"){attempts++;continue}
  if(e.kind==="qualified_session"){
   if(e.origin!=="first_party_qa"||e.human!=="verified"||!e.session_ref||!e.asset_id||e.utm_content!==e.asset_id||e.utm_medium!=="organic_social"){rejected.push("SESSION_PROOF");continue}
   const sign=JSON.stringify([e.asset_id,e.utm_source,e.utm_campaign,e.utm_content]);
   if(sessions.has(e.session_ref)&&sessions.get(e.session_ref)!==sign)throw Error("SESSION_CONFLICT");
   sessions.set(e.session_ref,sign);
  }else if(e.kind==="confirmed_signup"){
   if(e.origin!=="jetpack_verified_record"||e.provider_ack!==true||e.email_status!=="active"||e.dispatch_consent!==true||!e.subscriber_ref){rejected.push("SIGNUP_PROOF");continue}
   signups.add(e.subscriber_ref);
  }else if(e.kind==="paid_settlement"){
   if(!["payhip_settlement","inspire3_partner_settlement"].includes(e.origin)||e.provider_ack!==true||e.settled!==true||e.received!==true||!e.order_ref||!["owned_product","affiliate_commission"].includes(e.basis)||![e.proceeds_usd,e.fees_usd,e.refunds_usd].every(safe)){rejected.push("REVENUE_PROOF");continue}
   const sign=JSON.stringify([e.basis,e.proceeds_usd,e.fees_usd,e.refunds_usd]);
   if(orders.has(e.order_ref)&&orders.get(e.order_ref)!==sign)throw Error("ORDER_CONFLICT");
   orders.set(e.order_ref,sign);
  }
 }
 let cents=0;
 for(const order of orders.values()){const [,p,f,r]=JSON.parse(order);cents+=Math.round(100*p)-Math.round(100*f)-Math.round(100*r)}
 const netUsd=Math.round(cents)/100,denom=sessions.size;
 return Object.freeze({qualified_human_sessions:denom,confirmed_signups:signups.size,settled_paid_orders:orders.size,realized_net_usd:orders.size?netUsd:null,net_usd_per_1000_qualified_sessions:(orders.size&&denom)?Math.round((netUsd*1000/denom)*100)/100:null,lead_to_customer_rate:null,diagnostic_cta_clicks:clicks,diagnostic_pdf_downloads:downloads,diagnostic_signup_attempts:attempts,rejected_proof_events:rejected.length,status:orders.size&&denom?"INPUT_DEPENDENT_NOT_LIVE_VERIFIED":"NOT_COMPUTABLE_FROM_INPUT"});
}

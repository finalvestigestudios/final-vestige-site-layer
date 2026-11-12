// R305. No network, no sender, no personal data.
export function replay({asOf,events}) {
 const day=s=>{const d=Date.parse(s);if(!Number.isFinite(d))throw Error("Invalid time");return d;};
 const now=day(asOf+"T23:59:59Z"),sessions=new Map(),leads=new Set(),orders=new Map(),reasons={};
 const reject=k=>reasons[k]=(reasons[k]||0)+1;
 const types=["visit","form_submit","pdf_download","provider_subscribed","welcome_received","guide_click","merchant_click","merchant_settled_order","merchant_refund"];
 for(const e of events){
  if(!e||!types.includes(e.type))throw Error("Bad event");
  if(/["']?(email|phone|ip_address|full_name|cookie|utm_email)["']?\s*:/i.test(JSON.stringify(e))||/@[\w.-]+\.[a-z]{2,}/i.test(JSON.stringify(e)))throw Error("PII prohibited");
  if(typeof e.session!=="string"||!/^[a-z0-9_-]{4,48}$/i.test(e.session))throw Error("Invalid opaque session");
  const ts=day(e.at);if(ts>now){reject("future");continue;}
  if(e.type==="visit"){
   if(sessions.has(e.session)){reject("repeated_visit");continue;}
   const tagged=e.utm_source==="grok"&&/^[a-z0-9_-]{3,50}$/i.test(e.asset_id||"")&&/^[a-z0-9_-]{3,80}$/i.test(e.utm_campaign||"");
   const qualified=tagged&&e.human_verified===true&&e.bot_flag!==true;
   sessions.set(e.session,{at:ts,qualified,lead:false,guide:false,outbound:false});
   if(!qualified)reject("unqualified_visit");continue;
  }
  const s=sessions.get(e.session);if(!s){reject("orphan");continue;}if(ts<s.at){reject("out_of_order");continue;}
  if(e.type==="form_submit"||e.type==="pdf_download"){reject(e.type+"_not_signup");continue;}
  if(e.type==="provider_subscribed"){
   const confirmed=e.status==="Subscribed"&&e.consent_to_dispatch===true&&e.suppressed!==true&&(
    e.path==="confirmed_email"&&e.email_confirmation_verified===true||
    e.path==="existing_verified_wp_account"&&e.provider_account_verified===true);
   if(!confirmed||!/^PROOF-[A-Z0-9-]{8,60}$/.test(e.proof_ref||"")){reject("invalid_provider_proof");continue;}
   if(leads.has(e.proof_ref)){reject("duplicate_confirmed_signup");continue;}
   leads.add(e.proof_ref);s.lead=true;continue;
  }
  if(e.type==="welcome_received"){if(!(s.lead&&e.receipt_verified===true))reject("welcome_not_proven");continue;}
  if(e.type==="guide_click"){if(s.lead&&e.destination==="approved_first_party_guide"&&e.guide_live_verified===true)s.guide=true;else reject("guide_ineligible");continue;}
  if(e.type==="merchant_click"){if(s.guide&&e.email_permission_verified===true&&e.issued_link_verified===true)s.outbound=true;else reject("merchant_ineligible");continue;}
  if(e.type==="merchant_settled_order"){
   const valid=s.outbound&&e.independent_partner_report===true&&e.verified_attribution===true&&e.status==="settled"&&
   Number.isSafeInteger(e.gross_cents)&&e.gross_cents>=0&&Number.isSafeInteger(e.fees_cents)&&e.fees_cents>=0&&
   /^ORDER-[A-Z0-9-]{7,50}$/.test(e.order_ref||"");
   if(!valid||orders.has(e.order_ref)){reject("order_unverified_or_duplicate");continue;}
   orders.set(e.order_ref,{session:e.session,gross:e.gross_cents,fees:e.fees_cents,refund:0,customer_ref:e.customer_ref_verified===true&&/^CUSTOMER-[A-Z0-9-]{7,50}$/.test(e.customer_ref||"")?e.customer_ref:null});continue;
  }
  if(e.type==="merchant_refund"){
   const o=orders.get(e.order_ref);if(!o||o.session!==e.session||e.partner_refund_verified!==true||!Number.isSafeInteger(e.refund_cents)||e.refund_cents<0||e.refund_cents>o.gross-o.refund){reject("refund_unverified");continue;}
   o.refund+=e.refund_cents;
  }
 }
 const result={status:"SYNTHETIC_OFFLINE_ONLY",send_authorized:false,
  holds:["founder_final_send_approval_missing","merchant_publisher_email_permission_unverified","guide_live_unverified","eligible_recipient_population_unknown","real_received_email_unsubscribe_and_publisher_postal_address_missing","genuine_jetpack_preview_unverified"],
  counts:{observed_opaque_sessions:sessions.size,unique_provider_proofs:leads.size,verified_orders:orders.size},rejection_counts:reasons,cohorts:{}};
 for(const days of [7,30]){
  const ss=[...sessions].filter(([_,v])=>v.qualified&&v.at>now-days*86400000&&v.at<=now);
  const keys=new Set(ss.map(([k])=>k)),os=[...orders.values()].filter(o=>keys.has(o.session));
  const q=ss.length,n=os.length,l=ss.filter(([_,s])=>s.lead).length,customers=os.length>0&&os.every(o=>o.customer_ref)?new Set(os.map(o=>o.customer_ref)).size:null;
  const gross=os.reduce((a,o)=>a+o.gross,0),fees=os.reduce((a,o)=>a+o.fees,0),refunds=os.reduce((a,o)=>a+o.refund,0);
  result.cohorts["d"+days]={qualified_human_sessions:q,confirmed_signups:l,settled_orders:n,gross_cents:n?gross:null,fees_cents:n?fees:null,
   refunds_cents:n?refunds:null,net_cents:n?gross-fees-refunds:null,
   net_per_1000_qualified_sessions_cents:n&&q?Math.round(1000*(gross-fees-refunds)/q):null,
   verified_paying_customers:customers,paid_conversion_rate:customers!==null&&q?customers/q:null,lead_to_customer_rate:customers!==null&&l?customers/l:null,
   caveat:"entirely synthetic; no A/B claims or real-revenue inference"};
 }
 return result;
}

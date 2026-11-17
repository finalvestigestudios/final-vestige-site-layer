function analyzeCohort(events,opts){
 if(!Array.isArray(events)||!opts||![7,30].includes(opts.window_days))throw Error("invalid input/window");
 const end=Date.parse(opts.as_of);
 if(!Number.isFinite(end)||! /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(opts.as_of))throw Error("invalid as_of");
 const start=end-opts.window_days*86400000, seen=new Set(),sessions=new Map(),leads=[],orders=[];
 const allowed={
 session:["kind","id","at","proof_ref","audit_class","qualified_human","utm_source","utm_medium","utm_campaign","asset_id"],
 signup:["kind","id","at","proof_ref","audit_class","session_id","subscriber_token","confirmed","email_eligible","unsubscribed"],
 sale:["kind","id","at","proof_ref","audit_class","session_id","order_ref","state","gross_cents","fees_cents","refund_cents"]
 };
 for(const e of events){
  if(!e||typeof e!=="object"||!allowed[e.kind])throw Error("invalid event");
  if(Object.keys(e).some(k=>!allowed[e.kind].includes(k)))throw Error("PII/unknown field");
  if(Object.values(e).some(v=>typeof v==="string"&&(/@|https?:|[?&](email|token)=/i.test(v)||v.length>180)))throw Error("PII/link in data");
  if(!/^[a-z][a-z0-9_-]{3,50}$/.test(e.id||"")||seen.has(e.id))throw Error("duplicate/bad id");seen.add(e.id);
  if(!/^audit_[a-z0-9_-]{8,80}$/.test(e.proof_ref||""))throw Error("invalid opaque evidence");
  if(!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(e.at||"")||!Number.isFinite(Date.parse(e.at)))throw Error("event timestamp");
  const time=Date.parse(e.at);if(time<start||time>end)continue;
  if(e.kind==="session"){
   if(e.audit_class==="first_party_human_audit"&&e.qualified_human===true
    &&["youtube","tiktok","instagram","facebook","pinterest","x","bluesky"].includes(e.utm_source)
    &&e.utm_medium==="organic_social"
    &&/^[a-z0-9_]{6,80}$/.test(e.utm_campaign||"")
    &&/^[a-z0-9_-]{6,80}$/.test(e.asset_id||""))sessions.set(e.id,time);
  }else if(e.kind==="signup")leads.push({...e,time});
  else orders.push({...e,time});
 }
 const uniqueLeads=new Set(),uniqueOrders=new Set();
 let gross=0,fees=0,refunds=0;
 for(const e of leads){
  const t=sessions.get(e.session_id);if(t===undefined||e.time<t)continue;
  if(e.audit_class!=="jetpack_confirmation_record"||e.confirmed!==true||e.email_eligible!==true||e.unsubscribed!==false)continue;
  if(!/^[a-f0-9]{40}$/.test(e.subscriber_token||""))continue;
  uniqueLeads.add(e.subscriber_token);
 }
 for(const e of orders){
  const t=sessions.get(e.session_id);if(t===undefined||e.time<t)continue;
  if(e.audit_class!=="merchant_paid_settlement"||e.state!=="settled"
     ||!/^order_[a-z0-9_-]{8,60}$/.test(e.order_ref||"")
     ||!["gross_cents","fees_cents","refund_cents"].every(k=>Number.isSafeInteger(e[k])&&e[k]>=0))continue;
  if(uniqueOrders.has(e.order_ref))continue;uniqueOrders.add(e.order_ref);
  gross+=e.gross_cents;fees+=e.fees_cents;refunds+=e.refund_cents;
 }
 const net=gross-fees-refunds;
 return {mode:"SYNTHETIC_TEST_ONLY",production_verified:false,business_net_per_1000:null,
  simulated_qualified_sessions:sessions.size,simulated_confirmed_leads:uniqueLeads.size,
  simulated_settled_orders:uniqueOrders.size,simulated_net_cents:net,
  simulated_net_per_1000_cents:sessions.size?Math.round(net*1000/sessions.size):null,
  sample_warning:sessions.size<100||uniqueOrders.size<20,release:"HOLD_UNSENT"};
}
export { analyzeCohort };

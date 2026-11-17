// R424 evidence and copy gate. No network or writes.
export function audit(s,d,f,h){
 const errors=[],norm=x=>String(x||"").toLowerCase();
 if(s?.schema!=="fv-dispatch-r424-v1")errors.push("SCHEMA");
 if(s?.newsletter_enabled!==true||s?.auto_send!==false)errors.push("AUTO_SEND_OR_NEWSLETTER_DRIFT");
 if(s?.dashboard?.total!==3||s?.dashboard?.confirmed!==3||s?.dashboard?.unconfirmed!==2)errors.push("SOURCE_COUNTS_DRIFT");
 if(s?.eligible_unique!==null)errors.push("ELIGIBLE_RECIPIENT_FABRICATED");
 if(s?.issues?.editorial!==4||s?.issues?.commercial!==2)errors.push("PILOT_RATIO");
 for(const [name,copy]of [["DISPATCH",d],["FOCUS",f]]){
  if(!norm(copy).includes("occasion")||!norm(copy).includes("confirm"))errors.push(name+"_CONSENT_COPY");
  if(!norm(copy).includes("do not")||!norm(copy).includes("every"))errors.push(name+"_CADENCE");
  if(!norm(copy).includes("free")||!norm(copy).includes("without"))errors.push(name+"_FREE_ACCESS");
  if(/href=["']https?:\/\/(?:inspire3|zen12|hypnosislive)/i.test(copy))errors.push(name+"_MERCHANT_LINK");
 }
 if(!/<html lang="en">/.test(h)||!/viewport/.test(h)||!/focus-visible/.test(h))errors.push("ACCESSIBILITY");
 if(/<(?:form|input|script|iframe)\b/i.test(h))errors.push("NONSTATIC_REVIEW");
 if((h.match(/<h1\b/g)||[]).length!==1)errors.push("HEADING");
 if(/href=["']https?:\/\/(?:inspire3|zen12|hypnosislive)/i.test(h))errors.push("COMMERCIAL_LINK");
 for(const key of ["welcome_received","jetpack_preview","postal_verified","unsubscribe_verified","inspire3_email_permission","affiliate_link_verified","paid_orders_verified","founder_send_approval"])if(s?.[key]!==false)errors.push("UNWITNESSED_"+key);
 if(s?.qualified_human_sessions!==null||s?.net_revenue_per_1000!==null)errors.push("FAKE_REVENUE");
 return {pass:errors.length===0,errors,release:"HOLD_UNSENT",send:false,publish:false};
}

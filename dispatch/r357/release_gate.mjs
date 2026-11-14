// R357: pure offline release validation; no network, WordPress or mail access
export const validate=function validate(d){
 const err=[];const o=d.original,l=d.ledger;
 if(o.status!=="DRAFT_UNSENT_NO_SCHEDULING"||o.issues?.length!==6||o.issues.filter(x=>x.kind==="editorial").length!==4||o.issues.filter(x=>x.kind==="commercial-review-pending").length!==2)err.push("original campaign");
 if(o.issues.some(x=>x.merchant_affiliate_url!==null||x.publish_state!=="hold"))err.push("original activated");
 if(l.decision!=="HOLD_UNSENT"||l.original_adoption!==false||l.compliance.all!=="HOLD_UNSENT"||l.compliance.founder_send_approval!==false)err.push("release false");
 if(l.time_reconstruction.length!==4||!l.time_reconstruction.some(x=>x.interval.includes("14 seconds")&&x.kind.includes("preliminary"))||!l.time_reconstruction.some(x=>x.interval.includes("15 seconds")&&x.kind.includes("later")))err.push("source chronology");
 if(l.time_reconstruction.some(x=>!(x.source.startsWith("https://www.nasa.gov/")||x.source.startsWith("https://nssdc.gsfc.nasa.gov/"))))err.push("untrusted source");
 if(l.merchant.length!==2||l.merchant.some(x=>x.status!=="HOLD_MERCHANT"||x.publisher_email_permission!=="NOT VERIFIED"||x.affiliate_url!=="NOT VERIFIED"||x.live_guide!=="NOT VERIFIED"))err.push("merchant false");
 for(const s of [d.md,d.txt,d.html]){
  if(!s.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]")||!s.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"))err.push("legal footer");
  if(!s.includes("https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/invest.html")||!s.includes("https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/seamans.html"))err.push("citation");
  if(/https:\/\/(?:zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com)|died in 14 seconds|NASA confirmed the first spark/i.test(s))err.push("unsafe claim/merchant");
  if(!/UNSENT/.test(s))err.push("mail hold missing");
 }
 if(!d.md.includes("**PRIMARY CTA:**")||!d.txt.includes("PRIMARY CTA:")||!d.html.includes('href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"'))err.push("CTA");
 if(!d.md.includes("NOT ADOPTED")||!d.html.includes("NOT ADOPTED"))err.push("not adopted label");
 if(!d.html.includes('role="presentation"')||!d.html.includes('lang="en"')||!d.html.includes("SIMULATED PREHEADER, NOT JETPACK-VERIFIED")||/<(form|script|iframe|img)\b/i.test(d.html))err.push("HTML safety");
 if(/Subject:\*\* Fourteen seconds\./.test(d.md))err.push("ambiguous subject");
 return {ok:err.length===0,errors:err};
};

export function review(html,text,manifest) {
 const errors=[];
 if(manifest.release!=="HOLD_UNSENT"||manifest.send_authorized!==false)errors.push("UNAUTHORIZED_RELEASE");
 if(/SUBSCRIBER-FACING CANDIDATE COPY ENDS|Complete research notes \/ proof limits|Reviewer internal/i.test(html+text))errors.push("INTERNAL_NOTES_LEAK");
 if(!html.includes('lang="en"')||!html.includes('role="presentation"')||!html.includes('<h1 ')||!html.includes('<h2 '))errors.push("STRUCTURE");
 if(/<(?:script|iframe|form|img|video|audio)\b/i.test(html))errors.push("UNSAFE_MARKUP");
 if(!html.includes("REVIEW ONLY / HOLD UNSENT")||!text.includes("HOLD UNSENT"))errors.push("NO_VISIBLE_HOLD");
 if(!html.includes("Commercial disclosure")||!text.includes("Commercial disclosure"))errors.push("MISSING_DISCLOSURE");
 if(!html.includes("[GUIDE UNAVAILABLE")||!text.includes("[GUIDE UNAVAILABLE"))errors.push("FAKE_GUIDE_LINK");
 if(/<a[^>]+href="[^"]*(?:affiliate_id=|subid=|utm_medium=affiliate|zen12\.com\/secret)/i.test(html))errors.push("UNAPPROVED_REFERRAL");
 if(!html.includes("[[VALID_FV_POSTAL_ADDRESS_REQUIRED]]")||!text.includes("[[VALID_FV_POSTAL_ADDRESS_REQUIRED]]"))errors.push("UNVERIFIED_POSTAL");
 if(!html.includes("[[RENDERED_JETPACK_UNSUBSCRIBE_REQUIRED]]")||!text.includes("[[RENDERED_JETPACK_UNSUBSCRIBE_REQUIRED]]"))errors.push("UNVERIFIED_UNSUBSCRIBE");
 for(const url of ["gutenberg.org/ebooks/78413","rcpe.ac.uk/sites","hypnosislive.com/faq","finalvestige.com/editorial-standards/"])if(!html.includes(url)||!text.includes(url))errors.push("MISSING_SOURCE:"+url);
 if(manifest.revenue_per_1000!==null||manifest.settled_net_revenue!==null)errors.push("FABRICATED_REVENUE");
 if(["merchant_email_permission","merchant_earning_url","live_guide","actual_jetpack_preview","received_fieldbook_welcome","valid_publisher_postal","rendered_optout","founder_final_campaign_approval"].some(x=>manifest[x]!==false))errors.push("FALSE_ATTESTATION");
 return {pass:errors.length===0,errors,release:"HOLD_UNSENT"};
}

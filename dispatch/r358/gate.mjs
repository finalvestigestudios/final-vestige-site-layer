// Pure offline R358 guard; no filesystem, network, mail or checkout access.
export function validate(a){
 const e=[],m=a.md,t=a.txt,h=a.html,g=a.gates;
 if(g.release!=="HOLD_UNSENT"||g.adoption!=="NOT_ADOPTED"||g.founder_final_send_approval!==false)e.push("release");
 if(g.preserve_original_issue_count!==6||g.editorial_issues.join(",")!=="1,2,4,6"||g.commercial_reservations.join(",")!=="3,5")e.push("ratio");
 if(!g.wordpress_observed.newsletter_enabled||g.wordpress_observed.automatic_new_post_email!==false||g.wordpress_observed.welcome_received_verified!==false||g.wordpress_observed.recipient_eligibility_verified!==false)e.push("wp");
 if(g.wordpress_observed.counts.total!==3||g.wordpress_observed.counts.confirmed!==3||g.wordpress_observed.counts.unconfirmed!==2)e.push("counts");
 if(g.wordpress_observed.native_preview_verified||g.wordpress_observed.unsubscribe_functional_verified||g.wordpress_observed.publisher_postal_address_verified)e.push("mail false claim");
 if(Object.entries(g.merchant).filter(([k])=>k.endsWith("_verified")).some(([,v])=>v!==false))e.push("merchant false claim");
 if(g.commercial_disclosure_in_candidate!==true||g.net_revenue_per_1000_qualified_sessions!==null||g.real_qualified_sessions_verified||g.independently_settled_orders_verified)e.push("revenue");
 for(const s of [m,t,h]) {
 if(!s.includes("UNSENT")||!s.includes("NOT ADOPTED")||!s.includes("HOLD_MERCHANT"))e.push("hold labels");
 if(!s.includes("[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]")||!s.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]")||!s.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"))e.push("hard stop");
 if(!s.includes("Commercial disclosure:")||!s.includes("commission"))e.push("commercial disclosure");
 if(!s.includes("https://hypnosislive.com/mental-skills/total-focus")||!s.includes("https://hypnosislive.com/faq"))e.push("seller citations");
 if(/\b(?:guaranteed focus|clinically proven to reprogram|100% (?:results|success)|no questions asked refund|buy now|limited time)\b/i.test(s))e.push("seller promises");
 if(/https:\/\/(?:www\.)?(?:paypal|checkout|clickbank)\.[a-z]+\//i.test(s))e.push("checkout");
 }
 if(!m.includes("**PRIMARY CTA — INACTIVE:**")||!t.includes("PRIMARY CTA (INACTIVE):")||!h.includes("PRIMARY CTA — INACTIVE"))e.push("cta");
 if(/<(?:form|script|iframe|img)\b/i.test(h)||!h.includes('lang="en"')||!h.includes('role="presentation"')||!h.includes("OFFLINE SIMULATION"))e.push("html");
 if((h.match(/href=/g)||[]).length!==4)e.push("exactly 4 source links, zero CTA link");
 if(!m.includes("five sessions per year")||!t.includes("five sessions per year"))e.push("refund caveat");
 return {ok:e.length===0,errors:[...new Set(e)]};
}

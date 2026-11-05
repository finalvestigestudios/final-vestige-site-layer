"use strict";
function inspect(a){
 const errors=[],m=a.manifest||{},md=a.markdown||"",h=a.html||"",p=a.plain||"";
 const need=(ok,code)=>{if(!ok)errors.push(code)};
 need(m.status==="DRAFT_UNSENT"&&m.issue_number===3,"not_draft_issue03");
 need(m.original_canonical_manuscripts_unchanged===true&&m.campaign_mix?.editorial===4&&m.campaign_mix?.commercial_review_pending===2,"mix_or_canonical_drift");
 for(const key of ["offer_authorization","merchant_email_channel_permission","merchant_tracking_format","partner_approved_creative","final_price","actual_refund_terms"])need(m[key]==="UNVERIFIED","unverified_"+key);
 for(const key of ["guide_live","send_authorized","approved_audience","rendered_unsubscribe_verified","publisher_postal_address_verified","received_jetpack_preview_verified","recipient_eligibility_verified","delivered_fieldbook_verified","confirmed_signup_attribution_verified"])need(m[key]===false,"false_"+key);
 need(m.earning_url===null,"merchant_link_not_null");
 need(m.conversion_contract?.verified_orders===null&&m.conversion_contract?.net_revenue_usd===null&&m.conversion_contract?.qualified_human_sessions===null,"no_sale_claim");
 need(m.conversion_contract?.destination==="[[APPROVED_LIVE_FIRST_PARTY_ZEN12_BUYER_GUIDE_REQUIRED]]","guide_activated");
 need(m.subscriber_snapshot?.total===3&&m.subscriber_snapshot?.confirmed===3&&m.subscriber_snapshot?.unconfirmed===2&&m.subscriber_snapshot?.not_additive===true&&m.subscriber_snapshot?.email_eligible===null,"count_conflation");
 const sourceString=(m.source_observations||[]).map(x=>x.source).join("\n");
 need(sourceString.includes("zen12.com/hnp")&&sourceString.includes("inspire3.com/privacy/")&&sourceString.includes("nccih.nih.gov")&&sourceString.includes("ftc.gov"),"sources_missing");
 for(const [textPart,id] of [[md,"markdown"],[p,"plain"]]){
  need(textPart.includes("Twelve minutes of calm")&&textPart.includes("HOLD_"),"status_missing_"+id);
  need(textPart.includes("seller's newsletter")&&textPart.includes("separate"),"seller_list_not_clear_"+id);
  need(textPart.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]")&&textPart.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"),"footer_hold_missing_"+id);
  need(textPart.includes("[[APPROVED_LIVE_FIRST_PARTY_ZEN12_BUYER_GUIDE_REQUIRED]]"),"guide_hold_missing_"+id);
  need(!/https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com)\/.*(?:aff|ref|utm_)/i.test(textPart),"direct_earning_url_"+id);
 }
 need((md.match(/ONE PRIMARY ACTION/g)||[]).length===1&&(p.match(/PRIMARY CTA/g)||[]).length===1,"more_than_one_primary_action");
 need(md.includes("Commercial disclosure (beside")&&p.includes("Commercial disclosure:"),"disclosure_missing");
 need(md.includes("Stop if")&&md.includes("not independently"),"benefit_claim_overreach");
 need(/<html lang="en">/i.test(h)&&/name="viewport"/i.test(h),"html_mobile_language_missing");
 need(/role="presentation"/i.test(h)&&/max-width:600px/.test(h),"html_email_table_missing");
 need(!/<(?:script|form|iframe|img|video|input)\b/i.test(h),"html_unsafe_markups");
 need(!/href=["']https?:\/\/(?:www\.)?zen12\.com/i.test(h)||h.includes("Source notes"),"merchant_checkout_button");
 need(h.includes("UNSENT")&&h.includes("GUIDE NOT LIVE")&&h.includes("Seller")==false,"html_preview_not_inert");
 need(h.includes("Commercial disclosure beside the proposed CTA")&&h.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]")&&h.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"),"html_legal_hold_missing");
 need((m.source_observations||[]).some(x=>x.fact?.includes("names")),"data_sharing_not_disclosed");
 return {status:"HOLD_ALL_UNSENT",commercial_status:"HOLD_MERCHANT",passed:errors.length===0,errors};
}
module.exports={inspect};

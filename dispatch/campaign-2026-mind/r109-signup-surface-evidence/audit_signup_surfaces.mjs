/* R109: Read-only Gutenberg/REST signup-surface inspector. Not live browser or mail proof. */
function visible(raw) {
 return String(raw||"").replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi," ")
 .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi," ")
 .replace(/<!--[\s\S]*?-->/g," ").replace(/<[^>]*>/g," ")
 .replace(/&nbsp;|&#160;/gi," ").replace(/&amp;/gi,"&").replace(/\s+/g," ").trim();
}
function links(raw) { return Array.from(String(raw||"").matchAll(/\bhref\s*=\s*["']([^"']+)["']/gi),m=>m[1]); }
function firstparty(link,prefix){
 let p=String(link||"").trim();
 if(/^https:\/\//i.test(p)){
  let m=p.match(/^https:\/\/(?:www\.)?finalvestige\.com(\/[^?#]*)?(?:[?#].*)?$/i);
  return !!m && (m[1]||"/").startsWith(prefix);
 }
 return p.startsWith("/") && !p.startsWith("//") && p.split(/[?#]/)[0].startsWith(prefix);
}
function subBlocks(raw){
 const re=/<!--\s*wp:jetpack\/subscriptions\s*(\{[\s\S]*?\})?\s*\/-->/g, out=[];
 for(const m of String(raw||"").matchAll(re)){
  try{out.push(m[1]?JSON.parse(m[1]):{})}catch(e){out.push({malformed:true})}
 } return out;
}
function formHint(html){
 return /<form(?:\s|>)/i.test(html) && /<input\b[^>]*\btype\s*=\s*["']?email\b/i.test(html);
}
function fallbackHint(html){
 return /wp-block-jetpack-subscriptions/i.test(html) && !formHint(html) &&
 /<a\b[^>]*href\s*=\s*["'][^"']*(?:post_type=page|p=\d+)[^"']*["'][^>]*>[^<]{1,100}<\/a>/i.test(html);
}
export function auditSurface({route,raw,rendered}={}){
 if(!["focus","dispatch"].includes(route)||typeof raw!=="string"||typeof rendered!=="string")throw new TypeError("Expected route focus/dispatch and two HTML strings");
 if(raw.length>250000||rendered.length>250000)throw new RangeError("Oversize offline snapshot");
 let subs=subBlocks(raw), body=visible(raw), hrefs=links(raw);
 let foundCommission=/some emails may include recommendations that earn us a commission|may earn (?:a )?commission/i.test(body);
 let proof={
  schema:"fv.dispatch.signup-surface.v1",route,native_subscription_block_count:subs.length,
  native_subscription_block_unique:subs.length===1&&!subs[0]?.malformed,
  confirmation_explained:/confirm (?:your |the )?(?:email|subscription)|check your email to confirm/i.test(body)||
    subs.some(v=>/confirm your subscription|confirm your email/i.test(v.successMessage||"")),
  fieldbook_promise:/(?:52.page|52 pages|Focus Fieldbook)/i.test(body),
  commission_recommendations_disclosed:foundCommission,
  privacy_policy_link:hrefs.some(h=>firstparty(h,"/privacy-policy/")),
  direct_fieldbook_download_link:hrefs.some(h=>firstparty(h,"/wp-content/uploads/")&&
   /\/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition\.pdf(?:[?#].*)?$/i.test(h)),
  rest_has_form_hint:formHint(rendered),
  rest_has_anchor_fallback:fallbackHint(rendered),
  browser_form_usable_verified:false,subscriber_consent_proven:false,confirmed_signup_observed:false,
  fieldbook_welcome_received:false,unsubscribed_proven:false,paid_sale_observed:false,
  decision:"HOLD_UNSENT"
 };
 let f=[];
 if(!proof.native_subscription_block_unique)f.push("NATIVE_JETPACK_BLOCK_NOT_UNIQUE");
 if(!proof.confirmation_explained)f.push("CONFIRMATION_COPY_MISSING");
 if(!proof.fieldbook_promise)f.push("FIELDBOOK_PROMISE_MISSING");
 if(!proof.privacy_policy_link)f.push("PRIVACY_POLICY_LINK_MISSING");
 if(!proof.commission_recommendations_disclosed)f.push("COMMISSION_RECOMMENDATION_NOTICE_MISSING");
 if(route==="focus"&&!proof.direct_fieldbook_download_link)f.push("FOCUS_DOWNLOAD_LINK_MISSING");
 if(proof.rest_has_anchor_fallback)f.push("REST_ANCHOR_FALLBACK_NEEDS_PUBLIC_BROWSER_TEST");
 if(!proof.rest_has_form_hint)f.push("FORM_NOT_VISIBLE_IN_REST_NOT_PROOF_OF_BREAKAGE");
 return {...proof,review_flags:f.sort()};
}
export function auditPair(focus,dispatch){
 if(focus?.route!=="focus"||dispatch?.route!=="dispatch")throw new TypeError("Need Focus then Dispatch");
 let mismatches=[];
 if(focus.commission_recommendations_disclosed!==dispatch.commission_recommendations_disclosed)mismatches.push("CONSENT_WORDING_PARITY_GAP");
 if(!focus.native_subscription_block_unique||!dispatch.native_subscription_block_unique)mismatches.push("NATIVE_BLOCK_INTEGRITY_GAP");
 if(!focus.privacy_policy_link||!dispatch.privacy_policy_link)mismatches.push("PRIVACY_LINK_GAP");
 if(!focus.confirmation_explained||!dispatch.confirmation_explained)mismatches.push("OPT_IN_EXPLANATION_GAP");
 return {schema:"fv.dispatch.signup-parity.v1",list:"one_existing_jetpack_list",mismatches,
  wording_parity:mismatches.length===0,confirmed_signup_observed:false,pdf_click_is_not_lead:true,
  email_click_is_not_sale:true,real_email_browser_test:false,paid_sale_observed:false,decision:"HOLD_UNSENT"};
}

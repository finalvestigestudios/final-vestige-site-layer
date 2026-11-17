"use strict";
// Pure R431 source inspector, never WordPress email or an actual preview.
function strip(t){return t.replace(/<[^>]*>/g,"").replace(/&amp;/g,"&").replace(/&quot;/g,'"').replace(/&lt;/g,"<").replace(/&gt;/g,">").replace(/\s+/g," ").trim();}
function check(i,html,issue){
 if(i!==issue.number||i<1||i>6)throw Error("issue mismatch");
 if(typeof html!=="string"||!html.startsWith("<!-- wp:"))throw Error("invalid Gutenberg source");
 if(/<(script|iframe|form|img|style|video|object|embed|input)\b/i.test(html))throw Error("active media");
 if(!html.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]")||!html.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"))throw Error("postal/unsub hardstop");
 let p=[...html.matchAll(/<!-- wp:paragraph --><p>([\s\S]*?)<\/p><!-- \/wp:paragraph -->/g)].map(x=>strip(x[1]));
 if(p.length<4||!p[0].startsWith("EDITORIAL HOLD — DO NOT PUBLISH OR EMAIL."))throw Error("top release hold");
 if(!p.at(-1).startsWith("PRE-SEND BLOCKER"))throw Error("bottom release hold");
 const hrefs=[...html.matchAll(/href="([^"]+)"/g)].map(x=>x[1]);
 if(hrefs.some(x=>!/^https:\/\/finalvestige\.com\/[a-z0-9/._%?=&\-]+$/i.test(x)))throw Error("external or unsafe href");
 if(issue.kind==="editorial"&&!hrefs.includes(issue.editorial_cta))throw Error("editorial CTA");
 if(issue.kind!=="editorial"&&(!html.includes("[[APPROVED_")||issue.merchant_affiliate_url!==null))throw Error("commercial link activated");
 if(issue.publish_state!=="hold")throw Error("source release drift");
 return {issue:i,subject:issue.subject,planned_preheader_not_native_verified:issue.preheader,kind:issue.kind,
  real_source_first_paragraph:p[0],hypothetical_editorial_opening:p[1],hypothetical_80_char_snippet:p[1].slice(0,80),paragraphs:p.length,first_party_hrefs:hrefs,
  risk:i===4?"FACTUAL_SUBJECT_HOLD":i===1||i===2?"DUPLICATE_CTA":i===6?"REPEAT_SIGNUP_RISK":issue.kind!=="editorial"?"MERCHANT_RIGHTS_MISSING":"EDITORIAL_REVIEW",
  source_footer_hardstop:true,merchant_rights_verified:false,actual_jetpack_preview_verified:false,actual_email_receipt_verified:false,send_authorized:false,status:"HOLD_UNSENT"};
}
module.exports={strip,check};

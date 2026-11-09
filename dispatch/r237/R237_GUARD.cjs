'use strict';
/* Pure offline source guard. No networking, filesystem, import, analytics or mail. */
function check(article,html,plain,notes,master){
 const problems=[];
 const put=(p)=>{if(!problems.includes(p)) problems.push(p)};
 const subject="Apollo 1: the cause wasn't one neat spark";
 const preheader="NASA identified the dangers. The exact ignition source remained unproven.";
 for(const s of [article,html,plain,notes]) if(typeof s!=="string" || s.length<300) put("missing_required_asset");
 if(problems.length) return problems;
 if(!article.includes("**Subject:** "+subject)||!plain.includes("Subject: "+subject)||!html.includes("<h1")||!html.includes(subject)) put("subject_mismatch");
 if(!article.includes("**Preheader:** "+preheader)||!plain.includes("Preheader: "+preheader)||!html.includes(preheader)) put("preheader_mismatch");
 if(!/OPTIONAL PRIMARY-SOURCE CORRECTION/.test(article)||!/UNSENT OFFLINE REVIEW ONLY/.test(html)||!/HOLD_UNSENT/.test(plain))put("review_hold_missing");
 const nurl="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/";
 const sUrl="https://sma.nasa.gov/sma-disciplines/accllp/apollo-1";
 const cUrl="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/";
 for(const [k,asset] of [["md",article],["html",html],["text",plain]])for(const u of [nurl,sUrl,cUrl])if(!asset.includes(u))put("missing_"+k+"_source");
 if(!article.includes("approximately fifteen seconds")||!plain.includes("approximately fifteen seconds")||!html.includes("approximately fifteen seconds"))put("timing_source_caution_missing");
 if(!article.includes("no single ignition source had been conclusively identified")||!plain.includes("no single ignition source had been conclusively identified")||!html.includes("no single ignition source had been conclusively identified"))put("causality_limit_missing");
 const markers=["[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"];
 for(const [k,a] of [["md",article],["html",html],["txt",plain]])for(const m of markers)if(!a.includes(m))put("missing_"+k+"_legal_hold");
 if((plain.match(/READ THE INVESTIGATION \(one primary CTA\)/g)||[]).length!==1)put("wrong_primary_cta");
 if((html.match(/Read the Apollo 1 investigation/g)||[]).length!==1)put("wrong_html_cta");
 if(/<script\b|<iframe\b|<form\b|<img\b|tracking-pixel/i.test(html))put("unsafe_html");
 if(/href=["'](?:javascript:|data:|http:)/i.test(html))put("unsafe_link");
 if(/((buy now|guaranteed result|proven for everyone|you must purchase|limited time only))/i.test(article+" "+html+" "+plain))put("unsupported_promotion");
 if(/affiliates\.inspire3\.com\/track|utm_source=|utm_medium=/.test(html))put("tracking_link_not_permitted");
 if(!notes.includes("NOT COMPUTABLE")||!notes.includes("HOLD_MERCHANT")||!notes.includes("HOLD_DELIVERY"))put("missing_business_restrictions");
 if(!notes.includes("not a denial or proof of absence"))put("gmail_negative_proof_missing");
 if(master!==undefined){
  if(typeof master!=="string"||!(master.includes('"editorial": 4')&&master.includes('"commercial_review_pending": 2')))put("original_campaign_allocation_change");
 }
 return problems;
}
if(typeof module!=="undefined")module.exports={check};

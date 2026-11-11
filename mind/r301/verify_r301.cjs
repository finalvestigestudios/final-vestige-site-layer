"use strict";
/**
 * Mind R301 source-only, fail-closed static safety checks.
 * Run at repo root: node mind/r301/verify_r301.cjs
 * Node 18+, standard library, offline. Does not render WordPress or prove sales.
 */
const fs=require("node:fs");
const path=require("node:path");
const paths={
 article:"mind/r301/THE-SECOND-LETTER-THAT-VANISHED-UNPUBLISHED.md",
 hub:"mind/r301/MIND-ATTENTION-EVIDENCE-ROOM-UNPUBLISHED.html",
 matrix:"mind/r301/ATTENTION-SOURCE-CLAIM-OFFER-GATES.json",
 rosenhan:"mind/r299/THE-PATIENT-THE-STUDY-COULD-NOT-ACCOUNT-FOR-UNPUBLISHED.md",
 legacy_matrix:"mind/r299/CLAIMS-SOURCES-OFFERS-AND-REVENUE-GATES.json",
 A:"mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html",
 B:"mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html"
};
const fail=(code)=>{throw new Error(code)};
const assert=(condition,code)=>{if(!condition)fail(code)};
const read=()=>Object.fromEntries(Object.entries(paths).map(([key,p])=>[key,fs.readFileSync(path.resolve(process.cwd(),p),"utf8")]));
function htmlCheck(s,mode){
 assert(/<!doctype html>/i.test(s)&&/<html\s+lang="en">/i.test(s),"HTML_LANG");
 assert(/<meta\s+name="robots"\s+content="noindex,nofollow"/i.test(s),"HTML_NO_INDEX");
 assert(/<meta\s+name="viewport"/i.test(s),"HTML_VIEWPORT");
 assert(/<main\b[^>]*id="main"/i.test(s)&&/<h1\b/i.test(s),"HTML_SEMANTICS");
 assert(/href="#main"/.test(s),"HTML_SKIP");
 assert(/prefers-reduced-motion:reduce/.test(s)&&/@media\(max-width:700px\)/.test(s),"HTML_RESPONSIVE");
 assert(!/<(?:script|iframe|form|base|object|embed|img|video|source|audio)\b/i.test(s),"HTML_UNAUTHORIZED_ELEMENT");
 assert(!/\b(?:src|srcset|poster|action|formaction|data-url)\s*=/i.test(s),"HTML_REMOTE_RESOURCE");
 assert(!/<meta[^>]+http-equiv\s*=\s*["']?refresh/i.test(s),"HTML_META_REFRESH");
 assert(!/\b(onclick|onload|onerror|onmouseover)\s*=|javascript:|data:text\/html|@import|url\s*\(/i.test(s),"HTML_SCRIPT_OR_URL");
 const links=[...s.matchAll(/\bhref\s*=\s*(["'])(.*?)\1/gi)].map(a=>a[2]);
 assert(links.length>=5,"HTML_LINKS_MISSING");
 for(const link of links){
   if(link.startsWith("#")){assert(/^#[a-z][\w-]*$/i.test(link),"HTML_BAD_FRAGMENT"); continue;}
   assert(/^https:\/\//i.test(link),"HTML_BAD_SCHEME");
   const u=new URL(link);
   assert(["finalvestige.com","pubmed.ncbi.nlm.nih.gov"].includes(u.hostname),"HTML_BAD_LINK_DOMAIN");
   assert(!u.search&&!u.hash&&!u.username&&!u.password&&!u.port,"HTML_LINK_TRACKER");
 }
 for(const [_,id] of s.matchAll(/href="#([\w-]+)"/g))assert(new RegExp('\\bid="'+id+'"').test(s),"HTML_DANGLING_ANCHOR");
 const buttons=[...s.matchAll(/<button\b[^>]*>/gi)];
 assert(buttons.length===1,"HTML_BUTTON_COUNT");
 assert(/\sdisabled\b/i.test(buttons[0][0]),"HTML_BUTTON_MUST_DISABLE");
 assert(!/\b(?:href|onclick|formaction)\s*=/i.test(buttons[0][0]),"HTML_BUTTON_MERCHANT_ACTION");
 const near=s.slice(Math.max(0,buttons[0].index-950),buttons[0].index);
 assert(/Prospective affiliate disclosure/i.test(near)&&/may earn a commission/i.test(near),"HTML_DISCLOSURE_ADJACENCY");
 assert(/not playable media/i.test(s)&&!/\bplayable video is available\b/i.test(s),"HTML_VIDEO_TRUTH");
 assert(/52-page/i.test(s)&&/Final Vestige/i.test(s),"HTML_FOCUS_ROUTE");
 assert(mode==="hub","MODE");
}
function matrixCheck(s){
 const m=JSON.parse(s);
 assert(m.release==="UNPUBLISHED_HARD_HOLD"&&m.source_count===18&&m.claim_count===28,"MATRIX_COUNTS");
 assert(Array.isArray(m.sources)&&m.sources.length===18&&new Set(m.sources.map(x=>x.id)).size===18,"SOURCE_IDS");
 assert(new Set(m.sources.map(x=>x.url)).size===18,"SOURCE_URLS");
 assert(m.sources.every(x=>/^https:\/\//.test(x.url)&&x.read_depth&&x.limitation),"SOURCE_DETAILS");
 assert(m.claims.length===28&&new Set(m.claims.map(x=>x.id)).size===28,"CLAIM_IDS");
 const ids=new Set(m.sources.map(x=>x.id));
 assert(m.claims.every(x=>x.source_ids.length&&x.source_ids.every(y=>ids.has(y))),"CLAIM_SOURCE_RELATION");
 for(const id of ["AB2","AB4","AB7","AB8","AB9","ZEN2","ZEN3","HY2","BS2","BS3","AFF1","GO1","FIN1","FIN2"]){
  assert(m.claims.find(x=>x.id===id)?.decision.startsWith("OMIT"),"MATRIX_FORBIDDEN_"+id);
 }
 assert(m.holds.length===18&&new Set(m.holds.map(x=>x.id)).size===18&&m.holds.every(x=>x.status==="HARD_HOLD"&&x.verified_evidence===null),"RELEASE_HOLDS");
 const p=m.partner;
 for(const field of ["final_vestige_approved","allowed_social_channels","allowed_email","issued_earning_url","commission_rate_for_FV","tracking_terms_for_FV","claim_proof_product_specific"])assert(p[field]===null,"PARTNER_NOT_AUTHORIZED_"+field);
 assert(p.link_state==="WITHHELD","AFFILIATE_LINK_WITHHELD");
 assert(m.fallback_owned_product.verified_paid_mind_sku===null,"NO_FABRICATED_OWNED_SKU");
 for(const field of ["qualified_human_sessions","provider_confirmed_leads","affiliate_outbound_clicks","partner_confirmed_paid_orders","cleared_attributable_commission","verified_owned_net_receipts","net_revenue_per_1000"])assert(m.measurement[field]===null,"NO_FABRICATED_METRIC_"+field);
 assert(m.measurement.pii_collected===false&&m.measurement.new_scripts_added===false,"MEASUREMENT_PRIVACY");
 assert(m.creator_fit.length===3&&m.creator_fit.every(x=>x.owner==="Praxxis/Grok"),"GROK_OWNERSHIP");
 assert(m.creator_fit[2].asset_verification==="owner_reported_TASK008_not_platform_verified","GROK_UNVERIFIED");
 assert(Object.values(m.release_approvals).every(x=>x===false),"NO_RELEASE_APPROVAL");
 return m;
}
function validate(data){
 htmlCheck(data.hub,"hub");
 const m=matrixCheck(data.matrix);
 assert(data.article.split(/\s+/).length>=1700,"ARTICLE_DEPTH");
 for(const phrase of ["180–450 milliseconds","lag-1 sparing","not a diagnostic","not an attentional-blink","PubMed abstract"]){
   assert(data.article.toLowerCase().includes(phrase.toLowerCase()),"ARTICLE_SCOPE_"+phrase);
 }
 assert(data.article.includes("https://pubmed.ncbi.nlm.nih.gov/1500880/")&&data.article.includes("https://pubmed.ncbi.nlm.nih.gov/16365947/")&&data.article.includes("https://pubmed.ncbi.nlm.nih.gov/16341546/"),"ARTICLE_PRIMARY_SOURCES");
 assert(/UNPUBLISHED/i.test(data.article),"ARTICLE_UNPUBLISHED");
 assert(/Direct original-published-paper scan inspected/i.test(data.rosenhan)&&/Publisher-hosted \*Nature\* review continuation inspected/.test(data.rosenhan),"ROSENHAN_SOURCE_CORRECTIONS");
 const old=JSON.parse(data.legacy_matrix);
 assert(old.claims.find(x=>x.id==="C28").reason.toLowerCase().includes("owner"),"ROSENHAN_OWNER_REPORT");
 assert(old.sources.find(x=>x.id==="S21").read_depth==="owner_report_shared_drive_only","GROK_PROVENANCE");
 for(const mode of ["A","B"]){
   const s=data[mode];
   assert(/noindex,nofollow/i.test(s)&&!/<(?:script|form|video)\b/i.test(s),"CANONICAL_SAFE_"+mode);
   assert(/<button\b[^>]*\sdisabled\b/i.test(s),"CANONICAL_DISABLED_"+mode);
   assert(/may earn a commission/i.test(s),"CANONICAL_DISCLOSURE_"+mode);
   assert(!/href=["']https?:\/\/(?:zen12|hypnosislive|brainwaveshots|affiliates\.inspire3)/i.test(s),"CANONICAL_NO_EARNING_LINK_"+mode);
 }
 assert(data.B.includes('id="film-title"')&&!data.A.includes('id="film-title"'),"AB_VARIANT_IDENTITY");
 return {sources:m.sources.length,claims:m.claims.length,holds:m.holds.length};
}
const negative=[
 ["enable_buy","hub",s=>s.replace('type="button" disabled','type="button"'),"HTML_BUTTON_MUST_DISABLE"],
 ["remove_disclosure","hub",s=>s.replace("Prospective affiliate disclosure:","Disclosure removed:"),"HTML_DISCLOSURE_ADJACENCY"],
 ["fake_affiliate","hub",s=>s.replace('href="#review"','href="https://zen12.com/getstarted?aff=abc"'),"HTML_BAD_LINK_DOMAIN"],
 ["new_form","hub",s=>s.replace("</main>",'<form><input type="email"></form></main>'),"HTML_UNAUTHORIZED_ELEMENT"],
 ["pixel","hub",s=>s.replace("</body>",'<img src="https://tracker.invalid/p"></body>'),"HTML_UNAUTHORIZED_ELEMENT"],
 ["auto_video","hub",s=>s.replace("</body>",'<video autoplay src="x.mp4"></video></body>'),"HTML_UNAUTHORIZED_ELEMENT"],
 ["refresh","hub",s=>s.replace("</head>",'<meta http-equiv="refresh" content="1;url=https://zen12.com"></head>'),"HTML_META_REFRESH"],
 ["js_handler","hub",s=>s.replace("<main id=\"main\">",'<main id="main" onclick="go()">'),"HTML_SCRIPT_OR_URL"],
 ["erase_skip","hub",s=>s.replace('href="#main"','href="#missing"'),"HTML_SKIP"],
 ["remove_responsive","hub",s=>s.replace("prefers-reduced-motion:reduce","prefers-reduced-motion:none"),"HTML_RESPONSIVE"],
 ["fake_video","hub",s=>s.replace("not playable media","playable video is available"),"HTML_VIDEO_TRUTH"],
 ["partner_approved","matrix",s=>s.replace('"final_vestige_approved": null','"final_vestige_approved": true'),"PARTNER_NOT_AUTHORIZED_final_vestige_approved"],
 ["earning_url","matrix",s=>s.replace('"issued_earning_url": null','"issued_earning_url": "https://example.invalid/ref"'),"PARTNER_NOT_AUTHORIZED_issued_earning_url"],
 ["gate_open","matrix",s=>s.replace('"status": "HARD_HOLD"','"status": "PASS"'),"RELEASE_HOLDS"],
 ["faked_order","matrix",s=>s.replace('"partner_confirmed_paid_orders": null','"partner_confirmed_paid_orders": 1'),"NO_FABRICATED_METRIC_partner_confirmed_paid_orders"],
 ["faked_commission","matrix",s=>s.replace('"cleared_attributable_commission": null','"cleared_attributable_commission": 9'),"NO_FABRICATED_METRIC_cleared_attributable_commission"],
 ["source_swapped","matrix",s=>s.replace('https://pubmed.ncbi.nlm.nih.gov/1500880/','http://wrong.invalid/a'),"SOURCE_DETAILS"],
 ["unbacked_claim","matrix",s=>s.replace('"source_ids": [\n        "AB92"','"source_ids": [\n        "NONEXISTENT"'),"CLAIM_SOURCE_RELATION"],
 ["false_AB_promise","matrix",s=>s.replace('"decision": "OMIT"','"decision": "ALLOW"'),"MATRIX_FORBIDDEN_AB2"],
 ["asset_faked","matrix",s=>s.replace('"asset_verification": "owner_reported_TASK008_not_platform_verified"','"asset_verification": "verified_platform"'),"GROK_UNVERIFIED"],
 ["false_article","article",s=>s.replace("not a diagnostic","a diagnostic"),"ARTICLE_SCOPE_not a diagnostic"],
 ["source_removed","article",s=>s.replace("https://pubmed.ncbi.nlm.nih.gov/1500880/","https://unrelated.invalid"),"ARTICLE_PRIMARY_SOURCES"],
 ["undo_Rosenhan","rosenhan",s=>s.replace("Direct original-published-paper scan inspected","Abstract only"),"ROSENHAN_SOURCE_CORRECTIONS"],
 ["enable_A","A",s=>s.replace(' disabled aria-describedby',' aria-describedby'),"CANONICAL_DISABLED_A"],
 ["enable_B","B",s=>s.replace(' disabled aria-describedby',' aria-describedby'),"CANONICAL_DISABLED_B"]
];
function run(){
 const all=read();const baseline=validate(all);let passed=0;const failures=[];
 for(const [name,key,mut,expected] of negative){
   const revised={...all,[key]:mut(all[key])};
   if(revised[key]===all[key]){failures.push(name+":UNCHANGED");continue}
   let error=null;
   try{validate(revised)}catch(e){error=e.message}
   if(error!==expected)failures.push(name+":"+String(error)); else passed++;
 }
 if(failures.length)fail("NEGATIVE_FAILURES "+failures.join("; "));
 console.log(JSON.stringify({status:"PASS",files:Object.keys(paths).length,...baseline,negative_passed:passed,mode:"OFFLINE_SOURCE_ONLY",native_browser:"NOT_TESTED",wordpress:"NOT_TESTED",merchant:"NOT_VERIFIED"},null,2));
 return {baseline,negative_passed:passed};
}
if(require.main===module)run();
module.exports={run,validate,negative,paths};

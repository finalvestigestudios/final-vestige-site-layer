/* Final Vestige Studios / Mind R279.
 * Source-level, fail-closed regression. No live network requests, PII, checkout or analytics.
 * Node command: node mind/r279/verify_r279.cjs [repository-root]
 * Exported validate() also supports independent execution on freshly fetched GitHub text.
 */
"use strict";
function validate(f) {
  const bad=[];
  const fail=(why)=>bad.push(why);
  const a=f.article||"", h=f.hub||"", p=f.plan||"";
  let m; try {m=JSON.parse(f.matrix||"");} catch(e){return ["invalid JSON evidence matrix"];}
  const safe=(condition,why)=>{if(!condition)fail(why);};
  safe(m.schema==="fv-mind-claim-register-r279","matrix schema changed");
  safe(m.editorial_only===true && m.release_status==="HARD_HOLD","matrix release must remain held");
  safe(Array.isArray(m.sources)&&m.sources.length===20,"source inventory drift");
  safe(Array.isArray(m.claims)&&m.claims.length===34,"claim inventory drift");
  safe(Array.isArray(m.offers)&&m.offers.length===5,"offer inventory drift");
  safe(Array.isArray(m.commercial_gates)&&m.commercial_gates.length===16,"16-gate contract broken");
  const ids=new Set((m.sources||[]).map(s=>s.id));
  safe(ids.size===20,"duplicate source identifiers");
  for(const s of m.sources||[])safe(/^https:\/\//.test(s.url||"")&&!(s.url||"").includes("example.com"),"bad source URL "+s.id);
  for(const c of m.claims||[]){
    safe((c.source_ids||[]).length>0 && c.source_ids.every(x=>ids.has(x)),"unlinked claim "+c.id);
    safe(!(c.status||"").includes("approved")||c.status.includes("blocked"),"unauthorized approved science "+c.id);
  }
  const required=["named_publisher_approved","partner_terms_current","approved_earning_url","link_destination_and_redirect_chain","permitted_website_channel","permitted_email_channel","allowed_social_platforms","approved_creatives_rights","final_cart_total","tax_currency_and_checkout_terms","return_policy_and_fulfillment","product_specific_claim_substantiation","privacy_consent_attribution","publisher_earned_commission_tracking","actual_paid_transaction_and_refund_ledger","founder_qa_release_permission"];
  safe(required.every(x=>(m.commercial_gates||[]).some(g=>g.id===x && g.decision==="HARD_HOLD" && g.evidence===null)),"not every exact commercial gate hard held");
  safe((m.offers||[]).every(o=>o.earning_url===null),"unexpected earning URL");
  safe((m.offers||[]).filter(o=>o.id!=="fv_existing_focus_fieldbook").every(o=>o.verified_checkout_price===null),"unauthenticated checkout price");
  safe(m.offers.find(o=>o.id==="fv_existing_focus_fieldbook")?.status==="LIVE_FREE_RESOURCE_NOT_PAID_SALE","free Fieldbook misrepresented as paid");
  safe(m.offers.find(o=>o.id==="fv_mind_paid_candidate")?.status==="NOT_AUTHENTICATED","paid Mind SKU fabricated");
  const mt=m.measurement||{};
  safe(mt.collector==="none_new" && mt.event_schema==="proposed_only","unauthorized analytics");
  safe(mt.affiliate_click==="diagnostic_not_sale","outbound click falsely upgraded");
  safe(mt.verified_paid_order===null && mt.verified_commission===null && mt.qualified_human_sessions===null,"fabricated commercial observation");
  safe(mt.realized_net_revenue_per_1000_qualified_human_sessions==="NOT_COMPUTABLE","misrepresented net revenue KPI");
  safe(Array.isArray(m.consent_separation)&&new Set(m.consent_separation).size===4&&m.consent_separation.includes("INSPIRE3_SELLER_NEWSLETTER"),"seller consent conflated");
  safe((m.creator_to_content_map||[]).length===3,"three creator fit routes required");
  safe((m.creator_to_content_map||[]).every(x=>x.immutable_grok_asset_id===null),"fabricated immutable creator ID");
  safe(m.prior_canonical_experiment?.hosted_video===false && m.prior_canonical_experiment?.live_ab===false && m.prior_canonical_experiment?.live_wordpress===false,"fake media or live experiment");
  const source=(id,url)=>safe((m.sources||[]).some(s=>s.id===id&&s.url===url),"exact offer source mismatch: "+id);
  source("HL_TOTAL_FOCUS","https://hypnosislive.com/mental-skills/total-focus");
  source("ZEN12_STANDARD","https://zen12.com/hnp");
  source("ZEN12_PROMO","https://zen12.com/secret/");
  source("ZEN12_FREE","https://zen12.com/welcome");
  source("BWS_FOCUS","https://brainwaveshots.com/focus-shot");
  safe(/^<!doctype html>/i.test(h.trim()) && /<html lang="en">/.test(h),"HTML document language or doctype lost");
  safe(/<meta name="viewport"/.test(h) && /<meta name="description"/.test(h),"mobile and semantic metadata lost");
  safe((h.match(/<h1\b/g)||[]).length===1 && /The Mind &amp;/.test(h),"archive heading drift");
  safe(/href="#main"/.test(h)&&/id="main"/.test(h)&&/:focus-visible/.test(h),"keyboard skip/focus contract broken");
  safe(/prefers-reduced-motion:reduce/.test(h),"reduced motion support missing");
  safe(/@media\(max-width:420px\)/.test(h) && /@media\(max-width:800px\)/.test(h),"mobile breakpoints missing");
  safe(/aria-labelledby="pilot-title"/.test(h) && /aria-label="Prototype navigation"/.test(h),"accessible labelling missing");
  safe(/<button[^>]*\bdisabled\b[^>]*aria-disabled="true"[^>]*>Merchant offer unavailable/.test(h),"commercial CTA not disabled");
  const button=h.indexOf("<button");const d=h.lastIndexOf("Prospective affiliate disclosure:",button);
  safe(button>0 && d>=0 && button-d<1000 && /Final Vestige may receive a commission at no additional cost/.test(h.slice(d,button)),"FTC disclosure not adjacent to purchasing control");
  safe(/seller's newsletter/.test(h)&&/separate merchant newsletter/.test(h),"dual-consent note missing");
  safe(/42-second/.test(h)&&/NOT a playable hosted video|not hosted or playable/i.test(h),"film concept misrepresented");
  safe(/NO \/mind\/ ROUTE ACTIVATED/.test(h) && /No WordPress draft ID/.test(h),"prototype marked live");
  safe(/https:\/\/finalvestige.com\/focus\//.test(h) && /https:\/\/finalvestige.com\/free-resources\/puysegurs-animal-magnetism-files\//.test(h),"existing internal links lost");
  safe(!/<(?:script|form|iframe|object|embed|video|audio|img|link)\b/i.test(h),"resource/script/form/media injection detected");
  safe(!/\bon(?:click|load|error|submit|mouseover|focus|touchstart)\s*=/i.test(h),"inline handler injection detected");
  safe(!/url\s*\(|@import\b|<meta[^>]*http-equiv="refresh"/i.test(h),"CSS/redirect network injection detected");
  const anchors=[...h.matchAll(/<a\b[^>]*href\s*=\s*"([^"]+)"/gi)].map(x=>x[1]);
  safe(anchors.every(x=>x.startsWith("#")||x.startsWith("https://finalvestige.com/")||x.startsWith("https://www.ftc.gov/")),"merchant/external link activated in hub");
  safe(!/\b(?:affiliate_click|gtag\(|dataLayer|pixel\b|analytics\.js|beacon\b)\b/i.test(h),"extra tracking introduced");
  safe(a.split(/\s+/).length>=2400,"insufficiently substantial investigation");
  for(const term of ["Neurypnology","Puységur","333","clinical population","Total Focus","Focus Shot","Zen12","What would convincing product evidence look like","FTC","seller's newsletter"])safe(a.includes(term),"article lost evidence or caveat: "+term);
  safe(a.includes("not a clinical trial")||a.includes("not a clinical")||a.includes("not proof"),"research limitations missing");
  safe(a.includes("UNPUBLISHED") && !/I (?:used|tested|bought) Zen12/i.test(a),"false experience/publication status");
  safe(p.includes("HARD HOLD") && p.includes("NOT COMPUTABLE"),"release/metrics plan drift");
  safe(p.includes("42-second") && p.includes("NOT a playable hosted video"),"A/B prototype limitations absent");
  safe(p.includes("16 / 16 gates HARD HOLD") && p.includes("source-led"),"offer proof and experiment unpinned");
  safe(p.includes("qualified human") && p.includes("merchant-confirmed") && p.includes("refunds"),"net revenue contract missing");
  safe(!/guaranteed sales|guaranteed conversion|we tested the merchant checkout/i.test(p),"fabricated commercial outcome in plan");
  return bad;
}
function mutations(f) {
  return [
    ["no disabled button",{...f,hub:f.hub.replace('type="button" disabled','type="button"')}],
    ["no aria disabled",{...f,hub:f.hub.replace('aria-disabled="true"','aria-disabled="false"')}],
    ["no adjacent FTC",{...f,hub:f.hub.replace('Prospective affiliate disclosure:','Other note:')}],
    ["no near-link money language",{...f,hub:f.hub.replace('may receive a commission at no additional cost','may be helped')}],
    ["merchant anchor",{...f,hub:f.hub.replace('href="#read"','href="https://zen12.com/hnp"')}],
    ["script injection",{...f,hub:f.hub.replace('</body>','<script>alert(1)</script></body>')}],
    ["form injection",{...f,hub:f.hub.replace('</main>','<form action="/signup"></form></main>')}],
    ["pixel injection",{...f,hub:f.hub.replace('</main>','<img src="https://tracking.com/pixel"></main>')}],
    ["CSS network image",{...f,hub:f.hub.replace('body{margin:0','body{background-image:url(https://attacker.invalid/pixel)}body{margin:0')}],
    ["inline handler",{...f,hub:f.hub.replace('<main id="main">','<main id="main" onclick="send()">')}],
    ["iframe",{...f,hub:f.hub.replace('</main>','<iframe src="https://merchant.invalid"></iframe></main>')}],
    ["missing skip",{...f,hub:f.hub.replace('href="#main"','href="#wrong"')}],
    ["missing focus",{...f,hub:f.hub.replace(':focus-visible{outline',':hover{outline')}],
    ["missing mobile",{...f,hub:f.hub.replace('@media(max-width:420px)','@media(min-width:420px)')}],
    ["missing reduced motion",{...f,hub:f.hub.replace('prefers-reduced-motion:reduce','prefers-reduced-motion:no-preference')}],
    ["false hosted film",{...f,hub:f.hub.replace('not hosted or playable','now hosted and playable')}],
    ["new list conflation",{...f,hub:f.hub.replace("separate merchant newsletter","same newsletter")}],
    ["missing Focus",{...f,hub:f.hub.replaceAll('https://finalvestige.com/focus/','https://wrong.invalid/free')}],
    ["fake CMS",{...f,hub:f.hub.replace('NO /mind/ ROUTE ACTIVATED','NOW LIVE')}],
    ["claim count",{...f,matrix:f.matrix.replace('"C34"','"C33"')}],
    ["one gate cleared",{...f,matrix:f.matrix.replace('"decision": "HARD_HOLD"','"decision": "APPROVED"')}],
    ["evidence fabricated",{...f,matrix:f.matrix.replace('"evidence": null','"evidence": "approved"')}],
    ["sale fabricated",{...f,matrix:f.matrix.replace('"verified_paid_order": null','"verified_paid_order": 2')}],
    ["payout fabricated",{...f,matrix:f.matrix.replace('"verified_commission": null','"verified_commission": 250')}],
    ["metric fabricated",{...f,matrix:f.matrix.replace('"NOT_COMPUTABLE"','"123.45"')}],
    ["earning URL fabricated",{...f,matrix:f.matrix.replace('"earning_url": null','"earning_url": "https://partner.invalid/offer"')}],
    ["priced cart fabricated",{...f,matrix:f.matrix.replace('"verified_checkout_price": null','"verified_checkout_price": 10')}],
    ["creator ID fabricated",{...f,matrix:f.matrix.replace('"immutable_grok_asset_id": null','"immutable_grok_asset_id": "GUESS1"')}],
    ["product science approval",{...f,matrix:f.matrix.replace('"status": "blocked_unsupported_efficacy"','"status": "approved_scientific"')}],
    ["exact seller drift",{...f,matrix:f.matrix.replace('https://zen12.com/hnp','https://zen12.com/something-else')}],
    ["wrong consent",{...f,matrix:f.matrix.replace('INSPIRE3_SELLER_NEWSLETTER','FV_JETPACK_FOCUS')}],
    ["paid fieldbook",{...f,matrix:f.matrix.replace('LIVE_FREE_RESOURCE_NOT_PAID_SALE','PAID_ORDER_VERIFIED')}],
    ["paid sku fraud",{...f,matrix:f.matrix.replace('"status": "NOT_AUTHENTICATED"','"status": "VERIFIED"}')],
    ["tracking collector",{...f,matrix:f.matrix.replace('"collector": "none_new"','"collector": "custom_pixel"')}],
    ["false live video",{...f,matrix:f.matrix.replace('"hosted_video": false','"hosted_video": true')}],
    ["false experiment",{...f,matrix:f.matrix.replace('"live_ab": false','"live_ab": true')}],
    ["no film caution in plan",{...f,plan:f.plan.replace("NOT a playable hosted video","A live video")}],
    ["no hard hold plan",{...f,plan:f.plan.replaceAll("HARD HOLD","ACTIVATED")}],
    ["article too short",{...f,article:"# Short\n"}],
    ["article no research sample",{...f,article:f.article.replaceAll("333","several")}],
    ["missing source",{...f,matrix:f.matrix.replace('"id": "FTC_HEALTH"','"id": "FTC_UNVERIFIED"')}],
  ];
}
if(typeof module!=="undefined"){module.exports={validate,mutations};}
if(typeof require!=="undefined" && typeof module!=="undefined" && require.main===module){
  const fs=require("node:fs"),path=require("node:path"),root=process.argv[2]||".";
  const dir=path.join(root,"mind","r279");
  const read=x=>fs.readFileSync(path.join(dir,x),"utf8");
  const f={article:read("THE-VOICE-THAT-PROMISED-FOCUS-UNPUBLISHED.md"),hub:read("MIND-READING-ROOM-UNPUBLISHED-PREVIEW.html"),matrix:read("HYPNOSIS-PRODUCT-SOURCE-COMMERCIAL-GATES.json"),plan:read("ONE-OFFER-CREATOR-TO-SETTLED-REVENUE-ACCEPTANCE.md")};
  const errs=validate(f);if(errs.length){console.error("BASELINE FAIL:",errs);process.exit(1);}
  const cases=mutations(f);let hit=0;for(const [name,m] of cases){const e=validate(m);if(!e.length){console.error("MISSED UNSAFE MUTATION",name);process.exit(2);}hit++;}
  console.log("R279 baseline PASS, "+hit+"/"+cases.length+" unsafe mutations rejected; SOURCE-LEVEL ONLY, NOT BROWSER/CMS/MERCHANT TEST");
}

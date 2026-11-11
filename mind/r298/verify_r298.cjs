"use strict";
/**
 * FV Mind R298 fail-closed research/commercial source gate.
 * Run at repository root: node mind/r298/verify_r298.cjs
 * Uses Node standard library only; no network or live actions.
 * Protects exact reviewed strings with FNV64 fingerprints (not cryptographic
 * signatures). GitHub blob SHA-1 separately validates repository custody.
 * Source-scanning does NOT replace parsing/rendered-browser, WordPress,
 * merchant or legal acceptance.
 */
const fs=require("node:fs");
const path=require("node:path");
const paths={
 A:"mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html",
 B:"mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html",
 previousGuide:"mind/r297/BEFORE-YOU-BUY-MEDITATION-AUDIO-INDEPENDENT-GUIDE-UNPUBLISHED.md",
 previousDossier:"mind/r297/CANONICAL-ZEN12-AB-COMMERCE-AND-GROK-ACCEPTANCE.md",
 previousMatrix:"mind/r297/MEDITATION-AUDIO-CLAIMS-SOURCES-AND-REVENUE-HOLDS.json",
 guide:"mind/r298/THE-MEDITATION-STUDY-THAT-DID-NOT-TEST-YOUR-RECORDING-UNPUBLISHED.md",
 hub:"mind/r298/MIND-RESEARCH-DELIVERY-HUB-UNPUBLISHED.html",
 matrix:"mind/r298/DIGITAL-MEDITATION-SOURCE-CLAIM-COMMERCE-GATES.json",
 dossier:"mind/r298/ONE-OFFER-DELIVERY-MODE-CONVERSION-RELEASE-ACCEPTANCE.md"
};
const exact={
 A:"e0bbb529cff3f5e4",B:"4b1b9fe38a5a89a1",
 previousGuide:"3b20ab3003387795",previousDossier:"16a3fab98a900d5a",previousMatrix:"0e747395257a6ef8",
 guide:"d5a9514f4c643293",hub:"adb57aca6ddf67a1",matrix:"ab8ed0c1e3193c96",dossier:"d0dff9c2d3118d31"
};
const refuse=(code)=>{throw new Error(code)};
const needs=(value,code)=>{if(!value)refuse(code)};
function fnv64(s){let h=0xcbf29ce484222325n;for(let i=0;i<s.length;i++){h^=BigInt(s.charCodeAt(i));h=(h*0x100000001b3n)&0xffffffffffffffffn;}return h.toString(16).padStart(16,"0")}
const allowedHosts=new Set(["finalvestige.com","www.ftc.gov","pubmed.ncbi.nlm.nih.gov","pmc.ncbi.nlm.nih.gov","doi.org","research.monash.edu","www.nccih.nih.gov","journals.plos.org"]);
function checkHtml(html,strict=false){
 needs(/<html\b[^>]*lang=["']en["']/i.test(html),"HTML_LANG");
 needs(/<meta\s+name=["']viewport["']/i.test(html),"HTML_VIEWPORT");
 needs(/<meta\s+name=["']robots["'][^>]*noindex/i.test(html),"HTML_UNPUBLISHED");
 needs(/<main\b/i.test(html)&&/<h1\b/i.test(html),"HTML_SEMANTICS");
 needs(!/<(?:script|iframe|form|base|link|img|picture|video|audio|source|object|embed|svg|math|template)\b/i.test(html),"HTML_UNSAFE_TAG");
 needs(!/<meta\b[^>]*http-equiv\s*=\s*["']?refresh/i.test(html),"HTML_META_REFRESH");
 needs(!/\b(?:src|srcset|poster|action|formaction|data-url|data-href|data-target)\s*=/i.test(html),"HTML_RESOURCE_OR_DESTINATION");
 needs(!/\bhref\s*=\s*[^"'\s>]/i.test(html),"HTML_UNQUOTED_HREF");
 needs(!/\b(?:on[a-z]+)\s*=|\bhidden(?:\s|=|>)|\binert(?:\s|=|>)|\baria-hidden\s*=\s*["']?true/i.test(html),"HTML_HIDDEN_OR_EVENT");
 needs(!/@import\b|url\s*\(|expression\s*\(|visibility\s*:\s*hidden|display\s*:\s*none|opacity\s*:\s*0(?:[;}"'\s])/i.test(html),"HTML_CSS_REMOTE_OR_HIDDEN");
 needs(!/\\u0*02f|\\u0*03a|&(?:#x?[0-9a-f]+|colon|sol);/i.test(html),"HTML_OBFUSCATED_URL");
 const links=[...html.matchAll(/\bhref\s*=\s*(["'])(.*?)\1/gi)].map(m=>m[2]);
 needs(links.length>1,"HTML_LINKS_MISSING");
 for(const link of links){
  if(link.startsWith("#")){needs(/^#[a-z][\w-]*$/i.test(link),"HTML_BAD_FRAGMENT");continue;}
  needs(/^https:\/\//i.test(link)&&!link.startsWith("https:////"),"HTML_HTTPS_ONLY");
  const u=new URL(link);
  needs(u.protocol==="https:"&&allowedHosts.has(u.hostname),"HTML_FORBIDDEN_LINK_HOST");
  needs(!u.username&&!u.password&&!u.port&&!u.search&&!u.hash,"HTML_LINK_QUERY_OR_FRAGMENT");
 }
 const buttons=[...html.matchAll(/<button\b[^>]*>/gi)];
 needs(buttons.length===1,"HTML_PURCHASE_BUTTON_COUNT");
 needs(/\sdisabled(?:\s|=|>)/i.test(buttons[0][0]),"HTML_BUTTON_NOT_DISABLED");
 needs(!/\b(?:href|onclick|formaction|data-url)\s*=/i.test(buttons[0][0]),"HTML_BUTTON_HAS_DESTINATION");
 const previous=html.slice(Math.max(0,buttons[0].index-750),buttons[0].index);
 needs(previous.includes("may earn a commission"),"HTML_AFFILIATE_DISCLOSURE_ADJACENCY");
 needs(/<p\b[^>]*class=["']disclosure["'][^>]*>[^]*may earn a commission/i.test(previous),"HTML_DISCLOSURE_ROLE");
 if(strict){
  needs(/<a\s+class=["']skip["']\s+href=["']#main["']/i.test(html),"HTML_SKIP_LINK");
  needs(/prefers-reduced-motion/i.test(html)&&/max-width:790px/i.test(html),"HTML_RESPONSIVE_REDUCED_MOTION");
  needs(/<details><summary>Read the original short-film transcript/i.test(html),"HTML_TRANSCRIPT_ACCESS");
  needs(!/<input\b/i.test(html),"HTML_DUPLICATE_SIGNUP");
  needs(/NOT a WordPress CMS draft/i.test(html)||/Not a WordPress CMS draft/i.test(html),"HTML_NOT_CMS");
 }
}
function validate(d,options={}){
 for(const [k,p] of Object.entries(paths)){
  needs(typeof d[k]==="string"&&d[k].length>400,"MISSING_FILE_"+k);
  if(options.pin!==false)needs(fnv64(d[k])===exact[k],"PIN_"+k);
 }
 const m=JSON.parse(d.matrix);
 needs(m.status==="UNPUBLISHED_HARD_HOLD","RELEASE_HOLD");
 needs(m.sources.length===20&&new Set(m.sources.map(s=>s.url)).size===20,"SOURCES_20_DISTINCT");
 needs(m.claims.length===28&&m.offers.length===5&&m.creator_fit.length===3&&m.gates.length===18,"STRUCTURE_COUNTS");
 const ids=new Set(m.sources.map(s=>s.id));
 needs(ids.size===20&&m.sources.every(s=>s.url.startsWith("https://")&&s.retrieval_depth),"SOURCE_ID_URL");
 needs(new Set(m.claims.map(c=>c.id)).size===28,"CLAIMS_DISTINCT");
 for(const c of m.claims)needs(Array.isArray(c.source_ids)&&c.source_ids.length>0&&c.source_ids.every(x=>ids.has(x))&&c.decision,"CLAIM_SOURCE_"+c.id);
 const byId=Object.fromEntries(m.claims.map(c=>[c.id,c]));
 needs(byId.C08.decision==="DELIVERY_MODERATOR_REQUIRED"&&byId.C08.statement.includes("face-to-face"),"FACE_TO_FACE_CAVEAT");
 needs(byId.C09.decision==="OUTLIER_QUALIFIER_REQUIRED"&&byId.C09.statement.includes("AFTER outlier"),"OUTLIER_CAVEAT");
 needs(byId.C10.statement.includes("attention-shifting"),"ATTENTION_SHIFT_SCOPE");
 needs(byId.C21.statement.includes("one refund in six months"),"RETURN_LIMITS");
 needs(m.sources.find(s=>s.id==="S20").type==="brand_policy_not_regulator","SITE_POLICY_NOT_FTC");
 needs(m.sources.find(s=>s.id==="S15").retrieval_depth==="web_fetch_error","SOURCE_FETCH_STATUS");
 for(const g of m.gates)needs(g.status==="HARD_HOLD"&&g.evidence===null,"COMMERCIAL_GATE_"+g.name);
 needs(new Set(m.gates.map(g=>g.name)).size===18,"COMMERCIAL_GATE_ID");
 needs(m.offers[0].name==="Zen12"&&m.offers[0].earning_url===null&&m.offers[0].merchant_authorization===false,"AFFILIATE_UNAUTHORIZED");
 needs(m.offers[4].sku===null&&m.offers[4].rights_approval===null,"OWNED_SKU_UNVERIFIED");
 for(const c of m.creator_fit)needs(c.grok_asset_id===null&&c.post_url===null&&c.rights===null&&c.clickable_native_mobile_path===null,"CREATOR_UNVERIFIED_"+c.topic);
 needs(m.creator_fit[2].topic==="mindfulness_audio_buyer"&&!m.creator_fit[2].verified_existing_article,"CREATOR_THIRD_IS_UNPUBLISHED");
 needs(m.experiment.current_B_media==="STATIC_STORYBOARD_NOT_PLAYABLE"&&m.experiment.status==="NOT_STARTED","FALSE_FILM_AB");
 needs(m.experiment.canonical_A===paths.A&&m.experiment.canonical_B===paths.B,"CANONICAL_AB_IDENTITY");
 const mm=m.measurement;
 for(const k of ["qualified_human_sessions_7d","qualified_human_sessions_30d","affiliate_outbound_clicks","confirmed_jetpack_leads","merchant_confirmed_paid_orders","settled_commission","refunds","fees","net_realized_revenue","net_revenue_per_1000_qualified_human_sessions"])needs(mm[k]===null,"METRIC_NOT_NULL_"+k);
 needs(mm.pii_collected===false&&mm.added_tracking_scripts===false&&mm.affiliate_click_is_sale===false,"METRIC_PRIVACY_OR_SALE");
 needs(mm.creator_asset_id==="UNVERIFIED"&&mm.campaign_id==="HARD_HOLD_UNCHOSEN","CAMPAIGN_UNVERIFIED");
 for(const k of ["A","B","hub"])checkHtml(d[k],k==="hub");
 const wc=d.guide.trim().split(/\s+/).length;
 needs(wc>=2200,"ARTICLE_NOT_SUBSTANTIVE");
 for(const phrase of ["111 randomized controlled trials","9,538","18 eligible studies","29 studies","19 digital-training studies","45 randomized trials","face-to-face","self-guided","outliers","Puységur","There is no active purchasing recommendation"]){
  needs(d.guide.toLowerCase().includes(phrase.toLowerCase()),"GUIDE_EVIDENCE_"+phrase);
 }
 for(const s of m.sources){needs(d.guide.includes(s.url)||(["S11","S16","S17","S18","S20"].includes(s.id)),"SOURCE_URL_MISSING_IN_GUIDE_"+s.id);}
 needs(d.dossier.includes("NOT COMPUTABLE")&&d.dossier.includes("mind_pilot_2026_11")&&d.dossier.includes("mind_proposed_2026_11"),"DOSSIER_ATTRIBUTION_AND_REVENUE");
 needs(d.dossier.includes("face-to-face")&&d.dossier.includes("outliers")&&d.dossier.includes("No verified"),"DOSSIER_EVIDENCE_LIMITS");
 needs(d.dossier.includes("NOT PLAYABLE")&&d.dossier.includes("NO VERIFIED MATCH"),"DOSSIER_MEDIA_HOLD");
 return {pass:true,files:Object.keys(paths).length,sources:m.sources.length,claims:m.claims.length,gates:m.gates.length,negative_cases:negative.length,guide_words:wc};
}
const negative=[
 ["remove_disclosure","hub",s=>s.replace(/may earn a commission/g,"could get paid"),"HTML_AFFILIATE_DISCLOSURE_ADJACENCY"],
 ["activate_button","hub",s=>s.replace('type="button" disabled','type="button"'),"HTML_BUTTON_NOT_DISABLED"],
 ["fake_video","matrix",s=>s.replace("STATIC_STORYBOARD_NOT_PLAYABLE","PLAYABLE_LIVE"),"FALSE_FILM_AB"],
 ["fictional_revenue","matrix",s=>s.replace('"merchant_confirmed_paid_orders": null','"merchant_confirmed_paid_orders": 12'),"METRIC_NOT_NULL"],
 ["fake_account","matrix",s=>s.replace('"merchant_authorization": false','"merchant_authorization": true'),"AFFILIATE_UNAUTHORIZED"],
 ["real_earning_link","matrix",s=>s.replace('"earning_url": null','"earning_url": "https://merchant.invalid/abc"'),"AFFILIATE_UNAUTHORIZED"],
 ["wrong_face_to_face","matrix",s=>s.replace("DELIVERY_MODERATOR_REQUIRED","CLAIM_PROVEN"),"FACE_TO_FACE_CAVEAT"],
 ["wrong_outliers","matrix",s=>s.replace("AFTER outlier","without outlier"),"OUTLIER_CAVEAT"],
 ["bad_refund","matrix",s=>s.replace("one refund in six months","unlimited refunds"),"RETURN_LIMITS"],
 ["fake_creator","matrix",s=>s.replace('"grok_asset_id": null','"grok_asset_id": "imaginary"'),"CREATOR_UNVERIFIED"],
 ["duplicated_sources","matrix",s=>s.replace('"id": "S20"','"id": "S19"'),"SOURCE_ID_URL"],
 ["site_policy_as_ftc","matrix",s=>s.replace("brand_policy_not_regulator","regulator"),"SITE_POLICY_NOT_FTC"],
 ["source_lookup_missing","matrix",s=>s.replace('"S03"','"S999"'),"CLAIM_SOURCE_"],
 ["fake_owner_sku","matrix",s=>s.replace('"sku": null','"sku": "FV-MIND-001"'),"OWNED_SKU_UNVERIFIED"],
 ["privacy_violation","matrix",s=>s.replace('"pii_collected": false','"pii_collected": true'),"METRIC_PRIVACY_OR_SALE"],
 ["script","hub",s=>s.replace("</body>","<script>alert(1)</script></body>"),"HTML_UNSAFE_TAG"],
 ["iframe","hub",s=>s.replace("</body>","<iframe src=\"https://evil.invalid\"></iframe></body>"),"HTML_UNSAFE_TAG"],
 ["tracking_pixel","hub",s=>s.replace("</body>","<img src=\"//evil.invalid/pixel\"></body>"),"HTML_UNSAFE_TAG"],
 ["hidden_disclosure","hub",s=>s.replace('class="disclosure"','class="disclosure" hidden'),"HTML_HIDDEN_OR_EVENT"],
 ["style_hidden","hub",s=>s.replace('class="disclosure"','class="disclosure" style="display:none"'),"HTML_CSS_REMOTE_OR_HIDDEN"],
 ["css_import","hub",s=>s.replace("</style>","@import url(https://evil.invalid/x.css);</style>"),"HTML_CSS_REMOTE_OR_HIDDEN"],
 ["url_href","hub",s=>s.replace('href="https://finalvestige.com/focus/"','href="//evil.invalid"'),"HTML_HTTPS_ONLY"],
 ["unquoted_href","hub",s=>s.replace('href="https://finalvestige.com/focus/"','href=https://evil.invalid'),"HTML_UNQUOTED_HREF"],
 ["query_affiliate","hub",s=>s.replace('href="https://finalvestige.com/focus/"','href="https://finalvestige.com/focus/?affid=123"'),"HTML_LINK_QUERY_OR_FRAGMENT"],
 ["meta_refresh","hub",s=>s.replace("</head>","<meta http-equiv=\"refresh\" content=\"0;url=https://evil.invalid\"></head>"),"HTML_META_REFRESH"],
 ["button_data_url","hub",s=>s.replace('type="button" disabled','type="button" data-url="https://evil.invalid" disabled'),"HTML_RESOURCE_OR_DESTINATION"],
 ["external_image_unquoted","hub",s=>s.replace("</body>","<img src=//evil.invalid/p.png></body>"),"HTML_UNSAFE_TAG"],
 ["new_form","hub",s=>s.replace("</body>","<form><input type=\"email\"></form></body>"),"HTML_UNSAFE_TAG"],
 ["unexpected_body_change","guide",s=>s.replace("The current Zen12 checkout can be reviewed at the first rung","The current Zen12 checkout is clinically proven at the first rung"),"PIN_guide"],
 ["inherited_A_changed","A",s=>s.replace("Zen12 purchase link unavailable","Buy Zen12 now"),"PIN_A"],
 ["source_hub_changed","hub",s=>s.replace("The Mind &amp; Perception Archive","The Mind &amp; Sales Archive"),"PIN_hub"]
];
const read=()=>Object.fromEntries(Object.entries(paths).map(([key,p])=>[key,fs.readFileSync(path.join(process.cwd(),p),"utf8")]));
function run(){const d=read(),summary=validate(d);let passed=0;
for(const [name,key,modify,expected] of negative){const copy={...d,[key]:modify(d[key])};needs(copy[key]!==d[key],"TEST_MUTATION_NOT_APPLIED_"+name);
let thrown=null;try{validate(copy,{pin:expected.startsWith("PIN_")})}catch(e){thrown=String(e.message||e)}
needs(thrown!==null,"TEST_UNSAFE_ACCEPTED_"+name);
needs(thrown.includes(expected),"TEST_WRONG_REASON_"+name+"_GOT_"+thrown+"_EXPECTED_"+expected);passed++;}
return {...summary,negative_test_passes:passed,negative_test_total:negative.length,scope:"source-only, Node standard library; NOT browser/CI/WP/merchant/payment"};}
if(require.main===module){try{console.log(JSON.stringify(run(),null,2));}catch(error){console.error("R298 HARD HOLD TEST FAILURE: "+error.message);process.exitCode=1;}}
module.exports={validate,run,paths,exact,negative,fnv64};
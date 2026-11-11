"use strict";
/**
 * R297 cumulative research/commerce security tests; run from repository root:
 *   node mind/r297/verify_r297.cjs
 * Standard-library only. Baseline checks nine real files plus this dossier.
 * Negative tests check changed inputs and EXPECTED failure reasons.
 * Does not prove WCAG in a browser, real merchant acceptance, WordPress sanitization,
 * actual sales, affiliate attribution, paid settlement or video playback.
 */
const fs = require("node:fs");
const P = "mind/r297/";
const paths = {
 parentArticle:"mind/r296/THE-SOUND-THAT-PROMISED-TO-HOLD-YOUR-ATTENTION-UNPUBLISHED.md",
 parentHub:"mind/r296/MIND-ARCHIVE-AUDIO-EVIDENCE-WP-CANDIDATE-UNPUBLISHED.html",
 parentMatrix:"mind/r296/ISOCHRONIC-PRODUCT-CLAIM-SOURCE-AND-COMMERCE-GATES.json",
 parentDossier:"mind/r296/ONE-OFFER-ISOCHRONIC-RESEARCH-AND-REVENUE-ACCEPTANCE.md",
 guideA:"mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html",
 guideB:"mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html",
 article:P+"BEFORE-YOU-BUY-MEDITATION-AUDIO-INDEPENDENT-GUIDE-UNPUBLISHED.md",
 hub:P+"MIND-EVIDENCE-ARCHIVE-WP-HTML-UNPUBLISHED.html",
 matrix:P+"MEDITATION-AUDIO-CLAIMS-SOURCES-AND-REVENUE-HOLDS.json",
 dossier:P+"CANONICAL-ZEN12-AB-COMMERCE-AND-GROK-ACCEPTANCE.md"
};
function fail(why){throw new Error(why)}
function ok(v,why){if(!v)fail(why)}
function hash(s){let h=0xcbf29ce484222325n;for(let i=0;i<s.length;i++){h^=BigInt(s.charCodeAt(i));h=(h*0x100000001b3n)&0xffffffffffffffffn}return h.toString(16).padStart(16,"0")}
const frozen={
 parentArticle:"b2adedb103842ed0",parentHub:"5a075bcb30165502",
 parentMatrix:"47dfb5e7d3b08f89",parentDossier:"930fe2995646ac5d",
 guideA:"e0bbb529cff3f5e4",guideB:"4b1b9fe38a5a89a1"
};
const digests={
 sources:"cb994535dd3e8231",claims:"bd58461ca38eecea",gates:"7db7cd8a950d244d",
 creator_topic_fit:"1e92d5682e0185ee",offers:"a916d00c5d7b0fa2"
};
const allowedHosts=new Set(["finalvestige.com","pubmed.ncbi.nlm.nih.gov","pmc.ncbi.nlm.nih.gov","www.ftc.gov","doi.org","research.monash.edu","www.nccih.nih.gov","journals.plos.org"]);
function validateHtml(page,tag){
 ok(/<html\b[^>]*\blang=["']en["']/i.test(page),"LANG_"+tag);
 ok(/<meta\b[^>]*\bname=["']viewport["']/i.test(page),"VIEWPORT_"+tag);
 ok(/<meta\b[^>]*\bname=["']robots["'][^>]*\bnoindex\b/i.test(page),"NOINDEX_"+tag);
 ok(!/<(?:script|iframe|form|base|link|object|embed|video|audio)\b/i.test(page),"UNSAFE_TAG_"+tag);
 ok(!/<meta\b[^>]*\bhttp-equiv\s*=\s*["']?refresh/i.test(page),"META_REFRESH_"+tag);
 ok(!/<img\b[^>]*\bsrc\s*=\s*["']https?:/i.test(page),"REMOTE_IMG_"+tag);
 ok(!/\b(?:srcset|data-href|data-url|data-target|formaction)\s*=/i.test(page),"HIDDEN_DESTINATION_"+tag);
 ok(!/\bon[a-z]+\s*=/i.test(page),"INLINE_EVENT_"+tag);
 ok(!/@import\b|url\s*\(|expression\s*\(/i.test(page),"EXTERNAL_CSS_"+tag);
 ok(!/\.(?:disclosure)\s*\{[^}]*\b(?:display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0)/i.test(page),"HIDDEN_DISCLOSURE_"+tag);
 const buttons=[...page.matchAll(/<button\b[^>]*>/gi)].map(x=>({tag:x[0],start:x.index}));
 ok(buttons.length===1,"BUTTON_COUNT_"+tag);
 ok(/\sdisabled(?:\s|=|>)/i.test(buttons[0].tag),"DISABLED_PURCHASE_"+tag);
 ok(!/\s(?:href|onclick|formaction)\s*=/i.test(buttons[0].tag),"BUTTON_DESTINATION_"+tag);
 const preceding=page.slice(Math.max(0,buttons[0].start-900),buttons[0].start);
 ok(/may earn a commission/i.test(preceding),"NEAR_LINK_DISCLOSURE_"+tag);
 ok(!/<(?:section|article)\b/i.test(preceding.slice(preceding.toLowerCase().lastIndexOf("may earn a commission"))),"DISCLOSURE_DIFFERENT_SECTION_"+tag);
 // There must not be any case-encoded or parameterized target destination.
 const links=[...page.matchAll(/\bhref\s*=\s*["']([^"']+)["']/gi)].map(x=>x[1]);
 ok(links.length>=2,"HREF_INVENTORY_"+tag);
 for(const link of links){
  ok(!/&(?:#x?[0-9a-f]+|colon|sol|amp);/i.test(link),"ENCODED_HREF_"+tag);
  ok(!/^(?:javascript|data|vbscript|file|blob):/i.test(link),"DANGEROUS_SCHEME_"+tag);
  if(link.startsWith("#")){ok(/^#[a-z][\w-]*$/i.test(link),"BAD_FRAGMENT_"+tag);continue;}
  ok(/^https:\/\//i.test(link),"HTTPS_ONLY_"+tag);
  const u=new URL(link);
  ok(u.protocol==="https:"&&allowedHosts.has(u.hostname),"HREF_HOST_"+tag);
  ok(!u.username&&!u.password&&!u.search&&u.port==="","HREF_QUERY_USERINFO_"+tag);
 }
 // Raw unquoted href tokens, javascript escapes and special redirects must not sneak through.
 ok(!/\bhref\s*=\s*[^"'\s>]/i.test(page),"UNQUOTED_HREF_"+tag);
 ok(!/https?\\u00(?:2f|3a)|&#(?:x0*3a|0*58);/i.test(page),"OBFUSCATED_LINK_"+tag);
}
function verify(x){
 for(const [k,p] of Object.entries(paths))ok(typeof x[k]==="string"&&x[k].length>350,"MISSING_FULL_FILE_"+k+"_"+p);
 let m;try{m=JSON.parse(x.matrix)}catch(e){fail("MATRIX_BAD_JSON")}
 ok(m.status==="DRAFT_HARD_HOLD"&&m.draft_only===true&&m.release==="UNPUBLISHED_NO_AFFILIATE_ACTIVATION","RELEASE_HARD_HOLD");
 ok(m.sources.length===25&&new Set(m.sources.map(s=>s.url)).size===23,"SOURCE_COUNT_OR_UNIQUES");
 ok(m.claims.length===42&&m.gate_count===18&&m.gates.length===18,"CLAIM_OR_GATE_COUNT");
 ok(m.offers.length===5,"OFFER_COUNT");
 ok(m.creator_topic_fit.length===3,"CREATOR_COUNT");
 const idSet=new Set(m.sources.map(s=>s.id));
 ok(idSet.size===m.sources.length,"SOURCE_ID_DUPLICATE");
 for(const c of m.claims)ok(c.source_ids.length>0&&c.source_ids.every(id=>idSet.has(id)),"CLAIM_UNSOURCED_"+c.id);
 ok(m.sources.find(s=>s.id==="S18").type==="brand_policy_not_regulator","SOURCE_BRAND_POLICY");
 ok(m.claims.find(c=>c.id==="C07").statement.includes("less than half")&&m.claims.find(c=>c.id==="C07").statement.includes("one refund per six months"),"REFUND_RESTRICTION_MISSING");
 ok(m.claims.find(c=>c.id==="C20").statement.includes("ONE 33-minute 47MB MP3"),"HYPNOSIS_FORMAT_ERROR");
 for(const [k,h] of Object.entries(digests))ok(hash(JSON.stringify(m[k]))===h,"RELATIONSHIP_DIGEST_"+k);
 ok(m.gates.every(g=>g.status==="HARD_HOLD"&&g.evidence===null),"GATE_NOT_HOLD");
 ok(m.offers.every(o=>o.earning_url===null||o.earning_url===undefined),"EARNING_URL_ACTIVATED");
 ok(m.offers.find(o=>o.name==="FV paid Mind owned SKU").paid_fv_product_authenticated===false,"OWNED_PAID_NOT_VERIFIED");
 ok(m.offer_hypothesis.account_approval_verified===false&&m.offer_hypothesis.authorized_earning_url===null,"ACCOUNT_NOT_APPROVED");
 ok(m.offer_hypothesis.fallback_owned_paid_sku_verified===false,"OWNED_FALLBACK_NOT_VERIFIED");
 ok(m.ab_hypothesis.B_media_actual==="static_storyboard_not_playable"&&m.ab_hypothesis.test_status==="NOT_STARTED","B_STATIC_OR_AB_STATUS");
 for(const row of m.creator_topic_fit)ok(row.grok_asset_id===null&&row.asset_url===null&&row.rights===null,"CREATOR_UNVERIFIED_"+row.topic);
 ok(m.first_party_event_contract.creator_asset_id.includes("UNKNOWN")&&m.first_party_event_contract.campaign_id.includes("HARD_HOLD"),"CAMPAIGN_HOLD");
 const measurements=["qualified_sessions_7d","qualified_sessions_30d","relevant_cta_clicks","confirmed_jetpack_leads","merchant_confirmed_orders","commission_settled","refunds","fees","net_realized_revenue","revenue_per_1000_qualified_humans"];
 for(const k of measurements)ok(Object.hasOwn(m.measurement,k)&&m.measurement[k]===null,"METRIC_NULL_"+k);
 ok(m.measurement.first_party_only===true&&m.measurement.pii===false&&m.measurement.new_scripts===false,"PRIVACY_CONTRACT");
 ok(m.measurement.affiliate_click_vs_sale.startsWith("STRICTLY_SEPARATE"),"CLICK_NOT_SALE");
 for(const tag of ["guideA","guideB","parentHub","hub"])validateHtml(x[tag],tag);
 ok(x.article.trim().split(/\s+/).length>=2200,"ARTICLE_NOT_SUBSTANTIVE");
 for(const s of ["111 randomized","9,538","18 studies","29 studies","Zen12","Hypnosis Live","Brainwave Shots","Puységur","S1","S14","no active affiliate"]){
  ok(x.article.toLowerCase().includes(s.toLowerCase()),"ARTICLE_PROOF_"+s);
 }
 ok(x.dossier.includes("NOT COMPUTABLE")&&x.dossier.includes("mind_pilot_2026_11")&&x.dossier.includes("mind_proposed_2026_11"),"ACCEPTANCE_UNVERIFIED_REVENUE_OR_CAMPAIGN");
 ok(x.hub.includes("NOT a playable video")&&x.hub.includes("preload")===false,"FALSE_FILM_PLAYBACK");
 for(const [k,h] of Object.entries(frozen))ok(hash(x[k])===h,"FROZEN_"+k);
 return {valid:true,files:Object.keys(paths).length,source_records:m.sources.length,unique_urls:23,claim_decisions:m.claims.length,commercial_gates:m.gates.length,creator_paths:m.creator_topic_fit.length};
}
function mutate(x){
 const tests=[
  ["active_buy", "hub",z=>z.hub=z.hub.replace('type="button" disabled','type="button"'),"DISABLED_PURCHASE"],
  ["affiliate_link", "hub",z=>z.hub=z.hub.replace("</body>",'<a href="https://zen12.com/getstarted">Checkout</a></body>'),"HREF_HOST"],
  ["encoded_link","hub",z=>z.hub=z.hub.replace("</body>",'<a href="javascript&#58;alert(1)">Link</a></body>'),"ENCODED_HREF"],
  ["meta_refresh","hub",z=>z.hub=z.hub.replace("</head>",'<meta http-equiv="refresh" content="0;url=https://zen12.com"></head>'),"META_REFRESH"],
  ["base_href","hub",z=>z.hub=z.hub.replace("</head>",'<base href="https://evil.example/"></head>'),"UNSAFE_TAG"],
  ["remote_script","hub",z=>z.hub=z.hub.replace("</head>",'<script src="https://evil.example/tracker.js"></script></head>'),"UNSAFE_TAG"],
  ["css_import","hub",z=>z.hub=z.hub.replace("</style>",'@import "https://evil.example/x.css";</style>'),"EXTERNAL_CSS"],
  ["css_url","hub",z=>z.hub=z.hub.replace("</style>",'.x{background:url(https://evil.example/pixel)}</style>'),"EXTERNAL_CSS"],
  ["duplicate_form","hub",z=>z.hub=z.hub.replace("</body>",'<form action="https://evil.example"><input type="email"></form></body>'),"UNSAFE_TAG"],
  ["inline_event","hub",z=>z.hub=z.hub.replace("</body>",'<b onclick="go()">x</b></body>'),"INLINE_EVENT"],
  ["hidden_link","hub",z=>z.hub=z.hub.replace("</body>",'<div data-href="https://zen12.com">x</div></body>'),"HIDDEN_DESTINATION"],
  ["iframe","hub",z=>z.hub=z.hub.replace("</body>",'<iframe src="https://zen12.com"></iframe></body>'),"UNSAFE_TAG"],
  ["remote_image","hub",z=>z.hub=z.hub.replace("</body>",'<img src="https://evil.example/track.png" alt=""></body>'),"REMOTE_IMG"],
  ["hidden_disclosure","hub",z=>z.hub=z.hub.replace("</style>",'.disclosure{display:none}</style>'),"HIDDEN_DISCLOSURE"],
  ["remove_disclosure","hub",z=>z.hub=z.hub.replace("may earn a commission","may receive updates"),"NEAR_LINK_DISCLOSURE"],
  ["guide_A_insecure","guideA",z=>z.guideA=z.guideA.replace("https://finalvestige.com/focus/","http://finalvestige.com/focus/"),"HTTPS_ONLY"],
  ["guide_B_merchant","guideB",z=>z.guideB=z.guideB.replace("</body>",'<a href="https://brainwaveshots.com/focus-shot">Order</a></body>'),"HREF_HOST"],
  ["guide_B_safe_sentence_edit","guideB",z=>z.guideB=z.guideB.replace("Zen12 Premium","Zen12 Premium EDITED"),"FROZEN_guideB"],
  ["upstream_article_tamper","parentArticle",z=>z.parentArticle=z.parentArticle.replace("isochronic","ISoCHRONIC"),"FROZEN_parentArticle"],
  ["sources_removed","matrix",z=>{const m=JSON.parse(z.matrix);m.sources=[];z.matrix=JSON.stringify(m)},"SOURCE_COUNT_OR_UNIQUES"],
  ["source_url_swap","matrix",z=>{const m=JSON.parse(z.matrix);m.sources[0].url="https://example.com";z.matrix=JSON.stringify(m)},"RELATIONSHIP_DIGEST_sources"],
  ["source_type_launder","matrix",z=>{const m=JSON.parse(z.matrix);m.sources.find(s=>s.id==="S01").type="official_regulator";z.matrix=JSON.stringify(m)},"RELATIONSHIP_DIGEST_sources"],
  ["claim_statement","matrix",z=>{const m=JSON.parse(z.matrix);m.claims.find(c=>c.id==="C32").statement="Zen12 proven";z.matrix=JSON.stringify(m)},"RELATIONSHIP_DIGEST_claims"],
  ["claim_source","matrix",z=>{const m=JSON.parse(z.matrix);m.claims.find(c=>c.id==="C32").source_ids=["S01"];z.matrix=JSON.stringify(m)},"RELATIONSHIP_DIGEST_claims"],
  ["claim_decision","matrix",z=>{const m=JSON.parse(z.matrix);m.claims.find(c=>c.id==="C34").decision="SUPPORTED";z.matrix=JSON.stringify(m)},"RELATIONSHIP_DIGEST_claims"],
  ["gate_removed","matrix",z=>{const m=JSON.parse(z.matrix);m.gates.pop();z.matrix=JSON.stringify(m)},"CLAIM_OR_GATE_COUNT"],
  ["gate_approved","matrix",z=>{const m=JSON.parse(z.matrix);m.gates[0].status="APPROVED";z.matrix=JSON.stringify(m)},"RELATIONSHIP_DIGEST_gates"],
  ["offers_removed","matrix",z=>{const m=JSON.parse(z.matrix);m.offers=[];z.matrix=JSON.stringify(m)},"OFFER_COUNT"],
  ["earning_url","matrix",z=>{const m=JSON.parse(z.matrix);m.offer_hypothesis.authorized_earning_url="https://x.example";z.matrix=JSON.stringify(m)},"ACCOUNT_NOT_APPROVED"],
  ["offer_changed","matrix",z=>{const m=JSON.parse(z.matrix);m.offers[0].name="Hype";z.matrix=JSON.stringify(m)},"RELATIONSHIP_DIGEST_offers"],
  ["creator_removed","matrix",z=>{const m=JSON.parse(z.matrix);m.creator_topic_fit=[];z.matrix=JSON.stringify(m)},"CREATOR_COUNT"],
  ["invented_grok","matrix",z=>{const m=JSON.parse(z.matrix);m.creator_topic_fit[0].grok_asset_id="fake";z.matrix=JSON.stringify(m)},"RELATIONSHIP_DIGEST_creator_topic_fit"],
  ["fake_campaign","matrix",z=>{const m=JSON.parse(z.matrix);m.first_party_event_contract.campaign_id="mind_live";z.matrix=JSON.stringify(m)},"CAMPAIGN_HOLD"],
  ["false_playable_B","matrix",z=>{const m=JSON.parse(z.matrix);m.ab_hypothesis.B_media_actual="playable";z.matrix=JSON.stringify(m)},"B_STATIC_OR_AB_STATUS"],
  ["owned_fallback_approved","matrix",z=>{const m=JSON.parse(z.matrix);m.offer_hypothesis.fallback_owned_paid_sku_verified=true;z.matrix=JSON.stringify(m)},"OWNED_FALLBACK_NOT_VERIFIED"],
  ["false_article_efficacy","article",z=>z.article=z.article.replace("111 randomized trials","111 unrelated ads"),"ARTICLE_PROOF_111 randomized"],
  ["remove_noindex","hub",z=>z.hub=z.hub.replace('name="robots" content="noindex,nofollow"','name="robots" content="index,follow"'),"NOINDEX"],
  ["false_film_page","hub",z=>z.hub=z.hub.replace("NOT a playable video","IS a playable video"),"FALSE_FILM_PLAYBACK"]
 ];
 for(const metric of ["qualified_sessions_7d","qualified_sessions_30d","relevant_cta_clicks","confirmed_jetpack_leads","merchant_confirmed_orders","commission_settled","refunds","fees","net_realized_revenue","revenue_per_1000_qualified_humans"]){
  tests.push(["metric_"+metric,"matrix",z=>{const m=JSON.parse(z.matrix);m.measurement[metric]=1;z.matrix=JSON.stringify(m)},"METRIC_NULL_"+metric]);
 }
 let passed=0;
 for(const [name,key,edit,expected] of tests){
  const z={...x},old=z[key];edit(z);
  ok(z[key]!==old,"MUTATION_NO_CHANGE_"+name);
  let caught=null;try{verify(z)}catch(e){caught=String(e.message)}
  ok(caught!==null&&caught.includes(expected),"WRONG_REASON_"+name+" expected="+expected+" got="+caught);
  passed++;
 }
 return {rejected_for_expected_reason:passed,total:tests.length};
}
function load(){const o={};for(const [k,p] of Object.entries(paths))o[k]=fs.readFileSync(p,"utf8");return o}
if(require.main===module){
 try{const src=load();console.log("R297 BASELINE "+JSON.stringify(verify(src)));console.log("R297 MUTATIONS "+JSON.stringify(mutate(src)));process.exitCode=0}
 catch(e){console.error("R297 FAILED "+e.stack);process.exitCode=1}
}
module.exports={verify,mutate,load,paths};

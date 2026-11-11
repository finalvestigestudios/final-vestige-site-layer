"use strict";
/** Mind R301 standard-library-only source validation. Run from repo root:
 * node mind/r301/verify_r301.cjs
 * NO external calls, mutations, accounts, CMS writes or merchant tracking.
 * Browser, WP sanitization, hosted video, payment and consent remain separately unverified.
 */
const fs=require("node:fs"),path=require("node:path");
const root=path.resolve(__dirname,"../..");
const files={
  article:"mind/r301/THE-SECOND-TARGET-THAT-VANISHED-ATTENTIONAL-BLINK-UNPUBLISHED.md",
  matrix:"mind/r301/ATTENTIONAL-BLINK-PRODUCT-CLAIMS-CREATOR-COMMERCE-MATRIX.json",
  acceptance:"mind/r301/ZEN12-ONE-OFFER-PRESELL-ORIGINAL-FILM-AND-REVENUE-ACCEPTANCE.md",
  film:"mind/r301/video/render_zen12_source_ladder.py",
  captions:"mind/r301/video/captions.vtt",
  legacyArticle:"mind/r299/THE-PATIENT-THE-STUDY-COULD-NOT-ACCOUNT-FOR-UNPUBLISHED.md",
  legacyMatrix:"mind/r299/CLAIMS-SOURCES-OFFERS-AND-REVENUE-GATES.json",
  A:"mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html",
  B:"mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html",
  hub:"mind/r299/MIND-ARCHIVE-RESEARCH-ROOM-WP-HTML-CANDIDATE.html"
};
const fail=(x)=>{throw new Error(x)},ok=(x,y)=>{if(!x)fail(y)};
const load=()=>Object.fromEntries(Object.entries(files).map(([k,v])=>[k,fs.readFileSync(path.join(root,v),"utf8")]));
function validate(d){
 const m=JSON.parse(d.matrix),legacy=JSON.parse(d.legacyMatrix);
 ok(m.schema==="fv.mind.r301.v1"&&m.release_status==="UNPUBLISHED_HARD_HOLD","RELEASE_HARD_HOLD");
 ok(m.sources.length===22&&m.claims.length===24&&m.gates.length===18,"SOURCE_CLAIM_GATE_COUNT");
 const sm=new Map(m.sources.map(x=>[x.id,x]));
 ok(sm.size===22&&new Set(m.sources.map(x=>x.url)).size===22,"SOURCE_DUPLICATES");
 for(const x of m.sources)ok(/^https:\/\//.test(x.url)&&x.source_class&&x.reading_limit,"SOURCE_URL_OR_DEPTH");
 ok(new Set(m.claims.map(x=>x.id)).size===24,"CLAIM_DUPLICATE");
 for(const x of m.claims)ok(x.source_ids.length&&x.source_ids.every(id=>sm.has(id))&&x.decision&&x.reason,"CLAIM_SOURCE_RELATION");
 ok(m.gates.every(x=>x.status==="HARD_HOLD"&&x.proof===null),"COMMERCIAL_HOLDS");
 ok(Object.values(m.release_approval).every(x=>x===false),"RELEASE_APPROVAL_FALSE");
 ok(m.canonical_routing.variant_A===files.A&&m.canonical_routing.variant_B===files.B,"CANONICAL_AB");
 ok(/B STATIC storyboard/.test(m.canonical_routing.video_state),"NOT_LIVE_VIDEO");
 ok(m.creator_topic_fit.every(x=>x.asset_id===null||x.asset_id==="zctcIECAZ2s"),"NO_FABRICATED_CREATOR_ID");
 ok(m.creator_topic_fit.find(x=>x.asset_id==="zctcIECAZ2s").status.includes("OWNER_REPORTED"),"NO_FAKE_PLATFORM_VERIFICATION");
 ok(m.attribution_contract.unknown_metric==="NOT_COMPUTABLE"&&m.attribution_contract.metric.includes("qualified human sessions"),"NO_FAKE_PAID_KPI");
 ok(!m.release_approval.earning_url_verified&&m.release_approval.video_hosted===false,"NO_FALSE_ACTIVATION");
 ok(legacy.claims.find(x=>x.id==="C28").reason.includes("owner-reported"),"LEGACY_C28_WORDING");
 ok(!legacy.claims.find(x=>x.id==="C28").reason.includes("Drive reports authentication"),"LEGACY_C28_FALSE_AUTH");
 ok(d.legacyArticle.includes("Primary article scan directly inspected")&&d.legacyArticle.includes("continuation page (printed p. 623)"),"LEGACY_LEDGER_REPAIR");
 ok(d.article.trim().split(/\s+/).length>=2400,"ARTICLE_LENGTH");
 for(const q of ["pubmed.ncbi.nlm.nih.gov/1500880","pubmed.ncbi.nlm.nih.gov/7707027","pmc.ncbi.nlm.nih.gov/articles/PMC8062350","pubmed.ncbi.nlm.nih.gov/17488185","not a test of","48-MP3"])ok(d.article.includes(q),"ARTICLE_SOURCE_OR_CLAIM_"+q);
 ok(d.article.includes("unpublished editorial draft")&&d.article.includes("does **not**"),"ARTICLE_UNPUBLISHED_LIMITS");
 ok(d.acceptance.includes("R284 A/B")&&d.acceptance.includes("HARD HOLD")&&d.acceptance.includes("cleared FV commission"),"ONE_OFFER_REVENUE_GUARD");
 ok(d.acceptance.includes("no external script")||d.acceptance.includes("no external assets"),"VIDEO_PRIVACY");
 ok(d.film.includes("W,H,FPS,DURATION=960,540,12,42"),"FILM_DURATION_42");
 ok(d.film.includes("-an")&&d.film.includes("+faststart")&&d.film.includes("render(t)"),"FILM_SOURCE");
 ok((d.captions.match(/-->/g)||[]).length===7&&d.captions.includes("00:00:42.000"),"VTT_42S_SEVEN_SCENES");
 ok(d.hub.includes("may earn a commission")&&/disabled/i.test(d.hub)&&!/<script\b/i.test(d.hub),"HUB_DISABLED_DISCLOSURE");
 for(const key of ["A","B"])ok(d[key].includes("disabled")&&d[key].includes("<html")&&!/<script\b/i.test(d[key]),"AB_INACTIVE_"+key);
 // The register and the guide can cite seller pages as SOURCES, not active earning destinations.
 ok(!/https:\/\/(?:www\.)?awin1.com/i.test(d.acceptance)&&!/(affiliate_url|earning_url)\s*:\s*["']https:/i.test(d.acceptance),"NO_EARNING_URL");
 return true;
}
const fixtures=[
 ["fake_gate","matrix",s=>s.replace('"status": "HARD_HOLD"','"status": "PASS"'),"COMMERCIAL_HOLDS"],
 ["pretend_approval","matrix",s=>s.replace('"affiliate_publisher_accepted": false','"affiliate_publisher_accepted": true'),"RELEASE_APPROVAL_FALSE"],
 ["pretend_video_live","matrix",s=>s.replace('B STATIC storyboard','B LIVE video'),"NOT_LIVE_VIDEO"],
 ["fake_revenue","matrix",s=>s.replace('"unknown_metric": "NOT_COMPUTABLE"','"unknown_metric": "100"'),"NO_FAKE_PAID_KPI"],
 ["remove_source","matrix",s=>s.replace('"id": "S01"','"id": "WRONG"'),"CLAIM_SOURCE_RELATION"],
 ["duplicate_source","matrix",s=>s.replace('"id": "S02"','"id": "S01"'),"SOURCE_DUPLICATES"],
 ["false_creator","matrix",s=>s.replace('"asset_id": null','"asset_id": "invented"'),"NO_FABRICATED_CREATOR_ID"],
 ["false_asset_approval","matrix",s=>s.replace("OWNER_REPORTED_NOT_PLATFORM_VERIFIED","VERIFIED_LIVE"),"NO_FAKE_PLATFORM_VERIFICATION"],
 ["fewer_captions","captions",s=>s.replace("00:00:36.000 --> 00:00:42.000","00:00:36.000 --> 00:00:36.000"),"VTT_42S_SEVEN_SCENES"],
 ["short_film","film",s=>s.replace("960,540,12,42","960,540,12,30"),"FILM_DURATION_42"],
 ["remove_free_alternative","article",s=>s.replace("48-MP3","48 unknown"),"ARTICLE_SOURCE_OR_CLAIM_48-MP3"],
 ["remove_disclosure","hub",s=>s.replace("may earn a commission","may receive no commission"),"HUB_DISABLED_DISCLOSURE"],
 ["false_original_scan","legacyArticle",s=>s.replace("Primary article scan directly inspected","Abstract only"),"LEGACY_LEDGER_REPAIR"],
 ["false_grok_source","legacyMatrix",s=>s.replace("owner-reported","directly verified"),"LEGACY_C28_WORDING"],
 ["invalid_article","article",s=>s.slice(0,1000),"ARTICLE_LENGTH"]
];
function run(){
 const d=load();validate(d);let n=0;
 for(const [name,key,mutate,expected] of fixtures){
  const x={...d,[key]:mutate(d[key])};ok(x[key]!==d[key],"NO_MUTATION_"+name);
  let error=null;try{validate(x)}catch(e){error=e.message}
  // These fixtures reject changes; use exact expected code where stable.
  ok(error!==null,"UNDETECTED_"+name);
  n++;
 }
 console.log(JSON.stringify({status:"PASS",files:Object.keys(files).length,sources:22,claims:24,commercial_gates:18,mutation_rejections:n,scope:"source_only",video:"LOCAL_NOT_HOSTED",wordpress:"NOT_TESTED",paid_conversions:"NOT_VERIFIED"},null,2));
}
if(require.main===module)run();
module.exports={validate};

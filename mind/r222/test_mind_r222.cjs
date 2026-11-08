// FV Mind R222 -- source-only safety/claims tests. Run: node mind/r222/test_mind_r222.cjs
// Does NOT prove actual WordPress sanitization, browser/AT, media playback, merchant authorization or revenue.
"use strict";
const fs=require("node:fs"),path=require("node:path");
const ROOT=path.resolve(__dirname,"../..");
const PATHS={
 article:"mind/r222/the-face-that-changed-when-upright-THATCHER-UNPUBLISHED.md",
 hub:"mind/r222/mind-archive-four-stream-thatcher-WP-PREVIEW-UNPUBLISHED.html",
 a:"mind/r222/zen12-r222-A-TEXT-UNPUBLISHED.html",
 b:"mind/r222/zen12-r222-B-OPTIONAL-42S-UNRENDERED.html",
 poster:"mind/r222/zen12-r222-42s-POSTER-ORIGINAL.svg",
 captions:"mind/r222/zen12-r222-42s-CONCEPT.vtt",
 matrix:"mind/r222/THATCHER-ZEN12-CLAIM-PROOF-ELIGIBILITY-MATRIX.json",
 plan:"mind/r222/OFFER-FIRST-THATCHER-CREATOR-REVENUE-AB-RELEASE-PLAN.md"
};
const REQUIRED_GATE_STATUS={G01:"HARD_HOLD",G02:"HARD_HOLD",G03:"HARD_HOLD",G04:"HARD_HOLD",G05:"HARD_HOLD",G06:"HARD_HOLD",G07:"HARD_HOLD",G08:"HARD_HOLD",G09:"HARD_HOLD",G10:"NOT_TESTED",G11:"NOT_TESTED",G12:"NOT_BUILT",G13:"HOLD_UNTIL_ELIGIBLE",G14:"PENDING",G15:"BLOCKED_PROVIDER",G16:"NOT_COMPUTABLE"};
function attrs(html,tag){return [...html.matchAll(new RegExp("<"+tag+"\\b([^>]*)>","gi"))].map(x=>x[1]);}
function hrefs(html){return attrs(html,"a").map(a=>{const m=a.match(/(?:^|\s)href\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>]+))/i);return m?(m[1]??m[2]??m[3]):null;}).filter(Boolean);}
function nativeDisabled(a){return /(?:^|\s)disabled(?=\s|=|$)/i.test(a);}
function earningUrl(url){return /(?:awin1\.com|clickbank|[?&](?:aff|affiliate|hop|subid|clickref|ref)=|\/checkout(?:[/?#]|$)|\/order(?:[/?#]|$)|\bpayhip\.com\/b\/)/i.test(url);}
function normalizeB(html){return html.replace(/<section class="film reading"[\s\S]*?<\/section>/,"").replaceAll("VARIANT B","VARIANT A").replace(" / B | Final Vestige"," / A | Final Vestige");}
function extractGuide(html){const a=html.indexOf('<section class="reading" aria-labelledby="what">'),b=html.indexOf('<section class="offer reading"');return a<0||b<0?"":html.slice(a,b);}
function validate(f){
 const issues=[],ok=(v,l)=>{if(!v)issues.push(l);};
 for(const k of Object.keys(PATHS))ok(typeof f[k]==="string"&&f[k].length>120,"missing_file_"+k);
 if(issues.length)return issues;
 const {article,hub,a,b,poster,captions,plan}=f;
 let m;try{m=JSON.parse(f.matrix);}catch(e){return["bad_matrix_json"];}
 ok(article.split(/\s+/).length>=2900,"article_depth_2900");
 for(const s of ["10.1068/p090483","10.1068/p6659","21639673","PMC2982021","0956797613501521","Thatcher illusion","theory","copyright","Puységur","Access note","UNPUBLISHED","/focus/"])ok(article.toLowerCase().includes(s.toLowerCase()),"article_source_or_limit_"+s);
 ok(!/i personally used zen12|i tried zen12|zen12 cures|guaranteed cognitive improvement|we earned commission/i.test(article),"no_research_as_ad");
 for(const [i,h] of [hub,a,b].entries()){
  ok(h.includes("<!doctype html>")&&h.includes('lang="en"')&&h.includes("noindex,nofollow"),"html_unpublished_"+i);
  ok(h.includes('href="#main"')&&h.includes('id="main"')&&h.includes("focus-visible")&&h.includes("prefers-reduced-motion"),"accessibility_scaffold_"+i);
  ok(!/<(?:script|iframe|form|video|audio|source|meta\s+http-equiv\s*=\s*["']?refresh)\b/i.test(h),"no_thirdparty_or_form_"+i);
  ok(!/\s(?:onclick|onload|onerror|onkeydown|formaction|data-affiliate|data-checkout|data-redirect|data-tracking)\s*=/i.test(h),"no_event_or_checkout_attr_"+i);
  ok(!hrefs(h).some(earningUrl),"no_commercial_url_"+i);
  const buttons=attrs(h,"button");
  ok(buttons.length===1&&buttons.every(v=>nativeDisabled(v)&&/(?:^|\s)type\s*=\s*["']?button/i.test(v)),"all_buttons_native_disabled_"+i);
  const d=h.indexOf("may earn a commission"),btn=h.indexOf("<button");
  ok(d>=0&&btn>d&&btn-d<500,"adjacent_commission_notice_"+i);
  ok(h.includes("https://finalvestige.com/focus/"),"existing_free_focus_"+i);
 }
 ok(!/<script|<foreignObject|<image|<use\b|onload=|href=/i.test(poster),"poster_original_offline_svg");
 ok(poster.includes('role="img"')&&poster.includes("<desc")&&poster.includes("TWELVE MINUTES"),"poster_alt");
 ok(hub.includes("Puységur")&&hub.includes("PR #172")&&hub.includes("Change Blindness")&&hub.includes("Thatcher"),"hub_four_stream");
 ok(hub.includes('<svg')&&hub.includes('role="img"')&&hub.includes('<desc'),"hub_art_description");
 ok(b.includes("42-second")&&b.includes("narration")&&/not rendered|unrendered/i.test(b),"film_explicit_unrendered");
 ok(!a.includes('<section class="film reading"')&&b.includes('<section class="film reading"'),"ab_film_only_difference");
 ok(extractGuide(a).length>4000&&extractGuide(a)===extractGuide(b),"ab_same_core_claims");
 ok(normalizeB(b)===a,"ab_exact_except_optional_film_and_label");
 ok(captions.startsWith("WEBVTT")&&(captions.match(/-->/g)||[]).length===5&&captions.includes("00:00:42.000"),"timed_five_captions");
 ok(b.includes("Read full narration / transcript")&&b.includes("0–8 seconds")&&b.includes("34–42 seconds"),"transcript_equivalence");
 ok(m.sources?.length>=18&&m.claims?.length>=28,"matrix_source_claim_count");
 const gates=m.release_gates||[];
 ok(gates.length===16,"gates_exact_count");
 for(const [id,status]of Object.entries(REQUIRED_GATE_STATUS)){let g=gates.filter(x=>x.id===id);ok(g.length===1&&g[0].status===status,"required_gate_"+id);}
 for(const id of ["C16","C17","C18","C20","C23","C24","C26","C29"]){ok(m.claims.some(c=>c.id===id&&/(UNSUBSTANTIATED|PROHIBITED|REJECTED|FALSE|NOT_COMPUTABLE)/.test(c.status)),"claims_boundary_"+id);}
 ok(m.primary_kpi_status==="NOT_COMPUTABLE"&&m.commerce_activation==="HARD_HOLD","matrix_economic_truth");
 ok(plan.includes("NOT COMPUTABLE")&&plan.includes("merchant-confirmed")&&plan.includes("Grok")&&plan.includes("Praxxis")&&plan.includes("Issue #820"),"plan_revenue_and_coordination");
 ok(plan.includes("subscribe")&&plan.includes("Jetpack")&&plan.includes("6724517348"),"known_focus_spoof_blocker");
 ok(plan.includes("R210")&&plan.includes("42-second")&&plan.includes("NO live CMS"),"ab_governance");
 return issues;
}
const baseline=Object.fromEntries(Object.entries(PATHS).map(([k,p])=>[k,fs.readFileSync(path.join(ROOT,p),"utf8")]));
const errors=validate(baseline);if(errors.length)throw Error("BASELINE FAIL: "+errors.join(", "));
const mutate=(id,key,fn)=>({id,key,fn});
const cases=[
 mutate("enable_hub","hub",s=>s.replace('type="button" disabled','type="button"')),
 mutate("enable_a","a",s=>s.replace('type="button" disabled','type="button"')),
 mutate("enable_b","b",s=>s.replace('type="button" disabled','type="button"')),
 mutate("aria_only_hub","hub",s=>s.replace('type="button" disabled','type="button" aria-disabled="true"')),
 mutate("second_enabled_a","a",s=>s.replace("</main>",'<button type="button">buy</button></main>')),
 mutate("second_enabled_b","b",s=>s.replace("</main>",'<button type="button">buy</button></main>')),
 mutate("second_enabled_hub","hub",s=>s.replace("</main>",'<button type="button">buy</button></main>')),
 mutate("onclick_b","b",s=>s.replace("<button class=",'<button onclick="checkout()" class=')),
 mutate("data_checkout_a","a",s=>s.replace("<button class=",'<button data-checkout="true" class=')),
 mutate("unquoted_affiliate_url","hub",s=>s.replace("</main>",'<a href=https://www.awin1.com/cread.php?aff=wrong>buy</a></main>')),
 mutate("quoted_affiliate_url","a",s=>s.replace("</main>",'<a href="https://www.awin1.com/cread.php?aff=wrong">buy</a></main>')),
 mutate("direct_checkout","b",s=>s.replace("</main>",'<a href="https://zen12.com/checkout">pay</a></main>')),
 mutate("payhip_order_a","a",s=>s.replace("</main>",'<a href="https://payhip.com/b/FakeID">pay</a></main>')),
 mutate("remove_disclosure_hub","hub",s=>s.replace("may earn a commission","may offer a description")),
 mutate("remove_disclosure_a","a",s=>s.replace("may earn a commission","may mention a product")),
 mutate("remove_disclosure_b","b",s=>s.replace("may earn a commission","may mention a product")),
 mutate("duplicate_form_a","a",s=>s.replace("</main>",'<form><input type="email"></form></main>')),
 mutate("duplicate_form_hub","hub",s=>s.replace("</main>",'<form><input type="email"></form></main>')),
 mutate("script_b","b",s=>s.replace("</main>",'<script src="https://tracker.test/t.js"></script></main>')),
 mutate("iframe_a","a",s=>s.replace("</main>",'<iframe src="https://video.test"></iframe></main>')),
 mutate("fake_video_b","b",s=>s.replace("</main>",'<video autoplay src="https://some.cdn/video.mp4"></video></main>')),
 mutate("missing_primary_source","article",s=>s.replaceAll("10.1068/p090483","missing")),
 mutate("remove_rights_warning","article",s=>s.replaceAll("copyright","copy right")),
 mutate("remove_pubmed","article",s=>s.replaceAll("21639673","missing")),
 mutate("truncate_article","article",s=>s.slice(0,2000)),
 mutate("poster_external","poster",s=>s.replace("</svg>",'<image href="https://example.com/pixel.png"/></svg>')),
 mutate("poster_no_alt","poster",s=>s.replace('role="img"','role="presentation"')),
 mutate("caption_remove","captions",s=>s.replace(/00:00:34.000 --> 00:00:42.000[\s\S]*/,"")),
 mutate("a_remove_research","a",s=>s.replace(/<section class="reading" aria-labelledby="what">[\s\S]*?<\/section>/,"")),
 mutate("b_omits_objections","b",s=>s.replace("Questions worth asking before any purchase","Ignore questions")),
 mutate("remove_film","b",s=>s.replace(/<section class="film reading"[\s\S]*?<\/section>/,"")),
 mutate("remove_gate","matrix",s=>{let m=JSON.parse(s);m.release_gates=m.release_gates.filter(g=>g.id!=="G09");return JSON.stringify(m);}),
 mutate("rename_gate","matrix",s=>{let m=JSON.parse(s);m.release_gates[0].id="G99";return JSON.stringify(m);}),
 mutate("duplicate_gate","matrix",s=>{let m=JSON.parse(s);m.release_gates.push({...m.release_gates[0]});return JSON.stringify(m);}),
 mutate("activate_gate","matrix",s=>{let m=JSON.parse(s);m.release_gates.find(g=>g.id==="G01").status="APPROVED";return JSON.stringify(m);}),
 mutate("claim_effective","matrix",s=>{let m=JSON.parse(s);m.claims.find(c=>c.id==="C16").status="PROVEN_EFFECTIVE";return JSON.stringify(m);}),
 mutate("fabricate_approval","matrix",s=>{let m=JSON.parse(s);m.claims.find(c=>c.id==="C20").status="VERIFIED";return JSON.stringify(m);}),
 mutate("fabricate_sales","matrix",s=>{let m=JSON.parse(s);m.primary_kpi_status="VERIFIED_100_USD";return JSON.stringify(m);}),
 mutate("remove_focus_spoof_warning","plan",s=>s.replace("6724517348","not known")),
 mutate("remove_ab_governance","plan",s=>s.replaceAll("R210","R222"))
];
let failures=[];for(const t of cases){const changed=t.fn(baseline[t.key]);if(changed===baseline[t.key]){failures.push("mutation_no_effect:"+t.id);continue;}const trial={...baseline,[t.key]:changed};if(validate(trial).length===0)failures.push("undetected:"+t.id);}
if(failures.length)throw Error("MUTATION FAIL: "+failures.join(", "));
console.log("R222 PASS: baseline 0 violations; "+cases.length+"/"+cases.length+" malicious/invalid mutations rejected. Source-level only; no browser/WP/merchant proof.");

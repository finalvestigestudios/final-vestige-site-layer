#!/usr/bin/env node
"use strict";
/** Mind R302: pure validation of exact file bytes; native Node CLI when locally checked out.
 * This guard is source QA only, not browser/WP/merchant authorization.
 */
const fs = require("node:fs"), path=require("node:path");
const EXPECTED_SOURCES={"S01":"https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/","S02":"https://journals.sagepub.com/doi/10.1068/p281059","S03":"https://doi.org/10.1111/1467-9280.00303","S04":"https://finalvestige.com/2026/11/02/change-blindness/","S05":"https://finalvestige.com/explore/","S06":"https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/","S07":"https://finalvestige.com/focus/","S08":"https://finalvestige.com/blog/","S09":"https://inspire3.com/","S10":"https://zen12.com/getstarted","S11":"https://hypnosislive.com/mental-skills/total-focus","S12":"https://brainwaveshots.com/focus-shot","S13":"https://affiliates.inspire3.com/","S14":"https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking","S15":"https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance"};
const EXPECTED_CLAIMS={"C01":{"statement":"2013 experiment recruited 24 radiologists","source_ids":["S01"],"decision":"supported_in_study"},"C02":{"statement":"20 of 24 did not report gorilla in the controlled task","source_ids":["S01"],"decision":"supported_in_study"},"C03":{"statement":"12 of 20 non-reporters fixated gorilla location","source_ids":["S01"],"decision":"supported_in_study"},"C04":{"statement":"Mean dwell time for those fixators was 547ms","source_ids":["S01"],"decision":"supported_in_study"},"C05":{"statement":"Gorilla was inserted across five slices and 48x typical nodule volume","source_ids":["S01"],"decision":"supported_in_study"},"C06":{"statement":"Expert mean nodule detection 55%; novices 12%","source_ids":["S01"],"decision":"supported_in_study"},"C07":{"statement":"2013 third control 88% gorilla detection with cueing","source_ids":["S01"],"decision":"supported_in_study"},"C08":{"statement":"2013 results prove real clinical missed-diagnosis rate 83%","source_ids":["S01"],"decision":"REJECT_extrapolation"},"C09":{"statement":"2013 results prove audio fixes inattentional blindness","source_ids":["S01","S10"],"decision":"REJECT_no_product_trial"},"C10":{"statement":"1999 original study shows task-dependent unexpected-event detection","source_ids":["S02"],"decision":"supported_abstract_only"},"C11":{"statement":"2001 unexpected bright red cross missed by nearly 30% of observers in condition","source_ids":["S03"],"decision":"supported_abstract_only"},"C12":{"statement":"Change blindness and inattentional blindness are identical","source_ids":["S02","S04"],"decision":"REJECT_distinct_constructs"},"C13":{"statement":"Puysegur historical files prove animal magnetism cures","source_ids":["S05","S06"],"decision":"REJECT_historical_claim_not_efficacy"},"C14":{"statement":"FV Journal currently displays 66 results; Issue171 earlier says 61","source_ids":["S08"],"decision":"supported_as_page_view_not_catalog_audit"},"C15":{"statement":"Focus Fieldbook is free 52-page existing lead resource","source_ids":["S07"],"decision":"supported_live_page"},"C16":{"statement":"Zen12 seller lists 12 levels and 48 MP3s","source_ids":["S09","S10"],"decision":"seller_format_only"},"C17":{"statement":"Zen12 improves concentration or clinical outcomes","source_ids":["S10","S15"],"decision":"REJECT_product_specific_support_missing"},"C18":{"statement":"Hypnosis Live Total Focus lists 33-min 47-MB audio","source_ids":["S11"],"decision":"seller_format_only"},"C19":{"statement":"Hypnosis Live Total Focus guarantees attention recovery","source_ids":["S11","S15"],"decision":"REJECT_outcome"},"C20":{"statement":"Brainwave Shots Focus Shot lists 15/30 minute tracks","source_ids":["S12"],"decision":"seller_format_only"},"C21":{"statement":"Brainwave Shots scientifically proven to fix inattentional blindness","source_ids":["S12","S01"],"decision":"REJECT_no_trials"},"C22":{"statement":"Inspire3 public affiliate recruiting proves FV accepted publisher","source_ids":["S13"],"decision":"REJECT_account_specific_authorization_absent"},"C23":{"statement":"Affiliate disclosure must be close to actionable earning link","source_ids":["S14"],"decision":"supported_guidance"},"C24":{"statement":"Health benefit marketing needs adequate relevant substantiation","source_ids":["S15"],"decision":"supported_guidance"},"C25":{"statement":"A click on an affiliate link represents a paid commission","source_ids":["S13"],"decision":"REJECT_accounting_equivalence"},"C26":{"statement":"A merchant's price/discount is final FV approved offer","source_ids":["S10","S11","S12"],"decision":"REJECT_volatile_seller_terms"}};
const FILES={
 article:"THE-GORILLA-IN-THE-SCAN-UNPUBLISHED.md",
 hub:"MIND-OBSERVER-RESEARCH-ROOM-WP-REVIEW-ONLY.html",
 matrix:"EXPERT-GORILLA-CLAIMS-PRODUCT-AND-AUTHORIZATION.json",
 memo:"ONE-OFFER-BUYER-VIDEO-REVENUE-ACCEPTANCE.md"
};
function assert(c,k){if(!c)throw Error(k)}
function validate(f){
 const a=f.article,h=f.hub,m=f.memo;let j;
 try{j=JSON.parse(f.matrix)}catch{throw Error("MATRIX_PARSE")}
 assert(j.status==="SOURCE_CONTROLLED_DRAFT_ONLY","STATUS");
 assert(j.canonical_pilot.earning_url===null && j.canonical_pilot.partner_approved===null && j.canonical_pilot.cleared_commission===null && j.canonical_pilot.net_revenue_per_1000===null,"COMMERCIAL_NOT_NULL");
 assert(j.canonical_pilot.merchant_confirmed_paid_orders===null && j.canonical_pilot.qualified_human_sessions===null,"REVENUE_NOT_NULL");
 assert(Array.isArray(j.sources)&&j.sources.length===15,"SOURCE_COUNT");
 const sm=Object.fromEntries(j.sources.map(s=>[s.id,s.url]));
 assert(new Set(j.sources.map(s=>s.id)).size===15 && new Set(j.sources.map(s=>s.url)).size===15,"SOURCE_UNIQUE");
 assert(JSON.stringify(sm)===JSON.stringify(EXPECTED_SOURCES),"SOURCE_PIN");
 assert(j.claims.length===26,"CLAIM_COUNT");
 const cm=Object.fromEntries(j.claims.map(c=>[c.id,{statement:c.statement,source_ids:c.source_ids,decision:c.decision}]));
 assert(JSON.stringify(cm)===JSON.stringify(EXPECTED_CLAIMS),"CLAIM_PIN");
 assert(j.claims.every(c=>c.source_ids.every(s=>Object.hasOwn(EXPECTED_SOURCES,s))),"DANGLING_SOURCE");
 assert(Array.isArray(j.gates)&&j.gates.length===18&&j.gates.every((g,i)=>g.id==="G"+String(i+1).padStart(2,"0")&&g.status==="HARD_HOLD"&&g.proof===null),"GATE_HOLD");
 assert(j.creator_topic_fit.length===3 && j.creator_topic_fit[1].asset_id===null && j.creator_topic_fit[2].asset_id===null,"CREATOR_IDS");
 assert(a.split(/\s+/).length>1950 && a.startsWith("# The Gorilla in the Scan:") && a.includes("20 of 24") && a.includes("12 looked directly") && a.includes("55 percent") && a.includes("12 percent") && a.includes("88 percent"),"ARTICLE_EVIDENCE");
 assert(a.includes("https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/") && a.includes("full text restricted") && a.includes("not a universal risk percentage"),"ARTICLE_READING_SCOPE");
 assert(/<html lang="en">/.test(h) && /<main id="main">/.test(h) && /class="skip" href="#main"/.test(h),"ACCESSIBILITY_NAV");
 assert(/@media\(max-width:650px\)/.test(h) && /prefers-reduced-motion:reduce/.test(h),"RESPONSIVE_MOTION");
 assert(/<button type="button" disabled aria-describedby="commission-disclosure authorization-status">/.test(h),"CTA_DISABLED");
 assert(/id="commission-disclosure"[^>]*>/.test(h)&&/may earn a commission at no additional cost to you/.test(h)&&h.indexOf('id="commission-disclosure"')>h.indexOf("Purchase link unavailable"),"DISCLOSURE_ADJACENT");
 assert(/<details>/.test(h) && /00–07s/.test(h) && /31–42s/.test(h) && /Not a playable video/.test(h),"FILM_TRUTH");
 assert(!/<(?:script|iframe|form|video|audio|object|embed)\b/i.test(h),"UNAPPROVED_ACTIVE_ELEMENT");
 assert(!/<meta[^>]*http-equiv\s*=\s*["']?refresh/i.test(h),"UNAPPROVED_REDIRECT");
 assert(!/\bon(?:click|load|error|submit|mouseover|focus)\s*=/i.test(h),"UNAPPROVED_EVENT_HANDLER");
 assert(!/\b(?:autoplay|data:|javascript:|window\.location|gtag\(|fbq\()\b/i.test(h),"UNAPPROVED_TRACKING");
 assert(!/<a\b[^>]*\bhref=["'](?:https?:\/\/)?(?:www\.)?(?:zen12|hypnosislive|brainwaveshots|inspire3|affiliates\.inspire3)\b/i.test(h),"MERCHANT_LINK_HOLD");
 const hrefs=[...h.matchAll(/<a\b[^>]*\bhref=["']([^"']+)/gi)].map(x=>x[1]);
 assert(hrefs.length>=6&&hrefs.every(s=>s.startsWith("#")||/^https:\/\/(?:finalvestige\.com|pmc\.ncbi\.nlm\.nih\.gov)\//.test(s)),"OUTBOUND_ALLOWLIST");
 assert(!/display\s*:\s*none|visibility\s*:\s*hidden|aria-hidden\s*=\s*["']true/.test(h.slice(h.indexOf("id=\"commission-disclosure\""),h.indexOf("id=\"authorization-status\""))),"DISCLOSURE_VISIBLE");
 assert(m.includes("HARD HOLD") && m.includes("NOT COMPUTABLE") && m.includes("no independently")===false || m.includes("HARD HOLD") && m.includes("NOT COMPUTABLE"),"REVENUE_MEMO");
 assert(m.includes("not a playable video")===false || m.includes("film"),"FILM_SCOPE");
 return {sources:j.sources.length,claims:j.claims.length,gates:j.gates.length,links:hrefs.length};
}
function run(){
 const f=Object.fromEntries(Object.entries(FILES).map(([k,p])=>[k,fs.readFileSync(path.join(__dirname,p),"utf8")]));
 const baseline=validate(f);let passed=0;const fails=[];
 const fixture=(name,expected,fn)=>{let next={...f};next=fn(next);try{validate(next);fails.push(name+":accepted")}catch(e){if(String(e.message)!==expected)fails.push(name+":wrong-guard-"+e.message);else passed++}};
 const matrix=(f,fn)=>{const j=JSON.parse(f.matrix);fn(j);return {...f,matrix:JSON.stringify(j)}};
 fixture("status","STATUS",f=>matrix(f,j=>{j.status="LIVE"}));
 fixture("merchant earning link","COMMERCIAL_NOT_NULL",f=>matrix(f,j=>{j.canonical_pilot.earning_url="https://fake.invalid/x"}));
 fixture("invented partner approval","COMMERCIAL_NOT_NULL",f=>matrix(f,j=>{j.canonical_pilot.partner_approved=true}));
 fixture("invented cleared commission","COMMERCIAL_NOT_NULL",f=>matrix(f,j=>{j.canonical_pilot.cleared_commission=200}));
 fixture("invented net revenue","COMMERCIAL_NOT_NULL",f=>matrix(f,j=>{j.canonical_pilot.net_revenue_per_1000=500}));
 fixture("invented paid orders","REVENUE_NOT_NULL",f=>matrix(f,j=>{j.canonical_pilot.merchant_confirmed_paid_orders=2}));
 fixture("invented sessions","REVENUE_NOT_NULL",f=>matrix(f,j=>{j.canonical_pilot.qualified_human_sessions=250}));
 fixture("delete source","SOURCE_COUNT",f=>matrix(f,j=>{j.sources.pop()}));
 fixture("duplicate URL","SOURCE_UNIQUE",f=>matrix(f,j=>{j.sources[1].url=j.sources[0].url}));
 fixture("source redirected","SOURCE_PIN",f=>matrix(f,j=>{j.sources[0].url="https://not-science.invalid"}));
 fixture("missing claim","CLAIM_COUNT",f=>matrix(f,j=>{j.claims.pop()}));
 fixture("claim changed","CLAIM_PIN",f=>matrix(f,j=>{j.claims[0].decision="product_proven"}));
 fixture("claim ref swapped","CLAIM_PIN",f=>matrix(f,j=>{j.claims[0].source_ids=["S10"]}));
 fixture("authorizes gate","GATE_HOLD",f=>matrix(f,j=>{j.gates[0].status="PASS"}));
 fixture("deletes gate","GATE_HOLD",f=>matrix(f,j=>{j.gates.pop()}));
 fixture("fake Grok ID","CREATOR_IDS",f=>matrix(f,j=>{j.creator_topic_fit[1].asset_id="invented"}));
 fixture("short article","ARTICLE_EVIDENCE",f=>({...f,article:f.article.slice(0,500)}));
 fixture("reading depth overclaim","ARTICLE_READING_SCOPE",f=>({...f,article:f.article.replace("full text restricted","all full text read")}));
 fixture("missing skip link","ACCESSIBILITY_NAV",f=>({...f,hub:f.hub.replace('class="skip" href="#main"','class="skip" href="#top"')}));
 fixture("no mobile CSS","RESPONSIVE_MOTION",f=>({...f,hub:f.hub.replace("@media(max-width:650px)","@media(max-width:900px)")}));
 fixture("enable CTA","CTA_DISABLED",f=>({...f,hub:f.hub.replace('<button type="button" disabled','<button type="button"')}));
 fixture("remove disclosure","DISCLOSURE_ADJACENT",f=>({...f,hub:f.hub.replace("may earn a commission at no additional cost to you","read our full policy")}));
 fixture("claim playable video","FILM_TRUTH",f=>({...f,hub:f.hub.replace("Not a playable video","Playable now")}));
 fixture("inject script","UNAPPROVED_ACTIVE_ELEMENT",f=>({...f,hub:f.hub+"<script>doBad()</script>"}));
 fixture("inject form","UNAPPROVED_ACTIVE_ELEMENT",f=>({...f,hub:f.hub+"<form></form>"}));
 fixture("inject video","UNAPPROVED_ACTIVE_ELEMENT",f=>({...f,hub:f.hub+"<video autoplay></video>"}));
 fixture("meta redirect","UNAPPROVED_REDIRECT",f=>({...f,hub:f.hub.replace("</head>","<meta http-equiv=\"refresh\" content=\"0;url=https://fake.invalid\"></head>")}));
 fixture("inline event","UNAPPROVED_EVENT_HANDLER",f=>({...f,hub:f.hub.replace("<main id=\"main\">","<main id=\"main\" onclick=\"go()\">")}));
 fixture("merchant link","MERCHANT_LINK_HOLD",f=>({...f,hub:f.hub.replace("</footer>",'<a href="https://zen12.com/getstarted">Buy</a></footer>')}));
 fixture("unapproved outbound","OUTBOUND_ALLOWLIST",f=>({...f,hub:f.hub.replace("</footer>",'<a href="https://pixel.example.net/track">Click</a></footer>')}));
 fixture("hidden disclosure","DISCLOSURE_VISIBLE",f=>({...f,hub:f.hub.replace('id="commission-disclosure" class="disclosure"','id="commission-disclosure" class="disclosure" style="display:none"')}));
 fixture("remove revenue acceptance","REVENUE_MEMO",f=>({...f,memo:f.memo.replaceAll("NOT COMPUTABLE","unknown")}));
 if(fails.length)throw Error("NEGATIVE_FIXTURE_FAILURES "+fails.join(";"));
 console.log(JSON.stringify({result:"PASS",negative_passed:passed,baseline,execution:"local Node if invoked with node; no browser/merchant testing"}));
}
module.exports={validate,run};
if(require.main===module)run();

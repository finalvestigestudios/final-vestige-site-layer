"use strict";
/* FV Mind R252: dependency-free static safety and provenance regression.
   SOURCE-LEVEL only: not WordPress sanitization, browser a11y, checkout, CI, or a real A/B test.
   Native run: node mind/r252/test_r252.cjs from repository root.
   Connector V8: pass four GitHub-retrieved exact source strings to runR252. */
const PINS = Object.freeze({
article:"2a7f884de4e8bc5ec04d88002c34cc9c74f76840",
html:"4b436df50c166d1564d27c0519381aeb51b8e4f4",
matrix:"5e13ab24ac65bddcfb5511fba3606d207d31de86",
plan:"eb968d6d386a63738f4b84c0eab6d9b286f6649a"
});
const PATHS=Object.freeze({
article:"mind/r252/THE-LIE-THAT-LEARNED-TO-SOUND-FAMILIAR-UNPUBLISHED.md",
html:"mind/r252/zen12-premium-one-offer-decision-WP-PREVIEW-UNPUBLISHED.html",
matrix:"mind/r252/CLAIM-PROOF-REVENUE-GATES.json",
plan:"mind/r252/ONE-OFFER-CREATOR-CANONICAL-REVENUE-ACCEPTANCE.md"
});
function validateR252(x){
 const err=[];const push=(ok,message)=>{if(!ok)err.push(message)};
 const article=x.article||"", html=x.html||"", plan=x.plan||"";
 let matrix={};try{matrix=JSON.parse(x.matrix||"")}catch(e){err.push("JSON_PARSE")}
 push(article.trim().split(/\s+/).length>=2200,"ARTICLE_TOO_SHORT");
 push(/The Lie That Learned to Sound Familiar/.test(article),"ARTICLE_TITLE");
 for(const v of ["182 studies","366 effect sizes","31,184","0.37","0.30","0.44","heterogeneity","2026-02-27"]){push(article.includes(v),"ARTICLE_EVIDENCE_"+v)}
 push(/original research manuscript|ORIGINAL INVESTIGATION/.test(article),"ARTICLE_EDITORIAL_MARK");
 push(/not a purchase recommendation/i.test(article),"ARTICLE_COMMERCE_SEPARATION");
 push(article.includes("Puységur")&&article.includes("2022"),"ARTICLE_HISTORICAL_OR_METHOD");
 push(/UNPUBLISHED/.test(html)&&/noindex,nofollow/.test(html),"HTML_UNPUBLISHED_ROBOTS");
 push(/<main\b/.test(html)&&/<nav\b/.test(html)&&/<h1\b/.test(html),"HTML_SEMANTICS");
 push(/<svg[^>]*role="img"/.test(html)&&/aria-labelledby="art-title art-desc"/.test(html),"HTML_SVG_ACCESS");
 push(/prefers-reduced-motion/.test(html)&&/max-width:720px/.test(html),"HTML_RESPONSIVE");
 push(/<table[\s\S]*<th scope="col"/.test(html),"HTML_COMPARISON");
 push(/<details>/.test(html)&&/00:35–00:42/.test(html)&&/not playable/i.test(html),"HTML_FILM_FALLBACK");
 push(!/<(?:script|iframe|form|video|audio)\b/i.test(html),"HTML_NO_TRACKING_FORM_OR_FAKE_VIDEO");
 push(!/\b(?:onload|onclick|onerror|onmouseenter|onfocus)\s*=/i.test(html),"HTML_NO_INLINE_HANDLERS");
 push(!/\bautoplay\b\s*(?:=|>)/i.test(html),"HTML_NO_AUTOPLAY"); 
 push(!/href\s*=\s*["'](?:https?:\/\/)?(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3|hypnosislive|brainwaveshots)\./i.test(html),"HTML_NO_MERCHANT_LINKS");
 push(!/\b(?:gtag\s*\(|fbq\s*\(|dataLayer\.push|localStorage|sessionStorage|document\.cookie)\b/.test(html),"HTML_NO_TRACKERS");
 const btns=html.match(/<button\b[^>]*>/gi)||[];
 push(btns.length===1&&/\bdisabled\b/.test(btns[0])&&/aria-describedby="hold-reason"/.test(btns[0]),"HTML_NATIVE_DISABLED_ONE_BUTTON");
 const bi=html.indexOf("<button"),di=html.indexOf('class="disclosure"');
 push(bi>=0&&di>=0&&di<bi&&bi-di<700,"HTML_NEAR_BUTTON_DISCLOSURE");
 push(/If you purchase through a qualifying link, Final Vestige may earn a commission at no additional cost to you/.test(html),"HTML_EXPLICIT_AFFILIATE_DISCLOSURE");
 push(html.includes('id="hold-reason"')&&html.includes('https://finalvestige.com/focus/'),"HTML_EXISTING_FUNNEL");
 push(!/<input\b/i.test(html)&&!/<select\b/i.test(html),"HTML_NO_NEW_LEAD_CAPTURE");
 push(/12 levels, 48 downloadable MP3|12 levels and 48 MP3|12 levels\/48 MP3/i.test(html),"HTML_PREMIUM_OFFER_MATCH");
 push(html.includes("$87.99")&&/not.*checkout|not.*final charge|not checked/i.test(html),"HTML_PRICE_CAVEAT");
 push(html.includes("not been produced")||html.includes("not playable"),"HTML_NO_VIDEO_OVERCLAIM");
 push(matrix.schema_version==="fv-mind-claim-gates-r252-1","MATRIX_SCHEMA");
 push(matrix.status==="SOURCE_DRAFT_NO_COMMERCE","MATRIX_NOT_LIVE");
 push(matrix.offer==="Zen12 Premium (not Beginner or Advanced)","MATRIX_OFFER");
 push(Array.isArray(matrix.sources)&&matrix.sources.length===matrix.source_count&&matrix.sources.length>=15,"MATRIX_SOURCES");
 push(Array.isArray(matrix.claims)&&matrix.claims.length===matrix.claim_count&&matrix.claims.length>=20,"MATRIX_CLAIMS");
 push(Array.isArray(matrix.gates)&&matrix.gates.length===16&&matrix.gate_count===16,"MATRIX_GATES_COUNT");
 push(Array.isArray(matrix.gates)&&matrix.gates.every(z=>z.status==="HARD_HOLD"&&z.cleared_evidence===null),"MATRIX_FAIL_CLOSED");
 const sourceIds=new Set((matrix.sources||[]).map(s=>s.id));
 push((matrix.claims||[]).every(c=>c.sources?.length&&c.sources.every(s=>sourceIds.has(s))),"MATRIX_SOURCE_REFERENCES");
 push(new Set((matrix.claims||[]).map(c=>c.id)).size===matrix.claim_count,"MATRIX_UNIQUE_CLAIMS");
 push(new Set((matrix.gates||[]).map(c=>c.id)).size===16,"MATRIX_UNIQUE_GATES");
 push((matrix.sources||[]).every(s=>/^https:\/\//.test(s.url)),"MATRIX_SOURCE_HTTPS");
 const hard=(matrix.claims||[]).find(c=>c.id==="C09");
 push(hard&&hard.decision==="UNKNOWN-HARD-HOLD","MATRIX_AFFILIATE_STATUS");
 const rv=matrix.revenue||{};
 push(["qualified_human_sessions","verified_paid_orders","verified_settled_affiliate_commissions","verified_net_revenue","net_revenue_per_1000_qualified_human_sessions"].every(k=>rv[k]===null),"MATRIX_REVENUE_NOT_FABRICATED");
 push(/R204 \/ R218 \/ R251/.test(plan),"PLAN_RUBBER_HAND_CANONICAL");
 push(/156 \/ 404/.test(plan)&&/353 rubber-hand/.test(plan),"PLAN_2020_SAMPLE_CORRECTION");
 push(/2022 same-data reanalysis/.test(plan),"PLAN_DISPUTE_BOTH_SIDES");
 push(/R185\/R250/.test(plan)&&/R236\/R249/.test(plan),"PLAN_OTHER_CANONICAL");
 push(/seller.*not.*FV factual conclusions|seller.*not.*product-specific/i.test(plan),"PLAN_EFFICACY_LIMITS");
 push(/HARD_HOLD/.test(plan)&&/NOT_COMPUTABLE/.test(plan),"PLAN_NONCOMMERCIAL_STATUS");
 push(/affiliate_click/.test(plan)&&/merchant_paid_order/.test(plan)&&/settled_cash/.test(plan),"PLAN_EVENT_DISTINCTIONS");
 push(/actual signed-out mobile/.test(plan)&&/UNKNOWN/.test(plan),"PLAN_CREATOR_IDS");
 push(/No direct WordPress changes/.test(plan)&&/Founder gives separate release permission/.test(plan),"PLAN_RELEASE_CONTROL");
 push(/R248 Variant A/.test(plan)&&/42-second/.test(plan),"PLAN_NO_NEW_AB_ARM");
 push(/360\/390\/768\/1440\/1920/.test(plan),"PLAN_VIEWPORTS");
 return err;
}
function mutationSuite(x){
 const cases=[
 ["enable-button",y=>y.html=y.html.replace('type="button" disabled','type="button"')],
 ["merchant-link",y=>y.html=y.html.replace("</footer>","<a href='https://zen12.com/hnp?affiliate=fake'>BUY</a></footer>")],
 ["no-disclosure",y=>y.html=y.html.replace('class="disclosure"','class="hidden-prospective"')],
 ["fake-disclosure",y=>y.html=y.html.replace("may earn a commission at no additional cost to you","recommend this great product")],
 ["second-CTA",y=>y.html=y.html.replace("</main>","<button disabled>Buy</button></main>")],
 ["hidden-CTA-reason",y=>y.html=y.html.replace('id="hold-reason"','id="gone-reason"')],
 ["autoplay",y=>y.html=y.html.replace("</main>","<video autoplay></video></main>")],
 ["script",y=>y.html=y.html.replace("</main>","<script src='https://tracker.example/p.js'></script></main>")],
 ["form",y=>y.html=y.html.replace("</main>","<form action='/subscribe'><input></form></main>")],
 ["inline-js",y=>y.html=y.html.replace("<main",'<main onclick="alert(1)"')],
 ["analytics",y=>y.html=y.html.replace("</main>","<div>dataLayer.push()</div></main>")],
 ["remove-index-block",y=>y.html=y.html.replace("noindex,nofollow","index,follow")],
 ["drop-svg-access",y=>y.html=y.html.replace('aria-labelledby="art-title art-desc"',"")],
 ["drop-responsive",y=>y.html=y.html.replace("max-width:720px","max-width:900px")],
 ["price-unchecked",y=>y.html=y.html.replaceAll("not authenticated checkout","confirmed checkout").replaceAll("not checked","certified")],
 ["empty-claim-matrix",y=>y.matrix=JSON.stringify({...JSON.parse(y.matrix),claims:[]})],
 ["invent-gate-approved",y=>{const m=JSON.parse(y.matrix);m.gates[0].status="APPROVED";y.matrix=JSON.stringify(m)}],
 ["invent-commission",y=>{const m=JSON.parse(y.matrix);m.revenue.verified_settled_affiliate_commissions=98.5;y.matrix=JSON.stringify(m)}],
 ["invent-qualified-session",y=>{const m=JSON.parse(y.matrix);m.revenue.qualified_human_sessions=30;y.matrix=JSON.stringify(m)}],
 ["change-audience-product",y=>{const m=JSON.parse(y.matrix);m.offer="Hypnosis Live";y.matrix=JSON.stringify(m)}],
 ["remove-publisher-claim",y=>{const m=JSON.parse(y.matrix);m.claims.find(c=>c.id==="C09").decision="APPROVED";y.matrix=JSON.stringify(m)}],
 ["invalid-source-ref",y=>{const m=JSON.parse(y.matrix);m.claims[0].sources=["UNKNOWN_SOURCE"];y.matrix=JSON.stringify(m)}],
 ["duplicate-gate",y=>{const m=JSON.parse(y.matrix);m.gates[1].id=m.gates[0].id;y.matrix=JSON.stringify(m)}],
 ["bad-source-url",y=>{const m=JSON.parse(y.matrix);m.sources[0].url="http://tracking.test";y.matrix=JSON.stringify(m)}],
 ["erase-review-N",y=>y.article=y.article.replace("31,184","99")],
 ["erase-heterogeneity",y=>y.article=y.article.replaceAll("heterogeneity","uniformity")],
 ["erase-merchant-separation",y=>y.article=y.article.replace("not a purchase recommendation","a product recommendation")],
 ["erase-rubber-hand",y=>y.plan=y.plan.replace("R204 / R218 / R251","R251 alone")],
 ["erase-rubber-N",y=>y.plan=y.plan.replace("353 rubber-hand","353 five-star")],
 ["erase-merch-hold",y=>y.plan=y.plan.replaceAll("HARD_HOLD","APPROVED")],
 ["erase-revenue-distinction",y=>y.plan=y.plan.replaceAll("affiliate_click","sale_click")],
 ["erase-creator-verification",y=>y.plan=y.plan.replace("actual signed-out mobile","unconfirmed mobile")],
 ["erase-viewport",y=>y.plan=y.plan.replace("360/390/768/1440/1920","mobile only")],
 ["erase-film-prereg",y=>y.plan=y.plan.replace("R248 Variant A","R252 Variant Z")],
 ["erase-founder-control",y=>y.plan=y.plan.replace("Founder gives separate release permission","Publish automatically")],
 ];
 const pass=[];const fails=[];
 for(const [name,mutate] of cases){let y={...x};mutate(y);const errs=validateR252(y);(errs.length?pass:fails).push({name,errors:errs});}
 return {count:cases.length,rejected:pass.length,escaped:fails.map(z=>z.name),details:pass};
}
function runR252(x){const baseline=validateR252(x),mutations=mutationSuite(x);return {baseline_pass:baseline.length===0,baseline_errors:baseline,mutations_total:mutations.count,mutations_rejected:mutations.rejected,mutations_escaped:mutations.escaped,pass:baseline.length===0&&mutations.escaped.length===0};}
if(typeof module!=="undefined"){module.exports={PATHS,PINS,validateR252,mutationSuite,runR252};if(require.main===module){const fs=require("fs");const docs={};for(const [k,path] of Object.entries(PATHS))docs[k]=fs.readFileSync(path,"utf8");const report=runR252(docs);process.stdout.write(JSON.stringify(report,null,2)+"\n");process.exitCode=report.pass?0:1;}}

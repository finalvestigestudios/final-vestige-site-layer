"use strict";
/**
 * R165 source-level release safety suite.
 * Native: node mind/r165/test_mind_r165.cjs (after checking out the repo).
 * No third-party packages, network access, merchant or CMS changes.
 * A V8 harness may require this module and pass exact retrieved files to run().
 */
const P={
  correctedArticle:"mind/r164/choice-blindness-the-answer-you-never-gave-UNPUBLISHED.md",
  correctedHtml:"mind/r164/zen12-choice-record-buyer-bridge-UNPUBLISHED.html",
  correctedLedger:"mind/r164/zen12-commercial-evidence-and-release-matrix.json",
  guide:"mind/r165/before-you-buy-twelve-minutes-zen12-buyer-guide-UNPUBLISHED.md",
  html:"mind/r165/zen12-evidence-first-presell-UNPUBLISHED.html",
  matrix:"mind/r165/exact-claims-authorizations-and-revenue-gates.json",
  plan:"mind/r165/one-offer-three-creator-routes-revenue-experiment.md",
  hub:"mind/r165/mind-hub-companion-wordpress-DRAFT-UNPUBLISHED.html",
};
function scan(files){
 let assertions=0;
 function check(ok,message){assertions++;if(!ok)throw new Error("R165: "+message)}
 for(const path of Object.values(P))check(typeof files[path]==="string"&&files[path].length>500,"missing or suspiciously short "+path);
 const a=files[P.correctedArticle],h=files[P.correctedHtml],oldLedger=JSON.parse(files[P.correctedLedger]);
 check(a.includes("tasted two jams or smelled two teas"),"precise sensory modalities article");
 check(a.includes("before the participant's final selection"),"precise timing article");
 check(!a.includes("follow-up tastings"),"old incorrect follow-up-tasting wording");
 check(h.includes("tasting jam, smelling tea"),"precise sensory modalities old buyer page");
 check(h.includes("before the final choice"),"precise timing old buyer page");
 check(!h.includes("jam and tea tastings"),"no false universal taste assumption");
 const c=oldLedger.claims.find(x=>x.id==="CB-04");
 check(c&&c.statement.includes("tasted jam or smelled tea"),"old ledger sensory correction");
 check(c&&c.statement.includes("before the final preference"),"old ledger timing correction");
 check(c&&c.source_ids.includes("S15"),"old ledger full text methods source");
 const guide=files[P.guide], page=files[P.html], spec=files[P.plan], hub=files[P.hub], m=JSON.parse(files[P.matrix]);
 check(guide.split(/\s+/).length>=1650,"independent guide substantial");
 check(guide.includes("November 6, 2026"),"research date");
 check(guide.includes("tasted jam or smelled tea"),"guide sensory correction");
 check(guide.includes("before the final preference"),"guide method correction");
 check(guide.includes("111 randomized controlled trials"),"review sample context");
 check(guide.includes("14 EEG studies"),"brainwave evidence context");
 check(guide.includes("not")&&guide.includes("Zen12 Premium"),"commercial evidence limitation");
 check(guide.includes("https://pubmed.ncbi.nlm.nih.gov/20637455/"),"marketplace source");
 check(guide.includes("https://pubmed.ncbi.nlm.nih.gov/37578065/"),"RCT source");
 check(guide.includes("https://pubmed.ncbi.nlm.nih.gov/37205669/"),"EEG source");
 check(guide.includes("https://zen12.com/?no-popup=1"),"exact seller source guide");
 check(guide.includes("https://finalvestige.com/focus/"),"existing Focus guide link");
 check(guide.includes("NO AFFILIATE URL"),"unpublished and no earning link guide");
 check(page.includes("<!doctype html>")&&page.includes('lang="en"'),"valid HTML shell");
 check(page.includes('name="viewport"')&&page.includes('name="robots" content="noindex,nofollow"'),"draft SEO and responsive defaults");
 check(page.includes('href="#main"')&&page.includes('id="main"'),"skip navigation");
 check(page.includes(":focus-visible")&&page.includes("prefers-reduced-motion"),"focus and reduced motion styles");
 check(page.includes("max-width:1160px")&&page.includes("@media(max-width:770px)"),"fluid/responsive intent");
 check(page.includes("jams by taste")&&page.includes("teas by smell"),"page correct modalities");
 check(page.includes("before the final choice"),"page correct timing");
 check(page.includes("12 levels and 48 downloadable MP3s"),"exact seller package");
 check(page.includes("111 randomized mindfulness studies"),"research transfer limitation");
 check(page.includes("14 binaural-beat EEG studies"),"mixed review represented");
 check(page.includes("The existing Final Vestige Focus page")||page.includes("established first-party Focus/Jetpack"),"one native Focus pathway");
 check(page.includes('href="https://finalvestige.com/focus/"'),"active free first-party destination");
 check(page.includes("If a future approved purchasing link appears here and you buy through it, Final Vestige may earn a commission"),"plain adjacent material connection");
 check(page.includes('<button class="btn btn-disabled" type="button" disabled aria-disabled="true">'),"native disabled purchase");
 check(!/href=["']https?:\/\/(?:www\.)?(?:inspire3\.com|zen12\.com|affiliates\.inspire3\.com|www\.awin1\.com)/i.test(page),"no live merchant or affiliate hyperlinks");
 check(!/<script\b/i.test(page),"no JavaScript scripts");
 check(!/<form\b/i.test(page),"no duplicate mailing forms");
 check(!/<iframe\b|<video\b/i.test(page),"no externally embedded or falsely playable video");
 check(page.includes("42-second")&&page.includes("<details>")&&page.includes("<summary>"),"optional accessible text video treatment");
 check(page.includes("No video file, player, autoplay"),"video explicitly not produced");
 check(page.includes("No approved affiliate sales links are active"),"compliance notice near hero");
 check(page.includes("FTC")&&page.includes("Last editorial review"),"disclosures and date");
 check(m.status==="DRAFT_UNPUBLISHED_NOT_LIVE", "matrix unpublished status");
 check(m.affiliate_partner_acceptance==="UNVERIFIED"&&m.affiliate_earning_url===null,"partner authorization gated");
 check(m.paid_orders_confirmed===null&&m.commission_paid===null,"no invented sales or payouts");
 check(m.actual_checkout_price===null,"no unverified checkout price");
 check(m.realized_net_revenue_per_1000===null,"net per 1k not fabricated");
 check(m.claims.length>=20&&m.sources.length>=10,"meaningful source/claim matrix");
 check(m.gates.length>=20&&m.gates.every(g=>g.status==="CLOSED"),"all release gates closed");
 check(m.commercial_button==="native_button_disabled"&&m.active_external_merchant_links===0,"merchant off");
 check(m.claims.find(x=>x.id==="CB-02")?.statement.includes("before final choice"),"new matrix correct timing");
 check(m.claims.find(x=>x.id==="Z-08")?.status==="seller_claim_unsubstantiated","equivalence not adopted");
 check(m.claims.find(x=>x.id==="COM-01")?.status==="NOT_VERIFIED","named acceptance not assumed");
 check(m.measurement.net_revenue_per_1000==="NOT_COMPUTABLE","correct revenue state");
 check(spec.includes("asset_id = NULL")&&spec.includes("three")&&spec.includes("TASK-008"),"creator coordination only");
 check(spec.includes("7-day")&&spec.includes("30-day"),"cohorts");
 check(spec.includes("confirmed_paid_order")&&spec.includes("affiliate_click"),"clicks separate from commerce");
 check(spec.includes("preload=\"none\"")&&spec.includes("WebVTT"),"video accessibility/performance planned");
 check(spec.includes("Do not")&&spec.includes("Grok"),"no Grok queue takeover");
 check(hub.includes("wp:group")&&hub.includes("Mind &amp; Perception"),"WordPress hub companion");
 check(hub.includes("PR #172")&&hub.includes("unpublished"),"canonical ownership and draft status");
 check(hub.includes("https://finalvestige.com/focus/"),"single Focus path hub");
 check(!/<form\b|<script\b/i.test(hub),"no scripts/forms in hub");
 check(!/href=["']https?:\/\/(?:www\.)?zen12\.com/i.test(hub),"no commerce links hub");
 return assertions;
}
const mutations=[
 ["erase-disclosure",P.html,s=>s.replace("Final Vestige may earn a commission","Final Vestige recommends")],
 ["activate-merchant-button",P.html,s=>s.replace('type="button" disabled aria-disabled="true"','type="button"')],
 ["add-merchant-href",P.html,s=>s.replace("</footer>","<a href=\"https://zen12.com/checkout\">Buy now</a></footer>")],
 ["add-tracking-script",P.html,s=>s.replace("</head>","<script src=\"https://example.com/tracker.js\"></script></head>")],
 ["add-extra-form",P.html,s=>s.replace("</main>","<form><input type=\"email\"></form></main>")],
 ["add-autoplay",P.html,s=>s.replace("</main>","<video autoplay></video></main>")],
 ["remove-focus",P.html,s=>s.replace('href="https://finalvestige.com/focus/"','href="#none"')],
 ["remove-source",P.guide,s=>s.replace("https://pubmed.ncbi.nlm.nih.gov/37578065/","about:blank")],
 ["erase-guide-limits",P.guide,s=>s.replace("NO AFFILIATE URL","AFFILIATE LINK ACTIVE")],
 ["erase-precise-jam",P.correctedArticle,s=>s.replace("tasted two jams or smelled two teas","tasted two jams and two teas")],
 ["flip-after-choice",P.correctedArticle,s=>s.replace("before the participant's final selection","after the participant's final selection")],
 ["erase-old-ledger-correction",P.correctedLedger,s=>s.replace("before the final preference","after the final preference")],
 ["erase-full-text-ledger",P.correctedLedger,s=>s.replace('"S15"','"NONE"')],
 ["flip-new-ledger",P.matrix,s=>s.replace("before final choice","after final choice")],
 ["enable-authorization",P.matrix,s=>s.replace('"affiliate_partner_acceptance": "UNVERIFIED"','"affiliate_partner_acceptance": "APPROVED"')],
 ["fabricate-commission",P.matrix,s=>s.replace('"commission_paid": null','"commission_paid": 1000')],
 ["fabricate-earning-url",P.matrix,s=>s.replace('"affiliate_earning_url": null','"affiliate_earning_url": "https://zen12.com/buy"')],
 ["activate-gate",P.matrix,s=>s.replace('"status": "CLOSED"','"status": "OPEN"')],
 ["erase-cohort",P.plan,s=>s.replace("30-day","one-day")],
 ["erase-click-vs-sale",P.plan,s=>s.replace("affiliate_click","fake_affiliate_sale")],
 ["overreach-grok",P.plan,s=>s.replace("asset_id = NULL","asset_id = ASSIGNED")],
 ["erase-hub-preservation",P.hub,s=>s.replace("PR #172","PR #NEXT")],
 ["add-hub-script",P.hub,s=>s+"<script>alert(1)</script>"],
 ["remove-42s",P.html,s=>s.replace("42-second", "short")],
];
function run(files,{mutations_enabled=true}={}){
 const assertions=scan(files);
 let killed=0; let survived=[];
 if(mutations_enabled){for(const [name,p,change] of mutations){const modified={...files,[p]:change(files[p])};try{scan(modified);survived.push(name)}catch(e){killed++}}if(survived.length)throw new Error("Mutation failures: "+survived.join(", "))}
 return {assertions,mutations_killed:killed,mutations_total:mutations.length,all_passed:true};
}
if(typeof module!=="undefined")module.exports={P,scan,run,mutations};
if(typeof require!=="undefined"&&typeof module!=="undefined"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path"),root=path.resolve(__dirname,"../..");
 const data={};for(const p of Object.values(P))data[p]=fs.readFileSync(path.join(root,p),"utf8");
 const r=run(data);console.log(JSON.stringify(r,null,2));
}

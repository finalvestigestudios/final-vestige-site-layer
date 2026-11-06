/* R160 reproducible static compliance regression.
 * Run: node mind/r160/test_mind_r160.cjs
 * No network access, browser, commercial events or WordPress writes.
 * Source-level compliance checks only: not a substitute for real device/checkout QA.
 */
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const root = __dirname;
const file = name => fs.readFileSync(path.join(root,name), "utf8");
const original = {
 article:file("the-room-that-erased-your-errand-investigation.md"),
 html:file("mind-threshold-evidence-zen12-preview-UNPUBLISHED.html"),
 matrix:JSON.parse(file("verified-claims-offer-authorization-matrix.json")),
 plan:file("one-offer-to-paid-order-funnel-and-grok-fit.md")
};
function validate(p){
 const {article,html,matrix,plan}=p;
 const has=(s,re,m)=>assert.match(s,re,m);
 assert.ok(article.trim().split(/\s+/).length>=2200,"research must be substantive");
 for(const re of [/Radvansky/i,/2006/,/2011/,/2021/,/no significant overall/i,/https:\/\/doi.org\/10\.1186\/s40359-021-00536-3/,/Puységur/,/not.*evidence.*commercial/i])has(article,re,"research context/replication missing");
 assert.ok(/<html lang="en">/.test(html),"language missing");
 has(html,/<meta name="viewport"/,"responsive meta missing");
 has(html,/name="robots" content="noindex,nofollow"/,"noindex hold missing");
 has(html,/@media\(max-width:720px\)/,"mobile CSS missing");
 has(html,/@media\(prefers-reduced-motion:reduce\)/,"reduced-motion support missing");
 has(html,/:focus-visible/,"keyboard focus missing");
 has(html,/<main id="main">/,"landmark missing");
 has(html,/role="img" aria-label=/,"decorative illustration description missing");
 has(html,/42-second.*Storyboard only|42-second.*No media loaded|No media loaded/i,"video must be disclosed as concept");
 has(html,/transcript \/ caption plan/i,"caption/transcript plan missing");
 assert.ok(!/<script\b/i.test(html),"external/inline script forbidden");
 assert.ok(!/<iframe\b/i.test(html),"third-party iframe forbidden");
 assert.ok(!/<form\b/i.test(html),"duplicate signup form forbidden");
 assert.ok(!/<video[^>]+(?:src\s*=|\bautoplay\b)/i.test(html),"unreviewed video/autoplay forbidden");
 assert.ok(!/<a\b[^>]+href\s*=\s*["'][^"']*(zen12\.com|affiliates\.inspire3\.com|awin1\.com)/i.test(html),"unapproved merchant click URL forbidden");
 assert.ok(!/<a\b[^>]+href\s*=\s*["'][^"']*(payhip\.com|checkout)/i.test(html),"unverified paid checkout forbidden");
 assert.ok(/<a[^>]+href="https:\/\/finalvestige\.com\/focus\/"/i.test(html),"existing focus route required");
 const match=html.match(/<p class="disclosure" id="merchant-disclosure">([\s\S]*?)<\/p>\s*<button class="locked"[^>]*>/i);
 assert.ok(match,"disclosure must immediately precede paid button");
 assert.ok(/commission/i.test(match[1]),"plain commission disclosure missing");
 assert.ok(/<button class="locked"[^>]*\bdisabled\b/i.test(html),"purchase control not natively disabled");
 assert.ok(/HARD HOLD/i.test(html),"commercial block not explained");
 assert.ok(/12 levels and 48 MP3s/i.test(html),"exact seller package not described");
 assert.ok(/seller/i.test(html)&&/refund/i.test(html)&&/have not been independently verified|not independently verified/i.test(html),"limits absent");
 assert.equal(matrix.release_status,"HARD_HOLD");
 assert.equal(matrix.affiliate.named_fv_authorization,"UNVERIFIED");
 assert.equal(matrix.affiliate.authorized_affiliate_url,null);
 assert.equal(matrix.affiliate.permissions,null);
 assert.equal(matrix.affiliate.commission_rate,null);
 assert.equal(matrix.affiliate.paid_commissions,null);
 assert.equal(matrix.owned_product_fallback.verified_payhip_sku,null);
 assert.equal(matrix.analytics.net_revenue_per_1000_qualified_human_sessions,null);
 assert.ok(matrix.sources.length>=12,"too few sources");
 assert.ok(matrix.claims.length>=30,"claims not comprehensive");
 assert.ok(matrix.gates.length>=25,"incomplete release gates");
 assert.ok(matrix.gates.every(g=>g.status==="CLOSED"&&g.evidence===null),"unsafe gate open or fabricated evidence");
 const sourceIds=new Set(matrix.sources.map(x=>x.id));
 assert.ok(matrix.claims.every(c=>c.source_ids.length>0&&c.source_ids.every(id=>sourceIds.has(id))),"claim source unresolved");
 has(plan,/net_revenue_per_1000_qualified_human_sessions/,"net metric undefined");
 has(plan,/NOT COMPUTABLE/,"missing data caveat");
 has(plan,/TASK-008/,"Grok coordination missing");
 has(plan,/Variant A/i,"text arm missing");
 has(plan,/Variant B/i,"optional video arm missing");
 has(plan,/affiliate_outbound_click/,"outbound diagnostic missing");
 has(plan,/settled/i,"settlement evidence missing");
 has(plan,/No named FV acceptance/i,"authorization negative missing");
 has(plan,/different pricing/i,"merchant route mismatch undocumented");
 return true;
}
assert.equal(validate(original),true);
const make=(key,fn)=>{const t={...original,matrix:JSON.parse(JSON.stringify(original.matrix))};fn(t);let failed=false;try{validate(t)}catch(e){failed=true}assert.ok(failed,"unsafe mutation escaped "+key)};
const mutations=[
["paid_button_enabled",t=>t.html=t.html.replace(/ type="button" disabled aria-describedby=/,' type="button" aria-describedby=')],
["disclosure_deleted",t=>t.html=t.html.replace(/<p class="disclosure"[\s\S]*?<\/p>/,'')],
["affiliate_link_injected",t=>t.html=t.html.replace("</main>",'<a href="https://affiliates.inspire3.com/?ref=FAKE">Buy</a></main>')],
["checkout_injected",t=>t.html=t.html.replace("</main>",'<a href="https://payhip.com/b/FAKE">Checkout</a></main>')],
["added_script",t=>t.html=t.html.replace("</head>","<script src=\"https://track.example/test.js\"></script></head>")],
["duplicated_email_form",t=>t.html=t.html.replace("</main>","<form><input type=email></form></main>")],
["external_video_iframe",t=>t.html=t.html.replace("</main>",'<iframe src="https://example.com/watch"></iframe></main>')],
["autoplay_video",t=>t.html=t.html.replace("</main>",'<video autoplay></video></main>')],
["noindex_removed",t=>t.html=t.html.replace('noindex,nofollow','index,follow')],
["reduced_motion_removed",t=>t.html=t.html.replace(/@media\(prefers-reduced-motion:reduce\)/,'@media print')],
["existing_focus_cta_removed",t=>t.html=t.html.replace(/href="https:\/\/finalvestige\.com\/focus\/"/g,'href="#offline"')],
["paper_retraction",t=>t.article=t.article.replace(/no significant overall doorway-related forgetting effect/i,'powerful overall doorway forgetting effect')],
["research_citation_removed",t=>t.article=t.article.replace('https://doi.org/10.1186/s40359-021-00536-3','NO_SOURCE')],
["authorization_forged",t=>t.matrix.affiliate.named_fv_authorization="APPROVED"],
["earning_url_forged",t=>t.matrix.affiliate.authorized_affiliate_url="https://example.com/paid"],
["commission_invented",t=>t.matrix.affiliate.commission_rate=0.6],
["paid_revenue_invented",t=>t.matrix.analytics.net_revenue_per_1000_qualified_human_sessions=500],
["opened_gate",t=>t.matrix.gates[0].status="OPEN"],
["unverified_payhip",t=>t.matrix.owned_product_fallback.verified_payhip_sku="FAKE"],
["unsourced_claim",t=>t.matrix.claims[0].source_ids=["NOT_REAL"]],
["measurement_removed",t=>t.plan=t.plan.replaceAll('net_revenue_per_1000_qualified_human_sessions','mere_click_rate')],
["pricing_mismatch_removed",t=>t.plan=t.plan.replace('different pricing','same prices')]
];
for(const [label,mutator] of mutations)make(label,mutator);
console.log("R160 PASS: baseline source gates and "+mutations.length+"/"+mutations.length+" adversarial mutations detected. This is not browser/CI/merchant proof.");
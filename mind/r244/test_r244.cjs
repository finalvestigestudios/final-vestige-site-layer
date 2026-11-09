#!/usr/bin/env node
"use strict";
/* R244 source-level commercial integrity: node mind/r244/test_r244.cjs
 * Read-only; no network, merchant, WP, subscribers, tracking or paid transaction.
 * Git blob IDs pin exact reviewed manuscript/HTML/claim matrix/contract AND R243 baseline.
 * This is a static preflight, NOT browser a11y, security audit or real attribution.
 */
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),assert=require("node:assert/strict");
const home=path.resolve(__dirname,"..");
const paths={
 oldArticle:"r243/THE-PROMISE-BENEATH-THE-PLAY-BUTTON-UNPUBLISHED.md",
 oldHtml:"r243/zen12-canonical-decision-PREVIEW-UNPUBLISHED.html",
 oldMatrix:"r243/CLAIM-PROOF-AND-AUTHORIZATION.json",
 oldPlan:"r243/CONVERSION-AND-QA-ACCEPTANCE.md",
 article:"r244/THE-CHOICE-THAT-CAME-BACK-CHANGED-UNPUBLISHED.md",
 html:"r244/zen12-choice-ledger-WP-SOURCE-UNPUBLISHED.html",
 matrix:"r244/CHOICE-BLINDNESS-CLAIMS-RELEASE-GATES.json",
 plan:"r244/OFFER-FUNNEL-QA-ATTRIBUTION-CORRECTIONS.md"
};
const pins={
 oldArticle:"bee5b63a29611b39d04ba492bdb038a0df2c277a",
 oldHtml:"c8e4e259d62f1158e45e82050d39d14346bb9dfc",
 oldMatrix:"e1c22f5576837e5e45cbcee9ae8feeedecc15f11",
 oldPlan:"f57cc5950774ec7fe2b7bff6d16d6d8a63a32e71",
 article:"1fcc40f86dddd7d9111bb41b60fdcd0885561ec4",
 html:"9ee807775082e4253d4d8daabb4797fe40db6dd3",
 matrix:"0bd42d72e7f8d6f794baa92550b8b573910371e4",
 plan:"bed11deaea6d4bd0ea6eb16f80ae30e41e6474a8"
};
const read=k=>fs.readFileSync(path.join(home,paths[k]),"utf8");
function blob(t){let b=Buffer.from(t,"utf8");return crypto.createHash("sha1").update(Buffer.from("blob "+b.length+"\0")).update(b).digest("hex")}
const data=Object.fromEntries(Object.keys(paths).map(k=>[k,read(k)]));
for(const k of Object.keys(paths))assert.equal(blob(data[k]),pins[k],"Pinned source drift "+paths[k]);
function clone(){return{...data,matrix:JSON.parse(data.matrix),oldMatrix:JSON.parse(data.oldMatrix)}}
const requiredGateIds=["named_publisher_acceptance","issued_earning_url","website_permission","organic_social_permission","email_permission","approved_creatives_rights","checkout_amount_confirmed","refund_fulfillment_terms_verified","paid_commission_terms","independent_claim_substantiation_or_removal","exact_product_match","adjacent_disclosure_browser_checked","no_duplicated_jetpack_list","creator_asset_id_verified","confirmed_order_or_commission_reporting","founder_release_authorization"];
function checkMatrix(m){
 assert.equal(m.milestone,244);assert.equal(m.status,"HARD_HOLD");
 assert.equal(m.source_count,15);assert.equal(m.claim_count,20);assert.equal(m.gate_count,16);
 assert.equal(m.sources.length,15);assert.equal(m.claims.length,20);assert.equal(m.gates.length,16);
 const sids=m.sources.map(s=>s.id),cids=m.claims.map(c=>c.id),gids=m.gates.map(g=>g.id);
 assert.equal(new Set(sids).size,15,"source IDs unique");
 assert.equal(new Set(cids).size,20,"claim IDs unique");
 assert.equal(new Set(gids).size,16,"gate IDs unique");
 assert.deepEqual(gids,requiredGateIds,"cannot replace release gates with different IDs");
 for(const s of m.sources){assert.ok(/^https:\/\//.test(s.url),"real HTTPS provenance");assert.ok(/^[A-Z0-9]+$/.test(s.id));assert.ok(s.kind)}
 for(const c of m.claims){assert.ok(sids.includes(c.source),"every claim must cite source ID");assert.ok(c.claim.length>=22);assert.ok(c.status);assert.ok(!/verified_efficacy|proven_cure|guaranteed_effect/i.test(c.status))}
 assert.ok(m.claims.some(c=>c.claim.includes("69%")&&c.source==="H12"));
 assert.ok(m.claims.some(c=>c.source==="ZEN"&&c.status==="not_independently_substantiated"));
 assert.ok(m.gates.every(g=>g.status==="HARD_HOLD"&&g.verified===false));
 const f=m.commercial;
 assert.equal(f.enabled,false);assert.equal(f.affiliate_url,null);assert.equal(f.named_partner_approval,null);
 for(const k of ["paid_orders","cleared_commissions","qualified_human_sessions"])assert.equal(f[k],null);
 assert.equal(f.net_revenue_per_1000,"NOT_COMPUTABLE");
 assert.equal(f.merchant_cart_tested,false);assert.equal(f.refund_issued_tested,false);assert.equal(f.owned_mind_sku_authenticated,false);
 return true;
}
function checkHtml(s){
 for(const tag of ["script","iframe","form","input","video","audio","object","embed","link","base"]){assert.ok(!new RegExp("<\\s*"+tag+"\\b","i").test(s),"prohibited active/capture tag: "+tag)}
 assert.ok(!/\bon[a-z]{3,}\s*=/i.test(s),"inline handlers blocked");
 assert.ok(!/\b(?:javascript|data|vbscript|file)\s*:/i.test(s),"unsafe URL scheme blocked");
 assert.ok(!/\b(?:srcdoc|formaction|action)\s*=/i.test(s),"hidden navigation blocked");
 assert.ok(!/url\s*\(/i.test(s),"no CSS remote resource");
 const anchors=[...s.matchAll(/<a\b([^>]*)>/gi)];
 assert.ok(anchors.length>=3,"working free links");
 for(const a of anchors){const match=a[1].match(/\bhref\s*=\s*(["'])(.*?)\1/i);assert.ok(match,"quoted anchor href mandatory");
 const href=match[2]; assert.ok(/^https:\/\//.test(href),"no scheme-relative or nonHTTPS link"); const u=new URL(href);
 assert.equal(u.hostname,"finalvestige.com","only existing first-party destinations");
 assert.equal(u.username,"");assert.equal(u.password,"");
 assert.ok(!/[?&](?:email|token|session_id|user_id)=/i.test(u.search),"no PII in URLs");
 }
 assert.ok(!/<a\b[^>]*\bhref\s*=\s*[^"']/i.test(s),"unquoted href disallowed");
 const buttons=[...s.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/gi)];
 assert.equal(buttons.length,1,"one sole held commerce control");
 assert.match(buttons[0][1],/\sdisabled(?:\s|=|$)/i,"native disabled required");
 assert.match(buttons[0][1],/\btype="button"/,"non-submit only");
 assert.match(buttons[0][1],/aria-describedby="mind244-disclosure mind244-hold"/);
 const disclosure=s.indexOf('id="mind244-disclosure"'),button=s.indexOf(buttons[0][0]);
 assert.ok(disclosure>=0&&button>disclosure&&button-disclosure<900,"adjacent disclosure preceding button");
 const segment=s.slice(disclosure,button);
 for(const k of ["may earn a commission","at no additional cost","No earning link is active"]) assert.ok(segment.includes(k),"clear near-link disclosure: "+k);
 assert.ok(s.includes('id="mind244-hold"'));assert.ok(s.includes("HARD HOLD"));
 assert.ok(s.includes("https://finalvestige.com/focus/"),"preserved single Focus path");
 assert.ok(s.includes('role="img"')&&s.includes('<desc'),"original accessible poster");
 assert.ok(s.includes("<details>")&&s.includes("<summary>"),"optional no-JS storyboard");
 assert.ok(s.includes("not a video")&&s.includes("No film has been rendered"),"no fabricated rendered asset");
 assert.ok(s.includes(":focus-visible")&&s.includes("prefers-reduced-motion")&&s.includes("max-width"),"a11y CSS");
 assert.ok(s.includes('noindex,nofollow'),"unpublished noindex");
 assert.ok(!/<(?:video|audio)\b[^>]*\bautoplay\b/i.test(s),"no autoplay attribute");
 return true;
}
function checkEditorial(a,p){
 for(const k of ["The Choice That Came Back Changed","choice blindness","Johansson","Hall","2010","69%","not estimates","not prove","UNPUBLISHED","**Editorial separation:**","https://zen12.com/hnp"])assert.ok(a.includes(k),"required scientific caveat or source: "+k);
 assert.ok(a.includes("https://pubmed.ncbi.nlm.nih.gov/16210542/"));
 assert.ok(a.includes("https://pubmed.ncbi.nlm.nih.gov/20637455/"));
 assert.ok(a.includes("https://doi.org/10.1371/journal.pone.0045457"));
 assert.ok(p.includes("R243 plan inaccurately says R243 suite pins R241 article"));
 assert.ok(p.includes("incremental attributable"));
 assert.ok(p.includes("not already netted"));
 assert.ok(p.includes("aren't deducted twice"));
 assert.ok(p.includes("NOT_COMPUTABLE")&&p.includes("HARD_HOLD"));
 assert.ok(p.includes("Grok + Praxxis")&&p.includes("Claude + Site QA"));
 assert.ok(p.includes("UNPUBLISHED")&&p.includes("PR #172")||p.includes("PR#172"));
 return true;
}
function verify(v){checkMatrix(v.matrix);checkHtml(v.html);checkEditorial(v.article,v.plan);assert.equal(v.oldMatrix.commercial.enabled,false);return true}
verify(clone());
let rejected=0;
function bad(label,change){const v=clone();change(v);assert.throws(()=>verify(v),undefined,label);rejected++}
bad("merchant anchor",v=>v.html+='<a href="https://zen12.com/hnp">Buy</a>');
bad("scheme-relative",v=>v.html+='<a href="//zen12.com/">Open</a>');
bad("unquoted href",v=>v.html+='<a href=https://finalvestige.com/focus/>Free</a>');
bad("unsafe JS",v=>v.html+='<a href="javascript:alert(1)">Hack</a>');
bad("data URL",v=>v.html+='<a href="data:text/html,x">Hack</a>');
bad("outside merchant redirect",v=>v.html+='<a href="https://payhip.com/">Shop</a>');
bad("tracking pixel",v=>v.html+='<script src="https://x.example/pixel.js"></script>');
bad("duplicate signup",v=>v.html+='<form><input type="email"></form>');
bad("tracking CSS",v=>v.html+='<style>p{background:url(https://x.example/t)}</style>');
bad("active button",v=>v.html=v.html.replace('type="button" disabled','type="button"'));
bad("aria-disabled bypass",v=>v.html=v.html.replace('type="button" disabled','type="button" aria-disabled="true"'));
bad("second button",v=>v.html+='<button type="button">Pay</button>');
bad("lost disclosure",v=>v.html=v.html.replace("may earn a commission","could help"));
bad("disclosure far away",v=>v.html=v.html.replace('id="mind244-disclosure"','id="broken-disclosure"'));
bad("PII URL",v=>v.html=v.html.replace("https://finalvestige.com/focus/","https://finalvestige.com/focus/?email=a%40b.test"));
bad("autoplay",v=>v.html+='<audio autoplay></audio>');
bad("lost noindex",v=>v.html=v.html.replace('noindex,nofollow','index,follow'));
bad("false rendered video",v=>v.html=v.html.replace("No film has been rendered","Video was produced"));
bad("fabricated order",v=>v.matrix.commercial.paid_orders=10);
bad("fabricated revenue",v=>v.matrix.commercial.net_revenue_per_1000=100);
bad("activates affiliate",v=>v.matrix.commercial.affiliate_url="https://example.com/aff");
bad("alter gate",v=>v.matrix.gates[1].status="PASS");
bad("alter gate verification",v=>v.matrix.gates[2].verified=true);
bad("gate identity swap",v=>v.matrix.gates[1].id="some_new_gate");
bad("duplicate source",v=>v.matrix.sources[0].id=v.matrix.sources[1].id);
bad("duplicate claim",v=>v.matrix.claims[0].id=v.matrix.claims[1].id);
bad("orphan source",v=>v.matrix.claims[0].source="NOT_A_SOURCE");
bad("source removal",v=>v.matrix.sources.pop());
bad("claims removal",v=>v.matrix.claims.pop());
bad("false efficacy",v=>v.matrix.claims[6].status="verified_efficacy");
bad("article journal scope",v=>v.article=v.article.replace("69%","every participant"));
bad("article study citation",v=>v.article=v.article.replace("16210542","00000000"));
bad("accounting double subtraction",v=>v.plan=v.plan.replace("not already netted","always subtracted"));
bad("incremental costs missing",v=>v.plan=v.plan.replace("incremental attributable","all historical"));
bad("fabricated media",v=>v.plan=v.plan.replace("NOT verified published Grok videos","fully verified live assets"));
console.log("PASS R244 8 exact Git-blob pins; source and offer baseline; "+rejected+"/"+rejected+" deliberate unsafe modifications rejected. SOURCE LEVEL ONLY: not browser, native staging, WordPress, merchant, payouts or production.");

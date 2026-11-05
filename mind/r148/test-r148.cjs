/* R148 exact-source negative-gate checks. Run from branch checkout with:
   node mind/r148/test-r148.cjs
   No remote dependencies, requests, CMS writes or credentials.
*/
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const here = __dirname;
const read = (name) => fs.readFileSync(path.join(here, name),"utf8");
const html=read("zen12-premium-buyer-agency-presell-UNPUBLISHED.html");
const article=read("choice-blindness-and-buyer-agency-investigation.md");
const contract=read("conversion-acceptance-and-partner-evidence-packet.md");
const evidence=JSON.parse(read("claim-source-offer-gates.json"));
let passed=0;
function check(name, predicate){ assert.equal(Boolean(predicate()),true,name); passed++; console.log("PASS",name); }
function merchantDisabled(h){
  const open=[...h.matchAll(/<button\b([^>]*)>/gi)].map(x=>x[1]);
  return open.length===1 && open.every(attrs=>/\sdisabled(?:\s|=|$)/i.test(attrs)) && !/href=["'][^"']*(?:affiliat|clickbank|hop=|subid=|partnerid=)/i.test(h);
}
function disclosureNextToButton(h){
  const block=(h.match(/<div class="money">([\s\S]*?)<\/div>/i)||[])[1]||"";
  return /If you purchase through this link, Final Vestige may earn a commission at no additional cost to you\./.test(block)
    && /<button[^>]*\sdisabled\b/i.test(block)
    && block.indexOf("If you purchase") < block.indexOf("<button");
}
function noInjectedActive(h){
  return !/<(?:script|iframe|form|video|audio|input)\b/i.test(h)
  && !/<a\b[^>]*href=["'][^"']*\?(?:[^"']*&)?(?:ref|aff|hop|subid|aid)=/i.test(h)
  && !/on(?:load|click|error|submit)\s*=/i.test(h);
}
check("article exact original 2005 primary study",()=>article.includes("https://pubmed.ncbi.nlm.nih.gov/16210542/"));
check("article exact 2010 consumer study",()=>article.includes("https://pubmed.ncbi.nlm.nih.gov/20637455/"));
check("article correct author attribution",()=>article.includes("Betty Tärning") && article.includes("Thérèse Deutgen"));
check("article careful 2010 manipulated-trial denominator",()=>article.includes("no more than one third") && article.includes("manipulated experimental trials"));
check("article recognizes study limits and no product evidence",()=>article.includes("never tested Zen12 Premium") && article.includes("does not constitute an endorsement"));
check("article preserves historical caveat",()=>article.includes("Puységur did not discover the modern choice-blindness mechanism"));
check("article no earning link nor sales CTA",()=>!/(?:affiliates\.inspire3\.com\/[^\s)]+\?|utm_content=)/i.test(article));
check("article respects free Focus route",()=>article.includes("https://finalvestige.com/focus/"));
check("presell is fully unpublished",()=>html.includes("data-release=\"HARD_HOLD\"") && html.includes("data-merchant-authorized=\"false\""));
check("prospective button really disabled, not just ARIA",()=>merchantDisabled(html));
check("single disabled button",()=>(html.match(/<button\b/gi)||[]).length===1);
check("immediate FTC disclosure in merchant box",()=>disclosureNextToButton(html));
check("no remote scripts, forms, media or tracking",()=>noInjectedActive(html));
check("one existing free signup destination",()=>html.includes('href="https://finalvestige.com/focus/"'));
check("exact Zen12 Premium product named",()=>html.includes("Zen12 Premium") && html.includes("48 MP3 recordings"));
check("same-SKU seller source as citation",()=>html.includes('href="https://zen12.com/hnp"'));
check("explicit no proven product outcome",()=>html.includes("It did not test Zen12") && html.includes("We have not listened to or personally tested Zen12 Premium"));
check("no magic hour in 12 efficacy claim",()=>html.includes("do not endorse") && html.includes("one hour in 12 minutes"));
check("refund guarantee labeled seller claim",()=>html.includes("advertised one-year money-back guarantee"));
check("checkout amount not falsely guaranteed",()=>html.includes("not a guaranteed current purchase price"));
check("privacy seller source documented",()=>html.includes("https://inspire3.com/privacy/"));
check("meaningful mobile single-column layout",()=>html.includes("grid-template-columns:minmax(0,1fr)"));
check("keyboard focus visible",()=>html.includes(":focus-visible"));
check("responsive desktop layout",()=>html.includes("@media(min-width:780px)"));
check("honors reduced motion",()=>html.includes("prefers-reduced-motion:reduce"));
check("published article not invented",()=>html.includes("Do not link to a nonexistent public article"));
check("merchant product not treated as trial",()=>html.includes("It did not test Zen12."));
check("source matrix readable",()=>evidence.schema==="fv-mind-evidence-v1");
check("source matrix minimum 16 references",()=>evidence.sources.length>=16);
check("source matrix minimum 30 decisions",()=>evidence.claims.length>=30);
check("source matrix claims linked to actual source IDs",()=>{const ids=new Set(evidence.sources.map(x=>x.id));return evidence.claims.every(x=>x.source_ids.every(id=>ids.has(id)));});
check("source matrix all unique claim IDs",()=>new Set(evidence.claims.map(x=>x.id)).size===evidence.claims.length);
check("source matrix only closed gates",()=>evidence.gates.length>=27 && evidence.gates.every(x=>x.open===false));
check("authorization not fabricated",()=>evidence.offer.named_partner_approval===null && evidence.offer.authorized_affiliate_url===null);
check("no fabricated settled money",()=>evidence.kpi.status==="NOT_COMPUTABLE" && evidence.kpi.result===null);
check("7 and 30-day cohorts",()=>[7,30].every(n=>evidence.kpi.windows_days.includes(n)));
check("3 creator topic paths, zero invented Grok media",()=>evidence.creator_to_product.length===3 && evidence.creator_to_product.every(x=>x.asset_id===null));
check("events do not misclassify clicks as sales",()=>evidence.events.filter(x=>/click|landing|signup/.test(x.event)).every(x=>x.paid_sale===false));
check("paid event requires merchant authority",()=>evidence.events.some(x=>x.event==="merchant_confirmed_paid_order" && x.paid_sale));
check("commissions are distinct from affiliate clicks",()=>evidence.events.some(x=>x.event==="affiliate_commission_settled" && x.paid_sale));
check("commercial governance records named owners",()=>contract.includes("Founder / Mind") && contract.includes("Praxxis / Grok") && contract.includes("Site QA / Founder"));
check("controlled A/B is not active",()=>contract.includes("poster/captions/transcript storyboard only") && html.includes('data-experiment="inactive"'));
check("no duplicate measurement, email or CMS",()=>contract.includes("no new script") && !/<form\b/i.test(html));
const mutantChecks=[
["enabled HTML purchase button",()=>!merchantDisabled(html.replace(/(<button\b[^>]*?)\sdisabled\b/i,"$1"))],
["deleted proximate affiliate disclosure",()=>!disclosureNextToButton(html.replace("If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.",""))],
["injected external script",()=>!noInjectedActive(html+"<script src='https://example.net/tracker.js'></script>")],
["injected signup form",()=>!noInjectedActive(html+"<form><input type=email></form>")],
["fabricated affiliate earning link",()=>!merchantDisabled(html+'<a href="https://zen12.com/?aff=FAKE">Buy now</a>')],
["opened authorization without proof",()=>!html.includes('data-merchant-authorized="true"') && evidence.gates.every(x=>!x.open)],
["injected iframe player",()=>!noInjectedActive(html+'<iframe src="https://example.net"></iframe>')],
["invented sale outcome",()=>evidence.kpi.result===null && evidence.offer.paid_orders_verified===null]
];
for(const [name,pred] of mutantChecks) check("negative mutation detected: "+name,pred);
console.log("TOTAL PASS",passed,"checks. Test is structural only; no browser, CI, real buyer or live funnel asserted.");

/* Final Vestige Mind R153 — no network/no CMS/no third-party packages.
   Reproduce in repository root: node mind/r153/test_mind_r153.cjs
   Authoritative inputs: exact Git files on the same branch; intentionally bad
   fixtures MUST fail to prevent disabled-button/disclosure/gate regressions. */
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const dir = __dirname;
const inputs = {
  article: fs.readFileSync(path.join(dir, "unfinished-task-attention-residue-investigation.md"), "utf8"),
  html: fs.readFileSync(path.join(dir, "focus-return-note-affiliate-slot-REVIEW-ONLY.html"), "utf8"),
  decision: fs.readFileSync(path.join(dir, "one-offer-conversion-first-acceptance.md"), "utf8"),
  matrix: fs.readFileSync(path.join(dir, "source-claim-release-gates.json"), "utf8")
};
let checks = 0;
function check(condition, message) { checks++; assert.ok(condition, message); }
function review(a) {
  const fail = [];
  const want = (condition, message) => { if (!condition) fail.push(message); };
  const {article, html, decision} = a;
  let data;
  try {data = JSON.parse(a.matrix);} catch(e) {return ["malformed JSON"];}

  want(article.includes("The Unfinished Task That Followed You Into the Next Room"), "original title missing");
  want((article.match(/\b[\w'-]+\b/g)||[]).length >= 1900, "article insufficient depth");
  want(article.includes("UNPUBLISHED"), "publication hold absent");
  want(article.includes("Leroy") && article.includes("Glomb"), "primary researchers missing");
  want(article.includes("https://doi.org/10.1287/orsc.2017.1184"), "primary 2018 paper absent");
  want(article.includes("https://doi.org/10.1016/j.obhdp.2009.04.002"), "2009 primary paper absent");
  want(article.includes("https://doi.org/10.1037/0096-1523.27.4.763"), "switch experiment absent");
  want(article.includes("did **not** test"), "important studied limit absent");
  want(article.includes("not a clinical intervention") || article.includes("not a clinical intervention"), "exercise warning absent");
  want(article.includes("https://finalvestige.com/focus/"), "free resource absent");
  want(article.includes("puysegurs-animal-magnetism-files"), "historical connection absent");
  want(!/href=.{0,30}(?:hypnosislive|affiliates\.inspire3)/i.test(article), "article must not endorse merchant");
  want(!/(?:we|final vestige) (?:guarantee|promise) (?:focus|results|wealth|health)/i.test(article), "unqualified guarantee");

  want(html.includes('data-release="HARD_HOLD"'), "review-only release gate absent");
  want(html.includes('data-merchant-approval="UNVERIFIED"'), "falsified partner approval");
  want(/<button\b[^>]*\sdisabled(?:\s|>|=)/i.test(html), "physically disabled button absent");
  want(!/<button\b[^>]*\saria-disabled="true"[^>]*>/.test(html) || /<button\b[^>]*\sdisabled(?:\s|>|=)/i.test(html), "ARIA-only disabled false positive");
  want(html.includes("Final Vestige could earn a commission"), "financial disclosure absent");
  want(html.includes("No earning link is active"), "inactive-earning statement absent");
  want(html.includes('id="fv-mind-r153-disclosure"'), "adjacent disclosure id absent");
  want(/aria-describedby="fv-mind-r153-disclosure fv-mind-r153-gate"/.test(html), "button not bound to disclosure");
  want(html.indexOf("Commercial relationship disclosure") < html.indexOf("<button"), "disclosure must precede prospective button");
  want(!/<script\b/i.test(html), "external or inline script forbidden");
  want(!/<form\b/i.test(html), "duplicate Jetpack form forbidden");
  want(!/<iframe\b|<video\b[^>]*autoplay/i.test(html), "embed/autoplay forbidden");
  want(!/href=["'][^"']*(?:hypnosislive|affiliates\.inspire3|payhip\.com)/i.test(html), "unapproved merchant earning link");
  want((html.match(/href="https:\/\/finalvestige\.com\/focus\/"/g)||[]).length === 1, "one existing first-party lead destination");
  want(html.includes("prefers-reduced-motion:reduce"), "reduced motion handling missing");
  want(html.includes("focus-visible"), "keyboard focus missing");
  want(html.includes("min-height:52px"), "tap target missing");
  want(html.includes("grid-template-columns:minmax(0,1fr)"), "small-width layout missing");
  want(html.includes("independently substantiated"), "independent-benefit limit missing");
  want(html.includes("33-minute") && html.includes("47 MB"), "exact SKU mismatch");

  want(decision.includes("NOT COMPUTABLE"), "explicit missing denominator outcome absent");
  want(decision.includes("TASK-008"), "Grok ownership coordination absent");
  want(decision.includes("UNKNOWN") && decision.includes("Payhip"), "owned fallback uncertainty absent");
  want(decision.includes("Issue") || decision.includes("Issue #"), "issue scope absent");
  want(decision.includes("No exact earning URL"), "commercial prohibition absent");
  want(decision.includes("jetpack_confirmed_signup"), "confirmed lead distinct from click");
  want(decision.includes("affiliate_outbound"), "click event specification absent");
  want(decision.includes("merchant_confirmed_order"), "paid event specification absent");
  want(decision.includes("refund"), "net-revenue reconciliation absent");
  want(decision.includes("2026-11-05"), "date of seller check absent");

  want(Array.isArray(data.sources) && data.sources.length >= 12, "source registry too shallow");
  want(Array.isArray(data.claims) && data.claims.length >= 20, "claim registry too shallow");
  want(Array.isArray(data.gates) && data.gates.length >= 20, "release gates missing");
  want(data.gates.every(g => g.status === "CLOSED"), "release gate opened without permission");
  want(data.primary_candidate.partner_approved === false, "partner approved without proof");
  want(data.primary_candidate.purchase_enabled === false, "merchant action unexpectedly enabled");
  want(data.primary_candidate.partner_url === null, "forbidden earning URL introduced");
  want(data.measurement.settled_net_revenue_per_1000_humans === "NOT_COMPUTABLE", "invented revenue");
  want(data.measurement.affiliate_click_is_sale === false, "click reclassified as sale");
  want(new Set(data.sources.map(s=>s.id)).size === data.sources.length, "duplicate sources");
  want(new Set(data.claims.map(c=>c.id)).size === data.claims.length, "duplicate claims");
  want(data.claims.every(c => c.source_ids.every(s=>data.sources.some(x=>x.id===s))), "orphan source reference");
  want(data.claims.some(c=>c.decision==="unsubstantiated_seller_claim"), "seller efficacy not flagged");
  return fail;
}
const defects=review(inputs); check(defects.length===0, "Source failures: "+defects.join("; "));
const cases = [
  ["physically enabled merchant control", x=>{x.html=x.html.replace('type="button" disabled', 'type="button"');}],
  ["disclosure deletion", x=>{x.html=x.html.replace("Final Vestige could earn a commission","We have no disclosures");}],
  ["hidden merchant href", x=>{x.html=x.html.replace("</section>", '<a href="https://affiliates.inspire3.com/track?ref=secret">Buy now</a></section>');}],
  ["unapproved third party script", x=>{x.html += "<script src=\"https://example.invalid/tag.js\"></script>";}],
  ["duplicate optin form", x=>{x.html += '<form action="https://example.invalid"><input type="email"></form>'; }],
  ["partner gate falsely opened", x=>{x.html=x.html.replace('data-merchant-approval="UNVERIFIED"','data-merchant-approval="VERIFIED"');}],
  ["machine release gates opened", x=>{let j=JSON.parse(x.matrix);j.gates[0].status="OPEN";x.matrix=JSON.stringify(j);}],
  ["invented merchant settlement", x=>{let j=JSON.parse(x.matrix);j.measurement.settled_net_revenue_per_1000_humans=1234;x.matrix=JSON.stringify(j);}],
  ["fake paid conversion from affiliate click", x=>{let j=JSON.parse(x.matrix);j.measurement.affiliate_click_is_sale=true;x.matrix=JSON.stringify(j);}],
  ["shortened article without evidence", x=>{x.article="A short claim about focus."; }],
  ["missing source in matrix", x=>{let j=JSON.parse(x.matrix);j.sources=j.sources.filter(s=>s.id!=="S01");x.matrix=JSON.stringify(j);}]
];
let killed=0;
for (const [label,mutate] of cases) {
  const x={...inputs}; mutate(x);
  const result=review(x); check(result.length>0, "FAIL: mutation escaped test: "+label);
  killed++;
}
console.log("FV Mind R153: "+checks+" top-level checks PASS; "+killed+"/"+cases.length+" adversarial mutations rejected.");

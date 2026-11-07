/* Mind R181 source-only regression suite.
   Runnable: node mind/r181/test_mind_r181.cjs
   Reads ONLY repository working-tree source; no network, no browser, no CMS writes.
   Exports verify(files) for independent readback/V8 execution with exact committed content.
*/
"use strict";
function verify(files) {
  const checks=[];
  function check(label, pass) { checks.push({label,pass:!!pass}); }
  const article=files.article, a=files.a, b=files.b, hub=files.hub, plan=files.plan, matrix=JSON.parse(files.matrix);
  const source=[a,b,hub,article,plan];
  check("all specified artifacts present",source.every(x=>typeof x==="string"&&x.length>1000));
  check("deep original investigation",article.split(/\s+/).length>=2000);
  check("1999 primary DOI",article.includes("10.1068/p281059"));
  check("2010 primary open text",article.includes("PMC3563049"));
  check("2013 expert n24 and 83% reported correctly",/Twenty-four radiologists/.test(article)&&/83%/.test(article));
  check("choice blindness separate research",article.includes("10.1126/science.1111709")||article.includes("16210542"));
  check("no article purchasing button",!/<button/i.test(article));
  check("article research-to-product inferential boundary",article.includes("not a clinical trial")&&article.includes("no responsible article can claim that Zen12"));
  check("claim register includes 18 source links",matrix.sources.length>=18);
  check("claim register includes at least 24 decisions",matrix.claims.length>=24);
  check("claim register includes 12 gates",matrix.gates.length>=12);
  check("acceptance must be false",matrix.affiliate_acceptance_verified===false);
  check("earning url must be null",matrix.verified_affiliate_earning_url===null);
  check("channel permission must be false",matrix.allowed_channel_terms_verified===false);
  check("no paid transactions implied",matrix.verified_paid_orders===null&&matrix.realized_net_revenue_usd===null);
  check("qualified human denominator must remain unknown",matrix.qualified_human_sessions===null);
  check("owned paid SKU must remain unverified",matrix.verified_owned_paid_mind_product===null);
  check("closed approval and checkout gates included",matrix.gates.some(g=>g.id==="G01"&&g.state==="HARD_HOLD")&&matrix.gates.some(g=>g.id==="G04"&&g.state==="UNVERIFIED"));
  check("no active CTA declared in ledger",matrix.enabled_purchase_cta===false);
  check("seller outcomes not treated as evidence",matrix.claims.some(c=>c.id==="C06"&&c.evidence_status==="UNSUBSTANTIATED_PRODUCT_EFFICACY"));
  check("price observation not final checkout",matrix.checkout_currency_fees_taxes_unknown===true);
  for (const [id,html] of [["A",a],["B",b]]) {
    check(id+" HTML semantic document",/<!doctype html>/i.test(html)&&/<main id="content">/.test(html)&&/<h1>/.test(html));
    check(id+" no-JS no tracking/embed",!/<script\b|<iframe\b|<form\b|\bgtag\s*\(|\bfbq\s*\(/i.test(html));
    check(id+" native disabled merchant control",/<button\s+class="disabled"\s+type="button"\s+disabled\s+aria-describedby="commercial-hold"/i.test(html));
    check(id+" direct offer disclosure adjacent to button",(() => {const p=html.indexOf('id="offer"'),d=html.indexOf('class="disclosure"',p),btn=html.indexOf('<button class="disabled"',p);return p>=0&&d>p&&btn>d&&btn-d<750&&html.slice(d,btn).includes("may earn a commission")})());
    check(id+" no commercial earning href",!/(href\s*=\s*["'][^"']*(?:awin1\.com|clkbank|clickbank|affiliate_id=|aff_id=|affiliate\.inspire3))/i.test(html));
    check(id+" no active merchant CTA anchors",!/<a\s+[^>]*class=["'][^"']*(?:purchase|buy-now|offer-cta)[^"']*["'][^>]*href=/i.test(html));
    check(id+" useful free Focus resource",html.includes('href="https://finalvestige.com/focus/"'));
    check(id+" explicit seller vs research limits",html.includes("None of these experiments tested Zen12")&&html.includes("seller's promotion"));
    check(id+" visible informational seller citation distinct from earning link",html.includes('href="https://zen12.com/"')&&html.includes("informational, not an affiliate link"));
    check(id+" no video/audio autoplay",!/<(?:video|audio)\b[^>]*\bautoplay\b/i.test(html));
    check(id+" inline mobile CSS and focus",html.includes("max-width:390px")&&html.includes(":focus-visible"));
    check(id+" reduced-motion treatment",html.includes("prefers-reduced-motion"));
    check(id+" no active email capture",!/<(?:form|input)\b/i.test(html));
  }
  check("B is poster-only no pretend playable video",b.includes('id="optional-film"')&&b.includes("non-playing storyboard")&&!/<video\b/i.test(b));
  check("A lacks extra optional film",!a.includes('id="optional-film"'));
  check("A and B otherwise identical",b.replace(/<section class="section" id="optional-film"[\s\S]*?<\/section>\n/,"\n")===a);
  check("mind hub has all four streams",["Perception & Attention","History of Suggestion","Practice & Reflection","Tools Under Review"].every(k=>hub.includes(k)));
  check("hub no duplicate list or script",!/<form\b|<script\b|<iframe\b/i.test(hub));
  check("hub labels new article unpublished",hub.includes("NEW research draft, not linked as published"));
  check("hub focus original destination",hub.includes("https://finalvestige.com/focus/"));
  check("hub no active commerce href",!hub.includes('href="https://zen12.com/"'));
  check("plan paid conversion excludes click equivalence",plan.includes("A click cannot prove revenue")&&plan.includes("NOT COMPUTABLE"));
  check("plan preserves negative revenue and refund netting",plan.includes("Do not censor a negative numerator")&&plan.includes("not already netted"));
  check("plan preserves founder release and cross-team ownership",plan.includes("homepage PR #49")&&plan.includes("art Issue #150")&&plan.includes("canonical Mind hub PR #172")&&plan.includes("Dispatch"));
  check("no known product price represented as checkout",plan.includes("checkout and refunds untested"));
  return {passed:checks.filter(c=>c.pass).length,total:checks.length,failures:checks.filter(c=>!c.pass).map(c=>c.label)};
}
function mutations(files) {
  const m=[
    f=>({...f,a:f.a.replace('type="button" disabled','type="button"')}),
    f=>({...f,b:f.b.replace('type="button" disabled','type="button"')}),
    f=>({...f,a:f.a.replace('class="disclosure"','class="missing-disclosure"')}),
    f=>({...f,b:f.b.replace('may earn a commission','is never paid')}),
    f=>({...f,a:f.a.replace("</main>",'<script src="https://track.example.com/tag.js"></script></main>')}),
    f=>({...f,b:f.b.replace("</main>","<form><input type=email></form></main>")}),
    f=>({...f,a:f.a.replace("</main>",'<a class="buy-now" href="https://zen12.com/">Buy!</a></main>')}),
    f=>({...f,b:f.b.replace("</main>",'<a href="https://www.awin1.com/?aff_id=123">Buy!</a></main>')}),
    f=>({...f,a:f.a.replace("</main>",'<video autoplay></video></main>')}),
    f=>({...f,b:f.b.replace("</main>",'<iframe src="https://example.com/ad"></iframe></main>')}),
    f=>({...f,a:f.a.replace('https://finalvestige.com/focus/','https://example.com/subscription/')}),
    f=>({...f,b:f.b.replace('https://finalvestige.com/focus/','https://example.com/subscription/')}),
    f=>({...f,hub:f.hub.replace("</main>","<form><input type=email></form></main>")}),
    f=>({...f,hub:f.hub.replace("NEW research draft, not linked as published","LIVE NOW")}),
    f=>({...f,matrix:f.matrix.replace('"affiliate_acceptance_verified": false','"affiliate_acceptance_verified": true')}),
    f=>({...f,matrix:f.matrix.replace('"verified_affiliate_earning_url": null','"verified_affiliate_earning_url": "https://fake.test"')}),
    f=>({...f,matrix:f.matrix.replace('"enabled_purchase_cta": false','"enabled_purchase_cta": true')}),
    f=>({...f,matrix:f.matrix.replace('"verified_paid_orders": null','"verified_paid_orders": 1')}),
    f=>({...f,matrix:f.matrix.replace('"qualified_human_sessions": null','"qualified_human_sessions": 50')}),
    f=>({...f,matrix:f.matrix.replace('"verified_owned_paid_mind_product": null','"verified_owned_paid_mind_product": "test"')}),
    f=>({...f,plan:f.plan.replace("Do not censor a negative numerator","Convert negative numerator to zero")}),
    f=>({...f,article:f.article.replace("10.1068/p281059","wrong citation")}),
    f=>({...f,article:f.article.replace("83%","100%")}),
    f=>({...f,b:f.b.replace('id="optional-film"','id="fake-film"')})
  ];
  const caught=m.filter(fn=>verify(fn(files)).failures.length>0).length;
  return {caught,total:m.length,all_detected:caught===m.length};
}
if(typeof module !== "undefined") module.exports={verify,mutations};
if(typeof require!=="undefined" && require.main===module){
 const fs=require("node:fs"),path=require("node:path"),dir=__dirname;
 const load=(f)=>fs.readFileSync(path.join(dir,f),"utf8");
 const files={
  article:load("the-gorilla-the-expert-and-the-unseen-INVESTIGATION-UNPUBLISHED.md"),
  a:load("zen12-premium-A-text-only-UNPUBLISHED.html"),
  b:load("zen12-premium-B-optional-video-storyboard-UNPUBLISHED.html"),
  hub:load("mind-archive-four-stream-WORDPRESS-PREVIEW-UNPUBLISHED.html"),
  matrix:load("verified-product-claims-and-activation-gates.json"),
  plan:load("one-offer-conversion-funnel-creator-ab-and-paid-proof.md")
 };
 const base=verify(files),mut=mutations(files);
 console.log(JSON.stringify({base,mut},null,2));
 if(base.failures.length||!mut.all_detected)process.exitCode=1;
}
/* Mind R182: source-only source-control regression suite.
 * Run from repository root: node mind/r182/test_mind_r182.cjs
 * No network, no CMS writes, no DOM, no merchant transactions.
 * Export verify(files) for independently fetched committed content.
 */
"use strict";
function netPerThousand({qualified,cleared,refundsNotYetNet,fees}) {
  if(!Number.isFinite(qualified)||qualified<=0||![cleared,refundsNotYetNet,fees].every(Number.isFinite)) return null;
  return 1000*(cleared-refundsNotYetNet-fees)/qualified;
}
function verify(files) {
  const checks=[];
  function check(label,yes){checks.push({label,pass:!!yes});}
  const matrix=typeof files.matrix==="string"?JSON.parse(files.matrix):files.matrix;
  const {article,r181,a,b,hub,plan}=files;
  check("source-control files all present",[article,r181,a,b,hub,plan].every(x=>typeof x==="string"&&x.length>1000));
  check("original investigation exceeds 2300 words",article.trim().split(/\s+/).length>2300);
  check("original Thompson 1980 DOI",article.includes("10.1068/p090483"));
  check("Lewis/Johnston primary DOI",article.includes("10.1068/p260225"));
  check("Psalta/Andrews expression study",article.includes("10.1068/p7755"));
  check("Psalta fMRI research",article.includes("10.1177/0956797613501521"));
  check("Mondloch orientation study",article.includes("10.1068/p6048"));
  check("Thatcher article contains no commerce CTA",!/<button\b|<form\b|href="https:\/\/affiliates\./i.test(article));
  check("Thatcher research not audio-efficacy endorsement",article.includes("None of the research above tested Zen12"));
  check("R181 analyzed sample correction",/64 viewers|sample of 64 viewers/.test(r181)&&r181.includes("23 who reported familiarity")&&r181.includes("41 who did not"));
  check("R181 correct other-event counts",r181.includes("four familiar viewers and twelve unfamiliar viewers"));
  check("R181 significance caution",r181.includes("not statistically significant"));
  check("R181 not causally interpreted",r181.includes("not randomly assigned")&&r181.includes("not experimentally established"));
  check("ledger 19 sources",matrix.sources.length>=19);
  check("ledger >=23 evaluated claims",matrix.claims.length>=23);
  check("ledger >=14 gated decisions",matrix.gates.length>=14);
  check("offer is precise Premium",matrix.offer_priority.includes("Zen12 Premium"));
  check("partner acceptance false",matrix.affiliate_acceptance_verified===false);
  check("allowed channel terms false",matrix.allowed_channel_terms_verified===false);
  check("earning URL null",matrix.verified_affiliate_earning_url===null);
  check("purchase CTA disabled in matrix",matrix.enabled_purchase_cta===false);
  check("verified paid orders and receipts null",matrix.verified_paid_orders===null&&matrix.received_affiliate_commissions_usd===null&&matrix.realized_net_revenue_usd===null);
  check("human denominator null",matrix.qualified_human_sessions===null);
  check("Payhip Mind paid SKU not invented",matrix.verified_owned_paid_mind_product===null);
  check("seller price not promoted to checkout",matrix.seller_price_observation_is_final_charge===false&&matrix.merchant_checkout_charge_usd===null);
  check("guarantee execution remains unverified",matrix.advertised_guarantee_refund_execution_verified===false);
  check("unsubstantiated product outcomes flagged",matrix.claims.filter(c=>c.evidence_status==="UNSUBSTANTIATED_PRODUCT_EFFICACY").length>=4);
  check("R181 causal limitation claim recorded",matrix.claims.some(c=>c.id==="C21"&&c.release_gate==="PROHIBITED_CAUSAL_INFERENCE"));
  for(const [name,html] of [["A",a],["B",b]]) {
    check(name+" HTML language/viewport/semantic landmarks",/<!doctype html>/i.test(html)&&/<html lang="en">/.test(html)&&/name="viewport"/.test(html)&&/<main id="content"/.test(html));
    check(name+" no JS nor form/iframe/tracking",!/<script\b|<form\b|<iframe\b|\bgtag\s*\(|\bfbq\s*\(/i.test(html));
    check(name+" no activated merchant link",!/<a[^>]+href="https:\/\/(?:affiliates\.inspire3|www\.awin1|payhip\.com\/checkout)/i.test(html));
    check(name+" no playable video nor autoplay",!/<video\b|<audio\b|\sautoplay(?:\s|=|>)/i.test(html));
    check(name+" merchant button native disabled",/<button class="disabled" type="button" disabled aria-describedby="commercial-hold">/.test(html));
    const disclosure=html.indexOf('id="commercial-hold"');const btn=html.indexOf('<button class="disabled"');
    check(name+" FTC disclosure adjacent before control",disclosure>=0&&btn>disclosure&&btn-disclosure<700&&html.slice(disclosure,btn).includes("may earn a commission"));
    check(name+" canonical free Focus only one URI",html.includes("https://finalvestige.com/focus/"));
    check(name+" seller link marked informational",html.includes("independent informational citation, not an affiliate purchasing CTA"));
    check(name+" page explicitly unpublished",html.includes("Unpublished")||html.includes("unpublished"));
    check(name+" accessible focus/skip",html.includes('href="#content"')&&html.includes(":focus-visible"));
    check(name+" has reduced-motion rule",html.includes("prefers-reduced-motion"));
  }
  check("A does not include film section",!a.includes('class="film"'));
  check("B includes optional film and transcript",b.includes('class="film"')&&b.includes("complete timed narration")&&b.includes("00–07")&&b.includes("33–42"));
  check("B film has accessible SVG labels",b.includes('role="img"')&&b.includes("<title id=")&&b.includes("<desc id="));
  check("A/B equal after removing B optional section",b.replace(/<section class="film"[\s\S]*?<\/section>/,"")===a);
  check("Hub has four distinct streams",(hub.match(/class="card"/g)||[]).length===4);
  check("Hub is not a second signup",!/<form\b|<script\b/i.test(hub));
  check("Hub contains 3 live editorial/Focus routes",hub.includes("/2026/11/02/change-blindness/")&&hub.includes("/free-resources/puysegurs-animal-magnetism-files/")&&hub.includes("/focus/"));
  check("Hub release remains editorial-only",hub.includes("Unpublished prototype")&&hub.includes("no extra signup form"));
  check("Plan declares merchant gate",plan.includes("affiliate approval, promotional terms")&&plan.includes("UNVERIFIED"));
  check("Plan has three creator paths",plan.includes("Thatcher")&&plan.includes("gorilla")&&plan.includes("audio library"));
  check("Plan respects revenue distinction",plan.includes("NOT COMPUTABLE")&&plan.includes("Outbound clicks, starts, signups"));
  check("Plan leaves Dispatch untouched",plan.includes("Dispatch #174 owns newsletter"));
  check("Plan records inaccuracy correction",plan.includes("not statistically significant")&&plan.includes("4/23 versus 12/41"));
  check("source only not live",matrix.live_wordpress_write===false);
  check("revenue unknown returns null",netPerThousand({qualified:null,cleared:10,refundsNotYetNet:0,fees:0})===null);
  check("negative net not floored",netPerThousand({qualified:1000,cleared:4,refundsNotYetNet:2,fees:6})===-4);
  check("no double-deduct of already-net refunds",netPerThousand({qualified:1000,cleared:6,refundsNotYetNet:0,fees:1})===5);
  return {pass:checks.every(c=>c.pass),checks,failed:checks.filter(c=>!c.pass)};
}
function mutateTests(files) {
  const mutants=[
    ["acceptance invented",x=>{x.matrix.affiliate_acceptance_verified=true;}],
    ["channel permission invented",x=>{x.matrix.allowed_channel_terms_verified=true;}],
    ["affiliate link inserted",x=>{x.matrix.verified_affiliate_earning_url="https://example.com/bad";}],
    ["purchase CTA activated in matrix",x=>{x.matrix.enabled_purchase_cta=true;}],
    ["fake orders",x=>{x.matrix.verified_paid_orders=5;}],
    ["fake paid net",x=>{x.matrix.realized_net_revenue_usd=100;}],
    ["fake human sessions",x=>{x.matrix.qualified_human_sessions=150;}],
    ["fake Payhip SKU",x=>{x.matrix.verified_owned_paid_mind_product="made-up";}],
    ["final checkout invented",x=>{x.matrix.seller_price_observation_is_final_charge=true;}],
    ["refund verified invented",x=>{x.matrix.advertised_guarantee_refund_execution_verified=true;}],
    ["A merchant button enabled",x=>{x.a=x.a.replace(' type="button" disabled aria-describedby',' type="button" aria-describedby');}],
    ["B merchant button enabled",x=>{x.b=x.b.replace(' type="button" disabled aria-describedby',' type="button" aria-describedby');}],
    ["A disclosure removed",x=>{x.a=x.a.replace("may earn a commission","may receive nothing");}],
    ["B disclosure removed",x=>{x.b=x.b.replace("may earn a commission","may receive nothing");}],
    ["A tracking injected",x=>{x.a=x.a.replace("</body>","<script>gtag('send')</script></body>");}],
    ["B autoplay injected",x=>{x.b=x.b.replace("</body>","<video autoplay></video></body>");}],
    ["A external merchant earning anchor",x=>{x.a=x.a.replace("</body>",'<a href="https://affiliates.inspire3.com/?ref=bad">Buy</a></body>');}],
    ["B additional form",x=>{x.b=x.b.replace("</body>",'<form action="#">email</form></body>');}],
    ["A/B changed seller pitch",x=>{x.b=x.b.replace("The buying decision in plain English","A magical new outcome");}],
    ["A film accidentally inserted",x=>{x.a=x.a.replace("</body>",'<section class="film"></section></body>');}],
    ["B film removed",x=>{x.b=x.b.replace(/<section class="film"[\s\S]*?<\/section>/,"");}],
    ["r181 significance removed",x=>{x.r181=x.r181.replace("not statistically significant","highly significant");}],
    ["r181 counts removed",x=>{x.r181=x.r181.replace("four familiar viewers and twelve unfamiliar viewers","everyone noticed");}],
    ["article source removed",x=>{x.article=x.article.replace("10.1068/p090483","DOI-removed");}],
    ["hub duplicate signup",x=>{x.hub=x.hub.replace("</body>",'<form action="#">Join</form></body>');}],
    ["Plan denies null metrics",x=>{x.plan=x.plan.replace("NOT COMPUTABLE","zero earnings");}],
    ["Negative net hidden",x=>{x.matrix.live_wordpress_write=true;}]
  ];
  const results=mutants.map(([name,mutate])=>{const copy={...files,matrix:JSON.parse(typeof files.matrix==="string"?files.matrix:JSON.stringify(files.matrix))};mutate(copy);return {name,detected:!verify(copy).pass};});
  return {pass:results.every(x=>x.detected),results};
}
module.exports={verify,mutateTests,netPerThousand};
if(require.main===module){
  const fs=require("node:fs"),path=require("node:path"),root=path.resolve(__dirname,"../..");
  const file=(p)=>fs.readFileSync(path.join(root,p),"utf8");
  const base="mind/r182/";
  const f={article:file(base+"thatcher-face-context-INVESTIGATION-UNPUBLISHED.md"),r181:file("mind/r181/the-gorilla-the-expert-and-the-unseen-INVESTIGATION-UNPUBLISHED.md"),a:file(base+"zen12-A-evidence-buying-decision-UNPUBLISHED.html"),b:file(base+"zen12-B-optional-film-UNPUBLISHED.html"),hub:file(base+"mind-archive-four-stream-WORDPRESS-UNPUBLISHED.html"),matrix:file(base+"offer-verification-claims-and-release-gates.json"),plan:file(base+"offer-first-conversion-funnel-creator-fit-ab-acceptance.md")};
  const q=verify(f),m=mutateTests(f);console.log(JSON.stringify({base_checks:q.checks.length,base_pass:q.pass,failed:q.failed,mutations:m.results.length,detected:m.results.filter(x=>x.detected).length,mutant_pass:m.pass},null,2));if(!q.pass||!m.pass)process.exitCode=1;
}

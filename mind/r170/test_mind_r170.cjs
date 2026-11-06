/* Reproducible static safety tests. Node 18+: node mind/r170/test_mind_r170.cjs
   Scope: source-level gates, NOT browser WCAG/performance, backend attribution, checkout, partner authorization or paid sales. */
"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const get=n=>fs.readFileSync(path.join(__dirname,n),"utf8");
const read=()=>({
 article:get("the-second-thing-you-didnt-see-attentional-blink-UNPUBLISHED.md"),
 buyer:get("zen12-attentional-blink-presell-UNPUBLISHED.html"),
 hub:get("mind-archive-four-stream-INTEGRATION-UNPUBLISHED.html"),
 ledger:get("verified-seller-claims-and-commercial-gates.json"),
 plan:get("creator-offer-proof-video-ab-and-net-acceptance.md")
});
function check(d){
const j=JSON.parse(d.ledger); let n=0;
const c=(label,ok)=>{n++;assert.ok(ok,label)};
c("primary citations",/1500880/.test(d.article)&&/7707027/.test(d.article)&&/17488185/.test(d.article));
c("experiment vs product boundary",/not.*Zen12 Premium/i.test(d.article)&&/intensive/i.test(d.article));
c("no article purchase endorsement",!/earn a commission|buy now|affiliate link/i.test(d.article));
c("draft noindex both",["buyer","hub"].every(k=>/name="robots" content="noindex,nofollow"/.test(d[k])));
c("no merchant links anywhere buyer/hub",!/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i.test(d.buyer+d.hub));
c("native disabled CTA",/<button\b[^>]*\sdisabled(?=\s|>)[^>]*>Purchase link unavailable/i.test(d.buyer));
c("disclosure adjacent",/Affiliate disclosure:[\s\S]{0,200}If you purchase through this link, Final Vestige may earn a commission at no additional cost to you[\s\S]{0,280}<button/i.test(d.buyer));
c("no scripts",!/<script\b/i.test(d.buyer+d.hub));
c("no forms",!/<form\b/i.test(d.buyer+d.hub));
c("one existing focus route",["buyer","hub"].every(k=>d[k].includes('href="https://finalvestige.com/focus/"')));
c("no auto playing video",!/<video\b/i.test(d.buyer+d.hub)&&!/autoplay\s*=/.test(d.buyer+d.hub));
c("readable timed video concept",/42-second/.test(d.buyer)&&/0–7s/.test(d.buyer)&&/34–42s/.test(d.buyer));
c("source-linked preview",/pubmed.ncbi.nlm.nih.gov/.test(d.buyer));
c("original SVG alt",/<svg\b[^>]*role="img"[^>]*aria-label=/.test(d.buyer));
c("skip links",["buyer","hub"].every(k=>/class="skip" href="#main"/.test(d[k])&&/id="main"/.test(d[k])));
c("responsive",["buyer","hub"].every(k=>/max-width:720px/.test(d[k])));
c("motion safe",["buyer","hub"].every(k=>/prefers-reduced-motion:reduce/.test(d[k])));
c("no current checkout price claim",!/(?:\$87|\$37|\$67|\$127)/.test(d.buyer));
c("seller attribution",/seller descriptions/i.test(d.buyer)&&/SELLER/.test(d.ledger));
c("product facts claimed only as seller",j.claims.some(x=>x.id==="Z1"&&x.decision==="ATTRIBUTE_TO_SELLER"));
c("suppress hour-equivalence efficacy",j.claims.some(x=>x.id==="Z4"&&x.decision==="EXCLUDE_UNSUPPORTED"));
c("no named affiliate approval",j.publisher_authorization==="UNVERIFIED"&&j.earning_url===null);
c("no owned SKU",j.owned_payhip_mind_sku==="UNKNOWN");
c("all release gates closed",Object.values(j.release_gates).every(x=>x==="CLOSED"));
c("free route only",j.cta.merchant_href===null&&j.cta.affiliate_href===null);
c("no fictitious revenue",j.net_revenue_per_1000==="NOT_COMPUTABLE");
c("no click-as-sale",j.measurement.events.affiliate_outbound==="CLICK_NOT_SALE");
c("money paid not retail gross",/merchant retail gross merchandise value/i.test(d.plan));
c("no double subtract discounts",/discounts already reflected/.test(d.plan)&&/never subtract both a paid net receipt/.test(d.plan));
c("explicit settlement-only commission",/commissions actually received/i.test(d.plan));
c("unknown sessions",/UNKNOWN/.test(d.plan)&&/qualified human sessions/.test(d.plan));
c("A/B never claimed live",/UNRUN HYPOTHESIS/.test(d.plan)&&/text-only/i.test(d.plan));
c("creator lanes precise",/Attentional blink/.test(d.plan)&&/Change blindness/.test(d.plan)&&/Puységur/.test(d.plan));
c("Grok identifiers unknown",/NULL/.test(d.plan)&&/TASK-008/.test(d.plan));
c("no additional email form",!/signup form/i.test(d.buyer+d.hub));
return n;
}
const baseline=read();const passed=check(baseline);
const mutations=[
["enable CTA","buyer",s=>s.replace('type="button" disabled','type="button"')],
["erase disclosure","buyer",s=>s.replace(/<p class="disclosure">[\s\S]*?<\/p>/,'')],
["add seller link","buyer",s=>s.replace("</main>",'<a href="https://zen12.com/">Buy Zen12</a></main>')],
["add publisher link","buyer",s=>s.replace("</main>",'<a href="https://inspire3.com/">Seller</a></main>')],
["add affiliate link","buyer",s=>s.replace("</main>",'<a href="https://affiliates.inspire3.com/">Affiliate</a></main>')],
["add JS","buyer",s=>s.replace("</head>",'<script src="https://example.org/pixel.js"></script></head>')],
["new form","hub",s=>s.replace("</main>",'<form></form></main>')],
["index draft","hub",s=>s.replace('name="robots" content="noindex,nofollow"','name="robots" content="index,follow"')],
["remove focus","buyer",s=>s.replace('href="https://finalvestige.com/focus/"','href="#"')],
["remove skip","hub",s=>s.replace('class="skip" href="#main"','class="skip" href="#"')],
["remove motion safety","buyer",s=>s.replace("prefers-reduced-motion:reduce","prefers-reduced-motion:normal")],
["fake checkout price","buyer",s=>s.replace("final checkout terms are unknown","final price $87")],
["fake partner approval","ledger",s=>s.replace('"publisher_authorization": "UNVERIFIED"','"publisher_authorization": "APPROVED"')],
["fake earning url","ledger",s=>s.replace('"earning_url": null','"earning_url": "https://example.com/"')],
["open release gate","ledger",s=>s.replace('"named_publisher_approval": "CLOSED"','"named_publisher_approval": "OPEN"')],
["pass unproved effect","ledger",s=>s.replace('"EXCLUDE_UNSUPPORTED"','"APPROVED"')],
["invent paid commission","ledger",s=>s.replace('"net_revenue_per_1000": "NOT_COMPUTABLE"','"net_revenue_per_1000": 10')],
["treat outbound as sale","ledger",s=>s.replace('"affiliate_outbound": "CLICK_NOT_SALE"','"affiliate_outbound": "PAID_SALE"')],
["count merchant gross","plan",s=>s.replace("not merchant retail gross merchandise value","including merchant retail gross merchandise value")],
["double discount","plan",s=>s.replace("never subtract both a paid net receipt","subtract both a paid net receipt")],
["erase not computable","plan",s=>s.replace("UNRUN HYPOTHESIS","SUCCESSFUL PAID TEST")],
["erase creator evidence","plan",s=>s.replace(/TASK-008/g,"unverified queue")],
["remove science citation","article",s=>s.replace(/1500880/g,"NOT_FOUND")],
["insert endorsement into article","article",s=>s.replace("The inquiry is worth pursuing","Buy now: affiliate link! The inquiry is worth pursuing")],
["inject automatic video","buyer",s=>s.replace("</main>",'<video autoplay src="test.mp4"></video></main>')]
];
let killed=0;
for(const [name,key,fn] of mutations){const a={...baseline,[key]:fn(baseline[key])};try{check(a)}catch{ killed++;continue}throw Error("UNDETECTED SAFETY MUTATION: "+name)}
console.log(JSON.stringify({status:"PASS",baseline_checks:passed,unsafe_mutations_detected:killed,unsafe_mutations_total:mutations.length,scope:"SOURCE_STATIC_ONLY; native Node status depends on execution environment"}));

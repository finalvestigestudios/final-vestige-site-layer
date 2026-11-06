/** FV Mind R172 source-level QA. Native: node mind/r172/test_mind_r172.cjs
 * Does not test browsers, real devices, merchant approval, conversions, or live CMS.
 */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const files = {
  investigation: "the-skill-that-attention-training-did-not-measure-INVESTIGATION-UNPUBLISHED.md",
  buyer: "zen12-what-attention-training-can-prove-PRESELL-UNPUBLISHED.html",
  hub: "mind-four-stream-editorial-hub-PREVIEW-UNPUBLISHED.html",
  matrix: "exact-product-source-claims-and-closed-conversion-gates.json",
  contract: "one-real-offer-creator-fit-ab-and-reconciled-net-contract.md"
};

function sourceCheck(b) {
  let n = 0;
  const ok = (pred, message) => { assert.ok(pred, message); n++; };
  const doc = JSON.parse(b.matrix);
  const art = b.investigation, buyer = b.buyer, hub = b.hub, plan = b.contract;
  const nw = art.trim().split(/\s+/).length;
  ok(nw >= 2000, "original sourced investigation must be substantial");
  for (const p of ["37263078","34843370","24395196","10.1068/p3104","Puységur","2022","2023"]) ok(art.includes(p),"missing research or history: "+p);
  ok(/NOT PUBLISHED|NOT PUBLISHED|UNPUBLISHED/i.test(art),"editorial release flag missing");
  ok(/not an endorsement|no commercial endorsement|no purchase recommendation/i.test(art),"editorial independence missing");
  ok(!/href\s*=\s*["'][^"']*(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i.test(buyer),"active seller href forbidden");
  ok(!/href\s*=\s*["'][^"']*awin1\.com/i.test(buyer),"affiliate URL forbidden");
  ok(!/href\s*=\s*["'][^"']*(?:zen12\.com|inspire3\.com)/i.test(hub),"hub commercial links forbidden");
  ok(!/<script\b/i.test(buyer+hub),"no new JS, scripts or trackers");
  ok(!/<form\b/i.test(buyer+hub),"do not duplicate signup mechanism");
  ok(!/<(?:video|audio)[^>]*\sautoplay(?:\s|=|>)/i.test(buyer),"no media autoplay attribute");
  ok(/<button[^>]*\sdisabled(?:\s|=|>)/i.test(buyer),"merchant button must natively be disabled");
  ok(/aria-disabled="true"/i.test(buyer),"a11y disability state missing");
  ok(/prospective affiliate disclosure/i.test(buyer),"visible adjacent disclosure missing");
  ok(/may earn a commission at no additional cost to you/i.test(buyer),"plain compensation disclosure missing");
  ok(/https:\/\/finalvestige.com\/focus\//i.test(buyer+hub),"existing Focus destination missing");
  ok(/href="#main"/.test(buyer) && /href="#main"/.test(hub),"skip-to-content behavior missing");
  ok(/prefers-reduced-motion/.test(buyer) && /prefers-reduced-motion/.test(hub),"reduced-motion safeguard missing");
  ok(/max-width:760px|760px/.test(buyer),"mobile breakpoint missing");
  ok(/max-width:700px/.test(hub),"hub breakpoint missing");
  ok(/meta name="robots" content="noindex,nofollow"/i.test(buyer) && /meta name="robots" content="noindex,nofollow"/i.test(hub),"unreleased preview indexed");
  ok(/42-second/.test(buyer),"video hypothesis duration missing");
  ok(/not a playable media file/i.test(buyer),"unproduced video must be labeled honestly");
  ok(/Neither study tested Zen12 audio/.test(buyer),"no research-to-commercial efficacy transfer");
  ok(/<details>/.test(buyer),"optional video treatment control missing");
  ok(/https:\/\/pubmed.ncbi.nlm.nih.gov\/34843370\//.test(buyer),"primary scientific source missing");
  ok(/seller representations|seller statements|seller promise|seller-listed/i.test(buyer),"seller vs evidence distinction missing");
  ok(/seller-listed/i.test(buyer),"product features must be labeled seller-listed");
  ok(/not a verified checkout|not a verified checkout total/i.test(buyer),"price and checkout caveat missing");
  ok(/refunds are fulfilled|refund fulfillment/i.test(buyer),"refund verification caveat missing");
  ok(doc.review_state==="DRAFT_UNPUBLISHED_HARD_HOLD","public commercial activation state");
  ok(doc.commercial_activation===false && doc.live_writes===false,"unauthorized release");
  ok(Array.isArray(doc.sources)&&doc.sources.length>=12,"sources missing");
  ok(Array.isArray(doc.claims)&&doc.claims.length>=15,"claims matrix too small");
  ok(doc.gates.length>=15 && doc.gates.every(g=>g.status==="CLOSED"),"unsafe open commercial gate");
  for (const id of ["partner_named_acceptance","partner_channel_email","partner_tracking_link","merchant_checkout_total","owned_payhip_sku","verified_affiliate_sale","verified_owned_purchase","reconciled_net_revenue","founder_release"]) ok(doc.gates.some(g=>g.id===id && g.status==="CLOSED"),"missing commercial gate "+id);
  ok(doc.current_kpi_value===null && /NOT COMPUTABLE/.test(doc.data_note),"invented net KPI");
  for (const id of ["ZEN-05","ZEN-06","ZEN-07","ZEN-08"]) ok(doc.claims.some(c=>c.id===id && c.decision==="unsupported_omit"),"unsupported seller efficacy allowed "+id);
  for (const p of ["Grok","asset_id","merchant_confirmed_paid_sale","qualified human","Focus","NOT RUN","UNKNOWN","HOLD","Payhip"]) ok(plan.includes(p),"measurement/ownership contract missing "+p);
  ok(/not 0/i.test(plan),"unknown denominator must not be fake zero");
  ok(!/http[s]?:\/\/www\.awin1\.com\/cread\.php/i.test(buyer+hub+plan),"earning URL present");
  return n;
}
function mutate(b) {
 const attacks=[
 ["button enables purchase",x=>({...x,buyer:x.buyer.replace('type="button" disabled aria-disabled="true"','type="button" aria-disabled="true"')})],
 ["affiliate link injection",x=>({...x,buyer:x.buyer.replace('</main>','<a href="https://www.awin1.com/cread.php?a=1">Buy</a></main>')})],
 ["seller link activation",x=>({...x,buyer:x.buyer.replace('</main>','<a href="https://zen12.com/">Buy</a></main>')})],
 ["inspire3 link activation",x=>({...x,buyer:x.buyer.replace('</main>','<a href="https://inspire3.com/">Buy</a></main>')})],
 ["remove explicit financial disclosure",x=>({...x,buyer:x.buyer.replace('may earn a commission at no additional cost to you','no compensation relationship')})],
 ["remove disclosure header",x=>({...x,buyer:x.buyer.replace('Prospective affiliate disclosure','Ad')})],
 ["add tracker",x=>({...x,buyer:x.buyer.replace('</head>','<script src="https://example.com/track.js"></script></head>')})],
 ["add signup form",x=>({...x,hub:x.hub.replace('</main>','<form action="/newsletter"><input type="email"></form></main>')})],
 ["remove Focus",x=>({...x,buyer:x.buyer.replaceAll('https://finalvestige.com/focus/','https://example.com/missing') ,hub:x.hub.replaceAll('https://finalvestige.com/focus/','https://example.com/missing')})],
 ["undo native disabled",x=>({...x,buyer:x.buyer.replace(' disabled aria-disabled="true"',' aria-disabled="true"')})],
 ["remove aria-disabled",x=>({...x,buyer:x.buyer.replace('aria-disabled="true"','aria-disabled="false"')})],
 ["raise merchant authorization",x=>{const d=JSON.parse(x.matrix);d.gates.find(g=>g.id==="partner_named_acceptance").status="OPEN";return {...x,matrix:JSON.stringify(d)};}],
 ["raise founder release",x=>{const d=JSON.parse(x.matrix);d.gates.find(g=>g.id==="founder_release").status="OPEN";return {...x,matrix:JSON.stringify(d)};}],
 ["invent net revenue",x=>{const d=JSON.parse(x.matrix);d.current_kpi_value=45;return {...x,matrix:JSON.stringify(d)};}],
 ["allow health cure",x=>{const d=JSON.parse(x.matrix);d.claims.find(c=>c.id==="ZEN-07").decision="allowed";return {...x,matrix:JSON.stringify(d)};}],
 ["missing sources",x=>{const d=JSON.parse(x.matrix);d.sources=[];return {...x,matrix:JSON.stringify(d)};}],
 ["remove metacognition primary research",x=>({...x,investigation:x.investigation.replaceAll("37263078","MISSING")})],
 ["remove study training reference",x=>({...x,investigation:x.investigation.replaceAll("34843370","MISSING")})],
 ["remove research limit",x=>({...x,buyer:x.buyer.replace('Neither study tested Zen12 audio.','Both studies tested Zen12 audio.')})],
 ["enable affiliate in state",x=>{const d=JSON.parse(x.matrix);d.commercial_activation=true;return {...x,matrix:JSON.stringify(d)};}],
 ["remove 42-second concept",x=>({...x,buyer:x.buyer.replaceAll("42-second","forty-two-second")})],
 ["remove buyer noindex",x=>({...x,buyer:x.buyer.replace('meta name="robots" content="noindex,nofollow"','meta name="robots" content="index,follow"')})],
 ["remove skip links",x=>({...x,buyer:x.buyer.replace('href="#main"','href="#other"'),hub:x.hub.replace('href="#main"','href="#other"')})],
 ["remove evidence seller warning",x=>({...x,buyer:x.buyer.replaceAll("seller-listed","internal-feature").replaceAll("Seller lists","Our editors confirm").replaceAll("seller statements","independent findings")})]
 ];
 let blocked=0;const names=[];
 for(const [name,act] of attacks){let failed=false;try{sourceCheck(act(b))}catch(_){failed=true}if(!failed)throw new Error("UNDETECTED mutation: "+name);blocked++;names.push(name)}
 return {blocked, attacks:attacks.length,names};
}
function main(b) {const assertions=sourceCheck(b);const mutation=mutate(b);return {status:"PASS",assertions,...mutation};}
if(require.main === module) {
 const b={};for(const [key,file] of Object.entries(files)) b[key]=fs.readFileSync(path.join(__dirname,file),"utf8");
 const result=main(b);console.log(JSON.stringify(result,null,2));
}
module.exports={main,sourceCheck,mutate,files};

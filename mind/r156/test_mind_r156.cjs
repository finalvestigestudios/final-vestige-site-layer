/* Final Vestige Mind R156: run from repo root with node mind/r156/test_mind_r156.cjs
 * Offline, read-only. No CMS, merchant, email, network or analytics activity. */
"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const read=name=>fs.readFileSync(path.join(__dirname,name),"utf8");
const originals={
 article:read("gorilla-inattentional-blindness-investigation.md"),
 html:read("mind-gorilla-focus-and-gated-offer-REVIEW-ONLY.html"),
 matrix:read("sourced-claims-commerce-and-release-gates.json"),
 plan:read("revenue-first-buyer-creator-and-experiment-plan.md")
};
function audit(d){
 const errors=[]; const ck=(pass,label)=>{if(!pass)errors.push(label);};
 let m={}; try{m=JSON.parse(d.matrix);}catch{return ["bad JSON matrix"];}
 const buttons=[...d.html.matchAll(/<button\b[^>]*>/gi)].map(x=>x[0]);
 ck(buttons.length===1 && /\sdisabled(?:\s|>|=)/i.test(buttons[0]),"purchase control must be physically disabled");
 ck(/data-release="HARD_HOLD"/.test(d.html)&&/data-commercial-approved="false"/.test(d.html),"review and commerce remain blocked");
 ck(/data-video-status="STORYBOARD_ONLY"/.test(d.html) && !/<video\b/i.test(d.html),"storyboard must not masquerade as produced video");
 ck(d.html.includes("class=\"disclosure\"") && d.html.indexOf("class=\"disclosure\"")<d.html.indexOf("<button"),"near-offer disclosure precedes paid button");
 ck(/If you purchase through a future authorized link, Final Vestige may earn a commission at no additional cost to you/.test(d.html),"plain prospective paid-link disclosure");
 ck(/href="https:\/\/finalvestige\.com\/focus\/"/.test(d.html),"existing Focus destination");
 ck(!/<form\b|<script\b|<iframe\b/i.test(d.html),"no new forms scripts frames");
 ck(!/<video\b[^>]*\bautoplay\b/i.test(d.html),"no autoplay media");
 ck(!/href="https?:\/\/(?:[^"]*hypnosislive\.com|[^"]*zen12\.com|[^"]*affiliates\.inspire3\.com)/i.test(d.html),"no clickable merchant link pending partner approval");
 ck(!/href="[^"]*(?:affiliate_id|sub_id|\/track\?|\/click\?)/i.test(d.html),"no unapproved earning or tracking URL");
 ck(/:focus-visible/.test(d.html)&&/prefers-reduced-motion/.test(d.html),"accessible focus and motion CSS");
 ck(/max-width:390px/.test(d.html) && /min-width:820px/.test(d.html),"responsive 390/820 breakpoints");
 ck(/0–7s/.test(d.html)&&/34–40s/.test(d.html) && /caption and accessible transcript concept/.test(d.html),"original timed storyboard and transcript");
 ck(d.article.trim().split(/\s+/).length>1800,"investigation must have substantial depth");
 ck(d.article.includes("https://pubmed.ncbi.nlm.nih.gov/10694957/"),"primary 1999 source");
 ck(d.article.includes("https://pubmed.ncbi.nlm.nih.gov/23397479/"),"2010 counterexample source");
 ck(d.article.includes("https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/"),"2013 expert primary study");
 ck(d.article.includes("No affiliate earning link is active in this investigation"),"scientific and commercial conclusions separate");
 ck(d.plan.includes("Total Focus")&&d.plan.includes("33-minute")&&d.plan.includes("47 MB"),"exact product description retained");
 ck(d.plan.includes("NOT COMPUTABLE")&&d.plan.includes("qualified_human_session")&&d.plan.includes("affiliate_commission_settled"),"realized revenue versus clicks");
 ck(d.plan.includes("360/390/768/1440/1920"),"five viewport QA plan");
 ck(d.plan.includes("12 minutes equals one hour") && d.plan.includes("not independently established"),"reject Zen12 equivalence seller claim");
 ck(d.plan.includes("TRUE")===false,"avoid fake test outcome");
 ck(m.claims.length>=35 && m.claims.every(c=>/^https:\/\//.test(c.source)),"all claims linked");
 ck(m.release_gates.length>=40 && m.release_gates.every(g=>g.status==="CLOSED"),"all commercial release gates closed");
 ck(m.eligible_for_publication===false&&m.eligible_for_affiliate_activation===false&&m.affiliate_partner_acceptance_verified===false,"must not activate partner or release");
 ck(m.affiliate_earning_url===null&&m.merchant_confirmed_sales===null&&m.affiliate_commissions_settled===null&&m.qualified_human_sessions===null&&m.net_revenue_per_1000_qualified_sessions===null&&m.costs===null,"unknown commercial counts null, not fabricated zero");
 ck(m.claims.some(c=>/Zen12/.test(c.claim)&&c.disposition.startsWith("REJECT")),"reject unsupported Zen12 equivalence");
 ck(m.claims.some(c=>/Total Focus/.test(c.claim)&&c.disposition.startsWith("REJECT")),"reject unsupported paid audio effects");
 ck(/seller.*claim/i.test(d.article),"seller claims explicitly marked");
 return errors;
}
assert.deepEqual(audit(originals),[],"exact committed-source safety audit");
const trial=[
 ["enabled button",d=>d.html=d.html.replace('type="button" disabled','type="button"')],
 ["claim affiliate approved",d=>d.html=d.html.replace('data-commercial-approved="false"','data-commercial-approved="true"')],
 ["claim published",d=>d.html=d.html.replace('data-release="HARD_HOLD"','data-release="LIVE"')],
 ["erase disclosure",d=>d.html=d.html.replace('class="disclosure"','class="omitted"')],
 ["strip disclosure meaning",d=>d.html=d.html.replace('If you purchase through a future authorized link, Final Vestige may earn a commission at no additional cost to you.','We like this')],
 ["inject tracker",d=>d.html+='<script src="https://example.com/pixel.js"></script>'],
 ["inject signup",d=>d.html+='<form><input type="email"></form>'],
 ["insert merchant CTA",d=>d.html+='<a href="https://hypnosislive.com/mental-skills/total-focus">buy now</a>'],
 ["insert earning URL",d=>d.html+='<a href="https://affiliates.inspire3.com/track?affiliate_id=unverified">purchase</a>'],
 ["drop Focus",d=>d.html=d.html.replaceAll('href="https://finalvestige.com/focus/"','href="#"')],
 ["remove study",d=>d.article=d.article.replaceAll('https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/','NO_SOURCE')],
 ["mark video produced",d=>d.html=d.html.replace('data-video-status="STORYBOARD_ONLY"','data-video-status="PLAYABLE"')],
 ["erase caption timing",d=>d.html=d.html.replace('34–40s','timing-unknown')],
 ["fake sale",d=>{const m=JSON.parse(d.matrix);m.merchant_confirmed_sales=1;d.matrix=JSON.stringify(m)}],
 ["fake commission",d=>{const m=JSON.parse(d.matrix);m.affiliate_commissions_settled=1;d.matrix=JSON.stringify(m)}],
 ["invent zero costs",d=>{const m=JSON.parse(d.matrix);m.costs=0;d.matrix=JSON.stringify(m)}],
 ["open partner gate",d=>{const m=JSON.parse(d.matrix);m.release_gates[0].status="OPEN";d.matrix=JSON.stringify(m)}],
 ["approve affiliate",d=>{const m=JSON.parse(d.matrix);m.affiliate_partner_acceptance_verified=true;d.matrix=JSON.stringify(m)}],
 ["remove paid event",d=>d.plan=d.plan.replaceAll("affiliate_commission_settled","affiliate_click")],
 ["drop mobile styling",d=>d.html=d.html.replace("max-width:390px","max-width:180px")],
 ["erase media motion consideration",d=>d.html=d.html.replace("prefers-reduced-motion","prefers-motion")]
];
for(const [name,change] of trial){const d={...originals};change(d);assert(audit(d).length>0,"adversarial mutation not caught: "+name)}
console.log("PASS R156 exact-source audit; "+trial.length+"/"+trial.length+" adversarial mutations rejected; "+Object.keys(originals).length+" files; "+JSON.parse(originals.matrix).claims.length+" sourced claim decisions; "+JSON.parse(originals.matrix).release_gates.length+" closed gates.");

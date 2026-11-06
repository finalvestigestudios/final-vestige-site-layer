/* Run from repository root: node mind/r157/test_mind_r157.cjs
 * Read-only, offline regression. Does NOT test browser behavior, Jetpack delivery, merchant checkout or actual sales.
 */
"use strict";
const fs=require("node:fs"),path=require("node:path");
const get=name=>fs.readFileSync(path.join(__dirname,name),"utf8");
const data={
 article:get("auditory-entrainment-the-beat-and-the-promise-investigation.md"),
 guide:get("brainwave-shots-focus-shot-independent-buyer-guide.md"),
 html:get("brainwave-focus-ethical-bridge-UNPUBLISHED.html"),
 ledger:get("claim-sources-authorizations-and-revenue-gates.json"),
 plan:get("commercial-acceptance-creator-map-and-zen12-video-hypothesis.md")
};
function inspect(x){
 const errors=[], check=(ok,label)=>{if(!ok)errors.push(label)};
 let json;
 try{json=JSON.parse(x.ledger)}catch(e){errors.push("bad JSON ledger");return errors}
 const wc=s=>(s.match(/\b[\w'-]+\b/g)||[]).length;
 check(wc(x.article)>=1750,"long-form article too short");
 check(wc(x.guide)>=800,"buyer guide too short");
 check(/Ingendoh|2023 systematic review/i.test(x.article),"no EEG review");
 check(/five[\s\S]{0,100}eight/i.test(x.article),"study tally missing");
 check(/isochronic/i.test(x.article)&&/binaural/i.test(x.article),"stimulus type confusion");
 check(/None of these papers directly tested the commercial Focus Shot|not.{0,70}tested.{0,55}Focus Shot/i.test(x.article),"product scope not clear");
 check(/no commercial|no product purchased|not an endorsement/i.test(x.article),"editorial independence absent");
 check(/https:\/\/finalvestige.com\/free-resources\/puysegurs-animal-magnetism-files\//i.test(x.article),"Puységur source missing");
 check(/https:\/\/brainwaveshots.com\/focus-shot/.test(x.guide),"exact product source missing");
 check(/https:\/\/brainwaveshots.com\/faq/.test(x.guide),"merchant FAQ missing");
 check(/15-minute|fifteen-minute/i.test(x.guide)&&/30-minute|thirty-minute/i.test(x.guide),"bundle duration omitted");
 check(/12.{0,4}18.{0,12}hertz|12\/18/i.test(x.guide),"exact protocol missing");
 check(/isochronic/i.test(x.guide)&&/binaural/i.test(x.guide),"buyer method distinction missing");
 check(/NOT AUTHORIZED FOR FINAL VESTIGE/.test(x.guide),"authorization caution omitted");
 check(/not a checked checkout price/i.test(x.guide),"price certainty caution omitted");
 check(/refund.{0,100}(?:untested|not tested|not verified|unverified)|(?:untested|not tested|not verified|unverified).{0,100}refund/i.test(x.guide),"refund caveat omitted");
 check(/<html\s+lang="en"/i.test(x.html),"lang missing");
 check(/<meta\s+name="robots"\s+content="noindex,nofollow"/i.test(x.html),"review status indexable");
 check(/<main\s+id="main">/i.test(x.html),"semantic main missing");
 check(/class="skip"/.test(x.html)&&/href="#main"/.test(x.html),"skip link missing");
 check(/:focus-visible/.test(x.html),"focus ring missing");
 check(/prefers-reduced-motion:reduce/.test(x.html),"motion fallback missing");
 check(/max-width:780px/.test(x.html)&&/max-width:370px/.test(x.html),"mobile breakpoints missing");
 check(/https:\/\/finalvestige.com\/focus\//.test(x.html),"single pre-existing Focus CTA absent");
 check(!/<form\b/i.test(x.html),"duplicate form detected");
 check(!/<script\b/i.test(x.html),"script detected");
 check(!/<iframe\b/i.test(x.html),"third-party embed detected");
 check(!/<video\b/i.test(x.html),"fake playable video detected");
 check(!/autoplay/i.test(x.html),"forced playback term detected");
 check(!/\*\*those outcomes/i.test(x.html),"raw markdown in HTML");
 check(!/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:brainwaveshots|hypnosislive|zen12)\.com/i.test(x.html),"merchant outbound anchor activated");
 check(!/awin1\.com\/cread|ref=3055117|affiliate_id=|[?&]aff(?:iliate)?=/.test(x.html),"affiliate tracking link detected");
 check(/<button\b[^>]*\bdisabled(?=[\s>])[^>]*>/i.test(x.html),"merchant control not physically disabled");
 check(/Possible future commission:/.test(x.html)&&/may earn a commission at no additional cost/i.test(x.html),"adjacent commission disclosure absent");
 const d=x.html.indexOf("Possible future commission:"),b=x.html.indexOf("<button",d);
 check(d>=0&&b>d&&b-d<600,"disclosure not next to prospective CTA");
 check(json.status==="UNPUBLISHED_COMMERCE_HARD_HOLD","release status not closed");
 check(json.merchant_approval==="UNKNOWN_NOT_REJECTED","partner state must remain unknown");
 check(json.claims.length>=30,"source matrix insufficient");
 check(json.release_gates.length>=35,"release gate coverage insufficient");
 check(json.claims.every(c=>/^https:\/\//.test(c.source)&&c.disposition),"claim evidence source absent");
 check(json.release_gates.every(g=>g.status==="CLOSED"),"commercial gate opened");
 check(json.measurement_contract.metric_status==="NOT_COMPUTABLE","revenue improperly claimed");
 check(json.measurement_contract.non_equivalences.includes("outbound_click_not_sale"),"click conflated with sale");
 check(json.measurement_contract.no_pii===true,"privacy consent contract missing");
 check(/NULL until Grok supplies them/.test(x.plan),"fake media IDs introduced");
 check(/7- and 30-day cohorts/i.test(x.plan),"cohort contract omitted");
 check(/UNRUN/.test(x.plan)&&/poster/i.test(x.plan)&&/VTT/i.test(x.plan),"optional video prototype incomplete");
 check(/TASK-008/.test(x.plan)&&/Grok/.test(x.plan),"creator lane omitted");
 check(/PR #49/.test(x.plan)&&/PR #172/.test(x.plan),"owner protections absent");
 check(/OFFER → FUNNEL STEP/.test(x.plan),"offer blocker owner table missing");
 check(!/https?:\/\/www\.awin1\.com\/cread|www\.awin1\.com\/cread/.test(x.article+x.guide+x.html),"tracking URL present");
 return errors;
}
const base=inspect(data);
if(base.length)throw Error("FAIL BASE: "+base.join(" | "));
const mutations=[
["enable buy",d=>({html:d.html.replace(/<button type="button" class="button" disabled/,'<button type="button" class="button"')})],
["remove disclosures",d=>({html:d.html.replace(/Possible future commission:/,'Information:').replace(/may earn a commission at no additional cost/,'may offer a link')})],
["displace disclosure",d=>({html:d.html.replace("Possible future commission:","General information:")})],
["inject form",d=>({html:d.html.replace("</main>","<form><input type=email></form></main>")})],
["inject script",d=>({html:d.html.replace("</head>","<script src='https://example.com/track.js'></script></head>")})],
["inject iframe",d=>({html:d.html.replace("</main>","<iframe src='https://example.com'></iframe></main>")})],
["add merchant purchase",d=>({html:d.html.replace("</main>","<a href='https://brainwaveshots.com/focus-shot'>Buy now</a></main>")})],
["add affiliate URL",d=>({html:d.html.replace("</main>","<a href='https://www.awin1.com/cread?x=3'>Buy</a></main>")})],
["add fake video",d=>({html:d.html.replace("</main>","<video controls></video></main>")})],
["index review",d=>({html:d.html.replace('content="noindex,nofollow"','content="index,follow"')})],
["remove focus link",d=>({html:d.html.replace("https://finalvestige.com/focus/","/placeholder")})],
["remove source",d=>({guide:d.guide.replaceAll("https://brainwaveshots.com/focus-shot","https://example.invalid/")})],
["allow all approvals",d=>({ledger:JSON.stringify({...JSON.parse(d.ledger),release_gates:JSON.parse(d.ledger).release_gates.map((g,i)=>({...g,status:i===0?"OPEN":"CLOSED"}))})})],
["invent commission data",d=>({ledger:JSON.stringify({...JSON.parse(d.ledger),measurement_contract:{...JSON.parse(d.ledger).measurement_contract,metric_status:"VERIFIED_PROFIT"}})})],
["remove privacy",d=>({ledger:JSON.stringify({...JSON.parse(d.ledger),measurement_contract:{...JSON.parse(d.ledger).measurement_contract,no_pii:false}})})],
["fake grok IDs",d=>({plan:d.plan.replace("NULL until Grok supplies them","CONFIRMED media IDs")})],
["drop isochronic distinction",d=>({article:d.article.replaceAll("isochronic","simulated")})],
["remove script source tally",d=>({article:d.article.replace("Five","A few").replace("eight","some")})],
["drop QA scope",d=>({plan:d.plan.replaceAll("PR #49","Flagship").replaceAll("PR #172","Mind hub")})]
];
let detected=0;
for(const [name,mutate] of mutations){const changed={...data,...mutate(data)};const failures=inspect(changed);if(!failures.length)throw Error("Mutation escaped: "+name);detected++}
process.stdout.write("PASS: "+(mutations.length+1)+" test cases; "+detected+"/"+mutations.length+" adverse mutations detected; "+JSON.parse(data.ledger).claims.length+" claim decisions and "+JSON.parse(data.ledger).release_gates.length+" CLOSED gates\n");

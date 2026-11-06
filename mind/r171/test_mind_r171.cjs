"use strict";
/** R171 source-only guardrail suite. Run from repository: node mind/r171/test_mind_r171.cjs
 * No network, no credentials, no browser required. Does NOT certify WCAG/merchant eligibility. */
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const root=__dirname;
const read=n=>fs.readFileSync(path.join(root,n),"utf8");
const buyer=read("zen12-premium-stroop-buyer-experience-UNPUBLISHED.html");
const hub=read("mind-four-stream-integration-HUB-UNPUBLISHED.html");
const article=read("when-a-word-refuses-to-be-only-ink-INVESTIGATION-UNPUBLISHED.md");
const plan=read("one-offer-first-purchase-experiment-and-measurement.md");
const matrix=JSON.parse(read("official-offer-proof-claims-and-closed-commercial-gates.json"));
let checks=0;
const ok=(cond,msg)=>{assert.ok(cond,msg);checks++};
function checkBuyer(h){
  const b=h.toLowerCase();
  assert.match(h,/<html lang="en">/i);
  assert.match(h,/name="viewport"/i);
  assert.match(h,/name="robots" content="noindex,nofollow,noarchive"/i);
  assert.match(h,/<main id="main">/i);
  assert.match(h,/class="skip" href="#main"/i);
  assert.match(h,/prefers-reduced-motion/);
  assert.match(h,/<details class="film">/);
  assert.match(h,/full accessible transcript/i);
  assert.match(h,/No autoplay|no autoplay/i);
  assert.match(h,/42-second/);
  assert.match(h,/disabled aria-disabled="true"/);
  assert.match(h,/Affiliate disclosure:/);
  assert.match(h,/may earn a commission/i);
  assert.match(h,/No affiliate link is active on this page/i);
  assert.match(h,/pending verification/i);
  assert.match(h,/12 levels, 48 MP3 recordings/);
  assert.match(h,/four listening styles/i);
  assert.match(h,/seller's public Premium comparison/i);
  assert.match(h,/not<\\/em> a verified final checkout amount/i);
  assert.match(h,/no product-specific controlled evidence/i);
  assert.match(h,/Final Vestige does not subscribe/i);
  assert.match(h,/https:\/\/finalvestige.com\/focus\//);
  assert.match(h,/noindex,nofollow,noarchive/);
  assert.doesNotMatch(h,/<script\b/i);
  assert.doesNotMatch(h,/<iframe\b/i);
  assert.doesNotMatch(h,/<form\b/i);
  assert.doesNotMatch(h,/<video\b/i); // storyboard, not falsely presented as an actual playable video
  assert.doesNotMatch(h,/<a[^>]+href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots|affiliates\.inspire3)\.com/i);
  assert.doesNotMatch(h,/<a[^>]+href=["'][^"']*(?:awin1\.com|clickbank|tracking|ref=)/i);
  assert.doesNotMatch(h,/<button(?![^>]*disabled)[^>]*>[^<]*zen12/i);
  assert.doesNotMatch(h,/guaranteed (?:cure|results|profits)/i);
  assert.doesNotMatch(h,/<link[^>]+stylesheet/i);
  assert.doesNotMatch(h,/<img[^>]+src=["']https?:/i);
  const disclose=h.indexOf('class="disclose"'),button=h.indexOf("<button");
  assert.ok(disclose>=0&&button>disclose&&button-disclose<600,"disclosure must precede adjacent disabled CTA");
}
checkBuyer(buyer);checks+=35;
ok(hub.includes("canonical implementation remains draft PR #172")||hub.includes("Canonical implementation remains draft PR #172"),"PR172 preserved");
ok(hub.includes("https://finalvestige.com/focus/"),"hub keeps Focus");
ok(hub.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"),"hub links historical resource");
ok(!/<script\b/i.test(hub),"hub scriptless");
ok(!/<form\b/i.test(hub),"hub no new signup");
ok(!/<a[^>]*href=["'][^"']*zen12\.com/i.test(hub),"hub no seller link");
ok(article.includes("16 highly suggestible and 16 less suggestible"),"study selection");
ok(article.includes("2006 study"),"induction distinction");
ok(article.includes("not a validated Stroop task"),"exercise caution");
ok(article.includes("does not show that any person's attention"),"no universal product transfer");
ok(article.includes("Puységur"),"historical link");
ok(plan.includes("paid, attributable conversion rate"),"A/B paid objective");
ok(plan.includes("NOT_COMPUTABLE")||plan.includes("NOT COMPUTABLE"),"missing revenue stays undefined");
ok(plan.includes("confirmed_optin"),"confirmed optin distinct from click");
ok(plan.includes("affiliate_click"),"affiliate click event");
ok(plan.includes("NOT ALREADY NETTED")||plan.includes("not already netted"),"no double deduction");
ok(plan.includes("Grok / Praxxis"),"creator lane respected");
ok(matrix.sources.length>=14,"source register");
ok(matrix.claims.length>=30,"claim register");
ok(Object.keys(matrix.gates).length>=35,"commercial gates count");
ok(Object.values(matrix.gates).every(g=>g.status==="CLOSED"&&g.evidence===null),"all gates remain closed");
ok(matrix.commercial_activation==="HARD_HOLD","activation hard hold");
ok(matrix.revenue.qualified_human_sessions===null,"denominator unknown");
ok(matrix.revenue.settled_affiliate_commissions===null,"commissions unknown");
ok(matrix.revenue.net_revenue_per_1000_qualified_human_sessions==="NOT_COMPUTABLE","net unknown");
ok(matrix.claims.find(x=>x.id==="A02").decision==="UNKNOWN_HOLD","FV approval unverified");
ok(matrix.claims.find(x=>x.id==="Z09").decision==="REJECT_UNSUPPORTED","one-hour shortcut rejected");
ok(matrix.claims.every(x=>matrix.sources.some(s=>s.id===x.source)),"every claim has source");
ok(matrix.sources.every(x=>x.url.startsWith("https://")),"sources URL explicit");
ok(buyer.match(/<a\s/g).length>=4,"usable public free/scholarly links");
const bad=[
["merchant href",s=>s.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/"')],
["affiliate tracking href",s=>s.replace('href="https://finalvestige.com/focus/"','href="https://www.awin1.com/cread.php?x=1"')],
["native disabled removed",s=>s.replace('disabled aria-disabled="true"','aria-disabled="true"')],
["aria disabled missing",s=>s.replace('disabled aria-disabled="true"','disabled')],
["disclosure removed",s=>s.replace('Affiliate disclosure:','Marketing disclosure:')],
["earn disclosure removed",s=>s.replace('may earn a commission','enjoys a relationship')],
["activation claim",s=>s.replace('No affiliate link is active on this page','An affiliate link is active on this page')],
["noindex removed",s=>s.replace('noindex,nofollow,noarchive','index,follow')],
["script injection",s=>s.replace('</body>','<script src="https://tracker.test/a.js"></script></body>')],
["iframe injection",s=>s.replace('</body>','<iframe src="https://track.test"></iframe></body>')],
["form injection",s=>s.replace('</body>','<form><input type=email></form></body>')],
["remote image",s=>s.replace('</body>','<img src="https://track.test/pixel"></body>')],
["remote stylesheet",s=>s.replace('</head>','<link rel="stylesheet" href="https://track.test/a.css"></head>')],
["claims medical benefit",s=>s.replace('No autoplay','guaranteed cure. No autoplay')],
["playable video false claim",s=>s.replace('</body>','<video controls src="video.mp4"></video></body>')],
["remove transcript",s=>s.replace('full accessible transcript','summary of a storyboard')],
["reduce motion removed",s=>s.replace('@media(prefers-reduced-motion:reduce)','@media(prefers-motion:please)')],
["remove skip",s=>s.replace('class="skip" href="#main"','class="skip" href="#none"')],
["price becomes guaranteed",s=>s.replace('not</em> a verified final checkout amount','verified final checkout amount')],
["product description removed",s=>s.replace('12 levels, 48 MP3 recordings','many MP3 recordings')],
["no support caveat removed",s=>s.replace('no product-specific controlled evidence','excellent product-specific controlled evidence')],
["seller no optin replaced",s=>s.replace('Final Vestige does not subscribe','Final Vestige subscribes')],
["video details removed",s=>s.replace('<details class="film">','<section class="film">')]
];
let detected=0;
for(const [name,mutate] of bad){const tampered=mutate(buyer);assert.notEqual(tampered,buyer,"mutant did not change "+name);
try{checkBuyer(tampered)}catch(e){detected++;continue}throw Error("Unsafe mutation escaped: "+name)}
console.log(JSON.stringify({baseline_source_assertions:checks,unsafe_mutations_detected:detected,unsafe_mutations_total:bad.length,pass:true,limitations:"source checks only; native Node when executed; not live browser, WCAG, merchant authorization, video or paid sale proof"},null,2));

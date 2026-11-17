/* FV Mind R443 — offline, zero-dependency, READ-ONLY source regression gate.
   Run from repository root: node mind/r443/QA_GATE.cjs
   SOURCE CHECKS ONLY. Does not perform browser QA, partner approval,
   checkout, merchant settlement, live WordPress or video playback tests. */
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const dir = __dirname;
const read = file => fs.readFileSync(path.join(dir,file),"utf8");
const A=read("ZEN12_A_TEXT_ONLY.html");
const B=read("ZEN12_B_OPTIONAL_FILM_CONCEPT.html");
const H=read("MIND_HUB_WP_SOURCE_ONLY.html");
const ART=read("THE_SECOND_TARGET_DISAPPEARED.md");
const VTT=read("R443_OPTIONAL_FILM_CAPTIONS.vtt");
const MATRIX=JSON.parse(read("CLAIM_SOURCE_AND_RELEASE_MATRIX.json"));
const FUNNEL=read("OFFER_CREATOR_FUNNEL_REVENUE_ACCEPTANCE.md");
let passed=0,failed=[];
function check(name,fn){try{assert.ok(fn(),name);passed++}catch(e){failed.push(name+": "+e.message)}}
const sourceOnly=[A,B,H];
const buyerSpan=s=>{const start=s.indexOf('<section aria-labelledby="offer-scope" id="offer">');const end=s.indexOf('</section></section>',start);return start<0||end<0?"":s.slice(start,end+20)};
const sellerHref=/<a\b[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:inspire3\.com|zen12\.com|hypnosislive\.com|brainwaveshots\.com)/i;
const externalScript=/<script\b|<iframe\b|<form\b|<video\b|<audio\b|autoplay\s*=/i;
const enabledSellerCTA=s=>{const html=s.match(/<button\b[^>]*>Check the verified Zen12 offer[^<]*<\/button>/i);return !html||!/\sdisabled(?:\s|>|=)/i.test(html[0])};
const disclosureNextTo=s=>{const idx=s.indexOf("Affiliate disclosure:");const btn=s.indexOf("Check the verified Zen12 offer");return idx>=0&&btn>idx&&btn-idx<800};
function staticSafety(s){return !sellerHref.test(s)&&!externalScript.test(s)&&!enabledSellerCTA(s)&&disclosureNextTo(s)}
check("A/B same substantive offer section",()=>buyerSpan(A).length>3000&&buyerSpan(A)===buyerSpan(B));
check("A always disabled and disclosed",()=>staticSafety(A));
check("B always disabled and disclosed",()=>staticSafety(B));
check("no native external merchant hrefs all variants",()=>!sellerHref.test(A+B+H));
check("no forms/scripts/iframes/video preload",()=>sourceOnly.every(x=>!externalScript.test(x)));
check("B has poster accessible SVG semantics",()=>B.includes("poster-title")&&B.includes("poster-desc")&&B.includes('role="img"'));
check("B has complete concept, not fake playable film",()=>B.includes("OPTIONAL VIDEO CONCEPT")&&B.includes("Not a playable"));
check("B timed narrative six blocks",()=>[ "0–6s","6–13s","13–20s","20–27s","27–35s","35–42s"].every(t=>B.includes(t)));
check("VTT 6 cues",()=>VTT.match(/\d\d:\d\d:\d\d\.\d{3} -->/g)?.length===6);
check("VTT 42s exact",()=>VTT.includes("00:00:35.000 --> 00:00:42.000"));
check("privacy no email capture",()=>sourceOnly.every(x=>!/<input\b|<form\b|googletagmanager|facebook\.com\/tr|gtag\(/i.test(x)));
check("all pages noindex",()=>sourceOnly.every(x=>/name="robots" content="noindex,nofollow"/.test(x)));
check("all pages language and responsive",()=>sourceOnly.every(x=>x.includes('lang="en"')&&x.includes('name="viewport"')));
check("all pages visible focus",()=>sourceOnly.every(x=>x.includes(":focus-visible")));
check("all pages reduced motion",()=>sourceOnly.every(x=>x.includes("prefers-reduced-motion")));
check("hub has four streams",()=>["Perception &amp; Attention","History of Suggestion","Practice &amp; Reflection","Tools Under Review"].every(x=>H.includes(x)));
check("hub no seller recommendation activation",()=>!sellerHref.test(H)&&!/<button|<form|<script/i.test(H));
check("hub only existing first-party destinations",()=>H.includes("finalvestige.com/focus/")&&H.includes("puysegurs-animal-magnetism-files/"));
check("article original study identifiers",()=>["1500880","7707027","17488185"].every(x=>ART.includes(x)));
check("article no guaranteed product efficacy",()=>ART.includes("does not prove")&&ART.includes("seller"));
check("article no merchant shopping href",()=>!sellerHref.test(ART));
check("matrix all gates closed",()=>MATRIX.release_gates.length===28&&MATRIX.release_gates.every(x=>x.status==="HOLD"));
check("matrix claim provenance nonempty",()=>MATRIX.claims.length>=30&&MATRIX.claims.every(x=>x.sources?.length>=1));
check("matrix seller claim exclusions",()=>MATRIX.claims.filter(x=>x.status.includes("unsubstantiated")).length>=3);
check("funnel distinguishes affiliate click and sale",()=>["affiliate_click","merchant_paid_sale","refund_fee_settlement","qualified_landing"].every(x=>FUNNEL.includes(x)));
check("funnel missing denominator not treated as zero",()=>FUNNEL.includes("NOT COMPUTABLE")||FUNNEL.includes("not computable"));
check("funnel three real IDs not asserted",()=>FUNNEL.includes("UNMATCHED")&&FUNNEL.includes("Grok"));
check("no variant health outcome guarantee",()=>![A,B].some(x=>/proven Zen12 cures|guaranteed wealth|guaranteed focus|one hour of results guaranteed/i.test(x)));
check("no made-up merchant price in variants",()=>![A,B].some(x=>/\$\s*(?:37|87|99|19\.99)/.test(x)));
check("single live existing Focus funnel",()=>[A,B,H].every(x=>x.includes("finalvestige.com/focus/")));
check("A/B one exact prospective disclosure",()=>[A,B].every(x=>(x.match(/Affiliate disclosure:/g)||[]).length===1));
const mutations=[
["merchant href", s=>s.replace("</body>",'<a href="https://zen12.com/secret/">buy now</a></body>'),s=>sellerHref.test(s)],
["undeclared script",s=>s.replace("</body>","<script src='https://cdn.tracker.invalid'></script></body>"),s=>externalScript.test(s)],
["email capture",s=>s.replace("</body>","<form action='/x'><input name='email'></form></body>"),s=>externalScript.test(s)],
["enabled CTA",s=>s.replace(' type="button" disabled',' type="button"'),s=>enabledSellerCTA(s)],
["missing disclosure",s=>s.replace("Affiliate disclosure:","Prospective note:"),s=>!disclosureNextTo(s)],
["iframe",s=>s.replace("</body>","<iframe src='https://merchant.invalid'></iframe></body>"),s=>externalScript.test(s)],
["video autoplay",s=>s.replace("</body>","<video autoplay></video></body>"),s=>externalScript.test(s)],
["seller product href",s=>s.replace("</body>","<a href='https://inspire3.com/'>shop</a></body>"),s=>sellerHref.test(s)],
["hypnosis live seller href",s=>s.replace("</body>","<a href='https://hypnosislive.com/mental-skills/total-focus'>shop</a></body>"),s=>sellerHref.test(s)],
["brainwave seller href",s=>s.replace("</body>","<a href='https://brainwaveshots.com/focus-shot'>shop</a></body>"),s=>sellerHref.test(s)],
["merchant CTA renamed",s=>s.replace("Check the verified Zen12 offer","Buy now"),s=>enabledSellerCTA(s)],
["disclosure distant",s=>s.replace("Affiliate disclosure:","Affiliate disclosure:"+ "x".repeat(900)),s=>!disclosureNextTo(s)]
];
mutations.forEach(([name,mutate,detected])=>check("reject unsafe in-memory mutation "+name,()=>detected(mutate(A))));
const result={kind:"source_only",passed,total:passed+failed.length,failed,mutations:mutations.length,native_node:true,checkout_tested:false,wp_tested:false,accessibility_browser_tested:false,affiliate_approved:false};
process.stdout.write(JSON.stringify(result,null,2)+"\n");
if(failed.length)process.exitCode=1;

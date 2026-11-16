/** FV Mind R420 source-only safety verifier. Run: node mind/r420/verify-r420.cjs */
const fs=require('node:fs'),path=require('node:path');
const names=["THE_MISSING_SECOND_ATTENTIONAL_BLINK.md","ZEN12_A_TEXT_GUIDE.html","ZEN12_B_OPTIONAL_42S_CONCEPT.html","ZEN12_42S_CONCEPT.vtt","MIND_ARCHIVE_WORDPRESS_SOURCE_ONLY.html","CLAIM_SOURCE_PERMISSION_MATRIX.json","CONVERSION_ACCEPTANCE_CREATOR_FIT.md"];
const files=Object.fromEntries(names.map(n=>[n,fs.readFileSync(path.join(__dirname,n),'utf8')]));
const verify=function verify(files){
const A=files["ZEN12_A_TEXT_GUIDE.html"],B=files["ZEN12_B_OPTIONAL_42S_CONCEPT.html"],H=files["MIND_ARCHIVE_WORDPRESS_SOURCE_ONLY.html"],M=JSON.parse(files["CLAIM_SOURCE_PERMISSION_MATRIX.json"]),P=files["CONVERSION_ACCEPTANCE_CREATOR_FIT.md"],V=files["ZEN12_42S_CONCEPT.vtt"],I=files["THE_MISSING_SECOND_ATTENTIONAL_BLINK.md"];
const c=[];const ck=(name,ok)=>c.push([name,!!ok]);
const rules={
script:t=>!/<script\b|on(?:click|error|load|submit)\s*=/i.test(t),
merchant:t=>!/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(t),
form:t=>!/<form\b/i.test(t),
tracker:t=>!/googletagmanager\.com|google-analytics\.com|facebook\.net\/.*fbevents|pixel\.gif|datalayer\s*=/i.test(t),
autoplay:t=>!/\bautoplay\s*(?:=|\s|>)/i.test(t),
price:t=>!/\$\s*\d+(?:\.\d{2})?/i.test(t),
noindex:t=>/<meta name="robots" content="noindex,nofollow">/.test(t),
disclosure:t=>t.includes("If you purchase through a future authorized earning link, Final Vestige may earn a commission at no additional cost to you."),
disabled:t=>/<button\b[^>]*\bdisabled\b[^>]*aria-disabled="true"/.test(t),
adjacent:t=>t.indexOf("If you purchase through a future authorized earning link")>0&&t.indexOf('class="cta-disabled"')-t.indexOf("If you purchase through a future authorized earning link")<800&&t.indexOf('class="cta-disabled"')>t.indexOf("If you purchase through a future authorized earning link"),
main:t=>/<main\b/.test(t)&&/href="#main"/.test(t),
focus:t=>t.includes(":focus-visible"),mobile:t=>t.includes("@media(max-width:740px)"),reduced:t=>t.includes("prefers-reduced-motion:reduce"),
font:t=>!/@import|fonts\.googleapis\.com|<link[^>]*stylesheet/i.test(t)};
for(const [n,t] of [["A",A],["B",B],["Hub",H]])for(const [r,fn] of Object.entries(rules))ck(n+"/"+r,fn(t));
ck("A/B exact same buyer content",A.split('<main id="main" class="shell">')[1].split("</main>")[0]===B.split('<main id="main" class="shell">')[1].split('<section aria-labelledby="film">')[0]);
ck("B caption transcript",B.includes("Read the full optional film transcript")&&B.includes("No video file has been encoded"));
ck("B original svg",B.includes('viewBox="0 0 960 540"')&&B.includes('role="img"'));
ck("B not fake video",!/<video\b/i.test(B));
ck("VTT 6 cues",(V.match(/-->/g)||[]).length===6);
ck("VTT 42 second endpoint",V.includes("00:00:35.000 --> 00:00:42.000"));
ck("Hub four streams",["Perception &amp; Attention","History of Suggestion","Practice &amp; Reflection","Tools Under Review"].every(t=>H.includes(t)));
ck("Article wordcount",I.split(/\s+/).length>=2300);
ck("Article research source trail",["1500880","17488185","10.1111/j.1467-9280","puysegurs-animal-magnetism","ftc.gov"].every(t=>I.includes(t)));
ck("Matrix 34 claims",M.claim_count===34&&M.claims.length===34);
ck("Claims each source URL",M.claims.every(x=>x.source_url===M.source_urls[x.source_id]&&!!x.status));
ck("Matrix 28 HOLD gates",M.gate_count===28&&M.gates.length===28&&M.gates.every(x=>x.status==="HOLD"));
ck("No activation manifest",!M.activation_policy.merchant_anchor&&!M.activation_policy.affiliate_tracking&&!M.activation_policy.price_advertised);
ck("All exact seller routes",["ZEN_ORDER","ZEN_SECRET","ZEN","HL","BWS"].every(x=>!!M.source_urls[x]));
ck("Only real published creator routes",P.includes("change-blindness/")&&P.includes("mesmerism/")&&P.includes("NO public landing URL"));
ck("Cohort metrics",P.includes("7-day and 30-day")&&P.includes("settled_net_revenue_v1")&&P.includes("qualified_human_session_v1"));
ck("No invented FV SKU",P.includes("no matching rights-cleared"));
ck("Not computable",P.includes("NOT COMPUTABLE"));
const clean=t=>Object.values(rules).every(fn=>fn(t));
const mutant=[
["enable button",A.replace('disabled aria-disabled="true"','')],
["add merchant link",A.replace("</main>",'<a href="https://zen12.com/order">Buy</a></main>')],
["remove disclosure",A.replace(/<div class="disclosure">[\s\S]*?<\/div>/,"")],
["inject js",A.replace("</main>",'<script src="https://example.com/tracker.js"></script></main>')],
["inject form",A.replace("</main>",'<form action="/subscribe"></form></main>')],
["autoplay",A.replace("</main>","<video autoplay></video></main>")],
["invent price",A.replace("</main>","<p>$37.00</p></main>")],
["index page",A.replace("noindex,nofollow","index,follow")],
["analytics pixel",A.replace("</main>",'<img src="https://www.google-analytics.com/pixel.gif"></main>')],
["weak disclosure",A.replace("If you purchase through a future authorized earning link, Final Vestige may earn a commission at no additional cost to you.","Sponsored.")]
];
for(const [n,t] of mutant)ck("mutation rejected: "+n,!clean(t));
return {total:c.length,passed:c.filter(x=>x[1]).length,failures:c.filter(x=>!x[1]).map(x=>x[0]),checks:c};
};
const outcome=verify(files);for(const [name,pass] of outcome.checks)console.log((pass?'PASS ':'FAIL ')+name);console.log(JSON.stringify({passed:outcome.passed,total:outcome.total,failures:outcome.failures}));if(outcome.failures.length)process.exitCode=1;

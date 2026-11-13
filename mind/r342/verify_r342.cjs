// Mind R342 static acceptance test. Run: node mind/r342/verify_r342.cjs
// Source-only; not browser WCAG, live WordPress, merchant or conversion evidence.
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const read = (name) => fs.readFileSync(path.join(__dirname,name),"utf8");
const files = {
  a:read("ZEN12_A_TEXT_REVIEW.html"),
  b:read("ZEN12_B_FILM_REVIEW.html"),
  hub:read("MIND_HUB_WORDPRESS_REVIEW_ONLY.html"),
  poster:read("ZEN12_42S_POSTER.svg"),
  vtt:read("ZEN12_42S_CAPTIONS.vtt"),
  claims:JSON.parse(read("CLAIMS_AND_GATES.json")),
  guide:read("THE_TWELVE_MINUTE_FAIR_TEST.md"),
  dossier:read("CONVERSION_ACCEPTANCE.md")
};
const stripped = (html) => html.replace(/<title>[^<]*<\/title>/,"<title>same</title>");
const mainNoFilm = (html) => stripped(html).replace(/<section class="film"[\s\S]*?<\/section>/,"");
function checks(f) {
 let n=0;
 const yes=(cond,msg)=>{assert.ok(cond,msg);n++};
 yes(f.a.includes("noindex,nofollow")&&f.b.includes("noindex,nofollow"),"noindex");
 yes(stripped(f.a)===mainNoFilm(f.b),"A/B substantive copy parity");
 for(const h of [f.a,f.b]){
  yes(/<button\b[^>]*\bdisabled\b[^>]*>/.test(h),"native disabled CTA");
  yes(h.includes("If a future approved purchase link is used, Final Vestige may earn a commission"),"disclosure");
  yes(h.indexOf("may earn a commission")<h.indexOf("<button"),"disclosure adjacent before CTA");
  yes(!/<script\b|<iframe\b|<form\b|<input\b|on(?:click|load)=|autoplay\b|tracking.?pixel/i.test(h),"no tracking, autoplay or form");
  yes(!/href=["'][^"']*(zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(h),"merchant href withheld");
  yes(h.includes('href="https://finalvestige.com/focus/"'),"one Focus pathway");
  yes(!/\$\d|\b(?:guaranteed|clinically proven) (?:focus|results|benefits)\b/i.test(h),"no price/outcome promises");
 }
 yes(f.b.includes("ZEN12_42S_POSTER.svg")&&f.b.includes("ZEN12_42S_CAPTIONS.vtt"),"film poster captions");
 yes(f.b.includes("complete 42-second narration transcript"),"film transcript");
 yes(f.vtt.includes("00:00:35.000 --> 00:00:42.000"),"42s caption end");
 yes((f.vtt.match(/--> /g)||[]).length===6,"6 caption cues");
 yes(f.poster.includes('viewBox="0 0 1200 630"'),"original responsive poster");
 yes(f.hub.includes('href="https://finalvestige.com/focus/"'),"hub existing Focus");
 yes(!/<script\b|<form\b|autoplay\b/i.test(f.hub),"hub no active form/script");
 yes(Object.keys(f.claims.commercial_release_gates).length===20,"20 actual release gates");
 yes(Object.values(f.claims.commercial_release_gates).every(x=>x===false),"commercial holds closed");
 yes(f.claims.sources.length===20,"20 source/claim pairs");
 yes(f.claims.sources.every(x=>/^https:\/\//.test(x.url)),"source URLs explicit");
 yes(f.guide.split(/\s+/).length>=2000,"longform substantial");
 yes(f.guide.includes("not a Zen12 trial")||f.guide.includes("not a test of Zen12"),"independent science not vendor");
 yes(f.dossier.includes("NOT COMPUTABLE"),"revenue truth boundary");
 return n;
}
const passed=checks(files);
const mutate=[
 f=>({...f,a:f.a.replace(" disabled aria-describedby"," aria-describedby")}),
 f=>({...f,b:f.b.replace(" disabled aria-describedby"," aria-describedby")}),
 f=>({...f,a:f.a.replace("If a future approved purchase link is used, Final Vestige may earn a commission.","")}),
 f=>({...f,b:f.b.replace("ZEN12_42S_CAPTIONS.vtt","missing-caption.vtt")}),
 f=>({...f,b:f.b.replace("A quiet audio session can feel valuable.","Guaranteed concentration in 12 minutes.")}),
 f=>({...f,a:f.a.replace("</main>",'<script src="https://tracker.example/pixel.js"></script></main>')}),
 f=>({...f,a:f.a.replace("</main>",'<form action="https://third.example"><input name="email"></form></main>')}),
 f=>({...f,a:f.a.replace("Purchase link not yet available",'<a href="https://zen12.com/">Buy now</a>')}),
 f=>({...f,claims:{...f.claims,commercial_release_gates:{...f.claims.commercial_release_gates,issued_earning_url:true}}}),
 f=>({...f,vtt:f.vtt.replace("00:00:35.000 --> 00:00:42.000","00:00:35.000 --> 00:00:41.000")})
];
let rejected=0;
for(const fn of mutate){try{checks(fn(files))}catch(_e){rejected++}}
assert.equal(rejected,mutate.length,"unsafe mutation escaped checks");
console.log("R342 source-only PASS "+passed+" checks; "+rejected+"/"+mutate.length+" adversarial mutations rejected. Live/merchant/browser tests NOT RUN.");

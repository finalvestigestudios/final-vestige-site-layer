/* R323 source/claim/commercial release regression: node verify_r323.cjs; no third-party dependencies */
'use strict';
const fs=require('node:fs'),path=require('node:path');
function validate(f){
const errors=[], pick=(sub)=>f[Object.keys(f).find(k=>k.includes(sub))]||"", pass=(condition,label)=>{if(!condition)errors.push(label)};
const a=pick("ZEN12-A-"),b=pick("ZEN12-B-"),h=pick("MIND-RESEARCH"),art=pick("THE-FRACTION"),v=pick(".vtt"),doc=pick("OFFER-CONVERSION");let m;
try{m=JSON.parse(pick("MATRIX.json"))}catch(_){return ["JSON invalid"]}
pass(art.split(/\s+/).length>=1800&&art.includes("UNPUBLISHED")&&art.includes("Kleiser")&&art.includes("Yarrow"),"article length and evidence");
const start=b.indexOf('<div class="frame"><section id="optional-film"'),end=b.indexOf('</section></div>',start);
pass(start>=0&&end>start,"B film section");
if(start>=0&&end>start){const core=b.slice(0,start)+b.slice(end+16);const norm=s=>s.replace(/variant [AB], unpublished/g,"variant X, unpublished").replace(/data-variant="[AB]"/g,'data-variant="X"');pass(norm(a)===norm(core),"A/B parity")}
for(const [n,s] of [["A",a],["B",b],["hub",h]]){pass(!/<(?:script|form|iframe)\b|\bautoplay\b/i.test(s),n+" no unsafe embeds/forms");pass(!/href=["']https?:\/\/(?:zen12|hypnosislive|brainwaveshots|affiliates\.inspire3)\./i.test(s),n+" no seller links");pass(!/href=["'][^"']*(?:r323|THE-FRACTION-OF-A-SECOND)/i.test(s),n+" no draft public link");pass(!/All 48 recordings are guided meditation|meditates for you!|proven to improve focus/i.test(s),n+" seller claims blocked")}
for(const [n,s] of [["A",a],["B",b]]){const pos=s.indexOf("Zen12 purchase link withheld");pass(/<button type="button" disabled aria-disabled="true">/.test(s),n+" disabled");pass(pos>0&&s.slice(pos-550,pos).includes("earn a commission"),n+" adjacent disclosure");pass(s.includes("https://finalvestige.com/focus/"),n+" existing free route");pass(!/\$(?:37|87)(?:\.00|\.99)?\b/.test(s),n+" no promo price");pass(s.includes("guided meditation is <em>one</em>"),n+" package accuracy")}
pass(b.includes("has not been encoded")&&b.includes("original 42-second"),"static media truth");
pass(v.startsWith("WEBVTT")&&(v.match(/-->/g)||[]).length===6&&v.includes("00:00:42.000"),"timed captions");
pass(h.includes('id="fv-mind323"')&&h.includes("History of suggestion")&&h.includes("Tools under review"),"hub streams");
pass(m.sources.length===20&&m.claims.length===39&&m.claims.every(c=>c.support.every(id=>m.sources.some(s=>s.id===id))),"source refs");
pass(m.commercial_authorization.length===18&&m.commercial_authorization.every(g=>g.state==="HARD_HOLD"),"commercial hold");
pass(m.one_intended_offer.affiliate_earning_url===null&&m.one_intended_offer.merchant_partner_acceptance==="UNVERIFIED"&&m.one_intended_offer.exact_checkout_price===null,"partner hold");
pass(m.creator_paths.length===3&&m.creator_paths.every(p=>p.asset_id===null&&p.platform_post_url===null),"real media ID unknown");
pass(m.measurement_contract.north_star_value===null,"net rev not claimed");
pass(doc.includes("NOT COMPUTABLE")&&doc.includes("affiliate_click")&&doc.includes("PDF visibility")&&doc.includes("360/390/768/1440/1920"),"measurement and QA");
return errors;
}
function mutations(f){
const key=s=>Object.keys(f).find(k=>k.includes(s));const a=key("ZEN12-A"),b=key("ZEN12-B"),h=key("MIND-RESEARCH"),v=key(".vtt"),j=key("MATRIX.json"),art=key("THE-FRACTION"),doc=key("OFFER-CONVERSION");
const rep=(k,s)=>({...f,[k]:s});const json=fn=>{const o=JSON.parse(f[j]);fn(o);return rep(j,JSON.stringify(o))};
return [
["enable-buy",rep(a,f[a].replace('type="button" disabled aria-disabled="true"','type="button"'))],
["strip-disclosure",rep(b,f[b].replace('If a purchasing link is approved and you buy through it, Final Vestige may earn a commission at no additional cost to you.','No disclosure.'))],
["merchant-link",rep(b,f[b]+'<a href="https://zen12.com/secret/">Buy</a>')],
["script",rep(a,f[a]+'<script>bad()</script>')],
["form",rep(h,f[h]+'<form><input type=email></form>')],
["iframe",rep(a,f[a]+'<iframe src="https://test.example"></iframe>')],
["autoplay",rep(b,f[b]+'<video autoplay></video>')],
["different-copy",rep(b,f[b].replace("What the actual seller describes","An imaginary seller describes"))],
["no-captions",rep(v,"WEBVTT\n")],
["wrong-duration",rep(v,f[v].replace("00:00:42.000","00:00:43.000"))],
["gate-open",json(o=>o.commercial_authorization[0].state="APPROVED")],
["partner-accepted",json(o=>o.one_intended_offer.merchant_partner_acceptance="APPROVED")],
["orphan-citation",json(o=>o.claims[0].support.push("badsource"))],
["fictional-media",json(o=>o.creator_paths[0].asset_id="fiction")],
["invented-net-revenue",json(o=>o.measurement_contract.north_star_value=100)],
["false-guided",rep(a,f[a]+"<p>All 48 recordings are guided meditation.</p>")],
["fixed-price",rep(a,f[a]+"<p>Only $87.99 forever.</p>")],
["hub-merchant",rep(h,f[h]+'<a href="https://hypnosislive.com/">Buy now</a>')],
["unpublished-route",rep(h,f[h]+'<a href="/mind/r323/THE-FRACTION-OF-A-SECOND">Live</a>')],
["article-truncated",rep(art,f[art].slice(0,300))],
["net-revenue-misrepresented",rep(doc,f[doc].replace(/NOT COMPUTABLE/g,"CONFIRMED $100"))]
];
}
const names=["THE-FRACTION-OF-A-SECOND-YOUR-EYES-NEVER-SHOW-YOU-UNPUBLISHED.md","ZEN12-A-TRUTHFUL-TEXT-PRESELL-REVIEW.html","ZEN12-B-OPTIONAL-42S-ORIGINAL-STORYBOARD-REVIEW.html","ORIGINAL-42S-CAPTIONS.vtt","MIND-RESEARCH-ROOM-WORDPRESS-HTML-REVIEW-ONLY.html","SOURCE-CLAIM-AND-AUTHORIZATION-MATRIX.json","OFFER-CONVERSION-RELEASE-AND-ATTRIBUTION-ACCEPTANCE.md"];
const files=Object.fromEntries(names.map(n=>[n,fs.readFileSync(path.join(__dirname,n),'utf8')]));
const errors=validate(files);
if(errors.length){console.error('R323 baseline FAIL',errors);process.exit(1)}
const cases=mutations(files),escapes=cases.filter(([n,c])=>validate(c).length===0).map(([n])=>n);
if(escapes.length){console.error('R323 mutation FAIL',escapes);process.exit(1)}
console.log('R323 PASS: baseline and '+cases.length+'/'+cases.length+' deliberately unsafe mutations rejected (source only)');

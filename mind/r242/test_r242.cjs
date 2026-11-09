#!/usr/bin/env node
"use strict";
/**
 * R242 isolated source-commit integrity and commercial no-activation regression.
 * Native use: node mind/r242/test_r242.cjs
 * Requires only Node built-ins. Assertions do not constitute live browser/checkout testing.
 * SHA-1 here matches Git's blob identity, not a password hash or a signature.
 * Source citations may appear as literal text in Markdown. NO active merchant anchors
 * may appear in the WordPress-compatible buyer/hub previews before approval.
 */
const fs=require("node:fs"), path=require("node:path"), crypto=require("node:crypto"), assert=require("node:assert/strict");
const dir=__dirname;
const inherited=path.resolve(dir,"../r241");
const pins={
  "r241/test_r241.mjs":"292a139b734ae737d6c6468a57310e59d37a947b",
  "r241/FOCUS-SHOT-CLAIM-SOURCE-AUTHORIZATION.json":"300c450c231885631815233e570da54cd7449b87",
  "r241/focus-shot-presell-WP-SOURCE-UNPUBLISHED.html":"d7b110662f9f2e6d456fc6d372afe85d746c4371",
  "r241/THE-FOUR-HOUR-FOCUS-PROMISE-UNPUBLISHED.md":"f2c23ff394f267e56c602389ee9f95084ea97cf7",
  "r241/CONVERSION-REVENUE-ACCEPTANCE.md":"cd14d638360d3469a3930c37a2069fbcb96959da",
  "r242/THE-FREQUENCY-IS-NOT-THE-RESULT-UNPUBLISHED.md":"6d1c73b3ab295a1a194c2294d83e2158b41e70c7",
  "r242/PRODUCT-CLAIM-SOURCE-COMMERCIAL-GATES.json":"b088a98e6f4ed56c14e746dbabc46011f02875f2",
  "r242/MIND-ARCHIVE-FOUR-STREAM-WP-PREVIEW-UNPUBLISHED.html":"94d2cff6f58c88277d352e6b08e88504778dda28"
};
function read(rel){return fs.readFileSync(path.resolve(dir,"..",rel),"utf8")}
function gitBlob(text){const b=Buffer.from(text,"utf8");return crypto.createHash("sha1").update(Buffer.from("blob "+b.length+"\0")).update(b).digest("hex")}
for(const [p,sha] of Object.entries(pins)) assert.equal(gitBlob(read(p)),sha,"Immutable reviewed blob drift: "+p);
const r241html=read("r241/focus-shot-presell-WP-SOURCE-UNPUBLISHED.html");
const hub=read("r242/MIND-ARCHIVE-FOUR-STREAM-WP-PREVIEW-UNPUBLISHED.html");
const r241=JSON.parse(read("r241/FOCUS-SHOT-CLAIM-SOURCE-AUTHORIZATION.json"));
const matrix=JSON.parse(read("r242/PRODUCT-CLAIM-SOURCE-COMMERCIAL-GATES.json"));
const article=read("r242/THE-FREQUENCY-IS-NOT-THE-RESULT-UNPUBLISHED.md");
const permittedDomains=new Set(["finalvestige.com","www.ftc.gov","pmc.ncbi.nlm.nih.gov","pubmed.ncbi.nlm.nih.gov","doi.org"]);
const merchantDomains=["inspire3.com","zen12.com","brainwaveshots.com","hypnosislive.com","awin1.com","payhip.com"];
function testHtml(h,{disclosureId}){
  assert.ok(!/<\s*(script|form|iframe|video|audio|input|object|embed|link|meta|base)\b/i.test(h),"Forbidden executable/capture/media tag");
  assert.ok(!/\bon[a-z]{3,}\s*=/i.test(h),"Inline event handler");
  assert.ok(!/\b(?:javascript|data|vbscript)\s*:/i.test(h),"Unsafe URL scheme");
  assert.ok(!/\b(?:action|formaction|srcdoc)\s*=/i.test(h),"Unexpected navigation or HTML injection");
  const anchors=[...h.matchAll(/<a\b([^>]*)>/gi)];
  for(const a of anchors){
    const m=a[1].match(/\bhref\s*=\s*(["'])(.*?)\1/i);
    assert.ok(m,"Anchor missing quoted href");
    const dest=m[2];
    assert.ok(dest.startsWith("https://")||dest.startsWith("#"),"Unapproved link scheme");
    if(dest[0]==="#") continue;
    const u=new URL(dest);
    assert.ok(permittedDomains.has(u.hostname),"Unapproved external hostname: "+u.hostname);
    assert.ok(!merchantDomains.some(x=>u.hostname===x||u.hostname.endsWith("."+x)),"Merchant destination active");
    assert.ok(!/[\?&](?:email|token|session_id|user_id)=/i.test(u.search),"Potential PII attribution");
  }
  const buttons=[...h.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button\s*>/gi)];
  assert.equal(buttons.length,1,"Exactly one held purchasing control");
  assert.ok(/\sdisabled(?:\s|=|$)/i.test(buttons[0][1]),"Control must genuinely be disabled, aria-disabled alone insufficient");
  assert.ok(/\btype\s*=\s*["']button["']/i.test(buttons[0][1]));
  assert.ok(/aria-describedby\s*=\s*["']([^"']+)["']/i.test(buttons[0][1]));
  assert.ok(buttons[0][1].includes('aria-describedby="'+disclosureId+'"'));
  const disclosurePos=h.indexOf('id="'+disclosureId+'"');
  const buttonPos=h.indexOf(buttons[0][0]);
  assert.ok(disclosurePos>=0 && buttonPos>disclosurePos && buttonPos-disclosurePos<1500,"Disclosure must be directly adjacent and precede CTA");
  assert.ok(/may earn a commission/i.test(h.slice(disclosurePos,buttonPos)));
  assert.ok(/at no additional cost/i.test(h.slice(disclosurePos,buttonPos)));
  assert.ok(/no (?:earning link|affiliate|live purchase)/i.test(h.slice(disclosurePos,buttonPos)));
  assert.ok(h.includes("https://finalvestige.com/focus/"),"Preserve one original Focus funnel");
  assert.ok(/:focus-visible/.test(h)&&/prefers-reduced-motion/.test(h)&&/max-width/.test(h),"Baseline a11y/reflow CSS");
  assert.ok(!/autoplay|<marquee|<blink/i.test(h),"No autoplay/attention capture");
  return true;
}
function testMatrix(m,expectedSources,expectedClaims){
 assert.equal(m.commercial_activation??m.public_activation,false);
 const s=m.sources, c=m.claims, g=m.commercial_release_gates;
 assert.equal(s.length,expectedSources); assert.equal(c.length,expectedClaims);assert.equal(g.length,16);
 const ids=new Set(s.map(x=>x.id)), cids=new Set(c.map(x=>x.id)), gids=new Set(g.map(x=>x.id));
 assert.equal(ids.size,s.length,"Unique source IDs");
 assert.equal(cids.size,c.length,"Unique claim IDs");
 assert.equal(gids.size,g.length,"Unique release gate IDs");
 for(const a of s) { assert.ok(a.url.startsWith("https://")); assert.ok(a.kind); }
 for(const x of c) {assert.ok(ids.has(x.source_id));assert.ok(x.statement.length>=18);assert.ok(x.status.length>=4); assert.ok(x.status!=="VERIFIED_EFFICACY");}
 for(const x of g) { assert.equal(x.status,"HARD_HOLD");assert.equal(x.verified,false); }
 if(m.affiliate_url!==undefined) assert.equal(m.affiliate_url,null);
 if(m.permission_evidence!==undefined) assert.equal(m.permission_evidence.issued_url,null);
 if(m.offer_eligibility!==undefined)assert.equal(m.offer_eligibility,"NONE_VERIFIED");
 if(m.live_revenue!==undefined)for(let [k,v] of Object.entries(m.live_revenue))assert.equal(v,null,"Unverified live finance "+k);
 if(m.measurement!==undefined){
  assert.equal(m.measurement.no_pii,true); assert.equal(m.measurement.affiliate_click_not_sale,true);
  assert.equal(m.measurement.net_revenue_per_1000_qualified_human_sessions,null);
  assert.equal(m.measurement.confirmed_paid_orders,null);
  assert.equal(m.measurement.cleared_affiliate_sales,null);
 }
 return true;
}
testHtml(r241html,{disclosureId:"close-disclosure"});
testHtml(hub,{disclosureId:"mind242-disclosure"});
testMatrix(r241,11,22);testMatrix(matrix,15,28);
assert.match(article,/The Frequency Is Not the Result/);
assert.match(article,/seller claim/i);
assert.match(article,/Puységur/);
assert.match(article,/Sev[e]?n Day Focus Fieldbook/);
assert.match(article,/https:\/\/zen12.com\/hnp/);
assert.match(article,/https:\/\/brainwaveshots.com\/focus-shot/);
assert.match(article,/https:\/\/hypnosislive.com\/mental-skills\/total-focus/);
function rejects(fn,description){assert.throws(fn,undefined,description);return 1}
let mutations=0;
const by=(html,find,replacement)=>{assert.ok(html.includes(find),"Fixture must match real source");return html.replace(find,replacement)};
for(const [h,id] of [[r241html,"close-disclosure"],[hub,"mind242-disclosure"]]){
 const cases=[
  x=>x+'<button type="button">Buy</button>',
  x=>x.replace(/\sdisabled(?=[\s>])/i,''),
  x=>x.replace(/\sdisabled(?=[\s>])/i,' aria-disabled="true"'),
  x=>x.replace(/may earn a commission/i,'offers a guaranteed cure'),
  x=>x.replace('at no additional cost','at an added cost'),
  x=>x.replace('aria-describedby="'+id+'"','aria-describedby="missing"'),
  x=>x.replace('id="'+id+'"','id="lostDisclosure"'),
  x=>x+'<script src="https://example.test/x.js"></script>',
  x=>x+'<form><input name="email"></form>',
  x=>x+'<iframe srcdoc="<script>alert(1)</script>"></iframe>',
  x=>x+'<video autoplay></video>',
  x=>x+'<a href="javascript:alert(1)">Go</a>',
  x=>x+'<a href="data:text/html,x">Go</a>',
  x=>x+'<a href="https://zen12.com/hnp">Seller</a>',
  x=>x+'<a href="https://evil.example/give?email=a@b.test">Leak</a>',
  x=>x+'<a href="https://payhip.com/b/xxxx">Unverified product</a>',
  x=>x+'<a href="https://example.com/shop">Unapproved seller</a>',
  x=>x+'<div onclick="location.href=1">Track</div>',
  x=>x+'<button formaction="https://evil.example">Go</button>',
  x=>x.replace('https://finalvestige.com/focus/','https://external.example/focus/'),
  x=>x.replace(':focus-visible',':focus-only'),
  x=>x.replace('prefers-reduced-motion','prefers-super-motion'),
  x=>x+'<a href="https://www.ftc.gov/?token=private">Tracking leak</a>'
 ];
 for(const t of cases)mutations+=rejects(()=>testHtml(t(h),{disclosureId:id}),"unsafe html fixture");
}
for(const [m,sc,cc] of [[r241,11,22],[matrix,15,28]]){
 const cases=[
  x=>{x.commercial_release_gates[0].status="APPROVED"},
  x=>{x.commercial_release_gates[8].verified=true},
  x=>{x.commercial_release_gates.push({...x.commercial_release_gates[0]})},
  x=>{x.commercial_release_gates[5].id=x.commercial_release_gates[0].id},
  x=>{x.claims[0].source_id="NONEXISTENT"},
  x=>{x.claims[1].id=x.claims[0].id},
  x=>{x.claims.splice(0,1)},
  x=>{x.sources.splice(0,1)},
  x=>{x.sources[0].url="http://bad.example"},
  x=>{x.claims[0].status="VERIFIED_EFFICACY"},
  x=>{if(x.permission_evidence)x.permission_evidence.issued_url="https://unapproved.example";else x.affiliate_url="https://unapproved.example"}
 ];
 for(const tweak of cases){const v=JSON.parse(JSON.stringify(m));tweak(v);mutations+=rejects(()=>testMatrix(v,sc,cc),"unsafe matrix fixture")}
}
{let m=structuredClone(matrix);m.measurement.confirmed_paid_orders=1;mutations+=rejects(()=>testMatrix(m,15,28),"fake paid order")}
{let m=structuredClone(matrix);m.measurement.affiliate_click_not_sale=false;mutations+=rejects(()=>testMatrix(m,15,28),"clicked equals sold")}
{let m=structuredClone(matrix);m.measurement.no_pii=false;mutations+=rejects(()=>testMatrix(m,15,28),"PII event")}
console.log("R242 PASS: 8 exact Git blob pins; inherited+new source matrix and held-CTA baseline; "+mutations+"/"+mutations+" unsafe synthetic modifications rejected. SOURCE ONLY — not browser/CI/WordPress/checkout or sales.");

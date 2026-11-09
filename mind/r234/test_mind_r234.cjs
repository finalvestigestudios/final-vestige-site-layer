/* Mind R234 source checks. Run: node mind/r234/test_mind_r234.cjs
   This test is intentionally local and read-only; it does not authorize live publication. */
"use strict";
const fs=require("node:fs"), path=require("node:path"), assert=require("node:assert/strict");
const dir=__dirname;
const files={
 a:fs.readFileSync(path.join(dir,"zen12-A-WHITE-BEAR-TEXT-UNPUBLISHED.html"),"utf8"),
 b:fs.readFileSync(path.join(dir,"zen12-B-WHITE-BEAR-OPTIONAL-VIDEO-CONCEPT-UNPUBLISHED.html"),"utf8"),
 article:fs.readFileSync(path.join(dir,"THE-BEAR-YOU-CANNOT-UNTHINK-UNPUBLISHED.md"),"utf8"),
 matrix:JSON.parse(fs.readFileSync(path.join(dir,"SOURCE-CLAIM-COMMERCE-GATES.json"),"utf8")),
 captions:fs.readFileSync(path.join(dir,"WHITE-BEAR-42S-CAPTIONS-PROPOSAL.vtt"),"utf8"),
 plan:fs.readFileSync(path.join(dir,"OFFER-FIRST-CREATOR-AB-MEASUREMENT-RELEASE.md"),"utf8")
};
const expectedStatuses=["SUPPORTED_ABSTRACT","SUPPORTED_ABSTRACT","SUPPORTED_ABSTRACT","THEORETICAL_MODEL","SUPPORTED_ABSTRACT","SUPPORTED_ABSTRACT","SELLER_ONLY","SELLER_ONLY","SELLER_ONLY","UNSUBSTANTIATED_PRODUCT_CLAIM","UNSUBSTANTIATED_PRODUCT_CLAIM","UNVERIFIED","UNVERIFIED","NOT_AUTHENTICATED","NOT_AUTHENTICATED","NOT_AUTHENTICATED","NOT_VERIFIED","FALSE_CONFLATION","NOT_COMPUTABLE"];
function violations(f){
 const errors=[];
 const require=(ok,msg)=>{if(!ok)errors.push(msg)};
 const m=f.matrix;
 require(m.status==="UNPUBLISHED_HARD_HOLD","matrix status");
 require(Array.isArray(m.sources)&&m.sources.length===11,"source count");
 require(Array.isArray(m.claims)&&m.claims.length===19,"claim count");
 require(Array.isArray(m.gates)&&m.gates.length===16,"gate count");
 if(Array.isArray(m.sources))m.sources.forEach((s,i)=>{
  require(s.id==="S"+String(i+1).padStart(2,"0"),"source id "+i);
  require(/^https:\/\//.test(s.url),"source URL "+i);
 });
 if(Array.isArray(m.claims))m.claims.forEach((c,i)=>{
  require(c.id==="C"+String(i+1).padStart(2,"0"),"claim id "+i);
  require(c.status===expectedStatuses[i],"claim status "+i);
  require(Array.isArray(c.sources),"claim refs "+i);
 });
 if(Array.isArray(m.gates))m.gates.forEach((g,i)=>{
  require(g.id==="G"+String(i+1).padStart(2,"0"),"gate id "+i);
  require(g.status==="HARD_HOLD","gate status "+i);
 });
 require(m.visitor_measurement.pii==="NO"&&m.visitor_measurement.client_script==="NONE","privacy status");
 require(m.ab_test.exposure==="NOT_LIVE","experiment status");
 require(/white bear/i.test(f.article)&&/31 studies/.test(f.article),"research context");
 require(!/https:\/\/(?:www\.)?(?:inspire3|zen12|hypnosislive|brainwaveshots)\.com/i.test(f.article.slice(0,f.article.indexOf("**Sources and verification notes"))),"no merchant links in article narrative");
 const core=(s)=>{const a=s.indexOf('<section class="guide"');const b=s.indexOf("</section>",a);return a<0||b<0?"":s.slice(a,b+10)};
 require(core(f.a).length>6000&&core(f.a)===core(f.b),"A/B core identical");
 for(const [name,html]of[["A",f.a],["B",f.b]]){
  require(/<html lang="en">/.test(html)&&/name="viewport"/.test(html),"lang viewport "+name);
  require(/name="robots" content="noindex,nofollow"/.test(html),"unpublished metadata "+name);
  require(/<button[^>]*\bdisabled\b[^>]*>/.test(html),"native disabled CTA "+name);
  require(/id="affiliate-disclosure"/.test(html)&&/commission at no additional cost/.test(html),"adjacent disclosure "+name);
  require(!/<(?:script|form|iframe|video|audio)\b/i.test(html),"no executable, form, media "+name);
  require(!/<a[^>]+href\s*=\s*["'](?:https?:)?\/\/(?:www\.)?(?:inspire3|zen12|hypnosislive|brainwaveshots)\.com/i.test(html),"no clickable merchant "+name);
  require(!/(?:href\s*=\s*["']\s*javascript:|onclick\s*=|data-[^=]*affiliate)/i.test(html),"no injected redirect "+name);
  require(/https:\/\/finalvestige.com\/focus\//.test(html),"existing Focus "+name);
  require(/prefers-reduced-motion:reduce/.test(html),"reduced motion "+name);
  require(/:focus-visible/.test(html),"focus visible "+name);
 }
 require(!f.a.includes('class="video-proposal"'),"text arm video excluded");
 require(f.b.includes('class="video-proposal"')&&f.b.includes("Not a video player"),"B honestly static");
 require(f.b.includes("<details>")&&f.b.includes("complete 42-second film transcript"),"B readable transcript");
 require(f.captions.startsWith("WEBVTT"),"valid caption header");
 const slots=[...f.captions.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];
 require(slots.length===6,"six VTT cues");
 const seconds=t=>{const a=t.split(":");return +a[0]*3600+(+a[1])*60+(+a[2])};
 if(slots.length===6){
  require(seconds(slots[0][1])===0,"captions start 0");
  require(seconds(slots[5][2])===42,"captions end 42");
  slots.forEach((x,i)=>{require(seconds(x[2])>seconds(x[1]),"cue positive "+i);if(i)require(seconds(slots[i-1][2])===seconds(x[1]),"cue contiguous "+i)});
 }
 require(/NOT COMPUTABLE/.test(f.plan)&&/NOT LIVE/.test(f.plan),"paid conversion caution");
 require(/TASK-008/.test(f.plan)&&/Issue #150/.test(f.plan),"ownership scope");
 return errors;
}
const baseline=violations(files);assert.equal(baseline.length,0,"baseline violations: "+baseline.join("; "));
const mutations=[
 f=>f.a=f.a.replace("button type=\"button\" disabled","button type=\"button\""),
 f=>f.b=f.b.replace("button type=\"button\" disabled","button type=\"button\""),
 f=>f.a=f.a.replace("id=\"affiliate-disclosure\"","id=\"wrong-disclosure\""),
 f=>f.a=f.a.replace("</main>","<script src=\"https://tracker.invalid/x.js\"></script></main>"),
 f=>f.b=f.b.replace("</main>","<form><input type=\"email\"></form></main>"),
 f=>f.a=f.a.replace("</main>","<a href=\"https://zen12.com/hnp\">buy</a></main>"),
 f=>f.b=f.b.replace("</main>","<a href=\"https://inspire3.com/\">buy</a></main>"),
 f=>f.b=f.b.replace("Not a video player","Watch this actual film"),
 f=>f.b=f.b.replace("42-second film transcript","film transcript omitted"),
 f=>f.captions=f.captions.replace("00:00:42.000","00:00:41.000"),
 f=>f.captions=f.captions.replace("00:00:14.000\nIn a","00:00:15.000\nIn a"),
 f=>f.matrix.gates[0].status="AUTHORIZED",
 f=>f.matrix.gates[15].status="APPROVED",
 f=>f.matrix.claims[9].status="INDEPENDENTLY_PROVEN",
 f=>f.matrix.claims[13].status="APPROVED",
 f=>f.matrix.sources.splice(0,1),
 f=>f.matrix.visitor_measurement.pii="YES",
 f=>f.matrix.ab_test.exposure="LIVE",
 f=>f.article=f.article.replace("31 studies","many studies"),
 f=>f.plan=f.plan.replace("NOT COMPUTABLE","COMPUTABLE")
];
let rejected=0;
for(const mutate of mutations){const f=structuredClone(files);mutate(f);if(violations(f).length)rejected++}
assert.equal(rejected,mutations.length,"unsafe mutation not rejected");
console.log(JSON.stringify({result:"PASS",baseline:baseline.length,mutations_rejected:rejected,mutations_total:mutations.length,scope:"source static, no browser/commerce tests"}));

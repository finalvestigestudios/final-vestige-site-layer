"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const {buildIssue}=require("./render_gutenberg.cjs");
const p=path.join(__dirname,"..","campaign-2026-mind");const m=JSON.parse(fs.readFileSync(path.join(p,"manifest.json"),"utf8"));
const slugs=["01-the-mind-is-not-a-camera","02-before-hypnosis-had-a-name","03-the-twelve-minute-question","04-the-hatch-and-the-spark","05-before-you-press-play","06-the-evidence-log"];
let passes=0;const check=(ok,msg)=>{assert.ok(ok,msg);passes++};
check(m.issues.length===6,"six canonical issues");check(m.issues.filter(i=>i.kind==="editorial").length===4,"4 editorial");
for(let j=0;j<6;j++){let md=fs.readFileSync(path.join(p,"issues",slugs[j]+".md"),"utf8"),issue=m.issues[j],spec=buildIssue(md,issue),saved=fs.readFileSync(path.join(__dirname,"issue_0"+(j+1)+"_wp_blocks.html"),"utf8");check(spec.html===saved,"exact WordPress block parity");check(saved.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]")&&saved.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"),"hard stop footer");check(!/<(?:script|iframe|img|form|video|input|style)\b/i.test(saved),"no active content");check(spec.send_subscription===false&&spec.proposed_post_status==="draft","never live");check(spec.hrefs.every(u=>u.startsWith("https://finalvestige.com/")),"no merchant href");check(issue.kind==="editorial" ? spec.hrefs.includes(issue.editorial_cta) : saved.includes("[[APPROVED_"),"CTA guarded");let changed={...issue,subject:"Not the canonical subject"};assert.throws(()=>buildIssue(md,changed));passes++;
}
check(!m.issues.some(i=>i.merchant_affiliate_url),"no affiliate URLs");console.log("PASS "+passes+" native Node source-parity tests. UNSENT, NOT published.");

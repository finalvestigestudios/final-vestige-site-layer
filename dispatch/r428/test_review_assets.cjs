"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const m=JSON.parse(fs.readFileSync(path.join(__dirname,"manifest.json"),"utf8"));let passed=0;
function test(v,label){assert.ok(v,label);passed++}
test(m.status==="HOLD_UNSENT_UNADOPTED"&&!m.allow_send&&!m.allow_publish,"closed release");
test(m.allocation.editorial.length===4&&m.allocation.commercial.join(",")==="3,5","4:2 preserved");
for(const k of ["merchant_email_permission","earning_links_issued","warmup_guides_live","postal_verified","unsubscribe_verified","jetpack_preview_verified","founder_final_send_approval"])test(m[k]===false,k+" unverified");
for(const e of m.issues){const b="issue_0"+e.number;const md=fs.readFileSync(path.join(__dirname,b+"_candidate.md"),"utf8"),txt=fs.readFileSync(path.join(__dirname,b+"_preview.txt"),"utf8"),html=fs.readFileSync(path.join(__dirname,b+"_preview.html"),"utf8");for(const field of ["subject","preheader"])test([md,txt,html].every(s=>s.includes(e[field])),"subject/preheader parity");test(!/<(script|form|iframe|img|video)\b/i.test(html),"no active rich content");test(!/[?&](aff|affiliate|ref|utm_source)=/i.test(html),"no tracking/affiliate query");test((html.match(/<h1\b/g)||[]).length===1,"single heading");test((html.match(/role="presentation"/g)||[]).length>=2,"table layout");test(html.includes("INACTIVE"),"CTA disabled");for(const p of ["[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"])test([md,txt,html].every(s=>s.includes(p)),"unresolved legal token");for(const url of e.source_urls)test([md,txt,html].every(s=>s.includes(url)),"full source parity");}
console.log("PASS "+passed+" review-source checks. DOES NOT approve sending.");

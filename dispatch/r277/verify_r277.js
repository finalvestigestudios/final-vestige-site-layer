/* Dispatch R277 — pure offline bundle validator; never sends, never writes WP.
   Usage native: node dispatch/r277/verify_r277.js
   For isolated source-only evaluation call validateR277(files) with exact texts. */
function validateR277(files) {
 const errors=[];
 const must=(condition,reason)=>{if(!condition) errors.push(reason);};
 const md=files["issue04_optional.md"]||"",txt=files["issue04_optional.txt"]||"",html=files["issue04_optional.html"]||"";
 let ledger;try{ledger=JSON.parse(files["merchant_and_consent_ledger.json"]||"{}")}catch(e){ledger={};errors.push("invalid-json")}
 const subject="Signed at five. Silent at eleven.";
 const cta="https://finalvestige.com/free-resources/the-box-behind-the-citation/";
 const sources=["nationalarchives.gov.uk","theworldwar.org","history.navy.mil","nam.ac.uk"];
 must(md.includes(subject)&&txt.includes(subject)&&html.includes(subject),"subject missing");
 must(md.includes("CAB 23/14/46")&&txt.includes("CAB 23/14/46")&&html.includes("CAB 23/14/46"),"primary catalog reference missing");
 must([md,txt,html].every(s=>s.includes(cta)),"CTA parity missing");
 for(const src of sources)must([md,txt,html].every(s=>s.includes(src)),"source missing "+src);
 must([md,txt,html].every(s=>s.includes("[[FV_VERIFIED_BUSINESS_POSTAL_ADDRESS_REQUIRED]]")&&s.includes("[[ACTUAL_JETPACK_RENDERED_UNSUBSCRIBE_REQUIRED]]")),"compliance holds removed");
 must([md,txt,html].every(s=>/NOT_ADOPTED|NOT ADOPTED|NOT ADOPTED/.test(s)),"adoption guard removed");
 must(/lang="en"/.test(html)&&/role="presentation"/.test(html)&&/<h1/.test(html)&&/max-width:600px/.test(html),"accessibility/email shell missing");
 must(!/<script\b|<form\b|<iframe\b|<img\b|tracking-pixel|http-equiv="refresh"/i.test(html),"active content/resource");
 must((html.match(/href="https:\/\/finalvestige\.com\/free-resources\/the-box-behind-the-citation\//g)||[]).length===1,"multiple CTA in HTML");
 must((md.match(/\*\*One editorial CTA:\*\*/g)||[]).length===1,"multiple editorial CTA labels");
 must(!/\?utm_|aff_id=|ref=affiliate|affiliate_id=/i.test(md+html+txt),"unapproved earning/tracking link");
 must(ledger?.status==="HOLD_UNSENT"&&ledger?.draft_ratio?.commercial_hard_hold?.join(",")==="3,5","4:2 allocation lost");
 must(ledger?.conversion_contract?.net_revenue_per_1000_qualified_sessions===null,"numerical paid revenue fabricated");
 must(ledger?.canonical_production?.eligible_email_recipients===null,"recipient count fabricated");
 must(Array.isArray(ledger?.offers)&&ledger.offers.length===2&&ledger.offers.every(o=>o.email_permission_verified===false&&o.earning_link_verified===false),"merchant authorizations invented");
 must(ledger?.blockers&&Object.values(ledger.blockers).every(x=>x===false),"release gate activated");
 must((files["review_release_r277.md"]||"").includes("HOLD_COMPLIANCE"),"compliance handoff missing");
 return {pass:errors.length===0,errors,checks:18+sources.length};
}
if(typeof module!=="undefined"&&module.exports) module.exports={validateR277};
if(typeof require!=="undefined"&&require.main===module){
 const fs=require("fs"),path=require("path");
 const root=__dirname, names=["issue04_optional.md","issue04_optional.txt","issue04_optional.html","merchant_and_consent_ledger.json","review_release_r277.md"];
 const files=Object.fromEntries(names.map(n=>[n,fs.readFileSync(path.join(root,n),"utf8")]));
 const result=validateR277(files);
 if(!result.pass){process.stderr.write(result.errors.join("\n")+"\n");process.exitCode=1;}
 else process.stdout.write("R277 offline bundle PASS\n");
}

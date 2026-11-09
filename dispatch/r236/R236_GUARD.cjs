"use strict";
/* R236 read-only source safety gate. Does not send emails, contact users or activate links.
 * node dispatch/r236/R236_GUARD.cjs from repository root. Requires Node 18+.
 */
function inspect(files) {
  const md=files.md, txt=files.txt, html=files.html, evidence=files.evidence;
  let checks=0;
  function ok(condition, message) { checks++; if (!condition) throw new Error("R236 HOLD: "+message); }
  ok(md.includes("UNSENT DRAFT / HOLD_MERCHANT"),"markdown must remain unsent");
  ok(txt.includes("UNSENT DRAFT / HOLD_MERCHANT"),"plaintext must remain unsent");
  ok(html.includes("REVIEW-ONLY SPECIMEN"),"html must announce inert status");
  ok(md.includes("Content type:** commercial-review-pending"),"maintain commercial classification");
  const subject="Before you trust a focus recording, ask this";
  const preheader="A 33-minute seller offer, a historical lesson, and a five-minute evidence check.";
  ok([md,txt,html].every(s=>s.includes(subject)), "subject not aligned in variants");
  const actualTitle=(html.match(/<h1[^>]*>([^<]+)<\/h1>/i)||[])[1];
  ok(actualTitle===subject, "HTML displayed heading must exactly match approved subject");
  ok(md.includes("**Subject:** "+subject) && txt.includes("Subject: "+subject), "subject metadata must match exactly");
  ok(md.includes(preheader) && txt.includes(preheader), "preheader not aligned");
  ok((md.match(/APPROVED_TOTAL_FOCUS_WARMUP_GUIDE_URL_REQUIRED/g)||[]).length===1, "one inactive primary CTA in markdown");
  ok((txt.match(/APPROVED_TOTAL_FOCUS_WARMUP_GUIDE_URL_REQUIRED/g)||[]).length===1, "one inactive primary CTA in text");
  ok((html.match(/APPROVED_TOTAL_FOCUS_WARMUP_GUIDE_URL_REQUIRED/g)||[]).length===1, "one inactive primary CTA in HTML");
  ok(md.includes("**Commercial disclosure (prospective):") && md.indexOf("Commercial disclosure (prospective)") < md.indexOf("READ THE INDEPENDENT TOTAL FOCUS GUIDE"), "explicit markdown commercial disclosure precedes proposal CTA");
  ok(txt.includes("Commercial disclosure (prospective):") && txt.indexOf("Commercial disclosure (prospective)") < txt.indexOf("READ THE INDEPENDENT TOTAL FOCUS GUIDE"), "explicit plaintext disclosure precedes proposed CTA");
  ok(html.includes("Commercial disclosure (prospective):") && html.indexOf("Commercial disclosure (prospective)") < html.indexOf("READ THE INDEPENDENT TOTAL FOCUS GUIDE"), "explicit HTML disclosure precedes proposed CTA");
  for (const s of [md,txt,html]) {
    ok(s.includes("VALID_POSTAL_ADDRESS_REQUIRED"),"missing physical-address hard stop");
    ok(s.includes("JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED"),"missing unsubscribe hard stop");
    ok(s.includes("hypnosislive.com/mental-skills/total-focus"),"missing exact merchant source");
    ok(s.includes("hypnosislive.com/faq"),"missing refund source");
    ok(s.includes("nccih.nih.gov/health/hypnosis"),"missing independent science source");
    ok(!/affiliate_id=|aff_id=|ref=3055117|awin1.com|clickbank.net|utm_term=[^\s]+@/i.test(s),"tracking or private data in email creative");
    ok(!/guaranteed to improve|clinically proven product|reprograms your brain as a fact/i.test(s),"unjustified claim");
    ok(!/\$\d+[.,]?\d*/.test(s),"unverified checkout pricing in creative");
  }
  ok(html.includes('lang="en"'),"missing language for screen reader");
  ok(html.includes('<h1 '),"missing main heading");
  ok(html.includes('max-width:600px'),"email width not bounded");
  ok(html.includes('style="'),"HTML should be inline styled");
  ok(!/<script\b|<form\b|<img\b|<iframe\b|<button\b/i.test(html),"tracking/script/form/active CTA prohibited");
  const hrefs=[...html.matchAll(/href="([^"]+)"/g)].map(x=>x[1]);
  ok(hrefs.length===6,"exactly six cited noncommercial source hyperlinks");
  ok(hrefs.every(x=>/^https:\/\/(hypnosislive\.com|www\.nccih\.nih\.gov|finalvestige\.com|www\.ftc\.gov)\//.test(x)),"unexpected destination");
  ok(!hrefs.some(x=>x.includes("APPROVED_")),"guide placeholder must not be a link");
  ok(evidence.includes("6/6 passed"),"master native evidence required");
  ok(evidence.includes("HOLD_MERCHANT") && evidence.includes("NOT COMPUTABLE"),"revenue/release caveats missing");
  ok(!/\$\d[\d,]*(?:\.\d+)?\s*(?:PROFIT|REVENUE)|paid_orders\s*[:=]\s*[1-9]|realized_net_revenue\s*[:=]\s*[1-9]/i.test(evidence),"fabricated positive financial result");
  ok(evidence.includes("d57ccdba3aee8f065e143e101c2945f4f3d01647"),"original master head not pinned");
  return {passed:true,checks};
}
module.exports={inspect};
if (require.main===module) {
  const fs=require("node:fs"), path=require("node:path");
  const root=path.resolve(__dirname);
  const files={md:fs.readFileSync(path.join(root,"ISSUE05_TOTAL_FOCUS_ALTERNATIVE_UNSENT.md"),"utf8"),
    txt:fs.readFileSync(path.join(root,"ISSUE05_REVIEW_ONLY.txt"),"utf8"),
    html:fs.readFileSync(path.join(root,"ISSUE05_REVIEW_ONLY.html"),"utf8"),
    evidence:fs.readFileSync(path.join(root,"SOURCE_AND_CONVERSION_EVIDENCE.md"),"utf8")};
  console.log(JSON.stringify(inspect(files)));
}

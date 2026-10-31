"use strict";
const assert=require("node:assert/strict"), fs=require("node:fs"),path=require("node:path");
const m=require("../excerpt_truth.cjs");
const root=path.resolve(__dirname,"../../");
const manifest=JSON.parse(fs.readFileSync(path.join(root,"manifest.json"),"utf8"));
const sources=Object.fromEntries(manifest.issues.map(e=>[e.number,fs.readFileSync(path.join(root,"issues",String(e.number).padStart(2,"0")+"-"+e.slug+".md"),"utf8")]));
let count=0;const check=(test,name)=>{assert.ok(test,name);count++;};
const rows=m.audit(manifest,sources);
check(rows.length===6,"six issues");
check(rows.filter(x=>x.kind==="editorial").length===4,"four editorial");
check(rows.filter(x=>x.kind==="commercial-review-pending").length===2,"two commercial");
for(const r of rows) {
  check(r.ready_to_send===false,"no release "+r.issue);
  check(r.source_cta_target_present,"source CTA "+r.issue);
  check(r.modeled_default_misses_primary_cta,"default CTA missing "+r.issue);
  check(r.requires_actual_received_wordpress_mime,"MIME evidence missing "+r.issue);
  check(r.default_excerpt_55_word_model.words<=55,"55 model upper bound "+r.issue);
  check(r.default_excerpt_350_character_model.characters<=350,"350 model upper bound "+r.issue);
  check(r.default_excerpt_350_character_model.fraction_of_full_text<1,"truncation "+r.issue);
  if(r.kind==="commercial-review-pending") {
    check(r.commercial_disclosure_in_full_source,"source disclosure "+r.issue);
    check(!r.default_excerpt_55_word_model.commercial_disclosure_present,"not in 55 model "+r.issue);
    check(!r.default_excerpt_350_character_model.commercial_disclosure_present,"not in 350 model "+r.issue);
    check(r.guide_url_verified===false&&r.merchant_email_permission_verified===false,"merchant hold "+r.issue);
  }
}
check(m.plain("**One** [guide](https://example.org/path) [[PENDING]]")==="One guide [PENDING]","markdown parsing");
assert.throws(()=>m.audit({...manifest,mix:{editorial:5,commercial_review_pending:1}},sources),/4:2/);count++;
const mutant=structuredClone(manifest);mutant.issues[0].merchant_affiliate_url="https://example.com";assert.throws(()=>m.audit(mutant,sources),/Release hold/);count++;
const removed={...sources,1:sources[1].replace(manifest.issues[0].editorial_cta,"[missing]")};assert.throws(()=>m.audit(manifest,removed),/Missing CTA/);count++;
console.log("R27: "+count+" local guard assertions PASSED. Models only; no WP-native email tested.");

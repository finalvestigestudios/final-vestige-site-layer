"use strict";
/**
 * FV EX2 read-only EXACT-DELTA admission for WordPress Page 6.
 * Extends the structural safeguard in PR #1587: a structurally intact page can
 * still conceal new scripts, merchant links, misleading copy, or changed blocks.
 * Operates only on local, authenticated context=edit extracts.
 * NEVER writes WordPress, exports subscribers, or signifies release approval.
 */
const {assemble}=require("./atomic_page6_review.cjs");
const {admit}=require("./ex2_homepage_no_loss_gate.cjs");

function review(home,focus,candidate,options={}) {
  if(typeof candidate!=="string" || !candidate.length)
    throw Error("HOLD: candidate must be raw Gutenberg editor-source text");
  const input=home&&typeof home==="object"?(home.data||home):null;
  if(!input || typeof input.content!=="string")
    throw Error("HOLD: authenticated raw Page 6 content required");
  // The existing atomic composer pins Page 6/Focus IDs, publish state, modified
  // dates, source SHA-256, exact five substitutions, and byte-for-byte reversal.
  // hashFn is permitted only as an explicitly injected synthetic test dependency.
  const approved=assemble(home,focus,options);
  const structural=admit(input.content,candidate);
  if(structural.status!=="STRUCTURAL_PASS_RELEASE_HOLD")
    throw Error("HOLD: no-loss inventory failure ("+structural.failures.join(",")+")");
  // Crucial security property: preservation counts alone are not enough.
  // This rejects ANY additional byte change, including injected marketing/JS,
  // altered source claims, stealth checkout links and Gutenberg block drift.
  if(candidate!==approved.proposed_content)
    throw Error("HOLD: candidate differs from the five precisely reviewed edits");
  if(approved.receipt.operations.length!==5 ||
     approved.receipt.before.jetpack!==1 || approved.receipt.after.jetpack!==1 ||
     approved.receipt.after.margins!==72)
    throw Error("HOLD: expected preservation contract changed");
  return {
    status:"EXACT_DELTA_PASS_RELEASE_HOLD",release_approved:false,
    production_write:false,source_sha256:approved.receipt.source_sha256,
    operations:approved.receipt.operations,
    source_characters:input.content.length,candidate_characters:candidate.length,
    before:structural.before,after:structural.after,
    unresolved:["isolated WordPress/Assembler integration","Jetpack real opt-in",
      "Focus query-spoof fix","actual image delivery and rights","axe and manual WCAG 2.2 AA",
      "Lighthouse/CWV lab and field data","independent CI/QD","founder approval"],
    commercial:"No verified leads or sales; net revenue per 1000 qualified human sessions unknown"
  };
}

module.exports={review};
if(require.main===module){
  const fs=require("node:fs");
  const argv=process.argv.slice(2);
  if(argv.length!==3 || argv.some(x=>x.startsWith("http://")||x.startsWith("https://"))){
    console.error("Usage: node ex2_homepage_exact_delta_gate.cjs PRIVATE_HOME_EDIT.json PRIVATE_FOCUS_EDIT.json PRIVATE_CANDIDATE.txt");
    process.exit(2);
  }
  try{
    const [home,focus,candidate]=[
      JSON.parse(fs.readFileSync(argv[0],"utf8")),
      JSON.parse(fs.readFileSync(argv[1],"utf8")),
      fs.readFileSync(argv[2],"utf8")];
    console.log(JSON.stringify(review(home,focus,candidate),null,2));
  }catch(e){console.error(String(e.message||e));process.exit(1);}
}
"use strict";
/* Offline approximate-only — NEVER a received Jetpack email or a send approval. */
const fs=require("node:fs"),path=require("node:path");
function plain(s){return s.replace(/\[([^\]]+)\]\(([^)]+)\)/g,"$1").replace(/<[^>]*>/g," ").replace(/[\x60*_>]/g," ").replace(/\s+/g," ").trim()}
function inspect(e,s){
 const body=s.split("\n---\n")[1]||"",text=plain(body);
 const anchor=[...body.matchAll(/\[([^\]]+)\]\(([^)]+)\)/g)].find(v=>v[2]===e.editorial_cta);
 const targetFound=!!anchor||body.includes(e.editorial_cta);
 const shortWord=text.split(/\s+/).slice(0,55).join(" "),shortChar=text.slice(0,350);
 const targetVisible=x=>anchor?x.includes(anchor[1]):x.includes(e.editorial_cta);
 const commercial=e.kind==="commercial-review-pending";
 return {number:e.number,kind:e.kind,target_found:targetFound,
  first_55_word_excerpt_is_estimate:true,first_350_char_excerpt_is_estimate:true,
  words_in_body:text.split(/\s+/).length,excerpt_55_words:shortWord,excerpt_350_chars:shortChar,
  target_visible_55_words:targetVisible(shortWord),target_visible_350_chars:targetVisible(shortChar),
  disclosure_visible_55_words:commercial?shortWord.includes("Commercial disclosure:"):null,
  disclosure_visible_350_chars:commercial?shortChar.includes("Commercial disclosure:"):null,
  guide_is_inert_placeholder:e.editorial_cta.startsWith("[["),
  native_wp_email_preview_verified:false,actual_delivery_verified:false,send_gate:"HOLD_UNSENT"};
}
function audit(root){
 const manifest=JSON.parse(fs.readFileSync(path.join(root,"manifest.json"),"utf8"));
 if(manifest.status!=="DRAFT_UNSENT_NO_SCHEDULING"||manifest.issues.length!==6
  ||manifest.issues.filter(x=>x.kind==="editorial").length!==4
  ||manifest.issues.filter(x=>x.kind==="commercial-review-pending").length!==2)throw Error("canonical campaign drift");
 const entries=manifest.issues.map(e=>{
  const name=String(e.number).padStart(2,"0")+"-"+e.slug+".md";
  const s=fs.readFileSync(path.join(root,"issues",name),"utf8");
  if(!s.includes(e.subject)||!s.includes(e.preheader)||!s.includes("UNSENT DRAFT")
    ||!s.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]")
    ||!s.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"))throw Error("draft/legal gate changed "+e.number);
  const r=inspect(e,s);if(!r.target_found)throw Error("missing canonical CTA "+e.number);return r;
 });
 return {mode_observed:"excerpt",cutoffs:"first 55 words / first 350 characters (alternative docs, approximations)",canonical_pr:175,
  footer_address_verified:false,unsubscribe_in_received_email_verified:false,
  founder_final_approval:false,all_issues:"HOLD_UNSENT",entries};
}
module.exports={plain,inspect,audit};
if(require.main===module){const out=audit(process.argv[2]||"dispatch/campaign-2026-mind");console.log(JSON.stringify(out,null,2));
 if(out.entries.some(x=>!x.target_visible_55_words||!x.target_visible_350_chars
 ||(x.kind==="commercial-review-pending"&&(!x.disclosure_visible_55_words||!x.disclosure_visible_350_chars))))process.exitCode=2}

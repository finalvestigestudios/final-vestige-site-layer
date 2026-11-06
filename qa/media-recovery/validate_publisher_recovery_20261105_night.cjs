"use strict";
function validate(d){
 const e=[];
 if(!d||d.schema!=="fv-publisher-recovery-20261105-v1")return ["schema"];
 if(!Array.isArray(d.rows)||d.rows.length!==2)return ["rows"];
 const expected={"285:5":["images.saymedia-content.com","upload.wikimedia.org",285,"PD-self","2010"],"287:5":["stpetecatalyst.com","media.stpetecatalyst.com",287,"University Press of Florida","1987"]};
 const found=new Set();
 for(const r of d.rows){
  const x=expected[r.key];if(!x||found.has(r.key)){e.push("keys");continue;}found.add(r.key);
  if(r.post!==x[2]||!r.old.startsWith("https://"+x[0]+"/")||!r.candidate.startsWith("https://"+x[1]+"/"))e.push("source identity "+r.key);
  if(r.web_reader_old_status!==404||r.chrome_status!==null)e.push("retriever/browser conflation "+r.key);
  if(!r.publisher.startsWith("https://")||!r.catalog.startsWith("https://")||!r.source_chain||!r.visual_relationship)e.push("primary chain "+r.key);
  if(!r.rights.includes(x[3])||!r.credit||!r.editorial_gate.includes(x[4]))e.push("rights/chronology "+r.key);
  if(r.rehost_approved!==false||r.hotlink_approved!==false||r.wp_edit!==false)e.push("release unauthorized "+r.key);
  if(r.key==="285:5"&&(JSON.stringify(r.native)!=="[819,614]"||JSON.stringify(r.derivative)!=="[819,614]"))e.push("no upscale source geometry");
  if(r.key==="287:5"&&(r.native!==null||r.derivative!==null||!r.editorial_gate.includes("1980")))e.push("unknown publisher geometry/chronology");
 }
 if(found.size!==2)e.push("missing");
 const r=d.release||{},b=d.baseline||{};
 if(r.max_width!==960||r.never_upscale!==true||r.browser_proof_required!==true||r.rights_review_required!==true||r.visual_review_required!==true||r.publisher_hotlink_policy_review_required!==true)e.push("gates");
 if(r.production_repairs!==0||r.downloads!==0||r.wp_writes!==0||r.real_network_bytes!==null)e.push("invented release");
 if(b.frozen_posts!==61||b.frozen_slots!==355||b.alleged_broken!==42||b.broken_browser_verified!==null||b.claimed_weight_savings_percent!==76||b.measured_wire_savings_percent!==null||b.wp_large_orig_count!==13||b.wp_large_orig_stored_bytes!==43522829)e.push("baseline");
 return e;
}
module.exports={validate};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const d=JSON.parse(fs.readFileSync(process.argv[2]||path.join(__dirname,"publisher_recovery_20261105_night.json"),"utf8"));
 const e=validate(d);if(e.length){console.error(e);process.exitCode=1;}else console.log("PASS: publisher recovery safety gate");
}

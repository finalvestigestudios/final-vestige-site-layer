/** Read-only regression checks: node --test dispatch/r355/test_preview.mjs
 * No network, WordPress, email, recipients, merchant or checkout access. */
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { render, check } from "./preview_engine.mjs";
const dir=dirname(fileURLToPath(import.meta.url));
const source=resolve(dir,"../campaign-2026-mind");
const manifest=JSON.parse(readFileSync(resolve(source,"manifest.json"),"utf8"));
const provenance=JSON.parse(readFileSync(resolve(dir,"ISSUE_PROVENANCE.json"),"utf8"));
const originals=provenance.issues.map(entry=>({
 path:entry.source_file,
 content:readFileSync(resolve(dir,"../../",entry.source_file),"utf8"),
 sha:entry.git_blob
}));
function blobHash(text){let bytes=Buffer.from(text,"utf8");return createHash("sha1").update(Buffer.from("blob "+bytes.length+"\\0")).update(bytes).digest("hex");}
test("exact original campaign source blobs and 4:2 allocation",()=>{
 assert.equal(provenance.source_commit,"d57ccdba3aee8f065e143e101c2945f4f3d01647");
 originals.forEach((o,i)=>assert.equal(blobHash(o.content),provenance.issues[i].git_blob));
 let audit=check(originals,manifest,{});
 assert.equal(audit.valid_source,true,JSON.stringify(audit.problems));
 assert.equal(audit.all_send_state,"HOLD_UNSENT");
 assert.equal(audit.shared_missing.length,7);
 assert.equal(audit.merchant_missing.length,6);
});
test("six HTML and plaintext files reproduce from unchanged originals",()=>{
 originals.forEach((o,i)=>{
 const n=String(i+1).padStart(2,"0"), p=render(o.content,manifest.issues[i]);
 assert.equal(readFileSync(resolve(dir,"preview/issue-"+n+".html"),"utf8"),p.html);
 assert.equal(readFileSync(resolve(dir,"preview/issue-"+n+".txt"),"utf8"),p.plain);
 assert.match(p.html,/OFFLINE SIMULATION/);
 assert.match(p.html,/NOT VERIFIED — VALID FINAL VESTIGE POSTAL ADDRESS REQUIRED/);
 assert.doesNotMatch(p.html,/<(?:script|iframe|form|img)\b/i);
 assert.doesNotMatch(p.html,/href="\[\[/);
 });
});
test("merchant offer placeholders are always non-clickable",()=>{
 for(let i of [2,4]){
 const h=render(originals[i].content,manifest.issues[i]).html;
 assert.match(h,/INACTIVE — OFFER GUIDE|OFFER GUIDE CTA DISABLED/);
 assert.doesNotMatch(h,/<a[^>]+href="https?:\/\/(?:zen12|hypnosislive|inspire3)/i);
 }
});
test("one fabricated proof, fake merchant URL, and every synthetic approval never send",()=>{
 const keys=[...check(originals,manifest,{}).shared_missing,...check(originals,manifest,{}).merchant_missing];
 for(let k of keys){
 const p={[k]:{status:"verified",source_ref:"SYNTHETIC_ONLY"}};
 assert.equal(check(originals,manifest,p).all_send_state,"HOLD_UNSENT");
 }
 const fake=Object.fromEntries(keys.map(k=>[k,{status:"verified",source_ref:"SYNTHETIC_ONLY"}]));
 assert.equal(check(originals,manifest,fake).all_send_state,"HOLD_UNSENT");
 const poisoned=structuredClone(manifest);poisoned.issues[2].merchant_affiliate_url="https://unverified.example";
 assert.equal(check(originals,poisoned,{}).valid_source,false);
});

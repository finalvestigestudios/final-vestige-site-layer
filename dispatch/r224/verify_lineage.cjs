"use strict";
const fs = require("node:fs");
const cp = require("node:child_process");
const crypto = require("node:crypto");
const path = require("node:path");
const LEDGER = path.join(__dirname, "LINEAGE_LEDGER.json");
function gitBlobSha(bytes) {
  const content = Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes, "utf8");
  return crypto.createHash("sha1").update(Buffer.from("blob " + content.length + "\0")).update(content).digest("hex");
}
function evaluate(ledger, got) {
  if (!ledger || !Array.isArray(ledger.rows) || ledger.rows.length !== 9 || !got || !Array.isArray(got.rows) || got.rows.length !== 9) return {ok:false, release:"HOLD_UNSENT", reason:"INVALID_EVIDENCE_SHAPE"};
  let changed = 0;
  const bad=[];
  const seen=new Set();
  for (let i=0;i<ledger.rows.length;i++) {
    const e=ledger.rows[i], a=got.rows[i];
    if (seen.has(e.path) || a.path!==e.path || a.original!==e.original_blob || a.stacked!==e.stacked_blob || e.changed !== (e.original_blob !== e.stacked_blob)) bad.push(e.path);
    seen.add(e.path);
    if (e.changed) changed++;
  }
  if (changed!==7 || bad.length || !ledger.no_release_authorization) return {ok:false,release:"HOLD_UNSENT",reason:"SOURCE_DRIFT_OR_LEDGER_ERROR",bad};
  if (!got.baseline_mix || !got.stacked_mix || got.baseline_mix.editorial!==4 || got.stacked_mix.editorial!==4 || got.baseline_mix.commercial!==2 || got.stacked_mix.commercial!==2 || !got.baseline_mix.all_links_null || !got.stacked_mix.all_links_null) return {ok:false,release:"HOLD_UNSENT",reason:"CAMPAIGN_MIX_OR_LINK_ERROR"};
  return {ok:true,release:"HOLD_UNSENT",reason:"SEVEN_PATHS_REVISED_FOUNDER_SELECTION_AND_PROVIDER_RELEASE_PROOFS_PENDING",revised_paths:changed};
}
function inspectManifest(contents) {
  const d=JSON.parse(contents);
  const issues=d.issues||[];
  return {editorial:issues.filter(x=>x.kind==="editorial").length,commercial:issues.filter(x=>x.kind==="commercial-review-pending").length,all_links_null:issues.length===6 && issues.every(x=>x.merchant_affiliate_url===null && x.publish_state==="hold")};
}
function run(repoPath=".") {
  const ledger=JSON.parse(fs.readFileSync(LEDGER,"utf8"));
  const fromGit=(sha,p)=>cp.execFileSync("git",["show",sha+":"+p],{cwd:repoPath,maxBuffer:1024*1024,timeout:10000});
  const got={rows:ledger.rows.map(e=>({path:e.path,original:gitBlobSha(fromGit(ledger.original_commit,e.path)),stacked:gitBlobSha(fromGit(ledger.review_commit,e.path))})),
   baseline_mix:inspectManifest(fromGit(ledger.original_commit,"dispatch/campaign-2026-mind/manifest.json").toString("utf8")),
   stacked_mix:inspectManifest(fromGit(ledger.review_commit,"dispatch/campaign-2026-mind/manifest.json").toString("utf8"))};
  const report=evaluate(ledger,got);
  process.stdout.write(JSON.stringify(report,null,2)+"\n");
  if (!report.ok) process.exitCode=1;
}
if (require.main===module) run(process.argv[2]||".");
module.exports={gitBlobSha,evaluate,inspectManifest,run};

"use strict";
const {validateSkyway}=require("./validate_skyway_287_six_20261110.cjs");
function runSkywayTests(audit,current,previous) {
  const results=[];
  const clone=x=>JSON.parse(JSON.stringify(x));
  const run=(name,mutator,expected)=>{
    const a=clone(audit),n=clone(current),p=clone(previous);
    if(mutator) mutator(a,n,p);
    const v=validateSkyway(a,n,p);
    const passed=expected===null?v.ok:v.ok===false&&v.errors.some(e=>e.includes(expected));
    results.push({name,pass:passed,errors:passed?[]:v.errors});
    if(!passed)throw Error("FAIL "+name+": "+JSON.stringify(v.errors));
  };
  run("baseline pinned six-URL audit and 288-slot reconciled register",null,null);
  run("reject false visitor status",a=>{a.rows[0].guest_http_status=200},"NO_INVENTED_HTTP_OR_BYTES");
  run("reject fabricated transfer bytes",a=>{a.rows[0].guest_transfer_bytes=19000},"NO_INVENTED_HTTP_OR_BYTES");
  run("reject fabricated visitor broken flag",a=>{a.rows[0].guest_broken=true},"NO_INVENTED_HTTP_OR_BYTES");
  run("reject invented origin status",a=>{a.rows[1].origin_http_status=200},"NO_INVENTED_HTTP_OR_BYTES");
  run("reject claimed rights clearance",a=>{a.rows[0].rights_cleared=true},"NO_UNLICENSED_ACTION");
  run("reject image download authorization",a=>{a.rows[0].download_authorized=true},"NO_UNLICENSED_ACTION");
  run("reject caching authorization",a=>{a.rows[0].cache_authorized=true},"NO_UNLICENSED_ACTION");
  run("reject WordPress upload authorization",a=>{a.rows[0].wordpress_upload_authorized=true},"NO_UNLICENSED_ACTION");
  run("reject post rewrite authorization",a=>{a.rows[0].post_rewrite_authorized=true},"NO_UNLICENSED_ACTION");
  run("reject fabricated native source size",a=>{a.rows[0].source_native_px=[1000,700]},"NO_INVENTED_GEOMETRY");
  run("reject fabricated candidate target dimensions",a=>{a.rows[0].conditional_max960_px=[960,648]},"NO_INVENTED_GEOMETRY");
  run("reject assumed identical archives",a=>{a.rows[0].exact_binary_match_verified=true},"NO_INVENTED_GEOMETRY");
  run("reject inaccurate historical ALT-verified claim",a=>{a.post.historical_alt_equality_verified=true},"DO_NOT_CLAIM_HISTORICAL_ALT_PROOF");
  run("reject phantom success instead of wrapper 404",a=>{a.rows[5].retriever_wrapper_status=200},"LEGACY_URL_WRAPPER_404_NOT_GUEST");
  run("reject wrong publisher alternate CDN",a=>{a.rows[5].candidate_asset_url="https://not-existing.example/picture.jpg"},"PUBLISHER_CDN_CANDIDATE");
  run("reject omission of salvage crane ALT correction",a=>{a.rows[4].proposed_alt_for_editor=null},"CRANE_SCENE_ALT_CORRECTION");
  run("reject removal of newspaper figure rights",a=>{a.rows[2].rights_issue="public domain"},"NEWSPAPER_DIAGRAM_COPYRIGHT");
  run("reject invented visitor broken count",(a,n)=>{n.counts.guest_browser_confirmed_broken=42},"NO_GUEST_CLAIMS");
  run("reject invented 76 percent transfer savings",(a,n)=>{n.counts.wire_reduction_76_percent_measured=true},"NO_FAKE_PERFORMANCE");
  run("reject reported 42 as confirmed",(a,n)=>{n.counts.reported_42_broken_browser_confirmed=true},"NO_FAKE_PERFORMANCE");
  run("reject swapping stored original URL",(a,n)=>{n.rows.find(x=>x.slot==="287:0").stored_url="https://example.org/replacement.jpg"},"SOURCE_IDENTITY_287:0");
  run("reject unrelated source entry mutation",(a,n)=>{n.rows.find(x=>x.slot==="101:1").rights_cleared=true},"UNRELATED_MUTATED_101:1");
  run("reject double-counting previously researched P0",(a,n)=>{n.rows.find(x=>x.slot==="287:5").evidence.push({batch:"wrong"})},"PRIOR_P0_SLOT_UNCHANGED");
  run("reject evidence blob SHA corruption",(a,n)=>{n.rows.find(x=>x.slot==="287:1").evidence[0].blob_sha="not-real"},"BATCH_SHA_PIN_287:1");
  run("reject invented rights-cleared candidate",(a,n)=>{n.rows.find(x=>x.slot==="287:2").candidate_sources[0].item_rights_cleared=true},"CANDIDATE_HOLD_287:2");
  run("reject invented candidate 960 pixel size",(a,n)=>{n.rows.find(x=>x.slot==="287:2").candidate_sources[0].conditional_960px=[960,400]},"CANDIDATE_HOLD_287:2");
  run("reject count confusion from 42 alleged broken",(a,n)=>{n.counts.unresearched=42},"COVERAGE_COUNT");
  run("reject phantom evidence count",(a,n)=>{n.counts.total_evidence_records=263},"SOURCE_EVIDENCE_COUNT");
  run("reject unrelated 61-post inventory mutation",(a,n)=>{n.rows.pop()},"EXACT_288_SLOTS");
  run("reject source URL evidence mismatch",a=>{a.rows[3].original_url="https://invalid.example/id.jpg"},"SOURCE_IDENTITY_287:3");
  run("reject claimed 960-upscaling",a=>{a.rows[1].sizing_rule="always 960x640"},"NO_UPSCALE_RULE");
  return {ok:true,passed:results.length,total:results.length,results};
}
if(require.main===module) {
  const fs=require("node:fs"),path=require("node:path");
  const read=p=>JSON.parse(fs.readFileSync(path.join(__dirname,p),"utf8"));
  const outcome=runSkywayTests(read("skyway_287_six_live_retriever_rights_20261110.json"),
    read("coverage_257_exact_pr1703_20261110.json"),read("coverage_252_exact_pr1703_20261110.json"));
  process.stdout.write(JSON.stringify({ok:outcome.ok,passed:outcome.passed,total:outcome.total})+"\n");
}
module.exports={runSkywayTests};

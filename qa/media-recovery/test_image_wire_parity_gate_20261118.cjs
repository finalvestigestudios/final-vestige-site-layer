"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const {evaluate}=require("./image_wire_parity_gate_20261118.cjs");
const make=function make(cohort="targeted",count=1,after=20){
 const capture=(viewport,phase)=>({instrument:"CDP_NETWORK",capture_type:"GUEST_CHROMIUM",viewport,
  cache_disabled:true,service_worker_bypassed:true,complete_image_requests:true,
  trace_evidence_url:"https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154",trace_sha256:"a".repeat(64),
  pages:Array.from({length:count},(_,i)=>({post_id:i+1,url:`https://finalvestige.com/test-${i+1}/`,
    complete_image_requests:true,images:[{asset_id:`${i+1}:0`,authored_src:"https://i0.wp.com/archives.gov/pic.jpg",
      current_src:"https://i0.wp.com/archives.gov/pic.jpg?w=960",final_url:"https://i0.wp.com/archives.gov/pic.jpg?w=960",
      source_identity:"https://archives.gov/pic.jpg",request_id:`${viewport}-${phase}-${i+1}`,
      from_cache:false,from_service_worker:false,transfer_metric:"CDP_ENCODED_DATALENGTH",
      transfer_bytes:phase==="before"?100:after,http_status:200,mime:"image/jpeg",
      decoded:true,natural_width:960,natural_height:600,screenshot:"test-only/screen.png"}]}))});
 return {schema:"fv-image-wire-parity-v1",cohort:{id:cohort,expected_posts:count},manifest_sha256:"b".repeat(64),
   estimated_bytes:false,stored_original_bytes_used:false,before:{desktop:capture("desktop","before"),mobile:capture("mobile","before")},
   after:{desktop:capture("desktop","after"),mobile:capture("mobile","after")}};
};
test("targeted_not_sitewide",()=>{const x=(()=>make())();assert.equal((x=>!evaluate(x).threshold_met)(x),true);});
test("61_sitewide_with_76_percent",()=>{const x=(()=>make("historic-61",61,24))();assert.equal((x=>evaluate(x).threshold_met)(x),true);});
test("66_separate_cohort",()=>{const x=(()=>make("current-66",66,24))();assert.equal((x=>evaluate(x).cohort==="current-66"&&evaluate(x).threshold_met)(x),true);});
test("61_requires_all_posts",()=>{const x=(()=>make("historic-61",1))();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("post_coverage")))(x),true);});
test("stored_bytes_cannot_be_used",()=>{const x=(()=>{let z=make();z.stored_original_bytes_used=true;return z;})();assert.equal((x=>evaluate(x).errors.includes("not_real_wire"))(x),true);});
test("from_cache_must_fail",()=>{const x=(()=>{let z=make();z.after.mobile.pages[0].images[0].from_cache=true;return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("unmeasured_wire")))(x),true);});
test("zero_wire_bytes_must_fail",()=>{const x=(()=>{let z=make();z.before.desktop.pages[0].images[0].transfer_bytes=0;return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("unmeasured_wire")))(x),true);});
test("service_worker_must_fail",()=>{const x=(()=>{let z=make();z.before.mobile.pages[0].images[0].from_service_worker=true;return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("unmeasured_wire")))(x),true);});
test("page_drift_must_fail",()=>{const x=(()=>{let z=make();z.after.mobile.pages[0].url="https://finalvestige.com/changed/";return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("post_drift")))(x),true);});
test("missing_asset_must_fail",()=>{const x=(()=>{let z=make();z.after.desktop.pages[0].images=[];return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("asset_count_drift")))(x),true);});
test("broken_after_must_fail",()=>{const x=(()=>{let z=make();let m=z.after.mobile.pages[0].images[0];m.decoded=false;m.natural_width=0;m.natural_height=0;return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("broken_after")))(x),true);});
test("unapproved_source_must_fail",()=>{const x=(()=>{let z=make();z.after.desktop.pages[0].images[0].source_identity="https://archives.gov/other.jpg";return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("unapproved_replacement")))(x),true);});
test("approved_source_does_not_auto_publish",()=>{const x=(()=>{let z=make();let m=z.after.desktop.pages[0].images[0];m.source_identity="https://archives.gov/other.jpg";m.approval={rights:"CLEARED",exact_frame:true,catalog:"https://archives.gov/record",license:"https://archives.gov/rights",editorial_id:"QA-123",master_sha256:"c".repeat(64),target_width:960,no_upscale:true};return z;})();assert.equal((x=>!evaluate(x).claim_publicly_verified&&evaluate(x).errors.every(s=>!s.includes("unapproved_replacement")))(x),true);});
test("upscale_forbidden",()=>{const x=(()=>{let z=make();let m=z.after.desktop.pages[0].images[0];m.source_identity="https://archives.gov/other.jpg";m.approval={rights:"CLEARED",exact_frame:true,catalog:"https://archives.gov/record",license:"https://archives.gov/rights",editorial_id:"QA-123",master_sha256:"c".repeat(64),target_width:1200,no_upscale:true};return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("unapproved_replacement")))(x),true);});
test("request_id_dedup",()=>{const x=(()=>{let z=make();for(const stage of ["before","after"])for(const d of ["desktop","mobile"]){let a=z[stage][d].pages[0].images;a.push({...a[0],asset_id:"1:1"});}return z;})();assert.equal((x=>evaluate(x).devices.desktop.before_bytes===100)(x),true);});
test("request_id_conflict_must_fail",()=>{const x=(()=>{let z=make();let a=z.after.mobile.pages[0].images;a.push({...a[0],asset_id:"1:1",transfer_bytes:999});return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("request_collision")))(x),true);});
test("non_image_mime_must_fail",()=>{const x=(()=>{let z=make();z.before.desktop.pages[0].images[0].mime="text/html";return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("response")))(x),true);});
test("screenshots_required",()=>{const x=(()=>{let z=make();z.after.mobile.pages[0].images[0].screenshot="";return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("screenshot")))(x),true);});
test("trace_required",()=>{const x=(()=>{let z=make();z.after.desktop.trace_sha256="";return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("trace")))(x),true);});
test("full_image_coverage_required",()=>{const x=(()=>{let z=make();z.after.desktop.pages[0].complete_image_requests=false;return z;})();assert.equal((x=>evaluate(x).errors.some(s=>s.includes("incomplete_images")))(x),true);});
test("both_devices_require_76",()=>{const x=(()=>{let z=make("historic-61",61,24);for(const p of z.after.mobile.pages)p.images[0].transfer_bytes=50;return z;})();assert.equal((x=>!evaluate(x).threshold_met)(x),true);});
test("request_ids_are_scoped_to_page_navigation",()=>{const x=make("targeted",2);for(const phase of ["before","after"])for(const device of ["desktop","mobile"]){const pages=x[phase][device].pages;pages[1].images[0].request_id=pages[0].images[0].request_id;}assert.equal(evaluate(x).devices.desktop.before_bytes,200);assert.equal(evaluate(x).errors.includes("before-desktop:2:request_collision"),false);});

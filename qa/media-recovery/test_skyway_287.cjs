"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const {validateSkyway}=require("./validate_skyway_287.cjs");
const original=require("./skyway_287_source_relocation_20261101.json");
const frozen=require("./parts/03.json").images;
const copy=()=>JSON.parse(JSON.stringify(original));
const good=()=>validateSkyway(copy(),frozen);
function reject(name,mutator,expected){
 test(name,()=>{
  const x=copy();mutator(x);const r=validateSkyway(x,frozen);
  assert.equal(r.ok,false,name);
  assert.ok(r.errors.some(s=>s.includes(expected)),name+": "+r.errors.join(";"));
 });
}
test("baseline exact six-source CMS, web-retriever, source identity and HOLD gates",()=>assert.equal(good().ok,true,good().errors.join(";")));
for(let i=0;i<6;i++){
 reject("reject modified actual published URL "+i,x=>x.rows[i].current_published_source_url+="?fake=1","original source URL");
 reject("reject changed historical ALT "+i,x=>x.rows[i].current_published_alt+=" forged","original alt");
 reject("reject wrong post key "+i,x=>x.rows[i].key="tampered-key","key");
}
reject("never reinterpret retriever 404 as visitor 404",x=>x.rows[5].guest_browser.http_status=404,"unobserved browser");
reject("no fabricated decoded currentSrc",x=>x.rows[5].guest_browser.current_src=x.rows[5].current_published_source_url,"unobserved browser");
reject("no fabricated decoded width",x=>x.rows[5].guest_browser.natural_width_px=960,"unobserved browser");
reject("no fabricated image encoded bytes",x=>x.rows[0].guest_browser.encoded_transfer_bytes=1000,"unobserved browser");
reject("no fabricated sitewide broken count",x=>x.site_wide_context.verified_broken_count=42,"false 42 broken");
reject("no invented before-after percent saved",x=>x.site_wide_context.measured_reduction_percent=76,"false 76 percent");
reject("do not treat original library bytes as browser bytes",x=>x.site_wide_context.visitor_transfer_bytes=43522829,"storage is not transfer");
reject("rights cannot be default-cleared",x=>x.rows[5].rights.reproduction_clearance="PUBLIC_DOMAIN","rights hold");
reject("no allowed third-party cache mirror",x=>x.rows[5].rights.caching_clearance="CLEARED","rights hold");
reject("prevent unauthorized WordPress media upload",x=>x.rows[5].release.wordpress_media_upload_authorized=true,"release hold");
reject("prevent unauthorized Gutenberg post edit",x=>x.rows[5].release.wordpress_post_edit_authorized=true,"release hold");
reject("prevent falsely marked production repair",x=>x.site_wide_context.production_images_repaired=1,"false repairs");
reject("reject fabricated candidate identity match",x=>x.rows[5].candidate.proven_binary_same_as_published=true,"candidate identity");
reject("reject changed publisher relocation URL",x=>x.rows[5].candidate.asset_url="https://example.com/unrelated.jpg","exact relocated publisher candidate");
reject("do not call the publisher relocated image visitor-200",x=>x.rows[5].candidate.candidate_web_retriever.origin_http_status=200,"candidate retriever qualification");
reject("reject unsafe target above 960px",x=>x.rows[0].geometry.conditional_target_width_px=1024,"target width");
reject("prevent upscaling",x=>x.rows[1].geometry.no_upscale=false,"size safety");
reject("cannot make up master image geometry",x=>x.rows[4].geometry.original_master_width_px=1280,"no fabricated original pixels");
reject("preserve 1987 bridge editorial chronology review",x=>x.rows[5].visual_integrity.note="Only May 1980 crash photo without review.","later bridge claim review");
reject("retain private press credit",x=>x.rows[5].rights.basis="The photo is freely reusable.","photo credit restriction");
reject("do not deduplicate distinct vehicle photographs",x=>x.rows[3].visual_integrity.note="Same picture as slot zero.","two distinct photos");
reject("reject copied source status masquerading as browser method",x=>x.rows[5].source_retriever.method="logged_out_chrome","source methodology");
reject("reject invented origin 404",x=>x.rows[5].source_retriever.origin_http_status=404,"unobserved source evidence");
reject("reject invented candidate for other photo",x=>x.rows[0].candidate.asset_url="https://example.com/fake.jpg","no invented asset");
reject("flag court photograph's unidentified vessel",x=>x.rows[4].visual_integrity.review_required=false,"court image vessel identification gate");
reject("reject missing NTSB primary source",x=>x.authoritative_related_records=[],"NTSB primary record");

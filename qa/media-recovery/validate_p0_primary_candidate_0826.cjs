#!/usr/bin/env node
'use strict';
// Offline source/candidate validation: no network access, downloads, or WordPress writes.
const fs=require('node:fs');
const crypto=require('node:crypto');
const baseline=require('./p0_seven_guest_failure_queue_20261118.json');
const fail=s=>{throw Error(s)};
const ok=(x,s)=>{if(!x)fail(s)};
const sha=raw=>{const b=Buffer.from(raw,'utf8');return crypto.createHash('sha1').update('blob '+b.length+'\\0'.replace('\\0','\0')).update(b).digest('hex')};
function verify(a,base=baseline){
ok(a&&a.schema==='fv-p0-primary-candidate-v1'&&a.checked_on==='2026-11-18','schema/date');
ok(a.source_method==='public_retriever_origin_only_not_guest_browser'&&a.basis_blob==='16a7ec1c0b8cb92cef4a241eccc82924cd4ca74e','provenance');
ok(a.historical_posts===61&&a.current_posts===66&&a.claimed_42_browser_broken===null&&a.claimed_76_percent_wire_verified===false,'scope/unsupported claims');
ok(Array.isArray(a.rows)&&a.rows.length===2&&Array.isArray(base.slots),'rows/source snapshot');
const ids=new Set();for(const r of a.rows){
ok(['274:6','287:5'].includes(r.slot)&&!ids.has(r.slot),'unknown/duplicate');ids.add(r.slot);
const b=base.slots.find(x=>x.slot===r.slot);
ok(b&&r.origin_url===b.origin_url&&r.origin_http===404&&r.guest_http===null&&r.guest_decoded===null&&r.guest_bytes===null,'origin/guest distinction');
ok(b.authored_src.startsWith('https://i0.wp.com/')&&r.origin_url.startsWith('https://'),'source');
ok(r.new_sha256===null&&r.catalog.startsWith('https://')&&r.reuse_evidence.startsWith('https://'),'missing asset/rights');
if(r.slot==='274:6'){
ok(r.accession==='80-G-227989'&&r.candidate_role==='possible_same_historical_frame_unverified_crop'&&r.catalog.includes('history.navy.mil')&&r.reuse_evidence.includes('commons.wikimedia.org'),'Navy catalog mismatch');
ok(JSON.stringify(r.published_filename_hint)==='[640,432]'&&JSON.stringify(r.candidate_raster_catalog)==='[1910,1288]'&&JSON.stringify(r.existing_preview)==='[960,647]'&&JSON.stringify(r.navy_tiff_catalog)==='[6060,4926]'&&r.catalog_original_bytes===1245612&&/^[a-f0-9]{40}$/.test(r.catalog_sha1),'Navy dimensions/catalog hash');
ok(r.rights==='US_NAVY_FEDERAL_WORK_PUBLIC_DOMAIN_US_REVIEW','Navy item rights');
} else {
ok(r.accession==='RC09237'&&r.candidate_role==='different_archive_photo_editorial_alternative_only'&&r.catalog==='https://floridamemory.com/items/show/32083'&&r.catalog_image_path==='/fpc/reference/rc09237.jpg'&&r.date==='1980-05-09','Florida unrelated substitution');
ok(r.rights==='FLORIDA_MEMORY_PUBLIC_DOMAIN_MARK_1_GENERAL_POLICY_ITEM_REVIEW'&&r.reuse_evidence==='https://floridamemory.com/share/order-info/faq.php'&&r.candidate_raster_catalog===null&&r.existing_preview===null,'Florida rights/unknown dimensions');
}}
ok(a.max_derivative_width===960&&a.no_upscaling===true&&a.rights_review==='HOLD'&&a.exact_crop_review==='HOLD'&&a.editorial_review==='HOLD'&&!a.auto_rehost&&!a.wordpress_write&&!a.wordpress_production_write&&!a.merge_deploy,'release block');
return {verdict:'HOLD_BROWSER_EXACT_IMAGE_RIGHTS',priority_slots:2,source_origin_http_404:2,visitor_failures_confirmed:0,primary_navy_accession:'80-G-227989',florida_alternative_accession:'RC09237',production_writes:0,claim_76_percent:false};
}
module.exports={verify};
if(require.main===module){try{
if(process.argv.length!==3)fail('Usage: node validate_p0_primary_candidate_0826.cjs audit.json');
console.log(JSON.stringify(verify(JSON.parse(fs.readFileSync(process.argv[2],'utf8'))),null,2));
}catch(e){console.error('HOLD: '+e.message);process.exitCode=1;}}

'use strict';
/* Fail closed, offline only. No network, image binaries, CMS writes. */
const prefix='qa/media-recovery/';
const slot=r=>r.key||(typeof r.slot==='string'&&r.slot.includes(':')?r.slot:String(r.post_id)+':'+r.slot);
const url=r=>r.stored_url||r.stored_original_url||r.original_url||r.published_src||r.stored_source_url;
function validate(o,docs){
 const errors=[],ok=(x,msg)=>{if(!x)errors.push(msg)},rows=Array.isArray(o?.rows)?o.rows:[],map=new Map();
 ok(o?.schema==='fv-media-exact-source-full-research-coverage-v3','schema');
 ok(o?.frozen_source?.blob_sha==='92a904c8da1ace1f972b2f00adf1a4847dde2b99','census_blob');
 ok(o?.prior_reconciliation?.blob_sha==='dcab31b66c74a1a5765df2b7c7fcae71329a8371','prior_blob');
 ok(rows.length===288,'288_rows');
 for(const r of rows){
  ok(/^\d+:\d+$/.test(r.slot),'slot:'+r.slot);ok(!map.has(r.slot),'duplicate:'+r.slot);map.set(r.slot,r);
  ok(/^https?:\/\//.test(r.stored_url),'source:'+r.slot);
  for(const k of ['guest_http_status','guest_current_src','guest_decoded_px','guest_wire_bytes','guest_broken'])ok(r[k]===null,'fake_guest:'+r.slot+':'+k);
  for(const k of ['rights_cleared','exact_pixel_match_verified','download_authorized','cache_authorized','wordpress_media_upload_authorized','post_rewrite_authorized'])ok(r[k]===false,'release:'+r.slot+':'+k);
  ok(Array.isArray(r.evidence)&&Array.isArray(r.candidate_sources),'arrays:'+r.slot);
  for(const e of r.evidence||[])ok(!!e.path&&/^[0-9a-f]{40}$/.test(e.blob_sha),'evidence:'+r.slot);
  for(const c of r.candidate_sources||[]){
   ok(c.item_rights_cleared===false&&c.exact_image_match_verified===false,'candidate:'+r.slot);
   const d=c.conditional_960px;
   ok(d===null||(Array.isArray(d)&&d.length===2&&d.every(x=>Number.isInteger(x)&&x>0)&&d[0]<=960),'dimensions:'+r.slot);
  }
 }
 const researched=rows.filter(r=>r.evidence?.length).length,co=o?.counts||{};
 ok(researched===167&&rows.length-researched===121,'unique_167_pending_121');
 ok(co.total_external===288&&co.researched_unique===167&&co.unresearched===121,'counts');
 ok(co.new_research_source_rows===76&&co.unique_research_increase===74&&co.duplicated_with_prior===2,'source_overlap_count');
 ok(rows.reduce((n,r)=>n+(r.evidence?.length||0),0)===172&&co.total_evidence_records===172,'172_source_records');
 ok(JSON.stringify(o.overlap_slots_prior_and_new)==='["214:0","214:4"]','overlap_slots');
 ok(co.guest_browser_confirmed_broken===0&&co.guest_browser_confirmed_loaded===0&&co.reported_42_broken_browser_confirmed===false,'unknown_42');
 ok(co.wire_reduction_76_percent_measured===false,'unproven_76');
 ok(co.oversized_wp_originals_gt_1500000===15&&co.oversized_stored_original_bytes===47096779,'stored_not_transferred');
 ok(JSON.stringify(o.original_six_p0_guest_queue)==='["285:5","285:2","287:5","418:1","418:2","407:1"]','p0_queue');
 ok(o.batch_sources?.length===12,'new_12_batches');
 if(docs){
  ok(docs.census?.rows?.length===288&&docs.prior?.rows?.length===93,'source_dataset_counts');
  for(const original of docs.census?.rows||[])ok(map.get(original.slot)?.stored_url===original.stored_url&&map.get(original.slot)?.origin_host===original.origin_host,'census_source_drift:'+original.slot);
  let oldEvidence=0;
  for(const original of docs.prior?.rows||[]){
   const r=map.get(original.slot);ok(r?.stored_url===original.stored_url,'prior_source_drift:'+original.slot);
   for(const e of original.research_evidence||[]){oldEvidence++;ok(r?.evidence?.some(x=>x.path===e.path&&x.blob_sha===e.git_blob_sha),'missing_prior_evidence:'+original.slot)}
  }
  ok(oldEvidence===96,'prior_96');
  const seen=new Set(),over=[];let newRows=0;
  ok(docs.batches?.length===12,'12_inputs');
  for(const b of docs.batches||[]){
   const entries=b.obj.rows||b.obj.source_rows||b.obj.records||b.obj.sources||[];
   ok(o.batch_sources.some(x=>x.file===b.path&&x.blob_sha===b.sha&&x.source_records===entries.length),'source_blob_drift:'+b.path);
   for(const item of entries){
    const s=slot(item),r=map.get(s);newRows++;
    ok(!seen.has(s),'duplicate_new:'+s);seen.add(s);ok(r?.stored_url===url(item),'source_mismatch:'+s);
    ok(r?.evidence?.some(e=>e.path===b.path&&e.blob_sha===b.sha),'missing_new_evidence:'+s);
    if(docs.prior?.rows?.some(x=>x.slot===s))over.push(s);
   }
  }
  ok(newRows===76&&seen.size===76,'new_76');
  ok(over.sort().join(',')==='214:0,214:4','overlap_replay');
  ok(new Set([...(docs.prior?.rows||[]).map(x=>x.slot),...seen]).size===167,'union_167');
 }
 return {ok:errors.length===0,errors,stats:{rows:rows.length,researched,pending:rows.length-researched,records:rows.reduce((n,r)=>n+(r.evidence?.length||0),0)}};
}
module.exports={validate,slot,url};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const root=path.resolve(__dirname,'../..'),bytes=p=>fs.readFileSync(path.join(root,p)),read=p=>JSON.parse(bytes(p).toString('utf8'));
 const o=read(prefix+'coverage_167_exact_pr1703_20261110.json');
 const sources=[o.frozen_source,o.prior_reconciliation,...o.batch_sources.map(b=>({path:b.file,blob_sha:b.blob_sha}))];
 const shaErrors=sources.filter(s=>crypto.createHash('sha1').update('blob '+bytes(s.path).length+'\0').update(bytes(s.path)).digest('hex')!==s.blob_sha).map(s=>'source_git_sha_drift:'+s.path);
 const docs={census:read(o.frozen_source.path),prior:read(o.prior_reconciliation.path),batches:o.batch_sources.map(x=>({path:x.file,sha:x.blob_sha,obj:read(x.file)}))};
 const result=validate(o,docs);result.errors.push(...shaErrors);result.ok=!result.errors.length;
 process.stdout.write(JSON.stringify(result,null,2)+'\n');process.exitCode=result.ok?0:1;
}

'use strict';
/** Read-only proof boundary: retriever errors are NOT guest-browser failures. */
const fs=require('node:fs');
const {createHash}=require('node:crypto');
const expected=Object.freeze({
 '285:5':['b6a3b4ca2f7ea05a05c1ce8ed62d2101c48cccb089b8f0338c8232d3354041ab',404,'not_found'],
 '285:2':['6975275c6b7660b8d17c21e0a51cb25f2771563bb133d61a6cf83372f7903dbe',500,'redirect_target_inaccessible'],
 '287:5':['31a1074a3e7a184fa654b9b24d8e5262a84b781206cad5f66bce0ee304995d2b',404,'not_found'],
 '418:1':['b4be4bbe4f49607e1b9363fef60cebefe01426444d17349b75169e0090a44174',403,'forbidden'],
 '418:2':['c4f3b40143f5a0a6e487778639bd68164899d9ed514ca908c4769e558351030e',403,'forbidden'],
 '407:1':['4b2fa9f5a33d32f7381b2219d073b7ddac289cf80f923a3e78d8e2afb4128fa8',400,'unsupported_binary_content_type']
});
const eq=(a,b)=>a===b;
const nil=x=>x===null;
const safeUrl=x=>{try{const u=new URL(x);return u.protocol==='https:'&&!!u.hostname&&!u.username&&!u.password;}catch{return false;}};
function validate(a){
 const errors=[];const bad=s=>errors.push(s);
 if(!a||typeof a!=='object'||Array.isArray(a))return {ok:false,errors:['invalid_payload']};
 if(a.schema!=='fv-p0-six-retriever-recheck-v1'||a.date_pt!=='2026-11-14')bad('schema_or_date');
 const custody=a.source_custody||{};
 if(custody.previous_wp_readback_20261108_blob!=='04df35ce25f99626c7b754c1d7eed0f3f006e3f4'||
   custody.post_count_in_prior_wp_readback!==4||custody.live_wp_verified_this_sprint!==false)bad('source_custody');
 if(typeof a.methodology!=='string'||!a.methodology.includes('no origin-server HEAD/GET'))bad('method_not_limited');
 const b=a.historical_census||{};
 if(b.posts!==61||b.inline_images!==355||b.external_refs_media!==288||b.external_refs_site_qa!==286||
   b.broken_originals_reported!==42||!nil(b.broken_guest_verified)||b.sitewide_wire_reduction_76_percent_measured!==false)
  bad('census_or_fabricated_proof');
 const large=a.last_verified_large_wp_origins||{};
 if(large.threshold_decimal_bytes_exclusive!==1500000||large.count!==16||large.total_stored_bytes!==49107665||
   !nil(large.actual_visitor_bytes))bad('stored_bytes_mislabeled_as_wire');
 if(!Array.isArray(a.rows)||a.rows.length!==6)bad('six_rows_required');
 const seen=new Set();
 for(const r of Array.isArray(a.rows)?a.rows:[]){
  const key=r?.slot,e=expected[key];
  if(!e||seen.has(key)){bad('unexpected_or_duplicate_slot:'+key);continue;}
  seen.add(key);
  if(r.post_id!==Number(key.split(':')[0]))bad('post_slot_mismatch:'+key);
  const f=r.fresh_retriever||{},c=r.candidate||{},rel=r.release||{};
  const identity=[r.published_src_prior_wp_readback,c.catalog_or_candidate_url,c.relationship,c.rights_status].join('\n');
  const digest=createHash('sha256').update(identity).digest('hex');
  if(!eq(digest,e[0])||!safeUrl(r.published_src_prior_wp_readback)||!safeUrl(c.catalog_or_candidate_url))
   bad('source_candidate_or_rights_drift:'+key);
  if(f.date_pt!=='2026-11-14'||f.method!=='web.open'||f.tool_result_code!==e[1]||f.tool_result!==e[2])
   bad('unverified_retriever_result:'+key);
  for(const k of ['origin_http_status','logged_out_browser_http_status','current_src','decoded_intrinsic_px','encoded_transfer_bytes','guest_broken'])
   if(!nil(f[k]))bad('fabricated_guest_or_origin_evidence:'+key+':'+k);
  if(c.item_republication_rights_cleared!==false||c.historical_scene_verified_for_replacement!==false||
    c.editor_approved!==false||!nil(c.same_binary_sha256))bad('unsupported_clearance_or_identity:'+key);
  const d=c.native_dimensions_px,dev=c.conditional_no_upscale_960px_dimensions;
  if(key==='285:5'){
   if(!Array.isArray(d)||d[0]!==819||d[1]!==614||!Array.isArray(dev)||dev[0]!==819||dev[1]!==614)
    bad('tmi_native_no_upscale_geometry:'+key);
  }else if(!nil(d)||!nil(dev))bad('invented_candidate_dimensions:'+key);
  if(rel.auto_replace!==false||rel.download_or_cache!==false||rel.wordpress_write!==false||rel.risk_status!=='HOLD')
   bad('unauthorized_replacement_or_cache:'+key);
 }
 if(seen.size!==6)bad('p0_slot_set_incomplete');
 const rel=a.release||{};
 if(rel.guest_browser_evidence_required!==true||rel.rights_and_scene_approval_required!==true||
    rel.max_derivative_width_px!==960||rel.no_upscale!==true||rel.all_hold!==true||
    rel.binaries_downloaded!==0||rel.wordpress_prod_writes!==0||rel.homepage_design_writes!==0||
    rel.merges!==0||rel.deployments!==0||rel.subscriptions_usd!==0)bad('release_gate_violation');
 return {ok:errors.length===0,errors};
}
if(require.main===module){try{
 if(process.argv.length!==3)throw Error('Usage: node validate_p0_six_recheck_20261114.cjs AUDIT.json');
 const d=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
 const r=validate(d);console.log(JSON.stringify(r));if(!r.ok)process.exitCode=2;
 }catch(e){console.error('VALIDATION_INPUT_ERROR '+e.message);process.exitCode=2;}}
module.exports={validate};

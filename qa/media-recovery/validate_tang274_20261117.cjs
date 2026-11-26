'use strict';
const fs=require('node:fs'),crypto=require('node:crypto');
const PIN='c0d54c30769b0276a143c2f77b897202d818105f';
const sha=s=>{const b=Buffer.from(s,'utf8');return crypto.createHash('sha1').update('blob '+b.length+String.fromCharCode(0)).update(b).digest('hex');};
function verify(o,src,sourceRaw){const bad=m=>{throw Error(m)};
 if(sha(sourceRaw)!==PIN||o.source_snapshot?.git_blob_sha!==PIN)bad('source SHA drift');
 if(o.schema!=='fv-tang-274-seven-original-readonly-v1'||o.post_id!==274||o.status!=='REVIEW_ONLY')bad('schema');
 const slots=src.images.filter(x=>x.post_id===274).sort((a,b)=>a.slot-b.slot);if(slots.length!==7||o.slots?.length!==7)bad('slots');
 if(o.scope?.reported_broken_42_guest_confirmed!==null||o.scope?.claimed_76_percent_wire_reduction_measured!==false||o.scope?.visitor_wire_bytes!==null)bad('unproven claims');
 if(Object.entries(o.source_policy||{}).some(([k,v])=>typeof v==='boolean'&&v!==true)||o.source_policy?.media_max_width_px!==960)bad('production policy');
 if(o.slots.filter(r=>r.official_candidate).length!==7)bad('candidate count');
 const EXPECTED_ACCESSIONS=['NH 42273','80-G-227987','NH 84498','NH 45641','80-G-344565','80-G-227991','80-G-227989'];
 const EXPECTED_STATES=[['BINARY_RENDERED','not_reported'],['GATEWAY_ERROR',502],['GATEWAY_ERROR',502],['INTERNAL_TOOL_ERROR','not_reported'],['GATEWAY_ERROR',502],['BINARY_RENDERED','not_reported'],['RETRIEVER_HTTP_ERROR',404]];
 const seen=new Set();for(let i=0;i<7;i++){const r=o.slots[i],s=slots[i];
 if(r.slot!=='274:'+i||seen.has(r.slot))bad('slot identity');seen.add(r.slot);
 if(r.authored_view_src!==s.authored_view_src||r.source_origin_url!==s.source_origin_url||r.alt!==s.alt||r.source_route!==s.route_type)bad('exact URL mismatch');
 if(!r.guest_chromium||!['http_status','decoded','transferred_bytes','current_src','raster_sha256'].every(k=>Object.hasOwn(r.guest_chromium,k)&&r.guest_chromium[k]===null))bad('fabricated or incomplete browser');
 if(r.rights?.rehost_approved!==false||r.rights?.item_specific_rights_confirmed!==false)bad('rights hold');
 if(r.geometry?.no_upscale!==true||r.geometry?.native_master_dimensions_verified!==false||r.geometry?.master_sha256!==null||r.geometry?.max_width_px>960)bad('geometry hold');
 if((r.official_candidate?.accession??null)!==EXPECTED_ACCESSIONS[i])bad('catalog accession changed');
 if(i===3){
   if(r.official_candidate?.match_level!=='caption_subject_match_only'||r.official_candidate?.identical_raster_verified!==false||r.official_candidate?.actual_navy_record_http_status!==null)bad('Momsen exact frame/browser claim');
   const d=r.official_candidate?.official_catalog_high_tiff_dimensions_reported;
   if(d?.width_px!==4520||d?.height_px!==5080||r.geometry?.catalog_reported_master_width_px!==4520||r.geometry?.catalog_reported_master_height_px!==5080||r.geometry?.provisional_960w_height_px!==1079||r.geometry?.provisional_only_not_generated!==true)bad('Momsen catalog dimensions or derivative claim');
   if(r.rights?.publisher_original_rights_still_unverified!==true)bad('Momsen source rights not held');
 }
 if(r.official_candidate&&(!/^https:\/\/www\.history\.navy\.mil\//.test(r.official_candidate.catalog_url)||!/^(accession_and_subject_match|accession_in_original_query|caption_subject_match_only|subject_match_only)$/.test(r.official_candidate.match_level)))bad('unverified catalog');
 const p=r.public_retriever||{};if(p.result!==EXPECTED_STATES[i][0]||p.reported_status!==EXPECTED_STATES[i][1])bad('original reader observation drift');
 }if(o.slots[6].public_retriever.reported_status!==404)bad('404 evidence');
 return {status:'PASS',slots:7,official_candidates:7,guest_browser_confirmed:null,production_writes:0};}
module.exports={verify,sha,PIN};
if(require.main===module){try{const [ledgerPath,sourcePath]=process.argv.slice(2);if(!ledgerPath||!sourcePath)throw Error('usage: node validate_tang274_20261117.cjs ledger.json source_slice_5.json');const raw=fs.readFileSync(sourcePath,'utf8');console.log(JSON.stringify(verify(JSON.parse(fs.readFileSync(ledgerPath,'utf8')),JSON.parse(raw),raw),null,2));}catch(e){console.error('HOLD: '+e.message);process.exitCode=1;}}

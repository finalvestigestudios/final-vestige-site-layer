'use strict';
const fs=require('node:fs'),crypto=require('node:crypto');
const PIN='c0d54c30769b0276a143c2f77b897202d818105f';
const sha=s=>{const b=Buffer.from(s,'utf8');return crypto.createHash('sha1').update('blob '+b.length+'\\0'.replace('\\0','\0')).update(b).digest('hex');};
function verify(o,src,sourceRaw){const bad=m=>{throw Error(m)};
 if(sha(sourceRaw)!==PIN||o.source_snapshot?.git_blob_sha!==PIN)bad('source SHA drift');
 if(o.schema!=='fv-tang-274-seven-original-readonly-v1'||o.post_id!==274||o.status!=='REVIEW_ONLY')bad('schema');
 const slots=src.images.filter(x=>x.post_id===274).sort((a,b)=>a.slot-b.slot);if(slots.length!==7||o.slots?.length!==7)bad('slots');
 if(o.scope?.reported_broken_42_guest_confirmed!==null||o.scope?.claimed_76_percent_wire_reduction_measured!==false||o.scope?.visitor_wire_bytes!==null)bad('unproven claims');
 if(Object.entries(o.source_policy||{}).some(([k,v])=>typeof v==='boolean'&&v!==true)||o.source_policy?.media_max_width_px!==960)bad('production policy');
 if(o.slots.filter(r=>r.official_candidate).length!==6)bad('candidate count');
 const seen=new Set();for(let i=0;i<7;i++){const r=o.slots[i],s=slots[i];
 if(r.slot!==\`274:\${i}\`||seen.has(r.slot))bad('slot identity');seen.add(r.slot);
 if(r.authored_view_src!==s.authored_view_src||r.source_origin_url!==s.source_origin_url||r.alt!==s.alt||r.source_route!==s.route_type)bad('exact URL mismatch');
 if(!Object.values(r.guest_chromium||{}).every(v=>v===null))bad('fabricated browser');
 if(r.rights?.rehost_approved!==false||r.rights?.item_specific_rights_confirmed!==false)bad('rights hold');
 if(r.geometry?.no_upscale!==true||r.geometry?.native_master_dimensions_verified!==false||r.geometry?.master_sha256!==null||r.geometry?.max_width_px>960)bad('geometry hold');
 if(i===3&&r.official_candidate!==null)bad('unverified image identity');
 if(r.official_candidate&&(!/^https:\/\/www\.history\.navy\.mil\//.test(r.official_candidate.catalog_url)||!/^(accession_and_subject_match|accession_in_original_query|caption_subject_match_only|subject_match_only)$/.test(r.official_candidate.match_level)))bad('unverified catalog');
 const p=r.public_retriever||{};if(!({BINARY_RENDERED:'not_reported',GATEWAY_ERROR:502,INTERNAL_TOOL_ERROR:'not_reported',RETRIEVER_HTTP_ERROR:404}[p.result]===p.reported_status))bad('status provenance');
 }if(o.slots[6].public_retriever.reported_status!==404)bad('404 evidence');
 return {status:'PASS',slots:7,official_candidates:6,guest_browser_confirmed:null,production_writes:0};}
module.exports={verify,sha,PIN};
if(require.main===module){try{const [ledgerPath,sourcePath]=process.argv.slice(2);if(!ledgerPath||!sourcePath)throw Error('usage: node validate_tang274_20261117.cjs ledger.json source_slice_5.json');const raw=fs.readFileSync(sourcePath,'utf8');console.log(JSON.stringify(verify(JSON.parse(fs.readFileSync(ledgerPath,'utf8')),JSON.parse(raw),raw),null,2));}catch(e){console.error('HOLD: '+e.message);process.exitCode=1;}}

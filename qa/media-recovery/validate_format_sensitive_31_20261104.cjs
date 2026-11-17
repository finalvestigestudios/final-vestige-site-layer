'use strict';
/**
 * Reproduce an exact 31-slot visual-format audit from eight frozen, read-only
 * WordPress source parts. No web access, CMS writes, image retrieval or rehosting.
 * Usage: node qa/media-recovery/validate_format_sensitive_31_20261104.cjs
 */
const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const dir=__dirname;
const isSensitive=url=>/\.(?:png|gif|svg)(?:[?#]|$)/i.test(String(url));
const extOf=url=>(String(url).split('?')[0].match(/\.([a-zA-Z0-9]+)$/)||[])[1]?.toLowerCase()||null;
const gitBlobSha=raw=>crypto.createHash('sha1').update('blob '+Buffer.byteLength(raw,'utf8')+'\0'+raw).digest('hex');
function validate(data,parts,large) {
 const errors=[],fail=(v)=>errors.push(v);
 if(data?.schema!=='fv-media-format-integrity-sitewide-census-v1')fail('schema');
 if(!Array.isArray(parts)||parts.length!==8)fail('frozen_eight_parts_required');
 const names=new Set(),images=[];
 for(const p of parts||[]){
  if(names.has(p.name)||!/^qa\/media-recovery\/parts\/0[1-8]\.json$/.test(p.name))fail('source_path');
  names.add(p.name);
  if(data?.sources?.[p.name]!==gitBlobSha(p.raw))fail('source_blob_sha:'+p.name);
  try{images.push(...JSON.parse(p.raw).images)}catch{fail('bad_source_json:'+p.name)}
 }
 if(images.length!==355)fail('355_source_slots_required');
 if(new Set(images.map(x=>x.key)).size!==images.length)fail('duplicate_source_key');
 const expected=images.filter(x=>isSensitive(x.source_url));
 const expectedKeys=new Map(expected.map(x=>[x.key,x]));
 const rows=data?.rows;
 if(!Array.isArray(rows)||rows.length!==expected.length||rows.length!==31)fail('31_rows_required');
 const visited=new Set(),types={png:0,gif:0,svg:0},usedLarge=new Set();
 const library=new Map((large?.rows||[]).map(x=>[x.original_url,x]));
 for(const r of Array.isArray(rows)?rows:[]){
  const s=expectedKeys.get(r.key);
  if(!s||visited.has(r.key)){fail('bad_or_duplicate_key:'+r.key);continue}
  visited.add(r.key);
  if(r.original_url!==s.source_url||r.original_alt!==s.alt||
   r.post_id!==s.post_id||r.post_url!==s.post_url)fail('source_mismatch:'+r.key);
  const kind=extOf(s.source_url);
  if(r.media_format!==kind||!Object.hasOwn(types,kind))fail('format_mismatch:'+r.key);
  else types[kind]++;
  if(r.actual_guest_browser_http_status!==null||r.actual_guest_browser_current_src!==null||
    r.actual_guest_browser_decode_ok!==null||r.actual_browser_transfer_bytes!==null||
    r.actual_lab_cls!==null||r.broken_original_in_browser!==null)fail('fabricated_browser_proof:'+r.key);
  if(r.rehost_or_cache_approved!==false||r.rights_status!=='HOLD'||
     r.production_write_approved!==false)fail('rights_or_publish_bypass:'+r.key);
  if(r.max_width_conditional_px!==null&&(!Number.isSafeInteger(r.max_width_conditional_px)||
      r.max_width_conditional_px<1||r.max_width_conditional_px>960))fail('bad_960_width:'+r.key);
  const l=library.get(r.original_url),m=r.first_party_oversized_wordpress_original;
  if(m){
   usedLarge.add(r.key);
   if(!l||l.mime_type!=='image/png'||l.original_bytes<=1572864||
       m.media_id!==l.media_id||m.media_original_storage_bytes!==l.original_bytes||
       m.verified_media_metadata_dimensions_px?.width!==l.dimensions_px?.width||
       m.verified_media_metadata_dimensions_px?.height!==l.dimensions_px?.height||
       r.max_width_conditional_px!==960||r.max_height_conditional_px!==540)
     fail('unsupported_large_original:'+r.key);
  }else if(l&&l.mime_type==='image/png')fail('missing_large_original_evidence:'+r.key);
  if(!m&&r.max_width_conditional_px!==null)fail('invented_intrinsic_geometry:'+r.key);
  if(r.catalog_candidate&&(!r.catalog_candidate.source_record_url?.startsWith('https://')||
     !r.catalog_candidate.reuse_rights_status?.startsWith('HOLD:')))
      fail('unsupported_catalog_clearance:'+r.key);
 }
 for(const k of expectedKeys.keys())if(!visited.has(k))fail('missing_actual_slot:'+k);
 if(types.png!==28||types.gif!==2||types.svg!==1)fail('extension_counts');
 if(usedLarge.size!==5)fail('five_large_originals');
 const x=data?.inventory;
 if(x?.published_posts!==61||x?.all_img_src_references!==355||
    x?.offsite_img_src_references!==288||x?.format_sensitive_slots!==31||
    x?.original_over_1_5MiB_count!==13||x?.original_storage_bytes_for_13!==43522829||
    x?.reported_broken_42!=='NOT_BROWSER_VERIFIED'||
    x?.claimed_76pct_image_wire_reduction!=='NOT_MEASURED'||
    x?.actual_image_wire_saving_percent!==null||x?.production_repairs!==0)
    fail('fabricated_site_claims');
 if(data?.priorities?.join('|')!=='285:5|285:2|287:5|418:1|418:2|407:1')
   fail('changed_site_qa_priority');
 return {ok:errors.length===0,errors,checked_rows:Array.isArray(rows)?rows.length:0,source_slots:images.length,types};
}
function run(){
 const file=JSON.parse(fs.readFileSync(path.join(dir,'format_sensitive_31_sitewide_20261104.json'),'utf8'));
 const parts=Array.from({length:8},(_,i)=>{const name='qa/media-recovery/parts/'+String(i+1).padStart(2,'0')+'.json';
  return{name,raw:fs.readFileSync(path.join(dir,'parts',String(i+1).padStart(2,'0')+'.json'),'utf8')}});
 const large=JSON.parse(fs.readFileSync(path.join(dir,'large_first_party_20261101.json'),'utf8'));
 const report=validate(file,parts,large);
 process.stdout.write(JSON.stringify(report,null,2)+'\n');
 if(!report.ok)process.exitCode=1;
}
if(require.main===module)run();
module.exports={validate,gitBlobSha,extOf};

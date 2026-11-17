'use strict';
// Read-only validation: catalog-derived geometry is NOT Chrome intrinsic dimensions.
const https=s=>typeof s==='string'&&/^https:\/\/[a-z0-9.-]+\//i.test(s);
const noActualStatus=x=>x===null;
function validateAzorian(a,frozen){
 const errors=[],fail=m=>errors.push(m);
 if(!a||a.schema_version!==1||a.post_id!==218||a.sample_size!==6||
    a.frozen_blob_sha!=='0f3dfe398a76838049cebba7cb773d5c5a0c8c69')fail('invalid fixed census');
 const w=a?.verified_wp_state||{};
 if(w.status!=='publish'||w.last_modified!=='2026-10-29T16:01:32'||
    w.frozen_urls_and_alts_exact!==true||w.html_width_height_pairs!==0)fail('live WP readback drift');
 if(!Array.isArray(frozen)||frozen.length!==6)fail('frozen post missing');
 const rows=a?.rows;
 if(!Array.isArray(rows)||rows.length!==6)return {ok:false,errors:[...errors,'wrong row count']};
 const metrics=a?.metrics||{};
 if(metrics.published_sources!==6||metrics.commons_redirect_sources!==6||
    metrics.originals_at_or_below_960px!==3||metrics.originals_above_960px!==3||
    metrics.catalog_originals_above_1_5_mib!==2||
    metrics.actual_browser_broken_confirmed!==0||metrics.actual_browser_transfer_bytes!==null||
    metrics.reported_42_browser_verified!==false||metrics.claimed_76percent_wire_measured!==false||
    metrics.production_replacements!==0||
    metrics.sitewide_baseline?.published_posts!==61||metrics.sitewide_baseline?.inline_image_references!==355||
    metrics.sitewide_baseline?.offsite_original_references!==288||
    metrics.sitewide_baseline?.wp_media_originals_above_1_5_mib!==13)fail('unsupported metrics');
 const originalKeys=new Set(),catalogUrls=new Set();
 for(let i=0;i<6;i++){
   const row=rows[i],source=frozen?.[i],tag='slot'+i;
   if(!row||!source||row.slot!==source.key||row.published_url!==source.source_url||
      row.published_alt!==source.alt||row.published_html_dimensions!==null||
      !row.published_url.includes('Special:Redirect/file/')||
      row.requested_width_parameter_px!==1280)fail(tag+': published source drift');
   if(!https(row.catalog_record_url)||!row.catalog_record_url.includes('commons.wikimedia.org/wiki/File:')||
      !https(row.primary_institutional_context_url)||
      !row.primary_institutional_context_url.includes('cia.gov/')||
      row.archive_relation!=='same_named_commons_file_catalog_not_verified_binary_hash'||
      originalKeys.has(row.slot)||catalogUrls.has(row.catalog_record_url))fail(tag+': invalid provenance');
   originalKeys.add(row.slot);catalogUrls.add(row.catalog_record_url);
   const d=row.catalog_dimensions_px||{},t=row.conditional_derivative_px||{};
   const expectedWidth=Math.min(960,d.width);
   if(!Number.isSafeInteger(d.width)||d.width<1||!Number.isSafeInteger(d.height)||d.height<1||
      !Number.isSafeInteger(t.width)||t.width!==expectedWidth||
      t.height!==Math.round(expectedWidth*d.height/d.width)||t.height<1||
      row.no_upscale!==true)fail(tag+': unlawful geometry or speculative dimensions');
   if(typeof row.catalog_rights_note!=='string'||row.catalog_rights_note.length<15||
      row.item_rights_review!=='HOLD'||row.attribution_review!=='HOLD'||
      row.cache_or_rehost_allowed!==false||row.wordpress_write_allowed!==false)fail(tag+': rights/release invalid');
   if(!noActualStatus(row.real_guest_http_status)||row.real_guest_decode_ok!==null||
      row.real_guest_transfer_bytes!==null||row.image_binary_sha256!==null||
      row.web_retriever_observation!=='exact_1280_redirect_not_accessible_to_text_retriever_no_origin_http_status')
       fail(tag+': invented visitor/byte evidence');
 }
 if(a?.rights_and_release!=='NO_DOWNLOAD_NO_COPY_NO_WP_WRITE')fail('publication guard removed');
 return {ok:errors.length===0,errors,validated_rows:rows.length,visitor_broken_verified:false,weight_reduction_verified:false,production_write_authorized:false};
}
module.exports={validateAzorian};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const root=__dirname,partPath=path.join(root,'parts','06.json'),raw=fs.readFileSync(partPath);
 const blob=crypto.createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex');
 const doc=JSON.parse(fs.readFileSync(path.join(root,'azorian_218_six_commons_20261104.json'),'utf8'));
 const result=validateAzorian(doc,JSON.parse(raw).images.filter(x=>x.post_id===218));
 process.stdout.write(JSON.stringify({...result,source_blob_sha:blob},null,2)+'\n');
 if(blob!==doc.frozen_blob_sha||!result.ok)process.exitCode=1;
}

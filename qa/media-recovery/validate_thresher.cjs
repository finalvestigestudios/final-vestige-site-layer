'use strict';
/** Pure custody and no-upscale rights validator; no WordPress writes or network access. */
const EXPECTED=[
 ['220:0','NH 97545',4918,6136],['220:1','NH 97552',740,574],
 ['220:2','NH 97310',578,737],['220:3','NH 97567',740,532],
 ['220:4',null,1700,1349],['220:5','NH 97570',739,574],
 ['220:6','NH 97557',740,576]
];
const NHHC_PREFIX='https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-';
function validateThresher(data,census){
 const errors=[],check=(good,why)=>{if(!good)errors.push(why)};
 check(data&&data.schema_version===1&&data.post_id===220&&data.post_image_count===7,'source scope');
 check(data.verified_nhhc_catalog_crosswalks===6&&data.remaining_citation_only===1,'catalog count');
 check(data.reported_42_broken_status==='UNVERIFIED'&&data.reported_76_percent_weight_savings==='UNMEASURED'&&data.guest_browser_run_executed===false,'fabricated claims');
 check(Array.isArray(data.rows)&&data.rows.length===7,'row count');
 const originals=(census||[]).filter(x=>x.post_id===220);
 check(originals.length===7,'original snapshot count');
 const byKey=Object.fromEntries(originals.map(x=>[x.key,x]));
 for(let i=0;i<(data.rows||[]).length;i++){
  const r=data.rows[i],e=EXPECTED[i];if(!r||!e){errors.push('unexpected row '+i);continue}
  const src=byKey[e[0]];
  check(r.image_key===e[0]&&r.article_url===src?.post_url,'slot identity '+i);
  check(r.source_url===src?.source_url&&r.stored_alt===src?.alt,'exact URL/alt '+i);
  check(typeof r.source_url==='string'&&r.source_url.startsWith('https://commons.wikimedia.org/wiki/Special:Redirect/file/'),'stored source host '+i);
  const fname=decodeURIComponent(String(r.source_url).split('/').pop().split('?')[0]);
  const canonName=decodeURIComponent(String(r.commons_file_page).split('/').pop().split('?')[0]);
  check(String(r.commons_file_page).startsWith('https://commons.wikimedia.org/wiki/File:')&&canonName==='File:'+fname,'canonical Commons file identity '+i);
  check(r.catalog_id===e[1],'catalog accession '+i);
  if(e[1]){
   const num=e[1].slice(3);
   check(r.nhhc_record_url===NHHC_PREFIX+num+'.html'&&r.match_evidence==='COMMONS_FILE_DESCRIPTION_NAMES_OFFICIAL_NHHC_ID','primary catalog URL '+i);
  }else check(r.nhhc_record_url===null&&r.match_evidence==='COMMONS_ONLY_NAVSOURCE_UNVERIFIED_ORIGINAL','no fabricated primary match '+i);
  check(r.original_commons_width_px===e[2]&&r.original_commons_height_px===e[3],'original dimensions '+i);
  const tw=Math.min(960,e[2]),th=Math.round(e[3]*tw/e[2]);
  check(r.proposed_width_px===tw&&r.proposed_height_px===th&&r.no_upscale===true&&r.resize_max_width_px===960,'no upscale/aspect ratio '+i);
  check(r.rights_status==='HOLD_ITEM_LEVEL_REUSE_CHECK'&&r.reuse_cleared===false&&r.wp_media_upload_authorized===false&&r.wp_post_edit_authorized===false,'rights and CMS gate '+i);
  check(r.source_asset_hash_sha256===null&&r.source_binary_checked===false&&r.wp_media_id===null,'unverified binary/CMS ID '+i);
  check(r.guest_browser_http_status===null&&r.guest_browser_natural_width_px===null&&r.guest_browser_transfer_bytes===null&&r.confirmed_broken_in_browser===null&&r.measured_weight_reduction_pct===null,'no fabricated browser/wire '+i);
  check(typeof r.source_description==='string'&&r.source_description.length>=32&&typeof r.caption_integrity_caution==='string'&&r.caption_integrity_caution.length>=35,'source notes '+i);
 }
 return{ok:errors.length===0,errors,checked_images:data.rows?.length||0,nhhc_photo_crosswalks:6,originals_under_960:5,live_broken_count:null};
}
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),{loadSnapshot}=require('./validate_inventory.cjs');
 const file=path.join(__dirname,'thresher_nhhc_20261030.json');
 const result=validateThresher(JSON.parse(fs.readFileSync(file,'utf8')),loadSnapshot().parts.flatMap(x=>x.images));
 console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;
}
module.exports={validateThresher,EXPECTED};

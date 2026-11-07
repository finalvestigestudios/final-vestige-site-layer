'use strict';
// Offline, fail-closed manifest validator. No network or filesystem operations in validate().
function validate(x) {
 const e=[], need=(q,s)=>{if(!q)e.push(s);};
 const url=(s,h)=>typeof s==='string'&&s.startsWith('https://'+h+'/')&&!/[\s?#]/.test(s);
 if(!x||typeof x!=='object')return {ok:false,errors:['manifest missing']};
 need(x.schema==='fv-media-nasa-apollo1-v1','schema');
 need(x.article?.post_id===434&&x.article?.url==='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'&&x.article?.read_method?.includes('read-only')===true,'article');
 const sc=x.scope;
 need(sc?.inline_images===6&&sc?.first_party_images===1&&sc?.external_nasa_images===5&&sc?.catalog_records_found===5&&sc?.stored_html_width_height_present===6,'scope');
 need(x.rights?.policy_url==='https://www.nasa.gov/nasa-brand-center/images-and-media/'&&x.rights?.item_level_clearance==='REVIEW_REQUIRED_BEFORE_CACHE_OR_REPUBLICATION'&&x.rights?.allowed_automatic_localization===false,'rights gate');
 const perf=x.performance;
 need(perf?.legacy_post_cohort===61&&perf?.current_post_cohort===66&&perf?.alleged_broken===42&&perf?.guest_browser_verified_broken===null,'cohort and broken claims');
 need(perf?.proposed_transfer_savings_percent===76&&perf?.measured_transfer_savings_percent===null&&perf?.source_bytes_downloaded===null,'wire claims');
 need(perf?.oversize_wordpress_originals_count===13&&perf?.oversize_storage_bytes===43522829,'oversize scope');
 need(x.first_party_guard?.include_in_external_recovery===false&&url(x.first_party_guard?.src,'finalvestige.com'),'first-party exclusion');
 need(Array.isArray(x.images)&&x.images.length===5,'five NASA references');
 const ids=new Set(), sources=new Set(),keys=new Set();
 for(const [i,raw] of (Array.isArray(x.images)?x.images:[]).entries()){
  const y=raw&&typeof raw==='object'?raw:{};
  const k='item '+i+' ';
  need(y.key==='434:'+(i+1),'source position '+i);
  need(!ids.has(y.nasa_id)&&!sources.has(y.stored_src)&&!keys.has(y.key),k+'duplicate');ids.add(y.nasa_id);sources.add(y.stored_src);keys.add(y.key);
  need(/^(?:S[0-9]{2}-[0-9]+|KSC-[0-9]{8}-PH_KLS[0-9]{2}_[0-9]+)$/.test(y.nasa_id),k+'NASA identifier');
  need(y.stored_src==='https://images-assets.nasa.gov/image/'+y.nasa_id+'/'+y.nasa_id+'~large.jpg',k+'exact stored NASA image URL');
  need(url(y.nasa_catalog_url,'www.nasa.gov')&&y.nasa_catalog_url.includes('/image-detail/'),k+'primary NASA record');
  const [w,h]=y.publisher_metadata_native_dimensions||[];
  need(Number.isInteger(w)&&Number.isInteger(h)&&w>=960&&h>0&&w<=10000&&h<=10000,k+'catalog geometry');
  need(JSON.stringify(y.stored_html_dimensions)===JSON.stringify([w,h]),k+'HTML dimensions differ from catalog');
  need(JSON.stringify(y.conditional_preview_dimensions)===JSON.stringify([960,Math.round(h*960/w)]),k+'960px no-upscale geometry');
  need(typeof y.caption_credit==='string'&&y.caption_credit.startsWith('NASA / '),k+'attribution');
  need(typeof y.subject==='string'&&y.subject.length>35,k+'historical subject');
  const t=y.source_retrieval;
  need(t?.catalog_page_retrieved===true&&['rendered_as_image','web_retriever_internal_error'].includes(t?.stored_image_web_retriever),k+'retrieval evidence');
  need(t?.browser_http_status===null&&t?.browser_natural_width===null&&t?.browser_natural_height===null&&t?.browser_cold_transfer_bytes===null&&t?.visitor_broken===null,k+'unverified browser values');
  need(y.rights_state==='REVIEW_REQUIRED'&&y.binary_hash_match===null&&y.derivative_asset_url===null&&y.wordpress_publish_approved===false,k+'reproduction/publishing hold');
 }
 const r=x.release;
 for(const f of ['wordPress_writes','asset_downloads','third_party_caches','production_repairs','homepage_design_changes','subscription_spend_usd'])need(r?.[f]===0,'release '+f);
 return {ok:e.length===0,errors:e};
}
module.exports={validate};
if(require.main===module){const fs=require('node:fs');const p=process.argv[2];if(!p)throw Error('Usage: node validate_nasa_apollo1_20261106.cjs AUDIT.json');const result=validate(JSON.parse(fs.readFileSync(p,'utf8')));console.log(JSON.stringify(result));if(!result.ok)process.exitCode=2;}

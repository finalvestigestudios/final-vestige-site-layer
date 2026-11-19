'use strict';
function validate(d){
 const err=[],ok=(x,k)=>{if(!x)err.push(k)};
 ok(d?.schema==='fv-wp-oversized-exposure-20261117-v1','schema');
 ok(d?.read_method==='WP_AUTHENTICATED_MEDIA_AND_ASSOCIATED_CONTENT_VIEW','method');
 ok(d?.scope?.returned_media_images===132&&d?.scope?.media_pages===2,'media scope');
 ok(d?.scope?.decimal_threshold_bytes===1500000&&d?.scope?.binary_threshold_bytes===1572864,'thresholds');
 ok(d?.summary?.over_decimal_1_5MB===20&&d?.summary?.over_binary_1_5MiB===19&&d?.summary?.original_stored_bytes===64385752,'summary');
 ok(d?.summary?.reported_42_browser_failures_verified===null&&d?.summary?.claimed_76_percent_transfer_reduction_verified===false&&d?.summary?.visitor_transfer_bytes===null,'unverified metrics');
 for(const k of ['attachment_not_rendering_proof','unattached_not_unused_proof','featured_template_not_measured','jetpack_url_not_current_src_proof','stored_bytes_not_transfer_bytes'])ok(d?.caveats?.[k]===true,'caveat '+k);
 const kinds={published_inline:0,published_featured_only:0,draft_page_inline:0,unattached_unverified:0},ids=new Set();
 let sum=0,mib=0;
 ok(Array.isArray(d?.items)&&d.items.length===20,'item count');
 for(const x of (Array.isArray(d?.items)?d.items:[])){
  ok(Number.isInteger(x.media_id)&&!ids.has(x.media_id),'duplicate id');ids.add(x.media_id);
  ok(typeof x.original_url==='string'&&/^https:\/\/finalvestige\.com\/wp-content\/uploads\//.test(x.original_url),'media URL');
  ok(Number.isInteger(x.original_stored_bytes)&&x.original_stored_bytes>1500000,'stored original size');
  sum+=x.original_stored_bytes;if(x.original_stored_bytes>1572864)mib++;
  const w=x.native_dimensions_metadata?.width,h=x.native_dimensions_metadata?.height,tw=Math.min(960,w||0);
  ok(Number.isInteger(w)&&w>0&&Number.isInteger(h)&&h>0,'dimensions');
  ok(x.proposed_960px_no_upscale_metadata?.width===tw&&x.proposed_960px_no_upscale_metadata?.height===Math.round(tw*(h||0)/(w||1))&&x.proposed_960px_no_upscale_metadata?.geometry_only===true,'960px aspect ratio');
  ok(typeof x.mime_type==='string'&&x.mime_type.startsWith('image/'),'mime');
  ok(x.rights_review==='PENDING_INDIVIDUAL_ASSET_REVIEW'&&x.wp_upload_authorized===false&&x.wp_rewrite_authorized===false,'rights production gate');
  ok(x.browser_http_status===null&&x.browser_current_src===null&&x.browser_decode_success===null&&x.browser_transfer_bytes===null,'no fake browser evidence');
  ok(Number.isInteger(x.inline_tag_matches)&&x.inline_tag_matches>=0,'markup count');
  const p=x.parent_id,n=x.inline_tag_matches;
  let expectation=null;
  if(p===null&&x.parent_kind===null&&x.parent_status===null&&x.parent_url===null&&x.featured_media_id===null&&n===0)expectation='unattached_unverified';
  else if(Number.isInteger(p)&&x.parent_kind==='post'&&x.parent_status==='publish'&&n>0)expectation='published_inline';
  else if(Number.isInteger(p)&&x.parent_kind==='post'&&x.parent_status==='publish'&&n===0&&x.featured_media_id===x.media_id)expectation='published_featured_only';
  else if(Number.isInteger(p)&&x.parent_kind==='page'&&x.parent_status==='draft'&&n>0)expectation='draft_page_inline';
  ok(expectation===x.exposure_class&&expectation!==null,'group category');
  if(n>0)ok(typeof x.server_markup_img_src==='string'&&/^https:\/\//.test(x.server_markup_img_src),'actual server URL');
  else ok(x.server_markup_img_src===null,'not fabricated server URL');
  if(kinds[x.exposure_class]!==undefined)kinds[x.exposure_class]++;
 }
 ok(sum===64385752&&sum===d?.summary?.original_stored_bytes,'stored sum');
 ok(mib===19&&mib===d?.summary?.over_binary_1_5MiB,'binary sum');
 for(const [k,n] of Object.entries({published_inline:8,published_featured_only:4,draft_page_inline:2,unattached_unverified:6}))ok(kinds[k]===n&&d?.summary?.exposure_classes?.[k]===n,'group count '+k);
 return{ok:err.length===0,errors:err,metrics:{items:ids.size,sum,kinds}};
}
if(typeof module!=='undefined')module.exports={validate};
if(typeof module!=='undefined'&&typeof require!=='undefined'&&require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const d=JSON.parse(fs.readFileSync(path.join(__dirname,'wp_oversized_exposure_20_20261117_0428pt.json'),'utf8'));
 const result=validate(d);console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;
}

'use strict';
// Offline archival source-identity, rights and 960px safety gate; NEVER makes network/WP writes.
const EXPECTED_BLOB='948bc1b65b42799aa40cfdb810ddf6ffd80886b6';
const EXPECTED_SIZES=[[900,591],[1245,792],[1226,761],[798,1024],[1244,791],[994,625],[924,1105],[1227,783],[5098,3193]];
const titleFrom=(url,needle)=>decodeURIComponent((url.split(needle)[1]||'').split('?')[0]).replace(/_/g,' ');
function validate(a,census) {
 const e=[],bad=m=>e.push(m),b=a?.sitewide||{},ar=a?.article||{};
 if(a?.schema_version!==1||ar.id!==425||ar.inline_images!==9||ar.stored_external_images!==8||ar.current_wordpress_authenticated_recheck_done!==false||ar.source_blob_sha!==EXPECTED_BLOB||ar.source_part!=='qa/media-recovery/parts/01.json')bad('header/census');
 if(b.posts!==61||b.inline_references!==355||b.offsite_references!==288||b.over_1_5_mib_wordpress_originals!==13||b.reported_42_broken_browser_confirmed!==false||b.claimed_76_percent_weight_reduction_measured!==false||b.actual_broken_count!==null||b.actual_transfer_reduction_percent!==null||b.production_replacements!==0)bad('fabricated sitewide statistics');
 if(!a?.safety||Object.values(a.safety).some(v=>v!==true))bad('safety policy');
 const originals=(census?.images||[]).filter(x=>x.post_id===425).sort((x,y)=>x.slot-y.slot);
 if(originals.length!==9||!Array.isArray(a?.slots)||a.slots.length!==9)return [...e,'slot count'];
 a.slots.forEach((s,i)=>{
  const o=originals[i],p=s?.candidate||{},g=s?.geometry||{},v=s?.visitor||{},r=s?.release||{};
  if(!o||s.key!==o.key||s.slot!==i||s.post_id!==425||s.article_url!==o.post_url||s.published_source_url!==o.source_url||s.published_alt!==o.alt||s.source_kind!==o.source_kind||s.inventory_blob_sha!==EXPECTED_BLOB||s.current_wp_editor_rechecked!==false)bad('frozen source '+i);
  const match=o.source_url.match(/[?&]width=(\d+)/);
  if(s.requested_width_in_stored_url!==(match?Number(match[1]):null))bad('request geometry '+i);
  const [w,h]=EXPECTED_SIZES[i],tw=Math.min(960,w),th=Math.round(h*tw/w);
  if(g.reference_width_px!==w||g.reference_height_px!==h||g.proposed_width_px!==tw||g.proposed_height_px!==th||g.no_upscale!==true||g.visitor_transfer_bytes!==null||!g.reference_measurement)bad('original geometry '+i);
  if(i===0) {
   if(p.file_catalog_url!==null||p.commons_original_title!==null||p.catalog_html_opened!==false||p.public_domain_claim_in_commons!==false)bad('first party '+i);
  } else {
   const stored=titleFrom(s.published_source_url,'/file/'),catalog=titleFrom(p.file_catalog_url,'/File:');
   if(stored!==catalog||p.commons_original_title!==stored||p.catalog_html_opened!==true||p.public_domain_claim_in_commons!==true||!p.file_catalog_url.startsWith('https://commons.wikimedia.org/wiki/File:'))bad('wrong Commons item '+i);
  }
  if(!p.authority||!p.credit_or_caption_note||!p.match_method||p.us_rights_independently_confirmed!==false||p.exact_binary_match_confirmed!==false||p.master_sha256!==null||p.caching_rights_cleared!==false)bad('rights and source '+i);
  if(Object.keys(v).length!==8||Object.values(v).some(x=>x!==null))bad('invented guest-browser evidence '+i);
  if(Object.keys(r).length!==4||Object.values(r).some(x=>x!==false))bad('unauthorized release '+i);
 });
 if(!a.slots[7]?.candidate?.credit_or_caption_note?.includes('Berthou')||!a.slots[6]?.candidate?.credit_or_caption_note?.includes('Not an event photograph'))bad('historical-integrity safeguards');
 return e;
}
module.exports={validate};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const a=JSON.parse(fs.readFileSync(path.join(__dirname,'courrieres_425_commons_20261101.json'),'utf8'));
 const c=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/01.json'),'utf8'));
 const e=validate(a,c);if(e.length){console.error(e);process.exitCode=1;}else console.log('Courrieres source/rights/dimensions validated');
}

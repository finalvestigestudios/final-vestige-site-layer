'use strict';
// Offline archival-provenance gate. Never downloads, uploads, or writes WordPress.
const fs = require('node:fs');
function hold(message){throw new Error('HOLD: '+message);}
const https=x=>{try{const u=new URL(x);return u.protocol==='https:'&&!u.username&&!u.password;}catch{return false;}};
function validate(a){
  if(!a||a.schema!=='fv-media-scotch-cap-provenance-v1'||a.scope!=='read_only_source_catalog_crosswalk_no_guest_browser'||a.post_id!==418||a.historical_event_date!=='1946-04-01'||!https(a.post_url))hold('source scope, event or post drift');
  if(!Array.isArray(a.historical_sources)||a.historical_sources.length!==4||!a.historical_sources.every(https))hold('missing primary event provenance');
  const er=a.editorial_risk;
  if(!er||er.official_event_year!==1946||er.parent_noaa_article_year!==1946||er.media_card_caption_year!==1964||!Array.isArray(er.noaa_media_caption_urls_incorrectly_say_1964)||er.noaa_media_caption_urls_incorrectly_say_1964.length!==2||!er.noaa_media_caption_urls_incorrectly_say_1964.every(https)||er.result!=='CONFLICT_HOLD_DO_NOT_COPY_NOAA_MEDIA_CARD_CAPTIONS'||!String(er.name_conflict||'').includes('Petit'))hold('NOAA source conflict/name uncertainty suppressed');
  if(!Array.isArray(a.slots)||a.slots.length!==2||a.slots.map(x=>x.key).join('|')!=='418:1|418:2')hold('missing or displaced slot');
  const [portrait,debris]=a.slots;
  for(const slot of a.slots){
    if(!https(slot.authored_src)||!https(slot.exact_origin_url)||!slot.authored_src.startsWith('https://i0.wp.com/')||decodeURIComponent(new URL(slot.authored_src).pathname)!=='/'+new URL(slot.exact_origin_url).hostname+decodeURIComponent(new URL(slot.exact_origin_url).pathname) )hold('unmatched authored/origin identity');
    const p=slot.prior_public_retriever,v=slot.current_public_jetpack_retriever,g=slot.guest_chromium,c=slot.candidate;
    if(!p||p.kind!=='HTTP_ERROR'||p.http_status!==403||!v||v.kind!=='TOOL_INACCESSIBLE'||v.http_status!==null||!g||g.final_http!==null||g.decoded!==null||g.natural_width!==null||g.wire_bytes!==null)hold('fabricated HTTP/visitor diagnosis');
    if(!c||!https(c.catalog_url)||c.rehost_authorized!==false||c.master_sha256!==null||slot.max_derivative_width_px!==960||slot.no_upscale!==true||slot.wp_production_write!==false)hold('unsafe copy/resize/WordPress authorization');
    if(c.native_width_px!==null){
      const w=c.native_width_px,h=c.native_height_px,tw=c.proposed_width_px,th=c.proposed_height_px;
      if(![w,h,tw,th].every(v=>Number.isSafeInteger(v)&&v>0)||tw>960||tw>w||th>h||Math.abs(tw/th-w/h)>0.02)hold('geometry violates no-upscale or 960px');
    }else if(c.native_height_px!==null||c.proposed_width_px!==null||c.proposed_height_px!==null)hold('invented native dimensions');
  }
  if(!portrait.exact_origin_url.endsWith('/210330-G-DE713-0002.JPG')||portrait.candidate.catalog_virin!=='210330-G-DE713-0002.JPG'||!portrait.candidate.identity_level.startsWith('SAME_USCG_VIRIN')||!portrait.candidate.rights.includes('DOD_LIMITATIONS')||!portrait.candidate.subject_name_variants.includes('Anthony L. Petit')||!portrait.candidate.subject_name_variants.includes('Anthony Pettit'))hold('USCG portrait accession, rights or spelling ambiguity');
  if(!debris.exact_origin_url.endsWith('5_%20Scotch_Cap_debris2_1946.jpg')||!debris.candidate.preview_url.endsWith('5_-Scotch_Cap_debris2_1946-600x463.jpg')||debris.candidate.identity_level!=='MATCHING_STEM_AND_SUBJECT_ONLY_NOT_BINARY_OR_CROP_VERIFIED'||debris.candidate.rights.indexOf('UNVERIFIED')===-1)hold('debris crop or rights proof invented');
  const s=a.sitewide_baseline,r=a.release;
  if(!s||s.historical_posts!==61||s.historical_images!==355||s.historical_third_party!==288||s.latest_census_posts!==66||s.latest_images!==361||s.latest_external_origin!==294||s.reported_broken_guest_confirmed!==null||s.claimed_76pct_visitor_byte_saving_verified!==false||s.visitor_wire_bytes!==null||s.oversized_originals_decimal_mb!==20||s.oversized_stored_bytes!==64385752||!r||r.decision!=='HOLD'||r.actual_replacements!==0||r.wp_production_writes!==0||r.homepage_visual_changes!==0||r.new_browser_collector!==false||r.downloads!==0||r.subscription_spend_usd!==0)hold('sitewide inflated claim or unauthorized release');
  return {status:'HOLD',matched_slots:2,event_year:1946,conflicting_noaa_media_cards:2,official_virin:portrait.candidate.catalog_virin,guest_failures_confirmed:null,replacements_authorized:0};
}
module.exports={validate};
if(require.main===module){try{console.log(JSON.stringify(validate(JSON.parse(fs.readFileSync(process.argv[2],'utf8'))),null,2))}catch(e){console.error(e.message);process.exitCode=1;}}

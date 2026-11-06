'use strict';
/** Offline fail-closed audit schema for two Three Mile Island media references; no network or WordPress operations. */
function validate(m) {
  const errors=[];
  const bad=(s)=>errors.push(s);
  if(!m||typeof m!=='object'||Array.isArray(m)) return ['audit must be object'];
  if(m.schema!=='fv-tmi-two-priority-recovery-v1') bad('schema');
  if(m.provenance?.post_id!==285||m.provenance?.slot_count!==2) bad('provenance');
  if(m.provenance?.inventory_blob_sha!=='07d5d55f702f66a3807666c62167264aefaf07c6') bad('input SHA');
  if(m.summary?.claimed_broken_legacy!==42||m.summary.confirmed_visitor_broken!==null) bad('42 broken unverified');
  if(m.summary?.measured_transfer_savings_percent!==null||m.summary.proposed_sitewide_transfer_savings_percent!==76) bad('76% unmeasured');
  if(m.summary?.oversized_wp_originals!==13||m.summary?.oversized_original_storage_bytes!==43522829) bad('original storage-only count');
  if(!Array.isArray(m.assets)||m.assets.length!==2) return [...errors,'asset count'];
  const expected={
    '285:5':'https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg',
    '285:2':'https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg'
  };
  if(new Set(m.assets.map(a=>a?.key)).size!==2) bad('duplicate keys');
  for(const a of m.assets){
    if(!a||typeof a!=='object'){bad('bad asset');continue;}
    if(a.post_id!==285||expected[a.key]!==a.existing_src) bad('exact source '+a.key);
    if(a.source_retrieval?.browser_http_status!==null||a.source_retrieval?.origin_http_status!==null) bad('invented origin/browser status '+a.key);
    if(a.source_retrieval?.method!=='web.open') bad('retrieval method '+a.key);
    if(a.key==='285:5'&&a.source_retrieval?.result!=='retriever_404') bad('SayMedia retriever evidence');
    if(a.key==='285:2'&&a.source_retrieval?.result!=='retriever_wrapper_500_after_redirect_to_blog.ucs.org') bad('UCS retriever evidence');
    const c=a.candidate;
    if(!c||typeof c!=='object'){bad('missing candidate');continue;}
    for(const x of ['native_width','native_height','conditional_preview_width','conditional_preview_height']){
      if(!Number.isInteger(c[x])||c[x]<=0) bad('bad dimension '+a.key+':'+x);
    }
    if(c.conditional_preview_width>Math.min(960,c.native_width)||c.conditional_preview_height>c.native_height) bad('upscale or over 960 '+a.key);
    if(Math.abs(c.conditional_preview_width*c.native_height-c.conditional_preview_height*c.native_width)>Math.max(c.native_width,c.native_height)) bad('distorted ratio '+a.key);
    if(c.item_republication_clearance!=='HOLD'||c.same_binary!==false||c.exact_crop_verified!==false) bad('premature binary/rights clearance '+a.key);
    if(!Array.isArray(a.protections)||a.protections.length<2) bad('visual-history protection '+a.key);
  }
  if(m.assets[0]?.key!=='285:5'||m.assets[0]?.candidate?.catalog_url!=='https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg'||m.assets[0]?.candidate?.native_width!==819||m.assets[0]?.candidate?.native_height!==614) bad('plant scene provenance');
  if(m.assets[1]?.key!=='285:2'||m.assets[1]?.candidate?.catalog_url!=='https://commons.wikimedia.org/wiki/File:TMI-2_control_panel.png'||m.assets[1]?.candidate?.native_width!==604||m.assets[1]?.candidate?.native_height!==590) bad('panel provenance');
  for(const field of ['current_src','natural_width','natural_height','network_status','cold_wire_bytes','cache_flags','visitor_broken']) if(m.browser_validation?.[field]!==null) bad('unverified browser '+field);
  if(m.browser_validation?.required!==true||m.browser_validation?.visual_crops_approved!==false) bad('browser gate');
  for(const field of ['wordpress_production_writes','third_party_image_downloads','third_party_image_caches','production_image_fixes','subscription_spend_usd','homepage_design_changes']) if(m.release?.[field]!==0) bad('unapproved action '+field);
  return errors;
}
if(typeof module!=='undefined') module.exports={validate};

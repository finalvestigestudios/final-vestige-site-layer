'use strict';
// Offline-only validation. No HTTP, media download, or WordPress mutation.
function errorsFor(x) {
  const errors=[], bad=m=>errors.push(m);
  const known={
    '285:2':'https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg',
    '285:5':'https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg'
  };
  if(x.schema!=='fv-p0-tmi285-source-alternatives-v1'||x.as_of!=='2026-11-07')bad('schema or date');
  if(x.scope?.fresh_posts_read!==1||x.scope?.image_slots!==2||x.scope?.site_qa_owner!=='PR #154')bad('scope or ownership');
  if(JSON.stringify(x.scope?.p0_other_slots_not_modified)!==JSON.stringify(['287:5','418:1','418:2','407:1']))bad('P0 lane drift');
  const m=x.metrics||{};
  if(m.visitor_confirmed_broken!==0||m.origin_http_observations!==0||m.visitor_image_bytes_measured!==0||m.achieved_savings_percent!==null||m.claimed_42_broken!=='UNVERIFIED'||m.claimed_76pct_saving!=='UNMEASURED'||m.wordpress_writes!==0||m.media_downloads!==0)bad('unsupported measurement or production change');
  if(!Array.isArray(x.slots)||x.slots.length!==2)return [...errors,'must have exactly two slots'];
  const seen=new Set();
  for(const s of x.slots) {
    if(!Object.hasOwn(known,s.slot)||seen.has(s.slot)||s.src!==known[s.slot]||s.post_id!==285||s.wp_modified!=='2026-11-02T21:39:59')bad('published image identity');
    seen.add(s.slot);
    if(!s.article_url?.startsWith('https://finalvestige.com/')||!s.alt||!s.caption)bad('published editorial metadata');
    if(s.browser?.checked!==false||Object.entries(s.browser||{}).some(([k,v])=>k!=='checked'&&v!==null))bad('invented guest-browser evidence');
    const expected=s.slot==='285:2'?500:404;
    if(s.retriever?.method!=='web.run.open'||s.retriever?.tool_reported_status!==expected||!s.retriever?.description?.includes('not origin or visitor status'))bad('wrapper provenance');
    if(s.production_action!=='HOLD'||s.binary_downloaded!==false||s.uploaded_to_wp!==false||s.rights_clearance!=='HOLD')bad('unsafe production gate');
    if(!Array.isArray(s.candidates)||s.candidates.length!==(s.slot==='285:2'?1:2))bad('candidate count');
    for(const c of s.candidates||[]) {
      if(!c.catalog_url?.startsWith('https://commons.wikimedia.org/wiki/File:')||!c.rights_claim||c.rights_review!=='REQUIRED'||c.binary_match_verified!==false||c.rehosting_approved!==false||c.editorial_swap_approved!==false)bad('provenance or rights gate');
      if(!c.historical_integrity_note||!c.proposed_credit||!c.role?.includes('not-'))bad('historical accuracy note');
      const [w,h]=c.master_px||[],[pw,ph]=c.proposed_preview_px||[];
      if(![w,h,pw,ph].every(Number.isSafeInteger)||Math.min(w,h,pw,ph)<=0){bad('invalid image dimensions');continue;}
      const expectedWidth=Math.min(960,w),expectedHeight=Math.round(h*expectedWidth/w);
      if(pw!==expectedWidth||ph!==expectedHeight||pw>w||ph>h||pw>960)bad('upscale, crop or unsafe 960 preview');
    }
  }
  if(seen.size!==2)bad('missing published slot');
  const a=x.slots.find(s=>s.slot==='285:2'),b=x.slots.find(s=>s.slot==='285:5');
  if(a?.candidates?.[0]?.id!=='commission-1979-control-panel'||a?.candidates?.[0]?.master_px?.[0]!==604)bad('commission candidate identity');
  if(b?.candidates?.[0]?.id!=='commons-2010-publisher-photo'||b?.candidates?.[0]?.master_px?.[0]!==819||b?.candidates?.[1]?.id!=='doe-1979-color-aerial'||b?.candidates?.[1]?.master_px?.[0]!==2592)bad('2010 source vs 1979 period-alternative identity');
  return errors;
}
module.exports={errorsFor};
if(typeof require==='function'&&require.main===module) {
  const fs=require('node:fs'),path=require('node:path');
  const data=JSON.parse(fs.readFileSync(process.argv[2]||path.join(__dirname,'p0_tmi285_primary_alternatives_20261107.json'),'utf8'));
  const errors=errorsFor(data);
  if(errors.length){console.error('FAIL:',errors.join('; '));process.exitCode=1;}
  else console.log('PASS: two P0 stored sources; three non-approved catalog candidates; zero fabricated visitor metrics');
}

'use strict';
// Offline validator only. No network, WordPress writes, or binary image downloads.
const EXPECTED = Object.freeze([[274,7],[285,6],[287,6],[418,6],[407,8],[432,7],[34,1],[35,1],[36,1],[37,1],[38,1],[621,6]]);
const P0 = new Set(['274:6','285:2','285:5','287:5','418:1','418:2','407:1']);
const NO_SRCSET = new Map([['34:0',2892087],['38:0',2836245],['35:0',2552136],['36:0',2498247],['37:0',2488823]]);
const FRESH_404 = new Set(['274:6','287:5']);
const isObject = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const int = (x, min=0) => Number.isSafeInteger(x) && x>=min;
function fail(message) { throw new Error(message); }
function decodeAmp(s) { return s.replace(/&#0*38;|&amp;/gi,'&'); }
function secure(s) { try {const u=new URL(s);return typeof s==='string'&&u.protocol==='https:'&&!u.username&&!u.password&&!u.hash;} catch{return false;} }
function unwrapJetpack(url) {
  if(!secure(url))fail('Non-HTTPS/invalid normalized image URL');
  const u=new URL(url);
  if(!/^i[0-3]\.wp\.com$/i.test(u.hostname))return url;
  const m=/^\/([^/]+)(\/.*)$/.exec(u.pathname);
  if(!m || !/^[a-z\d.-]+$/i.test(m[1]) || !m[1].includes('.'))fail('Unsupported Jetpack origin');
  return 'https://'+m[1]+m[2];
}
function validate(snapshot) {
  if(!isObject(snapshot)||snapshot.schema!=='fv-media-wp-view-51-20261118-v1'||snapshot.capture_method!=='WordPress.com posts_get context=view'||!/^2026-11-18T\d\d:\d\d:\d\d-08:00$/.test(snapshot.captured_at)||!Array.isArray(snapshot.posts)||snapshot.posts.length!==12)fail('Invalid snapshot header');
  if(!isObject(snapshot.scope)||snapshot.scope.baseline_posts!==61||snapshot.scope.current_census_posts!==66||snapshot.scope.snapshot_posts!==12||snapshot.scope.snapshot_images!==51||snapshot.scope.reported_42_browser_broken_confirmed!==null||snapshot.scope.claimed_76_percent_wire_savings_verified!==false||snapshot.scope.production_writes!==0)fail('False census or savings assertions');
  if(!isObject(snapshot.probes)||snapshot.probes['274:6']!==404||snapshot.probes['287:5']!==404||Object.keys(snapshot.probes).length!==2)fail('Unverified source-status evidence');
  const counts = new Map(EXPECTED), seen = new Set(); let total=0,priority=0,unsrc=0,results404=0,originalBytes=0;
  for (const p of snapshot.posts) {
    if(!isObject(p)||!counts.has(p.id)||seen.has(p.id)||p.status!=='publish'||!secure(p.post_url)||!/^2026-\d\d-\d\dT/.test(p.modified||'')||!Array.isArray(p.images)||p.images.length!==counts.get(p.id))fail('Post count/revision/source drift');
    seen.add(p.id);
    p.images.forEach((im,i)=>{
      const key=p.id+':'+i;
      if(!isObject(im)||im.slot!==i||im.key!==key||!secure(im.normalized_src)||typeof im.view_src_html!=='string'||decodeAmp(im.view_src_html)!==im.normalized_src||im.origin_url!==unwrapJetpack(im.normalized_src)||!secure(im.origin_url))fail('Invalid source URL or origin identity '+key);
      if(typeof im.has_srcset!=='boolean'||(im.width_attr_px!==null&&!int(im.width_attr_px,1))||(im.height_attr_px!==null&&!int(im.height_attr_px,1)))fail('Invalid authored image dimensions '+key);
      if(im.guest_http_status!==null||im.guest_decoded!==null||im.guest_current_src!==null||im.guest_transfer_bytes!==null||im.raster_width_px!==null||im.raster_height_px!==null||im.raster_sha256!==null)fail('Fabricated Chromium/encoded raster evidence '+key);
      if(im.rehost_approved!==false||im.wp_write_approved!==false||im.rights_status!=='HOLD'||im.max_derivative_width_px!==960||im.allow_upscale!==false||im.derivative_width_px!==null)fail('Unsafe reuse or dimensions '+key);
      if(P0.has(key)){
        if(!isObject(im.candidate)||!secure(im.candidate.catalog_url)||im.candidate.rights_status!=='HOLD'||im.candidate.exact_raster_verified!==false||im.candidate.catalog_checked_in_this_run!==false)fail('Unapproved archival candidate '+key);
        priority++;
      } else if(im.candidate!==null)fail('Unmapped candidate '+key);
      if(NO_SRCSET.has(key)){
        if(im.has_srcset||im.stored_original_bytes!==NO_SRCSET.get(key)||im.width_attr_px!==1024||im.height_attr_px!==576)fail('Oversized inline PNG drift '+key);
        unsrc++;originalBytes+=im.stored_original_bytes;
      } else if(im.stored_original_bytes!==null)fail('Unknown stored-file bytes '+key);
      const status=FRESH_404.has(key)?404:null;
      if(im.source_http_status!==status||im.source_probe_kind!==(status===404?'PUBLIC_RETRIEVER_404':'NOT_CHECKED'))fail('Source status not supported '+key);
      if(status===404){results404++; if(!isObject(im.source_probe)||im.source_probe.url!==im.origin_url||im.source_probe.context!=='independent_web_retriever_not_guest')fail('Unverifiable 404 provenance '+key);}
      else if(im.source_probe!==null)fail('Invented source check '+key);
      total++;
    });
  }
  if(seen.size!==12||total!==51||priority!==7||unsrc!==5||originalBytes!==13267538||results404!==2)fail('Inventory coverage mismatch');
  return {status:'HOLD_GUEST_BROWSER_AND_RIGHTS',posts:12,images:total,priority_slots:priority,new_origin_404:results404,unresponsive_png_slots:unsrc,stored_original_bytes_not_wire:originalBytes,confirmed_guest_broken:null,verified_wire_savings_76_percent:false,wordpress_writes:0};
}
module.exports={EXPECTED,P0,NO_SRCSET,FRESH_404,decodeAmp,unwrapJetpack,validate};
if(require.main===module){
  try { if(process.argv.length!==3)fail('Usage: node fv_wp_view_51_20261118.cjs ledger.json');
    const fs=require('node:fs'); const result=validate(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));console.log(JSON.stringify(result,null,2)); }
  catch(e) {console.error('HOLD: '+e.message);process.exitCode=1;}
}

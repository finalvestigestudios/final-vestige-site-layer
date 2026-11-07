'use strict';
// Read-only, offline, immutable-source audit validator. Not a network or browser image checker.
const fs = require('node:fs');
const path = require('node:path');
const EXPECTED = Object.freeze({
 '418:0':['www.history.uscg.mil','Scotch-Cap-lighthouse-1200x984.jpg',600,480],
 '418:1':['media.defense.gov','210330-G-DE713-0002.JPG',null,null],
 '418:2':['www.history.uscg.mil','5_%20Scotch_Cap_debris2_1946.jpg',600,463],
 '418:3':['www.history.uscg.mil','6_%20Scotch%20Cap%20remains.jpg',600,474],
 '418:4':['www.hawaiimagazine.com','Tsunami1946NOAA2.jpg',null,null],
 '418:5':['d9-wret.s3.us-west-2.amazonaws.com','19460401_UNKNOWN_37-012_copy.jpg?itok=ASMRCahz',null,null]
});
const CATALOGS = Object.freeze({
 '418:0':'www.history.uscg.mil','418:1':'www.history.uscg.mil',
 '418:2':'nationalcoastguardmuseum.org','418:3':'nationalcoastguardmuseum.org',
 '418:4':'prod-01-alb-www-noaa.woc.noaa.gov','418:5':'www.usgs.gov'
});
function validate(d) {
 const e = []; const fail = s => e.push(s);
 if(!d || typeof d!=='object')return ['audit object required'];
 if(d.schema!=='fv.media_recovery.scotch_418.v1'||d.post?.id!==418||d.post?.image_count!==6||d.post?.wp_modified!=='2026-08-28T03:11:08')fail('post provenance mismatch');
 const b=d.baseline||{};
 if(b.posts!==61||b.stored_image_refs!==355||b.external_media_recovery!==288||b.external_site_qa!==286)fail('historical cohorts conflated');
 const m=d.metrics||{};
 if(m.reported_broken!==42||m.confirmed_broken!==null||m.proposed_reduction_pct!==76||m.measured_reduction_pct!==null||m.oversized_original_count!==13||m.oversized_original_storage_bytes!==43522829||m.storage_is_network_wire!==false)fail('invented failure/performance metrics');
 if(d.site_qa_owner!=='PR #154 owns Chrome/CDP probe'||d.guest_browser_verified!==false)fail('duplicate/invented browser probe');
 if(d.production_repairs!==0||d.downloaded_third_party_images!==0||d.wordpress_writes!==0||d.homepage_changes!==0||d.subscription_cost_usd!==0)fail('unsafe production/write/spend');
 if(!Array.isArray(d.items)||d.items.length!==6)return [...e,'six source images required'];
 const seen=new Set();
 for(const r of d.items) {
  const key=r?.slot;
  if(!Object.prototype.hasOwnProperty.call(EXPECTED,key)||seen.has(key)){fail('invalid/repeated slot '+key);continue;}
  seen.add(key);
  const [host,suffix,w,h]=EXPECTED[key];
  if(typeof r.published_img_src!=='string'||!r.published_img_src.startsWith('https://'+host+'/')||!r.published_img_src.endsWith(suffix)||r.source_host!==host)fail(key+' source URL/host changed');
  if(typeof r.published_alt!=='string'||r.published_alt.length<30||typeof r.published_caption!=='string'||r.published_caption.length<20)fail(key+' lost caption/ALT');
  if(typeof r.authoritative_catalog_url!=='string'||!r.authoritative_catalog_url.startsWith('https://'+CATALOGS[key]+'/'))fail(key+' unsupported catalog');
  if(typeof r.catalog_subject_note!=='string'||r.catalog_subject_note.length<35||typeof r.viewer_observation!=='string'||r.viewer_observation.length<20)fail(key+' lost evidence note');
  if(r.source_html_dimensions!==null||r.verified_original_binary_pixels!==null||r.proposed_derivative_pixels!==null)fail(key+' unverified output geometry');
  if(r.guest_http_status!==null||r.guest_decode_success!==null||r.guest_current_src!==null||r.guest_transfer_bytes!==null||r.confirmed_broken_in_browser!==false)fail(key+' invented guest HTTP/decode result');
  if(r.max_width_px!==960||r.no_upscale!==true||r.candidate_preview_not_verified_as_original!==true)fail(key+' unsafe sizing/identity');
  if(r.rights_status!=='HOLD_ITEM_LEVEL_REVIEW'||r.wordpress_upload_authorized!==false||r.third_party_cache_authorized!==false)fail(key+' premature rights or caching clearance');
  if(r.priority!==(key==='418:1'||key==='418:2'?'P0':'P1'))fail(key+' priority drift');
  if(w!==null) {
   if(!r.candidate_preview_url?.startsWith('https://nationalcoastguardmuseum.org/wp-content/uploads/')||r.candidate_preview_pixels?.width!==w||r.candidate_preview_pixels?.height!==h)fail(key+' museum rendition dimensions/URL wrong');
  }else if(r.candidate_preview_url!==null||r.candidate_preview_pixels!==null)fail(key+' invented alternative dimensions');
  if(typeof r.rights_note!=='string'||r.rights_note.length<55)fail(key+' missing rights discussion');
  if(key==='418:1'&&(!r.catalog_subject_note.includes('Pettit')||!r.catalog_subject_note.includes('Petit')))fail(key+' protect contradictory spelling');
  if(key==='418:5'&&!r.rights_note.includes('unknown'))fail(key+' protect unknown photographer');
  if(key==='418:4'&&!r.catalog_subject_note.includes('man on'))fail(key+' protect NOAA pier detail');
 }
 if(seen.size!==6)fail('incomplete slot coverage');
 return e;
}
if(require.main===module){
 const input=process.argv[2]||path.join(__dirname,'scotch_cap_418_six_archive_cursors_20261107.json');
 const e=validate(JSON.parse(fs.readFileSync(input,'utf8')));
 if(e.length){process.stderr.write(e.join('\n')+'\n');process.exitCode=1;}
 else process.stdout.write('PASS: six exact image sources; guest status and rights HOLD\n');
}
module.exports={validate};

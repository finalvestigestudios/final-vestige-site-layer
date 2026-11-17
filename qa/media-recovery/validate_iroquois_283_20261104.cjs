'use strict';
/* Read-only release gate for historical media, Iroquois post 283 (2026-11-04).
 * Node entrypoint checks the pinned Git blob; function is pure for V8 regression replay.
 * No HTTP, no image downloads, no WordPress calls and no writes except console output. */
const PINNED_PART_SHA = '49183f66f880f7c4dfd363acca906876877f2e5e';
const EXPECTED_KEYS = Array.from({length:7},(_,i)=>'283:'+i);
function validate(ledger,part) {
  const err=[];
  const req=(test,message)=>{ if(!test) err.push(message); };
  if(!ledger || !part || !Array.isArray(ledger.image_rows) || !Array.isArray(part.images))
    return {ok:false,errors:['missing ledger, part, or image rows']};
  const source=part.images.filter(x=>x.post_id===283);
  req(part.image_count===part.images.length,'part image_count mismatch');
  req(source.length===7,'frozen post 283 must contain exactly 7 images');
  req(ledger.source?.git_blob_sha===PINNED_PART_SHA,'frozen Git blob must be pinned');
  req(ledger.source?.path==='qa/media-recovery/parts/03.json','frozen source path drift');
  req(ledger.source?.reference_posts===61 && ledger.source?.reference_images===355 && ledger.source?.offsite_origin_refs===288,'site census drift');
  req(ledger.source?.oversized_wp_originals===13,'original image storage baseline drift');
  req(ledger.cms?.status==='publish' && ledger.cms?.id===283,'CMS post/status drift');
  req(ledger.cms?.img_tags===7 && ledger.cms?.matching_source_url===7 && ledger.cms?.matching_alt===7,'live CMS identity count drift');
  req(ledger.cms?.with_width_and_height===0,'known missing dimension finding drift');
  req(ledger.image_rows.length===7,'ledger length drift');
  const gotKeys=new Set();
  for(let i=0;i<ledger.image_rows.length;i++) {
    const a=ledger.image_rows[i], b=source[i];
    req(a?.key===EXPECTED_KEYS[i] && a?.key===b?.key,'wrong image slot '+i);
    req(!gotKeys.has(a?.key),'duplicate key '+i);gotKeys.add(a?.key);
    req(a?.original_url===b?.source_url,'original URL drift '+i);
    req(a?.original_alt===b?.alt,'original ALT drift '+i);
    req(a?.source_host===b?.source_host,'original host drift '+i);
    req(a?.published_html_width_px===null && a?.published_html_height_px===null,'invented HTML dimensions '+i);
    const t=a?.retrieval||{};
    req(t.method==='web.open image display (not a browser network trace)','misrepresented transport '+i);
    req(t.result===(i===3?'INACCESSIBLE':'DISPLAYED'),'retrieval display evidence drift '+i);
    req(t.origin_http_code===null && t.guest_browser_http_code===null &&
        t.guest_mime_type===null && t.guest_natural_dimensions===null &&
        t.guest_decode_success===null && t.cdp_encoded_bytes===null,'invented guest/origin/wire measurement '+i);
    const rights=a?.rights||{};
    req(rights.republication_status==='HOLD_FOR_ITEM_REVIEW' &&
        rights.approved_license===null && rights.allow_download_for_cache===false &&
        rights.allow_wp_upload===false && rights.allow_post_rewrite===false,'unauthorized media copying/edit '+i);
    req(a?.resize?.max_width_px===960 && a?.resize?.no_upscale===true &&
        a?.resize?.verified_original_width_px===null && a?.resize?.verified_original_height_px===null,'invalid source geometry '+i);
    req(typeof a?.visual?.evidence==='string' && a.visual.evidence.length>30,'no visual source basis '+i);
    req(/^https:\/\//.test(a?.provenance?.archive_url??'') && a.provenance.original_binary_sha256===null,'invalid archive proof '+i);
  }
  req(ledger.image_rows[0]?.visual?.finding==='MODERN_ANNOTATED_COMPOSITE_NOT_HISTORIC_PHOTOGRAPH','lost modern-composite integrity warning');
  req(ledger.image_rows[2]?.visual?.finding==='HISTORICAL_CAPTION_TIMING_CONFLICT','lost foyer chronology warning');
  req(ledger.image_rows[6]?.visual?.finding==='POST_FIRE_SCENE_TIMING_UNPROVEN','lost exterior chronology warning');
  const r=ledger.results||{};
  req(r.original_urls_displayed_in_independent_renderer===6 && r.original_urls_inaccessible_to_renderer===1,'tool display census drift');
  req(r.confirmed_guest_browser_broken===0 && r.confirmed_origin_http_status===0 && r.production_fixes===0,'unsupported remediation/status claim');
  req(r.claimed_broken_42==='UNVERIFIED' && r.claimed_savings_76_percent==='UNMEASURED','unverified global claims');
  const cand=ledger.primary_or_archival_candidates;
  req(Array.isArray(cand) && cand.length===3,'archive candidate list drift');
  const geometry={'283:0':[4118,5221,960,1217],'283:2':[1920,1192,960,596],'283:5':[1181,888,960,722]};
  for(const c of cand||[]) {
    const g=geometry[c.key];
    req(!!g,'unexpected archival candidate '+c.key);
    if(!g) continue;
    req(c.intrinsic_px?.[0]===g[0] && c.intrinsic_px?.[1]===g[1],'master geometry drift '+c.key);
    req(c.target_px?.[0]===g[2] && c.target_px?.[1]===g[3],'no-upscale geometry drift '+c.key);
    req(c.target_px[0]<=c.intrinsic_px[0] && Math.abs(c.target_px[1]-Math.round(c.intrinsic_px[1]*c.target_px[0]/c.intrinsic_px[0]))<=1,'upsampling/aspect mismatch '+c.key);
    req(typeof c.rights_signal==='string' && c.rights_signal.length>15,'rights review missing '+c.key);
    req(c.same_original!==true,'unverified binary identity was approved '+c.key);
  }
  req(ledger.release_plan?.includes('Site QA #154') && ledger.release_plan?.includes('approval'), 'release controls incomplete');
  return {ok:err.length===0,errors:err};
}
module.exports={validate,PINNED_PART_SHA};
if(require.main===module) {
  const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
  const root=path.resolve(__dirname,'../..');
  const partPath=path.join(root,'qa/media-recovery/parts/03.json');
  const bytes=fs.readFileSync(partPath);
  const actual=crypto.createHash('sha1').update('blob '+bytes.length+'\0').update(bytes).digest('hex');
  if(actual!==PINNED_PART_SHA){console.error('Frozen source Git blob mismatch',actual);process.exitCode=1;}
  else {
    const ledger=JSON.parse(fs.readFileSync(path.join(__dirname,'iroquois_283_visual_custody_20261104.json'),'utf8'));
    const out=validate(ledger,JSON.parse(bytes.toString('utf8')));
    console.log(JSON.stringify(out));
    if(!out.ok)process.exitCode=1;
  }
}

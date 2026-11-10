'use strict';
// Frozen source identity came from PR #183 Oct 30 fixture parts/05.json (Git blob 9b16b828342a9ac338f3e65610fd3d8d508355e9).
// Read-only; never HTTP fetches, downloads images, caches, edits WordPress or publishes.
const SOURCE_NAMES = [
 'SL1nuclearpowerplant.JPG',
 'SL-1_-_Cutaway_of_reactor_and_control_building.png',
 'SL-1_-_Reactor_schematic.png',
 'US_AEC_SL-1.JPG',
 'Sl-1-ineel81-3966.jpg',
 'Sl-1-ineel61-9.jpg',
 'SL-1_-_Dismantling_of_the_foundation_piers.jpg'
];
const ORIGINAL_ALTS = [
 'SL-1 nuclear reactor building at the National Reactor Testing Station in Idaho.',
 'Cutaway diagram of the SL-1 reactor and control building showing the reactor vessel and operating floor.',
 'SL-1 reactor schematic showing the core, pressure vessel and control-rod arrangement.',
 'Atomic Energy Commission crews removing the damaged SL-1 reactor core from the Idaho facility after the 1961 accident.',
 'Retrospective photograph showing severe damage inside the SL-1 reactor core after the 1961 prompt-critical excursion.',
 'Health physicists checking U.S. Highway 20 for radioactive contamination on the morning after the SL-1 accident.',
 'Workers dismantling the SL-1 reactor foundation piers during later cleanup of the Idaho site.'
];
const PIXELS = [[704,346],[729,589],[1454,1753],[346,253],[1406,1881],[1436,1113],[1402,1050]];
const NULL_PROOF = ['origin_http_status','guest_browser_http_status','guest_current_src','guest_natural_size','guest_transfer_bytes','guest_broken'];
const FALSE_GATES = ['exact_binary_match_verified','item_rights_cleared','cached_copy_authorized','wordpress_media_upload_authorized','post_block_change_authorized'];
function fail(s) { throw new Error(s); }
function validate(a) {
 if (!a || a.schema !== 'fv-media-sl1-221-seven-v1' || a.post_id !== 221) fail('audit schema/post changed');
 if (a.frozen_source?.blob_sha !== '9b16b828342a9ac338f3e65610fd3d8d508355e9') fail('fixture identity changed');
 if (!Array.isArray(a.rows) || a.rows.length !== 7) fail('exactly 7 source rows required');
 const postUrl='https://finalvestige.com/2026/08/18/the-rod-was-supposed-to-move-four-inches/';
 a.rows.forEach((r,i) => {
   const name = SOURCE_NAMES[i], original = PIXELS[i], [w,h] = original;
   const computed = [Math.min(w,960), Math.round(h*Math.min(w,960)/w)];
   if (r.slot !== '221:'+i || r.post_id !== 221 || r.published_url !== postUrl) fail('source slot/post mismatch '+i);
   if (r.original_stored_src !== 'https://commons.wikimedia.org/wiki/Special:Redirect/file/'+name) fail('original URL mismatch '+i);
   if (r.original_alt !== ORIGINAL_ALTS[i]) fail('frozen ALT mismatch '+i);
   if (r.catalog_url !== 'https://commons.wikimedia.org/wiki/File:'+name) fail('wrong source candidate '+i);
   if (r.catalog_retriever !== 'HTML_ACCESSIBLE_2026-11-10' || r.original_redirect_retriever !== 'TOOL_INACCESSIBLE_NOT_HTTP') fail('retriever provenance mismatch '+i);
   if (JSON.stringify(r.catalog_original_px) !== JSON.stringify(original) || JSON.stringify(r.conditional_max_width_960_px) !== JSON.stringify(computed)) fail('no upscale and correct aspect ratio required '+i);
   for(const key of NULL_PROOF) if(r[key] !== null) fail('unearned browser/origin claim '+i+':'+key);
   for(const key of FALSE_GATES) if(r[key] !== false) fail('unauthorized release '+i+':'+key);
   if (!r.rights_observation || !r.description || !r.historical_integrity) fail('rights/history evidence missing '+i);
 });
 if(!/1981/.test(a.rows[4].historical_integrity) || !/1961/.test(a.rows[4].historical_integrity)) fail('poster chronology not documented');
 if(!/67-2587/.test(a.rows[6].historical_integrity) || !/81-3966/.test(a.rows[6].historical_integrity)) fail('conflicting accession not documented');
 return {validated:7, catalog_only:7, confirmed_guest_broken:0, release_authorized:0};
}
if (require.main === module) {
 const fs=require('node:fs'); const path=require('node:path');
 const audit=JSON.parse(fs.readFileSync(path.join(__dirname,'sl1_221_seven_inl_primary_20261110.json'),'utf8'));
 process.stdout.write(JSON.stringify(validate(audit))+'\\n');
}
module.exports = { validate, SOURCE_NAMES, ORIGINAL_ALTS, PIXELS };

'use strict';
// Standalone offline tests, no third-party requests and no WordPress writes.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_skyway_287_p0_20261103.cjs');
const a=JSON.parse(fs.readFileSync(path.join(__dirname,'skyway_287_p0_migration_20261103.json'),'utf8'));
const s={posts:[{id:287,url:a.article.url}],images:a.published_images.map(x=>({post_id:287,key:x.key,source_url:x.published_src,alt:x.published_alt,width_px:x.cms_width_px,height_px:x.cms_height_px}))};
let n=0;
function check(label, mutateAudit, mutateSource, expected=false) {
 const x=structuredClone(a), y=structuredClone(s);
 if(mutateAudit)mutateAudit(x);
 if(mutateSource)mutateSource(y);
 const actual=validate(x,y);
 assert.equal(actual.ok,expected,label+': '+actual.errors.join(','));
 n++;
}
check('valid source-level evidence still HOLD',null,null,true);
const cases=[
 ['fake guest 404',x=>x.published_images[5].visitor_browser.http_status=404],
 ['fake guest image MIME',x=>x.published_images[5].visitor_browser.response_mime='image/jpeg'],
 ['fake decoded width',x=>x.published_images[5].visitor_browser.natural_width_px=1000],
 ['fake transfer bytes',x=>x.published_images[5].visitor_browser.encoded_image_bytes=200000],
 ['fake guest currentSrc',x=>x.published_images[5].visitor_browser.current_src=x.migration_candidate.new_url],
 ['claim visitor broken',x=>x.site_metrics.confirmed_visitor_image_failures=1],
 ['claim 42 proven',x=>x.site_metrics.claimed_broken_42_guest_verified=true],
 ['claim 76% measured',x=>x.site_metrics.claimed_76_percent_wire_reduction_measured=true],
 ['claim fixed production',x=>x.site_metrics.production_images_repaired=1],
 ['pretend original displays',x=>x.published_images[5].viewer_result='DISPLAYED'],
 ['hide original retriever 404',x=>x.published_images[5].retriever_wrapper_status=null],
 ['rewrite original src',x=>x.published_images[5].published_src=x.migration_candidate.new_url],
 ['rewrite candidate src',x=>x.migration_candidate.new_url+='?copy=1'],
 ['pretend license approved',x=>x.migration_candidate.rights_permission_verified=true],
 ['pretend rehost approved',x=>x.migration_candidate.wp_rehost_authorized=true],
 ['pretend post URL change approved',x=>x.migration_candidate.wp_url_change_authorized=true],
 ['invent source width',x=>x.migration_candidate.original_width_px=1000],
 ['invent derivative height',x=>x.migration_candidate.conditional_height_px=650],
 ['upscale width',x=>x.migration_candidate.maximum_no_upscale_width_px=1280],
 ['claim binary equivalence',x=>x.migration_candidate.binary_identical_verified=true],
 ['claim different scene is exact',x=>x.authoritative_archival_context_not_exact_replacements[0].same_scene=true],
 ['claim Florida Memory reuse licensed',x=>x.authoritative_archival_context_not_exact_replacements[1].publishing_rights_verified=true],
 ['rewrite ALT to hide old bridge',x=>x.migration_candidate.alt_correction_proposed_not_published='The 1987 new replacement bridge'],
 ['permit media download',x=>x.controls.no_image_download=false],
 ['permit WordPress edit',x=>x.controls.no_wordpress_write=false],
 ['permit homepage change',x=>x.controls.no_homepage_design_change=false],
 ['wrong part blob',x=>x.archived_inventory.git_blob_sha='0000000000000000000000000000000000000000'],
 ['drop post image',x=>x.published_images.pop()],
 ['duplicate image key',x=>x.published_images[5].key='287:4'],
 ['change unflagged viewer result',x=>x.published_images[4].viewer_result='RETRIEVER_403'],
 ['change cms dimensions',x=>x.published_images[0].cms_width_px=960],
 ['change source ALT',x=>x.published_images[1].published_alt='ship'],
];
for(const [label,fn] of cases)check(label,fn);
check('archive src drift',null,y=>y.images[5].source_url+='?moved=1');
check('archive ALT drift',null,y=>y.images[1].alt='fake');
check('archive article removal',null,y=>y.posts=[]);
console.log(n+'/'+n+' Skyway P0 source migration checks PASS (offline only)');

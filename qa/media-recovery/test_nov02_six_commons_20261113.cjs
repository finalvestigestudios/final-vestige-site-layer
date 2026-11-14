'use strict';
/** Native Node test definitions: read-only source/rights/guest evidence adversarial gates. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validateAudit}=require('./validate_nov02_six_commons_20261113.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'wp_nov02_five_post_six_commons_20261113.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(original));
test('unchanged six-image published-source audit passes',()=>assert.deepEqual(validateAudit(original),{ok:true,errors:[]}));
const changes=[
 ['invented visitor success',x=>x.images[0].visitor_http_status=200],
 ['invented visitor failure',x=>x.images[0].visitor_http_status=404],
 ['invented decoded pixels',x=>x.images[1].visitor_pixels=[1280,601]],
 ['invented visitor bytes',x=>x.images[2].visitor_encoded_transfer_bytes=10000],
 ['invented visitor currentSrc',x=>x.images[3].visitor_current_src='https://example.org/replaced.jpg'],
 ['invented rendered CSS width',x=>x.images[4].rendered_css_width=400],
 ['invented DPR',x=>x.images[4].dpr=2],
 ['invented binary hash',x=>x.images[5].source_binary_sha256='abc123'],
 ['unlicensed caching assertion',x=>x.images[1].third_party_cache_approved=true],
 ['unauthorized WP media approval',x=>x.images[2].wordpress_media_write_approved=true],
 ['unauthorized rehost approval',x=>x.images[3].rights_rehosting_approved=true],
 ['unauthorized derivative approval',x=>x.images[4].derivative_approved=true],
 ['changed historical source photo URL',x=>x.images[0].published_src='https://commons.wikimedia.org/wiki/Special:Redirect/file/Wrong.jpg?width=1280'],
 ['changed published source photo to another file',x=>x.images[1].published_src=x.images[0].published_src],
 ['wrong catalog file',x=>x.images[2].official_catalog_url=x.images[3].official_catalog_url],
 ['wrong Commons license classification',x=>x.images[3].catalog_license='PUBLIC_DOMAIN_MARK_1_0'],
 ['changed catalog original pixel width',x=>x.images[3].catalog_original_px[0]=900],
 ['invented 960 derivative to 1280',x=>x.images[0].conditional_max_derivative_px[0]=1280],
 ['falsely asserted HTML width present',x=>x.images[0].html_width_attr=1280],
 ['falsely asserted HTML height present',x=>x.images[0].html_height_attr=600],
 ['deleted caption credit',x=>x.images[2].published_figcaption='Beautiful ancient Roman vase'],
 ['erased alt description',x=>x.images[5].published_alt='skull'],
 ['silently changed source type',x=>x.images[0].origin_type='LOCAL_WORDPRESS'],
 ['silently moved post URL',x=>x.posts[0].url='https://finalvestige.com/2026/11/02/wrong/'],
 ['draft substituted for published post',x=>x.posts[0].status='draft'],
 ['zero-image post made to have one image',x=>x.posts[2].inline_image_count=1],
 ['new post removed from cohort',x=>x.posts.pop()],
 ['sixth image removed',x=>x.images.pop()],
 ['duplicate image slot',x=>x.images[5].slot=x.images[0].slot],
 ['added extra unrecognized root claim',x=>x.sitewide_transfer_verified=true],
 ['frozen cohort conflated with new posts',x=>x.historical.post_count=66],
 ['unverified 42 treated as confirmed',x=>x.historical.guest_confirmed_broken=42],
 ['fake 76 percent measured',x=>x.historical.measured_wire_reduction_pct=76],
 ['expanded offsite 294 count forged',x=>x.live.expanded_same_method_offsite_count=299],
 ['added source is falsely called first party',x=>x.live.new_commons_external_images=0],
 ['removed no-upscale policy',x=>x.release.no_upscale=false],
 ['removed map-legibility safeguard',x=>x.release.keep_map_zoom_and_labels=false],
 ['reassigned Site QA collector',x=>x.release.siteqa_browser_owner_pr=1703],
 ['changed original browser priority',x=>x.release.p0_queue_unchanged.reverse()],
 ['allowed third party cache writes',x=>x.release.third_party_cache_writes=1],
 ['allowed production WordPress writes',x=>x.release.wp_production_writes=1],
 ['allowed homepage work',x=>x.release.homepage_changes=1],
 ['allowed merge',x=>x.release.merges=1],
 ['asserted spend',x=>x.release.subscription_spend_usd=1],
 ['fabricated observation date',x=>x.observed_local_date='2026-11-14'],
 ['fabricated original visitor transfer',x=>x.images[0].catalog_original_is_visitor_transfer=true]
];
for(const [name,mutate] of changes){
 test('fail closed: '+name,()=>{const x=clone();mutate(x);const r=validateAudit(x);
  assert.equal(r.ok,false,'must refuse invented or changed evidence');
  assert.ok(r.errors.length>0,'must explain rejection');
 });
}
test('source is read only: validator does not mutate input',()=>{
 const x=clone(),before=JSON.stringify(x);validateAudit(x);assert.equal(JSON.stringify(x),before);
});

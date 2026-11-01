'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const ledger=require('./florida_432_primary_20261031.json');
const census=require('./source_viewer_25slot_20261031.json');
const {validateFlorida432}=require('./validate_florida_432.cjs');
function clone(x){return JSON.parse(JSON.stringify(x));}
test('unedited seven-slot ledger is valid, still no published repairs',()=>{
  assert.deepEqual(validateFlorida432(ledger,census),{valid:true,verified_catalog_rows:7,guest_http_statuses:0,production_repairs:0});
});
const changes=[
 ['wrong schema',d=>d.schema_version=2],
 ['scope drift',d=>d.audit_kind='BROWSER_VERIFIED'],
 ['wrong post id',d=>d.article.post_id=433],
 ['source row count drift',d=>d.article.read_only_editor_image_source_and_alt_matches=6],
 ['one source missing',d=>d.images.pop()],
 ['publisher rights policy missing',d=>d.official_rights_policy.mark='CC-BY'],
 ['rights released too soon',d=>d.official_rights_policy.final_editorial_release=true],
 ['source credit removed',d=>d.official_rights_policy.attribution_required=false],
 ['invented 42 failures verified',d=>d.inventory_scope.reported_broken_count_unverified=null],
 ['invented 76 percent',d=>d.inventory_scope.reported_weight_reduction_percent_unverified=74],
 ['wrong archive key',d=>d.images[0].image_key='432:4'],
 ['source URL swapped',d=>d.images[0].stored_source_url=d.images[1].stored_source_url],
 ['ALT changed',d=>d.images[1].stored_alt='Wrong site'],
 ['source identity not checked',d=>d.images[2].cms_src_and_alt_match_frozen_inventory=false],
 ['wrong catalog ID',d=>d.images[3].primary_catalog.identifier='N031899'],
 ['wrong catalog item page',d=>d.images[4].primary_catalog.item_url='https://floridamemory.com/items/show/4144'],
 ['unverified substitute photo path',d=>d.images[4].primary_catalog.catalog_path='/fpc/reference/rc04343.jpg'],
 ['invented canonical photo',d=>d.images[4].primary_catalog.publisher_canonical_image_url='https://floridamemory.com/fpc/reference/rc04343.jpg'],
 ['2001 site photograph relabelled 1928',d=>d.images[6].primary_catalog.date='1928'],
 ['catalog description removed',d=>d.images[1].primary_catalog.title='x'],
 ['mislabelled viewer result',d=>d.images[0].third_party_viewer_observation.result='VIEWER_DECODED'],
 ['fabricated image source response',d=>d.images[0].third_party_viewer_observation.original_image_http_status=200],
 ['invented guest currentSrc',d=>d.images[0].visitor_browser.current_src=d.images[0].stored_source_url],
 ['invented browser HTTP 404',d=>d.images[0].visitor_browser.http_status=404],
 ['invented browser MIME',d=>d.images[1].visitor_browser.mime='image/jpeg'],
 ['invented browser bytes',d=>d.images[2].visitor_browser.encoded_bytes=1234],
 ['invented naturalWidth',d=>d.images[1].visitor_browser.natural_width=600],
 ['unverified SHA',d=>d.images[0].original_binary_sha256='ab'],
 ['unverified original dimensions',d=>d.images[0].original_dimensions_px=[600,400]],
 ['invented 960x output dimension',d=>d.images[0].proposed_derivative.dimensions_px=[960,640]],
 ['overwide derivative plan',d=>d.images[0].proposed_derivative.max_width_px=1200],
 ['upscaling requested',d=>d.images[0].proposed_derivative.upscaling_allowed=true],
 ['aspect-crop requested',d=>d.images[0].proposed_derivative.preserve_aspect_ratio=false],
 ['item rights misrepresented',d=>d.images[0].copyright.individual_reuse_review='CLEARED'],
 ['wrong reuse mark',d=>d.images[0].copyright.source_mark='CC-BY'],
 ['credit omitted',d=>d.images[0].copyright.credit='No credit'],
 ['image downloaded',d=>d.images[0].staging.downloaded=true],
 ['asset fabricated',d=>d.images[0].staging.first_party_asset_created=true],
 ['WordPress media write asserted',d=>d.images[0].staging.wordpress_media_uploaded=true],
 ['article post rewrite asserted',d=>d.images[0].staging.article_rewritten=true],
 ['release authorized without review',d=>d.images[0].staging.approved=true],
 ['fabricated guest broken report',d=>d.images[0].verified_broken_for_visitors=true],
 ['fabricated savings measurement',d=>d.images[0].visitor_weight_savings_bytes=120000]
];
for(const [label,change] of changes){
 test('fail closed: '+label,()=>{
   const bad=clone(ledger);change(bad);
   assert.throws(()=>validateFlorida432(bad,census),/FL432_INVALID:/);
 });
}

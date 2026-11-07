'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {validate}=require('./validate_nasa_apollo1_20261106.cjs');
const fixture=require('./nasa_apollo1_five_20261106.json');
const copy=()=>JSON.parse(JSON.stringify(fixture));
test('NASA Apollo 1 complete manifest passes',()=>assert.deepEqual(validate(copy()),{ok:true,errors:[]}));
const cases=[
 ['false visitor failure',x=>x.images[0].source_retrieval.visitor_broken=true],
 ['invented browser HTTP 404',x=>x.images[0].source_retrieval.browser_http_status=404],
 ['invented browser transfer',x=>x.images[0].source_retrieval.browser_cold_transfer_bytes=123],
 ['invented browser naturalWidth',x=>x.images[0].source_retrieval.browser_natural_width=960],
 ['invented site-wide 76% reduction',x=>x.performance.measured_transfer_savings_percent=76],
 ['pretend source transfer known',x=>x.performance.source_bytes_downloaded=10000],
 ['unsafe first-party recovery',x=>x.first_party_guard.include_in_external_recovery=true],
 ['wrong first party URL',x=>x.first_party_guard.src='https://example.com/image.webp'],
 ['rights approval without review',x=>x.images[0].rights_state='CLEARED'],
 ['automatic localization',x=>x.rights.allowed_automatic_localization=true],
 ['invented image mirror',x=>x.images[1].derivative_asset_url='https://finalvestige.com/media/copy.jpg'],
 ['WP publishing',x=>x.images[0].wordpress_publish_approved=true],
 ['fake file download',x=>x.release.asset_downloads=1],
 ['production edit',x=>x.release.wordPress_writes=1],
 ['unlicensed cache',x=>x.release.third_party_caches=1],
 ['incorrect NASA ID',x=>x.images[0].nasa_id='S67-15718'],
 ['wrong NASA path',x=>x.images[0].stored_src=x.images[0].stored_src.replace('~large','~orig')],
 ['fake NASA catalog',x=>x.images[0].nasa_catalog_url='https://example.net/image-detail/'],
 ['duplicate NASA image',x=>x.images[1]=JSON.parse(JSON.stringify(x.images[0]))],
 ['unsafe 961px preview',x=>x.images[1].conditional_preview_dimensions=[961,773]],
 ['wrong aspect ratio',x=>x.images[2].conditional_preview_dimensions=[960,641]],
 ['upsizing geometry',x=>x.images[3].publisher_metadata_native_dimensions=[300,300]],
 ['HTML catalog geometry mismatch',x=>x.images[1].stored_html_dimensions=[10,10]],
 ['missing historical caption credit',x=>x.images[4].caption_credit='Photographer unknown'],
 ['inferred browser success',x=>x.images[1].source_retrieval.stored_image_web_retriever='200'],
 ['alter reported broken count',x=>x.performance.alleged_broken=0],
 ['alter published cohort',x=>x.performance.current_post_cohort=61],
 ['alter original oversize inventory',x=>x.performance.oversize_storage_bytes=0],
 ['set homepage edits',x=>x.release.homepage_design_changes=1],
 ['set subscription spend',x=>x.release.subscription_spend_usd=1],
 ['missing article read method',x=>delete x.article.read_method],
 ['null image object',x=>x.images[0]=null],
 ['missing catalog geometry',x=>delete x.images[0].publisher_metadata_native_dimensions]
];
for(const [name,mutation] of cases)test('reject: '+name,()=>{const x=copy();mutation(x);assert.equal(validate(x).ok,false);});

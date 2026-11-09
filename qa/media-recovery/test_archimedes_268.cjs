'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {validate}=require('./validate_archimedes_268.cjs');
const fs=require('node:fs');
const seed=JSON.parse(fs.readFileSync(__dirname+'/archimedes_268_ten_sources_20261108.json','utf8'));
const clone=()=>JSON.parse(JSON.stringify(seed));
test('frozen original audit validates',()=>assert.equal(validate(clone()).ok,true));
const mutations=[
 ['invent guest browser 404',a=>a.rows[0].retriever.guest_browser_http_status=404],
 ['fabricate 42 verified',a=>a.conclusions.reported_42_guest_verified=true],
 ['fabricate 76 percent',a=>a.conclusions.reported_76_percent_wire_reduction_verified=true],
 ['falsely grant rehost right',a=>a.rows[2].candidate.cache_or_rehost_authorized=true],
 ['falsely grant edit permission',a=>a.rows[3].actions.wordpress_post_change=true],
 ['substitute manuscript folio',a=>a.rows[5].candidate.catalog_url='https://commons.wikimedia.org/wiki/File:Wrong.jpg'],
 ['swap published source URLs',a=>[a.rows[2].source_url,a.rows[3].source_url]=[a.rows[3].source_url,a.rows[2].source_url]],
 ['claim 960 px for 665px original',a=>a.rows[0].candidate.conditional_max960_dimensions=[960,647]],
 ['reshape long folio incorrectly',a=>a.rows[9].candidate.conditional_max960_dimensions=[960,960]],
 ['overwrite native dimensions',a=>a.rows[6].candidate.catalog_native_dimensions=[900,900]],
 ['overstate rights for project JPEG',a=>a.rows[1].candidate.rights_status='PUBLIC_DOMAIN'],
 ['promote tool 403 to HTTP 403',a=>a.rows[1].retriever.origin_http_status=403],
 ['treat tool inaccessibility as visitor broken',a=>a.rows[8].retriever.visitor_broken=true],
 ['add unauthorized caching switch',a=>a.rows[1].actions.http_cache=true],
 ['add unverified publication proof field',a=>a.rows[4].candidate.published_now=true],
 ['invent binary content hash',a=>a.rows[0].candidate.binary_sha256='abc'],
 ['alter alt historical description',a=>a.rows[8].source_alt='Invented history'],
 ['alter source snapshot hash',a=>a.source.blob_sha='0'.repeat(40)],
 ['add false root performance claim',a=>a.sitewide_savings_percent=76],
 ['duplicate item',a=>a.rows[9]=a.rows[8]],
 ['truncate item inventory',a=>a.rows.pop()],
 ['force WordPress write conclusion',a=>a.conclusions.wordpress_writes=1],
 ['invent measured wire bytes',a=>a.rows[5].retriever.uncached_transfer_bytes=100],
 ['release non-960 approved dimensions',a=>a.rows[2].candidate.conditional_max960_dimensions=[1280,960]],
 ['misstate tool status',a=>a.rows[1].retriever.result='HTTP_403'],
 ['misstate author/license',a=>a.rows[3].candidate.rights_status='COMMONS_PD_US_CLAIM']
];
for(const [name,mut] of mutations)test(name,()=>{const a=clone();mut(a);assert.equal(validate(a).ok,false,name)});

// Historical provenance text is evidence, not free-form editable approval metadata.
for(const [name,mut] of [
 ['grant rights by prose',a=>a.rows[2].candidate.rights_notes='PUBLIC DOMAIN APPROVED'],
 ['promote candidate to exact pixel',a=>a.rows[3].candidate.relationship='EXACT_IMAGE_CONFIRMED'],
 ['change project license context',a=>a.catalog_context.research_license='All project JPEGs public domain'],
 ['add misleading 76-percentage to conclusions',a=>a.conclusions.measured_76_percent=true],
 ['alter original WordPress snapshot post URL',a=>a.rows[4].post_url='https://finalvestige.com/fake/'],
 ['alter reference to frozen Oct 30 source',a=>a.rows[0].source_snapshot_ref='future_wp_snapshot.json']
]) test(name,()=>{const x=clone();mut(x);assert.equal(validate(x).ok,false,name)});

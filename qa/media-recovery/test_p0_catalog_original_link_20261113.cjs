'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {audit}=require('./validate_p0_catalog_original_link_20261113.cjs');
const file=path.join(__dirname,'p0_catalog_original_link_custody_20261113.json');
const original=JSON.parse(fs.readFileSync(file,'utf8'));
const clone=()=>structuredClone(original);
function mutation(label,modify,expected){
 test(label,()=>{const d=clone();modify(d);const r=audit(d);
  assert.equal(r.pass,false);assert(r.errors.some(x=>x.includes(expected)),JSON.stringify(r.errors));});
}
test('6 true sources, 1 exact official catalog original, 0 real guest failures',()=>{
 const r=audit(original);assert.equal(r.pass,true,JSON.stringify(r.errors));
 assert.deepEqual([r.rows,r.direct_official_original_link_matches,r.confirmed_browser_broken,r.production_write_allowed],[6,1,0,false]);
});
mutation('source slot tampering fails',x=>x.rows[5].original+='?test','published_source_407:1');
mutation('wrapper 400 cannot become real guest status',x=>x.rows[5].guest_http_status=400,'no_guest_or_rights_claim_407:1');
mutation('42 must remain unconfirmed',x=>x.reported_broken_originals_unconfirmed=0,'broken_unconfirmed');
mutation('76% transferred saving cannot be measured by storage metadata',x=>x.proposed_transfer_reduction_76pct_measured=true,'76pct_not_measured');
mutation('stored original bytes are exact',x=>x.oversized_original_stored_bytes=100,'stored_original_bytes');
mutation('third-party caching cannot be authorized',x=>x.local_caching_authorized=true,'write_or_network_claim');
mutation('WordPress writes cannot be authorized',x=>x.wordpress_changes_authorized=true,'write_or_network_claim');
mutation('native dimensions cannot be invented',x=>x.rows[5].source_native_dimensions_px=[960,720],'no_invented_pixels_407:1');
mutation('cannot relax 960px ceiling',x=>x.conditional_derivative_max_width_px=1920,'width_limit');
mutation('Skyway moved photo not official exact original',x=>x.rows[2].catalog_original_same_url=true,'exact_official_link_287:5');
mutation('USGS original URL must be the published original',x=>x.rows[5].catalog_original_link='https://example.org/x.jpg','usgs_original_link');
mutation('USGS medium URL must remain exact',x=>x.rows[5].catalog_medium_link='https://example.org/medium.jpg','usgs_medium_link');
mutation('public-domain listing is not self-authorizing upload',x=>x.rows[5].item_rights_for_rehosting_verified=true,'no_guest_or_rights_claim_407:1');
mutation('web retriever 403 cannot be rewritten as actual 404',x=>x.rows[3].retriever_code=404,'wrapper_only_418:1');
mutation('catalog does not prove binary pixels identical',x=>x.rows[5].candidate_scene='BINARIES_IDENTICAL','no_binary_identity_claim');
mutation('source slots cannot be reordered',x=>x.rows.reverse(),'slot_0');

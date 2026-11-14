'use strict';
/** Frozen-source integrity: no HTTP/WordPress/network writes. */
const assert=require('node:assert/strict');
const {validate}=require('./validate_wp_123_media_16_draft_20261113.cjs');
const baseline=require('./wp_123_media_16_draft_20261113.json');
const copy=()=>JSON.parse(JSON.stringify(baseline));
const reject=(label,modify)=>{const x=copy();modify(x);assert.equal(validate(x).ok,false,label)};
assert.equal(validate(copy()).ok,true,'unmodified frozen WP ledger');
for(let i=0;i<baseline.oversized_media.length;i++){
 reject('same-host substituted image '+i,x=>{x.oversized_media[i].source_url='https://finalvestige.com/wp-content/uploads/2026/08/another-valid-looking-image.jpg'});
 reject('invented media bytes '+i,x=>{x.oversized_media[i].original_stored_bytes++});
 reject('hidden permission '+i,x=>{x.oversized_media[i].media_rehost_authorized=true});
 reject('native dimension modified '+i,x=>{x.oversized_media[i].native_dimensions_px.width++});
}
reject('compensating storage-byte swap',x=>{const p=x.oversized_media;[p[0].original_stored_bytes,p[1].original_stored_bytes]=[p[1].original_stored_bytes,p[0].original_stored_bytes]});
reject('edited upload timestamp',x=>{x.oversized_media[0].uploaded_date='2026-11-13T00:00:00'});
reject('image file mimetype switched',x=>{x.oversized_media[0].mime_type='image/jpeg'});
reject('descriptor removed',x=>{x.oversized_media.find(z=>z.wordpress_size_descriptors.length).wordpress_size_descriptors.pop()});
reject('descriptor invented',x=>{x.oversized_media[0].wordpress_size_descriptors.push({name:'large',virtual:false})});
reject('extra release field',x=>{x.wordpress_cache_allowed=true});
reject('extra policy field',x=>{x.rights_and_quality_policy.wp_upload_authorized=true});
reject('extra inventory field',x=>{x.inventory.cold_visitor_wire_bytes=240});
console.log('73/73 frozen-source identity assertions PASS (1 clean + 64 per-row + 8 additional)');

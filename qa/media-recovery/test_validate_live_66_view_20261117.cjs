'use strict';
// Run offline: node --test qa/media-recovery/test_validate_live_66_view_20261117.cjs
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readCensus,checkGitBlobs,verify}=require('./validate_live_66_view_20261117.cjs');
const base=readCensus();
function mutation(label,change) {
  test(label,()=>{
    const cloned=structuredClone(base);
    change(cloned);
    assert.throws(()=>verify(cloned.slices,cloned.rollup));
  });
}
test('unchanged live 66-post / 361-image audit validates',()=>{
  assert.deepEqual(verify(base.slices,base.rollup),{posts:66,images:361,external:294,hosts:81,missing_dimensions:273});
});
test('all nine source part files match their pinned Git blob SHA-1 identities',()=>{
  assert.doesNotThrow(()=>checkGitBlobs());
});
mutation('reject removed source image',x=>x.slices[1].images.splice(0,1));
mutation('reject an invented guest HTTP 404',x=>x.slices[1].images[0].visitor_http_status=404);
mutation('reject an invented visitor byte count',x=>x.slices[1].images[0].visitor_wire_bytes=199);
mutation('reject invented successful decode',x=>x.slices[1].images[0].visitor_decode=true);
mutation('reject unsupported image rehosting approval',x=>x.slices[1].images[0].replacement_approved=true);
mutation('reject fake cleared image rights',x=>x.slices[1].images[0].rights_rehosting='CLEARED');
mutation('reject origin-domain misclassification',x=>x.slices[1].images[0].origin_host='finalvestige.com');
mutation('reject a forged origin URL',x=>x.slices[1].images[0].source_origin_url='https://another-host.example/image.jpg');
mutation('reject duplicate CMS post IDs',x=>x.slices[1].posts[0].id=x.slices[0].posts[0].id);
mutation('reject changed image-slot index',x=>x.slices[1].images[0].slot=55);
mutation('reject unmeasured claimed 76 percent savings',x=>x.rollup.bandwidth_reduction_claim.verified_percent=76);
mutation('reject fake guest-confirmed broken count',x=>x.rollup.reported_broken_42.guest_confirmed_count=42);
mutation('reject unsupported visitor weight data',x=>x.rollup.oversized_library_originals.measured_user_wire_bytes=64385752);
mutation('reject P0 image URL substituted without proof',x=>x.rollup.priority_image_slots[0].view_url='https://elsewhere.example/another.jpg');
mutation('reject unapproved WordPress media uploads',x=>x.rollup.replacement_controls.rehost_or_wordpress_media_upload='approved');
mutation('reject incorrect 960px processing rule',x=>x.rollup.replacement_controls.max_target_width_px=1920);
mutation('reject any image upscaling permission',x=>x.rollup.replacement_controls.upscale=true);
mutation('reject any production writes',x=>x.rollup.production_writes=1);
mutation('reject count inflation on third-party images',x=>x.rollup.totals.external_origin_slots=300);
mutation('reject wrong source host frequencies',x=>x.rollup.source_hosts[0].count+=1);
mutation('reject a fabricated image dimension',x=>x.slices[1].images[0].width_attr=-10);

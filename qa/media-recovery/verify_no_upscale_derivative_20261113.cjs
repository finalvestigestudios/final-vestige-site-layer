'use strict';
/** Offline derivative gate. Call only with dimensions decoded from independently
 * SHA-256 verified ORIGINAL-MASTER and candidate raster bytes. This is not a
 * downloader, browser collector, rights grant, or publishing approval. */
const SHA=/^[0-9a-f]{64}$/;
const okDimension=n=>Number.isSafeInteger(n)&&n>0&&n<=100000;
const reject=reason=>({status:'HOLD',reason,derivative_review_admissible:false,
 production_write_allowed:false,third_party_cache_allowed:false});
function verifyNoUpscaleDerivative({review,master,derivative,masterSha256,rights}={}){
 const g=review?.geometry;
 if(!g||!master||!derivative||!rights||!SHA.test(masterSha256||'')||
    !okDimension(master.width)||!okDimension(master.height)||
    !okDimension(derivative.width)||!okDimension(derivative.height)||
    g.output_width!==derivative.width||g.output_height!==derivative.height||
    !['png','jpeg','webp'].includes(master.format)||
    !['png','jpeg','webp'].includes(derivative.format))
   return reject('MISSING_VERIFIED_MASTER_OR_DERIVATIVE_GEOMETRY');
 if(review.source_master_sha256!==masterSha256||
    rights.source_master_sha256!==masterSha256||
    review.source_master_provenance!=='AUTHORIZED_ORIGINAL_MASTER_BYTES'||
    rights.source_master_reuse_permission_verified!==true||
    rights.item_level_reuse_permission_verified!==true)
   return reject('MASTER_BYTES_AND_ITEM_RIGHTS_NOT_BOUND');
 if(derivative.width>960)
   return reject('DERIVATIVE_EXCEEDS_960PX_WIDTH');
 if(derivative.width>master.width||derivative.height>master.height)
   return reject('DERIVATIVE_WOULD_UPSCALE_MASTER');
 // Full-frame derivatives only. Material crop changes require a separate,
 // independently signed editorial scene/crop review, not an optimization pass.
 const cross=Math.abs(derivative.width*master.height-derivative.height*master.width);
 if(cross>Math.max(master.width,master.height))
   return reject('MASTER_ASPECT_OR_CROP_CHANGED');
 return {status:'ADMISSIBLE_FOR_MANUAL_STAGING_REVIEW_ONLY',reason:null,
   derivative_review_admissible:true,master_dimensions:[master.width,master.height],
   derivative_dimensions:[derivative.width,derivative.height],
   maximum_output_width_px:Math.min(master.width,960),
   no_upscale_verified_from_hash_bound_raster_geometry:true,
   image_scene_identity_verified:false,production_write_allowed:false,
   third_party_cache_allowed:false};
}
module.exports={verifyNoUpscaleDerivative};

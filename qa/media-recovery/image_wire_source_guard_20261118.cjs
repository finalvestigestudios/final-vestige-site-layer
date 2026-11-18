'use strict';
// Offline integrity gate for the Site QA cold-wire parity consumer.
// Verifies that a purported image response still represents the authored upstream
// asset; metadata-only source_identity labels must not launder a substituted image.
// No network, media download, WordPress write, or approval side effects.
const {parse, sourceMatches} = require('./jetpack_source_identity_20261118.cjs');
function canonicalOrigin(url) {
  const parsed=parse(url);
  if(!parsed)return null;
  const query=new URLSearchParams([...parsed.immutable.entries()].sort(([a,av],[b,bv])=>a.localeCompare(b)||av.localeCompare(bv))).toString();
  return `https://${parsed.host}${parsed.pathname}${query?'?'+query:''}`;
}
function guardImageSource(image, postId) {
  if(!image || typeof image!=='object' || Array.isArray(image))return {ok:false,reason:'missing_image'};
  if(!Number.isSafeInteger(Number(postId)) || Number(postId)<1 ||
    typeof image.asset_id!=='string' || !new RegExp(`^${postId}:\\d+$`).test(image.asset_id))
    return {ok:false,reason:'asset_slot_drift'};
  const expected=canonicalOrigin(image.authored_src);
  if(!expected || canonicalOrigin(image.source_identity)!==expected)
    return {ok:false,reason:'asserted_identity_drift'};
  if(!sourceMatches(image.current_src,image.authored_src))
    return {ok:false,reason:'responsive_source_drift'};
  // A redirect to another host/path is NOT proof of image identity. Site QA must
  // independently verify its actual raster/rights and stage a reviewed mapping.
  if(!sourceMatches(image.final_url,image.authored_src))
    return {ok:false,reason:'final_response_source_drift'};
  return {ok:true,reason:null,canonical_source:expected};
}
module.exports={canonicalOrigin,guardImageSource};

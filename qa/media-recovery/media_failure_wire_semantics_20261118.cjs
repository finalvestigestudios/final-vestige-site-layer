"use strict";
// Read-only CDP image response semantics. The before trace may contain a genuinely
// broken image request; its 404 HTML body must not be counted as image bandwidth.
// The after trace must contain a decoded 2xx image with real transfer bytes.
const pos=n=>Number.isSafeInteger(n)&&n>0;
const nonneg=n=>Number.isSafeInteger(n)&&n>=0;
function assessImageWire(m,phase) {
  const errors=[];
  if(!m||typeof m!=="object"||Array.isArray(m)||!["before","after"].includes(phase))
    return {errors:["response"],counted_bytes:0,broken:false};
  const status=Number.isInteger(m.http_status)&&m.http_status>=100&&m.http_status<=599;
  const success=status&&m.http_status>=200&&m.http_status<300;
  const failed=status&&m.http_status>=400;
  const imageMime=typeof m.mime==="string"&&/^image\/[a-z0-9.+-]+$/i.test(m.mime);
  const failureBody=typeof m.mime==="string"&&/^(?:text\/(?:html|plain)|application\/(?:json|problem\+json|xml))(?:\s*;.*)?$/i.test(m.mime);
  const beforeFailure=phase==="before"&&m.decoded===false&&(failed||success&&imageMime);
  const mimeOk=imageMime||(phase==="before"&&failed&&m.decoded===false&&failureBody);
  if(!status||!mimeOk||!(success||beforeFailure))errors.push("response");
  const validDecode=typeof m.decoded==="boolean"&&
    (m.decoded?(success&&imageMime&&pos(m.natural_width)&&pos(m.natural_height)):
       (m.natural_width===0&&m.natural_height===0));
  if(!validDecode)errors.push("decode_inconsistent");
  if(m.decoded===true&&!success)errors.push("decoded_error");
  if(phase==="after"&&m.decoded!==true)errors.push("broken_after");
  const measured=m.request_id&&typeof m.request_id==="string"&&
    m.from_cache===false&&m.from_service_worker===false&&
    m.transfer_metric==="CDP_ENCODED_DATALENGTH"&&
    (pos(m.transfer_bytes)||(beforeFailure&&nonneg(m.transfer_bytes)));
  if(!measured)errors.push("unmeasured_wire");
  // The target is *image* bytes, not error documents or HTTP failures.
  // Corrupt 2xx image responses remain counted (real image payload transfer).
  const counted=measured&&success&&imageMime?m.transfer_bytes:0;
  return {errors,counted_bytes:counted,broken:m.decoded===false,origin_error:beforeFailure&&failed};
}
module.exports={assessImageWire};

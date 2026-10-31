"use strict";
/**
 * Read-only MODEL of two published WordPress/Jetpack fallback excerpt limits.
 * Neither rule is a claim about an actual received email.
 * No I/O, no email API, no subscriber data.
 */
function plain(markdown) {
  return String(markdown).replace(/\[([^\]]+)\]\(https:\/\/[^)]+\)/g,"$1")
    .replace(/\[\[([A-Z0-9_]+)\]\]/g,"[$1]")
    .replace(/\*\*/g,"").replace(/\*/g,"")
    .replace(/\r/g,"").replace(/\s+/g," ").trim();
}
function segments(source) {
  const parts=String(source).split(/\n---\n/);
  if(parts.length<3) throw Error("Cannot identify issue body");
  return {header:parts[0],body:parts[1].trim(),footer:parts.slice(2).join("\n---\n")};
}
function analyze(entry, source) {
  const {body,header}=segments(source), bodyText=plain(body);
  const words=bodyText.split(/\s+/).filter(Boolean);
  const first55=words.slice(0,55).join(" ");
  const first350=bodyText.slice(0,350);
  const commercial=entry.kind==="commercial-review-pending";
  const target=entry.editorial_cta;
  if(!body.includes(target))throw Error("Missing CTA source for issue "+entry.number);
  const held=entry.publish_state==="hold" && entry.merchant_affiliate_url===null;
  if(!held) throw Error("Release hold or merchant URL changed for issue "+entry.number);
  const expectedSubject="**Subject:** "+entry.subject;
  if(!header.includes(expectedSubject)) throw Error("Subject drift in "+entry.number);
  const term=target.startsWith("[[") ? target.replace(/\[\[|\]\]/g,"") : target;
  const model=(sample)=>({
    characters:sample.length,
    words:sample.split(/\s+/).filter(Boolean).length,
    fraction_of_full_text:Number((sample.length/bodyText.length).toFixed(3)),
    cta_target_present:sample.includes(term),
    commercial_disclosure_present:/commercial disclosure:|may earn a commission|may receive a commission/i.test(sample),
    excerpt_text:sample
  });
  const a=model(first55),b=model(first350);
  return {issue:entry.number,subject:entry.subject,kind:entry.kind,proposed_preheader_not_native_verified:entry.preheader,
    source_cta_target_present:true,commercial_disclosure_in_full_source:commercial?/\*\*Commercial disclosure:/i.test(body):null,
    default_excerpt_55_word_model:a,default_excerpt_350_character_model:b,
    modeled_default_misses_primary_cta:!a.cta_target_present&&!b.cta_target_present,
    requires_actual_per_post_format_inspection:true,
    requires_actual_received_wordpress_mime:true,
    guide_url_verified:!commercial,merchant_email_permission_verified:!commercial,
    ready_to_send:false};
}
function audit(manifest, sources) {
  if(manifest.mix.editorial!==4||manifest.mix.commercial_review_pending!==2||manifest.issues.length!==6)
    throw Error("Founder's 4:2 pilot corrupted");
  return manifest.issues.map(i=>analyze(i,sources[i.number]));
}
module.exports={plain,segments,analyze,audit};

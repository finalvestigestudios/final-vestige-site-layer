'use strict';
function copyPreserved(before,after,from,to) {
 if(typeof before!=="string"||typeof after!=="string"||typeof from!=="string"||typeof to!=="string"||!from||!to||from===to||/["<>]/.test(from+to))return false;
 const tags=[...before.matchAll(/<img\b[^>]*>/gi)];
 const hits=tags.filter(m=>m[0].includes(' src="'+from+'"'));
 if(hits.length!==1)return false;
 const hit=hits[0], needle=' src="'+from+'"';
 if(hit[0].split(needle).length!==2)return false;
 const next=hit[0].replace(needle,' src="'+to+'"');
 return after===before.slice(0,hit.index)+next+before.slice(hit.index+hit[0].length);
}
function evaluate(r, evidence={}) {
 const reasons=[];
 if(r.kind!=="existing_attachment_reuse_candidate")reasons.push("already first-party; measure before optimizing");
 if(r.attachmentDimensions[0]!==r.catalogDimensions[0]||r.attachmentDimensions[1]!==r.catalogDimensions[1]||r.attachmentBytes!==r.catalogBytes)reasons.push("metadata mismatch");
 if(evidence.revision!==r.revision||evidence.slot!==r.slot||evidence.beforeSrc!==r.authoredSrc)reasons.push("stale or wrong target");
 if(evidence.mobileProblemVerified!==true||!Number.isInteger(evidence.status)||!(evidence.status===404||evidence.status===410||(evidence.status>=200&&evidence.status<300&&evidence.measuredPerformanceProblem===true)))reasons.push("no verified mobile problem");
 if(evidence.sameFrameAndRightsReviewed!==true||!(/^[a-f0-9]{64}$/).test(evidence.masterSha256||""))reasons.push("identity or rights missing");
 if(evidence.afterSrc!==r.existingVariant.url||r.existingVariant.width>960||r.existingVariant.width>r.attachmentDimensions[0])reasons.push("unapproved derivative route or geometry");
 if(typeof evidence.beforeMarkup!=="string"||typeof evidence.afterMarkup!=="string"||!copyPreserved(evidence.beforeMarkup,evidence.afterMarkup,r.authoredSrc,r.existingVariant.url))reasons.push("copy or markup changed beyond exact single source substitution");
 return {decision:reasons.length?"HOLD":"STAGING_REVIEW_ONLY",reasons};
}
module.exports={evaluate,copyPreserved};

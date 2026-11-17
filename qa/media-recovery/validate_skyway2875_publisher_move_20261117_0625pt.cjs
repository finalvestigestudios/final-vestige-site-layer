'use strict';
// Offline only; fail closed; no network or WordPress mutation.
function checkLedger(d){
 const need=(p,msg)=>{if(!p)throw Error(msg)};
 need(d&&d.schema==="fv-skyway2875-relocation-v1","schema");
 need(d.source?.slot==="287:5"&&d.source.post_id===287&&d.source.prior_blob==="dcb735226eb71fcba302b38ae3ab3a73751fe2a8","lineage");
 need(d.published.authored_url==="https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg"&&d.published.jetpack_view_src==="https://i0.wp.com/stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg?ssl=1","source paths");
 need(d.origin_candidate.url==="https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg","publisher new path");
 need(d.published.alt.includes("later bridge replacement")&&d.published.html_width===null&&d.published.html_height===null,"ALT/dims source");
 const m=d.origin_candidate;need(m.copyright==="UNKNOWN_NOT_AUTHORIZED"&&m.image_author==="UNKNOWN"&&m.binary_sha256===null&&m.native_dimensions===null&&m.conditional_960px===null&&m.max_width_no_upscale===960&&m.cache_authorized===false,"rights/dimensions");
 const r=d.reader_observations;need(r?.length===3&&r.map(x=>x.route).join("|")==="old_origin|publisher_moved|published_jetpack","routes");
 need(r[0].url===d.published.authored_url&&r[0].outcome==="RETRIEVER_HTTP_404"&&r[0].retriever_http_status===404,"retriever old");
 need(r[1].url===m.url&&r[1].outcome==="IMAGE_RENDERED"&&r[1].retriever_http_status===null,"retriever moved");
 need(r[2].url===d.published.jetpack_view_src&&r[2].outcome==="UNKNOWN"&&r[2].retriever_http_status===null,"Jetpack unknown");
 for(const x of r)need(x.guest_http_status===null&&x.guest_current_src===null&&x.guest_mime===null&&x.guest_decoded===null&&x.guest_natural_width===null&&x.guest_transfer_bytes===null,"fabricated browser result");
 need(d.archives?.length===2&&d.archives.map(x=>x.id).sort().join(",")==="RC09236,RC09237","archives");
 for(const a of d.archives)need(a.catalog.startsWith("https://www.floridamemory.com/items/show/")&&a.image.startsWith("https://www.floridamemory.com/fpc/reference/")&&a.relation==="DIFFERENT_FRAME"&&a.substitution_authorized===false&&a.native_dimensions===null&&a.review_960px===null,"false archive clearance");
 need(d.visual?.editorial_review_required===true&&!d.visual.auto_change,"editorial review");
 need(d.guest_release_gate?.owner==="Site QA PR #154 existing cold-browser collector"&&d.guest_release_gate.required.length===10&&d.guest_release_gate.decision==="HOLD_GUEST_RIGHTS_IDENTITY"&&!d.guest_release_gate.wordpress_write&&!d.guest_release_gate.rehost&&!d.guest_release_gate.automatic_replacement,"release");
 need(d.stats?.historical_posts===61&&d.stats.historical_images===355&&d.stats.oversized_wp_originals_gt_1_5mb===20&&d.stats.oversized_stored_bytes===64385752,"baselines");
 need(!d.stats.reported_broken_42_confirmed&&!d.stats.claimed_76pct_wire_reduction_measured&&d.stats.guest_wire_before===null&&d.stats.guest_wire_after===null,"browser 42/76");
 need(Object.keys(d.restrictions).length===7&&Object.values(d.restrictions).every(v=>v===false),"production");
 return "HOLD";
}
module.exports={checkLedger};

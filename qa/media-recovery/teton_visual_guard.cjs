'use strict';
function validate(d){
 const errors=[],ok=(x,m)=>{if(!x)errors.push(m)};
 if(!d||!Array.isArray(d.images))return{ok:false,errors:['missing_images']};
 ok(d.schema===1&&d.images.length===12,'snapshot_12');
 const keys=new Set();
 for(const x of d.images){
  ok(!keys.has(x.key),'duplicate_key');keys.add(x.key);
  ok(typeof x.url==='string'&&x.url.startsWith('https://')&&x.origin==='external','source_kind');
  ok(x.http_status===null&&x.natural_width===null&&x.wire_bytes===null&&x.broken_in_browser===null,'invented_browser_data');
  ok(x.rights_cleared===false&&x.wp_edit_approved===false&&x.max_width===960&&x.no_upscale===true,'rights_or_size');
 }
 const a=d.images.find(x=>x.key==='291:2'),b=d.images.find(x=>x.key==='291:5');
 ok(!!a&&!!b&&a.url===b.url&&d.duplicate_photo?.source_url===a.url,'same_photo');
 ok(/breach/i.test(a?.alt||'')&&/aftermath/i.test(b?.alt||''),'captions');
 ok(d.source_reconciliation?.current_original_classifier?.['291']===6&&d.source_reconciliation?.current_original_classifier?.['285']===6,'source_recount');
 ok(d.alternative?.naid==='28894684'&&d.alternative?.license==='HOLD_PER_IMAGE'&&d.alternative?.approved===false&&d.alternative?.original_binary_sha256===null,'archive_candidate_hold');
 ok(d.claims?.image_failures_42_verified===false&&d.claims?.weight_savings_76pct_verified===false&&d.claims?.no_wordpress_changes===true,'metrics');
 return{ok:errors.length===0,errors,images:d.images.length};
}
module.exports={validate};

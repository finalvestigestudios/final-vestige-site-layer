'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {validate}=require('./validate_iroquois_283_seven_visual_20261109.cjs');
const source=JSON.parse(fs.readFileSync('qa/media-recovery/iroquois_283_seven_visual_20261109.json','utf8'));
const mutate=(fn)=>{const z=JSON.parse(JSON.stringify(source));fn(z);return z};
test('seven-source evidence ledger passes',()=>assert.deepEqual(validate(source),[]));
const changes=[
['invented visitor 404',a=>a.source_rows[0].retriever.guest_http_status=404],
['invented origin 200',a=>a.source_rows[0].retriever.origin_http_status=200],
['invented decoded width',a=>a.source_rows[0].retriever.natural_width_px=960],
['invented wire bytes',a=>a.source_rows[0].retriever.wire_transfer_bytes=500],
['invented visitor broken',a=>a.source_rows[0].retriever.guest_broken=true],
['fabricated currentSrc',a=>a.source_rows[0].retriever.visitor_current_src='https://example.com'],
['false claims 42 confirmed',a=>a.historical_baseline.reported_broken_42_confirmed_by_guest_browser=true],
['false claims 76 measured',a=>a.historical_baseline.proposed_transfer_reduction_76pct_measured=true],
['changed original src',a=>a.source_rows[0].stored_source_url+='?foo=bar'],
['changed original alt',a=>a.source_rows[0].published_alt='A fire door'],
['changed inventory sha',a=>a.post.inventory_blob_sha='wrong'],
['delete source position',a=>a.source_rows.pop()],
['duplicate source position',a=>a.source_rows[1].key='283:0'],
['wrong image viewer status',a=>a.source_rows[3].retriever.observation='CONFIRMED_BROKEN'],
['censor diagram mismatch',a=>a.source_rows[0].visual.assessment='MATCHES_GENERAL_SCENE'],
['censor stairwell provenance flag',a=>a.source_rows[5].visual.assessment='MATCHES_GENERAL_SCENE'],
['censor facade chronology flag',a=>a.source_rows[6].visual.assessment='MATCHES_GENERAL_SCENE'],
['drop proposed editorial alt',a=>a.source_rows[0].visual.proposed_alt_review_only=null],
['invent editorial update',a=>a.source_rows[0].visual.editorial_change_applied=true],
['invent catalog identity',a=>a.source_rows[0].candidate.exact_pixel_and_crop_identity_proven=true],
['invent copyright clearance',a=>a.source_rows[0].candidate.rehosting_rights_cleared=true],
['invent downloaded binary',a=>a.source_rows[0].candidate.cached_or_downloaded=true],
['enlarge candidate',a=>a.source_rows[2].candidate.conditional_target_px=[960,568]],
['distort candidate',a=>a.source_rows[2].candidate.conditional_target_px=[715,400]],
['change maximum width',a=>a.source_rows[2].candidate.maximum_target_width_px=1280],
['enable WP upload',a=>a.source_rows[0].release.wordpress_upload_allowed=true],
['enable WP rewrite',a=>a.source_rows[0].release.post_rewrite_allowed=true],
['enable image caching',a=>a.source_rows[0].release.cache_allowed=true],
['enable external swap',a=>a.source_rows[0].release.source_swap_allowed=true],
['enable homepage design',a=>a.source_rows[0].release.homepage_change_allowed=true],
['hijack browser QA ownership',a=>a.acceptance_plan.owner='Media Recovery'],
['claim guest confirmed',a=>a.counts.guest_confirmed_broken=1]
];
for(const [name,fn] of changes)test(name,()=>assert.ok(validate(mutate(fn)).length>0));

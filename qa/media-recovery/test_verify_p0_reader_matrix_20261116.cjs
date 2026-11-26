'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {audit,P0} = require('./verify_p0_reader_matrix_20261116.cjs');
const fixture = path.join(__dirname,'p0_reader_matrix_20261116_1230pt.json');
const pinFile = path.join(__dirname,'p0_source_pin_projection_20261116.json');
const base = () => JSON.parse(fs.readFileSync(fixture,'utf8'));
const pinned = () => JSON.parse(fs.readFileSync(pinFile,'utf8'));
const mutated = (fn) => { const x=base(); fn(x); return audit(x,pinned()); };
test('pinned manifest, six slots and all existing upstream outcomes remain HOLD', () => {
  assert.deepEqual(P0,['285:5','285:2','287:5','418:1','418:2','407:1']);
  const r=audit(base(),pinned()); assert.equal(r.ok,true); assert.equal(r.decision,'HOLD');
  assert.equal(r.p0_slots_crosschecked,6); assert.equal(r.retriever_errors,6);
  assert.equal(r.alternatives_displayed_in_reader,3); assert.equal(r.guest_broken_confirmed,0);
  assert.equal(r.wordpress_writes,0);
});
const cases=[
  ['no 42-claim upgrade',x=>x.reported_42_guest_confirmed=true],
  ['no 76-claim upgrade',x=>x.measured_76_percent_wire_reduction=true],
  ['pinned source cannot drift',x=>x.pinned_source_blob_sha='bad'],
  ['no production writes',x=>x.wordpress_writes=1],
  ['no image downloading',x=>x.image_downloads=1],
  ['cannot skip a slot',x=>x.rows.pop()],
  ['cannot reorder a slot',x=>x.rows.reverse()],
  ['cannot change post URL',x=>x.rows[0].post_url='https://evil.example/'],
  ['cannot change authored URL',x=>x.rows[0].authored_url='https://evil.example/p.jpg'],
  ['cannot change Jetpack URL',x=>x.rows[0].jetpack_view_url='https://evil.example/p.jpg'],
  ['cannot drift WordPress revision',x=>x.rows[0].wp_modified='2026-11-16T11:11:11'],
  ['browser HTTP cannot be inferred from fetcher',x=>x.rows[2].guest_http_status=404],
  ['visitor decoded cannot be asserted',x=>x.rows[2].guest_decoded=false],
  ['network bytes cannot be fabricated',x=>x.rows[2].guest_transferred_bytes=1234],
  ['visitor broken cannot be asserted',x=>x.rows[2].broken_for_visitors_confirmed=true],
  ['fetcher 404 is not numeric HTTP 404',x=>x.rows[2].reader_numeric_http_status=404],
  ['tool result is not browser',x=>x.rows[3].reader_result_is_browser_http=true],
  ['unknown tool error code rejected',x=>x.rows[4].reader_tool_code=503],
  ['candidate must be image URL',x=>x.rows[5].alternative.image_url=''],
  ['candidate credentials rejected',x=>x.rows[5].alternative.image_url='https://user:pass@site.test/1.jpg'],
  ['candidate rights cannot auto-approve',x=>x.rows[5].alternative.rehosting_rights_approved=true],
  ['candidate same pixels cannot auto-approve',x=>x.rows[5].alternative.same_pixels_and_crop_verified=true],
  ['candidate native dimensions cannot be invented',x=>x.rows[5].alternative.native_dimensions_verified=true],
  ['candidate review dimensions cannot be invented',x=>x.rows[5].alternative.proposed_width_px=960],
  ['preview width cannot be negative',x=>x.rows[5].alternative.preview_width_px=-50],
  ['no cached mirror permission',x=>x.rows[5].cache_authorized=true],
  ['no WordPress write approval',x=>x.rows[5].wordpress_write_authorized=true],
  ['no released item rights',x=>x.rows[5].rights_release='APPROVED'],
  ['max width bound cannot change',x=>x.rows[5].max_review_width_px=1920]
];
for (const [title,fn] of cases) test(title,()=>assert.equal(mutated(fn).ok,false));

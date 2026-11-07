import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateTexasCity216 } from './validate_texas_city_216_20261107.mjs';
const ledger=JSON.parse(readFileSync(new URL('./texas_city_216_six_archive_20261107.json',import.meta.url),'utf8'));
const clone=x=>JSON.parse(JSON.stringify(x));
test('six frozen source and catalog bindings, fail-closed',()=>assert.deepEqual(validateTexasCity216(ledger),[]));
const changes=[
 d=>d.guest_browser_verified=true,d=>d.claimed_42_broken_images_verified=true,d=>d.claimed_76pct_wire_reduction_measured=true,
 d=>d.observed_broken_guest_images=6,d=>d.measured_transfer_delta_bytes=999,d=>d.wp_production_writes=1,
 d=>d.downloaded_media=1,d=>d.cached_media=1,d=>d.spend_usd=0.01,
 d=>d.priority_order_not_replaced.reverse(),d=>d.images.pop(),d=>d.images[0].key='216:1',
 d=>d.images[1].published_src='https://www.example.com/fake.jpg',d=>d.images[2].catalog_master_px.width=1024,
 d=>d.images[5].conditional_preview_px.width=960,d=>d.images[0].declared_html_width=960,
 d=>d.images[3].rights_review='public_domain_approved',d=>d.images[1].rights_for_local_cache_approved=true,
 d=>d.images[4].editorial_hold='none',d=>d.images[4].actual_http_status=404,
 d=>d.images[2].guest_broken=true,d=>d.images[3].guest_network_transfer_bytes=1024,
 d=>d.images[5].asset_downloaded=true,d=>d.images[1].wp_attachment_id=999,
 d=>d.images[5].source_credit='',d=>d.images[0].candidate_relation='confirmed exact replacement',
 d=>d.images[3].web_retriever_result='http_404',d=>d.images[1].conditional_preview_px.height=1000
];
changes.forEach((change,i)=>test('unsafe mutation #'+(i+1)+' rejected',()=>{const x=clone(ledger);change(x);assert.notDeepEqual(validateTexasCity216(x),[])}));

'use strict';
const assert=require('node:assert/strict');
const {validate}=require('./validate_st_francis_166_20261103.cjs');
const original=require('./st_francis_166_catalog_20261103.json');
let passed=0;
function copy(){return JSON.parse(JSON.stringify(original));}
function positive(name,change){const x=copy();if(change)change(x);assert.deepEqual(validate(x),[],name);passed++;}
function negative(name,change){const x=copy();change(x);assert.ok(validate(x).length>0,name);passed++;}
positive('exact pinned evidence passes');
negative('fabricated HTTP 200',x=>x.rows[1].origin_browser_http_status=200);
negative('fabricated browser 404',x=>x.rows[2].origin_browser_http_status=404);
negative('invented browser decoded success',x=>x.rows[3].origin_browser_decode_ok=true);
negative('invented visitor broken',x=>x.rows[4].visitor_broken=true);
negative('invented cold wire bytes',x=>x.rows[5].cold_browser_transfer_bytes=50000);
negative('promotion of retriever result to origin status',x=>x.rows[2].probe.origin_status_verified=true);
negative('forged retriever 403',x=>x.rows[1].probe.http_status=403);
negative('source silently swapped',x=>x.rows[6].published_src='https://evil.example/x.jpg');
negative('source blob changed',x=>x.archived_inventory.blob_sha='deadbeef');
negative('site content drift',x=>x.archived_inventory.all_published_sources_match_live_wp=false);
negative('first-party image omitted',x=>x.rows.shift());
negative('duplicate key',x=>x.rows[5].key=x.rows[4].key);
negative('rights treated as cleared',x=>x.rows[5].rights_review_complete=true);
negative('WP upload authorized',x=>x.rows[2].wp_media_upload_authorized=true);
negative('production rewrite authorized',x=>x.rows[4].production_rewrite_authorized=true);
negative('visual match fabricated',x=>x.rows[6].candidate_visual_match_verified=true);
negative('copyright critical information stripped',x=>x.rows[5].catalog.rights_basis='');
negative('invented LoC geometry',x=>x.rows[1].derivative_dimensions_px=[960,600]);
negative('no-upscale violation',x=>x.rows[4].derivative_dimensions_px=[1280,954]);
negative('incorrect aspect ratio',x=>x.rows[6].derivative_dimensions_px=[960,700]);
negative('claimed 42 verified',x=>x.stats.claimed_broken_42_verified=true);
negative('claimed 76 percent verified',x=>x.stats.claimed_reduction_76pct_verified=true);
negative('fake production repair count',x=>x.stats.production_changes=1);
negative('invalid post status',x=>x.post.status='draft');
console.log(passed+'/'+passed+' St Francis source integrity tests PASS');

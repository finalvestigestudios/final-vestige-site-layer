'use strict';
const assert=require('node:assert/strict');
const data=require('./okeechobee432_seven_catalog_crosswalk_20261117_0033pt.json');
const {validate}=require('./validate_okeechobee432_seven_catalog_crosswalk_20261117_0033pt.cjs');
function run(){
 const mutations=["fabricate guest HTTP", d=>d.items[0].guest.http_status=200],
["fabricate guest 404", d=>d.items[2].guest.http_status=404],
["fabricate failed decode", d=>d.items[1].guest.decoded=false],
["fabricate transferred bytes", d=>d.items[2].guest.transferred_bytes=200],
["fabricate screenshot", d=>d.items[0].guest.screenshot="https://cdn.example/p.png"],
["fabricate original HTTP", d=>d.items[3].origin_http_status=200],
["fabricate catalog HTTP", d=>d.items[5].catalog_http_status=200],
["falsely confirm 42", d=>d.baselines.confirmed_broken=42],
["falsely claim 76", d=>d.baselines.measured_savings_percent=76],
["conflate storage wire", d=>d.baselines.guest_transferred_bytes=64385752],
["mixed 66-post cohort", d=>d.baselines.historical_posts=66],
["drop last slot", d=>d.items.pop()],
["duplicate slot", d=>d.items[6].key="432:5"],
["alter original URL", d=>d.items[3].authored_url="https://example.com/a.jpg"],
["alter Jetpack", d=>d.items[4].published_view_url="https://www.floridamemory.com/fpc/reference/rc04344.jpg"],
["alter source catalog", d=>d.items[0].primary_catalog_url="https://example.com"],
["mismatch accession", d=>d.items[1].primary_accession="RC17074"],
["pretend catalog image binary", d=>d.items[2].original_route_relation="CATALOG_IS_JPEG"],
["pretend date 1928 for modern photo", d=>d.items[6].catalog_date="1928"],
["erase Pahokee overclaim warning", d=>d.items[3].editorial_note="all confirmed"],
["erase 2001 caution", d=>d.items[6].editorial_note="old burial"],
["invent native pixels", d=>d.items[0].geometry.native_width=1200],
["invent 960px export", d=>d.items[0].geometry.proposed_width=960],
["upscale max", d=>d.items[0].geometry.max_width=1920],
["turn off no-upscale", d=>d.items[0].geometry.no_upscale=false],
["premature rights", d=>d.items[0].clearance.item_rights_approved=true],
["premature rehosting", d=>d.items[0].clearance.wordpress_rehost_approved=true],
["fake binary hash", d=>d.items[0].clearance.binary_sha256="ab".repeat(32)],
["fake exact pixels", d=>d.items[0].clearance.same_frame_verified=true],
["allow production", d=>d.safeguards.wordpress_production_writes=1],
["allow mirror", d=>d.safeguards.media_rehosts=1],
["spend", d=>d.safeguards.subscription_spend_usd=12],
["homepage intrusion", d=>d.safeguards.homepage_design_changes=1],
["collector duplicated", d=>d.safeguards.browser_collector_duplicated=true],
["false approved", d=>d.safeguards.decision="APPROVED"],
["erase collection rights caveat", d=>d.rights.mark="No copyright"],
["change provenance blob", d=>d.provenance.source_ledger_blob_sha="x"];
 let passed=0;for(const [name,change] of [['baseline',()=>{}],...mutations]){const fixture=JSON.parse(JSON.stringify(data));change(fixture);const result=validate(fixture);assert.equal(result.ok,name==='baseline',name+': '+result.errors.join(','));passed++;}return passed;}
const passed=run();assert.equal(passed,38);console.log(passed+'/'+passed+' offline fail-closed cases passed');

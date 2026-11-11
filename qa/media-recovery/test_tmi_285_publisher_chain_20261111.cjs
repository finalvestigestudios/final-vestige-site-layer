'use strict';
const {test}=require('node:test'), assert=require('node:assert/strict');
const fs=require('node:fs'), path=require('node:path');
const {verify}=require('./validate_tmi_285_publisher_chain_20261111.cjs');
const source=JSON.parse(fs.readFileSync(path.join(__dirname,'tmi_285_publisher_chain_20261111.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(source));
const cases=[
["valid",a=>{},false],
["origin404",a=>a.originals[0].origin_http_status=404,true],
["guest200",a=>a.originals[0].guest_http_status=200,true],
["guest404",a=>a.originals[1].guest_http_status=404,true],
["inventedWire",a=>a.originals[0].cold_encoded_transfer_bytes=300,true],
["inventedCurrentSrc",a=>a.originals[1].guest_current_src="https://new.example",true],
["falseFailure",a=>a.originals[0].guest_failure_confirmed=true,true],
["falseRights",a=>a.originals[0].rights_clearance_verified=true,true],
["falseCrop",a=>a.originals[0].scene_crop_approved=true,true],
["falseCache",a=>a.originals[0].caching_approved=true,true],
["falseUpload",a=>a.originals[1].wordpress_staging_media_upload_approved=true,true],
["falseProduction",a=>a.originals[1].wordpress_production_write_approved=true,true],
["changedSource",a=>a.originals[0].stored_src="https://other.example",true],
["wrongWrapper",a=>a.originals[1].retriever.method="GUEST_CHROMIUM",true],
["fakeOrigin404",a=>a.originals[0].retriever.wrapper_code=200,true],
["wrongCropWidth",a=>a.originals[0].candidate.conditional_no_upscale_output_px=[960,720],true],
["fakeNative",a=>a.originals[0].candidate.native_px=[960,720],true],
["publisherSubstitution",a=>a.originals[0].publisher.image_credit_url="https://other.example",true],
["different1979AsSame",a=>a.originals[0].historical_alternative.same_photo=true,true],
["wrong1979Date",a=>a.originals[0].historical_alternative.year=2010,true],
["wrongFigure",a=>a.originals[1].publisher.figure_index=5,true],
["wrongNrcAttribution",a=>a.originals[1].publisher.figure_credit="UCS",true],
["inventedNrcCatalog",a=>a.originals[1].candidate.catalog_url="https://nrc.gov/guess",true],
["inventedNrcDimensions",a=>a.originals[1].candidate.native_px=[700,500],true],
["inventedNrcDerivative",a=>a.originals[1].candidate.original_derivative_crop_match_verified=true,true],
["duplicateSlot",a=>a.originals[1].slot="285:5",true],
["missingSlot",a=>a.originals.pop(),true],
["wrongCohort",a=>a.baseline.historical_posts=66,true],
["forged42",a=>a.baseline.guest_verified_broken=42,true],
["forged76",a=>a.baseline.measured_wire_saving_pct=76,true],
["storageAsWire",a=>a.baseline.oversized_stored_original_bytes=0,true],
["copiedCollector",a=>a.release.siteqa_guest_browser_collector_owner=1703,true],
["wrongQueue",a=>a.release.original_priority_order.reverse(),true],
["unlimitedWidth",a=>a.release.no_upscale_max_width_px=4000,true],
["wpWrite",a=>a.release.wordpress_writes=1,true],
["assetDownload",a=>a.release.third_party_binary_downloads=1,true],
["subscriptionSpend",a=>a.release.subscription_spend_usd=1,true],
["badBridgeSha",a=>a.reference_bridge_blob_sha="x",true]
];
for(const [name,modify,invalid] of cases){
test(name,()=>{const x=clone();modify(x);const failures=verify(x);assert.equal(failures.length>0,invalid,name+' '+failures.join(','));});
}

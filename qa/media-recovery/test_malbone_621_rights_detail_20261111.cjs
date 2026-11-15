'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {audit,proposal,frozen}=require('./assess_malbone_621_rights_detail_20261111.cjs');
const source=JSON.parse(fs.readFileSync(path.join(__dirname,'malbone_621_rights_detail_20261111.json'),'utf8'));
const copy=()=>structuredClone(source);
test('frozen two-row ledger records evidence but does NOT approve publication',()=>assert.equal(audit(source).state,'RECORD_VERIFIED_NOT_PUBLISHABLE'));
const mut=[
['wrong original URL',x=>x.rows[0].original_url='https://example.org/other.jpg'],
['wrong map original size',x=>x.rows[1].stored_bytes=8],
['fake 76 percent transfer',x=>x.measured_sitewide_transfer_reduction_pct=76],
['fabricated network bytes',x=>x.rows[1].guest_wire_bytes=100],
['fake guest currentSrc',x=>x.rows[0].guest_current_src='https://x.org/a.jpg'],
['fake origin 404',x=>x.rows[1].retriever.origin_http_status=404],
['fake guest 200',x=>x.rows[0].retriever.guest_browser_http_status=200],
['bad photo attribution',x=>x.rows[0].published_caption_credit='Unknown'],
['incorrect map history',x=>x.rows[1].visual_role='1918 wreck plan'],
['bad map catalog image ID',x=>x.rows[1].catalog_image_id='wrong'],
['map 960 only policy',x=>x.safeguards.require_same_map_accessible_full_detail=false],
['duplicate slot',x=>x.rows[1].slot='621:0'],
['false rights clearance',x=>x.rows[0].rights_cleared=true],
['illegal WP permission',x=>x.rows[1].production_write_approved=true],
['bad map image size',x=>x.rows[1].conditional_960_px=[960,960]],
['bad copyright provenance',x=>x.rows[0].catalog_item_identity_proven=true]
];
for(const [name,fn] of mut)test('audit rejects '+name,()=>{const x=copy();fn(x);assert.equal(audit(x).state,'HOLD')});
const photo=()=>({source_url:frozen['621:0'].url,original_bytes:4798395,output_px:[960,720],editor_visual_review:true,editor_rights_review:true,credit_link:'https://commons.wikimedia.org/wiki/File:VerifiedExample.jpg',author:'GeneralPunger',license:'CC-BY-SA-4.0',license_url:'https://creativecommons.org/licenses/by-sa/4.0/',catalog_photo_identity_verified:true,edit_notice_recorded:true});
const map=()=>({source_url:frozen['621:1'].url,original_bytes:5553669,output_px:[960,649],editor_visual_review:true,editor_rights_review:true,credit_link:'https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0',map_date:1903,asserts_1918_curve:false,nypl_catalog_url:'https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0',same_map_full_detail_verified:true,full_detail_url:frozen['621:1'].url,full_detail_width:5667,full_detail_height:3831,full_detail_guest_accessible:true});
test('photo only hypothetical isolated staging',()=>assert.equal(proposal('621:0',photo()).state,'ISOLATED_STAGING_CANDIDATE_ONLY'));
test('map only hypothetical isolated staging',()=>assert.equal(proposal('621:1',map()).state,'ISOLATED_STAGING_CANDIDATE_ONLY'));
for(const [name,slot,builder,change] of [
['photo no credit','621:0',photo,p=>p.author='None'],
['photo no license','621:0',photo,p=>p.license_url=''],
['photo different subject','621:0',photo,p=>p.replaced_subject=true],
['photo source unverified','621:0',photo,p=>p.catalog_photo_identity_verified=false],
['photo oversize','621:0',photo,p=>p.output_px=[1920,1440]],
['photo attribution no review','621:0',photo,p=>p.editor_rights_review=false],
['photo asserts savings','621:0',photo,p=>p.percent_savings_claim=76],
['map illegible without original','621:1',map,p=>p.same_map_full_detail_verified=false],
['map zoom only 960 pixels','621:1',map,p=>p.full_detail_width=960],
['map guest full resolution unavailable','621:1',map,p=>p.full_detail_guest_accessible=false],
['map false 1918 curve','621:1',map,p=>p.asserts_1918_curve=true],
['map rotated crop','621:1',map,p=>p.output_px=[960,540]],
['map wrong source','621:1',map,p=>p.nypl_catalog_url='https://nypl.org/other'],
['map production write','621:1',map,p=>p.production_write=true],
])test('proposal rejects '+name,()=>{const p=builder();change(p);assert.equal(proposal(slot,p).state,'HOLD')});

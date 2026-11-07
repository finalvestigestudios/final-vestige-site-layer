"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const {validate}=require("./validate_archimedes_268_20261106.cjs");
const baseline=require("./archimedes_268_primary_rights_geometry_20261106.json");
const clone=()=>JSON.parse(JSON.stringify(baseline));
test("committed ten-image original-source audit validates",()=>assert.deepEqual(validate(clone()),[]));
const mutations=[
 ["source URL substitution",x=>x.images[0].stored_src="https://incorrect.example/"],
 ["fake visitor 404",x=>x.images[3].guest_browser_http_status=404],
 ["fake origin 200",x=>x.images[6].actual_origin_http_status=200],
 ["fake visitor byte transfer",x=>x.images[7].guest_encoded_bytes=321],
 ["fake decoded width",x=>x.images[0].guest_natural_width=665],
 ["premature copyright clearance",x=>x.images[1].rights_cleared=true],
 ["unapproved rehost",x=>x.images[3].rehost_approved=true],
 ["unverified binary identical",x=>x.images[2].image_exact_binary_matched=true],
 ["upscale 665px source",x=>x.images[0].conditional_max_960px_no_upscale.width=960],
 ["wrong preview aspect ratio",x=>x.images[9].conditional_max_960px_no_upscale.height=1200],
 ["missing original catalog pixels",x=>x.images[5].catalog_original_pixels=null],
 ["invented project native pixels",x=>x.images[8].catalog_original_pixels={width:960,height:800}],
 ["false Wikimedia class",x=>x.images[4].source_class="commons_redirect"],
 ["concealed dual licensing",x=>x.images[6].documented_license_assertions=["CC BY 3.0"]],
 ["PD outside US claimed",x=>x.images[0].documented_license_assertions=["public domain everywhere"]],
 ["ALT erased",x=>x.images[2].stored_alt=""],
 ["one image removed",x=>x.images.pop()],
 ["slot identity duplicate",x=>x.images[1].slot=9],
 ["query width altered",x=>x.images[0].requested_width_parameter=960],
 ["42 failures claimed confirmed",x=>x.source_limitations.broken_42_guest_confirmed=true],
 ["76 percent claimed measured",x=>x.source_limitations.percent_76_savings_measured=true],
 ["WordPress edit enabled",x=>x.production_actions.wordpress_writes=1],
 ["download enabled",x=>x.production_actions.image_downloads=1],
 ["cache enabled",x=>x.production_actions.caching=1],
 ["wrapper mislabeled browser",x=>x.images[1].web_retriever.outcome="guest_403"]
];
for(const [name,mutate] of mutations)test(name+" fails closed",()=>{const input=clone();mutate(input);assert.ok(validate(input).length>0,name);});

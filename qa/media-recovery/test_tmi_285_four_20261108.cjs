'use strict';
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {validate}=require("./validate_tmi_285_four_20261108.cjs");
const original=JSON.parse(fs.readFileSync(path.join(__dirname,"tmi_285_four_offsite_20261108.json"),"utf8"));
function clone(){return JSON.parse(JSON.stringify(original));}
let done=0;
function ok(name,mutate){const a=clone();if(mutate)mutate(a);const r=validate(a);assert.equal(r.valid,!mutate,name+" "+JSON.stringify(r));done++;}
ok("unaltered source audit",null);
const mods=[
["new unknown root key",a=>a.browser_verified=true],
["alter method",a=>a.web_method+=" and chrome passed"],
["wrong cms modification",a=>a.cms.modified="2026-11-09"],
["extra CMS grant",a=>a.cms.published_to_wp=true],
["falsified image count",a=>a.cms.total_inline_images=8],
["swap slot source",a=>a.rows[0].published_src=a.rows[1].published_src],
["alter source alt",a=>a.rows[1].alt="Unknown scene"],
["missing slot",a=>a.rows.pop()],
["duplicate slot",a=>a.rows[3].slot="285:0"],
["unexpected slot",a=>a.rows[3].slot="285:5"],
["fake tool success for 403",a=>a.rows[0].web_retriever.observation="RENDERED_VIA_WEB_RETRIEVER"],
["fake origin HTTP",a=>a.rows[0].web_retriever.origin_http=403],
["fake guest 404",a=>a.rows[0].web_retriever.guest_http=404],
["fake natural width",a=>a.rows[1].web_retriever.guest_natural_width=960],
["fake transferred bytes",a=>a.rows[1].web_retriever.guest_wire_bytes=1024],
["wrong rights",a=>a.rows[3].archival_candidate.rights="CLEAR_TO_REHOST"],
["wrong NRC catalog",a=>a.rows[3].archival_candidate.official_catalog_url="https://nrc.gov/not-this-photo"],
["wrong Commons file",a=>a.rows[3].archival_candidate.commons_catalog_url="https://commons.wikimedia.org/wiki/File:Another.png"],
["fabricated dimensions",a=>a.rows[3].archival_candidate.native_dimensions=[1000,1000]],
["illegal upscale",a=>a.rows[3].archival_candidate.conditional_max_width_960=[1400,2072]],
["remove diagram readability guard",a=>a.rows[3].visual_caution="NONE"],
["invent unmapped candidate",a=>a.rows[0].archival_candidate.official_catalog_url="https://www.nrc.gov/other"],
["invent non-P0 rights",a=>a.rows[1].archival_candidate.rights="PD"],
["mark released",a=>a.rows[2].release="APPROVED"],
["authorize downloads",a=>a.rights_and_release.third_party_binary_downloads=1],
["authorize site write",a=>a.rights_and_release.word_press_writes=1],
["claim 76 pct measured",a=>a.aggregate.sitewide_76_percent_savings_verified=true],
["claim 42 broken",a=>a.aggregate.reported_42_broken_verified=true],
["fake confirmed broken",a=>a.aggregate.confirmed_visitor_broken=1],
["fake wire transfer",a=>a.aggregate.confirmed_wire_bytes=100],
["tamper rendered count",a=>a.aggregate.rendered_by_web_retriever=4],
["inject new source reference",a=>a.source_references.push("https://elsewhere.example/test")],
["null row",a=>a.rows[0]=null],
["null audit",a=>{a.cms=null;}],
];
for(const [name,mut] of mods)ok(name,mut);
console.log(done+"/"+done+" regression checks passed (execute with Node for native validation)");

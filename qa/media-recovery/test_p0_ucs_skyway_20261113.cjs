'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_p0_ucs_skyway_20261113.cjs');
const initial=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_ucs_skyway_20261113.json'),'utf8'));
const changes=[
  [
    "fabricated visitor 404",
    "rows.1.observation.visitor_http",
    404
  ],
  [
    "fake true origin 404",
    "rows.1.observation.origin_http",
    404
  ],
  [
    "invent guest wire size",
    "rows.0.observation.visitor_wire_bytes",
    2000
  ],
  [
    "substitute image",
    "rows.1.original_src",
    "https://example.org/other.jpg"
  ],
  [
    "different WP article",
    "rows.1.post_url",
    "https://finalvestige.com/not-real"
  ],
  [
    "fake original crop parity",
    "rows.1.candidate.original_file_or_crop_proven",
    true
  ],
  [
    "invent native pixels",
    "rows.0.candidate.native_px",
    [
      960,
      700
    ]
  ],
  [
    "rehost without rights",
    "rows.1.candidate.rights_to_rehost_verified",
    true
  ],
  [
    "wrong NRC credit",
    "rows.0.candidate.published_caption_source",
    "Getty"
  ],
  [
    "wrong visual scene",
    "rows.0.candidate.visual_type",
    "AERIAL"
  ],
  [
    "wrong archive ID",
    "rows.1.alternate_florida_archive.id",
    "RC09236"
  ],
  [
    "exact photo mislabel",
    "rows.1.alternate_florida_archive.exact_scene_match",
    true
  ],
  [
    "invent archive image status",
    "rows.1.alternate_florida_archive.http_status",
    200
  ],
  [
    "invent archive image pixels",
    "rows.1.alternate_florida_archive.native_px",
    [
      1200,
      800
    ]
  ],
  [
    "drop archive credit",
    "rows.1.alternate_florida_archive.credit",
    ""
  ],
  [
    "give archive rights to publisher",
    "rights.applies_to_publisher_skyway_photo",
    true
  ],
  [
    "give archive rights to UCS",
    "rights.applies_to_UCS_figure",
    true
  ],
  [
    "permit downloads",
    "release.downloaded_images",
    1
  ],
  [
    "permit WordPress changes",
    "release.staging_or_wordpress_writes",
    true
  ],
  [
    "permit deployment",
    "release.deploy_or_merge",
    true
  ],
  [
    "permit upscaling",
    "release.no_upscale",
    false
  ],
  [
    "fake 42 confirmed",
    "historical.guest_confirmed_broken",
    42
  ],
  [
    "fake 76 percent savings",
    "historical.measured_transfer_reduction_pct",
    76
  ],
  [
    "hijack Site QA collector",
    "siteqa.sole_owner_of_browser_collector",
    false
  ],
  [
    "surprise release permission",
    "release.cache_without_license",
    true
  ],
  [
    "erase browser DPR",
    "siteqa.required.8",
    "unknown"
  ],
  [
    "wrong publisher caption credit",
    "rows.1.candidate.published_caption_source",
    "State Archives"
  ]
];
test('frozen source audit passes HOLD gates',()=>assert.deepEqual(validate(initial),{ok:true,reasons:[]}));
for(const [n,p,v] of changes)test('reject '+n,()=>{const a=JSON.parse(JSON.stringify(initial)),ks=p.split('.');let o=a;for(const k of ks.slice(0,-1))o=o[k];o[ks.at(-1)]=v;assert.equal(validate(a).ok,false,n);});

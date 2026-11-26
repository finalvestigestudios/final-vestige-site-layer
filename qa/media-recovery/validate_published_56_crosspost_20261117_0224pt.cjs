'use strict';
// Offline only; source SHA and post-revision pins; no production actions.
const PINS=[
  {
    "post": 292,
    "path": "qa/media-recovery/prinsendam292_guest_source_custody_20261116_2031pt.json",
    "blob": "55f23c42b7fea5121f96fc0c18e2ff22fcfbdc70",
    "revision": "2026-08-27T11:24:49",
    "images": 6
  },
  {
    "post": 290,
    "path": "qa/media-recovery/campcentury290_six_source_custody_20261116.json",
    "blob": "fac93e43aa5771456ef931d00bbc7fe616195ee4",
    "revision": "2026-11-02T21:40:03",
    "images": 6
  },
  {
    "post": 291,
    "path": "qa/media-recovery/teton291_six_slot_visual_integrity_20261116.json",
    "blob": "4208d801ba0c5484d35f9a069ec35e95c13e4176",
    "revision": "2026-11-02T21:36:09",
    "images": 6
  },
  {
    "post": 285,
    "path": "qa/media-recovery/tmi285_archive_rights_20261116_2327pt.json",
    "blob": "5ff17bb508e8b1ee94c55d88f4e9d8317857c2cc",
    "revision": "2026-11-02T21:39:59",
    "images": 6
  },
  {
    "post": 418,
    "path": "qa/media-recovery/scotchcap_418_six_source_custody_20261116_1930pt.json",
    "blob": "a9e7a81ef01baa12ad381e112d480b01fe49e718",
    "revision": "2026-08-28T03:11:08",
    "images": 6
  },
  {
    "post": 407,
    "path": "qa/media-recovery/hebgen407_usgs_eight_custody_20261116_1830pt.json",
    "blob": "e12ac123ce53516fed1074c582686a3d93d65bed",
    "revision": "2026-10-29T18:30:30",
    "images": 8
  },
  {
    "post": 288,
    "path": "qa/media-recovery/honda_288_navy_20261116_1722pt.json",
    "blob": "00e6dde5cb66adb5f9213cd71e23cba49c9f2d39",
    "revision": "2026-08-19T14:37:40",
    "images": 6
  },
  {
    "post": 434,
    "path": "qa/media-recovery/apollo1_nasa_five_slot_custody_20261116.json",
    "blob": "9d263a474379252c88ce51eb411e08018fa68322",
    "revision": "2026-11-15T12:58:22",
    "images": 5
  },
  {
    "post": 432,
    "path": "qa/media-recovery/okeechobee432_seven_catalog_crosswalk_20261117_0033pt.json",
    "blob": "47266876208505e1efd6b2ca7ce733631728be8f",
    "revision": "2026-08-28T03:07:30",
    "images": 7
  }
];
function host(s){const m=typeof s==="string"?/^https:\/\/([a-z0-9.-]+)(?::443)?(?:[/?#]|$)/i.exec(s):null;return m&&s.length<4096?m[1].toLowerCase():null;}
function check(a,expected){
 const fail=reason=>({ok:false,decision:"HOLD",reason});
 if(!a||a.schema!=="fv-56-published-dependency-v1"||a.method!=="REPROJECTED_PRIOR_WP_EDIT_VIEW_NO_GUEST_BROWSER"||a.siteqa_pr!==154||
 !a.baseline||a.baseline.posts!==61||a.baseline.inline_images!==355||a.baseline.reported_42_guest_confirmed!==false||a.baseline.visitor_76_percent_measured!==false||
 a.baseline.oversized_20_stored_bytes!==64385752||a.baseline.stored_equals_transferred!==false||!a.safe||
 Object.values(a.safe).some(v=>v!==0)||!Array.isArray(a.pins)||a.pins.length!==9||!Array.isArray(a.rows)||a.rows.length!==56)return fail("BASELINE");
 for(let i=0;i<9;i++){const x=a.pins[i],p=expected[i];if(!x||x.post!==p.post||x.path!==p.path||x.blob!==p.blob||x.revision!==p.revision||x.images!==p.images)return fail("PIN");}
 const seen=new Set(),per={};let direct=0,jetpack=0,missing=0,leads=0;
 for(const r of a.rows){
  const p=expected.find(v=>v.post===r?.post);
  if(!p||typeof r.slot!=="string"||!/^[0-9]+:[0-9]+$/.test(r.slot)||!r.slot.startsWith(String(r.post)+":")||seen.has(r.slot)||r.source_blob!==p.blob||r.source_revision!==p.revision)return fail("SLOT");
  seen.add(r.slot);per[r.post]=(per[r.post]||0)+1;
  const h=host(r.published_markup_src);
  if(!h||!host(r.authored_url)||r.host!==h)return fail("URL");
  const isProxy=/^i[0-3]\.wp\.com$/.test(h);
  if(r.delivery!==(isProxy?"JETPACK":"DIRECT"))return fail("DELIVERY");
  if(isProxy)jetpack++;else direct++;
  if(typeof r.explicit_dimensions!=="boolean"||typeof r.srcset!=="boolean"||typeof r.sizes!=="boolean")return fail("GEOMETRY_TYPE");
  if(!r.explicit_dimensions)missing++;
  if(r.catalog_lead!==null){leads++;if(typeof r.catalog_lead!=="string")return fail("CATALOG");}
  if(r.guest_http_status!==null||r.guest_current_src!==null||r.guest_decode!==null||r.guest_mime!==null||r.guest_transfer_bytes!==null||r.guest_screenshot!==null||
  r.identity_approved!==false||r.rights_approved!==false||r.binary_sha256!==null||r.max_width!==960||r.no_upscale!==true||r.cache_authorized!==false||r.wp_write_authorized!==false)return fail("FALSE_EVIDENCE_OR_RIGHTS");
  const want=["285:5","285:2","287:5","418:1","418:2","407:1"].includes(r.slot)?"P0":isProxy?"OTHER":"DIRECT_CHECK";
  if(r.priority!==want)return fail("PRIORITY");
 }
 for(const p of expected)if(per[p.post]!==p.images)return fail("COUNTS");
 const s=a.totals;if(!s||s.posts!==9||s.images!==56||s.jetpack!==jetpack||s.direct!==direct||s.missing_geometry!==missing||s.catalog_leads!==leads||jetpack!==52||direct!==4||missing!==51)return fail("METRICS");
 return {ok:true,decision:"HOLD",posts:9,external_images:56,jetpack,direct,missing_geometry:missing,catalog_leads:leads,guest_status_observations:0,wp_writes:0};
}
const verify=a=>check(a,PINS);
module.exports={verify};
if(require.main===module){const fs=require('node:fs');const f=process.argv[2];if(!f)throw Error('audit JSON required');const o=verify(JSON.parse(fs.readFileSync(f,'utf8')));console.log(JSON.stringify(o,null,2));if(!o.ok)process.exitCode=1;}

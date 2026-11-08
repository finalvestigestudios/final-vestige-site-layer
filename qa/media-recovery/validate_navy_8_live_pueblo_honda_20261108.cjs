'use strict';
/* Read-only evidence validator. Never infers origin HTTP, cached identity, licensing or guest status. */
const EXPECTED={
  "280:0": {
    "post_id": 280,
    "url": "https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/ships-us/ships-usn-p/uss-pueblo-ager-2/428-gx-usn-1129207/_jcr_content/mediaitem/image.img.jpg/1504112093611.jpg",
    "accession": "428-GX-USN-1129207",
    "cat": "https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/ships-us/ships-usn-p/uss-pueblo-ager-2/428-gx-usn-1129207.html",
    "code": 400,
    "outcome": "TIMEOUT_FETCHING",
    "size": 215
  },
  "280:1": {
    "post_id": 280,
    "url": "https://www.history.navy.mil/content/history/nhhc/research/histories/ship-histories/danfs/p/pueblo-iii/_jcr_content/body/media_asset_1086930325/image.img.jpg/1514467381634.jpg",
    "accession": "NH 75559",
    "cat": "https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75559.html",
    "code": 400,
    "outcome": "TIMEOUT_FETCHING",
    "size": 133
  },
  "280:2": {
    "post_id": 280,
    "url": "https://www.history.navy.mil/bin/imageDownload?image=%2Fcontent%2Fdam%2Fnhhc%2Four-collections%2Fphotography%2Fimages%2FNH+75000%2FNH+75561&rendition=cq5dam.web.1280.1280.jpeg",
    "accession": "NH 75561",
    "cat": "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75561.html",
    "code": 400,
    "outcome": "TIMEOUT_FETCHING",
    "size": 152
  },
  "280:3": {
    "post_id": 280,
    "url": "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64683/_jcr_content/mediaitem/image.img.jpg/1459314791691.jpg",
    "accession": "K-64683",
    "cat": "https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64683.html",
    "code": 400,
    "outcome": "TIMEOUT_FETCHING",
    "size": 144
  },
  "280:4": {
    "post_id": 280,
    "url": "https://www.history.navy.mil/content/history/nhhc/research/histories/ship-histories/danfs/b/banner-ii/_jcr_content/body/media_asset/image.img.jpg",
    "accession": null,
    "cat": null,
    "code": null,
    "outcome": "NOT_ACCESSIBLE_IN_TOOL",
    "size": null
  },
  "280:5": {
    "post_id": 280,
    "url": "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64728/_jcr_content/mediaitem/image.img.jpg/1424360116159.jpg",
    "accession": "K-64728",
    "cat": "https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64728.html",
    "code": 400,
    "outcome": "TIMEOUT_FETCHING",
    "size": 124
  },
  "288:0": {
    "post_id": 288,
    "url": "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-69000/NH-69586/_jcr_content/mediaitem/image.img.jpg/1438378291110.jpg",
    "accession": "NH 69586",
    "cat": "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-69000/NH-69586.html",
    "code": 502,
    "outcome": "BAD_GATEWAY",
    "size": 279
  },
  "288:2": {
    "post_id": 288,
    "url": "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/technology/communications/radio/ug-21--us-naval-california-radio-station-collection/mare-island-naval-radio-station/ug-21-01-02-mare-island-naval-radio/jcr%3Acontent/mediaitem/image.img.jpg/1564510769845.jpg",
    "accession": null,
    "cat": null,
    "code": 502,
    "outcome": "BAD_GATEWAY",
    "size": null
  }
};
const KNOWN_OUTCOMES={TIMEOUT_FETCHING:400,BAD_GATEWAY:502,NOT_ACCESSIBLE_IN_TOOL:null};
function validate(a) {
 const errs=[],fail=s=>errs.push(s);
 if(!a||typeof a!=='object'||Array.isArray(a))return ['not_an_audit'];
 if(a.schema!=='fv-navy-eight-pueblo-honda-source-20261108-v1'||a.date_local!=='2026-11-08'||!String(a.methodology||'').includes('NOT origin HTTP'))fail('methodology');
 const c=a.counts||{},r=a.release||{};
 if(c.posts_live_read!==2||c.live_sources_readback!==8||c.web_retriever_nonrender!==8||c.web_retriever_timeout!==5||c.web_retriever_bad_gateway!==2||c.web_retriever_inaccessible!==1||c.verified_catalog_accessions!==6||c.private_courtesy_rights_hold!==1||c.guest_broken_confirmed!==null||c.reported_42_broken_guest_confirmed!==false||c.reported_76_percent_wire_savings_measured!==false||c.oversize_wp_originals_gt_1500000!==15||c.oversize_wp_stored_original_bytes!==47096779)fail('unverified_claim_or_baseline');
 if(r.all_candidates_hold!==true||r.wordpress_writes!==0||r.binary_downloads!==0||r.cached_assets!==0||r.homepage_changes!==0||r.subscription_spend_usd!==0||r.requires_site_qa_browser_verification!==true)fail('release_hold');
 if(a.rights_policy!=='https://www.history.navy.mil/our-collections/photography.html')fail('rights_policy');
 if(!Array.isArray(a.rows)||a.rows.length!==8)return [...new Set([...errs,'eight_rows_required'])];
 const seen=new Set();let catalogCount=0,nonrender=0;
 for(const x of a.rows) {
  const k=x.slot,v=EXPECTED[k],q=x.web_retriever||{},t=x.authoritative_candidate||{},act=x.actions||{};
  if(!v||seen.has(k)){fail('bad_or_duplicate_slot');continue;}seen.add(k);
  if(x.post_id!==v.post_id||!x.post_url?.startsWith('https://finalvestige.com/')||x.live_wp_exact_source_confirmed!==true||!x.post_modified?.startsWith('2026-')||x.published_source_url!==v.url)fail('published_source_identity');
  if(q.date!=='2026-11-08'||q.method!=='web.open'||q.result!==v.outcome||q.tool_error_code!==v.code||KNOWN_OUTCOMES[q.result]!==q.tool_error_code||['http_status_origin','http_status_guest','decoded_px_guest','transfer_bytes_guest','verified_broken_in_guest'].some(f=>q[f]!==null))fail('retriever_not_guest');
  if(t.accession!==v.accession||t.catalog_url!==v.cat||t.medium_1280x1280_catalog_kb!==v.size||t.medium_catalog_size_is_not_measured_wire_bytes!==true||t.original_image_sha256!==null||t.native_dimensions_px!==null||t.derivative_dimensions_px!==null||t.max_derivative_width_px!==960||t.no_upscale!==true||t.attribution_required!==true||t.permission_to_rehost_confirmed!==false||t.editor_release_approval!==false)fail('catalog_or_size_hold');
  if(t.primary_source_match_assurance!==(v.accession?'ACCESSION_AND_SCENE_METADATA_ONLY':'UNVERIFIED'))fail('identity_assurance');
  if(k==='288:0'&&(t.rights_status!=='COURTESY_PRIVATE_COLLECTION_VERIFY_ITEM_RIGHTS'||!String(t.archive_credit||'').includes('Courtesy Naval Historical Foundation')))fail('private_courtesy_rights');
  if(k!=='288:0'&&t.rights_status!=='PENDING_ITEM_LEVEL_RIGHTS_CONFIRMATION')fail('item_level_rights_hold');
  if(['binary_download','cache','wp_media','wp_post','homepage'].some(k=>act[k]!==false))fail('unapproved_writes');
  if(q.result in KNOWN_OUTCOMES)nonrender++;
  if(t.accession)catalogCount++;
 }
 if(seen.size!==8||Object.keys(EXPECTED).some(k=>!seen.has(k)))fail('missing_expected_source');
 if(catalogCount!==6||nonrender!==8)fail('counts_from_rows');
 if(!Array.isArray(a.source_snapshot?.parts)||a.source_snapshot.parts.length!==8||a.source_snapshot.source_posts!==61||a.source_snapshot.source_images!==355||a.source_snapshot.parts.some((x,i)=>x.path!==`qa/media-recovery/parts/0${i+1}.json`||!/^[0-9a-f]{40}$/.test(x.blob_sha||'')))fail('source_snapshot');
 return [...new Set(errs)];
}
module.exports={validate};
if(typeof require==='function'&&require.main===module) {
 const a=JSON.parse(require('node:fs').readFileSync(process.argv[2]||'qa/media-recovery/navy_8_live_pueblo_honda_retriever_20261108.json','utf8'));
 const e=validate(a); if(e.length){console.error('HOLD '+e.join(','));process.exitCode=1;}else console.log('PASS Navy 8 catalog/source identity and rights holds, no guest assertions');
}

'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {validate}=require('./validate_uscg_scotch_cap_418_custody_20261114.cjs');
const audit=require('./uscg_scotch_cap_418_primary_custody_20261114.json');
test('untouched exact-source/rights audit must remain release HOLD',()=>{assert.deepEqual(validate(audit),{state:'VALIDATED_HOLD',errors:[]});});
const cases=[
  [
    "reject renamed post",
    [
      "post",
      "id"
    ],
    419,
    "post_identity"
  ],
  [
    "reject stale modified token",
    [
      "post",
      "modified"
    ],
    "2026-11-14T00:00:00",
    "post_identity"
  ],
  [
    "reject extra source",
    [
      "sources",
      1,
      "slot"
    ],
    "418:1",
    "two_unique_slots"
  ],
  [
    "reject drifted portrait URL",
    [
      "sources",
      0,
      "published_source"
    ],
    "https://example.com/p.jpg",
    "portrait_published_url"
  ],
  [
    "reject false portrait ALT",
    [
      "sources",
      0,
      "published_alt"
    ],
    "Original portrait verified healthy",
    "portrait_published_copy"
  ],
  [
    "reject forged portrait license catalog",
    [
      "sources",
      0,
      "archival_candidate",
      "catalog_url"
    ],
    "https://not-real.test",
    "portrait_primary_catalog"
  ],
  [
    "reject swapped accession",
    [
      "sources",
      0,
      "archival_candidate",
      "identifier"
    ],
    "G-OTHER-2.JPG",
    "portrait_primary_catalog"
  ],
  [
    "reject binary sameness claim",
    [
      "sources",
      0,
      "archival_candidate",
      "binary_hash_verified"
    ],
    true,
    "portrait_exact_VIRIN_not_binary"
  ],
  [
    "reject visual parity claim",
    [
      "sources",
      0,
      "archival_candidate",
      "exact_visual_parity_verified"
    ],
    true,
    "portrait_exact_VIRIN_not_binary"
  ],
  [
    "reject removal of PD item statement",
    [
      "sources",
      0,
      "archival_candidate",
      "publisher_item_public_domain_assertion"
    ],
    false,
    "portrait_item_PD_assertion"
  ],
  [
    "reject omitted DoD restrictions",
    [
      "sources",
      0,
      "archival_candidate",
      "publisher_republish_requires_credit_and_dod_guidance"
    ],
    false,
    "portrait_item_PD_assertion"
  ],
  [
    "reject invented settled surname",
    [
      "sources",
      0,
      "archival_candidate",
      "editorial_name_review"
    ],
    "Verified correct surname",
    "portrait_name_ambiguity"
  ],
  [
    "reject replaced debris source",
    [
      "sources",
      1,
      "published_source"
    ],
    "https://foo/bar.jpg",
    "debris_published_url"
  ],
  [
    "reject made-up debris caption",
    [
      "sources",
      1,
      "published_caption"
    ],
    "No debris",
    "debris_published_copy"
  ],
  [
    "reject museum image rewrite",
    [
      "sources",
      1,
      "archival_candidate",
      "candidate_image_url"
    ],
    "https://example.com/bridge.jpg",
    "debris_museum_catalog"
  ],
  [
    "reject museum presumed PD",
    [
      "sources",
      1,
      "archival_candidate",
      "publisher_item_public_domain_assertion"
    ],
    true,
    "debris_cannot_inherit_PD"
  ],
  [
    "reject claimed museum native dimension",
    [
      "sources",
      1,
      "archival_candidate",
      "actual_native_px"
    ],
    [
      960,
      740
    ],
    "debris_nominal_600px_not_native"
  ],
  [
    "reject false same-image clearance",
    [
      "sources",
      1,
      "archival_candidate",
      "exact_visual_parity_verified"
    ],
    true,
    "debris_identity_HOLD"
  ],
  [
    "reject invented guest status",
    [
      "sources",
      0,
      "guest_http_status"
    ],
    404,
    "visitor_status_unknown:418:1"
  ],
  [
    "reject fabricated origin status",
    [
      "sources",
      1,
      "origin_http_status"
    ],
    403,
    "visitor_status_unknown:418:2"
  ],
  [
    "reject claim wrapper is 200",
    [
      "sources",
      1,
      "external_retriever",
      "wrapper_status"
    ],
    200,
    "wrapper_not_guest:418:2"
  ],
  [
    "reject invented guest transfer",
    [
      "sources",
      0,
      "guest_encoded_transfer_bytes"
    ],
    40712,
    "visitor_status_unknown:418:1"
  ],
  [
    "reject automatic 960 rendition",
    [
      "sources",
      1,
      "archival_candidate",
      "conditional_output_px"
    ],
    [
      960,
      741
    ],
    "no_unapproved_localization:418:2"
  ],
  [
    "reject cache permission",
    [
      "qa_release",
      "allow_image_cache"
    ],
    true,
    "all_release_holds"
  ],
  [
    "reject WP publish permission",
    [
      "qa_release",
      "allow_wordpress_write"
    ],
    true,
    "all_release_holds"
  ],
  [
    "reject immediate merge",
    [
      "qa_release",
      "allow_merge"
    ],
    true,
    "all_release_holds"
  ],
  [
    "reject invented 76 percent proof",
    [
      "historical_baseline",
      "actual_visitor_wire_reduction_pct"
    ],
    76,
    "baseline_not_visitors"
  ],
  [
    "reject signed-off visual parity",
    [
      "qa_release",
      "await_exact_asset_hash_or_visual_comparison"
    ],
    false,
    "all_release_holds"
  ]
];
for(const [name,path,value,reason] of cases)test(name,()=>{
 const c=structuredClone(audit);let o=c;
 for(const seg of path.slice(0,-1))o=o[seg];o[path.at(-1)]=value;
 const result=validate(c);
 assert.equal(result.state,'INVALID');assert.ok(result.errors.includes(reason),JSON.stringify(result));
});

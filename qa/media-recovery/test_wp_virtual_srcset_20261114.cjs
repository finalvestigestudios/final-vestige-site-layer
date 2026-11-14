'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {audit, normalizeUrl, parseSrcset, localDerivativeCandidate} = require('./audit_wp_virtual_srcset_20261114.cjs');
const baseline = JSON.parse(fs.readFileSync(path.join(__dirname, 'draft_2429_virtual_srcset_20261114.json'), 'utf8'));
function edit(mutator) { const d = structuredClone(baseline); mutator(d); return d; }
function rejects(mutator, re) { assert.throws(()=>audit(edit(mutator)),re); }

test('original read-only snapshot: three unadvertised virtual filename uses, not proven 404s',()=>{
  const r=audit(baseline);
  assert.equal(r.verdict,'HOLD_UNVERIFIED_VIRTUAL_FILE_PATH');
  assert.equal(r.flagged_count,3);
  assert.equal(r.inspected_url_count,4);
  assert.equal(r.entries.filter(x=>x.advertised_by_media_api).length,1);
  assert.equal(r.entries.every(x=>x.guest_http_status===null && x.transferred_bytes===null),true);
});
test('matches exact fresh media originals, draft and time-separated cohort counts',()=>{
  const s=baseline.snapshot_reconciliation;
  assert.equal(s.nov_14_oversized_original_storage_bytes,s.nov_8_matched_published_inline_bytes+s.nov_8_unmatched_published_inline_bytes+s.added_asset_after_old_scan_bytes);
  assert.equal(s.nov_14_oversized_originals_decimal_over_1500000,s.nov_8_matched_published_inline_originals+s.nov_8_unmatched_published_inline_originals+1);
  assert.equal(baseline.asset.parent_page_id,baseline.page.id);
  assert.equal(baseline.asset.date.startsWith('2026-11-12'),true);
  assert.equal(baseline.page.status,'draft');
});
test('no inferred 76 percent, 42 browser failures or release authorization',()=>{
  assert.equal(baseline.reported_42_broken_guest_verified,false);
  assert.equal(baseline.reported_76_percent_savings_measured,false);
  assert.equal(baseline.release_authorized,false);
});
test('theoretical 960x540 at 2x serves at most 480 CSS px',()=>{
  assert.deepEqual(baseline.conditional_960px_derivative.dimensions,[960,540]);
  assert.equal(baseline.conditional_960px_derivative.safe_at_css_px_dpr_2_max_width,480);
  assert.equal(baseline.conditional_960px_derivative.verified_existing_asset,false);
});
test('replaced draft source with documented Jetpack URLs still requires guest proof',()=>{
  const d=edit(x=>{
    x.page.images[0].src=x.asset.virtual_renditions[0].url;
    x.page.images[0].srcset=x.asset.virtual_renditions[1].url+' 768w, '+x.asset.virtual_renditions[0].url+' 1024w, '+x.asset.original_url+' 1280w';
  });
  const r=audit(d);
  assert.equal(r.flagged_count,0);
  assert.equal(r.verdict,'HOLD_GUEST_BROWSER_PROOF');
});
test('correctly recognizes WordPress thumbnail filename suffix',()=>{
  assert.equal(localDerivativeCandidate(baseline.asset.original_url,baseline.page.images[0].src),true);
  assert.equal(localDerivativeCandidate(baseline.asset.original_url,baseline.asset.virtual_renditions[0].url),false);
  assert.equal(localDerivativeCandidate(baseline.asset.original_url,baseline.asset.original_url),false);
});
test('rejects non-HTTP src',()=>rejects(x=>x.page.images[0].src='javascript:alert(1)',/Non-HTTP URL/));
test('rejects credential-bearing src',()=>rejects(x=>x.page.images[0].src='https://user:pass@finalvestige.com/test.png',/Credential-bearing URL/));
test('rejects relative image URL',()=>rejects(x=>x.page.images[0].src='/wp-content/img.png',/Invalid URL/));
test('rejects missing src',()=>rejects(x=>x.page.images[0].src='',/URL missing/));
test('rejects malformed width descriptors',()=>rejects(x=>x.page.images[0].srcset='https://example.com/x.png 768h',/Invalid srcset descriptor/));
test('rejects missing srcset',()=>rejects(x=>x.page.images[0].srcset='',/srcset missing/));
test('rejects width > native original',()=>rejects(x=>x.page.images[0].srcset=x.asset.original_url+' 1600w',/Bad width descriptor/));
test('rejects mismatched original width descriptor',()=>rejects(x=>x.page.images[0].srcset=x.asset.original_url+' 960w',/Rendition width mismatch/));
test('rejects duplicated descriptor',()=>rejects(x=>x.page.images[0].srcset=x.asset.original_url+' 1280w, '+x.asset.original_url+' 1280w',/Duplicate URL/));
test('rejects fabricated 404 proof on the guest flag',()=>rejects(x=>x.guest_browser_verified=true,/Invalid release safety/));
test('rejects claimed browser verification of the 42 historical failures',()=>rejects(x=>x.reported_42_broken_guest_verified=true,/False site-wide evidence/));
test('rejects claimed visitor wire savings',()=>rejects(x=>x.reported_76_percent_savings_measured=true,/False site-wide evidence/));
test('rejects release authorization',()=>rejects(x=>x.release_authorized=true,/Invalid release safety/));
test('rejects WordPress write enablement',()=>rejects(x=>x.wp_write_allowed=true,/Invalid release safety/));
test('rejects virtual size that is marked physical',()=>rejects(x=>x.asset.virtual_renditions[0].virtual=false,/Invalid virtual rendition/));
test('rejects wrong virtual CDN host',()=>rejects(x=>x.asset.virtual_renditions[0].url='https://external.example.com/photo.png',/not a documented proxy/));
test('rejects wrong source content geometry',()=>rejects(x=>x.page.images[0].height=576,/Image geometry drift/));
test('rejects removing concept-art editorial disclosure',()=>rejects(x=>x.page.images[0].alt='Products on table',/Image meaning\/disclosure drift/));
test('rejects treating unpublished page as published',()=>rejects(x=>x.page.status='publish',/Unexpected source custody/));
test('rejects identity drift',()=>rejects(x=>x.asset.id=2433,/Unexpected source custody/));
test('rejects original source host substitution',()=>rejects(x=>x.asset.original_url='https://example.com/original.png',/Unexpected original host/));
test('rejects original file size change',()=>rejects(x=>x.asset.original_bytes=0,/Asset metadata drift/));
test('rejects duplicate virtual renditions',()=>rejects(x=>x.asset.virtual_renditions.push(structuredClone(x.asset.virtual_renditions[0])),/Duplicate rendition URL/));
test('does not mistake unknown HTTP for a confirmed failure',()=>{
  const r=audit(baseline); assert.ok(r.entries.every(e=>e.guest_http_status===null && !('http_404' in e)));
});
test('individual srcset URLs are parsed with widths',()=>{
  const e=parseSrcset(baseline.page.images[0].srcset);
  assert.deepEqual(e.map(x=>x.width),[768,1024,1280]);
});
test('rejects asset deletion inference from old scan',()=>rejects(x=>x.snapshot_reconciliation.no_inference_of_unused_or_deletable_assets=false,/Temporal media inventory mismatch/));
test('rejects inflated stored original bytes',()=>rejects(x=>x.snapshot_reconciliation.nov_14_oversized_original_storage_bytes+=1,/Temporal media inventory mismatch/));
test('rejects downloadable external binaries',()=>rejects(x=>x.third_party_asset_download_allowed=true,/Disallowed operations/));
test('rejects homepage design changes',()=>rejects(x=>x.homepage_design_changes_allowed=true,/Disallowed operations/));
test('rejects subscription spend',()=>rejects(x=>x.subscription_spend_usd=1,/Disallowed operations/));

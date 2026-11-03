'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {load,validateLedger}=require('./validate_camp_century_290_20261102.cjs');
function ctx(){const {ledger,source,raw}=load();return {ledger:JSON.parse(JSON.stringify(ledger)),source,raw};}
test('live-readback six image source census and rights-HOLD positive attestation',()=>{
 const {ledger,source,raw}=ctx();
 assert.deepEqual(validateLedger(ledger,source,raw),[]);
 assert.equal(ledger.rows.length,6);
 assert.equal(ledger.rows[2].dimensions.conditional_derivative_px.width,960);
 assert.equal(ledger.rows[2].dimensions.conditional_derivative_px.height,691);
});
const mutations=[
 ['source URL substituted',l=>l.rows[0].exact_published_source_url+='?wrong=1'],
 ['source ALT substituted',l=>l.rows[1].exact_published_alt='different caption'],
 ['image key duplicated',l=>l.rows[1].image_key=l.rows[0].image_key],
 ['wrong post ID',l=>l.rows[2].post_id=285],
 ['five rows only',l=>l.rows.pop()],
 ['tool timeout forged into 404',l=>l.rows[3].independent_retriever.origin_http_status=404],
 ['retriever wrapper invented 403',l=>l.rows[5].independent_retriever.visitor_http_status=403],
 ['image display mislabeled guest status',l=>l.rows[0].actual_visitor_browser.http_status=200],
 ['fake natural width',l=>l.rows[0].actual_visitor_browser.natural_width_px=960],
 ['fabricated transfer bytes',l=>l.rows[1].actual_visitor_browser.transfer_bytes=15000],
 ['fake site-wide 42 verified',l=>l.sitewide_context.alleged_broken_verified=true],
 ['fake 76 percent measured',l=>l.sitewide_context.claimed_reduction_measured=true],
 ['early WordPress edit authorization',l=>l.rows[3].release_gates.wordPress_edit_authorized=true],
 ['early media upload authorization',l=>l.rows[2].authoritative_recovery_candidate.wordPress_media_upload_authorized=true],
 ['guessed original dimensions',l=>l.rows[3].dimensions.conditional_derivative_px={width:960,height:600}],
 ['upsampling a catalog source',l=>l.rows[2].dimensions.conditional_derivative_px.width=1580],
 ['cropping off figure key',l=>l.rows[2].dimensions.preserve_full_image_no_crop=false],
 ['untrue original pixel height',l=>l.rows[2].dimensions.catalog_original_px.height=600],
 ['dropping thermal drill finding',l=>l.rows[4].proposed_alt_review=null],
 ['marking inaccurate ALT corrected',l=>l.rows[4].proposed_alt_review.status='PUBLISHED'],
 ['journal figure automatically inherits CC0',l=>l.rows[5].authoritative_recovery_candidate.kind='same_file_cc0'],
 ['stale archived post',l=>l.source_attestation.modified='2026-11-02T00:00:00'],
 ['invented browser-breakage count',l=>l.counts.actual_guest_browser_confirmed_broken=42],
 ['invented published media changes',l=>l.counts.published_edits=1],
 ['rights prematurely cleared',l=>l.rows[4].authoritative_recovery_candidate.item_specific_rights_review='APPROVED'],
 ['incorrect retriever classification',l=>l.rows[4].independent_retriever.observation='RETRIEVER_FETCH_404'],
];
for(const [name,mutate] of mutations)test('fail closed: '+name,()=>{
 const {ledger,source,raw}=ctx();mutate(ledger);
 assert.notDeepEqual(validateLedger(ledger,source,raw),[],name);
});
test('reject altered archived frozen source',()=>{
 const {ledger,source,raw}=ctx();const altered=Buffer.from(raw);
 altered[altered.length-1]=altered[altered.length-1]===10?32:10;
 assert.ok(validateLedger(ledger,source,altered).includes('source_part_sha_mismatch'));
});

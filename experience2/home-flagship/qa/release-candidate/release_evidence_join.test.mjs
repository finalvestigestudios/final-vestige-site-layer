import test from 'node:test';
import assert from 'node:assert/strict';
import {classifyReleaseEvidence, STAGE_WIDTHS, GUEST_WIDTHS,
  REQUIRED_STAGE_CHECKS, REQUIRED_NOJS_CHECKS, REQUIRED_GUEST_CHECKS} from './release_evidence_join.mjs';
const HEAD='6'.repeat(40);
function good(){
  const img={status:'PASS',failure_codes:[], decoded_payload_total_bytes:120000,
    images:[{archive:'apollo',http_status:200,response_seen:true,
      decoded_payload_bytes:40000,payload_sha256:'a'.repeat(64),
      detected_raster_format:'webp',content_type:'image/webp'},
    {archive:'franklin',http_status:200,response_seen:true,
      decoded_payload_bytes:80000,payload_sha256:'b'.repeat(64),
      detected_raster_format:'jpeg',content_type:'image/jpeg'}]};
  const viewports=STAGE_WIDTHS.map(width=>({
    width,checks:Object.fromEntries(REQUIRED_STAGE_CHECKS.map(k=>[k,true])),
    axe:{status:'RUN',violations:[]},image_http_delivery:img
  }));
  return {
    sha:HEAD,
    stage:{source_git_head:HEAD,status:'HOLD_INDEPENDENT_RELEASE_APPROVAL_REQUIRED',
      pass_for_measured_browser_gates:true, failure_codes:[], production_mutations:0,
      viewports, no_javascript:{checks:Object.fromEntries(REQUIRED_NOJS_CHECKS.map(k=>[k,true]))}},
    local:{status:'ISOLATED_BROWSER_AND_LAB_ADMISSION_PASSED_NOT_RELEASE',
      public_wordpress_writes:false,wordpress_com_host_parity:'NOT_ESTABLISHED'},
    lighthouse:{status:'ISOLATED_AUTHENTICATED_WORDPRESS_LIGHTHOUSE_MEASURED_NOT_RELEASE',
      exact_source_commit:HEAD, public_wordpress_writes:false, laboratory_only:true,
      field_cwv_p75:'NOT_MEASURED',
      audit_profiles:['mobile_390','desktop_1440'].map(profile=>({
        profile, scores_0_to_100:{performance:97,accessibility:100,best_practices:100},
        laboratory_metrics:{lcp_ms:2100,cls:0,fcp_ms:400,tbt_ms:10}
      }))},
    usability:{exact_source_commit:HEAD,status:'ISOLATED_WORDPRESS_KEYBOARD_TOUCH_REFLOW_PASS_NOT_WCAG_CERTIFIED',
      production_writes:false,failure_codes:[]},
    guest:{url:'https://finalvestige.com/focus/',
      results:GUEST_WIDTHS.map(width=>({width,pass:true,
        checks:Object.fromEntries(REQUIRED_GUEST_CHECKS.map(k=>[k,true])),
        markers:{guest_email_form:true,email_is_empty:true}}))},
    guestAgeHours:1
  };
}
test('complete evidence is still RELEASE HOLD, never commerce or WCAG certified',()=>{
  const r=classifyReleaseEvidence(good());
  assert.equal(r.lab_evidence_satisfied,true);
  assert.equal(r.classification,'LOCAL_WORDPRESS_AND_GUEST_LAB_EVIDENCE_COMPLETE_NOT_RELEASE');
  assert.equal(r.release,'HOLD');
  assert.equal(r.verified_paid_orders,'NOT_MEASURED');
  assert.equal(r.net_revenue_per_1000_qualified_sessions,'NOT_COMPUTABLE');
  assert.ok(r.independent_release_gates_still_required.length>=5);
});
const mutations=[
  ['wrong SHA',x=>{x.sha='invalid';},'EXPECTED_SHA_INVALID'],
  ['stale staging SHA',x=>{x.stage.source_git_head='a'.repeat(40);},'STAGE_EXACT_SHA_MISMATCH'],
  ['staging lost pass',x=>{x.stage.pass_for_measured_browser_gates=false;},'STAGE_BROWSER_ADMISSION_HOLD'],
  ['staging admitted production mutations',x=>{x.stage.production_mutations=1;},'STAGE_BROWSER_ADMISSION_HOLD'],
  ['missing width',x=>{x.stage.viewports.pop();},'STAGE_WIDTH_SET_MISSING'],
  ['failing WordPress check',x=>{x.stage.viewports[0].checks.all_seven_chapters=false;},'STAGE_CHECKS_FAIL_360'],
  ['axe unavailable',x=>{x.stage.viewports[1].axe.status='NOT_RUN';},'STAGE_AXE_NOT_ZERO_390'],
  ['axe violation',x=>{x.stage.viewports[2].axe.violations=[{id:'color-contrast'}];},'STAGE_AXE_NOT_ZERO_768'],
  ['media only metadata',x=>{x.stage.viewports[3].image_http_delivery.status='NOT_MEASURED';},'STAGE_REAL_IMAGE_TRANSFER_HOLD_1440'],
  ['noJS broken',x=>{x.stage.no_javascript.checks.all_chapters=false;},'STAGE_NOJS_MEANING_HOLD'],
  ['old local runner absent',x=>{x.local.status='UNKNOWN';},'LOCAL_WORDPRESS_RUN_HOLD'],
  ['local runner claimed hosted',x=>{x.local.wordpress_com_host_parity='VERIFIED';},'LOCAL_WORDPRESS_RUN_HOLD'],
  ['lighthouse stale SHA',x=>{x.lighthouse.exact_source_commit='b'.repeat(40);},'LIGHTHOUSE_SHA_LAB_RECEIPT_HOLD'],
  ['lighthouse not lab only',x=>{x.lighthouse.laboratory_only=false;},'LIGHTHOUSE_SHA_LAB_RECEIPT_HOLD'],
  ['lighthouse profile omitted',x=>{x.lighthouse.audit_profiles.pop();},'LIGHTHOUSE_MEASURED_PROFILES_MISSING'],
  ['lighthouse fake score',x=>{x.lighthouse.audit_profiles[0].scores_0_to_100.performance=120;},'LIGHTHOUSE_MEASURED_PROFILES_MISSING'],
  ['lighthouse no LCP',x=>{x.lighthouse.audit_profiles[0].laboratory_metrics.lcp_ms=null;},'LIGHTHOUSE_MEASURED_PROFILES_MISSING'],
  ['usability stale SHA',x=>{x.usability.exact_source_commit='c'.repeat(40);},'REAL_WORDPRESS_USABILITY_HOLD'],
  ['usability failure',x=>{x.usability.failure_codes=['TAB_ORDER'];},'REAL_WORDPRESS_USABILITY_HOLD'],
  ['guest synthetic',x=>{x.guest.url='offline synthetic fixture';},'ANONYMOUS_FOCUS_GUEST_RENDER_HOLD'],
  ['guest missing form',x=>{x.guest.results[0].markers.guest_email_form=false;},'ANONYMOUS_FOCUS_GUEST_RENDER_HOLD'],
  ['guest wrong widths',x=>{x.guest.results[0].width=600;},'ANONYMOUS_FOCUS_GUEST_RENDER_HOLD'],
  ['guest broken label',x=>{x.guest.results[2].checks.labelled_email=false;},'ANONYMOUS_FOCUS_GUEST_RENDER_HOLD'],
  ['guest failure result',x=>{x.guest.results[3].pass=false;},'ANONYMOUS_FOCUS_GUEST_RENDER_HOLD'],
  ['guest evidence older than 24h',x=>{x.guestAgeHours=49;},'ANONYMOUS_GUEST_EVIDENCE_STALE_OR_UNDATED'],
  ['guest evidence from future',x=>{x.guestAgeHours=-1;},'ANONYMOUS_GUEST_EVIDENCE_STALE_OR_UNDATED'],
  ['guest evidence time unknown',x=>{delete x.guestAgeHours;},'ANONYMOUS_GUEST_EVIDENCE_STALE_OR_UNDATED'],
];
for(const [name,change,code] of mutations){
  test('fail-closed: '+name,()=>{
    const x=good();change(x);
    const r=classifyReleaseEvidence(x);
    assert.equal(r.release,'HOLD',name);
    assert.equal(r.lab_evidence_satisfied,false,name);
    assert.ok(r.failure_codes.includes(code),name+': '+JSON.stringify(r.failure_codes));
  });
}

// Verify the real producers' schema, not arbitrary optimistic boolean labels.
const forgeryMutations=[
  ['stage generic true-only record',x=>{x.stage.viewports[0].checks={success:true};},'STAGE_CHECKS_FAIL_360'],
  ['no-JS generic true-only record',x=>{x.stage.no_javascript.checks={looks_ok:true};},'STAGE_NOJS_MEANING_HOLD'],
  ['media status PASS with no network receipts',x=>{x.stage.viewports[1].image_http_delivery={status:'PASS'};},'STAGE_REAL_IMAGE_TRANSFER_HOLD_390'],
  ['media zero bytes',x=>{x.stage.viewports[2].image_http_delivery.images[0].decoded_payload_bytes=0;},'STAGE_REAL_IMAGE_TRANSFER_HOLD_768'],
  ['media duplicate body hash',x=>{x.stage.viewports[3].image_http_delivery.images[1].payload_sha256='a'.repeat(64);},'STAGE_REAL_IMAGE_TRANSFER_HOLD_1440'],
  ['media totals disagree',x=>{x.stage.viewports[4].image_http_delivery.decoded_payload_total_bytes=1;},'STAGE_REAL_IMAGE_TRANSFER_HOLD_1920'],
  ['media bad HTTP status',x=>{x.stage.viewports[0].image_http_delivery.images[0].http_status=404;},'STAGE_REAL_IMAGE_TRANSFER_HOLD_360'],
  ['guest generic true-only record',x=>{x.guest.results[1].checks={all_ok:true};},'ANONYMOUS_FOCUS_GUEST_RENDER_HOLD'],
];
for(const [name,change,code] of forgeryMutations) {
  test('reject incomplete producer receipt: '+name,()=>{
    const x=good();change(x);
    const r=classifyReleaseEvidence(x);
    assert.equal(r.lab_evidence_satisfied,false,name);
    assert.ok(r.failure_codes.includes(code),name+': '+JSON.stringify(r.failure_codes));
    assert.equal(r.release,'HOLD');
  });
}

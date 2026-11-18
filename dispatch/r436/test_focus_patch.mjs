import test from 'node:test';
import assert from 'node:assert/strict';
import {LIVE_MODIFIED, OLD_PANEL, NEW_PANEL, OLD_SCRIPT, proposeFocusPatch} from './focus_patch.mjs';
const FORM = '<!-- wp:jetpack/subscriptions {"showSubscribersTotal":false,"successMessage":"Check your email to confirm your subscription."} /-->';
const fixture = '<!-- wp:group --><p id="before">Preserve me</p>'+FORM+
  '<!-- wp:html --><div class="fvf-hero-after">\n  '+OLD_PANEL+
  '\n</div><!-- /wp:html --><p id="after">Keep this exact.</p><!-- wp:html -->'+OLD_SCRIPT+'<!-- /wp:html -->';
const render = (body=fixture, version=LIVE_MODIFIED)=>proposeFocusPatch(body,version);

test('one exact WordPress snapshot yields an explicitly unpublishable proposal',()=>{
  const p=render();
  assert.equal(p.readyToPublish,false);
  assert.equal(p.sourceModified,LIVE_MODIFIED);
  assert.equal(p.changedElements.length,4);
});
test('free PDF is visible without subscriber state',()=>{
  const p=render().content;
  assert.ok(p.includes(NEW_PANEL));
  assert.ok(!p.includes('class="fvf-gift" hidden'));
  assert.ok(p.includes('role="region" aria-labelledby="fvf-gift-title"'));
  assert.ok(p.includes('id="fvf-gift-title"'));
});
test('no arbitrary subscribe token or Jetpack class controls download',()=>{
  const p=render().content;
  for(const banned of ['URLSearchParams','is-subscriber','MutationObserver','fvf-gift-v2','window.location.search'])
    assert.ok(!p.includes(banned),banned);
});
test('download events remain distinguishable from verified leads',()=>{
  const p=render().content;
  assert.equal(p.match(/data-fv-event="focus_pdf_click"/g)?.length,1);
  assert.ok(p.includes('data-fv-location="public_fieldbook"'));
  assert.ok(!p.includes('data-fv-location="after_signup"'));
  assert.ok(!p.includes('data-fv-event="confirmed_signup"'));
  assert.ok(p.includes('A PDF download is not a confirmed newsletter subscription.'));
});
test('non-affiliate file and Jetpack signup block are unchanged',()=>{
  const p=render().content;
  assert.ok(p.includes('Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf'));
  assert.ok(p.includes(FORM));
  assert.ok(p.includes('<p id="before">Preserve me</p>'));
  assert.ok(p.includes('<p id="after">Keep this exact.</p>'));
});
test('does not create send, tracking, subscriber or commerce controls',()=>{
  const p=render().content;
  for (const banned of ['fetch(', 'XMLHttpRequest','sendBeacon','pixel.gif','affiliate_id','utm_campaign=','email_new_posts_by_default=true'])
    assert.ok(!p.includes(banned),banned);
});
test('only the two intended substrings are replaced',()=>{
  const p=render().content;
  const expected=fixture.replace(OLD_PANEL,NEW_PANEL).replace(OLD_SCRIPT,'');
  assert.equal(p,expected);
});
test('reject stale WordPress modified date',()=>assert.throws(()=>render(fixture,'2026-11-17T01:00:00'),/STALE_WORDPRESS_VERSION/));
test('reject missing/short source',()=>{
  assert.throws(()=>render(''),/SOURCE_REQUIRED/);
  assert.throws(()=>render(null),/SOURCE_REQUIRED/);
});
test('reject missing Jetpack form',()=>assert.throws(()=>render(fixture.replace(FORM,'')),/JETPACK_FORM_MISSING/));
test('reject duplicate gift panel',()=>assert.throws(()=>render(fixture+OLD_PANEL),/EXPECTED_PANEL_NOT_UNIQUE/));
test('reject missing gift panel',()=>assert.throws(()=>render(fixture.replace(OLD_PANEL,'')),/EXPECTED_PANEL_NOT_UNIQUE/));
test('reject duplicate script',()=>assert.throws(()=>render(fixture+OLD_SCRIPT),/EXPECTED_SCRIPT_NOT_UNIQUE/));
test('reject missing script',()=>assert.throws(()=>render(fixture.replace(OLD_SCRIPT,'')),/EXPECTED_SCRIPT_NOT_UNIQUE/));
test('reject already-modified version',()=>assert.throws(()=>render(fixture.replace(OLD_PANEL,NEW_PANEL)),/EXPECTED_PANEL_NOT_UNIQUE/));
test('synthetic URL and subscriber-class manipulations never influence output',()=>{
  const correct=render().content;
  for(const token of ['success','confirmed','1','invalid_email','blocked','opted_out','UNKNOWN','is-subscriber']){
    assert.equal(render().content, correct,token);
    assert.ok(!correct.includes("get('subscribe')"));
  }
});
test('source intentionally includes NO grant of final campaign approval',()=>{
  assert.equal(render().readyToPublish,false);
  assert.ok(!NEW_PANEL.includes('successfully subscribed'));
  assert.ok(!NEW_PANEL.includes('you are confirmed'));
  assert.ok(NEW_PANEL.includes('The Dispatch is optional'));
});

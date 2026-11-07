#!/usr/bin/env node
/** FV /focus/ signal-integrity audit: replay a pinned, public-page script in a
 * local Node sandbox. NO external request, form submission, or real subscriber.
 * A visible gift is a UX state, NEVER verified Jetpack subscriber acquisition.
 */
import fs from 'node:fs';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { runInNewContext } from 'node:vm';

const fixture = JSON.parse(fs.readFileSync(new URL('./focus_gift_source_20261107.json', import.meta.url),'utf8'));
const hash = createHash('sha256').update(fixture.script).digest('hex');
const expectedHash = 'f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7';
if (hash !== expectedHash || fixture.page_id !== 1579 ||
    fixture.modified !== '2026-11-05T17:44:02' ||
    !fixture.script.includes('new URLSearchParams(window.location.search)')) {
  throw Error('WordPress Focus source has drifted: REVIEW REQUIRED; no pass');
}

function simulate({search='', className='', executeScript=true, mutateClass=''}={}) {
  const gift={hidden:true}, container={className};
  let observerCallback=null;
  class MutationObserverStub {
    constructor(callback){observerCallback=callback;}
    observe(){}
  }
  const document={
    getElementById:id=>id==='fvf-gift'?gift:null,
    querySelector:s=>s==='.wp-block-jetpack-subscriptions__container'?container:null,
  };
  const window={location:{search},MutationObserver:MutationObserverStub};
  if(executeScript){
    runInNewContext(fixture.script,{document,window,MutationObserver:MutationObserverStub,URLSearchParams});
  }
  if(mutateClass){container.className=mutateClass;observerCallback?.();}
  return {gift_visible:!gift.hidden, form_submitted:false, confirmed_lead:false};
}

const cases=[
  ['plain visit',{search:''},false],
  ['unrecognized query value without a form',{search:'?subscribe=made_up_value'},true],
  ['known rejected query value',{search:'?subscribe=invalid_email'},false],
  ['other rejected query value',{search:'?subscribe=blocked'},false],
  ['subscriber-class state, no form submission',{className:'wp-block-jetpack-subscriptions__container is-subscriber'},true],
  ['class mutation to subscriber without a form',{className:'wp-block-jetpack-subscriptions__container',mutateClass:'is-subscriber'},true],
  ['no-JS with unrecognized query value',{search:'?subscribe=made_up_value',executeScript:false},false],
];
let failures=[];
const observations=cases.map(([name,args,expected])=>{
  const state=simulate(args);
  if(state.gift_visible!==expected)failures.push(name);
  return {scenario:name,gift_visible:state.gift_visible,
    submitted_form:false,independently_confirmed_subscriber:false};
});
assert.equal(failures.length,0,JSON.stringify(failures));
assert.equal(observations.some(x=>x.gift_visible&&!x.independently_confirmed_subscriber),true);
const output={
  fixture:{page_id:fixture.page_id,modified:fixture.modified,script_sha256:hash},
  scope:'Exact public WordPress source snippet in local sandbox; NOT browser, WordPress runtime or Jetpack',
  executed_cases:observations.length,passed:observations.length,failed:failures.length,
  observations,
  finding:'Visible PDF gift state can be induced by an arbitrary subscribe query string without signup or confirmation. DOM gift visibility must never count as a subscriber, purchase or other commercial conversion.',
  decision:'ATTRIBUTION_HOLD_PENDING_CLAUDE_REVIEW',
  cms_writes:0,forms_submitted:0,external_requests:0
};
console.log(JSON.stringify(output,null,2));

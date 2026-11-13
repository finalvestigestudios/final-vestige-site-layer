import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {liveFocusGiftV2} from './live_focus_gift_fixture.mjs';
function inspect(query,widgetClass=''){
 const gift={hidden:true};
 const document={getElementById:id=>id==='fvf-gift'?gift:null,
  querySelector:()=>({className:widgetClass})};
 const window={location:{search:query},MutationObserver:null};
 vm.runInNewContext(liveFocusGiftV2,{document,window,URLSearchParams});
 return gift.hidden;
}
test('current source hides gift with no param/class',()=>assert.equal(inspect(''),true));
test('untrusted ?subscribe=arbitrary reveals gift without any provider proof',()=>{
 assert.equal(inspect('?subscribe=arbitrary'),false);
 assert.equal(inspect('?subscribe=not-a-confirmation'),false);
});
test('blocked error value prevents reveal',()=>{
 for(const q of ['invalid_email','error','blocked_email','opted_out','blocked'])
  assert.equal(inspect('?subscribe='+q),true);
});
test('widget CSS class independently reveals gift (UI only)',()=>{
 assert.equal(inspect('', 'widget is-subscriber'),false);
});
test('fixture is NOT a signed-up, confirmed or welcome-delivered proof',()=>{
 assert.match(liveFocusGiftV2,/URLSearchParams/);
 assert.doesNotMatch(liveFocusGiftV2,/confirmed_signup|email_delivery_eligible|welcome_received/);
});

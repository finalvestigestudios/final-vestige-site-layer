import test from 'node:test';
import assert from 'node:assert/strict';
import {runInNewContext} from 'node:vm';
import {readFileSync} from 'node:fs';
const live = readFileSync(new URL('../focus_live_js_excerpt.txt', import.meta.url),'utf8');
function simulate(search = '', className = '') {
  const gift = {hidden:true};
  const container = className ? {className} : null;
  const document = {getElementById:()=>gift, querySelector:()=>container};
  const window = {location:{search}};
  runInNewContext(live,{document,window,URLSearchParams});
  return gift.hidden === false;
}
test('LIVE CODE: arbitrary subscribe query reveals gift panel',()=>assert.equal(simulate('?subscribe=not_real_confirmation'),true));
test('LIVE CODE: some explicit denied query values do not reveal gift',()=>assert.equal(simulate('?subscribe=blocked'),false));
test('LIVE CODE: no query and no WP class leaves gift hidden',()=>assert.equal(simulate(),false));
test('LIVE CODE: is-subscriber class reveals gift without email eligibility evidence',()=>assert.equal(simulate('', 'wp-block-jetpack-subscriptions__container is-subscriber'),true));
test('LIVE CODE: another arbitrary truthy string also reveals gift',()=>assert.equal(simulate('?subscribe=anything_at_all'),true));

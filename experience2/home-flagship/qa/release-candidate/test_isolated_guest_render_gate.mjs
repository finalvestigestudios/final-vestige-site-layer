import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {safeLocalUrl,isCookieFreeGuest,phpGuestCopy,phpGuestDelete,validateGuestReceipt}
  from './isolated_guest_render_gate.mjs';

test('loopback host and same port required; production/external/credentials denied',()=>{
  for(const a of ['http://localhost:9473/','http://127.0.0.1:9473/?page_id=52'])
    assert.equal(safeLocalUrl(a,'http://localhost:9473/'),true,a);
  for(const a of ['https://finalvestige.com/','https://localhost:9473/',
    'http://localhost:9474/','http://localhost.evil.test:9473/',
    'http://localhost:9473@evil.test/','http://test:abc@localhost:9473/',
    'file:///tmp/sneaky','http://localhost/'])
    assert.equal(safeLocalUrl(a,'http://localhost:9473/'),false,a);
});
test('new anonymous context rejects WordPress logged-in credentials',()=>{
  assert.ok(isCookieFreeGuest([]));
  assert.ok(isCookieFreeGuest([{name:'wp_test_cookie'}]));
  for(const prefix of ['wordpress_logged_in_','wordpress_sec_','wp-settings-'])
    assert.equal(isCookieFreeGuest([{name:prefix+'abc'}]),false);
  assert.equal(isCookieFreeGuest(null),false);
});
test('PHP local creator validates WordPress and saved Gutenberg source before publish',()=>{
  const php=phpGuestCopy(123);
  const markers=["home_url('/')","get_stylesheet()!=='assembler'",
    'is_multisite()','get_post($id)',"$draft->post_status!=='draft'",
    "'FV EX2 SYNTHETIC EDITOR SAVED'",'data-fv-home-flagship',
    '72 published historical fragments in isolated review','data-fv-source=',
    'jetpack/subscriptions',"hash('sha256',$content)"];
  const write=php.indexOf('$copy=wp_insert_post(');
  assert.ok(write>0);
  for(const x of markers){assert.ok(php.includes(x));assert.ok(php.indexOf(x)<write,'Guard must precede write: '+x);}
  for(const k of ["'post_status'=>'publish'","'ping_status'=>'closed'",
    "'comment_status'=>'closed'","'to_ping'=>''","'pinged'=>''",
    "hash('sha256',$created->post_content)!==$source_sha","wp_delete_post($copy,true)"])
    assert.ok(php.includes(k),'Absent '+k);
  for(const text of ['finalvestige.com','wp_remote_post','wp_remote_get','subscriber'])
    assert.ok(!php.includes(text),'No prod/domain/network/user data: '+text);
});
test('copy deletion fails closed for arbitrary post before deleting',()=>{
  const php=phpGuestDelete(21);
  assert.ok(php.indexOf("str_starts_with($p->post_title,'EX2 ANONYMOUS LOCAL REVIEW')")<php.indexOf('wp_delete_post($id,true)'));
  assert.ok(php.includes('get_stylesheet()!==\'assembler\''));
  assert.ok(php.includes('get_post($id)===null'));
});
test('receipt must match draft, SHA and isolated copy URL',()=>{
  const base={type:'EPHEMERAL_LOOPBACK_ANONYMOUS_COPY',copy_id:3,
    source_draft_id:123,source_sha256:'a'.repeat(64),copy_sha256:'a'.repeat(64),
    url:'http://localhost:9473/?page_id=3',release:'HOLD'};
  assert.equal(validateGuestReceipt(base,123,'http://localhost:9473/'),base);
  for(const m of [{source_draft_id:45},{copy_sha256:'b'.repeat(64)},
      {url:'https://finalvestige.com/'},{copy_id:0},{release:'LIVE'},
      {source_sha256:'xyz'}]) assert.throws(()=>validateGuestReceipt({...base,...m},123,'http://localhost:9473/'));
});
test('both inlined PHP scripts lint without a WordPress runtime',()=>{
  for(const php of [phpGuestCopy(123),phpGuestDelete(123)]){
    const r=spawnSync('php',['-l'],{input:php,encoding:'utf8',timeout:10000});
    assert.equal(r.status,0,r.stderr||r.stdout||String(r.error));
  }
});

test('source browser gate checks unobstructed first-screen target and keyboard focus path',async()=>{
  const fs=await import('node:fs/promises');
  const source=await fs.readFile(new URL('./isolated_guest_render_gate.mjs',import.meta.url),'utf8');
  for(const marker of ['document.elementFromPoint','cta.contains(pointed)',
      'box.bottom<=innerHeight','box.width>=44','box.height>=44',
      "page.keyboard.press('Tab')","'#fv-hf-title'",
      'full-document axe']) {
    // axe is checked by a separate whole-document violation evaluation.
    if(marker==='full-document axe')assert.ok(source.includes('window.axe.run(document'));
    else assert.ok(source.includes(marker),'Missing browser admission: '+marker);
  }
});

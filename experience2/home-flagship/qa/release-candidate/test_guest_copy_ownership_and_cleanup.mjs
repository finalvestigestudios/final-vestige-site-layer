#!/usr/bin/env node
/** Offline, non-production security gate for the anonymous Assembler review copy.
 * Run: node --test experience2/home-flagship/qa/release-candidate/test_guest_copy_ownership_and_cleanup.mjs
 * PHP is required for syntax verification; never calls a server or creates a WP page.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {phpGuestCopy,phpGuestDelete} from './isolated_guest_render_gate.mjs';

const source=await readFile(new URL('./isolated_guest_render_gate.mjs',import.meta.url),'utf8');
const validId=41;
const creation=phpGuestCopy(validId);
const cleanup=phpGuestDelete(null);
const specificCleanup=phpGuestDelete(validId);
const requireTokens=(source,tokens)=>{
  for(const token of tokens)assert.ok(source.includes(token),'Missing safety invariant: '+token);
};
function copyInvariants(php){
  requireTokens(php,[
    "'/tmp/fv-ex2-synthetic-only.marker'",
    "'/tmp/fv-ex2-editor-token'",
    "'/tmp/fv-ex2-guest-copy-id'",
    "'SYNTHETIC_TEST_FIXTURE_ONLY'",
    "'_fv_ex2_editor_qa_owner'",
    "hash_equals(hash_hmac('sha256',(string)$id,$token),$owner)",
    "wp_set_current_user((int)$admins[0]->ID)",
    "current_user_can('unfiltered_html')",
    "'post_content'=>wp_slash($content)",
    "hash_hmac('sha256','guest:'.(string)$copy,$token)",
    "'_fv_ex2_guest_copy_owner'",
    "file_put_contents($copy_path,(string)$copy,LOCK_EX)",
    "wp_delete_post($copy,true)",
    "'release'=>'HOLD'"
  ]);
  assert.ok(php.indexOf("file_put_contents($copy_path")<
    php.indexOf("echo wp_json_encode(array('type'"),
    'Private tracking must precede release of the create receipt');
}
function deleteInvariants(php){
  requireTokens(php,[
    "'/tmp/fv-ex2-guest-copy-id'",
    "'/tmp/fv-ex2-editor-token'",
    "'_fv_ex2_guest_copy_owner'",
    "hash_hmac('sha256','guest:'.(string)$id,$token)",
    "hash_equals($proof,$owner)",
    "wp_delete_post($id,true)",
    "get_post($id)!==null",
    "!@unlink($copy_path)||is_file($copy_path)",
    "'release'=>'HOLD'"
  ]);
  assert.ok(!php.includes('https://finalvestige.com'),'Do not contact WordPress production');
}
test('anonymous copy source is HMAC-owned and retains Gutenberg source HTML',()=>{
  copyInvariants(creation);
  assert.ok(creation.includes('$id=41;'));
});
test('cleanup binds to private tracker, HMAC ownership and optional receipt ID',()=>{
  deleteInvariants(cleanup);
  deleteInvariants(specificCleanup);
  assert.ok(cleanup.includes('if (null !== null && $id !== null)'));
  assert.ok(specificCleanup.includes('if (41 !== null && $id !== 41)'));
});
test('creator and remover never resolve an external host or real WP database',()=>{
  for(const php of [creation,cleanup]){
    assert.ok(php.includes("get_stylesheet()!=='assembler'"));
    assert.ok(php.includes("empty($u['port'])||is_multisite()"));
    assert.ok(php.includes("($u['scheme']??'')!=='http'"));
    assert.ok(php.includes("'/wordpress/wp-load.php'"));
    assert.ok(!php.includes('https://finalvestige.com'));
  }
});
test('a lost or malformed creation receipt cannot bypass cleanup',()=>{
  requireTokens(source,[
    'copyAttempted=true;',
    'phpGuestCopy(draftId)',
    'phpGuestDelete(copyId)',
    "c.verified_absent===true",
    "c.release==='HOLD'",
    "copyId===null||copyId===c.id",
    'FAIL CLOSED: owned temporary guest page cleanup unverified'
  ]);
  assert.ok(source.indexOf('copyAttempted=true;')<
    source.indexOf('server.playground.run({code:phpGuestCopy(draftId)})'));
  assert.ok(source.indexOf('if(copyAttempted)')>
    source.indexOf('} finally {'));
});
test('invalid cleanup ID is refused before PHP generation',()=>{
  for(const input of [0,-1,1.5,'41',Number.MAX_SAFE_INTEGER+1]){
    assert.throws(()=>phpGuestDelete(input));
  }
  assert.throws(()=>phpGuestCopy(0));
});
test('source negative controls reject missing HMAC, no tracking, and no unfiltered HTML',()=>{
  for(const missing of [
    "hash_equals(hash_hmac('sha256',(string)$id,$token),$owner)",
    "file_put_contents($copy_path,(string)$copy,LOCK_EX)",
    "current_user_can('unfiltered_html')"
  ])assert.throws(()=>copyInvariants(creation.replace(missing,'')));
  assert.throws(()=>deleteInvariants(cleanup.replace('hash_equals($proof,$owner)','')));
});
test('generated PHP copy and cleanup compile with the system PHP interpreter',()=>{
  for(const php of [creation,cleanup,specificCleanup]){
    const run=spawnSync('php',['-l'],{input:php,encoding:'utf8',timeout:15000});
    assert.equal(run.error,undefined,run.error?.message||'PHP lint unavailable');
    assert.equal(run.status,0,(run.stderr||'')+(run.stdout||''));
    assert.match(run.stdout,/No syntax errors detected/i);
  }
});

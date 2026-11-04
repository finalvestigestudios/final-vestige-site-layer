/** EX2 local-only WordPress-native navigation semantics correction.
 * Never call on WordPress.com, production, a public preview or a shared DB.
 * Preserve an unmodified actual Assembler axe/DOM baseline before installing
 * a real wp_navigation and wp_template_part override in disposable Playground.
 * This does not change official theme source, live header or browser DOM.
 */
import assert from 'node:assert/strict';
import {join} from 'node:path';

export function isIsolatedLoopback(raw) {
  try {
    const u = new URL(raw);
    return u.protocol === 'http:' && Boolean(u.port) &&
      ['localhost','127.0.0.1','[::1]'].includes(u.hostname) &&
      !u.username && !u.password && u.pathname === '/';
  } catch { return false; }
}

export async function inspectNavigation(page,axePath) {
  const topology=await page.evaluate(()=>
    [...document.querySelectorAll('.wp-block-navigation__container')].map(root=>({
      tag:root.tagName.toLowerCase(),
      children:[...root.children].map(c=>c.tagName.toLowerCase()),
      nested_list_count:[...root.children].filter(c=>['UL','OL'].includes(c.tagName)).length,
      link_count:root.querySelectorAll('a[href]').length,
      role:root.getAttribute('role')
    }))
  );
  await page.addScriptTag({path:axePath});
  const violations=await page.evaluate(async()=>{
    if(!window.axe)throw new Error('axe unavailable: fail closed');
    const r=await window.axe.run(document,{runOnly:{type:'rule',values:['list','listitem']}});
    return r.violations.map(v=>({id:v.id,impact:v.impact,
      selectors:v.nodes.slice(0,5).map(n=>n.target)}));
  });
  return {topology,violations};
}
export function requiresSemanticCorrection(baseline) {
  assert.ok(baseline&&Array.isArray(baseline.topology)&&Array.isArray(baseline.violations),
    'Malformed navigation baseline');
  return baseline.topology.some(n=>n.tag==='ul'&&n.nested_list_count>0)&&
    baseline.violations.some(v=>v.id==='list'&&
      v.selectors.flat().some(s=>String(s).includes('wp-block-navigation__container')));
}

// PHP checks the ACTUAL WordPress home URL AND current active theme before
// any database write. No production or subscriber data enters the fixture.
const PHP=String.raw`<?php
require '/wordpress/wp-load.php';
function ex2_abort($message) { echo wp_json_encode(array('error'=>$message)); exit; }
$u=wp_parse_url(home_url('/'));
if (!is_array($u) || ($u['scheme'] ?? '') !== 'http' ||
    !in_array($u['host'] ?? '', array('localhost','127.0.0.1','::1'), true) ||
    empty($u['port']) || is_multisite() || get_stylesheet() !== 'assembler') {
    ex2_abort('Refusing non-loopback, multisite or non-Assembler WordPress');
}
$original=get_block_template('assembler//header','wp_template_part');
if (!$original || empty($original->content)) ex2_abort('Assembler header template part missing');
$source=$original->content;
$pattern='~<!-- wp:navigation(?:\s+(\{[^>]*\}))?\s*(?:/-->|-->.*?<!-- /wp:navigation -->)~s';
if (preg_match_all($pattern,$source,$matches,PREG_SET_ORDER)!==1) {
    ex2_abort('Unexpected header navigation block shape; wrapped='.preg_match_all('~<!-- wp:navigation(?:\\s|>)~',$source).' closing='.substr_count($source,'<!-- /wp:navigation -->').' selfclosing='.preg_match_all('~<!-- wp:navigation[^>]*?/-->~s',$source));
}
$attrs=json_decode($matches[0][1] ?: '{}',true);
if (!is_array($attrs)) ex2_abort('Unexpected header navigation block attributes');
$base=home_url('/');
$link_attrs=wp_json_encode(array('label'=>'Home','url'=>$base,'kind'=>'custom'));
$markup='<!-- wp:navigation-link '.$link_attrs.' -->'.
    '<li class="wp-block-navigation-item wp-block-navigation-link"><a class="wp-block-navigation-item__content" href="'.
    esc_url($base).'"><span class="wp-block-navigation-item__label">Home</span></a></li>'.
    '<!-- /wp:navigation-link -->';
$menu=wp_insert_post(array('post_type'=>'wp_navigation',
    'post_title'=>'EX2 Synthetic Accessible Navigation — Local Only',
    'post_status'=>'publish','post_content'=>$markup),true);
if (is_wp_error($menu) || !$menu) ex2_abort('Failed creating local navigation menu');
$attrs['ref']=(int)$menu;
$replacement='<!-- wp:navigation '.wp_json_encode($attrs).' /-->';
$replaced=str_replace($matches[0][0],$replacement,$source,$replace_count);
if ($replace_count!==1 || $replaced===$source) ex2_abort('Failed isolated header rewrite');
$post=wp_insert_post(array('post_type'=>'wp_template_part','post_name'=>'header',
  'post_title'=>'EX2 Synthetic Header — Local Only','post_status'=>'publish',
  'post_content'=>$replaced),true);
if (is_wp_error($post) || !$post) ex2_abort('Failed creating local template-part override');
$terms=wp_set_post_terms($post,array('assembler'),'wp_theme',false);
if (is_wp_error($terms) || !$terms) ex2_abort('Failed binding local template part to Assembler');
wp_clean_post_cache($post);
echo wp_json_encode(array('status'=>'ISOLATED_NAVIGATION_TEMPLATE_ONLY',
  'part_slug'=>'header','menu_id'=>$menu,'header_override_id'=>$post,
  'original_sha256'=>hash('sha256',$source),'modified_sha256'=>hash('sha256',$replaced),
  'navigation_block_replacements'=>1));`;
export function phpFixtureSource(){return PHP;}

export async function correctIsolatedNavigation({server,page,axePath,outputDirectory}) {
  assert.ok(isIsolatedLoopback(server.serverUrl),'Cannot modify any non-loopback WordPress');
  assert.ok(page.stageUrl&&new URL(page.stageUrl).origin===new URL(server.serverUrl).origin,
    'Preview must belong to exact isolated Playground server');
  await page.setViewportSize({width:768,height:900});
  await page.goto(page.stageUrl,{waitUntil:'domcontentloaded',timeout:90000});
  const baseline=await inspectNavigation(page,axePath);
  console.log(JSON.stringify({event:'EX2_UNMODIFIED_ASSEMBLER_NAV',baseline}));
  await page.screenshot({path:join(outputDirectory,'assembler-768-nav-unmodified.png'),
    animations:'disabled',timeout:30000});
  assert.ok(requiresSemanticCorrection(baseline),
    'Expected Assembler nested-page-list axe failure not reproduced; refusing blind correction');
  const raw=await server.playground.run({code:PHP});
  let native;
  try{native=JSON.parse(raw.text);}catch{throw new Error('Invalid isolated WP navigation override receipt');}
  assert.equal(native.status,'ISOLATED_NAVIGATION_TEMPLATE_ONLY',
    'WP native navigation override incomplete: '+String(native.error||''));
  assert.equal(native.navigation_block_replacements,1);
  assert.equal(native.part_slug,'header');
  assert.match(native.original_sha256,/^[a-f0-9]{64}$/);
  assert.match(native.modified_sha256,/^[a-f0-9]{64}$/);
  assert.notEqual(native.original_sha256,native.modified_sha256);
  await page.goto(page.stageUrl,{waitUntil:'domcontentloaded',timeout:90000});
  const corrected=await inspectNavigation(page,axePath);
  console.log(JSON.stringify({event:'EX2_NATIVE_WP_NAV_AFTER',native,corrected}));
  await page.screenshot({path:join(outputDirectory,'assembler-768-nav-native-corrected.png'),
    animations:'disabled',timeout:30000});
  assert.ok(corrected.topology.length>0,'No rendered native navigation');
  assert.ok(corrected.topology.some(n=>n.link_count>=1),'Navigation has no actual links');
  assert.ok(corrected.topology.every(n=>n.nested_list_count===0),
    'Nested ul/ol still direct child: WP-native navigation repair failed');
  assert.deepEqual(corrected.violations,[],'Native navigation still fails axe list semantics');
  return {baseline,corrected,native,limited_to:'isolated Playground WP template part'};
}

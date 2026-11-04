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
// Use WP block parser, not regex against serialized nested block markup.
function ex2_nav_count($blocks) {
  $n=0;
  foreach ($blocks as $b) {
    if (($b['blockName'] ?? '') === 'core/navigation') ++$n;
    if (!empty($b['innerBlocks'])) $n+=ex2_nav_count($b['innerBlocks']);
  }
  return $n;
}
function ex2_pattern_slugs($blocks) {
  $out=array();
  foreach ($blocks as $b) {
    if (($b['blockName'] ?? '') === 'core/pattern')
      $out[]=$b['attrs']['slug'] ?? null;
    if (!empty($b['innerBlocks']))
      $out=array_merge($out,ex2_pattern_slugs($b['innerBlocks']));
  }
  return $out;
}
function ex2_replace_native_nav(&$blocks,$menu_id) {
  $count=0;
  foreach ($blocks as &$b) {
    if (($b['blockName'] ?? '') === 'core/navigation') {
      $b['attrs']['ref']=(int)$menu_id;
      $b['innerBlocks']=array();
      $b['innerHTML']='';
      $b['innerContent']=array();
      ++$count;
    } elseif (!empty($b['innerBlocks'])) {
      $count+=ex2_replace_native_nav($b['innerBlocks'],$menu_id);
    }
  }
  unset($b);
  return $count;
}
$original=get_block_template('assembler//header','wp_template_part');
if (!$original || empty($original->content)) ex2_abort('Assembler header template part missing');
// A customized wp_template_part can override the same slug. Never use an
// imported editor/database header as the foundation of a synthetic fixture.
if (($original->source ?? '') !== 'theme' ||
    ($original->theme ?? '') !== 'assembler' ||
    ($original->slug ?? '') !== 'header')
    ex2_abort('Refusing non-vendor or customized Assembler header');
// Pin both vendor files BEFORE *either* branch can create a wp_navigation
// or wp_template_part post, not just the registered-pattern fallback.
$theme_dir=realpath(get_stylesheet_directory());
$header_path=realpath(get_stylesheet_directory().'/parts/header.html');
$pattern_path=realpath(get_stylesheet_directory().'/patterns/header.php');
if (!$theme_dir || !$header_path || !$pattern_path ||
    dirname(dirname($header_path)) !== $theme_dir ||
    dirname(dirname($pattern_path)) !== $theme_dir ||
    !is_file($header_path) || !is_readable($header_path) ||
    !is_file($pattern_path) || !is_readable($pattern_path))
    ex2_abort('Installed Assembler header or pattern absent/outside theme');
$part_bytes=file_get_contents($header_path);
$pattern_bytes=file_get_contents($pattern_path);
$expected_part_sha256='3b983fa0d9d6ce9b2bc1024e215d9d63d9ecba2ad11f881ec59e87a40c28c2aa';
$expected_pattern_sha256='962d31e7fe0dccc0f3398367b28744d54683743922b79209eeaae71b9731a480';
if (!is_string($part_bytes) || hash('sha256',$part_bytes)!==$expected_part_sha256 ||
    !is_string($pattern_bytes) || hash('sha256',$pattern_bytes)!==$expected_pattern_sha256)
    ex2_abort('Unreviewed installed Assembler header or pattern digest');
$source=$original->content;
// WordPress theme-sourced template parts originate from the theme file;
// reject even a deceptively theme-labelled or filtered altered copy.
if (hash('sha256',$source)!==$expected_part_sha256)
    ex2_abort('Resolved header differs from the pinned vendor part');
$resolved_header_sha256=hash('sha256',$source);
$header_source='wp_resolved_template';
$blocks=parse_blocks($source);
$pattern_source_sha256=null;
if (ex2_nav_count($blocks)!==1) {
    // The official theme ZIP at hosted run 41744662962 showed its *parts*
    // header references a PHP pattern; "nav_self" counted ALL self-closing
    // blocks, not necessarily navigation. Resolve that registered pattern
    // only after pinning BOTH public vendor files and verifying theme origin.
    // Theme custody and content digest already checked for every path above.
    $part_blocks=parse_blocks($part_bytes);
    $slugs=ex2_pattern_slugs($part_blocks);
    if ($slugs!==array('assembler/header') || ex2_nav_count($part_blocks)!==0)
        ex2_abort('Pinned part is not an exclusive assembler/header pattern reference');
    if (ex2_pattern_slugs($blocks)!==array('assembler/header'))
        ex2_abort('Resolved header is not the pinned vendor pattern');
    $entry=WP_Block_Patterns_Registry::get_instance()->get_registered('assembler/header');
    if (!is_array($entry) || !is_string($entry['content'] ?? null) || !$entry['content'])
        ex2_abort('Installed theme header pattern not registered in WordPress');
    $source=$entry['content'];
    $blocks=parse_blocks($source);
    if (ex2_nav_count($blocks)!==1)
        ex2_abort('Official registered Assembler header does not have one navigation block');
    $header_source='pinned_registered_theme_pattern';
    $pattern_source_sha256=hash('sha256',$source);
}
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
$replace_count=ex2_replace_native_nav($blocks,$menu);
if ($replace_count!==1) ex2_abort('Expected exactly one parsed native navigation rewrite');
$replaced=serialize_blocks($blocks);
if (!is_string($replaced) || $replaced===$source)
    ex2_abort('Failed native WordPress block serializer rewrite');
$post=wp_insert_post(array('post_type'=>'wp_template_part','post_name'=>'header',
  'post_title'=>'EX2 Synthetic Header — Local Only','post_status'=>'publish',
  'post_content'=>$replaced),true);
if (is_wp_error($post) || !$post) ex2_abort('Failed creating local template-part override');
$terms=wp_set_post_terms($post,array('assembler'),'wp_theme',false);
if (is_wp_error($terms) || !$terms) ex2_abort('Failed binding local template part to Assembler');
clean_post_cache($post);
echo wp_json_encode(array('status'=>'ISOLATED_NAVIGATION_TEMPLATE_ONLY',
  'part_slug'=>'header','menu_id'=>$menu,'header_override_id'=>$post,
  'original_sha256'=>hash('sha256',$source),'modified_sha256'=>hash('sha256',$replaced),
  'navigation_block_replacements'=>1,
  'header_source'=>$header_source,'resolved_header_sha256'=>$resolved_header_sha256,
  'pattern_source_sha256'=>$pattern_source_sha256));`;
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
  assert.ok(['wp_resolved_template','pinned_registered_theme_pattern'].includes(native.header_source),
    'Unrecognized source provenance');
  assert.match(native.resolved_header_sha256,/^[a-f0-9]{64}$/);
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

import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {isIsolatedLoopback,requiresSemanticCorrection,phpFixtureSource,
  correctIsolatedNavigation} from './assembler_nav_native_fixture.mjs';

const baseline={topology:[{tag:'ul',nested_list_count:1,link_count:1,children:['ul','li']}],
  violations:[{id:'list',impact:'serious',selectors:[['.wp-block-navigation__container']]}]};
const safe={topology:[{tag:'ul',nested_list_count:0,link_count:1,children:['li']}],violations:[]};
function mock({host='http://127.0.0.1:21234/',nativeError=false,source='pinned_registered_theme_pattern',resolvedHash='a'.repeat(64)}={}){
  let stage=0,runCount=0;const history=[];
  const page={stageUrl:host+'?page_id=3&preview=true',
    async setViewportSize(v){history.push('size:'+v.width)},
    async goto(){stage++;history.push('goto')},
    async evaluate(fn){
      const r=stage===1?baseline:safe;
      return String(fn).includes('.wp-block-navigation__container')?r.topology:r.violations;
    },
    async addScriptTag(){history.push('axe-injected')},
    async screenshot(o){history.push('image:'+o.path.split('/').pop())}};
  const server={serverUrl:host,playground:{async run({code}){
    runCount++;history.push('wordpress-run');
    if(!code.includes('wp_template_part'))throw new Error('Missing native WP storage');
    return {text:JSON.stringify(nativeError?{error:'not found'}:{
      status:'ISOLATED_NAVIGATION_TEMPLATE_ONLY',part_slug:'header',
      navigation_block_replacements:1,original_sha256:'b'.repeat(64),
      modified_sha256:'c'.repeat(64),header_source:source,
      resolved_header_sha256:resolvedHash})};
  }}};
  return {page,server,history,getRunCount:()=>runCount};
}
test('requires strict, uncredentialed HTTP loopback with explicit port',()=>{
  for(const s of ['http://localhost:3030/','http://127.0.0.1:9001/'])
    assert.ok(isIsolatedLoopback(s));
  for(const s of ['https://localhost:3030/','http://localhost/',
    'https://finalvestige.com/','http://localhost:3000@evil.test/',
    'http://127.0.0.1.evil.test:3000/','http://localhost:3000/path'])
    assert.equal(isIsolatedLoopback(s),false,s);
});
test('requires observed DOM AND actual axe failure',()=>{
  assert.equal(requiresSemanticCorrection(baseline),true);
  assert.equal(requiresSemanticCorrection(safe),false);
  assert.equal(requiresSemanticCorrection({...baseline,violations:[]}),false);
  assert.equal(requiresSemanticCorrection({...baseline,topology:safe.topology}),false);
});
test('malformed baseline fails closed',()=>{
  for(const x of [null,{}, {topology:[],violations:null}])
    assert.throws(()=>requiresSemanticCorrection(x));
});
test('PHP refuses production, wrong theme and multisite before native writes',()=>{
  const src=phpFixtureSource();
  for(const token of ["require '/wordpress/wp-load.php'","is_multisite()",
    "get_stylesheet() !== 'assembler'","'localhost','127.0.0.1','::1'",
    "'wp_navigation'","'wp_template_part'","'wp_theme'",
    'wp:navigation-link','wp_json_encode','wp_clean_post_cache'])
    assert.ok(src.includes(token),'missing '+token);
  assert.equal(src.includes('finalvestige.com'),false);
});
test('captures real baseline before isolated native WP override',async()=>{
  const x=mock();
  const result=await correctIsolatedNavigation({...x,axePath:'/fake/axe.js',outputDirectory:'/tmp'});
  assert.equal(result.limited_to,'isolated Playground WP template part');
  assert.equal(x.getRunCount(),1);
  assert.equal(x.history.filter(v=>v.startsWith('image:')).length,2);
  assert.ok(x.history.indexOf('image:assembler-768-nav-unmodified.png')<x.history.indexOf('wordpress-run'));
  assert.ok(x.history.indexOf('wordpress-run')<x.history.indexOf('image:assembler-768-nav-native-corrected.png'));
});
test('public site refuses before browser or WP interaction',async()=>{
  const x=mock({host:'https://finalvestige.com/'});
  await assert.rejects(correctIsolatedNavigation({...x,axePath:'axe',outputDirectory:'/tmp'}),/non-loopback/);
  assert.equal(x.history.length,0);assert.equal(x.getRunCount(),0);
});
test('invalid WordPress receipt fails closed',async()=>{
  const x=mock({nativeError:true});
  await assert.rejects(correctIsolatedNavigation({...x,axePath:'axe',outputDirectory:'/tmp'}),/incomplete/);
  assert.equal(x.getRunCount(),1);
});
test('cross-origin preview denied before WordPress writes',async()=>{
  const x=mock();x.page.stageUrl='https://finalvestige.com/?preview=true';
  await assert.rejects(correctIsolatedNavigation({...x,axePath:'axe',outputDirectory:'/tmp'}),/exact isolated/);
  assert.equal(x.getRunCount(),0);
});

test('pattern-only resolved header can use ONLY a pinned registered WordPress theme pattern',()=>{
  const php=phpFixtureSource();
  for(const marker of [
    "($original->source ?? '') !== 'theme'",
    "realpath(get_stylesheet_directory().'/parts/header.html')",
    "realpath(get_stylesheet_directory().'/patterns/header.php')",
    "dirname(dirname($header_path)) !== $theme_dir",
    "dirname(dirname($pattern_path)) !== $theme_dir",
    "get_stylesheet() !== 'assembler'",
    "3b983fa0d9d6ce9b2bc1024e215d9d63d9ecba2ad11f881ec59e87a40c28c2aa",
    "962d31e7fe0dccc0f3398367b28744d54683743922b79209eeaae71b9731a480",
    "hash('sha256',$part_bytes)!==$expected_part_sha256",
    "hash('sha256',$pattern_bytes)!==$expected_pattern_sha256",
    "ex2_pattern_slugs($part_blocks)",
    "array('assembler/header')",
    "WP_Block_Patterns_Registry::get_instance()->get_registered('assembler/header')",
    "parse_blocks($source)",
    "serialize_blocks($blocks)",
    "$header_source='pinned_registered_theme_pattern'",
    "header_source'=>$header_source"
  ]) assert.ok(php.includes(marker),'Missing fail-closed source custody: '+marker);
  const guard=php.indexOf("get_stylesheet() !== 'assembler'");
  const read=php.indexOf("file_get_contents($pattern_path)");
  const digest=php.indexOf("hash('sha256',$pattern_bytes)!==$expected_pattern_sha256");
  const resolve=php.indexOf("get_registered('assembler/header')");
  assert.ok(guard<read && read<digest && digest<resolve,
    'Must validate theme, file digest and pattern slug before loading registered content');
  assert.ok(php.indexOf("ex2_nav_count($blocks)!==1")<php.indexOf("$base=home_url('/')"),
    'Must select a single real native WP navigation block before creating menu');
});
test('unknown WordPress header provenance fails closed before completion',async()=>{
  for(const source of [null,'unreviewed_remote_header','']){
    const x=mock({source});
    await assert.rejects(
      correctIsolatedNavigation({...x,axePath:'axe',outputDirectory:'/tmp'}),
      /Unrecognized source provenance/);
    assert.equal(x.getRunCount(),1);
  }
});
test('missing or corrupt resolved header hash fails closed',async()=>{
  for(const hash of ['', 'deadbeef', 'x'.repeat(64)]){
    const x=mock({resolvedHash:hash});
    await assert.rejects(
      correctIsolatedNavigation({...x,axePath:'axe',outputDirectory:'/tmp'}),
      /assert|regular expression/i);
    assert.equal(x.getRunCount(),1);
  }
});

test('entire native WP inline PHP (including pinned fallback) parses with host PHP',()=>{
  const check=spawnSync('php',['-l'],{input:phpFixtureSource(),encoding:'utf8',timeout:10000});
  assert.equal(check.status,0,'PHP syntax error or missing PHP tool: '+(check.stderr||check.stdout||check.error));
  assert.match(check.stdout,/No syntax errors detected/);
});

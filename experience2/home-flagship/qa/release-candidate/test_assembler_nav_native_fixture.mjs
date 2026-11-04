import test from 'node:test';
import assert from 'node:assert/strict';
import {isIsolatedLoopback,requiresSemanticCorrection,phpFixtureSource,
  correctIsolatedNavigation} from './assembler_nav_native_fixture.mjs';

const baseline={topology:[{tag:'ul',nested_list_count:1,link_count:1,children:['ul','li']}],
  violations:[{id:'list',impact:'serious',selectors:[['.wp-block-navigation__container']]}]};
const safe={topology:[{tag:'ul',nested_list_count:0,link_count:1,children:['li']}],violations:[]};
function mock({host='http://127.0.0.1:21234/',nativeError=false}={}){
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
      modified_sha256:'c'.repeat(64)})};
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

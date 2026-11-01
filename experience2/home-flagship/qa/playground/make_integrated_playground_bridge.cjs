'use strict';
// LOCAL-ONLY Gutenberg staging bridge. Never contacts or edits a WordPress site.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { assemble } = require('../release-candidate/assemble_homepage_migration.cjs');
const { SHA } = require('../release-candidate/verify_homepage_migration.cjs');
const FRAGMENT = '/wordpress/wp-content/plugins/fv-ex2-playground/assets/wordpress-page-fragment.review-only.html';
const PLUGIN = '/wordpress/wp-content/plugins/fv-ex2-playground/fv-ex2-playground.php';
const REVIEWED = 'a868423c033a179d1821bb9eb1cf7b5c6c07106097e18cce6afe58b79f908cc1';
function assert(ok, why) { if (!ok) throw Error('FV INTEGRATED STAGE HOLD: ' + why); }
function one(steps, step, pred) {
  const matches=steps.filter(s=>s.step===step && pred(s));
  assert(matches.length===1,'unique '+step+' stage step required');
  return matches[0];
}
const BRIDGE = [
  "add_filter('render_block', static function($html, $block) {",
  "  if (!is_front_page()) return $html;",
  "  if (($block['blockName'] ?? '') === 'jetpack/subscriptions') {",
  "    if (!fv_ex2_safe_stage()) return $html;",
  "    return '<div class=\\\"fv-ex2-local-subscription-boundary\\\" role=\\\"note\\\" data-fv-subscriptions-local-only=\\\"true\\\"><strong>Dispatch signup — hosted verification required</strong><p>The original Jetpack signup block is preserved in the WordPress page source. It is unavailable in this isolated preview; no email addresses are collected here.</p></div>';",
  "  }",
  "  if (($block['blockName'] ?? '') !== 'core/html' || strpos($html,'data-fv-home-flagship')===false) return $html;",
  "  if (!fv_ex2_ready()) return '<p>Local stage CLOSED: media/source verification.</p>';",
  "  $source = @file_get_contents(__DIR__ . '/assets/wordpress-page-fragment.review-only.html');",
  "  if (!is_string($source) || trim($source) !== trim($html)) return '<p>Local stage CLOSED: changed WordPress flagship block.</p>';",
  "  return do_shortcode('[fv_ex2_stage_home]');",
  '}, 10, 2);'
].join('\n');
function integrate(base, publicPage, pageSha) {
  assert(base && Array.isArray(base.steps) && base.steps.length===19,'exact 19-step Playground baseline required');
  assert(typeof publicPage==='string' && Buffer.byteLength(publicPage)>1000 && Buffer.byteLength(publicPage)<500000,'PUBLIC page-6 raw Gutenberg content only');
  assert(/^[a-f0-9]{64}$/.test(pageSha||'') && SHA(publicPage)===pageSha,'independently verified page-6 SHA-256 required');
  const steps=base.steps;
  assert(steps[0].step==='defineWpConfigConsts' && steps[0].consts.WP_ENVIRONMENT_TYPE==='local' && steps[0].consts.FV_EX2_ALLOW_LOCAL_REVIEW===true,'local-only gate missing');
  assert(steps[1].step==='installTheme' && /\/assembler\.zip$/.test(steps[1].themeData?.url||''),'official Assembler theme required');
  assert(steps.filter(s=>s.step==='writeFile').length===15 && !steps.some(s=>['importWxr','runSql','importWordPressFiles'].includes(s.step)),'unsafe staging data import/file inventory');
  const original=one(steps,'writeFile',s=>s.path===FRAGMENT).data;
  assert(typeof original==='string' && SHA(original)===REVIEWED,'reviewed source fragment fingerprint changed');
  const oldPlugin=one(steps,'writeFile',s=>s.path===PLUGIN).data;
  assert(typeof oldPlugin==='string' && oldPlugin.includes('fv_ex2_integrity()') && oldPlugin.includes('fv_ex2_ready()') && !oldPlugin.includes("add_filter('render_block'"),'media-gated local plugin required');
  assert(one(steps,'runPHP',s=>typeof s.code==='string').code.includes('fv_ex2_ready()'),'local bootstrap gate missing');
  const composed=assemble(publicPage,original,{expectedLegacySha:pageSha,expectedFragmentSha:REVIEWED});
  const html=composed.candidate;
  const encoded=Buffer.from(html,'utf8').toString('base64');
  const digest=SHA(html);
  const next=JSON.parse(JSON.stringify(base));
  one(next.steps,'writeFile',s=>s.path===PLUGIN).data+='\n'+BRIDGE+'\n';
  one(next.steps,'runPHP',s=>true).code=[
    "<?php require_once '/wordpress/wp-load.php';",
    "if (!fv_ex2_ready() || get_stylesheet() !== 'assembler' || wp_get_environment_type() !== 'local') throw new Exception('FV stage CLOSED: environment, theme or media');",
    "$raw=base64_decode('"+encoded+"',true);",
    "if (!is_string($raw) || !hash_equals('"+digest+"',hash('sha256',$raw))) throw new Exception('FV stage CLOSED: page digest');",
    "if (substr_count($raw,'--i:') !== 72 || substr_count($raw,'<!-- wp:jetpack/subscriptions') !== 1) throw new Exception('FV stage CLOSED: protected history or Jetpack missing');",
    "$found=0; foreach(parse_blocks($raw) as $block) { if (($block['blockName'] ?? '')==='core/html' && strpos($block['innerHTML'] ?? '', 'data-fv-home-flagship') !== false) ++$found; }",
    "if ($found !== 1) throw new Exception('FV stage CLOSED: no unique Gutenberg flagship block');",
    "$id=wp_insert_post(array('post_title'=>'FV LOCAL Integrated Homepage Review','post_name'=>'fv-integrated-local-review','post_status'=>'publish','post_type'=>'page','post_content'=>$raw));",
    "if (!$id || is_wp_error($id)) throw new Exception('FV stage CLOSED: local WordPress insert');",
    "update_option('show_on_front','page'); update_option('page_on_front',$id); echo 'LOCAL STAGE ONLY: page '.$id;"
  ].join('\n');
  next.meta={title:'FV Integrated Seven-Chapter Homepage — LOCAL ONLY',description:'Public Gutenberg content and independently pinned media; no production DB/users/subscribers/secrets.'};
  assert(next.steps.length===19 && next.steps.filter(s=>s.step==='writeFile').length===15,'no new public asset files allowed');
  return {blueprint:next,candidate:html,receipt:{status:'LOCAL_PLAYGROUND_BLUEPRINT_PREPARED_NOT_EXECUTED',page_sha256:pageSha,fragment_sha256:REVIEWED,candidate_sha256:digest,candidate_bytes:Buffer.byteLength(html),margins:composed.receipt.preserved_margin_items,jetpack:composed.receipt.original_jetpack_blocks,focus:composed.receipt.original_focus_links,chapters:composed.receipt.chapter_anchors,cases:composed.receipt.evidence_cases,wordpress_rendered:false,rights_verified:false,axe_verified:false,lighthouse_verified:false}};
}
function cli(args){
  const get=k=>{const i=args.indexOf(k);return i>=0?args[i+1]:null;};
  for(const k of ['--public-page','--page-sha256','--output','--receipt']) assert(get(k) && !get(k).startsWith('--'),'missing '+k);
  assert(!fs.existsSync(get('--output')) && !fs.existsSync(get('--receipt')) && path.resolve(get('--output'))!==path.resolve(get('--receipt')),'refuse overwrite');
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'fv-isolated-page-'));
  try {
    const basefile=path.join(tmp,'base.json');
    require('./make_playground_blueprint.cjs').generate(basefile,{trustedMediaManifest:get('--trusted-media-manifest')||null});
    const base=JSON.parse(fs.readFileSync(basefile,'utf8'));
    const r=integrate(base,fs.readFileSync(get('--public-page'),'utf8'),get('--page-sha256'));
    fs.writeFileSync(get('--output'),JSON.stringify(r.blueprint,null,2)+'\n',{flag:'wx',mode:0o600});
    try{fs.writeFileSync(get('--receipt'),JSON.stringify(r.receipt,null,2)+'\n',{flag:'wx',mode:0o600});}
    catch(e){fs.rmSync(get('--output'),{force:true});throw e;}
    process.stdout.write(JSON.stringify(r.receipt)+'\n');
  }finally{fs.rmSync(tmp,{recursive:true,force:true});}
}
if(require.main===module){try{cli(process.argv.slice(2));}catch(e){console.error(String(e));process.exitCode=1;}}
module.exports={integrate,BRIDGE};

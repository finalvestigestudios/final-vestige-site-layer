'use strict';
/**
 * LOCAL-ONLY public Assembler page-template parity for the integrated homepage.
 * The real WordPress.com page 6 uses a customized assembler//page template;
 * stock Assembler (installed by Playground) does not automatically inherit it.
 * This module requires an independently SHA-256-pinned PUBLIC Gutenberg
 * template export, corrects only the dynamic front-page body selector, and
 * admits it in the EXISTING local-only runPHP step, never on production.
 * It cannot claim native WordPress rendering without running that step.
 */
const crypto = require('node:crypto');
const SHA = s => crypto.createHash('sha256').update(s,'utf8').digest('hex');
const FRONT_WIDTH = '.page-id-6 .fv-post-content>*{max-width:none!important}';
const LOCAL_WIDTH = 'body.home .fv-post-content>*{max-width:none!important}';
const BEFORE_PAGE = "$id=wp_insert_post(array('post_title'=>'FV LOCAL Integrated Homepage Review'";
function hold(why) { throw new Error('FV LOCAL TEMPLATE PARITY HOLD: ' + why); }
function verifyTemplate(source, digest) {
  if (typeof source !== 'string' || Buffer.byteLength(source,'utf8') < 1000 || Buffer.byteLength(source,'utf8') > 125000)
    hold('requires bounded public Assembler page-template Gutenberg markup');
  if (!/^[0-9a-f]{64}$/.test(digest||'') || SHA(source) !== digest)
    hold('original template SHA-256 mismatch or missing');
  if ((source.match(/<!-- wp:post-content\b/g)||[]).length !== 1 ||
      !/<!-- wp:post-content\s+\{[^\n]*"className":"fv-post-content"/.test(source) ||
      !/"contentSize":"760px"/.test(source) ||
      !/"wideSize":"1440px"/.test(source))
    hold('the authenticated production 760/1440 constrained post-content layout is absent');
  for (const fragment of ['<!-- wp:template-part {"slug":"header"','<!-- wp:template-part {"slug":"footer"']) {
    if (!source.includes(fragment)) hold('production template structure changed: '+fragment);
  }
  if (source.split(FRONT_WIDTH).length !== 2)
    hold('exact single production page-id-6 full-bleed override is required');
  if (/<(?:script|iframe|form|object|embed|php)\b|<\?php|<!--\s*wp:jetpack\/subscriptions\b/i.test(source))
    hold('non-template executable, user or subscriber markup is forbidden');
  return { localTemplate:source.replace(FRONT_WIDTH,LOCAL_WIDTH), original_sha256:digest };
}
function stageTemplate(blueprint, source, digest) {
  const {localTemplate,original_sha256}=verifyTemplate(source,digest);
  if (!blueprint || !Array.isArray(blueprint.steps) || blueprint.steps.length !== 19)
    hold('unchanged 19-step local-only Blueprint required');
  if (blueprint.steps[0]?.step !== 'defineWpConfigConsts' ||
      blueprint.steps[0]?.consts?.WP_ENVIRONMENT_TYPE !== 'local' ||
      blueprint.steps[0]?.consts?.FV_EX2_ALLOW_LOCAL_REVIEW !== true)
    hold('no explicit local-only authorization');
  if (blueprint.steps[1]?.step !== 'installTheme' ||
      !/\/assembler\.zip$/.test(blueprint.steps[1]?.themeData?.url||''))
    hold('verified Assembler install step missing');
  if (blueprint.steps.some(s=>['importWxr','runSql','importWordPressFiles'].includes(s.step)))
    hold('database/user import not permitted');
  const phpSteps = blueprint.steps.filter(s=>s.step==='runPHP');
  if (phpSteps.length!==1 || !phpSteps[0].code.includes(BEFORE_PAGE))
    hold('expected integrated bootstrap insert point changed');
  if (phpSteps[0].code.includes('FV LOCAL TEMPLATE PARITY'))
    hold('template already added; refuse duplicate');
  const templateDigest=SHA(localTemplate);
  const encoded=Buffer.from(localTemplate,'utf8').toString('base64');
  const snippet=[
    "// FV LOCAL TEMPLATE PARITY: only the already-gated local Playground database.",
    "$fv_template=base64_decode('"+encoded+"',true);",
    "if (!is_string($fv_template) || !hash_equals('"+templateDigest+"',hash('sha256',$fv_template))) throw new Exception('FV stage CLOSED: custom template digest');",
    "if (get_stylesheet() !== 'assembler' || wp_get_environment_type() !== 'local' || !fv_ex2_safe_stage()) throw new Exception('FV stage CLOSED: template only permitted locally');",
    "$fv_template_id=wp_insert_post(array('post_type'=>'wp_template','post_name'=>'page','post_title'=>'Page — FV Local Parity','post_status'=>'publish','post_content'=>wp_slash($fv_template)),true);",
    "if (!$fv_template_id || is_wp_error($fv_template_id)) throw new Exception('FV stage CLOSED: local block template insert');",
    "$fv_terms=wp_set_object_terms($fv_template_id,'assembler','wp_theme');",
    "if (is_wp_error($fv_terms) || !$fv_terms) throw new Exception('FV stage CLOSED: local block template theme binding');",
    "$fv_stored_template=get_post_field('post_content',$fv_template_id,'raw');",
    "if (!is_string($fv_stored_template) || !hash_equals('"+templateDigest+"',hash('sha256',$fv_stored_template))) throw new Exception('FV stage CLOSED: saved template content differs from reviewed source');",
    "$fv_resolved=wp_get_block_template('assembler//page','wp_template');",
    "if (!$fv_resolved || !isset($fv_resolved->content) || !is_string($fv_resolved->content) || !hash_equals('"+templateDigest+"',hash('sha256',$fv_resolved->content)) || ($fv_resolved->source ?? null) !== 'custom') throw new Exception('FV stage CLOSED: exact custom page template did not resolve');",
    "if (wp_get_block_template('assembler//front-page','wp_template')) throw new Exception('FV stage CLOSED: front-page template would supersede the verified page template');",
    "// The public site uses page-id-6; the isolated local front page gets an unrelated ID."
  ].join('\n')+'\n';
  const cloned=JSON.parse(JSON.stringify(blueprint));
  const target=cloned.steps.filter(s=>s.step==='runPHP')[0];
  target.code=target.code.replace(BEFORE_PAGE,snippet+BEFORE_PAGE);
  if (cloned.steps.length!==19 || cloned.steps.filter(s=>s.step==='writeFile').length!==15)
    hold('unexpected local Blueprint file or step inventory');
  return {blueprint:cloned,receipt:{status:'LOCAL_TEMPLATE_PARITY_PREPARED_NOT_RENDERED',source_template_sha256:original_sha256,local_template_sha256:templateDigest,source_template_bytes:Buffer.byteLength(source),local_template_bytes:Buffer.byteLength(localTemplate),template_slug:'assembler//page',front_width_rule:LOCAL_WIDTH,actual_wordpress_rendered:false,actual_full_bleed_verified:false,hosting_parity_verified:false}};
}
module.exports={verifyTemplate,stageTemplate,FRONT_WIDTH,LOCAL_WIDTH,SHA};

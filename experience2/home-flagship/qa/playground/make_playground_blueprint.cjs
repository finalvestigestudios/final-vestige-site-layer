'use strict';
/**
 * Self-contained, isolated WordPress Playground Blueprint generator.
 * Exact source and asset identity are enforced by the pre-existing release builder.
 * No WordPress production API, database export, subscription or hosted write.
 */
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { makeBundle, ASSETS, SOURCE_GIT_BLOB } = require('../release-candidate/build_release_review.cjs');
const IMAGES = Object.freeze([
  ['apollo.webp', 'https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'],
  ['franklin.jpg', 'https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg'],
  ['nypl.jpg', 'https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg']
]);
const REVIEW_FRAGMENT = 'wordpress-page-fragment.review-only.html';
const THEME_URL = 'https://public-api.wordpress.com/rest/v1/themes/download/assembler.zip';
const ROOT = '/wordpress/wp-content/plugins/fv-ex2-playground';
const MEDIA_BYTES = Object.freeze({'apollo.webp':78346,'franklin.jpg':466043,'nypl.jpg':5553669});
function trustedMediaHashes(manifestPath) {
  if (!manifestPath) return null; // never silently trust downloaded file dimensions
  const m = JSON.parse(fs.readFileSync(manifestPath,'utf8'));
  assert(m && m.purpose === 'isolated-staging-media-review' && m.images && typeof m.images === 'object',
    'unreviewed media fingerprint manifest');
  const keys=Object.keys(m.images).sort();
  const required=IMAGES.map(x=>x[0]).sort();
  assert(JSON.stringify(keys)===JSON.stringify(required),'trusted media must list exactly three originals');
  const hashes={};
  for (const [name,url] of IMAGES) {
    const rec=m.images[name];
    assert(rec && rec.source_url===url && rec.bytes===MEDIA_BYTES[name]
      && typeof rec.sha256==='string' && /^[a-f0-9]{64}$/.test(rec.sha256),
      'invalid verified digest/origin/length for '+name);
    hashes[name]=rec.sha256;
  }
  return hashes;
}
function assert(cond, reason) { if (!cond) throw new Error('PLAYGROUND CLOSED: ' + reason); }
function generate(outputPath, options={}) {
  assert(typeof outputPath === 'string' && outputPath.length, 'specify a new output path');
  assert(!fs.existsSync(outputPath), 'refusing overwrite of existing Blueprint');
  const hashesForMedia=trustedMediaHashes(options.trustedMediaManifest);
  const work = fs.mkdtempSync(path.join(os.tmpdir(), 'fv-ex2-playground-'));
  try {
    const release = path.join(work, 'release');
    const home = path.resolve(__dirname, '..', '..');
    const manifest = makeBundle(home, release);
    assert(manifest.sourceGitBlob === SOURCE_GIT_BLOB, 'source identity drift');
    const names = [REVIEW_FRAGMENT, ...ASSETS];
    assert(names.length === 11 && IMAGES.length === 3, 'unexpected manifest shape');
    for (const name of names) {
      assert(manifest.files[name] && manifest.files[name].sha256, 'missing sealed file ' + name);
    }
    const template = fs.readFileSync(path.join(__dirname, 'fv-ex2-playground.php.template'), 'utf8');
    assert(template.includes('__FV_EXPECTED_HASHES__') && template.includes('__FV_ENQUEUE_STATEMENTS__')
      && template.includes('__FV_TRUSTED_MEDIA_SHA256__'), 'PHP template markers changed');
    const hashes = 'array(\n' + names.map(name => "        '" + name + "' => '" + manifest.files[name].sha256 + "'").join(',\n') + '\n    )';
    const enqueue = ASSETS.map(name => {
      const handle = 'fv-ex2-' + name.replace(/\.(css|js)$/, '');
      const url = "plugins_url('assets/" + name + "', __FILE__)";
      const version = "'" + manifest.files[name].sha256.slice(0, 12) + "'";
      return name.endsWith('.css')
        ? "    wp_enqueue_style('" + handle + "', " + url + ", array(), " + version + ");"
        : "    wp_enqueue_script('" + handle + "', " + url + ", array(), " + version + ", true);";
    }).join('\n');
    const mediaHashesPHP = hashesForMedia
      ? 'array(\n' + IMAGES.map(([name]) => "        '" + name + "' => '" + hashesForMedia[name] + "'").join(',\n') + '\n    )'
      : 'array()'; // explicit fail-closed until separately verified originals are provided
    const plugin = template.replace('__FV_EXPECTED_HASHES__', hashes)
      .replace('__FV_ENQUEUE_STATEMENTS__', enqueue)
      .replace('__FV_TRUSTED_MEDIA_SHA256__', mediaHashesPHP);
    assert(!plugin.includes('__FV_EXPECTED_HASHES__') && !plugin.includes('__FV_ENQUEUE_STATEMENTS__')
      && !plugin.includes('__FV_TRUSTED_MEDIA_SHA256__'), 'unexpanded PHP markers');
    const steps = [
      { step:'defineWpConfigConsts', consts:{ WP_ENVIRONMENT_TYPE:'local', FV_EX2_ALLOW_LOCAL_REVIEW:true } },
      { step:'installTheme', themeData:{ resource:'url', url:THEME_URL }, options:{activate:true} },
      { step:'writeFile', path:ROOT + '/fv-ex2-playground.php', data:plugin }
    ];
    for (const name of names) {
      steps.push({step:'writeFile',path:ROOT + '/assets/' + name, data:fs.readFileSync(path.join(release,name),'utf8')});
    }
    for (const [name,url] of IMAGES) {
      steps.push({step:'writeFile',path:ROOT + '/media/' + name,data:{resource:'url',url}});
    }
    steps.push({step:'activatePlugin',pluginPath:'fv-ex2-playground/fv-ex2-playground.php'});
    const bootstrap = "<?php require_once '/wordpress/wp-load.php'; if (!fv_ex2_ready() || get_stylesheet() !== 'assembler') { throw new Exception('FV stage CLOSED: Assembler/source/media gate failed'); } $id = wp_insert_post(array('post_title'=>'FV Seven-Chapter Private Acceptance','post_name'=>'fv-ex2-preview','post_status'=>'publish','post_type'=>'page','post_content'=>'<!-- wp:shortcode -->[fv_ex2_stage_home]<!-- /wp:shortcode -->')); if (is_wp_error($id) || !$id) { throw new Exception('FV stage CLOSED: local page creation failed'); } update_option('show_on_front','page'); update_option('page_on_front',$id); echo 'FV isolated Playground only: ' . $id;";
    steps.push({step:'runPHP',code:bootstrap});
    const blueprint = {
      $schema:'https://playground.wordpress.net/blueprint-schema.json',
      meta:{title:'Final Vestige Experience 2.0 — Isolated Seven-Chapter Acceptance',
        description:'Source-pinned real WordPress/Assembler review; no production data, users, subscriber list, secrets or merchant tracking.'},
      landingPage:'/', login:true, preferredVersions:{php:'8.3',wp:'latest'}, steps
    };
    assert(steps.length === 19 && steps.filter(s=>s.step==='writeFile').length === 15, 'unexpected staging steps');
    assert(!steps.some(s=>['importWxr','importWordPressFiles','runSql'].includes(s.step)), 'forbidden database/content import');
    fs.mkdirSync(path.dirname(path.resolve(outputPath)), {recursive:true});
    fs.writeFileSync(outputPath, JSON.stringify(blueprint, null, 2) + '\n', {flag:'wx'});
    return {outputPath, sourceGitBlob:manifest.sourceGitBlob, assets:names.length, media:IMAGES.length,
      steps:steps.length, bytes:fs.statSync(outputPath).size,
      mediaIdentityGate:hashesForMedia ? 'REVIEWED_SHA256_VALUES_SUPPLIED' : 'CLOSED_MISSING_MEDIA_FINGERPRINTS',
      wordpressRuntimeVerified:false, stagingRenderVerified:false};
  } finally { fs.rmSync(work,{recursive:true,force:true}); }
}
module.exports = {generate, IMAGES, THEME_URL, trustedMediaHashes};
if (require.main === module) {
  const i = process.argv.indexOf('--output');
  if (i<0 || !process.argv[i+1]) { process.stderr.write('Use: node make_playground_blueprint.cjs --output /private/new-blueprint.json\n'); process.exitCode=2; }
  else { try {
    const k=process.argv.indexOf('--trusted-media-manifest');
    const opts={trustedMediaManifest:k>=0 ? process.argv[k+1] : null};
    if(k>=0 && !opts.trustedMediaManifest)throw new Error('Missing --trusted-media-manifest path');
    process.stdout.write(JSON.stringify(generate(process.argv[i+1],opts))+'\n');
  } catch(e) { process.stderr.write(String(e)+'\n'); process.exitCode=1; } }
}

"""Offline regression tests; fixture is NOT a running WordPress/Playground instance."""
from __future__ import annotations
import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from prepare_unified_playground import bind, verify_sources, verify_parity, verify_stage, sha, PARITY, CANONICAL_LOCAL_SEED, expected_php_payload

HERE = Path(__file__).parent
SOURCE_ASSETS = ('index.html','flagship.css','chronicle.css','chronicle-lens.css',
                 'inquiry.css','observer-lab.css','reading-trail.css','flagship.js',
                 'observer-lab.js','chronicle-lens.js','reading-trail.js')

BASE_PARTS = ('prepare_unified_playground.py', 'test_prepare_unified_playground.py',
              'apply_local_parity.php',
              'sanitize_theme_parity.py', 'blueprint.local.json')


def fixture():
    """Commit an exact-source synthetic parity repository and make a separate stage kit."""
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    repo = root/'repository'
    repo.mkdir()
    local = repo/PARITY
    local.mkdir(parents=True)
    for name in BASE_PARTS:
        (local/name).write_bytes((HERE/name).read_bytes())
    template = ('<!-- wp:group --><header>FINAL VESTIGE / ARCHIVE / FOCUS</header>'
                '<!-- /wp:group --><!-- wp:html --><style>.fv{color:#f4efe6}</style><!-- /wp:html -->')
    data = {
        'schema':'fv-local-assembler-parity-v1', 'release':'HOLD',
        'source_theme':{'stylesheet':'assembler','version':'0.0.126'},
        'local_only':True,
        'template_content':{k:template+('<!-- wp:template-part {"slug":"footer"} /-->' if k=='page' else '')
                            for k in ('page','header','footer','overlay')},
        'global_styles':{'settings':{'layout':{'contentSize':'760px','wideSize':'1440px'}},
                         'styles':{'css':'.fv{color:#f4efe6}'+('.fv a{color:#cda75d}\n'*40)}}
    }
    (local/'assembler-public-safe.json').write_text(json.dumps(data))
    upstream = repo/'experience2/home-flagship'
    upstream.mkdir(parents=True, exist_ok=True)
    for a in SOURCE_ASSETS:
        (upstream/a).write_bytes(('synthetic '+a).encode())
    source_php = upstream/'qa/integration/private-preview/fv-ex2-private-preview.php'
    source_php.parent.mkdir(parents=True)
    source_php.write_text('<?php // committed private-preview test stub\n')
    subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True)
    subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(repo), '-c','user.name=FV Test','-c','user.email=fv@example.invalid','commit','-qm','Fixture'],check=True)
    head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    stage=root/'stage'
    (stage/'mounts'/'assembler').mkdir(parents=True)
    (stage/'mounts'/'assembler'/'style.css').write_text('Theme Name: Assembler\nVersion: 0.0.126')
    (stage/'mounts'/'assembler'/'templates').mkdir()
    (stage/'mounts'/'assembler'/'templates'/'index.html').write_text('<!-- wp:group /-->')
    (stage/'mounts'/'fv-ex2-private-preview').mkdir(parents=True)
    private_mount=stage/'mounts'/'fv-ex2-private-preview'
    private_mount.joinpath('fv-ex2-private-preview.php').write_bytes(source_php.read_bytes())
    private_mount.joinpath('fv-ex2-private-payload.php').write_bytes(expected_php_payload({name:(upstream/name).read_bytes() for name in SOURCE_ASSETS}))
    manifest={'release_status':'HOLD_UNPUBLISHED_STAGING_ONLY','expected_git_head_given_by_caller':head,
              'payload_sha256':sha(private_mount.joinpath('fv-ex2-private-payload.php').read_bytes()),
              'source_hashes':{name:sha((upstream/name).read_bytes()) for name in SOURCE_ASSETS}}
    private_mount.joinpath('STAGING_MANIFEST.json').write_text(json.dumps(manifest))
    private_mount.joinpath('INSTALLATION_HOLD.txt').write_text('NOT FOR INSTALLATION')
    theme_zip=root/'official-assembler-source.zip'
    with zipfile.ZipFile(theme_zip,'w') as archive:
        for f in sorted((stage/'mounts'/'assembler').rglob('*')):
            if f.is_file(): archive.write(f, 'assembler/'+f.relative_to(stage/'mounts'/'assembler').as_posix())
    plugin_zip=stage/'private-preview-release-HOLD.zip'
    with zipfile.ZipFile(plugin_zip,'w') as archive:
        for f in sorted(private_mount.rglob('*')):
            if f.is_file(): archive.write(f, 'fv-ex2-private-preview/'+f.relative_to(private_mount).as_posix())
    theme_sha=sha(theme_zip.read_bytes())
    blueprint={'$schema':'https://playground.wordpress.net/blueprint-schema.json',
               'landingPage':'/?pagename=fv-ex2-playground-review', 'login':True,
               'steps':[{'step':'defineWpConfigConsts','consts':{'WP_ENVIRONMENT_TYPE':'local','FV_EX2_ALLOW_PREVIEW':True,'WP_DEBUG':True,'WP_DEBUG_DISPLAY':False}},
                        {'step':'activateTheme','themeFolderName':'assembler'},
                        {'step':'activatePlugin','pluginPath':'/wordpress/wp-content/plugins/fv-ex2-private-preview/fv-ex2-private-preview.php'},
                        {'step':'runPHP','code':CANONICAL_LOCAL_SEED}]}
    bytes_bp=(json.dumps(blueprint,indent=2)+'\n').encode()
    (stage/'playground-blueprint.json').write_bytes(bytes_bp)
    cli=['npx','@wp-playground/cli@latest','server',
         '--blueprint='+str(stage/'playground-blueprint.json'),
         '--mount='+str(stage/'mounts'/'assembler')+':/wordpress/wp-content/themes/assembler',
         '--mount='+str(stage/'mounts'/'fv-ex2-private-preview')+':/wordpress/wp-content/plugins/fv-ex2-private-preview',
         '--port=9400']
    (stage/'playground-cli-arguments.json').write_text(json.dumps(cli))
    receipt={'status':'LOCAL_PLAYGROUND_PREPARED_NOT_EXECUTED','release':'HOLD',
             'exact_git_head':head,'assembler_sha256_out_of_band_pin_verified':True,
             'wordpress_instance':'NOT_STARTED','blueprint_sha256':sha(bytes_bp),
             'assembler_zip_sha256':theme_sha, 'plugin_sha256':sha(plugin_zip.read_bytes())}
    (stage/'STAGING_PREP_RECEIPT.json').write_text(json.dumps(receipt))
    return temp, repo, head, stage, theme_zip, theme_sha


class UnifiedStageTests(unittest.TestCase):
    def test_safely_combines_existing_seven_chapter_preview_and_parity(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            receipt=bind(repo,head,stage,theme_zip,theme_sha)
            self.assertEqual(receipt['assembler_parity'],'MOUNTED_NOT_IMPORTED')
            bp=json.loads((stage/'playground-blueprint.json').read_text())
            self.assertEqual([s['step'] for s in bp['steps']],['defineWpConfigConsts','activateTheme','runPHP','activatePlugin','runPHP'])
            self.assertIn('apply_local_parity.php',bp['steps'][2]['code'])
            self.assertIn('fv-ex2-playground-review',bp['steps'][4]['code'])
            cli=json.loads((stage/'playground-cli-arguments.json').read_text())
            self.assertEqual(len([x for x in cli if x.startswith('--mount=')]),3)
            self.assertIn('fv-ex2-parity',json.dumps(cli))
            self.assertEqual(receipt['local_wp_import'],'NOT_EXECUTED')
            self.assertEqual(receipt['actual_wordpress_render'],'NOT_TESTED')
            self.assertEqual(receipt['release'],'HOLD')
            self.assertTrue((stage/'mounts'/'fv-ex2-parity'/'apply_local_parity.php').exists())
            self.assertEqual(len(receipt['parity_source_sha256']),6)

    def test_rerun_does_not_double_import(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            bind(repo,head,stage,theme_zip,theme_sha)
            with self.assertRaisesRegex(ValueError,'STAGE HOLD'):
                bind(repo,head,stage,theme_zip,theme_sha)

    def test_incorrect_head_is_refused(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp, self.assertRaises(ValueError): bind(repo,'f'*40,stage,theme_zip,theme_sha)

    def test_changed_tracked_sanitizer_is_refused(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            (repo/PARITY/'sanitize_theme_parity.py').write_text('print("unsafe")')
            with self.assertRaisesRegex(ValueError,'uncommitted parity source'):bind(repo,head,stage,theme_zip,theme_sha)

    def test_symlinked_source_is_refused(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            path=repo/PARITY/'apply_local_parity.php'
            original=path.read_text();path.unlink()
            alt=repo/'outside.php';alt.write_text(original)
            path.symlink_to(alt)
            with self.assertRaisesRegex(ValueError,'unsafe or absent'):bind(repo,head,stage,theme_zip,theme_sha)

    def test_reject_unexpected_css_outbound_request(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            path=repo/PARITY/'assembler-public-safe.json';data=json.loads(path.read_text())
            data['global_styles']['styles']['css']+='@import url(https://tracker.invalid/style.css);'
            path.write_text(json.dumps(data))
            # Git custody must reject even before semantic validation.
            with self.assertRaisesRegex(ValueError,'uncommitted parity source'):bind(repo,head,stage,theme_zip,theme_sha)

    def test_catches_sanitizer_bypass_in_committed_manifest(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            path=repo/PARITY/'assembler-public-safe.json';data=json.loads(path.read_text())
            data['template_content']['footer']+='<!-- wp:html --><script>posthog.init("x")</script><!-- /wp:html -->'
            path.write_text(json.dumps(data))
            subprocess.run(['git','-C',str(repo),'add','.'],check=True)
            subprocess.run(['git','-C',str(repo),'-c','user.name=FV','-c','user.email=fv@example.invalid','commit','-qm','New malicious head'],check=True)
            new_head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
            receipt_path=stage/'STAGING_PREP_RECEIPT.json';receipt=json.loads(receipt_path.read_text());receipt['exact_git_head']=new_head;receipt_path.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError,'executable'):bind(repo,new_head,stage,theme_zip,theme_sha)

    def test_reject_dirty_stage_blueprint(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            bp=stage/'playground-blueprint.json';bp.write_text(bp.read_text()+'\n')
            with self.assertRaisesRegex(ValueError,'Blueprint was modified'):bind(repo,head,stage,theme_zip,theme_sha)

    def test_reject_production_environment_even_with_renamed_hash(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            p=stage/'playground-blueprint.json';bp=json.loads(p.read_text());bp['steps'][0]['consts']['WP_ENVIRONMENT_TYPE']='production'
            raw=(json.dumps(bp)+'\n').encode();p.write_bytes(raw)
            rec=stage/'STAGING_PREP_RECEIPT.json';data=json.loads(rec.read_text());data['blueprint_sha256']=sha(raw);rec.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'not a local-only'):bind(repo,head,stage,theme_zip,theme_sha)

    def test_reject_untrusted_external_mount(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            cli=stage/'playground-cli-arguments.json';data=json.loads(cli.read_text())
            data.append('--mount=/private/secrets:/wordpress/wp-content');cli.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'unexpected CLI flag'):bind(repo,head,stage,theme_zip,theme_sha)

    def test_reject_missing_theme_binary(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            (stage/'mounts'/'assembler'/'style.css').unlink()
            with self.assertRaisesRegex(ValueError,'unsafe theme/plugin entry point'):bind(repo,head,stage,theme_zip,theme_sha)


    def test_reject_cli_public_bind_even_with_existing_original_flags(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            p=stage/'playground-cli-arguments.json'
            argv=json.loads(p.read_text());argv.append('--host=0.0.0.0');p.write_text(json.dumps(argv))
            with self.assertRaisesRegex(ValueError,'unexpected CLI flag'): bind(repo,head,stage,theme_zip,theme_sha)

    def test_reject_cli_external_wordpress_url(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            p=stage/'playground-cli-arguments.json'
            argv=json.loads(p.read_text());argv.append('--site-url=https://finalvestige.com');p.write_text(json.dumps(argv))
            with self.assertRaisesRegex(ValueError,'unexpected CLI flag'): bind(repo,head,stage,theme_zip,theme_sha)

    def test_reject_cli_duplicate_blueprint_override(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            p=stage/'playground-cli-arguments.json'
            argv=json.loads(p.read_text());argv.append('--blueprint=/private/other.json');p.write_text(json.dumps(argv))
            with self.assertRaisesRegex(ValueError,'unexpected CLI flag'): bind(repo,head,stage,theme_zip,theme_sha)

    def test_reject_blueprint_extra_php_action_even_if_receipt_hash_matches(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            p=stage/'playground-blueprint.json'
            bp=json.loads(p.read_text());bp['steps'][3]['code']+='file_get_contents("https://example.invalid/");'
            raw=(json.dumps(bp)+'\n').encode();p.write_bytes(raw)
            r=stage/'STAGING_PREP_RECEIPT.json';receipt=json.loads(r.read_text());receipt['blueprint_sha256']=sha(raw);r.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError,'changed local-only preview seed'):bind(repo,head,stage,theme_zip,theme_sha)

    def test_reject_blueprint_extra_import_action_even_with_matching_hash(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            p=stage/'playground-blueprint.json'
            bp=json.loads(p.read_text());bp['steps'][2]['dangerous']='unexpected'
            raw=(json.dumps(bp)+'\n').encode();p.write_bytes(raw)
            r=stage/'STAGING_PREP_RECEIPT.json';receipt=json.loads(r.read_text());receipt['blueprint_sha256']=sha(raw);r.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError,'private preview plugin action'):bind(repo,head,stage,theme_zip,theme_sha)

    def test_reject_external_mount_root_symlink_and_prevent_external_writes(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            external=stage.parent/'other-folder'
            (stage/'mounts').rename(external)
            (stage/'mounts').symlink_to(external, target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'unsafe mounts root'):bind(repo,head,stage,theme_zip,theme_sha)
            self.assertFalse((external/'fv-ex2-parity').exists())

    def test_reject_theme_entry_point_symlink(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            p=stage/'mounts'/'assembler'/'style.css';raw=p.read_text();p.unlink()
            outside=stage.parent/'style.css';outside.write_text(raw)
            p.symlink_to(outside)
            with self.assertRaisesRegex(ValueError,'unsafe theme/plugin entry point'):bind(repo,head,stage,theme_zip,theme_sha)

    def test_reject_stage_root_symlink(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            alias=stage.parent/'stage_alias';alias.symlink_to(stage, target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'stage root cannot be a symlink'):bind(repo,head,alias,theme_zip,theme_sha)

    def test_reject_blueprint_remote_landing_page(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            p=stage/'playground-blueprint.json'
            bp=json.loads(p.read_text());bp['landingPage']='https://finalvestige.com/'
            raw=(json.dumps(bp)+'\n').encode();p.write_bytes(raw)
            r=stage/'STAGING_PREP_RECEIPT.json';receipt=json.loads(r.read_text());receipt['blueprint_sha256']=sha(raw);r.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError,'Blueprint top-level action or URL'):bind(repo,head,stage,theme_zip,theme_sha)

    def test_plugin_payload_replacement_is_rejected_before_parity_write(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            (stage/'mounts'/'fv-ex2-private-preview'/'fv-ex2-private-payload.php').write_text('<?php // altered')
            with self.assertRaisesRegex(ValueError, 'modified or unexpected private-preview'):
                bind(repo,head,stage,theme_zip,theme_sha)
            self.assertFalse((stage/'mounts'/'fv-ex2-parity').exists())

    def test_theme_extra_php_code_is_rejected(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            (stage/'mounts'/'assembler'/'surprise.php').write_text('<?php file_get_contents("https://example.invalid/");')
            with self.assertRaisesRegex(ValueError, 'modified or unexpected assembler'):
                bind(repo,head,stage,theme_zip,theme_sha)

    def test_theme_style_mutation_is_rejected(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            with (stage/'mounts'/'assembler'/'style.css').open('a') as f: f.write('\nbody{display:none}')
            with self.assertRaisesRegex(ValueError, 'modified or unexpected assembler'):
                bind(repo,head,stage,theme_zip,theme_sha)

    def test_theme_subdir_symlink_is_rejected(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            path=stage/'mounts'/'assembler'/'templates'/'index.html'
            path.unlink()
            path.symlink_to(repo/'experience2/home-flagship/index.html')
            with self.assertRaisesRegex(ValueError, 'symlink or path escape'):
                bind(repo,head,stage,theme_zip,theme_sha)

    def test_theme_missing_nested_template_is_rejected(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            (stage/'mounts'/'assembler'/'templates'/'index.html').unlink()
            with self.assertRaisesRegex(ValueError, 'missing assembler extracted files'):
                bind(repo,head,stage,theme_zip,theme_sha)

    def test_independently_supplied_theme_pin_required(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            with self.assertRaisesRegex(ValueError, 'independently pinned'):
                bind(repo,head,stage,theme_zip, '0'*64)

    def test_private_plugin_zip_mutation_with_receipt_rehash_rejected_by_commit(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            plugin=stage/'private-preview-release-HOLD.zip'
            source=stage/'mounts'/'fv-ex2-private-preview'
            source.joinpath('fv-ex2-private-preview.php').write_text('<?php // hostile replacement')
            with zipfile.ZipFile(plugin,'w') as z:
                for f in sorted(source.rglob('*')):
                    if f.is_file(): z.write(f, 'fv-ex2-private-preview/'+f.relative_to(source).as_posix())
            receipt_file=stage/'STAGING_PREP_RECEIPT.json'
            rec=json.loads(receipt_file.read_text()); rec['plugin_sha256']=sha(plugin.read_bytes())
            receipt_file.write_text(json.dumps(rec))
            with self.assertRaisesRegex(ValueError, 'staged PHP differs from exact Git HEAD'):
                bind(repo,head,stage,theme_zip,theme_sha)

    def test_plugin_manifest_asset_hash_mismatch_is_rejected_even_after_rezip(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            plugin=stage/'private-preview-release-HOLD.zip'
            source=stage/'mounts'/'fv-ex2-private-preview'
            manifest_file=source/'STAGING_MANIFEST.json'
            manifest=json.loads(manifest_file.read_text());manifest['source_hashes']['index.html']='0'*64
            manifest_file.write_text(json.dumps(manifest))
            with zipfile.ZipFile(plugin,'w') as z:
                for f in sorted(source.rglob('*')):
                    if f.is_file():z.write(f,'fv-ex2-private-preview/'+f.relative_to(source).as_posix())
            receipt_file=stage/'STAGING_PREP_RECEIPT.json'
            rec=json.loads(receipt_file.read_text());rec['plugin_sha256']=sha(plugin.read_bytes())
            receipt_file.write_text(json.dumps(rec))
            with self.assertRaisesRegex(ValueError, 'plugin manifest differs from canonical asset index.html'):
                bind(repo,head,stage,theme_zip,theme_sha)

    def test_repacked_php_payload_with_rehashed_manifest_and_receipt_still_fails_exact_source(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            plugin=stage/'private-preview-release-HOLD.zip'
            source=stage/'mounts'/'fv-ex2-private-preview'
            payload_file=source/'fv-ex2-private-payload.php'
            payload_file.write_bytes(payload_file.read_bytes()+b'\n<?php // injected')
            manifest_file=source/'STAGING_MANIFEST.json'
            manifest=json.loads(manifest_file.read_text())
            manifest['payload_sha256']=sha(payload_file.read_bytes())
            manifest_file.write_text(json.dumps(manifest))
            with zipfile.ZipFile(plugin,'w') as z:
                for f in sorted(source.rglob('*')):
                    if f.is_file():z.write(f,'fv-ex2-private-preview/'+f.relative_to(source).as_posix())
            receipt_file=stage/'STAGING_PREP_RECEIPT.json'
            rec=json.loads(receipt_file.read_text());rec['plugin_sha256']=sha(plugin.read_bytes())
            receipt_file.write_text(json.dumps(rec))
            with self.assertRaisesRegex(ValueError, 'payload bytes differ from exact committed'):
                bind(repo,head,stage,theme_zip,theme_sha)

    def test_private_archive_absent_is_rejected(self):
        temp,repo,head,stage,theme_zip,theme_sha=fixture()
        with temp:
            (stage/'private-preview-release-HOLD.zip').unlink()
            with self.assertRaisesRegex(ValueError,'missing private-preview source archive'):
                bind(repo,head,stage,theme_zip,theme_sha)

    def test_php_importer_syntax_is_valid(self):
        p=subprocess.run(['php','-l',str(HERE/'apply_local_parity.php')],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)


if __name__ == '__main__':unittest.main()

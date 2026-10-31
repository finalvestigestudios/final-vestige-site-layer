"""Offline regression tests; fixture is NOT a running WordPress/Playground instance."""
from __future__ import annotations
import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from prepare_unified_playground import bind, verify_sources, verify_parity, verify_stage, sha, PARITY

HERE = Path(__file__).parent
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
    subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True)
    subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(repo), '-c','user.name=FV Test','-c','user.email=fv@example.invalid','commit','-qm','Fixture'],check=True)
    head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    stage=root/'stage'
    (stage/'mounts'/'assembler').mkdir(parents=True)
    (stage/'mounts'/'assembler'/'style.css').write_text('Theme Name: Assembler\nVersion: 0.0.126')
    (stage/'mounts'/'fv-ex2-private-preview').mkdir(parents=True)
    (stage/'mounts'/'fv-ex2-private-preview'/'fv-ex2-private-preview.php').write_text('<?php // fixture guarded preview ?>')
    blueprint={'$schema':'https://playground.wordpress.net/blueprint-schema.json',
               'steps':[{'step':'defineWpConfigConsts','consts':{'WP_ENVIRONMENT_TYPE':'local','FV_EX2_ALLOW_PREVIEW':True}},
                        {'step':'activateTheme','themeFolderName':'assembler'},
                        {'step':'activatePlugin','pluginPath':'/wordpress/wp-content/plugins/fv-ex2-private-preview/fv-ex2-private-preview.php'},
                        {'step':'runPHP','code':"<?php $slug='fv-ex2-playground-review';"}]}
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
             'wordpress_instance':'NOT_STARTED','blueprint_sha256':sha(bytes_bp)}
    (stage/'STAGING_PREP_RECEIPT.json').write_text(json.dumps(receipt))
    return temp, repo, head, stage


class UnifiedStageTests(unittest.TestCase):
    def test_safely_combines_existing_seven_chapter_preview_and_parity(self):
        temp,repo,head,stage=fixture()
        with temp:
            receipt=bind(repo,head,stage)
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
        temp,repo,head,stage=fixture()
        with temp:
            bind(repo,head,stage)
            with self.assertRaisesRegex(ValueError,'STAGE HOLD'):
                bind(repo,head,stage)

    def test_incorrect_head_is_refused(self):
        temp,repo,head,stage=fixture()
        with temp, self.assertRaises(ValueError): bind(repo,'f'*40,stage)

    def test_changed_tracked_sanitizer_is_refused(self):
        temp,repo,head,stage=fixture()
        with temp:
            (repo/PARITY/'sanitize_theme_parity.py').write_text('print("unsafe")')
            with self.assertRaisesRegex(ValueError,'uncommitted parity source'):bind(repo,head,stage)

    def test_symlinked_source_is_refused(self):
        temp,repo,head,stage=fixture()
        with temp:
            path=repo/PARITY/'apply_local_parity.php'
            original=path.read_text();path.unlink()
            alt=repo/'outside.php';alt.write_text(original)
            path.symlink_to(alt)
            with self.assertRaisesRegex(ValueError,'unsafe or absent'):bind(repo,head,stage)

    def test_reject_unexpected_css_outbound_request(self):
        temp,repo,head,stage=fixture()
        with temp:
            path=repo/PARITY/'assembler-public-safe.json';data=json.loads(path.read_text())
            data['global_styles']['styles']['css']+='@import url(https://tracker.invalid/style.css);'
            path.write_text(json.dumps(data))
            # Git custody must reject even before semantic validation.
            with self.assertRaisesRegex(ValueError,'uncommitted parity source'):bind(repo,head,stage)

    def test_catches_sanitizer_bypass_in_committed_manifest(self):
        temp,repo,head,stage=fixture()
        with temp:
            path=repo/PARITY/'assembler-public-safe.json';data=json.loads(path.read_text())
            data['template_content']['footer']+='<!-- wp:html --><script>posthog.init("x")</script><!-- /wp:html -->'
            path.write_text(json.dumps(data))
            subprocess.run(['git','-C',str(repo),'add','.'],check=True)
            subprocess.run(['git','-C',str(repo),'-c','user.name=FV','-c','user.email=fv@example.invalid','commit','-qm','New malicious head'],check=True)
            new_head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
            receipt_path=stage/'STAGING_PREP_RECEIPT.json';receipt=json.loads(receipt_path.read_text());receipt['exact_git_head']=new_head;receipt_path.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError,'executable'):bind(repo,new_head,stage)

    def test_reject_dirty_stage_blueprint(self):
        temp,repo,head,stage=fixture()
        with temp:
            bp=stage/'playground-blueprint.json';bp.write_text(bp.read_text()+'\n')
            with self.assertRaisesRegex(ValueError,'Blueprint was modified'):bind(repo,head,stage)

    def test_reject_production_environment_even_with_renamed_hash(self):
        temp,repo,head,stage=fixture()
        with temp:
            p=stage/'playground-blueprint.json';bp=json.loads(p.read_text());bp['steps'][0]['consts']['WP_ENVIRONMENT_TYPE']='production'
            raw=(json.dumps(bp)+'\n').encode();p.write_bytes(raw)
            rec=stage/'STAGING_PREP_RECEIPT.json';data=json.loads(rec.read_text());data['blueprint_sha256']=sha(raw);rec.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'not a local-only'):bind(repo,head,stage)

    def test_reject_untrusted_external_mount(self):
        temp,repo,head,stage=fixture()
        with temp:
            cli=stage/'playground-cli-arguments.json';data=json.loads(cli.read_text())
            data.append('--mount=/private/secrets:/wordpress/wp-content');cli.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'paths point outside'):bind(repo,head,stage)

    def test_reject_missing_theme_binary(self):
        temp,repo,head,stage=fixture()
        with temp:
            (stage/'mounts'/'assembler'/'style.css').unlink()
            with self.assertRaisesRegex(ValueError,'theme/plugin/preview'):bind(repo,head,stage)

    def test_php_importer_syntax_is_valid(self):
        p=subprocess.run(['php','-l',str(HERE/'apply_local_parity.php')],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)


if __name__ == '__main__':unittest.main()

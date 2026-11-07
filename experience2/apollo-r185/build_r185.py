#!/usr/bin/env python3
"""R185: deterministic R184 -> early-style WordPress staging candidate.
No WP/site writes; generated assets in ignored local dist only. No network.
"""
from pathlib import Path
import hashlib, importlib.util, json, shutil, sys

HERE=Path(__file__).resolve().parent
R184=HERE.parent/'apollo-r184'
OUT=HERE/'dist'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def render_php(html_sha, css_sha):
    template=r'''<?php
/**
 * Plugin Name: FV Apollo Experience 2 Atlas (staging R185)
 * Description: Draft only: verified, early-loaded Apollo 1 research shortcode. Never activate in production without governed acceptance.
 * Version: 0.1.0-r185
 */
if (!defined('ABSPATH')) { exit; }

function fv_ex2_r185_fallback() {
    return '<p class="fv-apollo-fallback">The Apollo evidence Atlas is unavailable here. '
        . '<a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the original investigation</a>.</p>';
}
function fv_ex2_r185_assets_ok() {
    $root=plugin_dir_path(__FILE__);
    $html=$root.'templates/atlas-fragment.html';
    $css=$root.'assets/atlas-scoped.css';
    return is_readable($html) && is_readable($css)
        && hash_file('sha256',$html)==='__HTML__'
        && hash_file('sha256',$css)==='__CSS__';
}
function fv_ex2_r185_enqueue() {
    // Style is small, fully scoped, and only loaded when an actual singular post contains the shortcode.
    if (!fv_ex2_r185_assets_ok()) return false;
    wp_enqueue_style('fv-apollo-r185',plugins_url('assets/atlas-scoped.css',__FILE__),array(),'__VERSION__');
    return true;
}
function fv_ex2_r185_preflight() {
    // wp_enqueue_scripts runs before wp_head's stylesheet printing, unlike the_content shortcodes.
    if (is_admin() || !is_singular()) return;
    $post=get_queried_object();
    if (!($post instanceof WP_Post)) return;
    if (has_shortcode($post->post_content,'fv_ex2_apollo_atlas')) fv_ex2_r185_enqueue();
}
add_action('wp_enqueue_scripts','fv_ex2_r185_preflight',20);

function fv_ex2_r185_render($atts=array(),$content=null) {
    static $rendered=false;
    if ($rendered || !fv_ex2_r185_assets_ok()) return fv_ex2_r185_fallback();
    // Any rendering path not known before wp_head fails open to the free investigation,
    // rather than returning unstyled content or depending on late footer CSS delivery.
    if (!wp_style_is('fv-apollo-r185','enqueued')) {
        if (did_action('wp_head')) return fv_ex2_r185_fallback();
        if (!fv_ex2_r185_enqueue()) return fv_ex2_r185_fallback();
    }
    $html=file_get_contents(plugin_dir_path(__FILE__).'templates/atlas-fragment.html');
    if ($html===false) return fv_ex2_r185_fallback();
    $rendered=true; // Prevent duplicate IDs when the same shortcode appears twice.
    return $html;
}
add_shortcode('fv_ex2_apollo_atlas','fv_ex2_r185_render');
'''
    return template.replace('__HTML__',html_sha).replace('__CSS__',css_sha).replace('__VERSION__',css_sha[:12])

def build(use_existing_r184=False):
    rdist=R184/'dist'
    if not use_existing_r184:
        builder=R184/'build_wp_atlas.py'
        spec=importlib.util.spec_from_file_location('r184_builder',builder)
        if spec is None or spec.loader is None:raise RuntimeError('Missing R184 builder')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.build()
    manifest=json.loads((rdist/'manifest.json').read_text())
    if manifest.get('r183_html_sha256')!='dd09aaeefa1326d2c1ab42d7084a6525a048c167e7de8e013f53c930486b2b27':
        raise RuntimeError('Source custody failed: R183 HTML mismatch')
    html=rdist/'templates/atlas-fragment.html'; css=rdist/'assets/atlas-scoped.css'
    if sha(html)!=manifest['fragment_sha256'] or sha(css)!=manifest['css_sha256']:
        raise RuntimeError('R184 asset manifest mismatch')
    (OUT/'templates').mkdir(parents=True,exist_ok=True)
    (OUT/'assets').mkdir(parents=True,exist_ok=True)
    shutil.copyfile(html,OUT/'templates/atlas-fragment.html')
    shutil.copyfile(css,OUT/'assets/atlas-scoped.css')
    phppath=OUT/'fv-ex2-apollo-r185.php'
    phppath.write_text(render_php(sha(html),sha(css)),encoding='utf-8')
    result={'r183_html_sha256':manifest['r183_html_sha256'],
            'r184_fragment_sha256':sha(html),'r184_css_sha256':sha(css),
            'r185_php_sha256':sha(phppath),'mode':'UNPUBLISHED_STAGING_HOLD',
            'wp_installed':False,'axe_executed':False,'sales_verified':False}
    (OUT/'manifest.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return result

if __name__=='__main__':
    print(json.dumps(build(use_existing_r184='--reuse-r184-dist' in sys.argv),indent=2))

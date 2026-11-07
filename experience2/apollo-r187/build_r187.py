#!/usr/bin/env python3
"""R187 isolated Atlas shortcode: Gutenberg synced-pattern early CSS detection.

Builds only to local ignored dist/. R186 HTML/CSS/PHP are byte-pinned and
preserved in every generated R187 asset. No remote resources or CMS writes.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R186 = HERE.parent / 'apollo-r186'
OUT = HERE / 'dist'
PIN = {
    'php': '25f7acfe36a4e81c44e3b91cd594706539e76506b3abc44d8e0e50d082f45cd5',
    'html': 'f368766a4b8058208c524f5809f975ba859a108090923de6d6d8e2b59653c315',
    'css': 'dddb5a73a58d266f5d5dc67f88b7114c15fb8736134b2c345126717f91c1d7b6',
}

# Bound CPU/database reads in malformed, recursive or hostile block content.
# WordPress core stores synced patterns as core/block refs to wp_block posts.
SCAN = '''/**
 * Scan a bounded Gutenberg block tree for the Apollo shortcode in synced
 * patterns (core/block refs). Direct shortcodes are detected first.
 * The scan is read-only: no WP content/option writes or template mutation.
 */
function fv_ex2_r187_scan_blocks($blocks, &$seen, &$budget, $depth) {
    if ($depth > 12 || $budget <= 0 || !is_array($blocks)) return false;
    foreach ($blocks as $block) {
        if (--$budget < 0) return false;
        if (!is_array($block)) continue;
        if (isset($block['blockName']) && $block['blockName'] === 'core/block') {
            $attrs = isset($block['attrs']) && is_array($block['attrs']) ? $block['attrs'] : array();
            $ref = isset($attrs['ref']) && is_int($attrs['ref']) ? $attrs['ref'] : 0;
            if ($ref > 0 && !isset($seen[$ref])) {
                $seen[$ref] = true; // Cycle guard, including nested/self references.
                $reusable = get_post($ref);
                if ($reusable instanceof WP_Post && $reusable->post_type === 'wp_block'
                    && fv_ex2_r187_has_target($reusable->post_content, $seen, $budget, $depth + 1)) {
                    return true;
                }
            }
        }
        if (!empty($block['innerBlocks'])
            && fv_ex2_r187_scan_blocks($block['innerBlocks'], $seen, $budget, $depth + 1)) return true;
    }
    return false;
}
function fv_ex2_r187_has_target($content, &$seen, &$budget, $depth = 0) {
    if (!is_string($content) || $depth > 12 || $budget <= 0) return false;
    if (has_shortcode($content, 'fv_ex2_apollo_atlas')) return true;
    // Do not parse non-block pages; do not assume synced blocks can be found
    // by searching only the currently requested post's raw post_content.
    if (strpos($content, '<!-- wp:') === false || !function_exists('parse_blocks')) return false;
    return fv_ex2_r187_scan_blocks(parse_blocks($content), $seen, $budget, $depth);
}

'''
NEEDLE = "    if (has_shortcode($post->post_content,'fv_ex2_apollo_atlas')) fv_ex2_r186_enqueue();"
REPLACEMENT = "    $seen = array(); $budget = 96;\n    if (fv_ex2_r187_has_target($post->post_content, $seen, $budget)) fv_ex2_r187_enqueue();"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def patch(original):
    text = original.decode('utf-8')
    if text.count(NEEDLE) != 1 or text.count('function fv_ex2_r186_preflight()') != 1:
        raise ValueError('R186 preflight did not match exactly; stop instead of guessing')
    text = text.replace('r186', 'r187').replace('R186', 'R187')
    anchor = 'function fv_ex2_r187_preflight() {'
    if text.count(anchor) != 1:
        raise ValueError('Wrong WordPress preflight insertion point')
    text = text.replace(anchor, SCAN + anchor, 1)
    text = text.replace(NEEDLE.replace('r186', 'r187'), REPLACEMENT, 1)
    if text.count('function fv_ex2_r187_has_target') != 1:
        raise ValueError('Scanner was not installed exactly once')
    return text.encode('utf-8')


def build(reuse=False):
    if not reuse:
        spec = importlib.util.spec_from_file_location('apollo_r186', R186 / 'build_r186.py')
        if spec is None or spec.loader is None:
            raise RuntimeError('Exact R186 builder missing')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build()
    root = R186 / 'dist'
    data = {
        'php': (root / 'fv-ex2-apollo-r186.php').read_bytes(),
        'html': (root / 'templates/atlas-fragment.html').read_bytes(),
        'css': (root / 'assets/atlas-scoped.css').read_bytes(),
    }
    for key, blob in data.items():
        if sha(blob) != PIN[key]:
            raise ValueError(f'R186 {key} SHA-256 mismatch; refusing build')
    php = patch(data['php'])
    (OUT / 'templates').mkdir(parents=True, exist_ok=True)
    (OUT / 'assets').mkdir(parents=True, exist_ok=True)
    (OUT / 'templates/atlas-fragment.html').write_bytes(data['html'])
    (OUT / 'assets/atlas-scoped.css').write_bytes(data['css'])
    (OUT / 'fv-ex2-apollo-r187.php').write_bytes(php)
    manifest = {
        'r186_pins_sha256': PIN,
        'r187_php_sha256': sha(php),
        'r187_html_sha256': sha(data['html']),
        'r187_css_sha256': sha(data['css']),
        'change': 'bounded synced-pattern/core-block pre-head stylesheet discovery',
        'browser_environment': 'local PHP WordPress-function harness plus Chromium, NOT installed WP',
        'installed_wordpress_tested': False,
        'axe_executed': False,
        'live': False,
        'paid_orders_verified': False,
    }
    (OUT / 'manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    print(json.dumps(build(reuse='--reuse-r186-dist' in sys.argv), indent=2))

#!/usr/bin/env python3
"""R189 isolated cache-invariant Apollo campaign handoff; no WordPress writes."""
from pathlib import Path
import hashlib, json, subprocess, sys

ROOT = Path(__file__).resolve().parent
R188 = ROOT.parent / 'apollo-r188'
OUT = ROOT / 'dist'
PIN = {
    'html': 'f368766a4b8058208c524f5809f975ba859a108090923de6d6d8e2b59653c315',
    'css': 'dddb5a73a58d266f5d5dc67f88b7114c15fb8736134b2c345126717f91c1d7b6',
}
DEST = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
JS = r'''/* Apollo R189: optional, first-party, cache-safe CTA context; no analytics or storage. */
(function () {
  'use strict';
  var DEST = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
  var SOURCES = ['youtube', 'tiktok', 'instagram', 'facebook', 'pinterest', 'x', 'bluesky'];
  function enhance() {
    try {
      var incoming = new URL(window.location.href).searchParams;
      var names = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
      var value = {};
      for (var i = 0; i < names.length; i++) {
        var entries = incoming.getAll(names[i]);
        if (entries.length !== 1) return; // reject incomplete / duplicated params
        value[names[i]] = entries[0];
      }
      if (SOURCES.indexOf(value.utm_source) === -1 ||
          value.utm_medium !== 'organic_social' ||
          !/^history_pilot_20\d{2}_(0[1-9]|1[0-2])$/.test(value.utm_campaign) ||
          !/^[a-z0-9][a-z0-9_-]{3,63}$/.test(value.utm_content)) return;
      var ctas = document.querySelectorAll('.fv-apollo-atlas a.cta');
      if (ctas.length !== 1) return;
      var anchor = ctas[0];
      if (anchor.getAttribute('href') !== DEST) return;
      var destination = new URL(DEST);
      for (var j = 0; j < names.length; j++) {
        destination.searchParams.set(names[j], value[names[j]]);
      }
      anchor.setAttribute('href', destination.href);
    } catch (_) { /* keep the original free investigation link usable */ }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhance, { once: true });
  } else enhance();
}());
'''

def digest(data):
    return hashlib.sha256(data).hexdigest()

def build(reuse=False):
    if not reuse:
        subprocess.run([sys.executable, str(R188 / 'build_r188.py')], check=True)
    original = {
        'php': (R188 / 'dist/fv-ex2-apollo-r188.php').read_bytes(),
        'html': (R188 / 'dist/templates/atlas-fragment.html').read_bytes(),
        'css': (R188 / 'dist/assets/atlas-scoped.css').read_bytes(),
    }
    for kind in ('html', 'css'):
        if digest(original[kind]) != PIN[kind]:
            raise RuntimeError('R188 historical source custody mismatch: ' + kind)
    html = original['html'].decode('utf-8')
    if html.count('<a class="cta" href="' + DEST + '">') != 1:
        raise RuntimeError('Unexpected first-party reading CTA')
    php = original['php'].decode('utf-8')
    start_tag = 'function fv_ex2_r188_campaign_handoff($html) {'
    end_tag = 'function fv_ex2_r188_render('
    return_tag = 'return fv_ex2_r188_campaign_handoff($html);'
    style_tag = "wp_enqueue_style('fv-apollo-r188',plugins_url('assets/atlas-scoped.css',__FILE__),array(),'dddb5a73a58d');"
    if any(php.count(tag) != 1 for tag in (start_tag, end_tag, return_tag, style_tag)):
        raise RuntimeError('R188 PHP adapter no longer matches reviewed contract')
    start, end = php.index(start_tag), php.index(end_tag)
    if start >= end:
        raise RuntimeError('R188 handoff boundaries invalid')
    php = php[:start] + php[end:]
    php = php.replace(return_tag, 'return $html;')
    php = php.replace('r188', 'r189').replace('R188', 'R189')
    marker = style_tag.replace('r188', 'r189')
    script_sha = digest(JS.encode('utf-8'))
    php = php.replace("    $css=$root.'assets/atlas-scoped.css';",
                      "    $css=$root.'assets/atlas-scoped.css';\n    $js=$root.'assets/campaign-handoff.js';", 1)
    php = php.replace('return is_readable($html) && is_readable($css)',
                      "return is_readable($html) && is_readable($css) && is_readable($js)\n        && hash_file('sha256',$js)==='" + script_sha + "'", 1)
    php = php.replace(marker, marker + "\n    wp_enqueue_script('fv-apollo-r189-context',plugins_url('assets/campaign-handoff.js',__FILE__),array(),'" + script_sha[:12] + "',true);", 1)
    if '$_GET' in php or 'campaign_handoff($html)' in php or php.count('wp_enqueue_script(') != 1:
        raise RuntimeError('Server-varying HTML or missing optional JS handoff')
    (OUT / 'assets').mkdir(parents=True, exist_ok=True)
    (OUT / 'templates').mkdir(parents=True, exist_ok=True)
    (OUT / 'fv-ex2-apollo-r189.php').write_text(php, encoding='utf-8')
    (OUT / 'assets/campaign-handoff.js').write_text(JS, encoding='utf-8')
    (OUT / 'assets/atlas-scoped.css').write_bytes(original['css'])
    (OUT / 'templates/atlas-fragment.html').write_bytes(original['html'])
    output = {'php': digest(php.encode()), 'js': script_sha, **PIN}
    receipt = {'status': 'STAGING HOLD; no installed WordPress test',
               'base': 'R188 draft PR #1397', 'input_r188_sha256': {k:digest(v) for k,v in original.items()},
               'output_sha256': output, 'html_query_invariant': True,
               'no_js_original_cta': DEST, 'confirmed_orders': None, 'revenue': None,
               'axe_real': False, 'wp_installed': False}
    (OUT / 'manifest.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    return receipt

if __name__ == '__main__':
    print(json.dumps(build(reuse='--reuse-r188-dist' in sys.argv), indent=2))

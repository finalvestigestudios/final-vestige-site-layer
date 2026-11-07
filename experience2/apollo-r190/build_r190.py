#!/usr/bin/env python3
"""R190 Apollo: independent source-integrity gate; optional JS cannot suppress history."""
from pathlib import Path
import hashlib, json, subprocess, sys
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'apollo-r189'
OUT=ROOT/'dist'
EXPECTED={
'php':'f63f75fd295679cd70841092739cb166ec96dd3b922841c5ad12fa34e487dfcf',
'html':'f368766a4b8058208c524f5809f975ba859a108090923de6d6d8e2b59653c315',
'css':'dddb5a73a58d266f5d5dc67f88b7114c15fb8736134b2c345126717f91c1d7b6',
'js':'eeab075280948b771eecd4cb13cc04ed946ffc34fc059bd6ac0d16ba555e446b'}
PATHS={'php':'fv-ex2-apollo-r189.php','html':'templates/atlas-fragment.html',
       'css':'assets/atlas-scoped.css','js':'assets/campaign-handoff.js'}
def sha(x):return hashlib.sha256(x).hexdigest()
def once(data,old,new):
    if data.count(old)!=1:raise ValueError('R189 contract changed: '+old[:60])
    return data.replace(old,new)
def build(reuse=False):
    if not reuse:subprocess.run([sys.executable,str(PARENT/'build_r189.py')],check=True)
    data={k:(PARENT/'dist'/path).read_bytes() for k,path in PATHS.items()}
    for k,x in data.items():
        if sha(x)!=EXPECTED[k]:raise ValueError('Source pin mismatch '+k)
    php=data['php'].decode()
    # Defer campaign-continuity integrity to its own optional gate.
    php=once(php, "    $js=$root.'assets/campaign-handoff.js';\n", '')
    php=once(php,"return is_readable($html) && is_readable($css) && is_readable($js)",
             "return is_readable($html) && is_readable($css)")
    php=once(php,"        && hash_file('sha256',$js)==='"+EXPECTED['js']+"'\n",'')
    marker='function fv_ex2_r189_enqueue() {'
    php=once(php,marker,"""/** Campaign enrichment is optional; never hide source evidence if it fails. */
function fv_ex2_r189_optional_js_ok() {
    $js=plugin_dir_path(__FILE__).'assets/campaign-handoff.js';
    return is_readable($js) && hash_file('sha256',$js)==='eeab075280948b771eecd4cb13cc04ed946ffc34fc059bd6ac0d16ba555e446b';
}
"""+marker)
    script="    wp_enqueue_script('fv-apollo-r189-context',plugins_url('assets/campaign-handoff.js',__FILE__),array(),'eeab07528094',true);"
    php=once(php,script,'    if (fv_ex2_r189_optional_js_ok()) {\n'+script+'\n    }')
    php=once(php,"    if (!wp_style_is('fv-apollo-r189','enqueued')) {",
             "    if (!wp_style_is('fv-apollo-r189','enqueued') && !wp_style_is('fv-apollo-r189','done')) {")
    php=php.replace('r189','r190').replace('R189','R190')
    (OUT/'assets').mkdir(parents=True,exist_ok=True)
    (OUT/'templates').mkdir(parents=True,exist_ok=True)
    (OUT/'fv-ex2-apollo-r190.php').write_text(php)
    for key in ('html','css','js'):(OUT/PATHS[key]).write_bytes(data[key])
    receipt={'parent_exact_commit':'be63ae4f62e9463cb6e6e8af069806d2441e4227',
             'input_sha256':EXPECTED,'output_sha256':{k:sha((OUT/('fv-ex2-apollo-r190.php' if k=='php' else PATHS[k])).read_bytes()) for k in PATHS},
             'release':'STAGING HOLD','genuine_axe':False,'installed_wp':False,'paid_orders':None}
    (OUT/'manifest.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt
if __name__=='__main__':print(json.dumps(build('--reuse-r189-dist' in sys.argv),indent=2))

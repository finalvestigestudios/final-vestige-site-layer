#!/usr/bin/env python3
"""Execute actual staging plugin PHP in isolated WordPress function shims.
Negative control must fail against R293 historical artifact, which used 'r285'
asset version and an unversioned body-link fallback.
"""
import hashlib, json, os, re, subprocess, sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
PHP=BASE/'apollo-r281/apollo-source-experience.php'
CSS=BASE/'apollo-r281/assets/apollo-source-experience.css'
EXPECTED='r296-'+hashlib.sha256(CSS.read_bytes()).hexdigest()[:12]
TESTS=[]

def check(flag, label):
    if not flag: raise AssertionError(label)
    TESTS.append(label)

SHIM=r'''<?php
$case=$argv[1];$source=$argv[2];
define('ABSPATH', '/sandbox/');
function plugins_url($path,$file) {return $GLOBALS['case']==='existingQuery' ? '/assets/apollo-source-experience.css?v=old' : '/assets/apollo-source-experience.css';}
function is_singular(){return true;}
function get_post($id=null){return (object)['post_content'=>'[fv_apollo_source_experience]'];}
function has_shortcode($content,$tag){return strpos($content,'['.$tag)!==false;}
function add_action($event,$callback){}
function add_shortcode($name,$callback){}
function wp_style_is($handle,$state){return $state===$GLOBALS['case'];}
function wp_enqueue_style($handle,$src,$deps,$version){$GLOBALS['style_v']=$version;}
$GLOBALS['case']=$case;
require $source;
fv_r281_preflight();
$output=fv_r281_render();$again=fv_r281_render();
echo json_encode(['v'=>$GLOBALS['style_v']??null,'body'=>$output,'again'=>$again,
   'ver'=>FV_R294_STYLE_VERSION??null,'href'=>fv_r294_fallback_stylesheet_url()]);
'''
TMP=BASE/'apollo-r296/qa/.temp_cache_shim.php'
TMP.write_text(SHIM)
try:
    for scenario in ['enqueued','done','none','existingQuery']:
        raw=subprocess.run(['php',str(TMP),scenario,str(PHP)],text=True,capture_output=True,check=True)
        data=json.loads(raw.stdout)
        check(data['v']==EXPECTED,scenario+' enqueue version matches reviewed CSS sha256 prefix')
        check(data['ver']==EXPECTED,scenario+' constant version matches reviewed CSS sha256 prefix')
        check(data['body'].count('<link rel="stylesheet"')==(0 if scenario in ['enqueued','done'] else 1),scenario+' linked only in unqueued fallback')
        check(data['again'].count('<link rel="stylesheet"')==0,scenario+' duplicate shortcode adds no stylesheet')
        check('ver='+EXPECTED in data['href'],scenario+' direct CSS fallback URL cache keyed')
        if scenario=='existingQuery':check('&ver=' in data['href'], 'query-safe fallback delimiter')
        check('data-fv-evidence-status="editorial-review-pending"' in data['body'],scenario+' source integrity fallback not triggered')
    print('PASS',len(TESTS),'cache/source regression assertions on actual PHP')
    print('CSS sha256:',hashlib.sha256(CSS.read_bytes()).hexdigest())
    print('PHP sha256:',hashlib.sha256(PHP.read_bytes()).hexdigest())
    output=BASE/'QA/r296-php-cache-receipt.json'
    output.write_text(json.dumps({'status':'PASS','assertions':TESTS,'css_sha256':hashlib.sha256(CSS.read_bytes()).hexdigest(),
      'php_sha256':hashlib.sha256(PHP.read_bytes()).hexdigest(),'asset_version':EXPECTED},indent=2,sort_keys=True)+'\n')
finally:
    TMP.unlink(missing_ok=True)

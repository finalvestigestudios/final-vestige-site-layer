<?php
/**
 * R231 exact-GitHub-template smoke test, no WordPress or production writes.
 * php experience2/research-desk/qa/r231_smoke.php [normal|duplicate|tampered]
 * Emits a JSON receipt including HTML for the independent Playwright test.
 */
declare(strict_types=1);
error_reporting(E_ALL);
define('ABSPATH', '/offline-r231/');
$GLOBALS['hooks'] = []; $GLOBALS['assets'] = [];
function add_action($tag,$fn,$priority=10){$GLOBALS['hooks'][$tag][]=$fn;}
function add_shortcode($tag,$fn){$GLOBALS['shortcode']=$fn;}
function is_singular(){return true;}
function get_post(){return (object)['post_content'=>'<!-- wp:block {"ref":42} /-->'];}
function has_shortcode($s,$tag){return strpos($s,'['.$tag.']')!==false;}
function plugins_url($p,$f){return 'https://staging.invalid/experience2/research-desk/'.$p;}
function plugin_dir_path($f){return dirname($f).'/';}
function esc_url($s){return htmlspecialchars($s,ENT_QUOTES,'UTF-8');}
function did_action($s){return $s==='wp_head'?1:0;}
function wp_style_is($h,$s){return false;}
function wp_script_is($h,$s){return false;}
function wp_enqueue_style($h,$u,$d,$v){$GLOBALS['assets']['styles'][$h]=$u;}
function wp_enqueue_script($h,$u,$d,$v,$f){$GLOBALS['assets']['scripts'][$h]=$u;}
function r231_check($ok,$message){if(!$ok)throw new RuntimeException($message);}
$case=$argv[1]??'normal';
r231_check(in_array($case,['normal','duplicate','tampered'],true),'invalid case');
$base=dirname(__DIR__);
$tmp=sys_get_temp_dir().'/fv_r231_'.bin2hex(random_bytes(8));
mkdir($tmp,0700,true); mkdir($tmp.'/templates',0700,true);
$fn='ledger-r231-source-scope.html';
try {
    copy($base.'/fv-ex2-r231-runtime.php',$tmp.'/fv-ex2-r231-runtime.php');
    copy($base.'/templates/'.$fn,$tmp.'/templates/'.$fn);
    if($case==='tampered'){
        $p=$tmp.'/templates/'.$fn;
        $content=file_get_contents($p);
        r231_check(strpos($content,'altitude-chamber')!==false,'tamper trigger missing');
        file_put_contents($p,str_replace('altitude-chamber','unverified-photo',$content));
    }
    require $tmp.'/fv-ex2-r231-runtime.php';
    $first=fv_ex2_r231_shortcode();
    $second=$case==='duplicate'?fv_ex2_r231_shortcode():'';
    if($case==='tampered'){
        r231_check(strpos($first,'Research source viewer unavailable')!==false,'fail-open fallback absent');
        r231_check(strpos($first,'data-fvx-record')===false,'corrupt source rendered');
    }else{
        r231_check(substr_count($first,'data-fvx-record')===6,'six exact source cards required');
        r231_check(substr_count($first,'data-fvx-source-scope')===3,'three source-context corrections required');
        r231_check(substr_count($first,'Read original investigation')===1,'single original investigation CTA');
        foreach (['NASA 1966 altitude-chamber training photo','NASA 2017 Apollo 1 tribute photo',
                  '1967 Review Board fire chronology','NASA engineering response'] as $phrase){
            r231_check(strpos($first,$phrase)!==false,'required source separation missing: '.$phrase);
        }
        r231_check(strpos($first,'data-lat=')===false,'no unsourced geocoordinates');
        if($case==='duplicate'){
            r231_check(strpos($second,'fv-ex2-ledger-apollo1-copy-2-')!==false,'second namespace absent');
            r231_check(substr_count($first.$second,'<link rel="stylesheet"')===1,'duplicate late stylesheet');
        }
    }
    echo json_encode(['status'=>'PASS','case'=>$case,'first'=>$first,'second'=>$second,
        'assets'=>$GLOBALS['assets'],'template_git_blob'=>'0fd4f9ddadb3473110d2709a52332a78fa4ac04a'],
        JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR);
} finally {
    foreach ([$tmp.'/templates/'.$fn,$tmp.'/fv-ex2-r231-runtime.php'] as $p)if(is_file($p))unlink($p);
    @rmdir($tmp.'/templates'); @rmdir($tmp);
}

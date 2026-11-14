<?php
/** Non-production WordPress stub and adversarial custody contract. */
define('ABSPATH', true);
$enqueued_styles=[];$enqueued_scripts=[];$shortcodes=[];$actions=[];
$reusable = array();
$main = (object)['post_type'=>'post','post_content'=>''];
function is_singular(){return true;}
function get_post($id=null){global $main,$reusable;return $id===null?$main:($reusable[$id]??null);}
function has_shortcode($s,$name){return strpos($s,'['.$name)!==false;}
function add_shortcode($tag,$cb){global $shortcodes;$shortcodes[$tag]=$cb;}
function add_action($key,$cb,$priority=10){global $actions;$actions[$cb]=$priority;}
function wp_enqueue_style($handle,$src,$dependencies=[],$version=null){global $enqueued_styles;$enqueued_styles[$handle]=$src;}
function wp_enqueue_script($handle,$src,$dependencies=[],$version=null,$footer=null){global $enqueued_scripts;$enqueued_scripts[$handle]=$src;}
function plugins_url($name,$file){return 'https://staging.invalid/'.ltrim($name,'/');}
function parse_blocks($html){
  // Reusable-block stub tests only core/block ref values, not complete Gutenberg.
  preg_match_all('/<!-- wp:block \{"ref":([0-9]+)\} \/-->/', $html, $matches);
  return array_map(function($x){return ['blockName'=>'core/block','attrs'=>['ref'=>(int)$x]];},$matches[1]);
}
require dirname(__DIR__).'/source-custody.php';
function ok($x,$msg){if(!$x){fwrite(STDERR,"FAIL $msg\n");exit(1);} echo "PASS $msg\n";}
$pages=fv_apollo_r348_custody();
ok(count($pages)===8,'eight deduplicated canonical source pages');
ok(array_sum(array_map(fn($x)=>count($x['items']),$pages))===13,'thirteen entries preserved');
ok(count(array_filter($pages,fn($x)=>$x['approved']))===8,'all canonical URLs approved');
$bad=fv_apollo_r348_custody([['url'=>'https://www.nasa.gov.evil.example/records','label'=>'Fake','type'=>'Mock','limit'=>'Do not link']]);
ok(count($bad)===1 && !$bad[0]['approved'] && $bad[0]['url']==='','spoofed NASA hostname quarantined');
$bad2=fv_apollo_r348_custody([['url'=>'https://www.nasa.gov/unverified-document','label'=>'Unreviewed','type'=>'Mock','limit'=>'Do not link']]);
ok(!$bad2[0]['approved'] && $bad2[0]['url']==='','even NASA-hosted unreviewed page quarantined');
$bad3=fv_apollo_r348_custody([['url'=>'javascript:alert(1)','label'=>'Code','type'=>'Mock','limit'=>'Do not link']]);
ok(!$bad3[0]['approved'] && $bad3[0]['url']==='','active-script URL quarantined');
$markup=fv_apollo_r348_experience_shortcode();
ok(substr_count($markup,'data-fv-custody-source')===8,'eight approved outbound custody links');
ok(substr_count($markup,'data-fv-custody-print')===8,'eight print-only custody twins');
ok(substr_count($markup,'data-fv-r339-cta="editorial"')===1,'one editorial continuation CTA; zero commerce');
ok(strpos($markup,'data-geo-pin')===false && strpos($markup,'payhip.com')===false,'no speculative geo pins or commerce');

$main->post_content='[fv_apollo_experience_r348]';fv_apollo_r348_enqueue();
ok(count($enqueued_styles)===5&&count($enqueued_scripts)===1,'composite enqueues five scoped styles and one inherited JS');
$enqueued_styles=[];$enqueued_scripts=[];
$main->post_content='[fv_apollo_source_drawer_r348]';fv_apollo_r348_enqueue();
ok(array_keys($enqueued_styles)===['fv-apollo-r348-custody']&&count($enqueued_scripts)===0,'standalone enqueues custody CSS only');
$enqueued_styles=[];$enqueued_scripts=[];
$main->post_content='<!-- wp:block {"ref":42} /-->';
$reusable[42]=(object)['post_type'=>'wp_block','post_content'=>'<!-- wp:block {"ref":43} /-->'];
$reusable[43]=(object)['post_type'=>'wp_block','post_content'=>'[fv_apollo_experience_r348]<!-- wp:block {"ref":42} /-->'];
fv_apollo_r348_enqueue();
ok(count($enqueued_styles)===5 && count($enqueued_scripts)===1,'nested cyclic reusable blocks bounded; composite assets pre-head');
$seen=[];$flags=fv_apollo_r348_flags(str_repeat('a',500001),$seen);
ok($flags===[false,false],'oversize content does not trigger parser');
$seen=[];$flags=fv_apollo_r348_flags('<!-- wp:block {"ref":999} /-->',$seen);
ok($flags===[false,false],'missing block reference fails safely');
echo "R348 PHP STUB/ADVERSARIAL CONTRACT: PASS\n";

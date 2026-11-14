<?php
declare(strict_types=1);
define('ABSPATH', __DIR__);
$shortcodes=[]; $styles=[];
function add_shortcode($tag,$callback){global $shortcodes;$shortcodes[$tag]=$callback;}
function wp_enqueue_style($handle,$url,$deps,$version){global $styles;$styles[$handle]=compact('url','deps','version');}
function plugins_url($rel,$file){return 'https://staging.example.invalid/'.basename(dirname($file)).'/'.$rel;}
require_once dirname(__DIR__,2).'/apollo-r365/chrono-rail.php';
require_once dirname(__DIR__,2).'/apollo-r367/sealed-chronology.php';
require_once dirname(__DIR__).'/evidence-bridge.php';
$checks=0;$assert=function($ok,$what) use (&$checks) {++$checks;if(!$ok)throw new RuntimeException("FAIL: $what");};
$assert(isset($shortcodes['fv_apollo_educator_bridge_r369']),'shortcode registration');
$rows=fv_apollo_r365_rows();
$valid=fv_apollo_r369_render($rows);
$assert(str_contains($valid,'Follow the evidence before drawing the conclusion'),'educator landing title');
$assert(substr_count($valid,'class="fv-apollo-r369__lens"')===3,'three original pedagogy lenses');
$assert(substr_count($valid,'data-fv-nasa-source')===4,'NASA source links from sealed chronology');
$assert(substr_count($valid,'data-fv-free-cta')===1,'only one onward editorial CTA');
$assert(substr_count($valid,'data-fv-source-drawer')===4,'four accessible drawers');
$assert(!preg_match('~href=\"https?://(?:www\.)?(?:payhip\.com|checkout\.)~i',$valid),'no buy link');
$assert(!str_contains($valid,'<script') && !str_contains($valid,'<img'),'no new scripts or images');
$again=fv_apollo_r369_shortcode();
$assert(str_contains($again,'Follow the evidence before drawing the conclusion'),'shortcode canonical content');
$assert(!str_contains($valid,'fv-apollo-r369-2-title') && str_contains($again,'fv-apollo-r369-2-title'),'unique instance IDs');
foreach ([0,1,2,3] as $idx){
  foreach(['id','when','era','heading','supported','limit','source','source_title','published','class'] as $field){
    $bad=$rows;$bad[$idx][$field]='UNREVIEWED';
    $got=fv_apollo_r369_render($bad);
    $assert(!str_contains($got,'data-fv-nasa-source'),'tampering withholds citations '.$idx.'/'.$field);
    $assert(!str_contains($got,'fv-apollo-r369__lens'),'tampering withholds pedagogy '.$idx.'/'.$field);
    $assert(substr_count($got,'data-fv-free-cta')===1,'tampering retains one CTA '.$idx.'/'.$field);
  }
}
foreach(['reorder','delete','duplicate','insert','associative','notarray'] as $type){
  $bad=$rows;
  if($type==='reorder'){[$bad[0],$bad[1]]=[$bad[1],$bad[0]];}
  if($type==='delete'){array_pop($bad);}
  if($type==='duplicate'){$bad[1]=$bad[0];}
  if($type==='insert'){$bad[]= $bad[0];}
  if($type==='associative'){$bad=['x'=>$rows[0]];}
  if($type==='notarray'){$bad=null;}
  $got=fv_apollo_r369_render($bad);
  $assert(!str_contains($got,'data-fv-nasa-source') && substr_count($got,'data-fv-free-cta')===1,'sequence invalid '.$type);
}
fv_apollo_r369_enqueue();
$assert(isset($styles['fv-apollo-r369-educator-bridge']),'staging stylesheet enqueue');
$assert($styles['fv-apollo-r369-educator-bridge']['deps']===['fv-apollo-r368-reflow'],'CSS dependency');
echo "PASS $checks PHP assertions\n";

<?php
/** R433 - isolated, staging-only claim/rights bridge; never publishes or measures sales. */
if (!defined('ABSPATH')) { exit; }
const FV_R433_FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R433_PARENT_BLOBS = [
 'staging-custody-gate.php' => '749e708b018b3dddfdc5dab3897665ad2bde55ec',
 'assets/custody-gate.css' => '9c586627f8c7e7096b9d6be8ac646bb990478400'
];
function fv_r433_fallback(): string {
 return '<p class="fv-r433-fallback">The source review is unavailable. <a href="'.FV_R433_FREE.'">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r433_parent_verified(): bool {
 $base=realpath(dirname(__DIR__).'/apollo-r432');
 if ($base === false || is_link(dirname(__DIR__).'/apollo-r432')) return false;
 foreach (FV_R433_PARENT_BLOBS as $relative=>$sha) {
  $file=$base.'/'.$relative;
  if (is_link($file) || is_link(dirname($file)) || !is_file($file) || !is_readable($file)) return false;
  $real=realpath($file);
  if ($real === false || strncmp($real,$base.'/',strlen($base)+1)!==0) return false;
  $bytes=file_get_contents($file);
  if (!is_string($bytes) || !hash_equals($sha,sha1('blob '.strlen($bytes)."\0".$bytes))) return false;
 }
 return true;
}
function fv_r433_allowed(): bool {
 return defined('FV_R433_ENABLED') && FV_R433_ENABLED === true
 && defined('FV_R433_STAGING_PAGE_ID') && is_int(FV_R433_STAGING_PAGE_ID) && FV_R433_STAGING_PAGE_ID>0
 && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
 && function_exists('is_singular') && is_singular()
 && function_exists('get_queried_object_id') && get_queried_object_id() === FV_R433_STAGING_PAGE_ID;
}
function fv_r433_claims(): array {
 return [
  ['1967-01-27','Documented event','The Apollo 1 crew died during a ground test.','The event does not establish the original ignition spark.','https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'],
  ['1967-04-05','Board inference','The Board regarded an electrical arc as the most probable initiator.','The Board did not identify a single ignition source conclusively.','https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'],
  ['2018-02-14','Later retrospective','NASA later described 102 deliberate flammability ignitions conducted after the fire.','These experiments are not observations of the 1967 accident itself.','https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/']
 ];
}
function fv_r433_render(int $instance,array $campaign=[]): string {
 if($instance<1 || $instance>30 || !fv_r433_parent_verified()) return fv_r433_fallback();
 if(empty($GLOBALS['fv_r433_trusted_parent'])) {
  if(function_exists('fv_r432_render') || function_exists('fv_r431_render') || function_exists('fv_r430_render') || function_exists('fv_r429_render')) return fv_r433_fallback();
  require_once dirname(__DIR__).'/apollo-r432/staging-custody-gate.php';
  if(!function_exists('fv_r432_render')) return fv_r433_fallback();
  $GLOBALS['fv_r433_trusted_parent']=true;
 }
 $inner=fv_r432_render($instance,$campaign);
 if (substr_count($inner,'class="fv-r429__cta"')!==1 || substr_count($inner,'class="fv-r430__question"')!==3
     || substr_count($inner,'class="fv-r429__plate"')!==3 || substr_count($inner,'data-fv-r431-actions')!==1) return fv_r433_fallback();
 $id='fv-r433-'.$instance;
 $escape=static function(string $x):string{return htmlspecialchars($x,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8');};
 $out='<section class="fv-r433" data-fv-r433 aria-labelledby="'.$id.'-title">';
 $out.='<header class="fv-r433__head"><p class="fv-r433__eyebrow">SOURCE DESK / EVIDENCE CONFIDENCE</p><h2 id="'.$id.'-title">What the record tells us—and what it does not.</h2><p>Three different documentary roles are not three independent eyewitness accounts. Inspect the limitations before relying on a claim in a lesson.</p></header>';
 $out.='<ol class="fv-r433__claims">';
 foreach (fv_r433_claims() as $n=>$claim){[$date,$role,$fact,$boundary,$source]=$claim;
  $out.='<li class="fv-r433__claim"><p><strong>'.($n+1).'. '.$escape($role).'</strong> <time datetime="'.$escape($date).'">'.$escape($date).'</time></p><p>'.$escape($fact).'</p>';
  $out.='<details><summary>Evidence boundary and original source</summary><p>'.$escape($boundary).'</p><p><a href="'.$escape($source).'">Inspect the NASA record</a></p></details>';
  $out.='<p class="fv-r433__printlimit"><strong>Evidence boundary:</strong> '.$escape($boundary).'</p></li>';
 }
 $out.='</ol><p class="fv-r433__policy">The claims and original classroom activities are editorial work, not NASA authorization or endorsement. No NASA photographs or logos are reproduced, and no paid educator product is presented as purchasable without independent rights, checkout and fulfillment proof.</p>';
 $out.=$inner.'</section>';
 return $out;
}
function fv_r433_shortcode(): string {
 if(!fv_r433_allowed() || !fv_r433_parent_verified()) return fv_r433_fallback();
 $n=($GLOBALS['fv_r433_instances']??0)+1;
 if(!is_int($n) || $n>30) return fv_r433_fallback();
 $GLOBALS['fv_r433_instances']=$n;
 return fv_r433_render($n,$_GET);
}
function fv_r433_enqueue(): void {
 if(!fv_r433_allowed() || !fv_r433_parent_verified() || !function_exists('wp_enqueue_style') || !function_exists('plugins_url'))return;
 $base=[
  ['apollo-r429/assets/bridge.css','fv-r433-429',[]],
  ['apollo-r430/assets/educator-case-lab.css','fv-r433-430',['fv-r433-429']],
  ['apollo-r431/assets/evidence-notebook.css','fv-r433-431',['fv-r433-430']],
  ['apollo-r432/assets/custody-gate.css','fv-r433-432',['fv-r433-431']]
 ];
 foreach($base as [$path,$handle,$deps])wp_enqueue_style($handle,plugins_url('../'.$path,__FILE__),$deps,'r433-pinned-parent');
 wp_enqueue_style('fv-r433-confidence',plugins_url('assets/claim-bridge.css',__FILE__),['fv-r433-432'],'r433');
 if(function_exists('wp_enqueue_script'))wp_enqueue_script('fv-r433-private-notes',plugins_url('../apollo-r431/assets/evidence-notebook.js',__FILE__),[],'r433-pinned-parent',true);
}
if(function_exists('add_shortcode'))add_shortcode('fv_apollo_claim_bridge_r433','fv_r433_shortcode');
if(function_exists('add_action'))add_action('wp_enqueue_scripts','fv_r433_enqueue',20);

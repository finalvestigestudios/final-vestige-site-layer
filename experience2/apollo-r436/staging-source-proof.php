<?php
/** Apollo R436 / staging source-classification correction. No WordPress or commerce writes. */
if (!defined('ABSPATH')) { exit; }
const FV_R436_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R436_CSS_SHA256 = '15b871ac9dcedd20a726144756c7203fa7e6a789ecaed8b5a36cceabe6394df5';
const FV_R436_PARENT = [
 'apollo-r435/staging-photo-custody.php'=>'68f276e9d7ad8cb2eaa9d992379b497e6ce15ddd',
 'apollo-r435/assets/photo-custody.css'=>'fdd83485823f708e22230cc9ca9fa1c2368c11d9',
 'apollo-r435/source_catalog.json'=>'0c0401f651a24c8a1bec16980e519df9df9e6762'
];
function fv_r436_fallback(): string {
 return '<p class="fv-r436-fallback">The source comparison is unavailable. <a href="'.FV_R436_ARTICLE.'">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r436_allowed(): bool {
 return defined('FV_R436_ENABLED') && FV_R436_ENABLED === true
  && defined('FV_R436_STAGING_PAGE_ID') && is_int(FV_R436_STAGING_PAGE_ID) && FV_R436_STAGING_PAGE_ID > 0
  && function_exists('wp_get_environment_type') && wp_get_environment_type()==='staging'
  && function_exists('is_singular') && is_singular()
  && function_exists('get_queried_object_id') && get_queried_object_id()===FV_R436_STAGING_PAGE_ID;
}
function fv_r436_verify(): bool {
 $root=realpath(dirname(__DIR__));
 if ($root===false) return false;
 foreach (FV_R436_PARENT as $relative=>$want) {
  $path=dirname(__DIR__);
  foreach (explode('/',$relative) as $part) {
   $path.='/'.$part;
   if (is_link($path)) return false;
  }
  $resolved=realpath($path);
  if ($resolved===false || !is_file($resolved) || !is_readable($resolved)
   || strncmp($resolved,$root.DIRECTORY_SEPARATOR,strlen($root)+1)!==0) return false;
  $bytes=file_get_contents($resolved);
  if (!is_string($bytes) || !hash_equals($want,sha1('blob '.strlen($bytes)."\0".$bytes))) return false;
 }
 $css=__DIR__.'/assets/source-proof.css';
 if (is_link($css) || !is_file($css) || !is_readable($css)) return false;
 $cssbytes=file_get_contents($css);
 if (!is_string($cssbytes) || !hash_equals(FV_R436_CSS_SHA256,hash('sha256',$cssbytes))) return false;
 return true;
}
function fv_r436_parent(): bool {
 if (!fv_r436_verify()) return false;
 if (!function_exists('fv_r435_render')) {
  require_once dirname(__DIR__).'/apollo-r435/staging-photo-custody.php';
 }
 return function_exists('fv_r435_render') && function_exists('fv_r435_parent')
    && fv_r435_parent() && function_exists('fv_r435_verify') && fv_r435_verify();
}
function fv_r436_render(int $instance, array $campaign=[]): string {
 if ($instance<1 || $instance>30 || !fv_r436_parent()) return fv_r436_fallback();
 $body=fv_r435_render($instance,$campaign);
 $gallery='<details class="fv-r435__catalog"';
 if (substr_count($body,$gallery)!==1
   || substr_count($body,'class="fv-r429__cta"')!==1
   || substr_count($body,'S67-19766 / crew portrait')!==1) return fv_r436_fallback();
 // The linked NASA "Crew Honored" page verifies the subject, but not this photo ID.
 // Do not perpetuate a catalogue identifier until it is verified from that record.
 $body=str_replace('S67-19766 / crew portrait','Crew photograph / catalogue ID not confirmed',$body);
 $proof='<details class="fv-r436__proof" data-fv-r436-proof><summary>Compare source types before drawing a conclusion</summary>'
 .'<p class="fv-r436__notice">A photograph of preparation is not a pressure trace. A memorial exhibit is not a contemporary accident record. The 1967 Review Board is the source for the probable initiator; its finding was not conclusive.</p>'
 .'<div class="fv-r436__grid">'
 .'<article><p class="fv-r436__tag">1966–1967 · PHOTOGRAPH</p><h3>What was photographed?</h3><p>Training, spacecraft preparation and aftermath are contextual visual records. None captures the initial spark or documents ground-test oxygen pressure.</p><a href="https://www.nasa.gov/gallery/apollo-1/" rel="noopener noreferrer">NASA Apollo 1 photograph index</a></article>'
 .'<article><p class="fv-r436__tag">APRIL 1967 · INVESTIGATION</p><h3>What did the Board determine?</h3><p>An electrical arc was the most probable initiator, but no single ignition source was conclusively identified. This is a finding of the official investigation, not an image-caption deduction.</p><a href="https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html" rel="noopener noreferrer">Review Board determinations</a></article>'
 .'<article><p class="fv-r436__tag">JANUARY 2017 · MEMORIAL</p><h3>What was interpreted later?</h3><p>Tribute and redesigned-hatch exhibits commemorate and explain subsequent changes. A 2017 exhibit photograph cannot itself record the 1967 emergency.</p><a href="https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/" rel="noopener noreferrer">NASA exhibit announcement</a></article>'
 .'</div><p class="fv-r436__rights">Source links are documentary references, not permission to reproduce an image or imply NASA endorsement. No paid offer is presented.</p></details>';
 $body=str_replace($gallery,$proof.$gallery,$body);
 return '<div class="fv-r436" data-fv-r436>'.$body.'</div>';
}
function fv_r436_shortcode(): string {
 if (!fv_r436_allowed() || !fv_r436_verify()) return fv_r436_fallback();
 $n=($GLOBALS['fv_r436_instances']??0)+1;
 if (!is_int($n) || $n>30) return fv_r436_fallback();
 $GLOBALS['fv_r436_instances']=$n;
 return fv_r436_render($n,$_GET);
}
function fv_r436_enqueue(): void {
 if (!fv_r436_allowed() || !fv_r436_parent()
  || !function_exists('plugins_url') || !function_exists('wp_enqueue_style')
  || !function_exists('fv_r435_enqueue')) return;
 fv_r435_enqueue();
 wp_enqueue_style('fv-r436-source-proof',plugins_url('assets/source-proof.css',__FILE__),['fv-r435-photo-custody'],'r436');
}
if (function_exists('add_shortcode')) add_shortcode('fv_apollo_source_proof_r436','fv_r436_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts','fv_r436_enqueue',22);

<?php
/** FV Apollo R440: educator classroom preview; fully separate staging shortcode, no paid CTA. */
if (!defined('ABSPATH')) { exit; }
const FV_R440_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R440_NASA_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R440_NASA_TESTS = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
const FV_R440_RIGHTS = 'https://www.nasa.gov/nasa-brand-center/advertising-guidelines/';
const FV_R440_ASSETS = [
 'assets/educator-intent.css' => 'b0b5c504e0ee57ed3f7b1525973842f8c2df1f9afdad0493f5a8fec4399971a1',
 'assets/educator-intent.js' => '13a186fb80b552f8cc9b96ffcfda38c0ccd111f43c3e147349a7847db2120888',
 'product_evidence.json' => '936cdae7af73e60139dd5fc7c58477be6aa4f7b662c4da5fb59c7f47b498b564',
];
function fv_r440_fallback(): string { return '<p>Classroom preview unavailable. <a href="'.FV_R440_ARTICLE.'">Read the free Apollo 1 investigation</a>.</p>'; }
function fv_r440_allowed(): bool {
 return defined('FV_R440_ENABLED') && FV_R440_ENABLED === true
  && defined('FV_R440_STAGING_PAGE_ID') && is_int(FV_R440_STAGING_PAGE_ID) && FV_R440_STAGING_PAGE_ID > 0
  && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
  && function_exists('is_singular') && is_singular()
  && function_exists('get_queried_object_id') && get_queried_object_id() === FV_R440_STAGING_PAGE_ID;
}
function fv_r440_verify(): bool {
 $base=realpath(__DIR__);if(!$base || !is_dir($base) || is_link(__DIR__))return false;
 foreach(FV_R440_ASSETS as $relative=>$sha){
  $p=$base;
  foreach(explode('/',$relative) as $part){if($part==='' || $part==='.' || $part==='..')return false;$p.='/'.$part;if(is_link($p))return false;}
  $real=realpath($p);
  if(!$real || !is_file($real) || !is_readable($real) || strncmp($real,$base.'/',strlen($base)+1)!==0)return false;
  $bytes=file_get_contents($real);
  if(!is_string($bytes) || !hash_equals($sha,hash('sha256',$bytes)))return false;
 }
 return true;
}
function fv_r440_offer_hold(): bool {
 if(!fv_r440_verify())return false;
 $d=json_decode((string)file_get_contents(__DIR__.'/product_evidence.json'),true);
 if(!is_array($d) || ($d['schema']??'')!=='fv-apollo-educator-offer-evidence-v1' || ($d['verification_status']??'')!=='HOLD_NOT_SELLABLE')return false;
 foreach(['merchant_seller_identity_verified','specific_paid_sku_verified','payment_checkout_verified','deliverable_fulfillment_verified','original_content_rights_verified','nasamedia_rights_reviewed_for_product','founder_approved_paid_launch','published_grok_asset_id_verified'] as $key)if(!array_key_exists($key,$d) || $d[$key]!==false)return false;
 return ($d['paid_checkout_url']??null)===null && ($d['verified_orders']??null)===null && ($d['realized_net_revenue']??null)===null;
}
function fv_r440_render(int $instance): string {
 if($instance<1||$instance>30||!fv_r440_offer_hold())return fv_r440_fallback();
 $id='fv-r440-'.$instance;
 return '<section class="fv-r440" data-r440-root aria-labelledby="'.$id.'-title">'
  .'<p class="fv-r440__eyebrow">APOLLO 1 / ORIGINAL CLASSROOM PREVIEW · FREE</p>'
  .'<h2 id="'.$id.'-title">Can your class distinguish evidence from inference?</h2>'
  .'<p>The research above remains free. This original classroom exercise can be read, printed or downloaded without an account. It does not reproduce NASA images or sell public records. Any future premium teaching kit is a <strong>proposal, not an available product</strong>.</p>'
  .'<div class="fv-r440__grid"><div><h3>Learning task</h3><p>Examine one official accident finding and one later experimental retrospective. Explain the difference between a <em>most probable initiator</em>, an <em>identified initiator</em>, and a test performed after the accident.</p>'
  .'<ol><li>Record the event date and each document’s publication context.</li><li>Identify the Review Board’s most probable ignition mechanism and its remaining uncertainty.</li><li>Explain why later controlled ignition tests cannot prove the initiating spark in January 1967.</li></ol></div>'
  .'<div><h3>Evidence and instructor checks</h3><details><summary>Instructor rubric and source limitations</summary><ul>'
  .'<li><strong>Chronology:</strong> distinguish January 27, 1967 from subsequent experiments and the 2018 account.</li>'
  .'<li><strong>Cause:</strong> the Board judged an electrical arc most probable; it did not conclusively identify one ignition source.</li>'
  .'<li><strong>Limits:</strong> the later controlled tests inform fire safety, not the location of the first spark.</li>'
  .'<li><strong>Rights:</strong> source access is not permission to use NASA identity, likenesses or third-party material in a commercial product.</li>'
  .'</ul></details><p><a href="'.FV_R440_NASA_BOARD.'" rel="noopener noreferrer">NASA Apollo 204 Review Board report</a></p>'
  .'<p><a href="'.FV_R440_NASA_TESTS.'" rel="noopener noreferrer">NASA flammability retrospective</a></p>'
  .'<p><a href="'.FV_R440_RIGHTS.'" rel="noopener noreferrer">NASA commercial media guidance</a></p></div></div>'
  .'<div class="fv-r440__export"><p><strong>Use it in class:</strong> The text and sources are readable here without JavaScript. With JavaScript, download an original text-only activity and rubric for offline use; nothing is submitted or tracked.</p>'
  .'<div data-r440-export></div><p data-r440-status role="status" aria-live="polite"></p></div>'
  .'<p class="fv-r440__next"><strong>Next step:</strong> return to the single “Read the free Apollo 1 investigation” link in the Evidence Atlas above, then inspect NASA’s documents directly. There is no paid checkout or new lead form in this staging component.</p>'
  .'</section>';
}
function fv_r440_shortcode(): string {
 if(!fv_r440_allowed())return fv_r440_fallback();
 $n=($GLOBALS['fv_r440_instances']??0)+1;
 if(!is_int($n)||$n>30)return fv_r440_fallback();
 $GLOBALS['fv_r440_instances']=$n;
 return fv_r440_render($n);
}
function fv_r440_enqueue(): void {
 if(!fv_r440_allowed()||!fv_r440_offer_hold()||!function_exists('wp_enqueue_style')||!function_exists('wp_enqueue_script')||!function_exists('plugins_url'))return;
 wp_enqueue_style('fv-r440-educator',plugins_url('assets/educator-intent.css',__FILE__),[],'r440');
 wp_enqueue_script('fv-r440-educator',plugins_url('assets/educator-intent.js',__FILE__),[],'r440',true);
}
if(function_exists('add_shortcode'))add_shortcode('fv_apollo_educator_preview_r440','fv_r440_shortcode');
if(function_exists('add_action'))add_action('wp_enqueue_scripts','fv_r440_enqueue',25);

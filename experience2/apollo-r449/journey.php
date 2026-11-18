<?php
/**
 * FV Apollo R449: staging-only single-CTA assembly of R448 evidence + R440 educator preview.
 * Nothing loads on production, nothing is persisted, and no merchant offer is activated.
 * This file is additive; earlier PRs and homepage ownership remain untouched.
 */
if (!defined('ABSPATH')) { return; }
const FV_R449_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R449_PINNED_DEPENDENCIES = [
 'apollo-r440/staging-educator-intent.php' => '835460b85afa4305f5419f09caad0fb8839202051359251d4c173954ff9ffa87',
 'apollo-r440/assets/educator-intent.css' => 'b0b5c504e0ee57ed3f7b1525973842f8c2df1f9afdad0493f5a8fec4399971a1',
 'apollo-r440/assets/educator-intent.js' => '13a186fb80b552f8cc9b96ffcfda38c0ccd111f43c3e147349a7847db2120888',
 'apollo-r440/product_evidence.json' => '936cdae7af73e60139dd5fc7c58477be6aa4f7b662c4da5fb59c7f47b498b564',
 'apollo-r448/crosswalk.php' => '69e7c1b4130445a56b2e869ee2c4eae79c886679de1ee2e669cb818cab937536',
 'apollo-r448/assets/crosswalk.css' => '0e0256d1f2ba2b0a200197d2092ce32e2caf8481307adbdbaf35fc9a868ae3a1',
 'apollo-r448/assets/crosswalk.js' => '1edc3a80838bfaad6bafa9a70134e872e3e74a7ff31afab6317f3aaa8eec1181',
 'apollo-r448/manifest.json' => '744ec9c2ca46693f116c7ea5a1edf4ec3416083384e11ade0d0b63ca900a9411',
];
const FV_R449_CSS_SHA256 = '3c0874945884ea234b19bae2f2ba1431836d7b384318c2142f202c28f2545481';
function fv_r449_fallback(): string {
    return '<p class="fv-r449-fallback">The classroom evidence journey is temporarily unavailable. '
       .'<a href="'.FV_R449_ARTICLE.'">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r449_root(): ?string {
    $root=realpath(dirname(__DIR__));
    return ($root && is_dir($root) && !is_link(dirname(__DIR__))) ? $root : null;
}
function fv_r449_dependency_ok(string $relative, string $checksum): bool {
    $root=fv_r449_root();
    if ($root===null || !preg_match('~^apollo-r(440|448)/[a-z0-9_./-]+$~D',$relative)) return false;
    $path=$root;
    foreach(explode('/',$relative) as $fragment) {
        if ($fragment==='' || $fragment==='.' || $fragment==='..') return false;
        $path.='/'.$fragment;
        if (is_link($path)) return false;
    }
    $resolved=realpath($path);
    if (!$resolved || strncmp($resolved,$root.'/',strlen($root)+1)!==0 || !is_file($resolved) || !is_readable($resolved)) return false;
    $bytes=file_get_contents($resolved);
    return is_string($bytes) && hash_equals($checksum,hash('sha256',$bytes));
}
function fv_r449_verified(): bool {
    if (!fv_r449_dependency_ok('apollo-r448/manifest.json', FV_R449_PINNED_DEPENDENCIES['apollo-r448/manifest.json'])) return false;
    foreach (FV_R449_PINNED_DEPENDENCIES as $file=>$sha) if(!fv_r449_dependency_ok($file,$sha)) return false;
    $css=__DIR__.'/assets/journey.css';
    if(is_link($css)||!is_file($css)||!is_readable($css)||!hash_equals(FV_R449_CSS_SHA256,(string)hash_file('sha256',$css))) return false;
    // These assertions are enforced by inherited R440 and R448 validators as well.
    $offer=json_decode((string)file_get_contents(dirname(__DIR__).'/apollo-r440/product_evidence.json'),true);
    $claims=json_decode((string)file_get_contents(dirname(__DIR__).'/apollo-r448/manifest.json'),true);
    return is_array($offer) && is_array($claims) && ($offer['verification_status']??'')==='HOLD_NOT_SELLABLE'
      && ($offer['founder_approved_paid_launch']??null)===false
      && array_key_exists('paid_checkout_url',$offer) && $offer['paid_checkout_url']===null
      && ($claims['editorial_approval']??'')==='PENDING_INDEPENDENT_QD'
      && ($claims['release_approved']??true)===false;
}
function fv_r449_allowed(): bool {
    return defined('FV_R449_ENABLE_STAGING') && FV_R449_ENABLE_STAGING===true
        && defined('FV_R449_STAGING_PAGE_ID') && is_int(FV_R449_STAGING_PAGE_ID) && FV_R449_STAGING_PAGE_ID>0
        && function_exists('wp_get_environment_type') && wp_get_environment_type()==='staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && get_queried_object_id()===FV_R449_STAGING_PAGE_ID;
}
function fv_r449_load(): bool {
    if (!fv_r449_verified()) return false;
    // Require checked bytes only, and never load a dependency on production.
    if (!function_exists('fv_r448_render')) require_once dirname(__DIR__).'/apollo-r448/crosswalk.php';
    if (!function_exists('fv_r440_render')) require_once dirname(__DIR__).'/apollo-r440/staging-educator-intent.php';
    return function_exists('fv_r448_render') && function_exists('fv_r440_render')
       && function_exists('fv_r440_offer_hold') && fv_r440_offer_hold()
       && function_exists('fv_r448_data') && fv_r448_data()!==null;
}
function fv_r449_render(): string {
    if(!fv_r449_allowed() || !fv_r449_load()) return fv_r449_fallback();
    static $count=0; $count++;
    if ($count>30) return fv_r449_fallback();
    $crosswalk=fv_r448_render();
    $preview=fv_r440_render($count);
    // Reject unexpected fallback, duplicate investigation CTAs, checkout, forms or promoted products.
    $combined=$crosswalk.$preview;
    if (substr_count($combined,'href="'.FV_R449_ARTICLE.'"')!==1
       || substr_count($crosswalk,'data-fv-r448-card')!==4
       || substr_count($preview,'data-r440-root')!==1
       || preg_match('~<form\b|(?:href|action)\s*=\s*["\'](?:https?://[^"\']*(?:payhip|checkout)|javascript:)~i',$combined)
       || stripos($combined,'<iframe')!==false) return fv_r449_fallback();
    $id='fv-r449-'.$count;
    return '<article class="fv-r449" data-fv-r449 aria-labelledby="'.$id.'-title">'
      .'<header class="fv-r449__header"><p class="fv-r449__kicker">Research Desk / Apollo 1 · Original teaching materials</p>'
      .'<h1 id="'.$id.'-title">What the records prove—and what they don’t</h1>'
      .'<p>A documented chronology for readers and educators. Original interpretation is awaiting independent review. No media is reproduced, and no Apollo teaching kit is currently offered for sale.</p></header>'
      .$crosswalk.'<aside class="fv-r449__educator" aria-label="Optional classroom evidence exercise">'.$preview.'</aside>'
      .'<footer class="fv-r449__end"><p>Source links provide supporting documents, not NASA endorsement. The complete investigation is free; there is no checkout or required signup.</p></footer></article>';
}
function fv_r449_shortcode(): string {return fv_r449_render();}
function fv_r449_enqueue(): void {
    if(!fv_r449_allowed()||!fv_r449_verified()||!fv_r449_load()
       || !function_exists('wp_enqueue_style')||!function_exists('wp_enqueue_script')||!function_exists('plugins_url'))return;
    foreach([
       ['fv-r449-integration','assets/journey.css',__FILE__],
       ['fv-r448-crosswalk','../apollo-r448/assets/crosswalk.css',__FILE__],
       ['fv-r440-educator','../apollo-r440/assets/educator-intent.css',__FILE__]
    ] as $entry) wp_enqueue_style($entry[0],plugins_url($entry[1],$entry[2]),[],'r449');
    foreach([
       ['fv-r448-crosswalk','../apollo-r448/assets/crosswalk.js',__FILE__],
       ['fv-r440-educator','../apollo-r440/assets/educator-intent.js',__FILE__]
    ] as $entry) wp_enqueue_script($entry[0],plugins_url($entry[1],$entry[2]),[],'r449',true);
}
if (function_exists('add_shortcode') && function_exists('wp_get_environment_type') && wp_get_environment_type()==='staging') {
    add_shortcode('fv_apollo_evidence_journey_r449','fv_r449_shortcode');
    if (function_exists('add_action')) add_action('wp_enqueue_scripts','fv_r449_enqueue',20);
}

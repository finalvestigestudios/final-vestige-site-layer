<?php
/** FV Apollo R438; isolated, staging-only, non-geographic source atlas. */
if (!defined('ABSPATH')) { exit; }
const FV_R438_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R438_PARENT = [
    'apollo-r437/staging-chronology-audit.php' => 'b911e256942805649cdc298b81ae1ceda420c429',
    'apollo-r437/assets/chronology-audit.css' => '828f51527c5d75b6b9099720dd7e466f111b378d',
    'apollo-r437/assets/chronology-audit.js' => '3d318c3264dc9289f957f0ef30cd239cb0b00fb7',
];
const FV_R438_ASSETS = [
    'source_catalog.json' => '353b4d962069ac871eeb6b20e9bbe31097c2dc062add3293affecad356075fdf',
    'assets/source-atlas.css' => 'b8dd9f74869b01d9f07edf4681c1cc4f50a5b1aceeef9bfa7b1ff63e146fb61d',
    'assets/source-atlas.js' => '1b6bd52525f6bcab1bfb21251099914fd24e03cfddc7b1a782a79caf1c2bdb8b',
];
function fv_r438_escape(string $s): string { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv_r438_fallback(): string { return '<p>Source comparison unavailable. <a href="'.FV_R438_ARTICLE.'">Read the free Apollo 1 investigation</a>.</p>'; }
function fv_r438_allowed(): bool {
 return defined('FV_R438_ENABLED') && FV_R438_ENABLED === true
 && defined('FV_R438_STAGING_PAGE_ID') && is_int(FV_R438_STAGING_PAGE_ID) && FV_R438_STAGING_PAGE_ID > 0
 && function_exists('wp_get_environment_type') && wp_get_environment_type()==='staging'
 && function_exists('is_singular') && is_singular()
 && function_exists('get_queried_object_id') && get_queried_object_id()===FV_R438_STAGING_PAGE_ID;
}
function fv_r438_file_ok(string $base,string $relative,string $expected,bool $git): bool {
 $b=realpath($base);if(!$b||!is_dir($b)||is_link($base))return false;
 $p=$b;foreach(explode('/',$relative) as $part){if($part===''||$part==='.'||$part==='..')return false;$p.='/'.$part;if(is_link($p))return false;}
 $r=realpath($p);if(!$r||!is_file($r)||!is_readable($r)||strncmp($r,$b.'/',strlen($b)+1)!==0)return false;
 $bytes=file_get_contents($r);if(!is_string($bytes))return false;
 $actual=$git?sha1('blob '.strlen($bytes)."\0".$bytes):hash('sha256',$bytes);return hash_equals($expected,$actual);
}
function fv_r438_verify(): bool {
 foreach(FV_R438_PARENT as $p=>$sha)if(!fv_r438_file_ok(dirname(__DIR__),$p,$sha,true))return false;
 foreach(FV_R438_ASSETS as $p=>$sha)if(!fv_r438_file_ok(__DIR__,$p,$sha,false))return false;
 return true;
}
function fv_r438_parent(): bool {
 if(!fv_r438_verify())return false;
 $p=realpath(dirname(__DIR__).'/apollo-r437/staging-chronology-audit.php');if(!$p)return false;
 if(!function_exists('fv_r437_render'))require_once $p;
 if(!function_exists('fv_r437_render')||!function_exists('fv_r437_parent'))return false;
 $reflection=new ReflectionFunction('fv_r437_render');if(realpath((string)$reflection->getFileName())!==$p)return false;
 return fv_r437_parent();
}
/** Schema is fixed to five approved NASA origin URLs, with NO coordinates or speculative graph edges. */
function fv_r438_catalog(): array {
 if(!fv_r438_verify())return [];
 $decoded=json_decode((string)file_get_contents(__DIR__.'/source_catalog.json'),true);
 if(!is_array($decoded)||($decoded['schema']??'')!=='fv-apollo-atlas-v1'||($decoded['release']??'')!=='source-link-only-no-geopins'||count($decoded['records']??[])!==5)return [];
 $ids=[];$allowed=['https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','https://www.nasa.gov/gallery/apollo-1/','https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/','https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/'];
 foreach($decoded['records'] as $r){if(!is_array($r)||count(array_diff(['id','class','date','date_label','title','source_name','source_url','supports','limit','rights','role'],array_keys($r)))||count(array_diff(array_keys($r),['id','class','date','date_label','title','source_name','source_url','supports','limit','rights','role'])))return [];
  foreach($r as $value)if(!is_string($value)||$value===''||strlen($value)>440)return [];
  if(!preg_match('/^[a-z0-9-]+$/D',$r['id'])||isset($ids[$r['id']])||!in_array($r['source_url'],$allowed,true)||!in_array($r['role'],['primary','photograph','retrospective'],true))return [];
  $ids[$r['id']]=true;
 }
 return $decoded['records'];
}
function fv_r438_atlas(int $instance): string {
 $records=fv_r438_catalog();if(count($records)!==5)return '';
 $id='fv-r438-'.$instance;
 $html='<section class="fv-r438" data-r438-atlas-root aria-labelledby="'.$id.'-title">'
 .'<p class="fv-r438__overline">APOLLO 1 / EVIDENCE ATLAS · DOCUMENTARY CUSTODY</p>'
 .'<h2 id="'.$id.'-title">What each NASA record can—and cannot—establish</h2>'
 .'<p class="fv-r438__sub">Select two sources to compare their evidentiary limits. The primary review, photographs and later retrospectives answer different questions. There are no speculative map pins, and every source remains readable without JavaScript.</p>'
 .'<ol class="fv-r438__atlas" data-r438-atlas>';
 foreach($records as $r){$e='fv_r438_escape';
  $html.='<li class="fv-r438__plate" data-r438-card="'.$e($r['id']).'">'
   .'<p class="fv-r438__kind">'.$e($r['class']).' · '.$e($r['role']).'</p>'
   .'<p class="fv-r438__date"><time datetime="'.$e($r['date']).'">'.$e($r['date_label']).'</time></p>'
   .'<h3>'.$e($r['title']).'</h3>'
   .'<p><strong>What it supports:</strong> <span data-r438-supports>'.$e($r['supports']).'</span></p>'
   .'<p class="fv-r438__limit"><strong>What it cannot prove:</strong> <span data-r438-limit>'.$e($r['limit']).'</span></p>'
   .'<details><summary>Rights and source custody</summary><p>'.$e($r['rights']).'</p></details>'
   .'<p class="fv-r438__print-only"><strong>Rights:</strong> '.$e($r['rights']).'</p>'
   .'<p><a rel="noopener noreferrer" href="'.$e($r['source_url']).'">Original NASA source: '.$e($r['source_name']).'</a></p></li>';
 }
 return $html.'</ol><div class="fv-r438__comparison" data-r438-comparison hidden aria-label="Evidence source comparison"></div>'
  .'<p class="fv-r438__rights">Source-links only: no NASA photos, insignia or astronaut likenesses reproduced here. NASA does not endorse Final Vestige; historical availability is not commercial image clearance. <a href="https://www.nasa.gov/nasa-brand-center/advertising-guidelines/" rel="noopener noreferrer">NASA advertising guidance</a>. This evidence experience is free; any future educator product requires independent rights and merchant verification.</p></section>';
}
function fv_r438_render(int $instance,array $campaign=[]): string {
 if($instance<1||$instance>30||!fv_r438_parent())return fv_r438_fallback();
 $parent=fv_r437_render($instance,$campaign);
 $needle='<section class="fv-r437__audit"';
 if(substr_count($parent,$needle)!==1||substr_count($parent,'class="fv-r429__cta"')!==1)return fv_r438_fallback();
 $atlas=fv_r438_atlas($instance);if($atlas==='')return fv_r438_fallback();
 return '<div class="fv-r438-shell">'.str_replace($needle,$atlas.$needle,$parent).'</div>';
}
function fv_r438_shortcode(): string {
 if(!fv_r438_allowed()||!fv_r438_verify())return fv_r438_fallback();
 $i=($GLOBALS['fv_r438_instances']??0)+1;if(!is_int($i)||$i>30)return fv_r438_fallback();
 $GLOBALS['fv_r438_instances']=$i;return fv_r438_render($i,$_GET);
}
function fv_r438_enqueue(): void {
 if(!fv_r438_allowed()||!fv_r438_parent()||!function_exists('fv_r437_enqueue')||!function_exists('plugins_url')||!function_exists('wp_enqueue_style')||!function_exists('wp_enqueue_script'))return;
 fv_r437_enqueue();
 wp_enqueue_style('fv-r438-atlas',plugins_url('assets/source-atlas.css',__FILE__),['fv-r437-chronology'],'r438');
 wp_enqueue_script('fv-r438-atlas',plugins_url('assets/source-atlas.js',__FILE__),[],'r438',true);
}
if(function_exists('add_shortcode'))add_shortcode('fv_apollo_source_atlas_r438','fv_r438_shortcode');
if(function_exists('add_action'))add_action('wp_enqueue_scripts','fv_r438_enqueue',23);

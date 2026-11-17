<?php
/** FV Apollo R439: evidence receipts; isolated and disabled except approved staging page. */
if (!defined('ABSPATH')) { exit; }
const FV_R439_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R439_PARENT = [
 'apollo-r438/staging-source-atlas.php'=>'4d3d8e72e71db109cf22083ec57c3b27ae7ff184',
 'apollo-r438/assets/source-atlas.css'=>'2154e3feb3811ef7abd53f229264cdb83428ae41',
 'apollo-r438/assets/source-atlas.js'=>'bd327465626fe3e591ae055273ced676bd03190e',
 'apollo-r438/source_catalog.json'=>'60903bdcf67a1f6b22f92508d4dcc181c5f95c5a',
];
const FV_R439_ASSETS = [
 'assets/source-receipt.css'=>'5615686a9e0d160542bac8e3af7397f94732123e9e0517cd7c837061d212401b',
 'assets/source-receipt.js'=>'87d9c1f771a86d7f00c015862a1f8f6f2fb39391e34f5c5a47ef0026a8839c0a',
];
function fv_r439_fallback(): string {return '<p>Evidence receipt unavailable. <a href="'.FV_R439_ARTICLE.'">Read the free Apollo 1 investigation</a>.</p>';}
function fv_r439_allowed(): bool {
 return defined('FV_R439_ENABLED') && FV_R439_ENABLED===true
  && defined('FV_R439_STAGING_PAGE_ID') && is_int(FV_R439_STAGING_PAGE_ID) && FV_R439_STAGING_PAGE_ID>0
  && function_exists('wp_get_environment_type') && wp_get_environment_type()==='staging'
  && function_exists('is_singular') && is_singular()
  && function_exists('get_queried_object_id') && get_queried_object_id()===FV_R439_STAGING_PAGE_ID;
}
function fv_r439_check(string $base,string $relative,string $hash,bool $git): bool {
 $b=realpath($base);if(!$b||!is_dir($b)||is_link($base))return false;
 $p=$b;foreach(explode('/',$relative) as $segment){if($segment===''||$segment==='.'||$segment==='..')return false;$p.='/'.$segment;if(is_link($p))return false;}
 $real=realpath($p);if(!$real||!is_file($real)||!is_readable($real)||strncmp($real,$b.'/',strlen($b)+1)!==0)return false;
 $bytes=file_get_contents($real);if(!is_string($bytes))return false;
 $actual=$git?sha1('blob '.strlen($bytes)."\0".$bytes):hash('sha256',$bytes);
 return hash_equals($hash,$actual);
}
function fv_r439_verify(): bool {
 foreach(FV_R439_PARENT as $p=>$sha)if(!fv_r439_check(dirname(__DIR__),$p,$sha,true))return false;
 foreach(FV_R439_ASSETS as $p=>$sha)if(!fv_r439_check(__DIR__,$p,$sha,false))return false;
 return true;
}
function fv_r439_parent(): bool {
 if(!fv_r439_verify())return false;
 $p=realpath(dirname(__DIR__).'/apollo-r438/staging-source-atlas.php');if(!$p)return false;
 if(!function_exists('fv_r438_render'))require_once $p;
 if(!function_exists('fv_r438_render')||!function_exists('fv_r438_parent'))return false;
 $reflection=new ReflectionFunction('fv_r438_render');
 return realpath((string)$reflection->getFileName())===$p && fv_r438_parent();
}
function fv_r439_render(int $instance,array $campaign=[]): string {
 if($instance<1||$instance>30||!fv_r439_parent())return fv_r439_fallback();
 $parent=fv_r438_render($instance,$campaign);
 $needle='<div class="fv-r438__comparison" data-r438-comparison hidden aria-label="Evidence source comparison"></div>';
 if(substr_count($parent,$needle)!==1||substr_count($parent,'class="fv-r429__cta"')!==1)return fv_r439_fallback();
 $id='fv-r439-'.$instance.'-title';
 $pass='<section class="fv-r439__receipt" data-r439-receipt aria-labelledby="'.$id.'">'
  .'<h2 id="'.$id.'">Keep a verifiable source receipt</h2>'
  .'<p>Use the NASA-linked Evidence Atlas above to distinguish a photograph from an accident finding or a later retrospective. The source receipt can include either all five records or the two selected for comparison. It records <strong>what each source cannot establish</strong> alongside the claim it supports.</p>'
  .'<p>For a class or independent research project, compare two records, save their citations, then continue to the full free investigation. No purchase or sign-up is required. Export is local and optional; source links do not convey commercial image rights or NASA endorsement.</p>'
  .'<div data-r439-controls></div><p class="fv-r439__status" data-r439-status role="status" aria-live="polite"></p>'
  .'<label class="fv-r439__manual-label" data-r439-manual-label hidden for="fv-r439-'.$instance.'-manual">Manual copy fallback (only shown when clipboard access is denied)</label>'
  .'<textarea class="fv-r439__manual" id="fv-r439-'.$instance.'-manual" data-r439-manual readonly hidden aria-label="Source receipt text for manual copying"></textarea>'
  .'<p><small>Without JavaScript, the complete five-record source trail, original NASA links, rights notes and free investigation remain available directly above.</small></p>'
  .'</section>';
 // The parent verified atlas data and canonical CTA are unchanged; insertion is at one exact template boundary.
 return '<div class="fv-r439" data-r439-root>'.str_replace($needle,$needle.$pass,$parent).'</div>';
}
function fv_r439_shortcode(): string {
 if(!fv_r439_allowed()||!fv_r439_verify())return fv_r439_fallback();
 $i=($GLOBALS['fv_r439_instances']??0)+1;if(!is_int($i)||$i>30)return fv_r439_fallback();
 $GLOBALS['fv_r439_instances']=$i;return fv_r439_render($i,$_GET);
}
function fv_r439_enqueue(): void {
 if(!fv_r439_allowed()||!fv_r439_parent()||!function_exists('fv_r438_enqueue')||!function_exists('plugins_url')||!function_exists('wp_enqueue_style')||!function_exists('wp_enqueue_script'))return;
 fv_r438_enqueue();
 wp_enqueue_style('fv-r439-receipt',plugins_url('assets/source-receipt.css',__FILE__),['fv-r438-atlas'],'r439');
 wp_enqueue_script('fv-r439-receipt',plugins_url('assets/source-receipt.js',__FILE__),[],'r439',true);
}
if(function_exists('add_shortcode'))add_shortcode('fv_apollo_evidence_receipt_r439','fv_r439_shortcode');
if(function_exists('add_action'))add_action('wp_enqueue_scripts','fv_r439_enqueue',24);

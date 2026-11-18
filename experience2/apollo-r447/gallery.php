<?php
/**
 * Apollo R447 source-verified photo RECORD gallery; no archival images shipped.
 * Staging opt-in only. No network, tracking, storage, commerce, WP changes, or paid calls.
 * Note: NASA availability does not itself clear commercial advertising/likeness rights.
 */
const FV_R447_MANIFEST_SHA256 = '2aa8f02041a310164fdbe15bbcee2b2f531401aa11508f0e04ae0ee8afea3458';
const FV_R447_INVESTIGATION = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
function fv_r447_escape($v): string { return htmlspecialchars((string)$v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv_r447_fallback(): string {
  return '<p class="fv-r447-fallback">The gallery source records are unavailable. <a href="'.FV_R447_INVESTIGATION.'">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r447_manifest(): ?array {
  $p=__DIR__.'/manifest.json';
  if (!is_readable($p) || !hash_equals(FV_R447_MANIFEST_SHA256,(string)hash_file('sha256',$p))) return null;
  $d=json_decode((string)file_get_contents($p),true);
  if (!is_array($d) || ($d['schema']??'')!=='fv-apollo-media-custody-v1'
      || ($d['review_status']??'')!=='HOLD_EDITORIAL_AND_MEDIA_RIGHTS'
      || ($d['commerce_status']??'')!=='NO_VERIFIED_APOLLO_PAID_SKU'
      || ($d['offer_release_approved']??true)!==false
      || ($d['no_image_embedding']??false)!==true
      || ($d['media_use_approval']??'')!=='NOT_GRANTED'
      || ($d['editorial_signoff']??'')!=='PENDING_INDEPENDENT_QD'
      || count($d['records']??[])!==4) return null;
  $ids=[];$previous='';
  foreach ($d['records'] as $r){
    if(!is_array($r)) return null;
    foreach(['id','date','date_label','stage','kind','title','source_id','source_url','source_state','description','limit','media_state'] as $k)
       if(!isset($r[$k]) || !is_string($r[$k]) || $r[$k]==='') return null;
    if(!preg_match('/^[a-z-]+$/D',$r['id']) || !preg_match('/^(1966|1967|2017)-[0-9]{2}-[0-9]{2}$/D',$r['date'])
       || ($previous!=='' && strcmp($r['date'],$previous)<0)
       || !in_array($r['stage'],['before','event','later'],true)
       || !in_array($r['source_state'],['NASA_RECORD_LINK_VERIFIED','NASA_REPORT_VERIFIED','CATALOG_LINK_RECORDED_NOT_RECHECKED'],true)
       || !in_array($r['media_state'],['RIGHTS_AND_LIKENESS_REVIEW_REQUIRED','NO_IMAGE_PRESENT'],true)) return null;
    $u=parse_url($r['source_url']);
    if(!is_array($u)|| ($u['scheme']??'')!=='https'||!in_array($u['host']??'',['www.nasa.gov','images.nasa.gov'],true)
        ||isset($u['user'])||isset($u['pass'])||isset($u['port'])||isset($u['fragment']))return null;
    $ids[]=$r['id'];$previous=$r['date'];
  }
  if(count(array_unique($ids))!==4 || $ids!==['crew-training','capsule-processing','accident-record','hatch-memorial'])return null;
  return $d;
}
function fv_r447_render(): string {
  $d=fv_r447_manifest(); if($d===null) return fv_r447_fallback();
  static $instance=0; $instance++; $uid='fv-r447-'.$instance;
  ob_start(); ?>
<section class="fv-r447" data-fv-r447 aria-labelledby="<?php echo $uid; ?>-title">
  <p class="fv-r447__eyebrow">APOLLO 1 / RESEARCH DESK · IMAGE CUSTODY</p>
  <h2 id="<?php echo $uid; ?>-title">Four records. Three photographic contexts. None shows the fire.</h2>
  <p class="fv-r447__intro">This is a chronology of <strong>archival source records, not the events pictured during the emergency</strong>. The photographs remain linked to their NASA catalogues rather than copied into a commercial experience while image and likeness review is pending.</p>
  <dl class="fv-r447__review"><div><dt>Document identity</dt><dd>Two original NASA image pages and the Board report checked; the museum image catalogue link requires rechecking</dd></div><div><dt>Historical interpretation</dt><dd>Independent editorial review pending</dd></div><div><dt>Media/likeness use</dt><dd>Not cleared for commercial promotional reproduction</dd></div></dl>
  <div class="fv-r447__filters" data-fv-r447-controls hidden aria-label="Choose source-era records">
    <button type="button" data-fv-r447-filter="all" aria-pressed="true">All four records</button>
    <button type="button" data-fv-r447-filter="before" aria-pressed="false">Before the fire</button>
    <button type="button" data-fv-r447-filter="event" aria-pressed="false">Board record</button>
    <button type="button" data-fv-r447-filter="later" aria-pressed="false">Later exhibit</button>
    <span data-fv-r447-count role="status" aria-live="polite"></span>
  </div>
  <ol class="fv-r447__gallery" aria-label="Chronologically ordered source records">
  <?php foreach($d['records'] as $r): ?><li class="fv-r447__card" data-fv-r447-card data-era="<?php echo fv_r447_escape($r['stage']); ?>">
    <div class="fv-r447__date"><time datetime="<?php echo fv_r447_escape($r['date']); ?>"><?php echo fv_r447_escape($r['date_label']); ?></time><span><?php echo fv_r447_escape($r['kind']); ?></span></div>
    <h3><?php echo fv_r447_escape($r['title']); ?></h3>
    <p><?php echo fv_r447_escape($r['description']); ?></p>
    <details><summary>Source, limits and reuse status</summary>
      <p><strong>Evidence boundary:</strong> <?php echo fv_r447_escape($r['limit']); ?></p>
      <p><strong>Source check:</strong> <?php echo fv_r447_escape(str_replace('_',' ',$r['source_state'])); ?>. <strong>Media:</strong> <?php echo fv_r447_escape(str_replace('_',' ',$r['media_state'])); ?>.</p>
      <p><a href="<?php echo fv_r447_escape($r['source_url']); ?>" rel="noopener noreferrer">View original NASA record: <?php echo fv_r447_escape($r['source_id']); ?></a></p>
    </details>
  </li><?php endforeach; ?>
  </ol>
  <p class="fv-r447__footer">For commercial uses, source availability is not permission to imply NASA endorsement or use an astronaut's likeness in advertising. See <a href="https://www.nasa.gov/nasa-brand-center/advertising-guidelines/" rel="noopener noreferrer">NASA advertising guidelines</a>. No pictures, badges, tracking, map pins or checkout buttons are embedded.</p>
  <div class="fv-r447__next"><p>Want the evidence behind the investigation? The complete Apollo 1 report analysis remains free.</p><a href="<?php echo FV_R447_INVESTIGATION; ?>">Read the full Apollo 1 investigation</a></div>
</section>
  <?php return (string)ob_get_clean();
}
// Explicit staging only. Asset delivery from nested template blocks must be independently QA'd.
if(defined('ABSPATH') && function_exists('add_shortcode') && function_exists('wp_get_environment_type')
    && wp_get_environment_type()==='staging' && defined('FV_APOLLO_R447_ENABLE_STAGING')
    && FV_APOLLO_R447_ENABLE_STAGING===true){
  add_shortcode('fv_apollo_rights_gallery',function(){
    $css=__DIR__.'/assets/gallery.css';$js=__DIR__.'/assets/gallery.js';
    if (!is_readable($css)||!is_readable($js))return fv_r447_fallback();
    if(function_exists('wp_enqueue_style'))wp_enqueue_style('fv-r447-gallery',plugins_url('assets/gallery.css',__FILE__),[],'0.0.1-r447');
    if(function_exists('wp_enqueue_script'))wp_enqueue_script('fv-r447-gallery',plugins_url('assets/gallery.js',__FILE__),[],'0.0.1-r447',true);
    return fv_r447_render();
  });
}

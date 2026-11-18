<?php
/**
 * Apollo R448: source-custody claim crosswalk, isolated staging-only opt-in.
 * A NASA source link is not NASA endorsement, editorial approval or image-use clearance.
 */
const FV_R448_CATALOG_SHA256 = '744ec9c2ca46693f116c7ea5a1edf4ec3416083384e11ade0d0b63ca900a9411';
const FV_R448_CSS_SHA256 = '0e0256d1f2ba2b0a200197d2092ce32e2caf8481307adbdbaf35fc9a868ae3a1';
const FV_R448_JS_SHA256 = '1edc3a80838bfaad6bafa9a70134e872e3e74a7ff31afab6317f3aaa8eec1181';
const FV_R448_FREE_INVESTIGATION = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
function fv_r448_e($value): string { return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv_r448_fallback(): string {
    return '<p class="fv-r448-fallback">The evidence comparison is temporarily unavailable. <a href="'.FV_R448_FREE_INVESTIGATION.'">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r448_asset_valid(string $relative, string $sha): bool {
    $path=__DIR__.'/'.$relative;
    return is_file($path) && is_readable($path) && hash_equals($sha, (string) hash_file('sha256', $path));
}
function fv_r448_data(): ?array {
    if (!fv_r448_asset_valid('manifest.json', FV_R448_CATALOG_SHA256)) return null;
    $data=json_decode((string)file_get_contents(__DIR__.'/manifest.json'),true);
    if (!is_array($data)
        || ($data['schema']??'') !== 'fv-apollo-claim-custody-v1'
        || ($data['editorial_approval']??'') !== 'PENDING_INDEPENDENT_QD'
        || ($data['image_rights']??'') !== 'NO_MEDIA_COPIED_OR_CLEARED_FOR_PROMOTIONAL_USE'
        || ($data['paid_offer_status']??'') !== 'NO_VERIFIED_APOLLO_SKU'
        || ($data['release_approved']??true)!==false
        || count($data['claims']??[])!==4) return null;
    $expected=['training','review-board','memorial','flammability'];
    $dates=[];$ids=[];
    foreach($data['claims'] as $claim) {
        if(!is_array($claim)) return null;
        foreach(['id','date','date_context','era','source_kind','title','supported','not_supported','source_title','source_url','rights'] as $key){
            if(!isset($claim[$key]) || !is_string($claim[$key]) || trim($claim[$key])==='') return null;
        }
        $url=parse_url($claim['source_url']);
        if(!is_array($url) || ($url['scheme']??'')!=='https' || ($url['host']??'')!=='www.nasa.gov'
            || isset($url['user'])||isset($url['pass'])||isset($url['port'])||isset($url['query'])||isset($url['fragment'])) return null;
        if(!preg_match('/^20[0-9]{2}-[0-9]{2}-[0-9]{2}$|^19[0-9]{2}-[0-9]{2}-[0-9]{2}$/D',$claim['date'])
            || !in_array($claim['era'],['before','event','later'],true)) return null;
        $dates[]=$claim['date'];$ids[]=$claim['id'];
    }
    if($ids!==$expected || $dates!==['1966-10-18','1967-01-27','2017-01-27','2018-02-14']) return null;
    return $data;
}
function fv_r448_render(): string {
    $data=fv_r448_data();
    if($data===null || !fv_r448_asset_valid('assets/crosswalk.css', FV_R448_CSS_SHA256)
       || !fv_r448_asset_valid('assets/crosswalk.js', FV_R448_JS_SHA256)) return fv_r448_fallback();
    static $index=0;$index++;$id='fv-r448-'.$index;
    ob_start(); ?>
<section class="fv-r448" data-fv-r448 aria-labelledby="<?php echo $id; ?>-title">
  <p class="fv-r448__eyebrow">Apollo 1 / Research Desk · evidence crosswalk</p>
  <h2 id="<?php echo $id; ?>-title">Four records. Four different things they can prove.</h2>
  <p class="fv-r448__intro">An archival photograph, an accident inquiry, a museum announcement and later engineering history are different kinds of evidence. The date on each card identifies the event, caption or publication as labelled—not necessarily when an investigation was written.</p>
  <dl class="fv-r448__states">
    <div><dt>Source identity</dt><dd>Official NASA URLs cross-referenced; identity is not endorsement</dd></div>
    <div><dt>Historical interpretation</dt><dd>Awaiting independent editorial acceptance</dd></div>
    <div><dt>Images and sales</dt><dd>No images embedded and no approved Apollo paid SKU</dd></div>
  </dl>
  <div class="fv-r448__filters" data-fv-r448-controls hidden aria-label="Filter evidence by era">
    <button type="button" data-fv-r448-filter="all" aria-pressed="true">All evidence</button>
    <button type="button" data-fv-r448-filter="before" aria-pressed="false">Before</button>
    <button type="button" data-fv-r448-filter="event" aria-pressed="false">1967 inquiry</button>
    <button type="button" data-fv-r448-filter="later" aria-pressed="false">Later history</button>
    <output data-fv-r448-status aria-live="polite"></output>
  </div>
  <ol class="fv-r448__rail" aria-label="Chronological source and claim crosswalk">
   <?php foreach($data['claims'] as $claim): ?>
   <li class="fv-r448__card" data-fv-r448-card data-era="<?php echo fv_r448_e($claim['era']); ?>">
     <p class="fv-r448__stamp"><time datetime="<?php echo fv_r448_e($claim['date']); ?>"><?php echo fv_r448_e($claim['date']); ?></time> · <?php echo fv_r448_e($claim['date_context']); ?></p>
     <p class="fv-r448__kind"><?php echo fv_r448_e($claim['source_kind']); ?></p>
     <h3><?php echo fv_r448_e($claim['title']); ?></h3>
     <div class="fv-r448__claim"><p><strong>The source supports:</strong> <?php echo fv_r448_e($claim['supported']); ?></p>
       <p><strong>It does not establish:</strong> <?php echo fv_r448_e($claim['not_supported']); ?></p></div>
     <details><summary>Open source and custody notes</summary>
       <p><a href="<?php echo fv_r448_e($claim['source_url']); ?>" rel="noopener noreferrer">Read source: <?php echo fv_r448_e($claim['source_title']); ?></a></p>
       <p><strong>Image / use status:</strong> <?php echo fv_r448_e($claim['rights']); ?></p>
     </details>
   </li>
   <?php endforeach; ?>
  </ol>
  <p class="fv-r448__foot">The previously cited 2017 hatch photo catalogue identifier remains pending exact-ID reconciliation. This component uses a separately verified NASA news release instead; that does not validate the old image URL. NASA media, trademarks and recognizable likenesses have separate usage conditions. <a href="https://www.nasa.gov/nasa-brand-center/images-and-media/" rel="noopener noreferrer">Review NASA media guidance</a>.</p>
  <div class="fv-r448__next"><p>Follow the complete, free investigation for the historical narrative and its sources.</p>
    <a href="<?php echo FV_R448_FREE_INVESTIGATION; ?>">Read the full Apollo 1 investigation</a></div>
</section>
<?php return (string)ob_get_clean();
}
if(defined('ABSPATH') && function_exists('add_shortcode') && function_exists('wp_get_environment_type')
    && wp_get_environment_type()==='staging' && defined('FV_APOLLO_R448_ENABLE_STAGING') && FV_APOLLO_R448_ENABLE_STAGING===true){
    add_shortcode('fv_apollo_claim_crosswalk',static function(){
        if(fv_r448_data()===null || !fv_r448_asset_valid('assets/crosswalk.css',FV_R448_CSS_SHA256)
           || !fv_r448_asset_valid('assets/crosswalk.js',FV_R448_JS_SHA256)) return fv_r448_fallback();
        if(function_exists('wp_enqueue_style')) wp_enqueue_style('fv-apollo-r448',plugins_url('assets/crosswalk.css',__FILE__),[],'r448');
        if(function_exists('wp_enqueue_script')) wp_enqueue_script('fv-apollo-r448',plugins_url('assets/crosswalk.js',__FILE__),[],'r448',true);
        return fv_r448_render();
    });
}

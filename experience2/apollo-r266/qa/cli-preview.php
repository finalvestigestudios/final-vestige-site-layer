<?php
declare(strict_types=1);
require dirname(__DIR__) . '/fv-post-article-preview.php';
$mode = $argv[1] ?? 'none';
$good = ['staging_review'=>true,'article_location_accepted'=>true,'rights_review_recorded'=>true,'offer_merchant_reviewed'=>true,'founder_preview_permission'=>true];
if ($mode === 'good') echo fv_apollo_r266_preview($good);
elseif ($mode === 'missing') { unset($good['offer_merchant_reviewed']); echo fv_apollo_r266_preview($good); }
elseif ($mode === 'string') { $good['founder_preview_permission'] = 'true'; echo fv_apollo_r266_preview($good); }
elseif ($mode === 'false') { $good['staging_review'] = false; echo fv_apollo_r266_preview($good); }
elseif ($mode === 'extra') { $good['merchant_url'] = 'javascript:alert(1)'; echo fv_apollo_r266_preview($good); }
elseif ($mode === 'states') {
 $results = [];
 foreach (array_keys($good) as $key) {
  $bad = $good;unset($bad[$key]);$results['missing_'.$key] = fv_apollo_r266_preview($bad)==='';
  $bad = $good;$bad[$key] = 'true';$results['string_'.$key] = fv_apollo_r266_preview($bad)==='';
  $bad = $good;$bad[$key] = false;$results['false_'.$key] = fv_apollo_r266_preview($bad)==='';
 }
 $results['empty']=fv_apollo_r266_preview([])==='';
 $results['valid']=strlen(fv_apollo_r266_preview($good))>800;
 echo json_encode($results,JSON_THROW_ON_ERROR);
}

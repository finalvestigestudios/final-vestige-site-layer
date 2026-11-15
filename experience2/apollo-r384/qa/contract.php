<?php
/** Offline PHP API stubs, not installed WordPress. Assertion failures abort. */
error_reporting(E_ALL);
$base=dirname(__DIR__);
define('ABSPATH',$base.'/');
$approved=dirname($base).'/apollo-r377/custody.json';
$source=file_get_contents($approved);
if (hash('sha256',$source)!=='60bfa330398b7684463c95afcc7e6ef347d44f22d5a2f1350286a660edb3a76f') { throw new RuntimeException('custody fixture mismatch'); }
$GLOBALS['canonical']=json_decode($source,true,512,JSON_THROW_ON_ERROR)['records'];
$GLOBALS['records']=$GLOBALS['canonical']; $GLOBALS['env']=true;
$GLOBALS['shortcode_tags']=array(); $GLOBALS['hooks']=array(); $GLOBALS['styles']=array();
$GLOBALS['post']=(object) array('post_content'=>'[fv_apollo_source_gallery_r384]');
function fv_r377_environment(){return $GLOBALS['env'];}
function fv_r377_records(){return $GLOBALS['records'];}
function fv_r381_approved($records){return is_array($records)&&$records===$GLOBALS['canonical'];}
function add_action($event,$fn,$priority=10){$GLOBALS['hooks'][]=array($event,$priority,$fn);}
function shortcode_exists($key){return isset($GLOBALS['shortcode_tags'][$key]);}
function add_shortcode($tag,$fn){$GLOBALS['shortcode_tags'][$tag]=$fn;}
function is_singular(){return true;}
function get_queried_object_id(){return 123;}
function get_post($id){return $GLOBALS['post'];}
function has_shortcode($content,$tag){return strpos($content,'['.$tag.']')!==false;}
function wp_enqueue_style(...$args){$GLOBALS['styles'][]=$args;}
function plugins_url($path,$file){return 'https://staging.example.invalid/wp-content/plugins/apollo-r384/'.$path;}
require $base.'/document-gallery.php';
$ok=0; $assert=function($condition,$description)use(&$ok){$ok++;if(!$condition){throw new RuntimeException('FAIL '.$description);}};
$assert(fv_r384_records()!==false,'approved data');
$assert(fv_r384_assets_verified(),'css seal');
$render=fv_r384_render();
$assert(substr_count($render,'data-fv-r384-record')===6,'six record cards');
$assert(substr_count($render,'data-fv-r384-nasa')===6,'six document source anchors');
$assert(substr_count($render,'data-fv-free-cta')===1,'one free CTA');
$assert(substr_count($render,'class="fv-r384__phase"')===3,'three phases');
$assert(substr_count($render,'<details')===6,'native disclosures');
$assert(substr_count($render,'<summary')===6,'keyboard summaries');
$assert(strpos($render,'NASA media-use guidance')!==false,'rights guidance');
$assert(strpos($render,'not endorsed by NASA')!==false,'nonendorsement');
$assert(strpos($render,'paid educator kit is not currently verified')!==false,'offer truth');
$assert(!preg_match('/<(?:img|iframe|canvas|script|video)\b/i',$render),'no media/tracking');
$assert(substr_count($render,FV_R384_BOARD)===5,'five board provenance links');
$assert(substr_count($render,FV_R384_TESTS)===1,'one later retrospective provenance');
$assert(substr_count($render,'href="'.FV_R384_FREE.'"')===1,'exact destination');
$assert(strpos($render,'id="fv-r384-1-event"')!==false,'first instance unique id');
$second=fv_r384_render();
$assert(strpos($second,'id="fv-r384-2-event"')!==false,'second instance distinct');
$assert(strpos($render,'100-percent oxygen')!==false,'source content');
// Test all claims and boundaries escaped, not inserted as live markup.
$GLOBALS['records'][0]['claim']='<script>alert(1)</script>';
$assert(fv_r384_records()===false,'source mutation rejected');
$assert(strpos(fv_r384_render(),'Source gallery unavailable')!==false,'closed on source mutation');
$GLOBALS['records']=$GLOBALS['canonical'];
$GLOBALS['records'][0]['evidence_url']='https://evil.example/';
$assert(fv_r384_records()===false,'foreign URL rejected');
$GLOBALS['records']=$GLOBALS['canonical'];
$GLOBALS['records'][5]['evidence_url']=FV_R384_BOARD;
$assert(fv_r384_records()===false,'later test cannot masquerade as Board');
$GLOBALS['records']=$GLOBALS['canonical'];
$GLOBALS['records'][3]['context_url']='javascript:alert(1)';
$assert(fv_r384_records()===false,'unsafe context URL rejected');
$GLOBALS['records']=$GLOBALS['canonical'];
$GLOBALS['env']=false;
$assert(fv_r384_records()===false,'production disabled');
$assert(strpos(fv_r384_render(),'Source gallery unavailable')!==false,'production no historical claims');
$GLOBALS['env']=true;
$assert(fv_r384_records()!==false,'restoration succeeds');
$assert($GLOBALS['styles']===array(),'no eager assets before hook');
$GLOBALS['post']->post_content='Unrelated article';fv_r384_enqueue();
$assert(count($GLOBALS['styles'])===0,'no sitewide style');
$GLOBALS['post']->post_content='[fv_apollo_source_gallery_r384]';fv_r384_enqueue();
$assert(count($GLOBALS['styles'])===1,'one direct shortcode style');
$assert($GLOBALS['styles'][0][0]==='fv-apollo-r384-gallery','own style handle');
$GLOBALS['env']=false;fv_r384_enqueue();
$assert(count($GLOBALS['styles'])===1,'no additional assets on production');
$GLOBALS['env']=true;
// The staging registration is delayed and refuses a foreign shortcode owner.
$callbacks=array_values(array_filter($GLOBALS['hooks'],fn($h)=>$h[0]==='plugins_loaded'));
$assert(count($callbacks)===1,'one setup callback');
$GLOBALS['shortcode_tags'][FV_R384_TAG]='foreign_handler';
$callbacks[0][2]();
$assert($GLOBALS['shortcode_tags'][FV_R384_TAG]==='foreign_handler','collision preserved');
unset($GLOBALS['shortcode_tags'][FV_R384_TAG]);$callbacks[0][2]();
$assert($GLOBALS['shortcode_tags'][FV_R384_TAG]==='fv_r384_shortcode','owns shortcode only when free');
$assert(strpos(fv_r384_fallback(),FV_R384_FREE)!==false,'fallback keeps free URL');
$fixture='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Apollo R384 local fixture (not staging)</title><style>'.file_get_contents($base.'/assets/gallery.css').'</style></head><body style="margin:0">'. $render .'</body></html>';
if (!is_dir($base.'/QA')) {mkdir($base.'/QA',0775,true);}
file_put_contents($base.'/QA/local-php-fixture.html',$fixture);
file_put_contents($base.'/QA/php-results.json',json_encode(array('status'=>'PHP_STUB_PASS_NOT_WORDPRESS','assertions'=>$ok,'custody_sha256'=>hash('sha256',$source)),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES)."\n");
echo json_encode(array('status'=>'PHP_STUB_PASS_NOT_WORDPRESS','assertions'=>$ok),JSON_PRETTY_PRINT)."\n";
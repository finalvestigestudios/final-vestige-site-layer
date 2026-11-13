<?php
/** R345 simulated WordPress composite pre-head stylesheet gate, NOT installed WordPress. */
declare(strict_types=1);
error_reporting(E_ALL);
define('ABSPATH', __DIR__);
$body=''; $styles=[];
function add_shortcode($tag,$fn): void {}
function add_action($name,$fn,$prio=10): void {}
function is_singular(): bool {return true;}
function get_post($id=null){return (object)['post_type'=>'post','post_content'=>$GLOBALS['body']];}
function has_shortcode($text,$tag): bool {return str_contains($text, '['.$tag.']');}
function parse_blocks($text): array {return [];}
function plugins_url($path,$file): string {return '/test-plugin/'.$path;}
function wp_enqueue_style($name,$src,$deps,$v): void {$GLOBALS['styles'][$name]=$src;}
require __DIR__.'/../../apollo-r340/apollo-accession-gallery.php';
$tests=[
 ['composite','[fv_apollo_experience_r340]',['fv-apollo-r339-chronology','fv-apollo-r345-evidence-plate','fv-apollo-r340-gallery']],
 ['gallery','[fv_apollo_gallery_r340]',['fv-apollo-r340-gallery']],
 ['unrelated','ordinary text',[]],
];
foreach($tests as [$name,$content,$expected]){
 $body=$content;$styles=[];fv_apollo_r340_enqueue();
 $actual=array_keys($styles);sort($actual);sort($expected);
 if($actual!==$expected){fwrite(STDERR,"FAIL $name ".json_encode($actual)."\n");exit(1);}
}
if(strpos(fv_apollo_r340_experience_shortcode(),'data-fv-apollo-claim-ledger')===false){exit(2);}
echo json_encode(['result'=>'PASS','cases'=>count($tests),'composite_stylesheets'=>3,'gallery_only_stylesheets'=>1,'installed_wordpress'=>false],JSON_PRETTY_PRINT)."\n";

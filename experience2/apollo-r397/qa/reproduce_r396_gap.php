<?php
/** Evidence witness: R396's acceptance of unreviewed record attributes and handle collisions.
 *  Native PHP with WP stubs; does not imply real installed WordPress exploitation.
 */
if (!defined('ABSPATH')) define('ABSPATH','/tmp/apollo-r397-repro');
$ledger=json_decode((string)file_get_contents(__DIR__.'/../../apollo-r377/custody.json'),true);
$GLOBALS['records']=$ledger['records'];
$GLOBALS['styles']=[];
function wp_get_environment_type(){return 'staging';}
function is_page($slug){return $slug==='apollo-1-evidence-atlas';}
function fv_r384_records(){return $GLOBALS['records'];}
function wp_enqueue_style($handle,$src,$deps,$ver,$media){$GLOBALS['styles'][]=$handle;}
function plugins_url($path,$plugin){return 'https://staging.fv.example/plugins/'.$path;}
function wp_style_is($handle,$state){return true;} // Deliberately pre-registered collision.
define('FV_R396_APOLLO_QA_ENABLE',true);
require __DIR__.'/../../apollo-r396/staging-custody.php';
$t=$ledger['records'];$t[0]['context_role']='Inaccurate narrative classification';
if(!fv_r396_records_are_reviewed($t)) {fwrite(STDERR,"unexpected R396 rejection\n");exit(1);}
$t=$ledger['records'];$t[0]['affiliate_checkout']='https://merchant.invalid/';
if(!fv_r396_records_are_reviewed($t)) {fwrite(STDERR,"unexpected R396 rejection of extra key\n");exit(1);}
if(!fv_r396_prepaint_eligible()) {fwrite(STDERR,"unexpected R396 block of registered handle\n");exit(1);}
echo "R396 acceptance gaps confirmed: changed context_role, injected extra field, registered-handle collision (PHP stubs only)\n";

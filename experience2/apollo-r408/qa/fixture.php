<?php
/** Instrumented structural fixture only; no full #158 NASA ledger copied or deployed. */
define('ABSPATH','/tmp');
define('FV_R408_ENABLED',true);
define('FV_R408_STAGING_PAGE_ID',408);
function wp_get_environment_type(): string { return $GLOBALS['env'] ?? 'staging'; }
function is_singular(): bool { return true; }
function get_queried_object_id(): int { return $GLOBALS['page_id'] ?? 408; }
function fv_r407_authorized(): bool { return true; }
function fv_r407_assets_valid(string $ignored=''): bool { return true; }
function fv_r407_shortcode($ignored=[]): string {
    static $num = 0; $num++;
    $prefix='fv-ex2-ledger-apollo1-r407-i' . $num . '-record-';
    $out='<div class="fv-r407" data-fv-r407><nav id="fv-r407-rail-' . $num . '"><h2>Chronology</h2></nav><section data-fvx-ledger><h2>Test-only source desk</h2>';
    for($i=1;$i<=6;$i++) {
        $id=sprintf('%02d',$i);
        $out.='<article data-fvx-record id="' . $prefix . $id . '"><h3>Test-only record ' . $i . '</h3><p>Not a primary historical text.</p><details><summary>Source limit</summary><p>Test only.</p></details></article>';
    }
    return $out.'<a href="'.FV_R408_ARTICLE.'">Free Apollo investigation</a></section></div>';
}
require dirname(__DIR__).'/staging-atlas.php';
$GLOBALS['fv_r407_ready']=true;
if (basename(__FILE__) === basename($_SERVER['SCRIPT_FILENAME'] ?? '')) {
    echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R408 test-only experience</title></head><body>';
    echo fv_r408_shortcode(); echo fv_r408_shortcode();
    echo '</body></html>';
}

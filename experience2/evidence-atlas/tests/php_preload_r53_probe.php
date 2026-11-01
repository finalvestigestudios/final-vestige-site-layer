<?php
/* Isolated R53 PHP lifecycle contract. Not an installed WordPress runtime. */
define('ABSPATH', '/tmp/fv-r53-probe/');
define('FV_EX2_APOLLO_SUITE_PRELOAD_PAGE_IDS', array(42, '61', -8, 0));
class WP_Post {
    public $ID;
    public $post_content;
    function __construct($id, $body = '') { $this->ID = $id; $this->post_content = $body; }
}
$GLOBALS['fv_hooks'] = array();
function add_action($name, $callback, $priority = 10) { $GLOBALS['fv_hooks'][] = array($name, $callback, $priority); }
function add_shortcode($tag, $callback) { }
function esc_url($str) { return htmlspecialchars($str, ENT_QUOTES, 'UTF-8'); }
function is_singular() { return true; }
function has_shortcode($content, $tag) { return strpos($content, '[' . $tag . ']') !== false; }
function get_queried_object() { return new WP_Post(11); }
require dirname(__DIR__) . '/integration/fv-ex2-apollo-suite.php';
$result = array(
    'opted_in_id' => fv_ex2_apollo_suite_page_opted_in(new WP_Post(42)),
    'string_id_rejected' => !fv_ex2_apollo_suite_page_opted_in(new WP_Post('42')),
    'string_list_item_rejected' => !fv_ex2_apollo_suite_page_opted_in(new WP_Post(61)),
    'other_page_rejected' => !fv_ex2_apollo_suite_page_opted_in(new WP_Post(43)),
    'negative_id_rejected' => !fv_ex2_apollo_suite_page_opted_in(new WP_Post(-8)),
    'zero_id_rejected' => !fv_ex2_apollo_suite_page_opted_in(new WP_Post(0)),
    'wrong_object_rejected' => !fv_ex2_apollo_suite_page_opted_in((object)array('ID' => 42)),
    'head_hook_priority' => in_array(array('wp_enqueue_scripts','fv_ex2_apollo_suite_pre_enqueue',22), $GLOBALS['fv_hooks'], true)
);
echo json_encode($result, JSON_UNESCAPED_SLASHES), "\n";

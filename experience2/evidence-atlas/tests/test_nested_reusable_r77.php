<?php
/** R77 zero-network source-level WordPress stub; NOT CMS integration evidence. */
error_reporting(E_ALL);
define('ABSPATH', '/dev/null/');
class WP_Post {
    public int $ID;
    public string $post_content;
    public string $post_type;
    public string $post_status;
    function __construct(int $id, string $body, string $type='page', string $status='publish') {
        $this->ID=$id; $this->post_content=$body;
        $this->post_type=$type; $this->post_status=$status;
    }
}
function add_action(...$args): void {}
function add_shortcode(...$args): void {}
function has_shortcode($content, $tag): bool {return strpos($content,'['.$tag.']')!==false;}
function parse_blocks($content): array {
    preg_match_all('/<!-- wp:block \\{"ref":([0-9]+)\\} \\/-->/', $content, $matches);
    $out=[];
    foreach ($matches[1] as $id) {
        $out[]=['blockName'=>'core/block','attrs'=>['ref'=>(int)$id],'innerBlocks'=>[]];
    }
    if (str_starts_with($content, 'GROUP:')) {
        return [['blockName'=>'core/group','attrs'=>[],'innerBlocks'=>$out]];
    }
    return $out;
}
$posts=[];
function get_post($id) {global $posts; return $posts[$id]??null;}
require_once __DIR__.'/../integration/fv-ex2-apollo-suite.php';
$ok=0;
function check($actual, $expected, $label): void {
    global $ok;
    if ($actual !== $expected) {fwrite(STDERR,"FAILED $label\n");exit(1);}
    $ok++;
}
$posts[10]=new WP_Post(10,'<!-- wp:shortcode -->[fv_ex2_apollo_suite]<!-- /wp:shortcode -->','wp_block');
$posts[11]=new WP_Post(11,'<!-- wp:block {"ref":10} /-->','wp_block');
check(fv_ex2_apollo_suite_nested_reusable_on_page(new WP_Post(1,'<!-- wp:block {"ref":11} /-->')),true,'two-level published core/block');
check(fv_ex2_apollo_suite_nested_reusable_on_page(new WP_Post(2,'GROUP:<!-- wp:block {"ref":11} /-->')),true,'child group nested blocks');
check(fv_ex2_apollo_suite_nested_reusable_on_page(new WP_Post(3,'<!-- wp:shortcode -->[fv_ex2_apollo_suite]<!-- /wp:shortcode -->')),true,'top-level preserved');
check(fv_ex2_apollo_suite_nested_reusable_on_page(new WP_Post(4,'<!-- wp:paragraph --><p>Safe</p><!-- /wp:paragraph -->')),false,'unrelated content');
$posts[12]=new WP_Post(12,'[fv_ex2_apollo_suite]','wp_block','draft');
check(fv_ex2_apollo_suite_nested_reusable_on_page(new WP_Post(5,'<!-- wp:block {"ref":12} /-->')),false,'nonpublished pattern excluded');
$posts[13]=new WP_Post(13,'[fv_ex2_apollo_suite]','page');
check(fv_ex2_apollo_suite_nested_reusable_on_page(new WP_Post(6,'<!-- wp:block {"ref":13} /-->')),false,'non-wp_block reference excluded');
$posts[14]=new WP_Post(14,'<!-- wp:block {"ref":15} /-->','wp_block');
$posts[15]=new WP_Post(15,'<!-- wp:block {"ref":14} /-->','wp_block');
check(fv_ex2_apollo_suite_nested_reusable_on_page(new WP_Post(7,'<!-- wp:block {"ref":14} /-->')),false,'cycle fails closed');
check(fv_ex2_apollo_suite_nested_reusable_on_page(new WP_Post(8,'<!-- wp:block {"ref":999} /-->')),false,'missing pattern fails closed');
check(fv_ex2_apollo_suite_nested_reusable_on_page(new WP_Post(9,str_repeat('X',200010).'<!-- wp:block {"ref":11} /-->')),false,'oversized content bounded');
check(fv_ex2_apollo_suite_nested_reusable_on_page(null),false,'invalid WordPress post excluded');
for ($i=20;$i<29;$i++) {$posts[$i]=new WP_Post($i,'<!-- wp:block {"ref":'.($i+1).'} /-->','wp_block');}
$posts[29]=new WP_Post(29,'[fv_ex2_apollo_suite]','wp_block');
check(fv_ex2_apollo_suite_nested_reusable_on_page(new WP_Post(30,'<!-- wp:block {"ref":20} /-->')),false,'deep recursion bounded');
echo "R77 source-level PHP stub: $ok assertions PASS\n";

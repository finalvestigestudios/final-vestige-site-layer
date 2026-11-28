<?php
/**
 * Plugin Name: FV Newsroom (review candidate)
 * Description: Dedicated, evidence-first news archive and private source lead queue. Independent candidate; not loaded by Site Layer.
 * Version: 0.1.0
 */
if (!defined('ABSPATH')) { exit; }

function fvn_desks() {
    return [
        'archaeology' => 'Archaeology & Lost History',
        'science-space' => 'Science & Space',
        'hidden-record' => 'The Hidden Record',
        'mysteries' => 'Mysteries & Anomalies',
        'technology' => 'Technology & Human Ingenuity',
        'engineering-failures' => 'Catastrophes & Engineering Failures',
        'mind' => 'Mind & Consciousness',
        'earth' => 'Earth & the Extraordinary',
    ];
}
function fvn_register() {
    register_post_type('fv_news', [
        'label'=>'FV News', 'public'=>true, 'show_in_rest'=>true,
        'has_archive'=>'news', 'rewrite'=>['slug'=>'news','with_front'=>false],
        'supports'=>['title','editor','excerpt','thumbnail','author','revisions'],
        'menu_icon'=>'dashicons-media-document',
    ]);
    register_taxonomy('fv_news_desk', ['fv_news'], [
        'label'=>'News Desks', 'public'=>true, 'show_in_rest'=>true,
        'hierarchical'=>true, 'rewrite'=>['slug'=>'news-desk','with_front'=>false],
    ]);
}
add_action('init','fvn_register');
function fvn_activate() {
    fvn_register();
    foreach (fvn_desks() as $slug=>$label) {
        if (!term_exists($slug,'fv_news_desk')) {
            wp_insert_term($label,'fv_news_desk',['slug'=>$slug]);
        }
    }
    flush_rewrite_rules(false);
}
register_activation_hook(__FILE__,'fvn_activate');
function fvn_deactivate() {
    wp_clear_scheduled_hook('fvn_collect_leads');
    unregister_post_type('fv_news');
    unregister_taxonomy('fv_news_desk');
    flush_rewrite_rules(false);
}
register_deactivation_hook(__FILE__,'fvn_deactivate');

function fvn_fields() {
    return [
        'source_url'=>'Primary source HTTPS URL',
        'source_notes'=>'Verification, original reporting and additional sources',
        'image_url'=>'Original image record / licensing URL',
        'image_credit'=>'Image credit, license and any restrictions',
        'reviewer'=>'Actual responsible reviewer',
    ];
}
function fvn_box() {
    add_meta_box('fvn-evidence','News evidence and image rights','fvn_box_render','fv_news','normal','high');
}
add_action('add_meta_boxes_fv_news','fvn_box');
function fvn_box_render($post) {
    wp_nonce_field('fvn_review','fvn_nonce');
    foreach (fvn_fields() as $key=>$label) {
        printf('<p><label for="fvn_%1$s">%2$s</label><br><textarea class="widefat" rows="2" id="fvn_%1$s" name="fvn[%1$s]">%3$s</textarea></p>',
            esc_attr($key),esc_html($label),esc_textarea(get_post_meta($post->ID,'_fvn_'.$key,true)));
    }
    echo '<p>Save as draft before publication. A source link is not verification. An image must be cleared at item level and have accurate alternative text.</p>';
    printf('<p><label><input type="checkbox" name="fvn_reviewed" value="1" %s> I reviewed the exact story, original value, claims, image permissions and corrections implications.</label></p>',
        checked(get_post_meta($post->ID,'_fvn_reviewed',true),'1',false));
}
function fvn_save($id) {
    if (wp_is_post_revision($id) || wp_is_post_autosave($id) ||
        !current_user_can('edit_post',$id) ||
        empty($_POST['fvn_nonce']) || !wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['fvn_nonce'])),'fvn_review')) { return; }
    $data = isset($_POST['fvn']) && is_array($_POST['fvn']) ? wp_unslash($_POST['fvn']) : [];
    foreach (fvn_fields() as $key=>$label) {
        $value = isset($data[$key]) && is_string($data[$key]) ? $data[$key] : '';
        update_post_meta($id,'_fvn_'.$key,substr(sanitize_textarea_field($value),0,4000));
    }
    update_post_meta($id,'_fvn_reviewed',isset($_POST['fvn_reviewed']) ? '1' : '0');
}
add_action('save_post_fv_news','fvn_save');
function fvn_https($url) {
    $p=wp_parse_url($url);
    return is_array($p) && ($p['scheme']??'')==='https' && !empty($p['host']) && empty($p['user']) && empty($p['pass']);
}
function fvn_ready($id) {
    if (!$id || get_post_meta($id,'_fvn_reviewed',true)!=='1') return false;
    foreach (fvn_fields() as $key=>$label) {
        $v=get_post_meta($id,'_fvn_'.$key,true);
        if (!is_string($v) || trim($v)==='') return false;
        if (in_array($key,['source_url','image_url'],true) && !fvn_https($v)) return false;
    }
    $image=get_post_thumbnail_id($id);
    return $image && wp_attachment_is_image($image) &&
        trim((string)get_post_meta($image,'_wp_attachment_image_alt',true))!=='' &&
        (bool)wp_get_post_terms($id,'fv_news_desk',['fields'=>'ids']) &&
        !is_wp_error(wp_get_post_terms($id,'fv_news_desk',['fields'=>'ids']));
}
// Publication is human-only. Existing draft evidence is required; no feed item becomes a post.
function fvn_gate($data,$postarr) {
    if (($data['post_type']??'')==='fv_news' && in_array($data['post_status']??'',['publish','future'],true)) {
        $id=(int)($postarr['ID']??0);
        if (!fvn_ready($id)) $data['post_status']='draft';
    }
    return $data;
}
add_filter('wp_insert_post_data','fvn_gate',10,2);
// Re-evaluate after metabox, terms and featured image writes where available.
function fvn_final_gate($id,$post) {
    if ($post->post_type==='fv_news' && in_array($post->post_status,['publish','future'],true) && !fvn_ready($id)) {
        remove_action('wp_after_insert_post','fvn_final_gate',100);
        wp_update_post(['ID'=>$id,'post_status'=>'draft']);
        add_action('wp_after_insert_post','fvn_final_gate',100,2);
    }
}
add_action('wp_after_insert_post','fvn_final_gate',100,2);

function fvn_template($template) {
    if (is_post_type_archive('fv_news') || is_tax('fv_news_desk')) {
        return __DIR__.'/archive.php';
    }
    return $template;
}
add_filter('template_include','fvn_template');
function fvn_assets() {
    if (is_post_type_archive('fv_news') || is_tax('fv_news_desk') || is_singular('fv_news')) {
        wp_enqueue_style('fvn-news',plugins_url('news.css',__FILE__),[],'0.1.0');
    }
}
add_action('wp_enqueue_scripts','fvn_assets');
function fvn_evidence($content) {
    if (!is_singular('fv_news') || !in_the_loop() || !is_main_query()) return $content;
    $id=get_the_ID();
    if (!fvn_ready($id)) return $content;
    $source=get_post_meta($id,'_fvn_source_url',true);
    $credit=get_post_meta($id,'_fvn_image_credit',true);
    $image=get_post_meta($id,'_fvn_image_url',true);
    return $content.'<aside class="fvn-evidence"><h2>Sources &amp; image provenance</h2><p><a href="'.esc_url($source).'">Primary source</a></p><p><a href="'.esc_url($image).'">Image record</a> — '.esc_html($credit).'</p><p><a href="'.esc_url(home_url('/editorial-standards/')).'">Editorial standards</a></p></aside>';
}
add_filter('the_content','fvn_evidence',20);

// Source polling is OFF until an operator enables the constant after reviewing the source registry.
// Discovery stores only bounded metadata in a private admin queue, never article bodies or images.
function fvn_sources() {
    return ['nasa'=>['label'=>'NASA','url'=>'https://www.nasa.gov/news-release/feed/','domain'=>'nasa.gov','desk'=>'science-space']];
}
function fvn_schedule($s) { $s['fvn_five_minutes']=['interval'=>300,'display'=>'FV five minutes']; return $s; }
add_filter('cron_schedules','fvn_schedule');
function fvn_enabled() { return defined('FV_NEWS_DISCOVERY_ENABLED') && FV_NEWS_DISCOVERY_ENABLED===true; }
function fvn_cron_setup() {
    if (fvn_enabled()) {
        if (!wp_next_scheduled('fvn_collect_leads')) wp_schedule_event(time()+60,'fvn_five_minutes','fvn_collect_leads');
    } else {
        if (wp_next_scheduled('fvn_collect_leads')) wp_clear_scheduled_hook('fvn_collect_leads');
    }
}
add_action('init','fvn_cron_setup',20);
function fvn_source_match($url,$domain) {
    if (!fvn_https($url)) return false;
    $host=strtolower((string)wp_parse_url($url,PHP_URL_HOST));
    return $host===$domain || substr($host,-strlen('.'.$domain))==='.' . $domain;
}
function fvn_collect() {
    if (!fvn_enabled() || get_transient('fvn_lead_lock')) return;
    set_transient('fvn_lead_lock',1,240);
    try {
        require_once ABSPATH.WPINC.'/feed.php';
        $cache=function(){return 300;};
        add_filter('wp_feed_cache_transient_lifetime',$cache);
        $leads=get_option('fvn_source_leads',[]);
        if (!is_array($leads)) $leads=[];
        $health=[];
        foreach (fvn_sources() as $key=>$source) {
            $feed=fetch_feed($source['url']);
            if (is_wp_error($feed)) { $health[$key]=['ok'=>false,'checked'=>time()]; continue; }
            $health[$key]=['ok'=>true,'checked'=>time()];
            foreach ($feed->get_items(0,20) as $item) {
                $url=esc_url_raw($item->get_permalink(),['https']);
                $date=(int)$item->get_date('U');
                if (!fvn_source_match($url,$source['domain']) || !$date || $date<time()-7*DAY_IN_SECONDS || $date>time()+300) continue;
                $hash=hash('sha256',$url);
                if (isset($leads[$hash])) continue;
                $title=trim(wp_strip_all_tags($item->get_title()));
                if (!$title) continue;
                $leads[$hash]=['title'=>substr($title,0,500),'url'=>$url,'published'=>$date,
                    'discovered'=>time(),'source'=>$source['label'],'desk'=>$source['desk']];
            }
        }
        remove_filter('wp_feed_cache_transient_lifetime',$cache);
        $leads=array_filter($leads,function($l){return ($l['published']??0)>=time()-7*DAY_IN_SECONDS;});
        uasort($leads,function($a,$b){return $b['published']<=>$a['published'];});
        update_option('fvn_source_leads',array_slice($leads,0,150,true),false);
        update_option('fvn_source_health',$health,false);
    } finally { delete_transient('fvn_lead_lock'); }
}
add_action('fvn_collect_leads','fvn_collect');
function fvn_admin_menu() {
    add_submenu_page('edit.php?post_type=fv_news','Source leads','Source leads','edit_posts','fvn-leads','fvn_admin');
}
add_action('admin_menu','fvn_admin_menu');
function fvn_admin() {
    if (!current_user_can('edit_posts')) return;
    echo '<div class="wrap"><h1>FV News source leads</h1><p>Private leads only. Verify each item, add original reporting, clear images, and create a separate editorial draft. No automatic publishing.</p>';
    echo '<p>Discovery: '.(fvn_enabled()?'Enabled':'Disabled').'</p>';
    foreach ((array)get_option('fvn_source_health',[]) as $k=>$h) {
        printf('<p>%s: %s — %s UTC</p>',esc_html($k),!empty($h['ok'])?'Feed read':'Feed error',esc_html(gmdate('Y-m-d H:i',(int)$h['checked'])));
    }
    echo '<ul>';
    foreach ((array)get_option('fvn_source_leads',[]) as $lead) {
        printf('<li><a href="%s">%s</a> — %s · %s UTC</li>',esc_url($lead['url']),esc_html($lead['title']),esc_html($lead['source']),esc_html(gmdate('Y-m-d H:i',$lead['published'])));
    }
    echo '</ul></div>';
}

<?php
if (!defined('ABSPATH')) exit;
get_header();
$desk=is_tax('fv_news_desk') ? get_queried_object() : null;
$label=$desk && isset($desk->name) ? $desk->name : 'Final Vestige News';
$terms=get_terms(['taxonomy'=>'fv_news_desk','hide_empty'=>false]);
?>
<main id="fvn-main" class="fvn-shell">
    <header class="fvn-masthead">
        <p class="fvn-kicker">FINAL VESTIGE STUDIOS / NEWSROOM</p>
        <h1><?php echo esc_html($label); ?></h1>
        <p>The stories others overlook. The evidence that matters.</p>
        <nav aria-label="News desks" class="fvn-desks">
            <a href="<?php echo esc_url(get_post_type_archive_link('fv_news')); ?>">All news</a>
            <?php if (!is_wp_error($terms)) foreach ($terms as $term) {
                $link=get_term_link($term);
                if (!is_wp_error($link)) {
                    echo '<a href="'.esc_url($link).'"'.($desk && $desk->term_id===$term->term_id?' aria-current="page"':'').'>'.esc_html($term->name).'</a>';
                }
            } ?>
        </nav>
    </header>
    <div class="fvn-columns">
        <section aria-labelledby="fvn-latest">
            <div class="fvn-section-heading"><h2 id="fvn-latest">Latest reporting</h2><span>Newest first</span></div>
            <div class="fvn-grid">
                <?php $index=0; while (have_posts()) : the_post(); ?>
                    <article <?php post_class('fvn-card '.($index++===0 && !is_paged()?'fvn-lead':'')); ?>>
                        <?php if (has_post_thumbnail()) : ?>
                            <a class="fvn-image" href="<?php the_permalink(); ?>" tabindex="-1" aria-hidden="true"><?php the_post_thumbnail('large',['loading'=>$index===1?'eager':'lazy','decoding'=>'async']); ?></a>
                        <?php endif; ?>
                        <div class="fvn-card-copy">
                            <p class="fvn-kicker"><?php
                                $names=wp_get_post_terms(get_the_ID(),'fv_news_desk',['fields'=>'names']);
                                if (!is_wp_error($names)) echo esc_html(implode(' · ',$names));
                            ?></p>
                            <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
                            <p><?php echo esc_html(wp_trim_words(get_the_excerpt(),36)); ?></p>
                            <p class="fvn-date"><time datetime="<?php echo esc_attr(get_the_date(DATE_W3C)); ?>"><?php echo esc_html(get_the_date('M j, Y')); ?></time> · <?php echo esc_html(get_the_time('g:i a T')); ?></p>
                        </div>
                    </article>
                <?php endwhile; if (!$index) : ?>
                    <p class="fvn-empty">No verified reports have been published in this edition yet. Visit the investigations archive for existing research.</p>
                <?php endif; ?>
            </div>
            <?php the_posts_pagination(['mid_size'=>1,'prev_text'=>'Previous','next_text'=>'Next']); ?>
        </section>
        <aside class="fvn-rail" aria-label="Explore Final Vestige">
            <div class="fvn-rail-box"><p class="fvn-kicker">THE DAILY EDITION</p><h2>Follow the evidence.</h2><p>Explore source-linked reporting and longer investigations from Final Vestige Studios.</p><a href="<?php echo esc_url(home_url('/blog/')); ?>">Read the investigations</a></div>
            <div class="fvn-rail-box"><p class="fvn-kicker">HOW WE REPORT</p><h2>Evidence before speculation.</h2><p>We distinguish established facts, developing reports and unresolved questions.</p><a href="<?php echo esc_url(home_url('/editorial-standards/')); ?>">Our editorial standards</a></div>
        </aside>
    </div>
</main>
<?php get_footer(); ?>

<?php
defined('ABSPATH') || exit;

final class FVDB_Admin {
    public static function boot(): void {
        add_action('admin_menu', [self::class, 'admin_menu']);
        add_action('admin_post_fvdb_regenerate_secret', [self::class, 'regenerate_secret']);
    }

    public static function admin_menu(): void {
        add_management_page(
            'Final Vestige Deployment Bridge',
            'FV Deployment Bridge',
            'manage_options',
            'fv-deployment-bridge',
            [self::class, 'admin_page']
        );
    }

    public static function admin_page(): void {
        if (!current_user_can('manage_options')) {
            wp_die('Insufficient permissions.');
        }
        require_once ABSPATH . 'wp-admin/includes/file.php';
        $secret = FVDB_Auth::current_secret();
        $state = FVDB_State::get();
        $status_url = rest_url(FVDB_REST_NAMESPACE . '/status');
        $deploy_url = rest_url(FVDB_REST_NAMESPACE . '/deploy');
        $zip_ok = class_exists('ZipArchive');
        $fs_direct = get_filesystem_method() === 'direct';
        ?>
        <div class="wrap">
            <h1>Final Vestige Deployment Bridge</h1>
            <p><strong>Bridge version:</strong> <?php echo esc_html(FVDB_VERSION); ?></p>
            <p><strong>Allowed repository:</strong> <code><?php echo esc_html(FVDB_EXPECTED_REPOSITORY); ?></code></p>
            <p><strong>Allowed branch:</strong> <code><?php echo esc_html(FVDB_EXPECTED_BRANCH); ?></code></p>
            <p><strong>Target plugin:</strong> <code><?php echo esc_html(FVDB_TARGET_SLUG); ?></code></p>
            <h2>Host capability</h2>
            <ul>
                <li>ZipArchive: <strong><?php echo $zip_ok ? 'available' : 'unavailable'; ?></strong></li>
                <li>Direct filesystem: <strong><?php echo $fs_direct ? 'available' : 'unavailable'; ?></strong></li>
            </ul>
            <p>If either capability is unavailable, the bridge will refuse deployment without changing the Site Layer.</p>
            <h2>GitHub Actions secret</h2>
            <p>Add this value to the private GitHub repository as an Actions secret named <code>FV_WP_DEPLOY_SECRET</code>. Treat it like a password.</p>
            <p><input id="fvdb-secret" type="password" readonly value="<?php echo esc_attr($secret); ?>" style="width:min(760px,95%);font-family:monospace" />
            <button type="button" class="button" onclick="const i=document.getElementById('fvdb-secret');i.type=i.type==='password'?'text':'password'">Show / hide</button></p>
            <p><strong>Status endpoint:</strong> <code><?php echo esc_html($status_url); ?></code></p>
            <p><strong>Deploy endpoint:</strong> <code><?php echo esc_html($deploy_url); ?></code></p>
            <h2>Last deployment state</h2>
            <pre><?php echo esc_html(wp_json_encode($state, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES)); ?></pre>
            <hr />
            <p><strong>Regenerating the secret immediately invalidates the current GitHub Actions secret.</strong></p>
            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <input type="hidden" name="action" value="fvdb_regenerate_secret" />
                <?php wp_nonce_field('fvdb_regenerate_secret'); ?>
                <?php submit_button('Regenerate deployment secret', 'secondary', 'submit', false, ['onclick' => "return confirm('Regenerate the deployment secret? Existing automated deployments will stop until GitHub is updated.');"]); ?>
            </form>
        </div>
        <?php
    }

    public static function regenerate_secret(): void {
        if (!current_user_can('manage_options')) {
            wp_die('Insufficient permissions.');
        }
        check_admin_referer('fvdb_regenerate_secret');
        FVDB_Auth::regenerate_secret();
        wp_safe_redirect(add_query_arg('page', 'fv-deployment-bridge', admin_url('tools.php')));
        exit;
    }
}

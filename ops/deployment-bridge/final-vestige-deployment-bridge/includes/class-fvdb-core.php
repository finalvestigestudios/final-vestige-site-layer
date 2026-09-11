<?php
defined('ABSPATH') || exit;

final class FVDB_Core {
    public static function boot(): void {
        register_activation_hook(FVDB_FILE, [self::class, 'activate']);
        add_action('rest_api_init', [self::class, 'register_routes']);
        FVDB_Admin::boot();
    }

    public static function activate(): void {
        FVDB_Auth::ensure_secret();
        FVDB_State::ensure();
    }

    public static function register_routes(): void {
        register_rest_route(FVDB_REST_NAMESPACE, '/status', [
            'methods' => 'GET',
            'callback' => [self::class, 'status'],
            'permission_callback' => '__return_true',
        ]);
        register_rest_route(FVDB_REST_NAMESPACE, '/deploy', [
            'methods' => 'POST',
            'callback' => [self::class, 'deploy'],
            'permission_callback' => '__return_true',
        ]);
    }

    public static function status(WP_REST_Request $request): WP_REST_Response {
        require_once ABSPATH . 'wp-admin/includes/plugin.php';
        require_once ABSPATH . 'wp-admin/includes/file.php';
        $state = FVDB_State::get();
        $manifest = FVDB_Package::read_installed_manifest();
        return new WP_REST_Response([
            'ok' => true,
            'bridge_version' => FVDB_VERSION,
            'repository' => FVDB_EXPECTED_REPOSITORY,
            'branch' => FVDB_EXPECTED_BRANCH,
            'host_capability' => [
                'ziparchive' => class_exists('ZipArchive'),
                'filesystem_direct' => get_filesystem_method() === 'direct',
            ],
            'site_layer' => [
                'installed' => is_file(FVDB_Package::target_main_path()),
                'active' => is_plugin_active(FVDB_TARGET_SLUG . '/' . FVDB_TARGET_MAIN),
                'commit' => $manifest['commit'] ?? ($state['last_commit'] ?? ''),
                'package_sha256' => $state['last_package_sha256'] ?? '',
            ],
            'last_status' => $state['last_status'] ?? 'unknown',
            'last_deployed_at' => $state['last_deployed_at'] ?? '',
        ], 200);
    }

    public static function deploy(WP_REST_Request $request): WP_REST_Response {
        $raw = $request->get_body();
        $body_sha = hash('sha256', $raw);
        $headers = FVDB_Auth::headers($request);
        $auth = FVDB_Auth::authenticate($headers, $body_sha);
        if (is_wp_error($auth)) {
            // Authentication failures do not write state. This avoids unauthenticated
            // request spam becoming a database-write amplification path or auth oracle.
            return new WP_REST_Response([
                'ok' => false,
                'error' => 'authentication_failed',
                'message' => 'Deployment authentication failed.',
            ], 401);
        }

        $payload = json_decode($raw, true);
        if (!is_array($payload)) {
            return self::reject_authenticated('invalid_json', 'Request body must be JSON.', 400);
        }
        $commit = strtolower((string) ($headers['commit'] ?? ''));
        $zip_b64 = (string) ($payload['package_base64'] ?? '');
        $declared_sha = strtolower((string) ($payload['package_sha256'] ?? ''));
        $result = FVDB_Package::install_from_base64($zip_b64, $declared_sha, $commit);
        if (is_wp_error($result)) {
            return self::error_authenticated($result, 500);
        }

        FVDB_State::write([
            'last_status' => 'deployed',
            'last_commit' => $commit,
            'last_package_sha256' => $result['package_sha256'],
            'last_deployed_at' => gmdate('c'),
            'last_error' => '',
        ]);
        return new WP_REST_Response([
            'ok' => true,
            'status' => 'deployed',
            'commit' => $commit,
            'package_sha256' => $result['package_sha256'],
            'target' => FVDB_TARGET_SLUG,
            'activation_changed' => false,
        ], 200);
    }

    private static function reject_authenticated(string $code, string $message, int $status): WP_REST_Response {
        FVDB_State::record_authenticated_error($code, $message);
        return new WP_REST_Response(['ok' => false, 'error' => $code, 'message' => $message], $status);
    }

    private static function error_authenticated(WP_Error $error, int $status): WP_REST_Response {
        FVDB_State::record_authenticated_error($error->get_error_code(), $error->get_error_message());
        return new WP_REST_Response([
            'ok' => false,
            'error' => $error->get_error_code(),
            'message' => $error->get_error_message(),
        ], $status);
    }
}

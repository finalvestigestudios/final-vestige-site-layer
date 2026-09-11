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
        $headers = FVDB_Auth::headers($request);
        $auth = FVDB_Auth::authenticate_status($headers);
        if (is_wp_error($auth)) {
            return self::authentication_failed();
        }
        require_once ABSPATH . 'wp-admin/includes/file.php';
        return new WP_REST_Response([
            'ok' => true,
            'bridge_version' => FVDB_VERSION,
            'host_capability' => [
                'ziparchive' => class_exists('ZipArchive'),
                'filesystem_direct' => get_filesystem_method() === 'direct',
            ],
        ], 200);
    }

    public static function deploy(WP_REST_Request $request): WP_REST_Response {
        $raw = $request->get_body();
        $body_sha = hash('sha256', $raw);
        $headers = FVDB_Auth::headers($request);
        $auth = FVDB_Auth::authenticate_deploy($headers, $body_sha);
        if (is_wp_error($auth)) {
            return self::authentication_failed();
        }

        $payload = json_decode($raw, true);
        if (!is_array($payload)) {
            return self::reject_authenticated('invalid_json', 'Request body must be JSON.', 400);
        }
        $commit = strtolower((string) ($headers['commit'] ?? ''));
        $zip_b64 = (string) ($payload['package_base64'] ?? '');
        $declared_sha = strtolower((string) ($payload['package_sha256'] ?? ''));
        if (!preg_match('/^[a-f0-9]{64}$/', $declared_sha) || $zip_b64 === '') {
            return self::reject_authenticated('invalid_package_envelope', 'Package envelope is incomplete or invalid.', 400);
        }

        $idempotency_key = hash('sha256', $commit . "\n" . $declared_sha);
        $lock = FVDB_Lock::acquire($idempotency_key);
        if (is_wp_error($lock)) {
            return self::error_authenticated($lock, 409, false);
        }

        try {
            $state = FVDB_State::get();
            if (
                hash_equals((string) ($state['last_idempotency_key'] ?? ''), $idempotency_key)
                && hash_equals((string) ($state['last_commit'] ?? ''), $commit)
                && hash_equals((string) ($state['last_package_sha256'] ?? ''), $declared_sha)
            ) {
                $installed = FVDB_Package::installed_matches($commit);
                if ($installed === true) {
                    return new WP_REST_Response([
                        'ok' => true,
                        'status' => 'already_deployed',
                        'commit' => $commit,
                        'package_sha256' => $declared_sha,
                        'target' => FVDB_TARGET_SLUG,
                        'activation_changed' => false,
                    ], 200);
                }
            }

            $result = FVDB_Package::install_from_base64($zip_b64, $declared_sha, $commit);
            if (is_wp_error($result)) {
                return self::error_authenticated($result, 500);
            }

            FVDB_State::write([
                'last_status' => 'deployed',
                'last_commit' => $commit,
                'last_package_sha256' => $result['package_sha256'],
                'last_idempotency_key' => $idempotency_key,
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
        } finally {
            FVDB_Lock::release($lock);
        }
    }

    private static function authentication_failed(): WP_REST_Response {
        // Authentication failures do not write state and intentionally expose no reason.
        return new WP_REST_Response([
            'ok' => false,
            'error' => 'authentication_failed',
            'message' => 'Deployment authentication failed.',
        ], 401);
    }

    private static function reject_authenticated(string $code, string $message, int $status): WP_REST_Response {
        FVDB_State::record_authenticated_error($code, $message);
        return new WP_REST_Response(['ok' => false, 'error' => $code, 'message' => $message], $status);
    }

    private static function error_authenticated(WP_Error $error, int $status, bool $record = true): WP_REST_Response {
        if ($record) {
            FVDB_State::record_authenticated_error($error->get_error_code(), $error->get_error_message());
        }
        return new WP_REST_Response([
            'ok' => false,
            'error' => $error->get_error_code(),
            'message' => $error->get_error_message(),
        ], $status);
    }
}

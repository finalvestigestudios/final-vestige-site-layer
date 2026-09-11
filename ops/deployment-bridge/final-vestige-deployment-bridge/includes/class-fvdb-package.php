<?php
defined('ABSPATH') || exit;

final class FVDB_Package {
    private const MAX_ZIP_BYTES = 5_242_880;
    private const MAX_TOTAL_UNCOMPRESSED = 20_971_520;
    private const MAX_FILES = 250;
    private const MAX_ENTRIES = 400;

    public static function install_from_base64(string $zip_b64, string $declared_sha, string $commit) {
        if (!preg_match('/^[a-f0-9]{64}$/', $declared_sha)) {
            return new WP_Error('invalid_package_hash', 'package_sha256 must be a 64-character SHA-256 value.');
        }
        if ($zip_b64 === '' || strlen($zip_b64) > (int) ceil(self::MAX_ZIP_BYTES * 1.5)) {
            return new WP_Error('invalid_package', 'Package is missing or too large.');
        }
        $zip_bytes = base64_decode($zip_b64, true);
        if (!is_string($zip_bytes)) {
            return new WP_Error('invalid_base64', 'Package is not valid base64.');
        }
        if (strlen($zip_bytes) > self::MAX_ZIP_BYTES) {
            return new WP_Error('package_too_large', 'Compressed package exceeds the configured size limit.');
        }
        $actual_sha = hash('sha256', $zip_bytes);
        if (!hash_equals($declared_sha, $actual_sha)) {
            return new WP_Error('package_hash_mismatch', 'Package SHA-256 mismatch.');
        }
        $result = self::install_package($zip_bytes, $commit);
        if (is_wp_error($result)) {
            return $result;
        }
        return ['package_sha256' => $actual_sha];
    }

    public static function target_main_path(): string {
        return trailingslashit(WP_PLUGIN_DIR) . FVDB_TARGET_SLUG . '/' . FVDB_TARGET_MAIN;
    }

    public static function read_installed_manifest(): array {
        $path = trailingslashit(WP_PLUGIN_DIR) . FVDB_TARGET_SLUG . '/release-manifest.json';
        if (!is_file($path)) {
            return [];
        }
        $decoded = json_decode((string) file_get_contents($path), true);
        return is_array($decoded) ? $decoded : [];
    }

    private static function install_package(string $zip_bytes, string $commit) {
        if (!class_exists('ZipArchive')) {
            return new WP_Error('zip_unavailable', 'ZipArchive is not available on this host.');
        }
        require_once ABSPATH . 'wp-admin/includes/file.php';
        if (get_filesystem_method() !== 'direct') {
            return new WP_Error('filesystem_not_direct', 'Host does not expose the direct filesystem method required by this bridge.');
        }

        $tmp_zip = wp_tempnam('fvdb-release.zip');
        if (!$tmp_zip || file_put_contents($tmp_zip, $zip_bytes) !== strlen($zip_bytes)) {
            return new WP_Error('temp_write_failed', 'Could not write temporary release package.');
        }
        $zip = new ZipArchive();
        $open = $zip->open($tmp_zip, ZipArchive::RDONLY);
        if ($open !== true) {
            @unlink($tmp_zip);
            return new WP_Error('zip_open_failed', 'Could not open release ZIP.');
        }
        if ($zip->numFiles > self::MAX_ENTRIES) {
            $zip->close();
            @unlink($tmp_zip);
            return new WP_Error('zip_entry_limit', 'ZIP contains too many entries.');
        }

        $file_count = 0;
        $expanded = 0;
        $entries = [];
        for ($i = 0; $i < $zip->numFiles; $i++) {
            $stat = $zip->statIndex($i);
            $name = is_array($stat) ? (string) ($stat['name'] ?? '') : '';
            $size = is_array($stat) ? (int) ($stat['size'] ?? 0) : 0;
            $enc = is_array($stat) ? (int) ($stat['encryption_method'] ?? 0) : 0;
            if (!self::safe_zip_path($name)) {
                return self::zip_error($zip, $tmp_zip, 'unsafe_zip_path', 'ZIP contains an unsafe path.');
            }
            if (!str_starts_with($name, FVDB_TARGET_SLUG . '/')) {
                return self::zip_error($zip, $tmp_zip, 'unexpected_zip_root', 'Every ZIP entry must live under the final-vestige-site-layer/ root.');
            }
            if ($enc !== 0) {
                return self::zip_error($zip, $tmp_zip, 'encrypted_zip_rejected', 'Encrypted ZIP entries are not accepted.');
            }
            if (isset($entries[$name])) {
                return self::zip_error($zip, $tmp_zip, 'duplicate_zip_entry', 'ZIP contains a duplicate path.');
            }
            $entries[$name] = true;
            if (!str_ends_with($name, '/')) {
                $file_count++;
                $expanded += max(0, $size);
            }
            if ($file_count > self::MAX_FILES || $expanded > self::MAX_TOTAL_UNCOMPRESSED) {
                return self::zip_error($zip, $tmp_zip, 'zip_limits_exceeded', 'ZIP exceeds file-count or expanded-size limits.');
            }
        }
        if ($file_count < 2) {
            return self::zip_error($zip, $tmp_zip, 'package_too_small', 'Release ZIP does not contain enough files to be a valid site-layer package.');
        }

        $tmp_dir = trailingslashit(WP_CONTENT_DIR) . 'fv-deploy-staging-' . wp_generate_password(12, false, false);
        if (!wp_mkdir_p($tmp_dir)) {
            return self::zip_error($zip, $tmp_zip, 'staging_dir_failed', 'Could not create staging directory.');
        }

        // Stream validated ZIP entries into regular files ourselves. ZipArchive::extractTo
        // is intentionally not used, so symlink/special-file metadata is never materialized.
        for ($i = 0; $i < $zip->numFiles; $i++) {
            $stat = $zip->statIndex($i);
            $name = is_array($stat) ? (string) ($stat['name'] ?? '') : '';
            $size = is_array($stat) ? (int) ($stat['size'] ?? 0) : 0;
            $dest = trailingslashit($tmp_dir) . $name;
            if (str_ends_with($name, '/')) {
                if (!wp_mkdir_p($dest)) {
                    return self::zip_stage_error($zip, $tmp_zip, $tmp_dir, 'extract_dir_failed', 'Could not create a release directory.');
                }
                continue;
            }
            if (!wp_mkdir_p(dirname($dest))) {
                return self::zip_stage_error($zip, $tmp_zip, $tmp_dir, 'extract_dir_failed', 'Could not create a release directory.');
            }
            $in = $zip->getStream($name);
            if (!is_resource($in)) {
                return self::zip_stage_error($zip, $tmp_zip, $tmp_dir, 'zip_stream_failed', 'Could not open a release file from the ZIP.');
            }
            $out = @fopen($dest, 'wb');
            if (!is_resource($out)) {
                fclose($in);
                return self::zip_stage_error($zip, $tmp_zip, $tmp_dir, 'staged_file_write_failed', 'Could not create a staged release file.');
            }
            $written = stream_copy_to_stream($in, $out);
            fclose($in);
            fclose($out);
            if ($written === false || $written !== $size) {
                return self::zip_stage_error($zip, $tmp_zip, $tmp_dir, 'staged_file_size_mismatch', 'A staged release file did not match the ZIP byte count.');
            }
        }
        $zip->close();
        @unlink($tmp_zip);

        $staged = trailingslashit($tmp_dir) . FVDB_TARGET_SLUG;
        $main = trailingslashit($staged) . FVDB_TARGET_MAIN;
        $manifest_path = trailingslashit($staged) . 'release-manifest.json';
        if (!is_file($main) || !is_file($manifest_path)) {
            self::delete_tree($tmp_dir);
            return new WP_Error('package_shape_invalid', 'Release is missing the required plugin main file or release-manifest.json.');
        }
        $manifest = json_decode((string) file_get_contents($manifest_path), true);
        if (!is_array($manifest)) {
            self::delete_tree($tmp_dir);
            return new WP_Error('manifest_invalid', 'release-manifest.json is invalid JSON.');
        }
        if (($manifest['repository'] ?? '') !== FVDB_EXPECTED_REPOSITORY || ($manifest['branch'] ?? '') !== FVDB_EXPECTED_BRANCH) {
            self::delete_tree($tmp_dir);
            return new WP_Error('manifest_identity_mismatch', 'Release manifest repository/branch does not match the bridge allowlist.');
        }
        if (strtolower((string) ($manifest['commit'] ?? '')) !== $commit) {
            self::delete_tree($tmp_dir);
            return new WP_Error('manifest_commit_mismatch', 'Release manifest commit does not match the signed commit.');
        }

        $files = $manifest['files'] ?? null;
        if (!is_array($files) || !$files) {
            self::delete_tree($tmp_dir);
            return new WP_Error('manifest_files_missing', 'Release manifest must include file hashes.');
        }
        $expected = [];
        foreach ($files as $entry) {
            if (!is_array($entry)) {
                self::delete_tree($tmp_dir);
                return new WP_Error('manifest_entry_invalid', 'Invalid release manifest file entry.');
            }
            $rel = (string) ($entry['path'] ?? '');
            $sha = strtolower((string) ($entry['sha256'] ?? ''));
            if (!self::safe_relative_path($rel) || !preg_match('/^[a-f0-9]{64}$/', $sha) || $rel === 'release-manifest.json') {
                self::delete_tree($tmp_dir);
                return new WP_Error('manifest_entry_invalid', 'Invalid path or hash in release manifest.');
            }
            if (isset($expected[$rel])) {
                self::delete_tree($tmp_dir);
                return new WP_Error('manifest_duplicate_path', 'Release manifest contains a duplicate file path.');
            }
            $full = trailingslashit($staged) . $rel;
            if (!is_file($full) || !hash_equals($sha, hash_file('sha256', $full))) {
                self::delete_tree($tmp_dir);
                return new WP_Error('manifest_hash_mismatch', 'A release file failed SHA-256 verification: ' . $rel);
            }
            $expected[$rel] = $sha;
        }
        if (!isset($expected[FVDB_TARGET_MAIN])) {
            self::delete_tree($tmp_dir);
            return new WP_Error('main_not_hashed', 'Plugin main file is not covered by the release manifest.');
        }

        $actual = self::regular_files_relative($staged);
        if (is_wp_error($actual)) {
            self::delete_tree($tmp_dir);
            return $actual;
        }
        unset($actual['release-manifest.json']);
        $expected_paths = array_keys($expected);
        $actual_paths = array_keys($actual);
        sort($expected_paths, SORT_STRING);
        sort($actual_paths, SORT_STRING);
        if ($expected_paths !== $actual_paths) {
            self::delete_tree($tmp_dir);
            return new WP_Error('manifest_file_set_mismatch', 'Release contains missing or unexpected files relative to the manifest allowlist.');
        }

        $target = trailingslashit(WP_PLUGIN_DIR) . FVDB_TARGET_SLUG;
        if (file_exists($target) && !is_dir($target)) {
            self::delete_tree($tmp_dir);
            return new WP_Error('target_shape_invalid', 'Target plugin path exists but is not a directory.');
        }
        $backup_root = trailingslashit(WP_CONTENT_DIR) . 'fv-deploy-backups';
        if (file_exists($backup_root) && !is_dir($backup_root)) {
            self::delete_tree($tmp_dir);
            return new WP_Error('backup_shape_invalid', 'Rollback root exists but is not a directory.');
        }
        if (!wp_mkdir_p($backup_root)) {
            self::delete_tree($tmp_dir);
            return new WP_Error('backup_dir_failed', 'Could not create the rollback directory.');
        }
        $backup = trailingslashit($backup_root) . FVDB_TARGET_SLUG . '.__fv_prev';
        if (file_exists($backup) && !is_dir($backup)) {
            self::delete_tree($tmp_dir);
            return new WP_Error('backup_slot_invalid', 'Rollback slot exists but is not a directory.');
        }
        if (is_dir($backup)) {
            self::delete_tree($backup);
        }
        $had_previous = is_dir($target);
        if ($had_previous && !@rename($target, $backup)) {
            self::delete_tree($tmp_dir);
            return new WP_Error('backup_swap_failed', 'Could not move the existing Site Layer into the rollback slot.');
        }
        if (!@rename($staged, $target)) {
            if ($had_previous && is_dir($backup)) {
                @rename($backup, $target);
            }
            self::delete_tree($tmp_dir);
            return new WP_Error('target_swap_failed', 'Could not move staged release into the plugin directory; prior version restore was attempted.');
        }
        self::delete_tree($tmp_dir);

        foreach ($expected as $rel => $sha) {
            $full = trailingslashit($target) . $rel;
            if (!is_file($full) || !hash_equals($sha, hash_file('sha256', $full))) {
                self::delete_tree($target);
                if ($had_previous && is_dir($backup)) {
                    @rename($backup, $target);
                }
                return new WP_Error('post_swap_verification_failed', 'Post-swap byte verification failed; rollback was attempted.');
            }
        }
        $post_actual = self::regular_files_relative($target);
        if (is_wp_error($post_actual)) {
            self::rollback_after_swap($target, $backup, $had_previous);
            return $post_actual;
        }
        unset($post_actual['release-manifest.json']);
        $post_paths = array_keys($post_actual);
        sort($post_paths, SORT_STRING);
        if ($post_paths !== $expected_paths) {
            self::rollback_after_swap($target, $backup, $had_previous);
            return new WP_Error('post_swap_file_set_mismatch', 'Deployed file set changed after swap; rollback was attempted.');
        }
        return true;
    }

    private static function safe_zip_path(string $path): bool {
        return $path !== ''
            && !str_starts_with($path, '/')
            && !str_contains($path, '\\')
            && !str_contains($path, "\0")
            && !preg_match('~(^|/)\.\.?(/|$)~', $path);
    }

    private static function safe_relative_path(string $path): bool {
        return self::safe_zip_path($path) && !str_ends_with($path, '/');
    }

    private static function regular_files_relative(string $root) {
        $root = rtrim($root, '/\\');
        if (!is_dir($root)) {
            return new WP_Error('staged_root_missing', 'Staged plugin root is missing.');
        }
        $result = [];
        $iterator = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS),
            RecursiveIteratorIterator::LEAVES_ONLY
        );
        foreach ($iterator as $item) {
            $path = $item->getPathname();
            if ($item->isLink() || !$item->isFile()) {
                return new WP_Error('non_regular_file_rejected', 'Release contains a symlink or non-regular file.');
            }
            $rel = ltrim(str_replace('\\', '/', substr($path, strlen($root))), '/');
            if (!self::safe_relative_path($rel)) {
                return new WP_Error('staged_path_invalid', 'Release contains an invalid staged path.');
            }
            $result[$rel] = true;
        }
        return $result;
    }

    private static function rollback_after_swap(string $target, string $backup, bool $had_previous): void {
        self::delete_tree($target);
        if ($had_previous && is_dir($backup)) {
            @rename($backup, $target);
        }
    }

    private static function zip_error(ZipArchive $zip, string $tmp_zip, string $code, string $message): WP_Error {
        $zip->close();
        @unlink($tmp_zip);
        return new WP_Error($code, $message);
    }

    private static function zip_stage_error(ZipArchive $zip, string $tmp_zip, string $tmp_dir, string $code, string $message): WP_Error {
        $zip->close();
        @unlink($tmp_zip);
        self::delete_tree($tmp_dir);
        return new WP_Error($code, $message);
    }

    private static function delete_tree(string $path): void {
        if (!file_exists($path) && !is_link($path)) {
            return;
        }
        if (is_file($path) || is_link($path)) {
            @unlink($path);
            return;
        }
        $items = scandir($path);
        if (!is_array($items)) {
            return;
        }
        foreach ($items as $item) {
            if ($item === '.' || $item === '..') {
                continue;
            }
            self::delete_tree(trailingslashit($path) . $item);
        }
        @rmdir($path);
    }
}

<?php

declare(strict_types=1);

require_once __DIR__ . '/helpers.php';

try {
    $config = app_load_config();
    app_ensure_storage_folders($config);

    $action = $_GET['action'] ?? '';

    switch ($action) {
        case 'save_titles':
            if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
                app_json_response(['ok' => false, 'message' => 'Method tidak diizinkan.'], 405);
            }

            $body = app_read_json_body();
            $titles = $body['titles'] ?? [];
            if (!is_array($titles)) {
                app_json_response(['ok' => false, 'message' => 'titles harus array.'], 422);
            }

            $cleanTitles = [];
            foreach ($titles as $title) {
                $trimmed = trim((string)$title);
                if ($trimmed !== '') {
                    $cleanTitles[] = $trimmed;
                }
            }

            if (count($cleanTitles) !== 10) {
                app_json_response(['ok' => false, 'message' => 'Harus tepat 10 judul non-kosong.'], 422);
            }

            $payload = [
                'updated_at' => app_now_iso(),
                'titles' => array_values($cleanTitles),
                'pairs' => app_build_pairs(array_values($cleanTitles)),
            ];

            file_put_contents(ROOT_DIR . '/storage/titles/latest_titles.json', json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
            app_json_response(['ok' => true, 'message' => 'Judul berhasil disimpan.', 'data' => $payload]);
            break;

        case 'start_generate':
            if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
                app_json_response(['ok' => false, 'message' => 'Method tidak diizinkan.'], 405);
            }

            $titlesPath = ROOT_DIR . '/storage/titles/latest_titles.json';
            if (!file_exists($titlesPath)) {
                app_json_response(['ok' => false, 'message' => 'Belum ada judul tersimpan.'], 422);
            }

            $runId = gmdate('Ymd_His') . '_' . substr(bin2hex(random_bytes(6)), 0, 6);
            $command = sprintf(
                'python %s --config %s --titles %s --run-id %s 2>&1',
                escapeshellarg(ROOT_DIR . '/scripts/run_automation.py'),
                escapeshellarg(ROOT_DIR . '/config/config.json'),
                escapeshellarg($titlesPath),
                escapeshellarg($runId)
            );

            $output = [];
            $exitCode = 0;
            exec($command, $output, $exitCode);

            $runMetaPath = ROOT_DIR . '/storage/runs/' . $runId . '.json';
            $runMeta = null;
            if (file_exists($runMetaPath)) {
                $raw = file_get_contents($runMetaPath);
                $runMeta = $raw ? json_decode($raw, true) : null;
            }

            app_json_response([
                'ok' => $exitCode === 0,
                'exit_code' => $exitCode,
                'run_id' => $runId,
                'console_output' => $output,
                'run_metadata' => $runMeta,
                'message' => $exitCode === 0 ? 'Generate selesai.' : 'Generate selesai dengan error. Cek log.',
            ], $exitCode === 0 ? 200 : 500);
            break;

        case 'status':
            app_json_response([
                'ok' => true,
                'latest_run' => app_latest_run(),
                'history' => app_list_runs(20),
            ]);
            break;

        case 'view_result':
            $latest = app_latest_run();
            if ($latest === null) {
                app_json_response(['ok' => false, 'message' => 'Belum ada run.'], 404);
            }

            $mergedTxt = $latest['paths']['merged_txt'] ?? null;
            if ($mergedTxt === null || !file_exists(ROOT_DIR . '/' . $mergedTxt)) {
                app_json_response(['ok' => false, 'message' => 'File hasil tidak ditemukan.'], 404);
            }

            $content = file_get_contents(ROOT_DIR . '/' . $mergedTxt);
            app_json_response(['ok' => true, 'content' => $content, 'run' => $latest]);
            break;

        case 'download_output':
            $latest = app_latest_run();
            if ($latest === null) {
                http_response_code(404);
                echo 'Belum ada run.';
                exit;
            }

            $format = $_GET['format'] ?? 'txt';
            $key = $format === 'html' ? 'merged_html' : 'merged_txt';
            $path = $latest['paths'][$key] ?? null;
            if ($path === null || !file_exists(ROOT_DIR . '/' . $path)) {
                http_response_code(404);
                echo 'Output tidak ditemukan.';
                exit;
            }

            $fullPath = ROOT_DIR . '/' . $path;
            header('Content-Description: File Transfer');
            header('Content-Type: ' . ($format === 'html' ? 'text/html' : 'text/plain'));
            header('Content-Disposition: attachment; filename="' . basename($fullPath) . '"');
            header('Content-Length: ' . filesize($fullPath));
            readfile($fullPath);
            exit;

        default:
            app_json_response(['ok' => false, 'message' => 'Action tidak dikenal.'], 404);
    }
} catch (Throwable $e) {
    app_json_response([
        'ok' => false,
        'message' => 'Terjadi kesalahan di server.',
        'error' => $e->getMessage(),
    ], 500);
}

<?php

declare(strict_types=1);

const ROOT_DIR = __DIR__ . '/..';

function app_config_path(): string
{
    return ROOT_DIR . '/config/config.json';
}

function app_load_config(): array
{
    $examplePath = ROOT_DIR . '/config/config.example.json';
    $configPath = app_config_path();

    if (!file_exists($configPath)) {
        if (!file_exists($examplePath)) {
            throw new RuntimeException('config/config.example.json tidak ditemukan.');
        }
        copy($examplePath, $configPath);
    }

    $raw = file_get_contents($configPath);
    if ($raw === false) {
        throw new RuntimeException('Gagal membaca file config.');
    }

    $config = json_decode($raw, true);
    if (!is_array($config)) {
        throw new RuntimeException('Format config JSON tidak valid.');
    }

    return $config;
}

function app_json_response(array $payload, int $statusCode = 200): void
{
    http_response_code($statusCode);
    header('Content-Type: application/json');
    echo json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    exit;
}

function app_read_json_body(): array
{
    $raw = file_get_contents('php://input');
    if ($raw === false || $raw === '') {
        return [];
    }

    $decoded = json_decode($raw, true);
    if (!is_array($decoded)) {
        throw new InvalidArgumentException('Body request JSON tidak valid.');
    }

    return $decoded;
}

function app_ensure_storage_folders(array $config): void
{
    $folders = [
        ROOT_DIR . '/storage/titles',
        ROOT_DIR . '/storage/raw',
        ROOT_DIR . '/storage/parsed',
        ROOT_DIR . '/storage/output',
        ROOT_DIR . '/storage/logs',
        ROOT_DIR . '/storage/runs',
    ];

    foreach ($folders as $folder) {
        if (!is_dir($folder) && !mkdir($folder, 0777, true) && !is_dir($folder)) {
            throw new RuntimeException('Gagal membuat folder: ' . $folder);
        }
    }
}

function app_now_iso(): string
{
    return gmdate('Y-m-d\TH:i:s\Z');
}

function app_build_pairs(array $titles): array
{
    $pairs = [];
    for ($i = 0; $i < count($titles); $i += 2) {
        $pairs[] = [$titles[$i], $titles[$i + 1]];
    }

    return $pairs;
}

function app_list_runs(int $limit = 20): array
{
    $files = glob(ROOT_DIR . '/storage/runs/*.json');
    if ($files === false) {
        return [];
    }

    rsort($files);
    $runs = [];
    foreach (array_slice($files, 0, $limit) as $file) {
        $raw = file_get_contents($file);
        if ($raw === false) {
            continue;
        }
        $decoded = json_decode($raw, true);
        if (!is_array($decoded)) {
            continue;
        }
        $runs[] = $decoded;
    }

    return $runs;
}

function app_latest_run(): ?array
{
    $runs = app_list_runs(1);
    return $runs[0] ?? null;
}

function app_save_run_metadata(array $data): void
{
    if (empty($data['run_id'])) {
        throw new InvalidArgumentException('run_id wajib ada saat save metadata.');
    }

    $path = ROOT_DIR . '/storage/runs/' . $data['run_id'] . '.json';
    file_put_contents($path, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

<?php

declare(strict_types=1);
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article Automation Admin</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="container">
    <h1>Article Automation</h1>
    <p class="subtitle">Workflow lokal GitHub + Laragon + Chrome profile login ChatGPT.</p>

    <section class="card">
        <h2>Input 10 Judul</h2>
        <div id="titles-grid" class="titles-grid"></div>
        <div class="actions">
            <button id="saveBtn">Simpan Judul</button>
            <button id="generateBtn" class="primary">Mulai Generate</button>
            <button id="viewResultBtn">Lihat Hasil</button>
            <button id="downloadTxtBtn">Download Output (.txt)</button>
            <button id="downloadHtmlBtn">Download Output (.html)</button>
        </div>
    </section>

    <section class="card">
        <h2>Status Proses</h2>
        <pre id="statusBox">Belum ada proses.</pre>
    </section>

    <section class="card">
        <h2>Riwayat Run (20 terakhir)</h2>
        <div id="historyBox">Belum ada data.</div>
    </section>

    <section class="card">
        <h2>Hasil Gabungan Terakhir</h2>
        <pre id="resultBox">Belum ada output.</pre>
    </section>
</div>
<script src="assets/app.js"></script>
</body>
</html>

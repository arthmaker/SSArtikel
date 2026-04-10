# article-automation

Project lokal production-ready untuk otomatisasi generate 10 artikel via 5 tab ChatGPT menggunakan **PHP native (Laragon) + Python Playwright + Chrome profile lokal**.

## Tujuan
Aplikasi menerima tepat 10 judul, membagi menjadi 5 pasangan, membuka 5 tab ChatGPT (menggunakan Chrome profile yang sudah login), mengirim prompt per tab, mengambil 2 code block HTML per tab, lalu menggabungkan 10 artikel ke output final dengan marker khusus.

## Arsitektur
- **Frontend admin**: `public/index.php` + `public/assets/*`
- **PHP API handler**: `app/api.php`
- **Python automation engine**: `scripts/run_automation.py`
- **Modul Python**:
  - `scripts/utils/config_loader.py`
  - `scripts/utils/prompt_builder.py`
  - `scripts/utils/playwright_runner.py`
  - `scripts/utils/extractor.py`
  - `scripts/utils/merger.py`
  - `scripts/utils/logger.py`
- **Storage**: file JSON/TXT/HTML tanpa database.

## Struktur Folder

```txt
article-automation/
├─ public/
├─ app/
├─ scripts/
├─ storage/
│  ├─ titles/
│  ├─ raw/
│  ├─ parsed/
│  ├─ output/
│  ├─ logs/
│  └─ runs/
├─ templates/
├─ config/
├─ bootstrap/
├─ requirements.txt
└─ README.md
```

## Prasyarat
1. Windows + Laragon terpasang.
2. Python 3.10+ tersedia di PATH.
3. Google Chrome terpasang dan akun ChatGPT sudah login di profile target.
4. Repo disimpan di folder Laragon (contoh: `C:\laragon\www\article-automation`).

## Langkah Instalasi (Windows + Laragon)

1. **Clone dari GitHub**
   ```bash
   git clone <URL_REPO_GITHUB> article-automation
   cd article-automation
   ```

2. **Setup Python + Playwright**
   Opsi cepat via script:
   ```bat
   bootstrap\install.bat
   ```

   Opsi manual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

3. **Setup config**
   - Copy `config/config.example.json` menjadi `config/config.json` (default sudah dibuat).
   - Edit nilai:
     - `chrome_executable_path`
     - `chrome_user_data_dir`
     - `chrome_profile`
     - timeout bila perlu.

4. **Jalankan lewat Laragon**
   - Letakkan project di `C:\laragon\www\article-automation`
   - Start Laragon
   - Buka URL: `http://article-automation.test/public/` (atau sesuai host Laragon)

## Konfigurasi Chrome Profile
Gunakan path profile yang benar agar sesi login ChatGPT terbaca:
- User data dir umum:
  `C:/Users/<USER>/AppData/Local/Google/Chrome/User Data`
- Profile:
  - `Default`
  - atau `Profile 1`, `Profile 2`, dst.

Jika ChatGPT minta login ulang, berarti profile/path tidak sesuai atau dibuka oleh instance Chrome lain.

## Alur End-to-End
1. Buka halaman admin.
2. Isi 10 judul.
3. Klik **Simpan Judul**.
4. Klik **Mulai Generate**.
5. Sistem akan:
   - baca `templates/base_prompt.txt`
   - buat 5 prompt (tiap prompt = 2 judul + base prompt)
   - buka 5 tab ChatGPT
   - kirim prompt
   - tunggu response selesai
   - ekstrak 2 code block HTML per tab
   - simpan raw + parsed + merge output
6. Klik **Lihat Hasil** untuk preview.
7. Klik **Download Output (.txt/.html)**.

## Format Output Final
Merger mempertahankan marker wajib berikut:
- pembuka garis underscore panjang
- repetisi blok `-###-`, isi artikel, `-$$$-`
- penutup garis underscore panjang

Output disimpan di:
- `storage/output/<run_id>_merged.txt`
- `storage/output/<run_id>_merged.html`

## Logging, Metadata, Recovery
- Log detail per run: `storage/logs/<run_id>.log`
- Metadata run: `storage/runs/<run_id>.json`
- Raw per tab: `storage/raw/<run_id>_tabX.txt`
- Parsed per artikel: `storage/parsed/<run_id>_tabX_articleY.html`
- Retry sederhana tab gagal: jalankan Python dengan `--retry-failed-tabs`.

## API Endpoint Lokal (dipakai frontend)
- `POST app/api.php?action=save_titles`
- `POST app/api.php?action=start_generate`
- `GET app/api.php?action=status`
- `GET app/api.php?action=view_result`
- `GET app/api.php?action=download_output&format=txt|html`

## Kustomisasi Prompt
Edit file:
- `templates/base_prompt.txt`

Pastikan instruksi meminta tepat 2 code block HTML agar extractor konsisten.

## Debugging Umum
1. **Chrome/profile/login gagal**
   - Pastikan `chrome_user_data_dir` benar.
   - Tutup semua Chrome lalu coba lagi.
   - Jalankan script manual untuk cek error:
     ```bash
     .venv\Scripts\python scripts\run_automation.py --config config\config.json --titles storage\titles\latest_titles.json --run-id test_run
     ```
2. **Selector berubah**
   - Update fallback selector di `scripts/utils/playwright_runner.py`.
3. **Tidak dapat 2 code block**
   - Perketat prompt di `templates/base_prompt.txt`.

## Screenshot Placeholder
Simpan screenshot UI pada path berikut (opsional):
- `docs/screenshots/admin-dashboard.png`

## TODO
- Mode async queue supaya run non-blocking dari UI.
- Penambahan endpoint retry tab tertentu dari admin UI.
- Health check terpisah untuk validasi Chrome profile sebelum run.
- Export ZIP untuk semua artefak run.

## Catatan Penting
- Tidak menggunakan database.
- Tidak menggunakan GitHub Actions untuk browser automation.
- Seluruh eksekusi browser automation fokus local execution.

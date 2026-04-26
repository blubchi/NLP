# FitScore — AI-Powered Career Match

FitScore menganalisis kecocokan CV kamu dengan job description menggunakan model NER (Named Entity Recognition) untuk ekstraksi skill dan S-BERT untuk mengukur kemiripan semantik pengalaman dan pendidikan.

---

## Arsitektur Sistem

```
Browser (mainfinal.html)
        │
        │  POST /analyze
        ▼
   proxy.js  (Node.js · port 5500)
        │
        │  forward ke Hugging Face / model lokal
        ▼
  model_server.py  (Python · port 7860)
        │
        ▼
   handler.py  ←  NER model lokal + S-BERT
```

---

## Prasyarat

Pastikan software berikut sudah terinstall di komputer kamu:

| Software | Versi minimal | Cek dengan |
|---|---|---|
| Python | 3.9+ | `python --version` |
| Node.js | 16+ | `node --version` |
| npm | 8+ | `npm --version` |
| pip | terbaru | `pip --version` |

---

## Struktur Folder

```
NER-AI-resume/
├── handler.py              ← logika AI (NER + S-BERT)
├── model_server.py         ← server Python yang expose handler
├── tokenizer.json          ← tokenizer NER model
├── tokenizer_config.json   ← konfigurasi tokenizer
├── config.json             ← konfigurasi NER model
├── model.safetensors       ← bobot NER model
│
src/
├── mainfinal.html          ← frontend utama
├── proxy.js                ← proxy Node.js (CORS bridge)
```

---

## Instalasi

### Langkah 1 — Install dependensi Python

Buka terminal di folder `NER-AI-resume/` lalu jalankan:

```bash
pip install torch transformers sentence-transformers pandas kaggle
```

> **Catatan:** Instalasi `torch` dan `sentence-transformers` bisa memakan waktu beberapa menit tergantung koneksi internet.

### Langkah 2 — Install dependensi Node.js

Buka terminal di folder `src/` lalu jalankan:

```bash
npm install
```

Jika belum ada `package.json`, install manual:

```bash
npm install express cors axios
```

### Langkah 3 — Setup Kaggle (untuk rekomendasi kursus)

Dataset kursus diambil dari Kaggle secara otomatis saat server pertama kali dijalankan.

1. Buka [https://www.kaggle.com/settings](https://www.kaggle.com/settings)
2. Scroll ke bagian **API** → klik **Create New Token**
3. File `kaggle.json` akan terdownload otomatis
4. Pindahkan file tersebut ke:
   - **Windows:** `C:\Users\NamaKamu\.kaggle\kaggle.json`
   - **Mac/Linux:** `~/.kaggle/kaggle.json`
5. Untuk Mac/Linux, set permission file:
   ```bash
   chmod 600 ~/.kaggle/kaggle.json
   ```

> **Jika tidak ingin setup Kaggle:** Aplikasi tetap bisa berjalan. Rekomendasi kursus akan menggunakan fallback link Coursera otomatis berdasarkan nama skill.

---

## Cara Menjalankan

> ⚠️ Urutan ini wajib diikuti. Jangan sampai terbalik.

Terminal 1 — Jalankan Model Server (Python)

```bash
python model_server.py
```

Tunggu sampai muncul output seperti ini:

```
[INFO] Loading NER model...
[INFO] NER model ready.
[INFO] Loading S-BERT model...
[INFO] S-BERT ready.
Running on http://0.0.0.0:7860
```

> Jangan tutup terminal ini selama aplikasi digunakan.

### Terminal 2 — Jalankan Proxy (Node.js)

Buka terminal baru, lalu:

```bash
node proxy.js
```

Tunggu sampai muncul:

```
Proxy running on http://localhost:5500
```

> Jangan tutup terminal ini selama aplikasi digunakan.

### Terminal 3 — Jalankan Live Server (Frontend)

Buka terminal baru. Jika menggunakan **VS Code Live Server extension**:

1. Buka file `src/mainfinal.html` di VS Code
2. Klik kanan → **Open with Live Server**
3. Browser akan terbuka otomatis di `http://127.0.0.1:5500/mainfinal.html`

Atau jika menggunakan `live-server` via npm:

```bash
npm install -g live-server
cd src
live-server --port=8080
```

Kemudian buka `http://localhost:8080/mainfinal.html` di browser.

---

## Cara Menggunakan Aplikasi

1. **Daftar / Login** — buat akun atau login dengan email dan password apapun (data disimpan lokal di sesi browser)

2. **Isi Profil** — lengkapi data diri:
   - Nama, bidang pekerjaan, ringkasan
   - Pengalaman kerja (posisi, perusahaan, deskripsi)
   - Skill teknis, tools, soft skills
   - Pendidikan terakhir

3. **Halaman Analisis** — paste job description dan requirements dari LinkedIn, Glints, JobStreet, atau platform lainnya ke kolom yang tersedia

4. **Klik Analisis** — tunggu beberapa detik sampai hasil muncul

5. **Baca Hasil:**
   - **Match Score** — skor kecocokan 0–100
   - **Breakdown** — detail Skill Similarity, Experience Match, Education Match
   - **Skill Gap Analysis** — skill mana yang sudah dimiliki (hijau) dan belum (merah)
   - **Rekomendasi Kursus** — klik card kursus untuk langsung diarahkan ke platform pembelajaran

---

## Troubleshooting

**Model server tidak bisa start / error saat load model**
```
Pastikan kamu berada di folder NER-AI-resume/ yang berisi file:
model.safetensors, config.json, tokenizer.json, tokenizer_config.json
```

**Error saat analisis: "Gagal menghubungi model AI"**
```
1. Pastikan model_server.py sudah jalan (Terminal 1)
2. Pastikan proxy.js sudah jalan (Terminal 2)
3. Cek port — proxy harus di port 5500, model server di port 7860
```

**Error 503 dari model**
```
Model sedang cold-start. Tunggu 30–60 detik lalu coba lagi.
```

**Rekomendasi kursus tidak muncul / kosong**
```
Dataset Kaggle gagal diload. Rekomendasi fallback ke Coursera search
otomatis tetap aktif — card kursus tetap bisa diklik.
```

**Port 5500 sudah dipakai (conflict dengan Live Server)**
```
Ubah port proxy di proxy.js:
  const PORT = 5501;  // ganti ke port lain

Lalu update PROXY_URL di mainfinal.html:
  const PROXY_URL = "http://localhost:5501/analyze";
```

---

## Catatan Teknis

- Model NER dijalankan **lokal** — tidak ada data profil yang dikirim ke server eksternal
- S-BERT (`all-MiniLM-L6-v2`) didownload otomatis dari Hugging Face saat pertama kali dijalankan (~90 MB)
- Dataset kursus dari Kaggle didownload sekali dan di-cache di folder `.cache_courses/`
- Semua pemrosesan AI terjadi di `handler.py` — frontend hanya menampilkan hasil
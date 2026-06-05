# User Guide: Information Retrieval System with Word2Vec Query Expansion

## Daftar Isi

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Instalasi](#instalasi)
4. [Menjalankan Aplikasi](#menjalankan-aplikasi)
5. [Panduan Penggunaan](#panduan-penggunaan)
   - [Panel Parameter](#51-panel-parameter)
   - [Melakukan Pencarian](#52-melakukan-pencarian)
   - [Tab Hasil (Results)](#53-tab-hasil-results)
   - [Tab Ekspansi (Expansion)](#54-tab-ekspansi-expansion)
   - [Tab Laporan MAP (MAP Report)](#55-tab-laporan-map-map-report)
6. [Troubleshooting](#troubleshooting)

---

## Overview

Aplikasi ini adalah **Information Retrieval System** berbasis web yang menggunakan **Word2Vec Query Expansion** untuk meningkatkan relevansi pencarian dokumen.

**Cara kerja:**

1. Pengguna memasukkan query bahasa Inggris
2. Sistem mencari dokumen relevan dari 1.460 dokumen ilmiah (dataset CISI) dengan parameter (penggunaan stemming dan stopword) dan weighting yang diinginkan
3. Sistem juga mencari kata-kata yang mirip/berhubungan secara semantik terhadap query menggunakan model **Google News Word2Vec**
4. Kata-kata mirip/berhubungan tersebut ditambahkan ke query melalui query expansion
5. Hasil pencarian original vs expanded ditampilkan berdampingan
6. Sistem juga dapat menampilkan **MAP (Mean Average Precision)** dengan dan tanpa query expansion dengan parameter pencarian yang dipilih user, untuk pencarian 112 query pada `data/query.text` dari koleksi dokumen di `data/cisi.all`

---

## Requirements

| Komponen | Minimum |
|---|---|
| Python | **3.13+** |
| Node.js | **18+** (untuk frontend) |

**Package manager Python:** `uv` (https://docs.astral.sh/uv/). Pastikan `uv` sudah terinstal:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# lalu restart terminal
```

---

## Instalasi

### 1. Clone Repository & Masuk Direktori

```bash
git clone <repo-url>
cd InformationRetrievalSystem-Word2Vec
```

### 2. Install Dependensi Python

```bash
uv sync
```

### 3. Download Data NLTK (WAJIB)

```bash
uv run python -c "import nltk; nltk.download('stopwords')"
```

### 4. Install Dependensi Frontend

```bash
cd frontend
npm install
cd ..
```

Catatan: Model Word2Vec `word2vec-google-news-300` (~1.6 GB) akan otomatis diunduh saat backend pertama kali dijalankan. Disimpan di `~/gensim-data/`.

---

## Menjalankan Aplikasi

Buka **2 terminal**:

### Terminal 1: Backend API Server

```bash
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Saat pertama kali dijalankan:**
- Akan mengunduh model Word2Vec (~1.6 GB) jika belum ada
- Akan menghitung MAP benchmark untuk 28 kombinasi parameter (2 stemming x 2 stopwords x 7 weighting schemes) — bisa memakan waktu **beberapa menit**
- Hasil perhitungan disimpan di cache (`output/`) sehingga run berikutnya jauh lebih cepat

**Output yang diharapkan di terminal:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
Starting MAP calculation...
Calculating MAP for 28 combinations...
MAP calculation complete
```

### Terminal 2: Frontend Dev Server

```bash
cd frontend
npm run dev
```

Buka browser di **http://localhost:5173**

### Opsional: API Documentation

Setelah backend berjalan, buka **http://localhost:8000/docs** untuk dokumentasi interaktif Swagger.

---

## Panduan Penggunaan

Tampilan aplikasi terdiri dari 3 area utama:
- **Panel Parameter** (panel kiri) → konfigurasi pencarian
- **Search Bar** (atas tengah) → input query
- **Area Hasil** (kanan/tengah) → 3 tab hasil

### 5.1 Panel Parameter

Terletak di sisi kiri layar. Berikut setiap kontrol:

| Parameter | Tipe | Default | Deskripsi |
|---|---|---|---|
| **Stemming** | Toggle | ON | Aktifkan **Porter Stemmer**. Mengubah kata ke bentuk dasar (misal: `running` → `run`, `documents` → `document`). Meningkatkan recall. |
| **Stopwords** | Toggle | ON | Buang kata-kata umum bahasa Inggris (misal: `the`, `is`, `a`, `of`). Mengurangi noise dan mempercepat pencarian. |
| **Weighting Scheme** | Dropdown | `tfidf_cos` | Pilih skema pembobotan TF-IDF. Lihat [Skema Pembobotan](#6-skema-pembobotan-tf-idf) untuk detail 7 pilihan. |
| **Top-N** | Number (1-50) | 5 | Jumlah dokumen teratas yang ditampilkan dalam hasil. Juga mengontrol jumlah expansion term yang ditampilkan (kecuali Expand All aktif). |
| **Expand All** | Checkbox | OFF | Jika ON, **semua** kandidat expansion term digunakan. |

### 5.2 Melakukan Pencarian

1. Atur parameter di panel kiri sesuai kebutuhan (atau biarkan default)
2. Ketik query dalam bahasa Inggris di search bar, contoh:
   - `information retrieval systems`
   - `machine learning for te classification`
   - `network optimization`
3. Tekan **Enter** atau klik tombol **Search**
4. Hasil akan muncul di area kanan dalam 3 tab

### 5.3 Tab Hasil (Results)

Menampilkan dua kolom berdampingan:

| Kolom | Isi |
|---|---|
| **Results (Original)** | Dokumen yang ditemukan menggunakan query asli (sebelum ekspansi) |
| **Results (Expanded)** | Dokumen yang ditemukan setelah query diekspansi dengan kata-kata mirip semantik dari Word2Vec |

Setiap kartu dokumen menampilkan:
- **Peringkat (rank)** — badge bernomor, makin kecil makin relevan
- **DOC ID** — identitas dokumen (misal `DOC042`)
- **Judul** — judul dokumen dari dataset CISI
- **Skor similarity** — semakin tinggi semakin relevan

**Highlight:** Dokumen yang peringkatnya membaik di hasil expanded ditandai dengan border cyan. Ini menunjukkan bahwa query expansion berhasil membawa dokumen relevan ke posisi lebih atas.

### 5.4 Tab Ekspansi (Expansion)

Menampilkan detail kata-kata yang ditambahkan oleh Word2Vec:

- **Original Query Terms** — kata-kata dari query asli (setelah preprocessing) ditampilkan sebagai pill
- **Expanded Terms** — kata-kata tambahan hasil ekspansi semantik, ditandai dengan prefix `+` dan warna cyan
- **Tabel Expansion Terms** — daftar lengkap semua expansion term dengan:
  - Nama term
  - Skor similaritas (cosine similarity dengan kata asli dalam ruang vektor Word2Vec)
  - Bar visual (indikator proporsional skor)

### 5.5 Tab Laporan MAP (MAP Report)

Menampilkan metrik evaluasi performa untuk eksperimen pencarian query `data/query.text` pada dokumen `data/cisi.all` dengan parameter yang diatur user di panel bagian kiri:

**Bagian atas — Ringkasan:**
- **MAP Original** — Mean Average Precision untuk query asli
- **MAP Expanded** — Mean Average Precision setelah ekspansi
- **Δ (Delta)** — selisih MAP (expanded - original). Positif = ekspansi meningkatkan performa
- **% Change** — persentase perubahan

**Bagian bawah — Tabel Per-Query:**
- Menampilkan Average Precision (AP) untuk setiap query evaluasi
- Query yang AP-nya meningkat setelah ekspansi menunjukkan bahwa Word2Vec membantu pencarian tersebut

**Tombol:**
- **Recalculate (Current)** — hitung ulang MAP hanya untuk kombinasi parameter yang sedang aktif
- **Recalculate (All 28)** — hitung ulang MAP untuk semua 28 kombinasi parameter. Memakan waktu.

---

## Troubleshooting

### Backend gagal start: `LookupError: Resource stopwords not found`

Jalankan ulang download NLTK:
```bash
uv run python -c "import nltk; nltk.download('stopwords')"
```

### Backend lama saat startup pertama

Expected. Startup pertama mengunduh model Word2Vec (~1.6 GB) dan menghitung MAP untuk 28 kombinasi parameter. Tunggu hingga muncul log `MAP calculation complete`. Run berikutnya akan jauh lebih cepat karena menggunakan cache di `output/`.

### Frontend kosong / tidak terhubung ke backend

1. Pastikan backend berjalan di `http://localhost:8000`
2. Pastikan frontend berjalan di `http://localhost:5173`
3. Cek CORS: frontend hanya bisa konek ke `localhost:8000` (sudah dikonfigurasi)
4. Jika backend berjalan di host/port lain, ubah `frontend/src/api/search.ts`

### Hasil pencarian selalu sama antara Original dan Expanded

Word2Vec mungkin tidak menemukan kata yang mirip untuk query tersebut. Coba:
- Gunakan query yang terdiri dari kata-kata umum bahasa Inggris
- Matikan Stopwords untuk melihat apakah stopwords mempengaruhi term yang tersedia
- Cek tab Expansion. Jika kosong, berarti model tidak menemukan similar terms

### Ingin me-reset cache dan mulai dari awal

```bash
rm -rf output/
# lalu restart backend
```

### Model Word2Vec gagal diunduh / koneksi lambat

Model `word2vec-google-news-300` bisa diunduh manual dari:
https://github.com/mmihaltz/word2vec-GoogleNews-vectors

Lalu taruh di `~/gensim-data/word2vec-google-news-300/`

### Ingin menjalankan evaluasi saja (tanpa frontend)

```bash
uv run python -m src.evaluator
# Output: map_report.txt
```

### Port 8000 atau 5173 sudah digunakan

```bash
# Cari proses yang menggunakan port
lsof -i :8000
lsof -i :5173

# Kill proses tersebut, atau gunakan port lain:
uv run uvicorn api.main:app --port 8001
# lalu ubah frontend/src/api/search.ts
```

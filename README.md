# Information Retrieval System dengan Word2Vec Query Expansion

## Judul Tugas
Tugas Besar IF4042 Sistem Temu Balik Informasi
Semester Genap Tahun Akademik 2025/2026

## Anggota Kelompok
- 13523017 - Orvin Andika Ikhsan Abhista
- 13523027 - Fajar Kurniawan
- 13523056 - Salman Hanif
- 13523100 - Aryo Wisanggeni
- 13523072 - Sabilul Huda

## Gambaran Umum Perangkat Lunak
Aplikasi ini merupakan sistem Information Retrieval (IR) yang melakukan pencarian dokumen pada koleksi CISI menggunakan pembobotan TF-IDF berbasis cosine similarity dan menyediakan fitur query expansion berbasis Word2Vec. Pengguna dapat mengatur parameter pencarian seperti stemming, stopword removal, skema pembobotan, dan top-N hasil. Sistem menampilkan hasil retrieval untuk query original dan query yang sudah diekspansi secara berdampingan, serta menyediakan evaluasi performa menggunakan Mean Average Precision (MAP) dengan perincian per query.

Komponen utama sistem meliputi:
- Backend REST API berbasis FastAPI untuk preprocessing, retrieval, query expansion, dan caching indeks serta MAP.
- Frontend web interaktif berbasis React, Vite, TypeScript, dan TailwindCSS.
- Pipeline evaluasi yang menghitung MAP untuk 28 kombinasi parameter (2 opsi stemming x 2 opsi stopword x 7 skema pembobotan).

Dataset yang digunakan adalah CISI dengan 1460 dokumen dan 112 query uji, dengan 76 query memiliki relevance judgments.

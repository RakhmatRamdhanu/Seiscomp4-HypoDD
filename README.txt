Nama Tool   : SeisComP4 to HypoDD
Author      : Rakhmat
Update      : Januari 2026
Bahasa      : Python 3
Lisensi     : Internal BMKG Stageof

[ 1. LATAR BELAKANG & FUNGSI ]
Perangkat lunak ini dikembangkan untuk menjembatani inkompatibilitas data antara 
sistem SeisComP 4 (Format Keluaran LOCSAT) dengan software relokasi HypoDD.

Sistem SeisComP 4 menghasilkan log dengan format yang bervariasi (M, MLv, Mw) 
dan tercampur antara data otomatis (Type A) dengan data manual (Type M).
Script ini berfungsi untuk:
1. Membersihkan data: Membuang event otomatis (Type A) yang merupakan noise.
2. Menstandarisasi format: Mengubah log teks menjadi format .pha baku.
3. Adaptasi Format: Membaca berbagai label magnitudo (MLv, Mw, M, dll) secara cerdas.

[ 2. FITUR UTAMA (KEY FEATURES) ]
1. Smart Filtering (Quality Control):
   Secara otomatis mendeteksi status "Type A" (Automatic) dan "Type M" (Manual).
   Hanya data Type M yang akan diproses ke output.

2. Adaptive Parsing Engine:
   Mampu membaca baris magnitudo yang tidak standar. Tidak peduli apakah labelnya
   "M=", "MLv=", "Mw=", atau "mb=", script akan otomatis mengenali pola data
   berdasarkan posisi karakter "=" dan format tanggal.

3. Automatic Phase Sorting (Physics-Based):
   Karena data mentah tidak memiliki label P/S, script menggunakan logika fisika:
   - Gelombang pertama (Arrival Tercepat) -> Label P.
   - Gelombang kedua (Arrival Berikutnya) -> Label S.
   
4. Coordinate & Time Normalization:
   - Konversi arah S (South) dan W (West) menjadi koordinat negatif (-).
   - Konversi tahun 2 digit (misal '26') menjadi 4 digit ('2026').

[ 3. CARA PENGGUNAAN ]
A. MODE INTERAKTIF (Paling Mudah)
   1. Pastikan script dan file data (misal: "data_gempa.txt") ada di satu folder.
   2. Klik 2x pada script (atau jalankan via terminal: python script.py).
   3. Script akan bertanya: "Ketik nama file input".
   4. Ketik nama file, lalu Enter.
   5. Selesai.

B. MODE OTOMASI / CLI (Untuk Advanced User)
   Jika ingin memproses banyak file sekaligus lewat terminal:
   Format: python script.py [file1.txt] [file2.txt] ...
   Contoh: python SeisComP4_to_HypoDD.py gempa_aceh.txt gempa_sumut.txt

[ 4. LOGIKA TEKNIS (UNTUK LAPORAN/AUDIT) ]
- Input Reading : Menggunakan buffer "Line-by-Line" (hemat memori).
- Parsing       : Menggunakan algoritma pencarian token dinamis (bukan indeks kaku),
                  sehingga tahan terhadap perubahan spasi atau label magnitudo.
- Weighting     : Nilai bobot (weight) fase di-set default ke "1.000" (Full Weight)
                  untuk memastikan HypoDD memproses seluruh data stasiun terpilih.

[ 5. TROUBLESHOOTING ]
Q: Kenapa jumlah event di output lebih sedikit dari input?
A: Cek laporan akhir. Kemungkinan event yang hilang adalah "Type A" (Otomatis) 
   yang sengaja dibuang oleh sistem filter.

Q: Kenapa muncul error "File tidak ditemukan"?
A: Pastikan nama file yang diketik sama persis (termasuk huruf besar/kecil dan 
   akhiran .txt).

[ 6. RIWAYAT PEMBARUAN (CHANGELOG) ]
- v1.0 : Rilis awal. Konversi dasar LOCSAT ke HypoDD.
- v2.0 : Penambahan fitur Filter "Type M" vs "Type A".
- v3.0 : Perbaikan bug pada konversi koordinat S/W.
- v4.0 : (Versi Saat Ini) Peningkatan algoritma parsing untuk mendukung
         variabel magnitudo dinamis (MLv, Mw, mb) yang sebelumnya menyebabkan
         error pembacaan waktu.
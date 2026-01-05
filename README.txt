Author      : Rakhmat Ramdhanu
Update      : Januari 2026
Bahasa      : Python 3
Input       : Log Output SeisComP 4 (Format LOCSAT Solution)
Output      : File Fase HypoDD (.pha)

[ 1. DESKRIPSI SINGKAT ]
Script ini berfungsi untuk:
1. Mengonversi format log SeisComP 4 menjadi format standar HypoDD.
2. MELAKUKAN FILTERING OTOMATIS: Hanya memproses event yang sudah divalidasi 
   oleh analis (Type M). Event otomatis (Type A) akan diabaikan agar database 
   tidak tercemar data noise/sampah.

[ 2. FITUR UTAMA ]
- Auto-Detect Tipe Event: Membaca baris "Alert" untuk membedakan Type M / A.
- Auto-Phase Labeling: Menentukan fase P dan S berdasarkan waktu tiba.
- Coordinate Fix: Mengubah format N/S/E/W menjadi koordinat +/-.
- CLI Support: Bisa dijalankan dengan argumen nama file (untuk otomasi).

[ 3. CARA PENGGUNAAN ]
A. MODE STANDAR (Manual)
   1. Pastikan file data bernama "Data_Seiscomp4.txt".
   2. Klik 2x script atau ketik: python SeisComP4_to_HypoDD.py
   
B. MODE EXPERT (Beda Nama File)
   Ketik di terminal:
   python SeisComP4_to_HypoDD.py [NamaFile_Input.txt] [NamaFile_Output.pha]
   Contoh:
   python SeisComP4_to_HypoDD.py Gempa_Januari.log Hasil_Januari.pha

[ 4. LOGIKA FILTERING (PENTING) ]
Script bekerja dengan membaca "Flag" pada baris Alert SeisComP:
- Jika baris mengandung "... type M" -> Data diproses & dikonversi.
- Jika baris mengandung "... type A" -> Data di-SKIP (Dihitung sebagai ignored).

[ 5. LAPORAN PROSES ]
Di akhir proses, layar akan menampilkan rekapitulasi:
- Jumlah Event M (Sukses masuk database).
- Jumlah Event A (Dibuang).

[ 6. CATATAN ]
Pastikan data input memuat baris "Alert ... type X" sebelum blok "LOCSAT solution".
Jika baris Alert tidak ada, script akan menganggap status event sebagai UNKNOWN 
dan mungkin akan melewatinya (tergantung konfigurasi keamanan).
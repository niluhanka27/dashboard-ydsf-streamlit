import csv
import os

# --- GANTI NAMA FILE INI ---
# Ganti dengan nama file yang menyebabkan error di aplikasi Anda.
# Contoh: "program_zakat.csv", "program_yatim.csv", dll.
NAMA_FILE_BERMASALAH = "program_yatim.csv"
# -------------------------

file_path = os.path.join("data", NAMA_FILE_BERMASALAH)

print(f"Menganalisis file: {file_path}\n")

try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        # Menggunakan csv.reader untuk kontrol manual
        reader = csv.reader(f)
        
        # Baca baris pertama (header) untuk mendapatkan jumlah kolom yang diharapkan
        try:
            header = next(reader)
            jumlah_kolom_harapan = len(header)
            print(f"✅ Header ditemukan dengan {jumlah_kolom_harapan} kolom.")
            print("-" * 30)
        except StopIteration:
            print("❌ ERROR: File CSV terdeteksi kosong.")
            exit()

        ada_masalah = False
        # Loop melalui sisa baris untuk menemukan ketidaksesuaian
        for i, row in enumerate(reader, start=1):
            jumlah_kolom_sekarang = len(row)
            
            # Bandingkan jumlah kolom saat ini dengan jumlah kolom header
            if jumlah_kolom_sekarang != jumlah_kolom_harapan:
                print(f"🔴 MASALAH DITEMUKAN PADA BARIS DATA KE-{i} (Baris file ke-{i + 1})")
                print(f"   -> Diharapkan {jumlah_kolom_harapan} kolom, tetapi ditemukan {jumlah_kolom_sekarang} kolom.")
                print(f"   -> Isi baris yang bermasalah:")
                print(f"      {row}\n")
                ada_masalah = True

        print("-" * 30)
        if not ada_masalah:
            print("✅ Selamat! Tidak ada masalah format kolom yang ditemukan di file ini.")
        else:
            print("Silakan perbaiki baris yang ditandai di atas dalam file CSV Anda.")

except FileNotFoundError:
    print(f"❌ ERROR: File tidak ditemukan di lokasi '{file_path}'. Pastikan nama file di dalam kode sudah benar dan file ada di dalam folder 'data'.")
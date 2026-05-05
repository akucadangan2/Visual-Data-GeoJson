import geopandas as gpd
import pandas as pd
import os

# Folder sumber data Anda
input_folder = r"C:\WEB muranai\GEOJESN\GEOJESN"

# Kita buat folder baru khusus untuk data yang sudah bersih/fix
output_folder = r"C:\WEB muranai\GEOJESN\GEOJESN_FIX"
os.makedirs(output_folder, exist_ok=True)

# Daftar keempat file Anda
files_to_process = [
    "Bangunan_Kajian.geojson",
    "Batas Penelitian.geojson",
    "Bidang Lahan.geojson",
    "Zonasi RDTR.geojson"
]

print("=== MEMULAI PEMROSESAN DATA GEOJSON ===")

for file_name in files_to_process:
    input_path = os.path.join(input_folder, file_name)
    output_path = os.path.join(output_folder, file_name)
    
    if not os.path.exists(input_path):
        print(f"\n[Lewati] File tidak ditemukan: {file_name}")
        continue
        
    print(f"\nMemproses: {file_name}")
    try:
        # Membaca data
        gdf = gpd.read_file(input_path)
        
        # 1. PERBAIKAN KOORDINAT (Wajib untuk WebGIS)
        if gdf.crs is None:
            print("  [Peringatan] CRS tidak ada, mengatur asusmi ke WGS84...")
            gdf.set_crs(epsg=4326, inplace=True)
        elif gdf.crs.to_epsg() != 4326:
            current_crs = gdf.crs.to_epsg() or gdf.crs.name
            print(f"  [Info] Konversi Koordinat dari {current_crs} ke EPSG:4326 (WGS84)...")
            gdf = gdf.to_crs(epsg=4326)
        else:
            print("  [Info] Koordinat sudah EPSG:4326.")

        # 2. PERBAIKAN ATRIBUT LOD2 (Hanya untuk Bangunan)
        if file_name == "Bangunan_Kajian.geojson":
            kolom_tinggi = ['MAX_HEIGHT', 'MIN_HEIGHT', 'measuredHe', 'HMAX']
            print("  [Info] Memperbaiki tipe data numerik untuk extrude 3D...")
            
            for col in kolom_tinggi:
                if col in gdf.columns:
                    # Ubah jadi float, hilangkan teks nyasar jadi 0.0
                    gdf[col] = pd.to_numeric(gdf[col], errors='coerce').fillna(0.0)
                else:
                    # Buat kolom default jika tidak ada
                    gdf[col] = 0.0 if 'MIN' in col else 10.0
            
            # Pastikan tinggi puncak > tinggi dasar
            mask_error = gdf['MAX_HEIGHT'] <= gdf['MIN_HEIGHT']
            if mask_error.any():
                jumlah_error = mask_error.sum()
                print(f"  [Perbaikan] {jumlah_error} atap error (Tinggi Maks <= Tinggi Dasar). Diperbaiki...")
                gdf.loc[mask_error, 'MAX_HEIGHT'] = gdf.loc[mask_error, 'MIN_HEIGHT'] + 3.0

        # Simpan file ke folder FIX
        print(f"  Menyimpan ke folder GEOJESN_FIX...")
        gdf.to_file(output_path, driver="GeoJSON")
        print(f"  [Sukses] {file_name} Selesai!")

    except Exception as e:
        print(f"  [Error] Gagal memproses {file_name}: {str(e)}")

print("\n=== SEMUA PROSES SELESAI ===")
print(f"Silakan gunakan data di folder: {output_folder}")
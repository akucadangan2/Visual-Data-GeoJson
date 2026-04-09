import geopandas as gpd
import os

# Lokasi folder tempat file GeoJSON Anda berada
folder_path = r"C:\WEB muranai\data"

# Daftar file yang akan dikonversi
file_list = [
    "Bangunan_Kajian.geojson",
    "Batas Penelitian.geojson",
    "Bidang Lahan.geojson",
    "Zonasi RDTR.geojson"
]

print("=== Memulai Konversi Koordinat UTM ke WGS 84 ===")

for filename in file_list:
    file_path = os.path.join(folder_path, filename)
    
    if os.path.exists(file_path):
        print(f"⏳ Membaca: {filename}...")
        
        # 1. Membaca file GeoJSON
        gdf = gpd.read_file(file_path)
        
        # 2. Jika sistem tidak otomatis mengenali CRS bawaan, kita paksa set ke UTM Zone 48S (EPSG:32748)
        if gdf.crs is None:
            gdf.set_crs(epsg=32748, inplace=True)
            
        # 3. Konversi koordinat ke WGS 84 (EPSG:4326)
        print(f"🔄 Mengonversi {filename} ke EPSG:4326...")
        gdf_wgs84 = gdf.to_crs(epsg=4326)
        
        # 4. Menyimpan file
        # Kita simpan dengan nama sementara dulu untuk mencegah file rusak/corrupt saat proses write
        temp_path = os.path.join(folder_path, "temp_" + filename)
        gdf_wgs84.to_file(temp_path, driver="GeoJSON")
        
        # 5. Timpa file asli dengan file yang sudah dikonversi
        os.replace(temp_path, file_path)
        
        print(f"✅ Selesai: {filename} berhasil diperbarui!\n")
    else:
        print(f"❌ Gagal: File tidak ditemukan di {file_path}\n")

print("🎉 Semua proses selesai! Silakan refresh browser web Anda.")
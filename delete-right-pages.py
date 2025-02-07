import os
import glob

# PNG dosyalarının bulunduğu klasörü belirt
directory = './'  # Buraya kendi dosya yolunu yaz

# Belirtilen klasördeki *_right.png desenine uyan dosyaları bul
files_to_delete = glob.glob(os.path.join(directory, '*_right.png'))

# Dosyaları sil
for file_path in files_to_delete:
    try:
        os.remove(file_path)
        # print(f"Silindi: {file_path}")
    except Exception as e:
        print(f"Silinemedi: {file_path}, Hata: {e}")

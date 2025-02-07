import os

# Dosyaların bulunduğu dizin
directory = './'  # Örneğin: 'C:/kullanici/dosyalar'

# Dizindeki tüm dosyaları al
for filename in os.listdir(directory):
    if filename.startswith("page_") and filename.endswith(".png"):
        # Dosya numarasını çıkar
        num_part = filename.replace("page_", "").replace(".png", "")

        if num_part.isdigit():
            number = int(num_part)
            # Çiftse 'left', tekse 'right' ekle
            new_filename = f"page_{number}_{'left' if number % 2 == 0 else 'right'}.png"

            # Eski ve yeni dosya yollarını oluştur
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, new_filename)

            # Dosyayı yeniden adlandır
            os.rename(old_file, new_file)
            print(f"Renamed: {filename} -> {new_filename}")

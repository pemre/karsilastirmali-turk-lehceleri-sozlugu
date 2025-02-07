from PIL import Image
import os
import glob

# PNG dosyalarının bulunduğu klasörün yolu
directory = './'  # Buraya kendi dosya yolunu yaz

# *_left.png dosyalarını bul
image_files = glob.glob(os.path.join(directory, '*_left.png'))

# Her bir resmi kırp
for image_path in image_files:
    try:
        with Image.open(image_path) as img:
            width, height = img.size

            # Kırpma koordinatları:
            # (left, upper, right, lower)
            left = 0               # Soldan başla (0px)
            upper = 230            # Üstten 230px kırp
            right = 333            # Sağdan 333px genişliğinde bırak
            lower = height         # Alt kısmı tamamen bırak

            # Resmi kırp
            cropped_img = img.crop((left, upper, right, lower))

            # Üzerine yazmak için resmi kaydet
            cropped_img.save(image_path)

            print(f"Kırpıldı: {image_path}")

    except Exception as e:
        print(f"Hata oluştu: {image_path}, Hata: {e}")

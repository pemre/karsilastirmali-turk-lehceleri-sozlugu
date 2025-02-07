import os
import cv2
import pytesseract
import numpy as np
import glob
from concurrent.futures import ThreadPoolExecutor
import re

# Klasör ve çıktı dosyası ayarları
directory = './'                   # Çalışma klasörü
output_file = 'index7-sonuc.txt'   # Sonuçların kaydedileceği dosya

# Dosya adındaki sayıyı çekip sıralama için fonksiyon
def extract_page_number(filename):
    match = re.search(r'page_(\d+)_left\.png', filename)
    return int(match.group(1)) if match else float('inf')

# *_left.png dosyalarını sayfa numarasına göre sırala
image_files = sorted(glob.glob(os.path.join(directory, '*_left.png')), key=extract_page_number)
total_files = len(image_files)

# OCR işlemini yapan fonksiyon
def process_image(image_path):
    try:
        # Görüntüyü oku, gri tonlamaya çevir
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Gürültü azaltma ve keskinleştirme
        blurred = cv2.medianBlur(gray, 3)
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        sharpened = cv2.filter2D(blurred, -1, kernel)

        # Binarizasyon (Otsu Thresholding)
        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # OCR işlemi: Türkçe dil desteği ile
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(binary, lang='tur', config=custom_config)

        return os.path.basename(image_path), text
    except Exception as e:
        return os.path.basename(image_path), f"Hata: {e}"

# Çıktı dosyasını baştan temizle
with open(os.path.join(directory, output_file), 'w', encoding='utf-8') as f:
    f.write("")

# executor.map kullanarak, sonuçları input listesindeki sıraya göre alıyoruz
with ThreadPoolExecutor() as executor:
    for idx, (basename, text) in enumerate(executor.map(process_image, image_files)):
        # Sonucu dosyaya ekle
        with open(os.path.join(directory, output_file), 'a', encoding='utf-8') as f:
            f.write(f"--- {basename} ---\n{text}\n")
        # Terminale ilerleme bilgisini yazdır
        print(f"[{idx + 1}/{total_files}] OCR tamamlandı: {basename}")

print(f"\nOCR işlemi tamamlandı! Sonuçlar '{output_file}' dosyasına kaydedildi.")

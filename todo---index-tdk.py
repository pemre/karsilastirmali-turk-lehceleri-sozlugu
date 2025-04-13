import os
import time
import re
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Giriş ve çıkış dosya/klasör ayarları
input_file = 'index7-sonuc.txt'
output_dir = './tdk'
error_file_path = 'index-tdk-errors.txt'

os.makedirs(output_dir, exist_ok=True)

# Dosyayı oku ve gereksiz satırları filtrele
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

words = []
for line in lines:
    line = line.strip()
    if not line or line.startswith('---'):
        continue
    words.append(line)

# Test amaçlı 20. kelimeden 100. kelimeye kadar olanları seç (Python indexleri: 20-99)
words = words[1000:10000]

# Fonksiyon: Özel harfleri ascii'ye çevir (Türkçe harfler kalır)
def to_ascii(word):
    replacements = {
        'â': 'a', 'Â': 'A',
        'î': 'i', 'Î': 'I',
        'û': 'u', 'Û': 'U',
        'ô': 'o', 'Ô': 'O',
        'á': 'a', 'Á': 'A',
        'é': 'e', 'É': 'E',
        'í': 'i', 'Í': 'I',
        'ó': 'o', 'Ó': 'O',
        'ú': 'u', 'Ú': 'U',
        # İhtiyaç duyulursa diğer özel karakterler eklenebilir.
    }
    for orig, repl in replacements.items():
        word = word.replace(orig, repl)
    return word

# Session oluştur ve retry stratejisi ayarla
session = requests.Session()
retry_strategy = Retry(
    total=5,                      # Toplam 5 deneme
    backoff_factor=1,             # Her başarısız denemeden sonra bekleme süresi
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Tarayıcı benzeri User-Agent ayarla
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/90.0.4430.85 Safari/537.36'
}

# Hata dosyasını aç (anlık yazım için)
with open(error_file_path, 'w', encoding='utf-8') as error_file:
    # Her kelime için API sorgusu yap
    for word in words:
        ascii_word = to_ascii(word)
        url = f"https://sozluk.gov.tr/lehceler?ara={ascii_word}&lehce=1"
        print(f"Sorgulanıyor: {word} (ASCII: {ascii_word}) -> {url}")
        try:
            response = session.get(url, headers=headers)
            if response.status_code == 200:
                try:
                    data = response.json()
                except Exception as e:
                    error_message = f"{word}: JSON parse hatası: {e}"
                    print(error_message)
                    error_file.write(error_message + "\n")
                    error_file.flush()
                    continue

                output_filename = os.path.join(output_dir, f"{ascii_word}.json")
                with open(output_filename, 'w', encoding='utf-8') as outfile:
                    json.dump(data, outfile, ensure_ascii=False, indent=2)
                print(f"'{word}' için sonuç kaydedildi: {output_filename}")
            else:
                error_message = f"{word}: Sorgu başarısız oldu. Durum kodu: {response.status_code}"
                print(error_message)
                error_file.write(error_message + "\n")
                error_file.flush()
        except Exception as e:
            error_message = f"{word}: Sorgu sırasında hata oluştu: {e}"
            print(error_message)
            error_file.write(error_message + "\n")
            error_file.flush()
        # API'yi yormamak için istekler arasında 1 saniye bekle
        time.sleep(0.35)

print("\nTüm sorgular tamamlandı!")

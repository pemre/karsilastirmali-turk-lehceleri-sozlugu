import requests
import json
import time
import os
from collections import OrderedDict

# AYARLANABİLİR DEĞİŞKENLER
INPUT_FILE = 'sozluk-turkce-dizini.txt'
ERROR_LOG_FILE = 'tdk-sorgu-hata.txt'
SUCCESS_LOG_FILE = 'tdk-sorgu-basarili.txt'
RESULT_DIR = 'tdk-sonuc'
URL_TEMPLATE = 'https://sozluk.gov.tr/lehceler?ara={}&lehce=1'
SLEEP_TIME = 1.0   # saniye cinsinden (350ms)
START_LINE = 1     # 1-indexli: 1. satırdan başla
END_LINE = 8000    # 1-indexli: 8000. satıra kadar (dahil)

# Tarayıcı benzeri User-Agent
HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/90.0.4430.85 Safari/537.36')
}

# TEMİZLEME İÇİN HARF REPLACE TABLOSU
replacements = {
    'ā': 'a',
    'â': 'a',
    'ı̄': 'ı',
    'ī': 'i',
    'î': 'i',
    'ū': 'u',
    'û': 'u',
    'ē': 'e',
    'ȫ': 'ö',
    'ḳ': 'k'
}

# Sonuç klasörünün varlığını kontrol et, yoksa oluştur.
if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)

# Log yazımı için fonksiyonlar.
def log_error(message):
    with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as log_file:
        log_file.write(message + "\n")
    print(message)

def log_success(message):
    with open(SUCCESS_LOG_FILE, 'a', encoding='utf-8') as log_file:
        log_file.write(message + "\n")
    print(message)

# Sozcugu temizleyen fonksiyon.
def clean_word(word):
    for old, new in replacements.items():
        word = word.replace(old, new)
    return word

# Dosyadan tüm satırları oku.
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1-index'e göre START_LINE ile END_LINE arası satırları işle.
for idx in range(START_LINE - 1, min(END_LINE, len(lines))):
    line = lines[idx].strip()
    # "---" ile başlayan satırları atla.
    if line.startswith('---'):
        continue

    original_word = line
    cleaned_word = clean_word(original_word)
    fetch_url = URL_TEMPLATE.format(cleaned_word)

    success = False
    # Retry mekanizması: toplam 3 deneme
    for attempt in range(1, 4):
        try:
            response = requests.get(fetch_url, headers=HEADERS)
        except Exception as e:
            if attempt == 3:
                error_msg = (f"* {original_word} --> {cleaned_word} --: HATA exception "
                             f"(attempt {attempt}) ---- {fetch_url}")
                log_error(error_msg)
            time.sleep(SLEEP_TIME)
            continue

        if response.status_code != 200:
            if attempt == 3:
                error_msg = (f"* {original_word} --> {cleaned_word} --: HATA {response.status_code} "
                             f"(attempt {attempt}) ---- {fetch_url}")
                log_error(error_msg)
            time.sleep(SLEEP_TIME)
            continue

        try:
            data = response.json()
        except Exception as e:
            if attempt == 3:
                error_msg = (f"* {original_word} --> {cleaned_word} --: HATA JSON_DECODE "
                             f"(attempt {attempt}) ---- {fetch_url}")
                log_error(error_msg)
            time.sleep(SLEEP_TIME)
            continue

        # 200 kodu geldiyse fakat içerik "Sonuç bulunamadı" ise
        if data == {"error": "Sonuç bulunamadı"}:
            error_msg = (f"* {original_word} --> {cleaned_word} --: 200 ama sonuç bulunamadı "
                         f"(attempt {attempt})")
            log_error(error_msg)
            break  # Bu durumda retry'a gerek yok
        else:
            # Başarılı sonuç, logla ve dosyaya kaydet.
            success_msg = f"* {original_word} --> {cleaned_word} --: BASARILI (attempt {attempt})"
            log_success(success_msg)

            # Gelen veriye "$kitaptaki_turkce" property'si ekleniyor.
            new_data = []
            for entry in data:
                new_entry = OrderedDict()
                new_entry["$kitaptaki_turkce"] = original_word
                if "lehce_id" in entry:
                    new_entry["lehce_id"] = entry["lehce_id"]
                for key, value in entry.items():
                    if key != "lehce_id":
                        new_entry[key] = value
                new_data.append(new_entry)

            # Dosya ismi oluşturma; eğer aynı isimde dosya varsa numaralı isimlendirme yap.
            base_filename = f"{cleaned_word}.json"
            file_path = os.path.join(RESULT_DIR, base_filename)
            if os.path.exists(file_path):
                # Dosya ismi çakışması durumunda ek log yaz
                log_success(f"**** AYNI sozcuk bulundu: {original_word} --> {cleaned_word}")
                index = 1
                while True:
                    new_filename = f"{cleaned_word}---{index}.json"
                    new_file_path = os.path.join(RESULT_DIR, new_filename)
                    if not os.path.exists(new_file_path):
                        file_path = new_file_path
                        break
                    index += 1

            with open(file_path, 'w', encoding='utf-8') as out_file:
                json.dump(new_data, out_file, ensure_ascii=False, indent=2)

            success = True
            break  # Başarılı olduğu için retry döngüsünden çık

    # Her sozcuk için, ister başarılı ister hata olsun her seferinde SLEEP_TIME kadar bekle.
    time.sleep(SLEEP_TIME)

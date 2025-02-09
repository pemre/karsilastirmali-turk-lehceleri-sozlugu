import requests
import json
import time
import os
from collections import OrderedDict

# AYARLANABİLİR DEĞİŞKENLER
LOG_INPUT_FILE = 'tdk-sorgu-hata.txt'  # İçinde örnek log satırları olan dosya
ERROR_LOG_FILE = 'tdk-sorgu-hata-multi.txt'
SUCCESS_LOG_FILE = 'tdk-sorgu-basarili-multi.txt'
RESULT_DIR = 'tdk-sonuc-multi'
URL_TEMPLATE = 'https://sozluk.gov.tr/lehceler?ara={}&lehce=1'
SLEEP_TIME = 1.0  # saniye cinsinden (1000ms)
RETRY_LIMIT = 3
START_LINE = 1    # 1-indexli: 1. satırdan başla
END_LINE = 700    # 1-indexli: 700. satıra kadar (dahil)

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

# RESULT_DIR varsa kontrol et, yoksa oluştur.
if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)

# Log yazım fonksiyonları.
def log_error(message):
    with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(message + "\n")
    print(message)

def log_success(message):
    with open(SUCCESS_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(message + "\n")
    print(message)

# Sozcugu temizleyen fonksiyon.
def clean_word(word):
    for old, new in replacements.items():
        word = word.replace(old, new)
    return word

# Log satırından, "* " sonrası ve ilk "(" öncesindeki kısmı çıkaran fonksiyon.
def extract_word(line):
    if line.startswith("* "):
        line = line[2:]
    idx = line.find("(")
    if idx != -1:
        return line[:idx].strip()
    else:
        return line.strip()

# Daha önce işlenmiş kelimeleri tutacak set
processed_words = set()

# Dosyadan log satırlarını oku.
with open(LOG_INPUT_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# START_LINE ve END_LINE aralığında işlem yap.
for i in range(START_LINE - 1, min(END_LINE, len(lines))):
    line = lines[i].strip()
    if not line:
        continue

    # Log satırından, "* " sonrası ve ilk "(" öncesindeki kelimeyi al (örn. "alay")
    original_word = extract_word(line)
    # Harf temizleme tablosunu uygulayarak temizlenmiş kelimeyi elde et.
    cleaned_word = clean_word(original_word)

    # Eğer bu kelime daha önce sorgu gönderildiyse, sorgu yapmadan atla.
    if cleaned_word in processed_words:
        log_success(f"**** {original_word} ({cleaned_word}) zaten işlendi, sorgu gönderilmiyor.")
        continue

    fetch_url = URL_TEMPLATE.format(cleaned_word)

    success = False
    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            response = requests.get(fetch_url, headers=HEADERS)
        except Exception as e:
            if attempt == RETRY_LIMIT:
                log_error(f"* {original_word} ({cleaned_word}) --: HATA exception (attempt {attempt}) ---- {fetch_url}")
            time.sleep(SLEEP_TIME)
            continue

        if response.status_code != 200:
            if attempt == RETRY_LIMIT:
                log_error(f"* {original_word} ({cleaned_word}) --: HATA {response.status_code} (attempt {attempt}) ---- {fetch_url}")
            time.sleep(SLEEP_TIME)
            continue

        try:
            data = response.json()
        except Exception as e:
            if attempt == RETRY_LIMIT:
                log_error(f"* {original_word} ({cleaned_word}) --: HATA JSON_DECODE (attempt {attempt}) ---- {fetch_url}")
            time.sleep(SLEEP_TIME)
            continue

        # {"error": "Sonuç bulunamadı"} durumu varsa, hata loglayıp döngüden çık.
        if isinstance(data, dict) and data.get("error") == "Sonuç bulunamadı":
            log_error(f"* {original_word} ({cleaned_word}) --: 200 ama sonuç bulunamadı (attempt {attempt})")
            break

        # Geçerli sonuçta data liste değilse, listeye çevir.
        if not isinstance(data, list):
            data = [data]

        # Çoklu sonuç varsa, her bir girdiyi "asil" property'sine göre ayrı dosyaya kaydet.
        for entry in data:
            new_entry = OrderedDict()
            new_entry["$kitaptaki_turkce"] = original_word
            asil_value = entry.get("asil", cleaned_word)
            new_entry["asil"] = asil_value
            for key, value in entry.items():
                if key == "asil":
                    continue
                new_entry[key] = value

            # Dosya adı: {asil_value}.json
            base_filename = f"{asil_value}.json"
            file_path = os.path.join(RESULT_DIR, base_filename)
            if os.path.exists(file_path):
                log_success(f"**** AYNI sozcuk bulundu: {original_word} --> {asil_value}")
                index = 1
                while True:
                    new_filename = f"{asil_value}---{index}.json"
                    new_file_path = os.path.join(RESULT_DIR, new_filename)
                    if not os.path.exists(new_file_path):
                        file_path = new_file_path
                        break
                    index += 1

            with open(file_path, 'w', encoding='utf-8') as out_file:
                json.dump(new_entry, out_file, ensure_ascii=False, indent=2)

        log_success(f"* {original_word} ({cleaned_word}) --: BASARILI (attempt {attempt})")
        # Bu kelime için sorgu gönderildi, set'e ekle.
        processed_words.add(cleaned_word)
        success = True
        break  # Başarılı olduğu için retry döngüsünden çık

    time.sleep(SLEEP_TIME)

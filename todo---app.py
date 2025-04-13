from flask import Flask, render_template
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    folder = './tdk'  # JSON dosyalarının bulunduğu klasör
    files = [f for f in os.listdir(folder) if f.endswith('.json')]
    rows = []
    # Kullanmak istediğiniz dil sütunları; sıralama soldan sağa olacaktır
    languages = ["turkce", "azerice", "baskurtca", "kazakca", "kirgizca", "ozbekce", "tatarca", "turkmence", "uygurca", "rusca"]

    for file in files:
        file_path = os.path.join(folder, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                continue
            # Dosya içeriği listeyse
            if isinstance(data, list):
                for record in data:
                    row = {}
                    row['file'] = file
                    row['lehce_id'] = record.get('lehce_id', '')
                    row['asil'] = record.get('asil', '')
                    # Her dil için önce ilgili anahtar, yoksa "1" eki olanı alıyoruz
                    for lang in languages:
                        value = record.get(lang)
                        if value is None:
                            value = record.get(lang + "1", "")
                        if value is None:
                            value = ""
                        row[lang] = value
                    rows.append(row)
            # Dosya bir sözlükse
            elif isinstance(data, dict):
                record = data
                row = {}
                row['file'] = file
                row['lehce_id'] = record.get('lehce_id', '')
                row['asil'] = record.get('asil', '')
                for lang in languages:
                    value = record.get(lang)
                    if value is None:
                        value = record.get(lang + "1", "")
                    if value is None:
                        value = ""
                    row[lang] = value
                rows.append(row)

    # Alfabetik sıralama: "asil" alanına göre (küçük harf olarak karşılaştırma yapılıyor)
    rows.sort(key=lambda row: row.get('asil', '').lower())

    # Tablo başlıklarını oluşturuyoruz; ilk sütunlarda dosya, lehce_id, asil bilgileri, sonra diller
    header = ["Dosya", "Lehce ID", "Asil"] + languages
    return render_template('matrix.html', header=header, rows=rows)

if __name__ == '__main__':
    app.run(debug=True)

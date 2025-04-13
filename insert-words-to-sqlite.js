// Gerekli modüllerin yüklenmesi
const fs = require('fs').promises;
const path = require('path');
const sqlite3 = require('sqlite3').verbose();

// Veritabanı bağlantısı (dosya yolunu kendi ortamınıza göre ayarlayın)
const db = new sqlite3.Database('./dil_test.db');

// Callback tabanlı sqlite metodlarını promise destekli hale getiren yardımcı fonksiyonlar
function runAsync(query, params = []) {
  return new Promise((resolve, reject) => {
    db.run(query, params, function (err) {
      if (err) reject(err);
      else resolve(this.lastID);
    });
  });
}

function getAsync(query, params = []) {
  return new Promise((resolve, reject) => {
    db.get(query, params, function (err, row) {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

function allAsync(query, params = []) {
  return new Promise((resolve, reject) => {
    db.all(query, params, function (err, rows) {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

// JSON dosyasındaki çeviri alanlarının, ilgili dilin ISO 639-3 kodlarıyla eşleşmesini sağlayan mapping
const fieldMapping = {
  "azerice": "aze",
  "baskurtca": "bak",  // Bashkir için ISO 639-3: 'bak'
  "kazakca": "kaz",
  "kirgizca": "kir",
  "ozbekce": "uzb",
  "tatarca": "tat",
  "turkmence": "tuk",
  "uygurca": "uig",
  "rusca": "rus"
};

async function processJSONFiles(directory) {
  try {
    // 1. language tablosundaki dilleri, {kod: id} şeklinde hafızaya alalım.
    const langRows = await allAsync("SELECT id, code FROM language");
    const languages = {};
    langRows.forEach(row => {
      languages[row.code] = row.id;
    });

    // 2. Kaynak (source) ekleniyor: "Karşılaştırmalı Türk Lehçeleri Sözlüğü I" kitabı Türkçe (kod: "tur") olarak.
    const sourceTitle = "Karşılaştırmalı Türk Lehçeleri Sözlüğü I";
    const sourceType = "kitap";  // tip olarak kitap varsayıldı
    const sourceLanguageCode = "tur";
    const sourceLanguageId = languages[sourceLanguageCode];
    if (!sourceLanguageId) {
      throw new Error(`Language with code "${sourceLanguageCode}" not found in language table.`);
    }

    // Eğer aynı kaynağın tekrar eklenmemesi için title bazlı kontrol eklenebilir.
    const sourceInsertQuery = `
      INSERT INTO source (type, language_id, title, publication_year, open_library_edition_id, annas_archive_id)
      VALUES (?, ?, ?, ?, ?, ?)
    `;
    const sourceId = await runAsync(sourceInsertQuery, [sourceType, sourceLanguageId, sourceTitle, null, null, null]);
    console.log(`Source added with id: ${sourceId}`);

    // 3. Dizin içerisindeki tüm JSON dosyalarını alıyoruz.
    const files = await fs.readdir(directory);

    for (const file of files) {
      // Sadece .json dosyalarını işleyelim
      if (path.extname(file) === '.json') {
        // Dosya adının uzantısı olmadan kalan kısmı, word tablosuna ekleyeceğimiz kelime olarak kullanılacak.
        const wordName = path.basename(file, '.json');
        const filePath = path.join(directory, file);
        console.log(`Processing file: ${filePath}`);

        // Dosya içeriğini oku
        const content = await fs.readFile(filePath, 'utf8');
        let record = JSON.parse(content);
        // Eğer dosya içeriği dizi ise, ilk nesneyi kullanalım
        if (Array.isArray(record)) {
          record = record[0];
        }

        // Her dosya için ayrı transaction açalım.
        await runAsync("BEGIN TRANSACTION");
        try {
          // 4. word tablosuna dosya adını ekle (örneğin "abajur")
          const wordInsertQuery = `INSERT INTO word (tur) VALUES (?)`;
          const wordId = await runAsync(wordInsertQuery, [wordName]);

          // 5. Dosyadaki çeviri alanlarını işle (örneğin azerice1...rusca4)
          for (const fieldPrefix in fieldMapping) {
            // Her dil için 1'den 4'e kadar alanı kontrol ediyoruz.
            for (let i = 1; i <= 4; i++) {
              const fieldName = `${fieldPrefix}${i}`;
              if (record.hasOwnProperty(fieldName) && record[fieldName] !== null) {
                const translationValue = record[fieldName];
                const langCode = fieldMapping[fieldPrefix];
                const languageId = languages[langCode];
                if (!languageId) {
                  console.warn(`Language with code "${langCode}" not found. Skipping field ${fieldName}.`);
                  continue;
                }

                // 5a. a-word-has-many-translations tablosuna ekleme
                const translationInsertQuery = `
                  INSERT INTO \`a-word-has-many-translations\` (word_id, language_id, translation)
                  VALUES (?, ?, ?)
                `;
                const translationId = await runAsync(translationInsertQuery, [wordId, languageId, translationValue]);

                // 5b. Her çeviri için a-translation-has-many-references tablosuna, kaynak (source) bilgisiyle birlikte ekleme
                const referenceInsertQuery = `
                  INSERT INTO \`a-translation-has-many-references\` (translation_id, source_id, meaning, etymology)
                  VALUES (?, ?, ?, ?)
                `;
                await runAsync(referenceInsertQuery, [translationId, sourceId, null, null]);
              }
            }
          }
          await runAsync("COMMIT");
          console.log(`Finished processing file: ${filePath}`);
        } catch (err) {
          await runAsync("ROLLBACK");
          console.error(`Error processing file ${filePath}:`, err);
        }
      }
    }
  } catch (err) {
    console.error("Error processing JSON files:", err);
  } finally {
    db.close();
  }
}

// JSON dosyalarının bulunduğu dizini belirtin (örneğin './json_data')
processJSONFiles(path.join(__dirname, 'tdk-sitesinden-sozcukler'));

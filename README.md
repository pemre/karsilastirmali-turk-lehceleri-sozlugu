# Karşılaştırmalı Türk Lehçeleri Sözlüğü'nün sayısal ortama aktarılması

Amacim etkileşimli ve karşılaştırmalı Türk lehçeleri sözlüğü yapmakti.

TDK'nin sitesinde yer alan [Karşılaştırmalı Türk Lehçeleri Sözlüğü](https://sozluk.gov.tr/) sozcukleri tek tek aramaniza yariyor.

![](images/tdk-arama.png)

![](images/tdk-sonuc.png)

Bu sozluk aslinda Prof. Dr. Ahmet Bican Ercilasun'un komisyon baskanligini yaptigi [Karşılaştırmalı Türk Lehçeleri Sözlüğü I](https://openlibrary.org/works/OL15193466W?edition=key%3A/books/OL14515952M) (bu birinci kitap tabloyu iceriyor, ikinci kitap ise [dizin](https://openlibrary.org/works/OL42480158W?edition=key%3A/books/OL57648043M))'in sayısal ortama aktarılmis surumu. Ben de bu sozlugun taranmis pdf bicimini indirdim: [Karşılaştırmalı Türk Lehçeleri Sözlüğü I](./book-pdf/Karşılaştırmalı%20Türk%20Lehçeleri%20Sözlüğü%20I.pdf).

![](images/ktls.png)

Buradaki Turkiye Turkce'si listesini cikarip tek tek TDK'da arayacaktim.

Dosyadaki tum resimleri png olarak cikardim. Soldaki sayfalari `page_{sayfa-numarasi}_left.png`, sagdakileri `page_{sayfa-numarasi}_right.png` olarak adlandirdim ([rename-left-right.py](./rename-left-right.py)).

Tabloda Turkiye Turkce'si sol sayfanin en solunda yer aldigi icin isime yaramayan sag sayfa dosyalarini bir kenara attim ([delete-right-pages.py](delete-right-pages.py)) ve sol sayfalari Python koduyla kirptim ([crop-left-column.py](./crop-left-column.py)). Bunlar [./book-png-files-cropped](./book-png-files-cropped) dizininde yer aliyor.

Daha sonra bu resimleri yaziya cevirmek icin OCR (Optical Character Recognition), ve işlemi hızlandırmak için aynı anda birden fazla dosyayı işleyen çoklu iş parçacığı (threading) kullandim ([make-ocr.py](./make-ocr.py)).

Tum bu kodlar icin ChatGPT'den yardim aldim. Bana cok zaman kazandirdi.

TODO: Ciktilar cok kaliteli degildi. Elimle bunlari tek tek duzeltip temiz bir liste elde ettim: [tdk.md](./tdk.md)

TODO: Daha sonra TDK'nin sitesinde listedeki sozcukleri tek tek arayip sonuclari aldim. Bu islemi [tdk.py](./tdk.py) dosyasi yapiyor.


## YAPILACAKLAR

* bul: bildircin
* billûr
* ā
* boşaltmak
* bugun
* buz dolabı

## Buyuk dosyalar

GitHub, genellikle dosya boyutu sınırını 100MB ile sınırlıdır. Bu durumda 175MB'lık bir PDF dosyasını doğrudan GitHub'a yüklemek mümkün olmayabilir. Ancak bu dosyayı yüklemek için bazı alternatif yollar şunlar olabilir:

### 1. **Git LFS (Large File Storage) Kullanarak Yüklemek:**
Git LFS, büyük dosyaları GitHub reposunda saklamak için kullanılan bir araçtır. Git LFS kullanarak 175MB'lık PDF dosyasını yükleyebilirsiniz.

#### Adımlar:
1. **Git LFS'yi kurun:**
    - Git LFS'yi kurmak için şu komutları kullanabilirsiniz:
      ```bash
      git lfs install
      ```

2. **PDF dosyasını izlemek için Git LFS'ye ekleyin:**
    - Dosyanızın Git LFS tarafından izlenmesini sağlamak için şu komutu kullanın:
      ```bash
      git lfs track "*.pdf"
      ```
    - Bu, `.gitattributes` dosyasına `*.pdf` ekler ve PDF dosyalarının LFS aracılığıyla takip edilmesini sağlar.

3. **Değişiklikleri ekleyin ve commit yapın:**
    - Yüklemek istediğiniz PDF dosyasını ekleyin:
      ```bash
      git add .gitattributes
      git add <pdf_dosya_adı>
      ```

    - Daha sonra değişiklikleri commit edin:
      ```bash
      git commit -m "Add large PDF file"
      ```

4. **GitHub'a push yapın:**
    - Son olarak, dosyayı GitHub reposuna yüklemek için:
      ```bash
      git push origin main
      ```

   Bu işlemi tamamladıktan sonra, PDF dosyanız GitHub reposunda LFS aracılığıyla saklanacak.

### 2. **Dosyayı Dış Kaynağa Yükleyip GitHub'a Bağlantı Vermek:**
Eğer Git LFS kullanmak istemiyorsanız, dosyayı başka bir dosya barındırma servisine (örneğin, Google Drive, Dropbox, vb.) yükleyip, GitHub reposundaki README dosyasına veya başka bir dosyaya bağlantı verebilirsiniz.

#### Adımlar:
1. PDF dosyasını Google Drive veya benzeri bir servise yükleyin.
2. Dosyanın paylaşılabilir bağlantısını oluşturun.
3. GitHub README dosyanıza veya diğer ilgili dosyaya bağlantıyı ekleyin.

Bu yöntemle dosyanın GitHub üzerinde görünmesini sağlamak yerine, dış bir kaynağa yönlendirme yapmış olursunuz.

### 3. **GitHub Release Kullanmak:**
Büyük dosyalar için başka bir alternatif, GitHub'ın "Releases" özelliğini kullanmaktır. GitHub Releases, genellikle yazılım sürümleriyle ilgili büyük dosyaların paylaşılması için kullanılır.

#### Adımlar:
1. GitHub repo sayfanızda "Releases" sekmesine gidin.
2. Yeni bir sürüm oluşturun.
3. PDF dosyanızı buraya yükleyin.
4. Bu sürümü "tag" ile işaretleyin ve yayınlayın.

Bu şekilde, PDF dosyanız repo üzerinden indirilebilir olacaktır.

Her iki seçenek de büyük dosyaların yüklenmesi için uygundur, ancak Git LFS en uygun olanıdır çünkü dosyanın GitHub reposunda direkt olarak saklanmasını sağlar.


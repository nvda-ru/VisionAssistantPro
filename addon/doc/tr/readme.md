Profesyonel Görsel Asistan Dokümantasyonu

# Profesyonel Görsel Asistan

**Profesyonel Görsel Asistan**, NVDA için gelişmiş, çok modlu bir yapay zekâ asistanıdır. Google’ın Gemini modellerini kullanarak akıllı ekran okuma, çeviri, sesli dikte ve belge analiz yetenekleri sunar.

*Bu eklenti, Engelliler Uluslararası Günü onuruna topluluğa sunulmuştur.*

## 1. Kurulum ve Yapılandırma

**NVDA Menüsü > Tercihler > Ayarlar > Profesyonel Görsel Asistan** yolunu izleyin.

* **API Anahtarı:** Gerekli. [Google AI Studio](https://aistudio.google.com/) üzerinden ücretsiz bir anahtar alın.
* **Model:** `gemini-2.5-flash-lite` (En hızlı) veya standart Flash modellerini seçin.
* **Diller:** Kaynak, Hedef ve Yapay Zekâ Yanıt dillerini ayarlayın.
* **Akıllı Takas:** Kaynak metin hedef dil ile eşleştiğinde dilleri otomatik olarak değiştirir.

## 2. Genel Kısayollar

Dizüstü bilgisayar düzenleriyle maksimum uyumluluk sağlamak için tüm kısayollar **NVDA + Control + Shift** kullanır.

| Kısayol           | İşlev               | Açıklama                                                                               |
| ----------------- | ------------------- | -------------------------------------------------------------------------------------- |
| NVDA+Ctrl+Shift+T | Akıllı Çevirmen     | Gezgin imlecinin altındaki metni çevirir. Seçime öncelik verir.                        |
| NVDA+Ctrl+Shift+Y | Pano Çevirmeni      | Pano içeriğini çevirir. **Web tarayıcıları için önerilir**.                            |
| NVDA+Ctrl+Shift+S | Akıllı Dikte        | Konuşmayı metne dönüştürür. Başlatmak için bir kez, durdurup yazmak için tekrar basın. |
| NVDA+Ctrl+Shift+R | Metin İyileştirici  | Özetle, Dilbilgisini Düzelt, Açıkla veya **Özel İstemleri** çalıştırır.                |
| NVDA+Ctrl+Shift+C | CAPTCHA Çözücü      | CAPTCHA’yı yakalar ve otomatik olarak çözer.                                           |
| NVDA+Ctrl+Shift+V | Nesne Görüşü        | Gezgin nesnesini takip sohbetiyle birlikte tanımlar.                                   |
| NVDA+Ctrl+Shift+O | Tam Ekran Görüşü    | Tüm ekran düzenini ve içeriğini analiz eder.                                           |
| NVDA+Ctrl+Shift+D | Belge Analizi       | PDF/TXT/MD/PY dosyalarıyla sohbet eder.                                                |
| NVDA+Ctrl+Shift+F | Dosya OCR           | Görüntü/PDF dosyasından doğrudan OCR yapar.                                            |
| NVDA+Ctrl+Shift+A | Ses Yazıya Dökme    | MP3/WAV/OGG dosyalarını yazıya döker.                                                  |
| NVDA+Ctrl+Shift+L | Son Çeviri          | API kullanmadan son çeviriyi yeniden okur.                                             |
| NVDA+Ctrl+Shift+U | Güncelleme Kontrolü | GitHub üzerinden en son sürümü kontrol eder.                                           |
| NVDA+Ctrl+Shift+I | Durum Bildirimi     | Geçerli durumu duyurur (ör. “Yükleniyor...”, “Boşta”).                                 |

## 3. Özel İstemler ve Değişkenler

Ayarlar bölümünde komutlar oluşturun: `Ad:İstem Metni` (`|` veya yeni satırlarla ayırın).

### Kullanılabilir Değişkenler

| Değişken        | Açıklama                                          | Girdi Türü         |
| --------------- | ------------------------------------------------- | ------------------ |
| `[selection]`   | Şu anda seçili olan metin                         | Metin              |
| `[clipboard]`   | Pano içeriği                                      | Metin              |
| `[screen_obj]`  | Gezgin nesnesinin ekran görüntüsü                 | Görüntü            |
| `[screen_full]` | Tam ekran görüntüsü                               | Görüntü            |
| `[file_ocr]`    | Görüntü/PDF/TIFF seçin (varsayılan “Metni çıkar”) | Görüntü, PDF, TIFF |
| `[file_read]`   | Metin belgesi seçin                               | TXT, Kod, PDF      |
| `[file_audio]`  | Ses dosyası seçin                                 | MP3, WAV, OGG      |

### Örnek Özel İstemler

* **Hızlı OCR:** `Benim OCR:[file_ocr]`
* **Görüntü Çevir:** `Görüntüyü Çevir:Bu görüntüden metni çıkar ve Farsçaya çevir. [file_ocr]`
* **Ses Analizi:** `Sesi Özetle:Bu kaydı dinle ve ana noktaları özetle. [file_audio]`
* **Kod Hata Ayıklayıcı:** `Hata Ayıkla:Bu koddaki hataları bul ve açıkla: [selection]`

**Not:** Dosya yüklemeleri 15MB ile sınırlıdır. İnternet gereklidir. Çok sayfalı TIFF dosyaları desteklenir.

## 2.8 için Değişiklikler

* İtalyanca çeviri eklendi.
* **Durum Bildirimi:** Eklentinin mevcut durumunu duyurmak için yeni bir komut eklendi (NVDA+Control+Shift+I) (ör. “Yükleniyor...”, “Analiz ediliyor...”).
* **HTML Dışa Aktarma:** Sonuç diyaloglarındaki “İçeriği Kaydet” düğmesi artık başlıklar ve kalın metin gibi stilleri koruyarak biçimlendirilmiş bir HTML dosyası olarak kaydediyor.
* **Ayarlar Arayüzü:** Erişilebilir gruplama ile Ayarlar paneli düzeni iyileştirildi.
* **Yeni Modeller:** gemini-flash-latest ve gemini-flash-lite-latest desteği eklendi.
* **Diller:** Desteklenen dillere Nepalce eklendi.
* **İyileştirme Menüsü Mantığı:** NVDA arayüz dili İngilizce olmadığında “Metni İyileştir” komutlarının çalışmamasına neden olan kritik bir hata düzeltildi.
* **Dikte:** Konuşma girişi olmadığında yanlış metin çıktısını önlemek için sessizlik algılama iyileştirildi.
* **Güncelleme Ayarları:** “Başlangıçta güncellemeleri kontrol et” seçeneği, Eklenti Mağazası politikalarına uymak için varsayılan olarak devre dışı bırakıldı.
* Kod temizliği yapıldı.

## 2.7 için Değişiklikler

* Daha iyi standart uyumu için proje yapısı resmi NV Access Eklenti Şablonuna taşındı.
* Yüksek trafik sırasında güvenilirliği sağlamak için HTTP 429 (Oran Sınırı) hatalarına yönelik otomatik yeniden deneme mantığı uygulandı.
* Daha yüksek doğruluk ve daha iyi “Akıllı Değişim” mantığı için çeviri istemleri optimize edildi.
* Rusça çeviri güncellendi.

## 2.6 için Değişiklikler

* Rusça çeviri desteği eklendi (nvda-ru’ya teşekkürler).
* Bağlantı durumlarıyla ilgili daha açıklayıcı geri bildirim sağlamak için hata mesajları güncellendi.
* Varsayılan hedef dil İngilizce olarak değiştirildi.

## 2.5 için Değişiklikler

* Yerel Dosya OCR Komutu eklendi (NVDA+Control+Shift+F).
* Sonuç diyaloglarına “Sohbeti Kaydet” düğmesi eklendi.
* Tam yerelleştirme desteği (i18n) uygulandı.
* Sesli geri bildirim NVDA’nın yerel tonlar modülüne taşındı.
* PDF ve ses dosyalarının daha iyi işlenmesi için Gemini Dosya API’sine geçildi.
* Küme parantezleri içeren metinler çevrilirken oluşan çökme düzeltildi.

## 2.1.1 için Değişiklikler

* `[file_ocr]` değişkeninin Özel İstemler içinde doğru çalışmamasına neden olan bir sorun düzeltildi.

## 2.1 için Değişiklikler

* NVDA’nın Dizüstü Bilgisayar düzeni ve sistem kısayollarıyla çakışmaları ortadan kaldırmak için tüm kısayollar NVDA+Control+Shift kullanacak şekilde standartlaştırıldı.

## 2.0 için Değişiklikler

* Yerleşik Otomatik Güncelleme sistemi uygulandı.
* Önceden çevrilmiş metinlerin anında geri alınması için Akıllı Çeviri Önbelleği eklendi.
* Sohbet diyaloglarında sonuçları bağlamsal olarak iyileştirmek için Konuşma Hafızası eklendi.
* Özel Pano Çevirisi komutu eklendi (NVDA+Control+Shift+Y).
* Yapay zekâ istemleri, hedef dil çıktısını kesin olarak zorlayacak şekilde optimize edildi.
* Girdi metnindeki özel karakterlerden kaynaklanan çökme düzeltildi.

## 1.5 için Değişiklikler

* 20’den fazla yeni dil desteği eklendi.
* Takip soruları için Etkileşimli İyileştirme Diyaloğu uygulandı.
* Yerel Akıllı Dikte özelliği eklendi.
* NVDA’nın Girdi Hareketleri diyaloguna “Vision Assistant” kategorisi eklendi.
* Firefox ve Word gibi bazı uygulamalarda oluşan COMError çökmeleri düzeltildi.
* Sunucu hataları için otomatik yeniden deneme mekanizması eklendi.

## 1.0 için Değişiklikler

* İlk sürüm.

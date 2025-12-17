Profesyonel Görsel Asistan Dokümantasyonu

# Profesyonel Görsel Asistan

**Profesyonel Görsel Asistan**, NVDA için gelişmiş, çok modlu bir yapay zekâ asistanıdır. Google’ın Gemini modellerini kullanarak akıllı ekran okuma, çeviri, sesli dikte ve belge analiz yetenekleri sunar.

*Bu eklenti, Engelliler Uluslararası Günü onuruna topluluğa sunulmuştur.*

## 1. Kurulum ve Yapılandırma

**NVDA Menüsü > Tercihler > Ayarlar > Profesyonel Görsel Asistan** yolunu izleyin.

* **API Anahtarı:** Gereklidir. [Google AI Studio](https://aistudio.google.com/) üzerinden ücretsiz bir anahtar alabilirsiniz.
* **Model:** `gemini-2.5-flash-lite` (En hızlı) veya standart Flash modellerini seçin.
* **Diller:** Kaynak, Hedef ve Yapay Zekâ Yanıt dillerini ayarlayın.
* **Akıllı takas:** Kaynak metin hedef dille eşleşirse dilleri otomatik olarak değiştirir.

## 2. Genel Kısayollar

Dizüstü bilgisayar düzenleriyle maksimum uyumluluk sağlamak için tüm kısayollar **NVDA + Kontrol + Shift** kullanır.

| Kısayol           | İşlev               | Açıklama                                                                               |
| ----------------- | ------------------- | -------------------------------------------------------------------------------------- |
| NVDA+Ctrl+Shift+T | Akıllı Çevirmen     | Gezgin imleci altındaki metni çevirir. Seçimi önceliklendirir.                         |
| NVDA+Ctrl+Shift+Y | Pano Çevirmeni      | Panodaki içeriği çevirir. **Web tarayıcıları için önerilir**.                          |
| NVDA+Ctrl+Shift+S | Akıllı Dikte        | Konuşmayı metne dönüştürür. Başlatmak için bir kez, durdurup yazmak için tekrar basın. |
| NVDA+Ctrl+Shift+R | Metin İyileştirici  | Özetle, Dilbilgisini Düzelt, Açıkla veya **Özel İstemler** çalıştırır.                 |
| NVDA+Ctrl+Shift+C | CAPTCHA Çözücü      | CAPTCHA’yı otomatik olarak yakalar ve çözer.                                           |
| NVDA+Ctrl+Shift+V | Nesne Görüntüsü     | Dolaşım nesnesini takip eden sohbetle birlikte tanımlar.                                  |
| NVDA+Ctrl+Shift+O | Tam Ekran Görüntüsü | Tüm ekran düzenini ve içeriğini analiz eder.                                           |
| NVDA+Ctrl+Shift+D | Belge Analizi       | PDF/TXT/MD/PY dosyalarıyla sohbet eder.                                                |
| NVDA+Ctrl+Shift+F | Dosya OCR           | Görüntü/PDF dosyasından doğrudan OCR yapar.                                            |
| NVDA+Ctrl+Shift+A | Ses Yazıya Dökme    | MP3/WAV/OGG dosyalarını yazıya döker.                                                  |
| NVDA+Ctrl+Shift+L | Son Çeviri          | Son çeviriyi API kullanmadan tekrar okur.                                              |
| NVDA+Ctrl+Shift+U | Güncellemeleri Denetle | GitHub üzerinden en son sürümü kontrol eder.                                           |
| NVDA+Ctrl+Shift+I | Durumu Seslendirme     | Mevcut durumu seslendirir (ör. “Yükleniyor…”, “Boşta”).                                    |

## 3. Özel İstemler ve Değişkenler

Ayarlar bölümünde komutlar oluşturun: `Ad:İstem Metni` (`|` veya yeni satır ile ayırın).

### Kullanılabilir Değişkenler

| Değişken        | Açıklama                                        | Girdi Türü         |
| --------------- | ----------------------------------------------- | ------------------ |
| `[selection]`   | Seçili olan metin                               | Metin              |
| `[clipboard]`   | Pano içeriği                                    | Metin              |
| `[screen_obj]`  | Dolaşım nesnesinin ekran görüntüsü                 | Görüntü            |
| `[screen_full]` | Tam ekran görüntüsü                             | Görüntü            |
| `[file_ocr]`    | Görüntü/PDF/TIFF seç (varsayılan “Metni çıkar”) | Görüntü, PDF, TIFF |
| `[file_read]`   | Metin belgesi seç                               | TXT, Kod, PDF      |
| `[file_audio]`  | Ses dosyası seç                                 | MP3, WAV, OGG      |

### Örnek Özel İstemler

* **Hızlı OCR:** `My OCR:[file_ocr]`
* **Görüntü Çevir:** `Translate Img:Bu görüntüden metni çıkar ve Farsçaya çevir. [file_ocr]`
* **Ses Analizi:** `Summarize Audio:Bu kaydı dinle ve ana noktaları özetle. [file_audio]`
* **Kod Hata Ayıklayıcı:** `Debug:Bu koddaki hataları bul ve açıkla: [selection]`

**Not:** Tüm yapay zekâ özellikleri için aktif bir internet bağlantısı gereklidir. Çok sayfalı TIFF dosyaları otomatik olarak işlenir.

## 3.0 için Değişiklikler

* **Yeni Diller:** **Farsça** ve **Vietnamca** çeviriler eklendi.
* **Genişletilmiş Yapay Zekâ Modelleri:** Model seçim listesi, ücretsiz ve hız sınırlı (ücretli) modelleri ayırt etmeye yardımcı olmak için (`[Free]`, `[Pro]`, `[Auto]`) önekleriyle yeniden düzenlendi. **Gemini 3.0 Pro** ve **Gemini 2.0 Flash Lite** desteği eklendi.
* **Dikte Kararlılığı:** Akıllı Dikte önemli ölçüde iyileştirildi. 1 saniyeden kısa ses kliplerini yok sayan bir güvenlik kontrolü eklendi; böylece yapay zekâ halüsinasyonları ve boş hatalar önlendi.
* **Dosya İşleme:** İngilizce olmayan isimlere sahip dosyaların yüklenememesine neden olan bir sorun düzeltildi.
* **İstem Optimizasyonu:** Çeviri mantığı geliştirildi ve Görüntü sonuçları daha yapılandırılmış hale getirildi.

## 2.9 için Değişiklikler

* **Fransızca ve Türkçe çeviriler eklendi.**
* **Biçimlendirilmiş Görünüm:** Sohbet diyaloglarında, konuşmayı başlıklar, kalın metinler ve kodlarla birlikte düzgün biçimde görüntülemek için “Biçimlendirilmiş Görünüm” düğmesi eklendi.
* **Markdown Ayarı:** Ayarlara “Sohbette Markdown Temizle” adlı yeni bir seçenek eklendi. Bu seçenek işaretlenmezse, kullanıcılar ham Markdown sözdizimini (`**`, `#` gibi) sohbet penceresinde görebilir.
* **Diyalog Yönetimi:** “Metni İyileştir” veya sohbet pencerelerinin birden fazla kez açılması ya da odağı doğru alamaması sorunu düzeltildi.
* **UX İyileştirmeleri:** Dosya iletişim kutusu başlıkları “Aç” olarak standartlaştırıldı ve daha akıcı bir deneyim için gereksiz sesli duyurular kaldırıldı (ör. “Menü açılıyor…”).

## 2.8 için Değişiklikler

* İtalyanca çeviri eklendi.
* **Durum Bildirimi:** Eklentinin mevcut durumunu (ör. “Yükleniyor…”, “Analiz ediliyor…”) duyurmak için yeni bir komut (NVDA+Control+Shift+I) eklendi.
* **HTML Dışa Aktarma:** Sonuç diyaloglarındaki “İçeriği Kaydet” düğmesi artık çıktıyı başlıklar ve kalın metinler gibi stilleri koruyarak biçimlendirilmiş bir HTML dosyası olarak kaydeder.
* **Ayarlar Arayüzü:** Ayarlar paneli, erişilebilir gruplamalarla iyileştirildi.
* **Yeni Modeller:** gemini-flash-latest ve gemini-flash-lite-latest desteği eklendi.
* **Diller:** Desteklenen dillere Nepalce eklendi.
* **İyileştirme Menüsü Mantığı:** NVDA arayüz dili İngilizce olmadığında “Metni İyileştir” komutlarının çalışmamasına neden olan kritik bir hata düzeltildi.
* **Dikte:** Konuşma girişi olmadığında yanlış metin üretimini önlemek için sessizlik algılama geliştirildi.
* **Güncelleme Ayarları:** “Başlangıçta güncellemeleri kontrol et” seçeneği, Eklenti Mağazası politikalarına uyum için varsayılan olarak devre dışı bırakıldı.
* Kod temizliği yapıldı.

## 2.7 için Değişiklikler

* Proje yapısı, daha iyi standart uyumluluğu için resmi NV Access Eklenti Şablonuna taşındı.
* Yüksek trafik sırasında güvenilirliği sağlamak için HTTP 429 (Hız Sınırı) hataları için otomatik yeniden deneme mantığı uygulandı.
* Daha yüksek doğruluk ve daha iyi “Akıllı Değiş Tokuş” mantığı için çeviri istemleri optimize edildi.
* Rusça çeviri güncellendi.

## 2.6 için Değişiklikler

* Rusça çeviri desteği eklendi (nvda-ru’ya teşekkürler).
* Bağlantı sorunlarıyla ilgili daha açıklayıcı geri bildirim sağlamak için hata mesajları güncellendi.
* Varsayılan hedef dil İngilizce olarak değiştirildi.

## 2.5 için Değişiklikler

* Yerel Dosya OCR Komutu eklendi (NVDA+Control+Shift+F).
* Sonuç diyaloglarına “Sohbeti Kaydet” düğmesi eklendi.
* Tam yerelleştirme desteği (i18n) uygulandı.
* Sesli geri bildirimler NVDA’nın yerel tonlar modülüne taşındı.
* PDF ve ses dosyalarının daha iyi işlenmesi için Gemini Dosya API’sine geçildi.
* Süslü parantez içeren metinler çevrilirken oluşan çökme düzeltildi.

## 2.1.1 için Değişiklikler

* `[file_ocr]` değişkeninin Özel İstemler içinde doğru çalışmamasına neden olan bir sorun düzeltildi.

## 2.1 için Değişiklikler

* NVDA’nın Dizüstü düzeni ve sistem kısayollarıyla çakışmaları önlemek için tüm kısayollar NVDA+Control+Shift olarak standartlaştırıldı.

## 2.0 için Değişiklikler

* Dahili Otomatik Güncelleme sistemi uygulandı.
* Önceden çevrilmiş metinlerin anında alınması için Akıllı Çeviri Önbelleği eklendi.
* Sohbet diyaloglarında sonuçları bağlamsal olarak iyileştirmek için Konuşma Hafızası eklendi.
* Ayrı Pano Çevirisi komutu eklendi (NVDA+Control+Shift+Y).
* Yapay zekâ istemleri, hedef dil çıktısını kesin olarak zorlayacak şekilde optimize edildi.
* Girdi metnindeki özel karakterlerin neden olduğu çökme düzeltildi.

## 1.5 için Değişiklikler

* 20’den fazla yeni dil desteği eklendi.
* Takip soruları için Etkileşimli İyileştirme Diyaloğu uygulandı.
* Yerel Akıllı Dikte özelliği eklendi.
* NVDA’nın Girdi Hareketleri diyaloguna “Vision Assistant” kategorisi eklendi.
* Firefox ve Word gibi belirli uygulamalarda oluşan COMError çökmeleri düzeltildi.
* Sunucu hataları için otomatik yeniden deneme mekanizması eklendi.

## 1.0 için Değişiklikler

* İlk sürüm.


# Prototype Gate, User Feedback Loop & Full-Version End-to-End Build Guide

Bu rehber, tüm rakip araştırması, gerçek hayat konu/marka incelemesi ve raporlama bittikten sonra ürünün **önce hızlı bir çalışan prototiple doğrulanmasını**, ardından kullanıcıdan **geri bildirim ve ekleme fikirleri toplanmasını**, son olarak kullanıcı **"her şey tamam, yap"** dediğinde **tüm uygulama/oyunun baştan sona tam sürüm olarak inşa edilmesini** yönetir.

---

## Kural: Rapor Biter Bitmez Kodlamaya Atlama — 2 Zorunlu Kullanıcı Kapısı Kullan

| Kapı | Ne Zaman? | Ajanın Yapması Gereken |
| :--- | :--- | :--- |
| **Kapı 1: Prototip Onayı (Adım 7)** | Tüm raporlar (`GENEL_TEARDOWN_RAPORU.md`, `DOMAIN_ARASTIRMASI.md`, `FREE_ASSET_VE_KIT_REHBERI.md`, `TASARIM_BLUEPRINT.md`, `PROTOTIP_VE_TAM_SURUM_PLANI.md`) ve `dashboard.html` teslim edildiğinde | Araştırmayı kısaca özetle ve kullanıcıya **çalışan bir prototip oluşturmak isteyip istemediğini sor.** |
| **Kapı 2: Geri Bildirim & Tam Sürüm Onayı (Adım 9)** | Hızlı prototip çalışır hale getirilip kullanıcıya sunulduğunda | Prototipte şu an çalışanları, **tam sürümde eklenecekleri ve tamamlanınca nasıl olacağını** net tabloyla sun; **geri bildirim, değişiklik ve yeni fikir** sor. Kullanıcı **"her şey tamam, yap"** diyene kadar tam sürüm inşasına geçme. |

---

## Adım 7: Araştırma Bitişi -> Prototip Oluşturmayı Sor

Raporlar tamamlandığında kullanıcıya şu yapıda kısa ve net bir soru yönelt:
1. Teslim edilen raporların linkleri (`GENEL_TEARDOWN_RAPORU.md`, `DOMAIN_ARASTIRMASI.md`, `FREE_ASSET_VE_KIT_REHBERI.md`, `TASARIM_BLUEPRINT.md`, `PROTOTIP_VE_TAM_SURUM_PLANI.md`, `dashboard.html`).
2. **Prototip Sorusu:**
   - *"Tüm araştırma ve tasarım planı tamamlandı. Şimdi bu uygulamanın/oyunun nasıl görüneceğini ve çalışacağını hızlıca deneyimleyebileceğin bir **çalışan prototip** oluşturalım mı?"*
   - Kullanıcıya 2-3 net seçenek sun:
     - **Seçenek A (Önerilen):** Seçilen teknolojiyle (`Godot 4` / `Unity` / `Flutter` / `React Native` vb.) hızlı çalışan prototip (Düşük-Orta karmaşıklık).
     - **Seçenek B:** Tarayıcıda tek tıkla açılan hafif etkileşimli web prototipi (hızlı görsel/akış doğrulaması için).
     - **Seçenek C:** Önce tasarım blueprint'inde veya özellik listesinde revizyon yapalım.

---

## Adım 8: Hızlı Çalışan Prototip İnşası ("Kısaca Uygulama Nasıl Olacak?")

Kullanıcı onay verdiğinde, `PROTOTIP_VE_TAM_SURUM_PLANI.md` dosyasına sadık kalarak **odaklı, temiz, hatasız çalışan bir prototip** üret:

### Oyun Prototipi (Game Mode) İçin Kapsam
- **Başlık / Giriş Ekranı:** Oyun adı, blueprint HEX paleti ve tek tıkla `Oyna` butonu.
- **1 Oynanabilir Çekirdek Döngü Sahnesi:** Temel kontrol (dokun/sürükle), ana mekanik (ör. kapılardan geçme, katman dizme, müşteri siparişi) ve `DOMAIN_ARASTIRMASI.md` kaynaklı temel gerçek hayat kuralı.
- **Temel HUD + Sonuç Ekranı:** Skor/ilerleme göstergesi, temel doğru/yanlış tepki ve `Kazandın / Tekrar Oyna` döngüsü.
- **Kapsam Dışı (Tam Sürüme Bırakılanlar):** 20+ seviye, ağır final 3D/2D sanat, tüm ses efektleri, reklam/IAP SDK entegrasyonu, bulut kayıt, canlı etkinlikler.

### Genel Uygulama Prototipi (App Mode) İçin Kapsam
- **Kısa Karşılama / Onboarding:** Değer vaadi ve ilk aksiyona hızlı geçiş.
- **Ana Ekran + Navigasyon İskeleti:** Blueprint HEX tasarım sistemi, alt tab bar / navigasyon ve ana CTA.
- **1 Çalışan Çekirdek Kullanıcı Akışı:** Gerçek yerel state ile ana görevin/takibin/hesaplamanın baştan sona çalışması.
- **Sonuç + Paywall Maketi:** Değer anı özet ekranı ve tıklanabilir paywall önizlemesi (gerçek ödeme olmadan).
- **Kapsam Dışı (Tam Sürüme Bırakılanlar):** Gerçek backend/bulut senkronizasyonu, canlı abonelik/ödeme SDK'sı, push bildirim altyapısı, tüm ayar/profil alt ekranları.

### Prototip Doğrulama Kuralı
- Prototipi mutlaka derle veya smoke-test ile çalıştır (hata/çökme olmadığından emin ol).
- `PROTOTIP_VE_TAM_SURUM_PLANI.md` içindeki `<!-- AGENT_PROTOTYPE_STATUS_START -->` alanını klasör yolu, tek komutluk çalıştırma talimatı ve çalışan özelliklerle güncelle.

---

## Adım 9: Tam Sürüm Yol Haritası Sunumu & Geri Bildirim Kapısı (ZORUNLU)

Prototip hazır olduğunda kullanıcıya şu 4 bölümü tek, taranabilir mesajda sun ve **onay bekle**:

1. **Prototipte Şu An Neler Çalışıyor & Nasıl Açarsın?**
   - Çalıştırma komutu ve prototipte denenebilecek 3-5 somut özellik.
2. **Tamamlanınca Nasıl Olacak? (Tam Sürümde Eklenecekler):**
   - `PROTOTIP_VE_TAM_SURUM_PLANI.md` tablosuna dayanarak tam sürümde eklenecek ana başlıkları özetle:
     - Tam seviye/içerik derinliği ve tüm gerçek hayat domain kuralları (`DOMAIN_ARASTIRMASI.md` + `EV-REF-XX`)
     - Parlatılmış görsel sanat, ücretsiz UI/3D/2D/font kitleri (`EV-KIT-XX`), animasyonlar ve shader/juice
     - Foley ses efektleri (SFX) ve müzik katmanı
     - Monetizasyon (Rewarded/Interstitial/IAP veya Paywall/Abonelik akışı)
     - Retention & Kalıcılık (Save/Load, günlük ödül/görev/streak, meta-progression)
     - QA, performans/Safe-Area kontrolleri ve mağaza yayın hazırlığı
3. **Geri Bildirim Soruları:**
   - *"Prototipte beğendiğin veya değişmesini istediğin mekanik, ekran, renk veya kontrol hissi var mı?"*
   - *"Tam sürüm listesine eklemek istediğin yeni fikirlerin veya çıkarmak istediğin özellikler var mı?"*
   - *"Önce prototipte hızlı bir düzeltme turu yapalım mı, yoksa **'her şey tamam, tam sürümü baştan sona yap'** dediğinde tam üretime geçeyim mi?"*
4. **Revizyon Döngüsü:**
   - Kullanıcı ekleme veya değişiklik isterse bunları `PROTOTIP_VE_TAM_SURUM_PLANI.md` (`<!-- AGENT_USER_FEEDBACK_START -->`) ve `TASARIM_BLUEPRINT.md` dosyalarına işle; isterse prototipi güncelleyip tekrar onay al.

---

## Adım 10: Tam Sürüm Uçtan Uca İnşa (Kullanıcı "Her Şey Tamam, Yap" Dediğinde)

Kullanıcı kesin onayı verdiğinde (`"her şey tamam, yap"`, `"tam sürümü geliştir"`, `"başla"` vb.):

1. **Tam Mimari Kurulumu:** Seçilen teknolojinin en iyi pratiklerine uygun modüler klasör yapısı, tasarım token'ları ve veri odaklı içerik dosyaları (Godot `.tres`, Unity `ScriptableObject`, Flutter feature-first vb.).
2. **Tüm Özelliklerin Uçtan Uca İnşası:**
   - Onaylanan prototipi temel alarak veya temiz tam mimariye taşıyarak tüm ekranları, seviyeleri/akışları, gerçek hayat domain kurallarını, meta-progression / retention sistemlerini, kalıcı kayıt (Save/Load) yapısını ve monetizasyon/paywall akışını eksiksiz kodla.
   - `FREE_ASSET_VE_KIT_REHBERI.md` (`EV-KIT-XX`) ve `DOMAIN_ARASTIRMASI.md` (`EV-REF-XX`) ilkelerine göre özgün, tutarlı ve telif haklarına saygılı görsel + ses katmanını entegre et.
3. **Derleme, Test & Görsel QA Doğrulaması:**
   - Otomatik birim/akış testlerini çalıştır, proje derlemesini doğrula ve mümkünse uygulama/oyun ekran görüntülerini alarak `read_file` ile görsel QA kontrolü yap.
   - `PROTOTIP_VE_TAM_SURUM_PLANI.md` kontrol listesini işaretle ve kullanıcıya tam sürüm özetini, çalıştırma komutlarını ve doğrulama sonuçlarını teslim et.

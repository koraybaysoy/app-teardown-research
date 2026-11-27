# Mobile App Teardown Rubric (Non-Game Apps)

Genel mobil uygulama (`app`: SaaS, verimlilik, sağlık/fitness, finans, sosyal, eğitim, yapay zeka aracı) modundaki her rakip için bu 7 ekseni kontrol et:

## 1. UI/UX Dizilimi & Bilgi Mimarisi (IA)
- **Navigasyon Modeli:** Alt tab bar (kaç sekme, hangi ikon/etiketler?), üst filtreler, FAB (Floating Action Button) veya kart tabanlı akış.
- **Tek El Kullanımı & Safe-Area:** Birincil aksiyonlar alt %40 başparmak bölgesinde mi? Başlık ve aksiyon butonları üst safe-area ile uyumlu mu?
- **Görsel Yoğunluk & Boşluk:** Kart yapısı, tipografi hiyerarşisi (başlık/alt metin/metrik kontrastı), boş durumlar (empty states) kullanıcıyı eyleme yönlendiriyor mu yoksa ölü ekran mı bırakıyor?

## 2. Onboarding, Aktivasyon & Temel Kullanıcı Akışı
- **Minimum Path to Value (MPTV):** Uygulama açılışından kullanıcının ilk gerçek değerini ("aha moment") yaşamasına kadar kaç ekran / kaç saniye geçiyor?
- **Kişiselleştirme & Sürtünme Dengesi:** Kısa hedef/rol anketi (Endowed Progress + kişiselleştirme hissi) kullanılıyor mu? Hesap oluşturma (signup) değerden önce mi sonra mı isteniyor?
- **İzin İsteme Zamanlaması:** Bildirim, kamera veya sağlık izni bağlam anlatılarak (pre-prompt) mı, açılır açılmaz soğuk biçimde mi soruluyor?
- **Temel Kullanım Döngüsü:** Kullanıcının her gün/hafta tekrarladığı ana iş akışı kaç adımda tamamlanıyor?

## 3. Renk Paleti, Marka Kimliği & Tasarım Sistemi
- **Tema Yaklaşımı:** Açık mod (clean light), koyu mod (dark pro), yüksek kontrastlı tüketici tonları veya sakin wellness paleti.
- **Vurgu & CTA Rengi:** Birincil aksiyon ve yükseltme (Upgrade/Pro) butonları `color_palette_card.png` içindeki hangi HEX tonuyla ayrışıyor?
- **Erişilebilirlik & Okunabilirlik:** Metin/arka plan kontrastı ve durum renkleri (başarı, uyarı, hata, aktif sekme).

## 4. Göze Çarpan Kısımlar (UX Delights & Conversion Hooks)
- Kullanıcıyı şaşırtan mikro etkileşimler (haptic/animasyon geri bildirimi, anlık önizleme, hazır şablonlar, AI destekli otomatik doldurma, widget'lar).
- Mağaza ekran görüntülerinde öne çıkarılan ana değer vaadi uygulama içinde gerçekten ilk oturumda teslim ediliyor mu?

## 5. Satın Alım (Paywall), Fiyatlandırma & Reklam Dizilimi
- **Paywall Zamanlaması:** Onboarding sonu hard/soft paywall mı, "aha anı" sonrası özellik kilidi (feature gate) mi, kullanım limiti (usage limit) mi?
- **Paywall Ekran Anatomisi:**
  - Değer odaklı başlık ve görsel önizleme ("Show, don't just tell")
  - Plan çıpalama: Yıllık plan varsayılan seçili mi? Haftalık/aylık fiyat farkı ve tasarruf rozeti nasıl gösteriliyor?
  - Ücretsiz deneme (3/7/14 gün trial) + deneme takvimi zaman çizelgesi ("Bugün 0 TL -> 5. gün hatırlatma") kullanılıyor mu?
  - Sosyal kanıt (yıldız puanı, kullanıcı sayısı, yorum alıntısı) ve kapatma/devam etme seçeneği (dark pattern var mı?)
- **Reklam Kullanımı (Varsa):** Ücretsiz katmanda banner/interstitial/rewarded kullanımı kullanıcı deneyimini bozuyor mu?

## 6. Kullanıcıyı Elde Tutma Stratejisi (Retention & Churn Prevention)
- **Alışkanlık Döngüsü (Hook Model):** Dış tetikleyici (akıllı bildirim, widget) -> Kolay aksiyon -> Değişken/kişisel ödül (haftalık özet, içgörü) -> Yatırım (kayıtlı veri, streak, kişiselleşmiş içerik).
- **Endowed Progress & Streak Mekaniği:** İlerleme yüzdesi, seri koruma (streak freeze), kilometre taşı kutlamaları.
- **Churn & İptal Sinyalleri:** Kullanıcı yorumlarında (`[EV-REV-XX]`) en çok hangi sebeplerle abonelik iptal ediliyor veya uygulama siliniyor? (Beklenmedik yenileme, pahalı abonelik, senkronizasyon hatası, eksik temel özellik.)

## 7. Gelir Stratejisi & Büyüme Döngüsü
- Gelir modeli: Freemium Subscription, Hard-Paywall Trial, Hybrid (Ads + Sub), Tek Seferlik Pro veya Kullanım Bazlı Kredi.
- Paylaşım/viral büyüme kancası var mı? (Paylaşılabilir özet kartı, davet linki, ekip/ortak kullanım.)
- Web kanıtlarından (`[EV-WEB-XX]`) gelen tahmini ARR, indirme hacmi veya büyüme stratejisi bulguları.

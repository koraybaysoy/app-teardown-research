# Mobile Game Teardown Rubric

Oyun (`game`) modundaki her rakip için kare kare inceleme ve web kanıtı analizinde bu 7 ekseni kontrol et:

## 1. UI/UX Dizilimi & HUD Mimarisi
- **Ekran Yönü & Kavrama:** Dikey tek el (portrait one-thumb) mi, yatay çift başparmak (landscape dual-thumb) mı?
- **Safe-Area & Çentik Koruması:** Üst HUD (para birimi, skor, seviye ilerleme çubuğu, ayarlar) çentik/Dynamic Island altından güvenli boşlukla mı başlıyor?
- **Görsel Hiyerarşi & Ekran Temizliği:** Oynanış anında ekranda kaç aktif UI elemanı var? Hypercasual'da oynanış HUD'u minimal (genelde 2-3 eleman), hybrid/midcore'da daha katmanlıdır.
- **Menü & Ekran Yığını (Screen Stack):** Ana lobi -> Oynanış -> Bölüm Sonu (Win/Lose) -> Ödül Çarpanı -> Mağaza geçişleri kaç dokunuş sürüyor?

## 2. Oynanış Mekaniği, Core Loop & Game Feel ("Juice")
- **İlk 5-10 Saniye (Zero-Friction Entry):** Oyun açılır açılmaz oynanışa mı sokuyor yoksa uzun menü/kayıt ekranı mı çıkarıyor?
- **Çekirdek Döngü (Core Loop):** `Aksiyon -> Anlık Geri Bildirim -> Ödül -> Yükseltme/Yeni Bölüm` döngüsü tek turda kaç saniye sürüyor?
- **Kontrol Şeması:** Sürükle-bırak (swerve), tek dokunuş (tap/hold), sanal joystick veya grid dokunma.
- **Game Feel & Juice:** Karelerde görünen görsel geri bildirimler neler? (Hasar/puan pop-up sayıları, parçacık efektleri, kamera sarsıntısı, kombo barı, karakter squash-and-stretch, renk parlaması.)
- **Zorluk & İlerleme Eğrisi:** İlk 3 bölümde kazanma kolaylığı, yeni mekanik tanıtım hızı ve başarısızlık anındaki duygu tasarımı.

## 3. Renk Paleti, Kontrast & Sanat Yönü
- **Figür-Zemin Ayrımı (Figure-Ground Separation):** Oyuncu/hedef objeler arka plandan renk sıcaklığı veya parlaklık kontrastıyla nasıl ayrılıyor? (Örn. düşük doygunluklu pastel zemin + yüksek doygunluklu sıcak oyuncu/CTA.)
- **Tehlike vs Ödül Kodlaması:** Engel/hasar (genelde kırmızı/koyu mor), ödül/para (altın/sarı/parlak yeşil), güvenli yol/UI yüzeyi.
- **HEX Kanıtı:** `color_palette_card.png` ve `teardown_report.md` HEX tablosundaki baskın tonların oyundaki rolünü açıkla.

## 4. Göze Çarpan Kısımlar (Standout Hooks & Wow Moments)
- Kullanıcıyı ilk 30 saniyede yakalayan tatmin edici an (satisfying physics, zincirleme patlama, devasa büyüme, risk-ödül kapısı).
- Sosyal medya / UA reklamlarında kolayca gösterilebilen "izlerken bile anlaşılır" görsel kanca.

## 5. Satın Alım (IAP) & Reklam Dizilimi (IAA)
- **Reklam Kadansı & Yerleşimi:**
  - **Banner:** Oynanış sırasında alt/üst sabit bant var mı? Oyun alanını veya parmak bölgesini engelliyor mu?
  - **Interstitial (Zorunlu Geçiş):** İlk kaçıncı dakikada/bölümde başlıyor? Bölüm sonu mu, yeniden deneme anında mı? Yorumlarda reklam sıklığı şikayeti (`excessive_ads`) yüzde kaç?
  - **Rewarded Video (Ödüllü Reklam):** Hangi değer anlarında sunuluyor? (2x-5x ödül çarpanı, ekstra can/devam etme, ücretsiz skin/boost, sandık açma.)
- **IAP & Fiyat Merdiveni:**
  - "Remove Ads" / "No Ads" paketi var mı ve kaç dolar?
  - Başlangıç paketi (Starter Pack), para birimi paketleri (`$0.99` -> `$99.99`), Battle/Season Pass veya VIP abonelik yapısı.

## 6. Kullanıcıyı Elde Tutma Stratejisi (D1 / D7 / D30)
- **FTUE / Onboarding:** Oynayarak öğretme ("Do, don't show") mi, zorunlu metin balonu mu? İlk zafer kaçıncı saniyede geliyor?
- **Kısa Vadeli (D1):** Seviye ilerleme barı, kilitli skin/karakter silüetleri, hızlı açılan ilk yükseltmeler.
- **Orta Vadeli (D7):** Günlük giriş ödülleri (7 günlük takvim), günlük görevler, dönen çark / sandık zamanlayıcıları.
- **Uzun Vadeli (D30):** Meta-progression (üs/oda dekore etme, koleksiyon albümü, yetenek ağacı), haftalık lig/leaderboard, sınırlı süreli Live-Ops etkinlikleri.

## 7. Gelir Stratejisi & Ekonomik Denge
- Gelir ağırlığı tahmini: Saf IAA (Hypercasual) vs Hibrit IAA+IAP (Hybridcasual) vs Ağır IAP/Live-Ops (Midcore).
- Çift para birimi (Soft Currency + Hard Currency) veya enerji/can sınırlaması kullanılıyor mu?
- Web kanıtlarından (`[EV-WEB-XX]`) gelen tahmini indirme/gelir/eCPM veya yayıncı stratejisi notları.

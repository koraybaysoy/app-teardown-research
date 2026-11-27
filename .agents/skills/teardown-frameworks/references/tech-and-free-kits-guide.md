# Technology Selection, Domain Decomposition & Free Asset Kit Guide

Bu rehber, kullanıcının ürün fikrini **doğru teknoloji seçimi**, **mekanik vs domain ayrımı** ve **ücretsiz üretim kitleri (UI/UX, 3D/2D model, SFX/müzik, font, SDK)** ile doğrudan geliştirilebilir hale getirmek için kullanılır.

## 1. Mekanik Ekseni vs Domain (Tema) Ekseni Ayrımı

Yeni bir ürün tasarlarken yapılan en büyük hata, rakipleri yalnızca dar temaya göre aramaktır.

- **Örnek 1 (Oyun):** *"Kapılardan geçtiğin hypercasual yemek yapma / hamburger dizme oyunu"*
  - **Yanlış rakip araması:** Sadece "yemek tarifi" veya "restoran simülatörü" aramak.
  - **Doğru Rakip Benchmark Ekseni (Mekanik):** `hypercasual runner stack gate game` (*Coffee Stack*, *Sandwich Runner*, *Tall Man Run*, *Mob Control*, *Count Masters*) -> HUD, kamera açısı, kapı çarpma matematiği, reklam kadansı, başparmak kontrolü buradan öğrenilir!
  - **Doğru Domain Araştırması Ekseni (Gerçek Hayat Konusu + Ünlü Marka Referansları):**
    1. **Nedir & Gerçek Hayat Karşılığı:** Hamburger nedir, gerçek dünyada ne tür bir tüketim ve sunum deneyimine denk gelir?
    2. **Nasıl Yapılır (Süreç):** Köfte mühürleme, peynir eritme, ekmek kızartma, soslama ve istifleme sırası.
    3. **Katmanlar & Anatomi:** Alt ekmek -> sos -> marul bariyeri -> ızgara köfte -> erimiş cheddar -> domates -> turşu -> soğan -> üst susamlı ekmek.
    4. **Ünlü Markalar Görsel İncelemesi (`EV-REF-XX`):** *McDonald's Big Mac*, *Burger King Whopper*, *Shake Shack ShackBurger*, *Five Guys*, *In-N-Out Double-Double* fotoğrafları (`assets/domain_references/domain_reference_sheet.png`) üzerinden katman yüksekliği, renk kontrastı, ekmek parıltısı ve okunabilirlik incelenir (marka logoları kopyalanmadan özgün stilize tasarım üretilir).

- **Örnek 2 (Genel Uygulama):** *"Oyunlaştırılmış su içme ve günlük alışkanlık takip uygulaması"*
  - **Rakip Benchmark Ekseni:** `habit tracker routine app` (*Habitica*, *Fabulous*, *Streaks*, *Waterllama*) -> Onboarding, paywall zamanlaması, tab bar IA ve bildirim retention'ı buradan öğrenilir.
  - **Domain Araştırması Ekseni:** *"Alışkanlık döngüsü nedir (ipucu-istek-tepki-ödül), gerçek hayatta bullet journal / duvar takvimi / Seinfeld zinciri nasıl işler, BJ Fogg ve James Clear yöntemleri nelerdir?"* -> Uygulamanın davranışsal kuralları ve gerçek hayat metaforları buradan öğrenilir.

## 2. Teknoloji Öneri Matrisi (Kullanıcıya Sunulacak Seçenekler)

### Mobil Oyunlar
| Teknoloji | Karmaşıklık | Lisans / Maliyet | En Uygun Senaryo | Temel Asset Formatları |
| :--- | :--- | :--- | :--- | :--- |
| **Godot 4 (GDScript / C#)** | **Low** | %100 Ücretsiz (MIT, sıfır telif) | Hypercasual, hybridcasual, stilize 2D/3D, hızlı prototip, küçük APK/IPA | `.glb`/`.gltf`, `.png`/`.svg`, `.ogg`/`.wav`, `.ttf` |
| **Unity 6 LTS (C#)** | **Medium** | $200K gelire kadar ücretsiz | Yayıncı/medyasyon ağırlıklı (AppLovin MAX, LevelPlay) ticari mobil oyunlar | `.fbx`/`.glb`, `.png`, `.wav`/`.ogg`, `.ttf` |
| **Phaser 4 / Three.js (Web)** | **Low** | %100 Ücretsiz (MIT) | Playable ads, web portalları (Poki/CrazyGames), hafif Capacitor mobil sarma | `.glb`, `.png`/`.webp`, `.mp3`/`.ogg` |

### Genel Mobil Uygulamalar
| Teknoloji | Karmaşıklık | Lisans / Maliyet | En Uygun Senaryo |
| :--- | :--- | :--- | :--- |
| **Flutter (Dart)** | **Low** | %100 Ücretsiz (BSD) | Zengin özel UI/animasyonlu iOS + Android tüketici/SaaS uygulamaları |
| **React Native + Expo (TS)** | **Low** | %100 Ücretsiz (MIT) | Web/React geçmişi olan ekipler, hızlı OTA güncelleme ve Superwall/RevenueCat paywall akışı |
| **Native (SwiftUI + Kotlin)** | **High** | Ücretsiz SDK | Ağır OS entegrasyonu (Widgets, HealthKit, Live Activities, StoreKit 2) |

## 3. Ücretsiz Kit & Lisans Doğrulama Kuralları

Rapora eklenen her ücretsiz UI/UX kiti, 3D/2D model paketi, ses/SFX kiti ve font için şu 4 alan zorunludur:
1. **Doğrudan Kaynak URL'si** (tıklanabilir)
2. **Açık Lisans Bilgisi:**
   - **CC0 1.0 / Public Domain:** En güvenli; atıf gerekmeden ticari kullanıma açık (Kenney.nl, Quaternius, KayKit, Freesound CC0 filtresi).
   - **MIT / Apache 2.0 / BSD / SIL OFL:** Ticari kullanıma açık; lisans metni korunur (Google Fonts, Lucide/Phosphor, Godot eklentileri).
   - **CC BY 3.0 / 4.0:** Ticari kullanıma açık ancak uygulama içi "Credits / Hakkında" ekranında atıf zorunludur (Game-Icons.net, bazı Poly Pizza modelleri).
   - **Royalty-Free (Mixkit vb.):** Ücretsiz ticari kullanım şartı kontrol edilmeli; yeniden dağıtım yasaktır.
3. **Seçilen Teknolojiye Format Uyumu** (Örn. Godot 4 için `.glb`, `.ogg`, `.png`, `.ttf`).
4. **Asset-to-Feature Eşleştirmesi:** Kitin soyut olarak adı değil, oyunda/uygulamada **tam olarak nerede** kullanılacağı yazılır (Örn. *Kenney Food Kit `burger-patty.glb` -> ızgara kapısından geçince eklenen köfte katmanı; Kenney Interface `confirmation_002.ogg` -> yeşil `+2` kapısından geçiş sesi*).

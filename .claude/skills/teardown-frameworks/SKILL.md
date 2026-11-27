---
name: teardown-frameworks
description: >
  Structured product teardown rubrics for mobile games and non-game apps covering UI/UX layout,
  core loop and game feel, HEX color systems, standout hooks, IAP/paywall and ad placement
  architecture, D1/D7/D30 retention strategy, revenue models, tech stack selection, free CC0/MIT
  UI/model/SFX kit curation, and zero-AI-slop evidence-cited analytical writing.
---

# Product, Domain & Tech Blueprint Analysis Frameworks

Bu skill, `app-teardown` akışı sırasında toplanan görsel kareleri, renk paletlerini, mağaza verilerini, domain kaynaklarını ve ücretsiz asset kitlerini **kıdemli ürün/oyun tasarımcısı ve teknik mimar** gözüyle değerlendirmek için standart analiz çerçevelerini sunar.

## Hangi Rubriği Okumalısın?

1. **Oyun analiz ediyorsan (`product_mode == "game"`):**
   `references/game-teardown-rubric.md` — Core Loop, Controls & Game Feel/Juice, HUD & Safe-Area UI/UX, Hypercasual/Hybridcasual/Midcore Monetization & Ad Cadence, Meta-Progression & Live-Ops Retention.
2. **Genel mobil uygulama analiz ediyorsan (`product_mode == "app"`):**
   `references/app-teardown-rubric.md` — Onboarding & Minimum Path to Value, Activation/Aha Moment, Information Architecture & Navigation, Paywall Timing & Pricing Anchoring, Habit Loops & Churn Prevention.
3. **Teknoloji seçimi, gerçek hayat domain / ünlü marka araştırması ve ücretsiz UI/UX + model + ses kitleri için:**
   `references/tech-and-free-kits-guide.md` — Motor/framework karar matrisi (Godot, Unity, Phaser, Flutter, React Native, Native), 4 sütunlu gerçek hayat konu ve ünlü marka görsel inceleme çerçevesi, mekanik vs tema ayrımı, CC0/MIT/SIL OFL lisans kontrolü ve asset-to-feature eşleştirme şablonu.
4. **Her raporda zorunlu yazım & kanıt kuralları:**
   `references/evidence-and-writing-rules.md` — Kanıt ID zorunluluğu (`[EV-FRAME-XX]`, `[EV-DOM-XX]`, `[EV-REF-XX]`, `[EV-KIT-XX]`, `[EV-WEB-XX]`), telif/marka referans sınırı, hipotez vs gözlem ayrımı, sıfır AI-slop ve sıfır em-dash kuralı.
5. **Araştırma sonrası prototip onay kapısı, kullanıcı geri bildirimi ve tam sürüm inşa akışı için:**
   `references/prototype-to-full-build-guide.md` — Rapor sonrası prototip sorma kapısı (Adım 7), hızlı çalışan prototip kapsamı (Adım 8), tam sürüm fark tablosu ve geri bildirim kapısı (Adım 9), kullanıcı "her şey tamam, yap" dediğinde tam sürüm uçtan uca geliştirme kuralları (Adım 10).

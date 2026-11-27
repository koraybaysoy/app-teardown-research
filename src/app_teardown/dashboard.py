"""Secure, zero-CDN, XSS-safe local HTML Visual Product, Domain & Free Kits Teardown Studio."""

from __future__ import annotations

import json
from pathlib import Path

from .models import TeardownRun
from .utils import safe_join


def _safe_json_for_script_tag(obj: object) -> str:
    """Serialize JSON safely for embedding inside <script type='application/json'>."""
    raw = json.dumps(obj, ensure_ascii=False)
    return (
        raw.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


_DASHBOARD_CSS = """/* App Teardown & Idea-to-Build Visual Studio — Self-contained stylesheet */
:root {
  --bg: #0b0f17;
  --surface: #131a26;
  --surface-2: #1c2536;
  --border: #2a364d;
  --text: #e6edf3;
  --muted: #94a3b8;
  --accent: #38bdf8;
  --violet: #a78bfa;
  --green: #22c55e;
  --amber: #f59e0b;
  --red: #ef4444;
  --gp: #34d399;
  --ios: #c084fc;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
}
.container { max-width: 1480px; margin: 0 auto; padding: 24px; }
header.hero {
  background: linear-gradient(135deg, #131a26 0%, #1d283d 100%);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 24px 28px;
  margin-bottom: 20px;
}
.hero h1 { margin: 0 0 6px 0; font-size: 1.65rem; }
.hero .meta { color: var(--muted); font-size: 0.92rem; display: flex; flex-wrap: wrap; gap: 16px; }
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
  gap: 14px;
  margin-bottom: 22px;
}
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 18px;
}
.kpi-label { font-size: 0.78rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
.kpi-val { font-size: 1.38rem; font-weight: 700; margin-top: 4px; color: var(--accent); }
.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px 20px;
  margin-bottom: 20px;
}
.panel h2 { margin: 0 0 12px 0; font-size: 1.12rem; }
.hidden { display: none; }
.kits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 12px;
}
.kit-card {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.kit-card a { color: var(--accent); text-decoration: none; font-weight: 600; font-size: 0.94rem; }
.kit-card a:hover { text-decoration: underline; }
.palette-wall { display: flex; flex-wrap: wrap; gap: 16px; }
.wall-tile {
  width: 150px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px;
  text-align: center;
}
.wall-tile img {
  width: 68px;
  height: 68px;
  border-radius: 16px;
  object-fit: cover;
  display: block;
  margin: 0 auto 8px auto;
  cursor: pointer;
}
.wall-tile .name {
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.swatches { display: flex; justify-content: center; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.swatch {
  width: 18px;
  height: 18px;
  border-radius: 5px;
  border: 1px solid rgba(255,255,255,0.25);
  display: inline-block;
}
.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 18px;
  align-items: center;
}
.controls select, .controls input {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 0.9rem;
}
.controls input { min-width: 240px; }
.app-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 22px;
}
.app-head {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
  padding-bottom: 14px;
  margin-bottom: 16px;
}
.app-identity { display: flex; gap: 14px; align-items: center; flex: 1; min-width: 260px; }
.app-identity img {
  width: 68px;
  height: 68px;
  border-radius: 16px;
  object-fit: cover;
  cursor: pointer;
}
.app-title { font-size: 1.22rem; font-weight: 700; margin: 0; }
.app-sub { color: var(--muted); font-size: 0.86rem; margin: 2px 0 4px 0; }
.badges { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.badge {
  font-size: 0.74rem;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 999px;
  background: var(--surface-2);
  border: 1px solid var(--border);
}
.badge.gp { color: var(--gp); border-color: rgba(52,211,153,0.4); }
.badge.ios { color: var(--ios); border-color: rgba(192,132,252,0.4); }
.badge.mode { color: var(--accent); border-color: rgba(56,189,248,0.4); }
.badge.warn { color: var(--amber); border-color: rgba(245,158,11,0.4); }
.badge.good { color: var(--green); border-color: rgba(34,197,94,0.4); }
.score-pill {
  font-size: 1.15rem;
  font-weight: 800;
  padding: 10px 16px;
  border-radius: 12px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  text-align: center;
  min-width: 122px;
  color: var(--accent);
}
.section-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
  margin: 16px 0 8px 0;
}
.palette-card-img {
  max-width: 680px;
  width: 100%;
  border-radius: 10px;
  border: 1px solid var(--border);
  cursor: pointer;
}
.video-row { display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-start; }
.video-row video {
  max-height: 300px;
  max-width: 520px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: #000;
}
.video-row img.storyboard {
  max-height: 300px;
  border-radius: 10px;
  border: 1px solid var(--border);
  cursor: pointer;
}
.filmstrip {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 10px;
}
.frame-tile {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 6px;
  flex-shrink: 0;
  width: 164px;
}
.frame-tile img {
  width: 100%;
  height: 128px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  display: block;
}
.frame-meta {
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 5px;
  display: flex;
  justify-content: space-between;
}
.gallery { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 8px; }
.gallery img {
  height: 220px;
  width: auto;
  border-radius: 10px;
  border: 1px solid var(--border);
  cursor: pointer;
  flex-shrink: 0;
}
.web-list { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
.web-item {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 0.85rem;
}
.web-item a { color: var(--accent); text-decoration: none; font-weight: 600; }
.web-item a:hover { text-decoration: underline; }
.web-snippet { color: var(--muted); font-size: 0.8rem; margin-top: 4px; }
.links-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
.links-row a {
  color: var(--accent);
  text-decoration: none;
  font-size: 0.85rem;
  padding: 6px 11px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--surface-2);
}
.links-row a:hover { border-color: var(--accent); }
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.9);
  display: none;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 24px;
}
.lightbox.open { display: flex; }
.lightbox img { max-width: 94vw; max-height: 86vh; border-radius: 10px; }
.lightbox-caption { color: #e2e8f0; margin-top: 10px; font-size: 0.92rem; }
"""

_DASHBOARD_JS = """/* App Teardown & Idea-to-Build Visual Studio — Safe DOM renderer (createElement + textContent only) */
(function () {
  "use strict";

  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "class") {
          node.className = attrs[k];
        } else if (k === "style" && typeof attrs[k] === "object") {
          Object.assign(node.style, attrs[k]);
        } else if (attrs[k] !== undefined && attrs[k] !== null) {
          node.setAttribute(k, String(attrs[k]));
        }
      });
    }
    if (text !== undefined && text !== null) {
      node.textContent = String(text);
    }
    return node;
  }

  function safeRelUrl(path) {
    if (!path || typeof path !== "string") return "";
    if (path.indexOf("..") !== -1 || /^[a-zA-Z]+:/.test(path)) return "";
    return path;
  }

  function safeExternalUrl(url) {
    if (!url || typeof url !== "string") return "";
    if (url.indexOf("https://") === 0 || url.indexOf("http://") === 0) return url;
    return "";
  }

  var dataNode = document.getElementById("teardown-data");
  if (!dataNode) return;
  var runData = JSON.parse(dataNode.textContent || "{}");
  var comps = Array.isArray(runData.competitors) ? runData.competitors : [];
  var ca = runData.cross_analysis || {};
  var brief = runData.idea_brief || null;
  var domainEv = Array.isArray(runData.domain_evidence) ? runData.domain_evidence : [];
  var freeKits = Array.isArray(runData.free_asset_kits) ? runData.free_asset_kits : [];

  // Lightbox
  var lightbox = document.getElementById("lightbox");
  var lightboxImg = document.getElementById("lightbox-img");
  var lightboxCaption = document.getElementById("lightbox-caption");
  function openLightbox(src, caption) {
    if (!src) return;
    lightboxImg.setAttribute("src", src);
    lightboxImg.setAttribute("alt", caption || "Preview");
    lightboxCaption.textContent = caption || "";
    lightbox.classList.add("open");
  }
  lightbox.addEventListener("click", function () {
    lightbox.classList.remove("open");
    lightboxImg.removeAttribute("src");
  });

  // Hero
  document.getElementById("hero-title").textContent =
    "Ürün & Oynanış Teardown Stüdyosu — " + (runData.campaign_name || runData.query || "Teardown");
  var heroMeta = document.getElementById("hero-meta");
  [
    "Mekanik Sorgusu: " + (runData.query || "Direct Targets"),
    "Teknoloji: " + (brief && brief.selected_tech ? brief.selected_tech.toUpperCase() : "Otomatik"),
    "Bölge/Dil: " + String(runData.country || "").toUpperCase() + " / " + (runData.lang || ""),
    "Baskın Mod: " + String(ca.dominant_mode || runData.product_mode || "auto").toUpperCase()
  ].forEach(function (t) {
    heroMeta.appendChild(el("span", null, t));
  });

  // KPI Grid
  var kpiGrid = document.getElementById("kpi-grid");
  [
    ["Analiz Edilen Rakip", String(ca.total_competitors || comps.length)],
    ["Toplam Video Karesi", String(ca.total_gameplay_frames || 0) + " kare"],
    ["Web + Domain Kanıtı", String((ca.total_web_evidence_sources || 0) + domainEv.length) + " kaynak"],
    ["Ücretsiz Asset Kiti", String(freeKits.length) + " paket"],
    ["Baskın Gelir Modeli", String(ca.dominant_monetization || "-")],
    ["Ort. Kanıt Skoru", String(ca.avg_evidence_score || 0) + " / 100"]
  ].forEach(function (item) {
    var c = el("div", { class: "kpi-card" });
    c.appendChild(el("div", { class: "kpi-label" }, item[0]));
    c.appendChild(el("div", { class: "kpi-val" }, item[1]));
    kpiGrid.appendChild(c);
  });

  // Idea & Tech Brief Panel
  var ideaPanel = document.getElementById("idea-panel");
  var ideaBody = document.getElementById("idea-body");
  if (brief && (brief.raw_idea || brief.selected_tech)) {
    ideaPanel.classList.remove("hidden");
    if (brief.raw_idea) ideaBody.appendChild(el("div", { class: "app-sub" }, "Fikir: " + brief.raw_idea));
    var bRow = el("div", { class: "badges" });
    if (brief.selected_tech) bRow.appendChild(el("span", { class: "badge mode" }, "Seçilen Teknoloji: " + brief.selected_tech.toUpperCase()));
    if (brief.mechanic_query) bRow.appendChild(el("span", { class: "badge good" }, "Mekanik Araştırması: " + brief.mechanic_query));
    if (brief.theme_label) bRow.appendChild(el("span", { class: "badge warn" }, "Tema / Domain: " + brief.theme_label));
    ideaBody.appendChild(bRow);
    var docLinks = el("div", { class: "links-row" });
    docLinks.appendChild(el("a", { href: "TASARIM_BLUEPRINT.md" }, "Tasarım Blueprint (TASARIM_BLUEPRINT.md)"));
    docLinks.appendChild(el("a", { href: "DOMAIN_ARASTIRMASI.md" }, "Domain Araştırması (DOMAIN_ARASTIRMASI.md)"));
    docLinks.appendChild(el("a", { href: "FREE_ASSET_VE_KIT_REHBERI.md" }, "Ücretsiz Kitler (FREE_ASSET_VE_KIT_REHBERI.md)"));
    docLinks.appendChild(el("a", { href: "GENEL_TEARDOWN_RAPORU.md" }, "Genel Rapor (GENEL_TEARDOWN_RAPORU.md)"));
    ideaBody.appendChild(docLinks);
  }

  // Domain Research Panel
  var domainPanel = document.getElementById("domain-panel");
  var domainList = document.getElementById("domain-list");
  if (domainEv.length > 0) {
    domainPanel.classList.remove("hidden");
    domainEv.forEach(function (d) {
      var li = el("li", { class: "web-item" });
      var u = safeExternalUrl(d.url);
      if (u) {
        li.appendChild(el("a", { href: u, target: "_blank", rel: "noopener noreferrer" }, "[" + d.evidence_id + "] " + (d.title || d.domain)));
      } else {
        li.appendChild(el("span", null, "[" + d.evidence_id + "] " + (d.title || d.domain)));
      }
      li.appendChild(el("span", { class: "app-sub" }, " (" + d.topic + ")"));
      if (d.snippet) li.appendChild(el("div", { class: "web-snippet" }, d.snippet));
      domainList.appendChild(li);
    });
  }

  // Free Asset Kits Panel
  var kitsPanel = document.getElementById("kits-panel");
  var kitsGrid = document.getElementById("kits-grid");
  var kitCatFilter = document.getElementById("kit-cat-filter");
  var catNames = {
    ui_ux: "UI / UX Kit",
    models_sprites: "3D / 2D Model",
    audio_sfx: "Ses / SFX",
    fonts: "Font",
    engine_sdk: "Teknoloji SDK / Eklenti"
  };
  function renderKits() {
    kitsGrid.replaceChildren();
    var cVal = kitCatFilter.value;
    freeKits.filter(function (k) { return cVal === "all" || k.category === cVal; }).forEach(function (k) {
      var card = el("div", { class: "kit-card" });
      var u = safeExternalUrl(k.url);
      if (u) {
        card.appendChild(el("a", { href: u, target: "_blank", rel: "noopener noreferrer" }, k.name + " ↗"));
      } else {
        card.appendChild(el("strong", null, k.name));
      }
      var kb = el("div", { class: "badges" });
      kb.appendChild(el("span", { class: "badge mode" }, catNames[k.category] || k.category));
      kb.appendChild(el("span", { class: "badge good" }, k.license || "Free"));
      if (k.source) kb.appendChild(el("span", { class: "badge" }, k.source));
      card.appendChild(kb);
      if (k.usage_note) card.appendChild(el("div", { class: "web-snippet" }, k.usage_note));
      kitsGrid.appendChild(card);
    });
  }
  if (freeKits.length > 0) {
    kitsPanel.classList.remove("hidden");
    kitCatFilter.addEventListener("change", renderKits);
    renderKits();
  }

  // Cross-competitor Icon & Palette Wall
  var wall = document.getElementById("palette-wall");
  comps.forEach(function (comp) {
    var tile = el("div", { class: "wall-tile" });
    var iconRel = comp.icon_asset && comp.icon_asset.local_path
      ? safeRelUrl("apps/" + comp.folder_name + "/" + comp.icon_asset.local_path)
      : "";
    if (iconRel) {
      var img = el("img", { src: iconRel, alt: comp.title, loading: "lazy" });
      img.addEventListener("click", function () { openLightbox(iconRel, comp.title + " Icon"); });
      tile.appendChild(img);
    }
    tile.appendChild(el("div", { class: "name", title: comp.title }, comp.title));
    tile.appendChild(el("div", { class: "app-sub" }, (comp.store === "apple_app_store" ? "iOS" : "Android") + " · " + (comp.product_mode || "")));
    var swWrap = el("div", { class: "swatches" });
    (comp.combined_palette || []).slice(0, 6).forEach(function (sw) {
      if (sw && /^#[0-9A-Fa-f]{6}$/.test(sw.hex)) {
        swWrap.appendChild(el("span", {
          class: "swatch",
          title: sw.hex + " (" + sw.ratio_pct + "%)",
          style: { backgroundColor: sw.hex }
        }));
      }
    });
    tile.appendChild(swWrap);
    wall.appendChild(tile);
  });

  // Filters
  var storeFilter = document.getElementById("store-filter");
  var modeFilter = document.getElementById("mode-filter");
  var sortBy = document.getElementById("sort-by");
  var searchBox = document.getElementById("search-box");
  var container = document.getElementById("apps-container");

  function render() {
    container.replaceChildren();
    var sVal = storeFilter.value;
    var mVal = modeFilter.value;
    var sortVal = sortBy.value;
    var q = (searchBox.value || "").toLowerCase().trim();

    var list = comps.filter(function (c) {
      if (sVal !== "all" && c.store !== sVal) return false;
      if (mVal !== "all" && c.product_mode !== mVal) return false;
      if (q) {
        var hay = (c.title + " " + c.developer + " " + c.category + " " + ((c.signals && c.signals.monetization_model) || "")).toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });

    list.sort(function (a, b) {
      if (sortVal === "evidence") return ((b.signals && b.signals.evidence_score) || 0) - ((a.signals && a.signals.evidence_score) || 0);
      if (sortVal === "rating") return (b.rating || 0) - (a.rating || 0);
      if (sortVal === "frames") {
        var fa = (a.youtube_videos || []).reduce(function (acc, v) { return acc + (v.frames || []).length; }, 0);
        var fb = (b.youtube_videos || []).reduce(function (acc, v) { return acc + (v.frames || []).length; }, 0);
        return fb - fa;
      }
      return ((b.signals && b.signals.popularity_score) || 0) - ((a.signals && a.signals.popularity_score) || 0);
    });

    list.forEach(function (comp) {
      var sig = comp.signals || {};
      var card = el("article", { class: "app-card" });

      var head = el("div", { class: "app-head" });
      var ident = el("div", { class: "app-identity" });
      var iconRel = comp.icon_asset && comp.icon_asset.local_path
        ? safeRelUrl("apps/" + comp.folder_name + "/" + comp.icon_asset.local_path)
        : "";
      if (iconRel) {
        var iconImg = el("img", { src: iconRel, alt: comp.title, loading: "lazy" });
        iconImg.addEventListener("click", function () { openLightbox(iconRel, comp.title); });
        ident.appendChild(iconImg);
      }
      var tcol = el("div");
      tcol.appendChild(el("h3", { class: "app-title" }, comp.title));
      if (comp.subtitle_or_short_desc) tcol.appendChild(el("div", { class: "app-sub" }, comp.subtitle_or_short_desc));
      var badges = el("div", { class: "badges" });
      badges.appendChild(el("span", { class: "badge " + (comp.store === "apple_app_store" ? "ios" : "gp") }, comp.store === "apple_app_store" ? "Apple App Store" : "Google Play"));
      badges.appendChild(el("span", { class: "badge mode" }, "Mode: " + String(comp.product_mode || "game").toUpperCase()));
      badges.appendChild(el("span", { class: "badge" }, sig.monetization_model || "-"));
      badges.appendChild(el("span", { class: "badge" }, String(comp.rating || 0) + " ★ (" + Number(comp.ratings_count || 0).toLocaleString() + ")"));
      if (comp.installs) badges.appendChild(el("span", { class: "badge" }, "İndirme: " + comp.installs));
      if (comp.iap_price_range) badges.appendChild(el("span", { class: "badge" }, "IAP: " + comp.iap_price_range));
      tcol.appendChild(badges);
      ident.appendChild(tcol);
      head.appendChild(ident);

      var scorePill = el("div", { class: "score-pill" });
      scorePill.appendChild(el("div", null, "Kanıt " + String(sig.evidence_score || 0) + "/100"));
      scorePill.appendChild(el("div", { class: "app-sub" }, "Pop: " + String(sig.popularity_score || 0)));
      head.appendChild(scorePill);
      card.appendChild(head);

      var sigBadges = el("div", { class: "badges" });
      (sig.detected_ad_formats || []).forEach(function (a) { sigBadges.appendChild(el("span", { class: "badge warn" }, "Ad: " + a)); });
      (sig.retention_hooks || []).forEach(function (r) { sigBadges.appendChild(el("span", { class: "badge good" }, "Retention: " + r)); });
      Object.keys(sig.ux_friction_themes || {}).forEach(function (f) {
        sigBadges.appendChild(el("span", { class: "badge warn" }, "Friction: " + f + " (" + sig.ux_friction_themes[f] + ")"));
      });
      if (sigBadges.childNodes.length > 0) {
        card.appendChild(el("div", { class: "section-label" }, "Monetizasyon, Retention & Sürtünme Sinyalleri"));
        card.appendChild(sigBadges);
      }

      if (comp.palette_card_path) {
        var palRel = safeRelUrl("apps/" + comp.folder_name + "/" + comp.palette_card_path);
        if (palRel) {
          card.appendChild(el("div", { class: "section-label" }, "Çıkarılan Renk Paleti (HEX Kartela)"));
          var palImg = el("img", { class: "palette-card-img", src: palRel, alt: "Color Palette Card", loading: "lazy" });
          palImg.addEventListener("click", function () { openLightbox(palRel, comp.title + " — Renk Paleti"); });
          card.appendChild(palImg);
        }
      }

      (comp.youtube_videos || []).forEach(function (vid, vIdx) {
        card.appendChild(el("div", { class: "section-label" }, "YouTube Gameplay / Walkthrough #" + (vIdx + 1) + ": " + (vid.title || "Video") + " (" + (vid.frames || []).length + " kare)"));
        var vrow = el("div", { class: "video-row" });
        if (vid.downloaded && vid.local_path) {
          var vRel = safeRelUrl("apps/" + comp.folder_name + "/" + vid.local_path);
          if (vRel) vrow.appendChild(el("video", { controls: "controls", preload: "metadata", src: vRel }));
        }
        (vid.storyboard_paths || []).forEach(function (sb, sbIdx) {
          var sbRel = safeRelUrl("apps/" + comp.folder_name + "/" + sb);
          if (sbRel) {
            var sbImg = el("img", { class: "storyboard", src: sbRel, alt: "Storyboard " + (sbIdx + 1), loading: "lazy" });
            sbImg.addEventListener("click", function () { openLightbox(sbRel, comp.title + " Storyboard #" + (sbIdx + 1)); });
            vrow.appendChild(sbImg);
          }
        });
        card.appendChild(vrow);

        var frames = vid.frames || [];
        if (frames.length > 0) {
          card.appendChild(el("div", { class: "section-label" }, "Kare Kare Zaman Çizelgesi (Büyütmek için kareye tıkla)"));
          var strip = el("div", { class: "filmstrip" });
          frames.forEach(function (kf) {
            var fRel = safeRelUrl("apps/" + comp.folder_name + "/" + kf.local_path);
            if (!fRel) return;
            var tile = el("div", { class: "frame-tile" });
            var fimg = el("img", { src: fRel, alt: "Frame " + kf.index, loading: "lazy" });
            var cap = comp.title + " — Frame #" + kf.index + " @" + kf.timestamp_label + " [" + kf.phase_hint + " | " + kf.source + "]";
            fimg.addEventListener("click", function () { openLightbox(fRel, cap); });
            tile.appendChild(fimg);
            var fmeta = el("div", { class: "frame-meta" });
            fmeta.appendChild(el("span", null, "#" + kf.index + " @" + kf.timestamp_label));
            fmeta.appendChild(el("span", null, kf.source === "scene_change" ? "SCN" : "TIM"));
            tile.appendChild(fmeta);
            strip.appendChild(tile);
          });
          card.appendChild(strip);
        }
      });

      var shots = (comp.screenshots || []).filter(function (s) { return s.downloaded && s.local_path; });
      if (shots.length > 0) {
        card.appendChild(el("div", { class: "section-label" }, "Mağaza Ekran Görüntüleri (" + shots.length + " adet)"));
        var gal = el("div", { class: "gallery" });
        shots.forEach(function (s, idx) {
          var sRel = safeRelUrl("apps/" + comp.folder_name + "/" + s.local_path);
          if (!sRel) return;
          var simg = el("img", { src: sRel, alt: comp.title + " Store #" + (idx + 1), loading: "lazy" });
          simg.addEventListener("click", function () { openLightbox(sRel, comp.title + " Store #" + (idx + 1)); });
          gal.appendChild(simg);
        });
        card.appendChild(gal);
      }

      var webEv = comp.web_evidence || [];
      if (webEv.length > 0) {
        card.appendChild(el("div", { class: "section-label" }, "Web Araştırma Kanıtları (" + webEv.length + " kaynak)"));
        var wlist = el("ul", { class: "web-list" });
        webEv.slice(0, 8).forEach(function (w) {
          var li = el("li", { class: "web-item" });
          var wUrl = safeExternalUrl(w.url);
          if (wUrl) {
            li.appendChild(el("a", { href: wUrl, target: "_blank", rel: "noopener noreferrer" }, "[" + w.evidence_id + "] " + (w.title || w.domain)));
          } else {
            li.appendChild(el("span", null, "[" + w.evidence_id + "] " + (w.title || w.domain)));
          }
          li.appendChild(el("span", { class: "app-sub" }, " (" + w.category + " · " + w.domain + ")"));
          if (w.snippet) li.appendChild(el("div", { class: "web-snippet" }, w.snippet));
          wlist.appendChild(li);
        });
        card.appendChild(wlist);
      }

      var links = el("div", { class: "links-row" });
      links.appendChild(el("a", { href: safeRelUrl("apps/" + comp.folder_name + "/teardown_report.md") }, "Teardown Raporu (teardown_report.md)"));
      links.appendChild(el("a", { href: safeRelUrl("apps/" + comp.folder_name + "/web_research.md") }, "Web Kanıtları (web_research.md)"));
      links.appendChild(el("a", { href: safeRelUrl("apps/" + comp.folder_name + "/store_metadata.md") }, "Mağaza Arşivi (store_metadata.md)"));
      links.appendChild(el("a", { href: safeRelUrl("apps/" + comp.folder_name + "/evidence.json") }, "Kanıt İndeksi (evidence.json)"));
      var storeExt = safeExternalUrl(comp.store_url);
      if (storeExt) links.appendChild(el("a", { href: storeExt, target: "_blank", rel: "noopener noreferrer" }, "Mağaza Sayfası ↗"));
      card.appendChild(links);

      container.appendChild(card);
    });
  }

  storeFilter.addEventListener("change", render);
  modeFilter.addEventListener("change", render);
  sortBy.addEventListener("change", render);
  searchBox.addEventListener("input", render);
  render();
})();
"""


def write_dashboard(run: TeardownRun, run_dir: Path) -> Path:
    """Write self-contained dashboard.html, dashboard.css, and dashboard.js inside run_dir."""
    css_path = safe_join(run_dir, "dashboard.css")
    js_path = safe_join(run_dir, "dashboard.js")
    html_path = safe_join(run_dir, "dashboard.html")

    css_path.write_text(_DASHBOARD_CSS, encoding="utf-8")
    js_path.write_text(_DASHBOARD_JS, encoding="utf-8")

    safe_payload = _safe_json_for_script_tag(run.to_dict())
    html_doc = f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; media-src 'self'; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none';">
  <title>Ürün, Domain &amp; Teardown Stüdyosu</title>
  <link rel="stylesheet" href="dashboard.css">
</head>
<body>
  <div class="container">
    <header class="hero">
      <h1 id="hero-title">Ürün &amp; Oynanış Teardown Stüdyosu</h1>
      <div class="meta" id="hero-meta"></div>
    </header>

    <section class="kpi-grid" id="kpi-grid"></section>

    <section class="panel hidden" id="idea-panel">
      <h2>Fikir Özeti, Mekanik/Domain Ayrımı &amp; Teknoloji Kararı</h2>
      <div id="idea-body"></div>
    </section>

    <section class="panel hidden" id="domain-panel">
      <h2>Gerçek Dünya Domain / Konu Araştırması Kanıtları</h2>
      <ul class="web-list" id="domain-list"></ul>
    </section>

    <section class="panel hidden" id="kits-panel">
      <div class="controls">
        <h2 style="margin:0;flex:1;">Ücretsiz UI/UX, 3D/2D Model, Ses &amp; SDK Kitleri</h2>
        <select id="kit-cat-filter" aria-label="Kit Kategorisi">
          <option value="all">Tüm Kitler</option>
          <option value="ui_ux">UI / UX Kitleri</option>
          <option value="models_sprites">3D / 2D Modeller</option>
          <option value="audio_sfx">Ses / SFX Kitleri</option>
          <option value="fonts">Fontlar</option>
          <option value="engine_sdk">Teknoloji SDK / Eklentiler</option>
        </select>
      </div>
      <div class="kits-grid" id="kits-grid"></div>
    </section>

    <section class="panel">
      <h2>Rakip İkon &amp; Renk Paleti Duvarı (Yan Yana Karşılaştırma)</h2>
      <div class="palette-wall" id="palette-wall"></div>
    </section>

    <section class="controls">
      <select id="store-filter" aria-label="Mağaza Filtresi">
        <option value="all">Tüm Mağazalar</option>
        <option value="google_play">Sadece Google Play</option>
        <option value="apple_app_store">Sadece Apple App Store</option>
      </select>
      <select id="mode-filter" aria-label="Mod Filtresi">
        <option value="all">Tüm Modlar (Oyun + Uygulama)</option>
        <option value="game">Sadece Oyun (Game Mode)</option>
        <option value="app">Sadece Uygulama (App Mode)</option>
      </select>
      <select id="sort-by" aria-label="Sıralama">
        <option value="popularity">Popülerlik Skoruna Göre</option>
        <option value="evidence">Kanıt Tamlık Skoruna Göre</option>
        <option value="rating">Mağaza Puanına Göre</option>
        <option value="frames">Video Kare Sayısına Göre</option>
      </select>
      <input id="search-box" type="search" placeholder="Uygulama, geliştirici veya gelir modeli ara...">
    </section>

    <main id="apps-container"></main>
  </div>

  <div class="lightbox" id="lightbox" role="dialog" aria-modal="true">
    <img id="lightbox-img" alt="Önizleme">
    <div class="lightbox-caption" id="lightbox-caption"></div>
  </div>

  <script id="teardown-data" type="application/json">{safe_payload}</script>
  <script src="dashboard.js"></script>
</body>
</html>
"""
    html_path.write_text(html_doc, encoding="utf-8")
    return html_path

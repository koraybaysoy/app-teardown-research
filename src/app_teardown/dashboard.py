"""Secure, zero-CDN, XSS-safe minimalist Dark Mode Teardown Workbench inspired by Linear and Raycast."""

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


_DASHBOARD_CSS = """/* App Teardown Workbench - Minimalist Dark Mode (Linear + Raycast inspired) */
:root {
  --rail: #0a0b0f;
  --bg: #0e1016;
  --surface: #13161f;
  --surface-hover: #191d28;
  --bar-bg: rgba(255, 255, 255, 0.05);
  --border: rgba(255, 255, 255, 0.07);
  --border-hover: rgba(255, 255, 255, 0.14);
  --ink: #f1f5f9;
  --ink-dim: #94a3b8;
  --muted: #64748b;
  --accent: #f1f5f9;
  --accent-fg: #0a0b0f;
  --emerald: #10b981;
  --amber: #f59e0b;
  --rose: #f43f5e;
  --radius: 12px;
}

body.light {
  --rail: #f4f4f5;
  --bg: #fafafa;
  --surface: #ffffff;
  --surface-hover: #f4f4f5;
  --bar-bg: #f4f4f5;
  --border: #e4e4e7;
  --border-hover: #d4d4d8;
  --ink: #09090b;
  --ink-dim: #52525b;
  --muted: #71717a;
  --accent: #18181b;
  --accent-fg: #fafafa;
  --emerald: #059669;
  --amber: #d97706;
  --rose: #e11d48;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg);
  color: var(--ink);
  font-size: 14px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
.hidden { display: none !important; }

/* Slim Left Rail + Spacious Canvas (Linear style) */
.shell {
  display: grid;
  grid-template-columns: 204px minmax(0, 1fr);
  min-height: 100vh;
}
aside.rail {
  background: var(--rail);
  border-right: 1px solid var(--border);
  padding: 20px 14px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 2px 8px;
}
.brand-mark {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: var(--accent);
  color: var(--accent-fg);
  display: grid;
  place-items: center;
  font-weight: 700;
  font-size: 11px;
  flex-shrink: 0;
}
.brand-name { font-size: 13.5px; font-weight: 600; letter-spacing: -0.01em; }
.rail-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--muted);
  padding: 0 8px 8px 8px;
}
.rail-nav { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 2px; }
.rail-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 10px;
  border-radius: 7px;
  color: var(--ink-dim);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
}
.rail-link:hover { color: var(--ink); background: var(--surface); }
.rail-link.active { color: var(--ink); background: var(--surface); }
.rail-cnt { font-size: 11.5px; color: var(--muted); font-variant-numeric: tabular-nums; }
.rail-foot {
  margin-top: auto;
  padding: 10px 8px 0 8px;
  border-top: 1px solid var(--border);
  font-size: 11.5px;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 8px;
}
.status-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--emerald); flex-shrink: 0; }

/* Main Column */
.workspace { display: flex; flex-direction: column; min-width: 0; }
header.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  height: 58px;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.top-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
.top-left h1 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.015em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.top-meta { font-size: 12px; color: var(--muted); font-family: ui-monospace, monospace; white-space: nowrap; }
.top-actions { display: flex; align-items: center; gap: 10px; }
.btn {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--ink);
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
}
.btn:hover { border-color: var(--border-hover); background: var(--surface-hover); }
.btn-primary { background: var(--accent); color: var(--accent-fg); border-color: var(--accent); font-weight: 600; }
.btn-primary:hover { opacity: 0.9; background: var(--accent); }

.canvas {
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 28px 32px 64px 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 4 Calm KPI Tiles */
.kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.kpi-tile {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 22px;
}
.kpi-label { font-size: 12.5px; color: var(--muted); font-weight: 500; }
.kpi-row { display: flex; align-items: baseline; justify-content: space-between; margin-top: 10px; gap: 8px; }
.kpi-val { font-size: 30px; font-weight: 600; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
.kpi-sub { font-size: 12px; color: var(--muted); font-variant-numeric: tabular-nums; }

/* Panels */
.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 22px 24px;
}
.panel-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}
.panel-hd h2 { margin: 0; font-size: 14.5px; font-weight: 600; letter-spacing: -0.01em; }
.panel-meta { font-size: 12px; color: var(--muted); font-variant-numeric: tabular-nums; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

/* Clean Borderless Rows (Competitors & Kits) */
.rows { display: flex; flex-direction: column; }
.row-item {
  display: grid;
  grid-template-columns: 1fr 70px 104px 52px 58px;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}
.row-item:first-child { padding-top: 0; }
.row-item:last-child { border-bottom: none; padding-bottom: 0; }
.row-id { display: flex; align-items: center; gap: 12px; min-width: 0; }
.row-id img { width: 32px; height: 32px; border-radius: 8px; object-fit: cover; cursor: pointer; flex-shrink: 0; }
.row-title { font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.row-muted { font-size: 12px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.row-num { font-weight: 600; text-align: right; font-variant-numeric: tabular-nums; }

.dots { display: flex; gap: 4px; justify-content: flex-end; }
.dot { width: 10px; height: 10px; border-radius: 50%; border: 1px solid rgba(255, 255, 255, 0.16); display: inline-block; }

/* Domain References & Moodboard */
.ref-overview { display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 16px; }
.ref-overview img { max-height: 220px; max-width: 100%; border-radius: 9px; cursor: pointer; }
.ref-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(195px, 1fr)); gap: 14px; }
.ref-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.ref-card img { width: 100%; height: 140px; object-fit: cover; border-radius: 7px; cursor: pointer; }
.ref-title { font-size: 12.5px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ref-meta { font-size: 11px; color: var(--muted); display: flex; justify-content: space-between; font-family: ui-monospace, monospace; }

/* Kits & Domain Evidence */
.kits-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
.kit-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.kit-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.kit-card a { color: var(--ink); text-decoration: none; font-weight: 500; font-size: 13px; }
.kit-card a:hover { text-decoration: underline; }
.kit-lic { font-size: 11px; color: var(--emerald); font-family: ui-monospace, monospace; }

.web-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; }
.web-item { padding: 11px 0; border-bottom: 1px solid var(--border); font-size: 13px; }
.web-item:first-child { padding-top: 0; }
.web-item:last-child { border-bottom: none; padding-bottom: 0; }
.web-item a { color: var(--ink); text-decoration: none; font-weight: 500; }
.web-item a:hover { text-decoration: underline; }
.web-snippet { font-size: 12px; color: var(--muted); margin-top: 3px; }

/* Controls */
.controls { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.controls select, .controls input {
  background: var(--surface);
  color: var(--ink);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 12px;
  font-size: 13px;
}
.controls input { min-width: 220px; }
.controls select:focus, .controls input:focus { outline: 1px solid var(--ink-dim); }

/* Competitor Detail Cards */
.app-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 22px 24px;
  margin-bottom: 16px;
}
.app-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 18px; }
.app-ident { display: flex; align-items: center; gap: 14px; min-width: 0; }
.app-ident img { width: 48px; height: 48px; border-radius: 11px; object-fit: cover; cursor: pointer; }
.app-title { margin: 0; font-size: 15.5px; font-weight: 600; }
.app-sub { font-size: 12.5px; color: var(--muted); margin-top: 2px; }
.app-score { font-size: 20px; font-weight: 600; font-variant-numeric: tabular-nums; }

.filmstrip { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; }
.frame-tile {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 9px;
  padding: 7px;
  flex-shrink: 0;
  width: 152px;
}
.frame-tile img { width: 100%; height: 120px; object-fit: cover; border-radius: 6px; cursor: pointer; display: block; }
.frame-meta {
  font-size: 11px;
  color: var(--muted);
  margin-top: 6px;
  display: flex;
  justify-content: space-between;
  font-family: ui-monospace, monospace;
}
.video-row { display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 14px; }
.video-row video { max-height: 240px; max-width: 440px; border-radius: 9px; background: #000; }
.video-row img.storyboard { max-height: 240px; border-radius: 9px; cursor: pointer; }
.gallery { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 6px; margin-top: 14px; }
.gallery img { height: 200px; width: auto; border-radius: 8px; cursor: pointer; flex-shrink: 0; }
.links-row { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 16px; font-size: 12.5px; }
.links-row a { color: var(--ink-dim); text-decoration: none; }
.links-row a:hover { color: var(--ink); text-decoration: underline; }

/* Lightbox */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(6, 8, 12, 0.92);
  display: none;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 24px;
}
.lightbox.open { display: flex; }
.lightbox img { max-width: 94vw; max-height: 85vh; border-radius: 10px; }
.lightbox-caption { color: #cbd5e1; margin-top: 12px; font-size: 13px; }

@media (max-width: 960px) {
  .shell { grid-template-columns: 1fr; }
  aside.rail { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--border); }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .grid-2 { grid-template-columns: 1fr; }
}
"""

_DASHBOARD_JS = """/* App Teardown Workbench - Minimalist safe DOM renderer (createElement and textContent only) */
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
  var domainRefs = Array.isArray(runData.domain_references) ? runData.domain_references : [];
  var freeKits = Array.isArray(runData.free_asset_kits) ? runData.free_asset_kits : [];

  // Theme Toggle (Dark default -> optional Light)
  var themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      var isLight = document.body.classList.toggle("light");
      themeToggle.textContent = isLight ? "Dark" : "Light";
    });
  }

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

  // Header & Sidebar Counters
  document.getElementById("hero-title").textContent = runData.campaign_name || runData.query || "Teardown";
  document.getElementById("top-meta").textContent =
    (brief && brief.selected_tech ? brief.selected_tech.toUpperCase() + " · " : "") +
    String(runData.country || "us").toUpperCase() + "/" + String(runData.lang || "en").toUpperCase() +
    (runData.official_only ? " · official" : "");

  var cntComps = document.getElementById("nav-count-comps");
  var cntRefs = document.getElementById("nav-count-refs");
  var cntKits = document.getElementById("nav-count-kits");
  if (cntComps) cntComps.textContent = String(comps.length);
  if (cntRefs) cntRefs.textContent = String(domainRefs.length);
  if (cntKits) cntKits.textContent = String(freeKits.length);

  var railStatus = document.getElementById("rail-status");
  if (railStatus) {
    railStatus.textContent = runData.official_only ? "Official APIs only" : "Local MCP ready";
  }

  // 4 Calm KPI Tiles
  var kpiGrid = document.getElementById("kpi-grid");
  [
    ["Competitors", String(ca.total_competitors || comps.length), String(ca.dominant_monetization || "-")],
    ["Keyframes", String(ca.total_gameplay_frames || 0), "SCN / TIM"],
    ["Subject Refs", String(domainRefs.length), domainEv.length + " sources"],
    ["Evidence Score", String(ca.avg_evidence_score || 0), freeKits.length + " kits"]
  ].forEach(function (item) {
    var tile = el("div", { class: "kpi-tile" });
    tile.appendChild(el("div", { class: "kpi-label" }, item[0]));
    var row = el("div", { class: "kpi-row" });
    row.appendChild(el("div", { class: "kpi-val" }, item[1]));
    row.appendChild(el("div", { class: "kpi-sub" }, item[2]));
    tile.appendChild(row);
    kpiGrid.appendChild(tile);
  });

  // Brief / Reports Links (PROTOTIP_VE_TAM_SURUM_PLANI.md)
  var briefPanel = document.getElementById("idea-panel");
  var briefLinks = document.getElementById("idea-links");
  if (brief && briefPanel && briefLinks) {
    briefPanel.classList.remove("hidden");
    [
      "TASARIM_BLUEPRINT.md",
      "PROTOTIP_VE_TAM_SURUM_PLANI.md",
      "DOMAIN_ARASTIRMASI.md",
      "FREE_ASSET_VE_KIT_REHBERI.md",
      "GENEL_TEARDOWN_RAPORU.md"
    ].forEach(function (doc) {
      briefLinks.appendChild(el("a", { href: doc }, doc));
    });
  }

  // Borderless Competitor Rows
  var compRows = document.getElementById("matrix-rows");
  var matrixPanel = document.getElementById("matrix-panel");
  if (comps.length > 0 && compRows && matrixPanel) {
    matrixPanel.classList.remove("hidden");
    comps.forEach(function (comp) {
      var sig = comp.signals || {};
      var row = el("div", { class: "row-item" });
      var idBox = el("div", { class: "row-id" });
      var iconRel = comp.icon_asset && comp.icon_asset.local_path
        ? safeRelUrl("apps/" + comp.folder_name + "/" + comp.icon_asset.local_path)
        : "";
      if (iconRel) {
        var im = el("img", { src: iconRel, alt: comp.title, loading: "lazy" });
        im.addEventListener("click", function () { openLightbox(iconRel, comp.title); });
        idBox.appendChild(im);
      }
      idBox.appendChild(el("span", { class: "row-title" }, comp.title));
      row.appendChild(idBox);

      row.appendChild(el("span", { class: "row-muted" }, comp.store === "apple_app_store" ? "iOS" : "Play"));
      row.appendChild(el("span", { class: "row-muted" }, sig.monetization_model || "-"));
      row.appendChild(el("span", { class: "row-num" }, String(sig.evidence_score || 0)));

      var dots = el("div", { class: "dots" });
      (comp.combined_palette || []).slice(0, 3).forEach(function (sw) {
        if (sw && /^#[0-9A-Fa-f]{6}$/.test(sw.hex)) {
          dots.appendChild(el("span", { class: "dot", title: sw.hex, style: { backgroundColor: sw.hex } }));
        }
      });
      row.appendChild(dots);
      compRows.appendChild(row);
    });
  }

  // Domain Visual References
  var domainRefsPanel = document.getElementById("domain-refs-panel");
  var domainRefsOverview = document.getElementById("domain-refs-overview");
  var domainRefsGrid = document.getElementById("domain-refs-grid");
  var refCatFilter = document.getElementById("ref-cat-filter");
  function renderDomainRefs() {
    domainRefsGrid.replaceChildren();
    var cVal = refCatFilter.value;
    domainRefs.filter(function (r) {
      return r.downloaded && r.local_path && (cVal === "all" || r.category === cVal);
    }).forEach(function (r) {
      var rel = safeRelUrl(r.local_path);
      if (!rel) return;
      var card = el("div", { class: "ref-card" });
      var img = el("img", { src: rel, alt: r.subject_label || r.title || "Reference", loading: "lazy" });
      img.addEventListener("click", function () { openLightbox(rel, r.evidence_id + " · " + (r.subject_label || r.title || "")); });
      card.appendChild(img);
      card.appendChild(el("div", { class: "ref-title" }, r.subject_label || r.title));
      var meta = el("div", { class: "ref-meta" });
      meta.appendChild(el("span", null, r.evidence_id));
      meta.appendChild(el("span", null, r.category));
      card.appendChild(meta);
      domainRefsGrid.appendChild(card);
    });
  }
  if (domainRefs.length > 0) {
    domainRefsPanel.classList.remove("hidden");
    var sheetRel = safeRelUrl(runData.domain_reference_sheet_path || "");
    if (sheetRel) {
      var shImg = el("img", { src: sheetRel, alt: "Reference Moodboard", loading: "lazy" });
      shImg.addEventListener("click", function () { openLightbox(sheetRel, "Subject Reference Sheet"); });
      domainRefsOverview.appendChild(shImg);
    }
    var domPalRel = safeRelUrl(runData.domain_palette_card_path || "");
    if (domPalRel) {
      var dpImg = el("img", { src: domPalRel, alt: "Subject Palette", loading: "lazy" });
      dpImg.addEventListener("click", function () { openLightbox(domPalRel, "Real-World Subject Palette"); });
      domainRefsOverview.appendChild(dpImg);
    }
    refCatFilter.addEventListener("change", renderDomainRefs);
    renderDomainRefs();
  }

  // Domain Text Evidence
  var domainPanel = document.getElementById("domain-panel");
  var domainList = document.getElementById("domain-list");
  if (domainEv.length > 0) {
    domainPanel.classList.remove("hidden");
    domainEv.forEach(function (d) {
      var li = el("li", { class: "web-item" });
      var u = safeExternalUrl(d.url);
      if (u) li.appendChild(el("a", { href: u, target: "_blank", rel: "noopener noreferrer" }, d.evidence_id + " · " + (d.title || d.domain)));
      else li.appendChild(el("span", null, d.evidence_id + " · " + (d.title || d.domain)));
      if (d.snippet) li.appendChild(el("div", { class: "web-snippet" }, d.snippet));
      domainList.appendChild(li);
    });
  }

  // Free Asset Kits
  var kitsPanel = document.getElementById("kits-panel");
  var kitsGrid = document.getElementById("kits-grid");
  var kitCatFilter = document.getElementById("kit-cat-filter");
  function renderKits() {
    kitsGrid.replaceChildren();
    var cVal = kitCatFilter.value;
    freeKits.filter(function (k) { return cVal === "all" || k.category === cVal; }).forEach(function (k) {
      var card = el("div", { class: "kit-card" });
      var hd = el("div", { class: "kit-head" });
      var u = safeExternalUrl(k.url);
      if (u) hd.appendChild(el("a", { href: u, target: "_blank", rel: "noopener noreferrer" }, k.name + " ↗"));
      else hd.appendChild(el("span", null, k.name));
      hd.appendChild(el("span", { class: "kit-lic" }, k.license || "Free"));
      card.appendChild(hd);
      if (k.usage_note) card.appendChild(el("div", { class: "web-snippet" }, k.usage_note));
      kitsGrid.appendChild(card);
    });
  }
  if (freeKits.length > 0) {
    kitsPanel.classList.remove("hidden");
    kitCatFilter.addEventListener("change", renderKits);
    renderKits();
  }

  // Filterable Competitor Detail Cards
  var storeFilter = document.getElementById("store-filter");
  var sortBy = document.getElementById("sort-by");
  var searchBox = document.getElementById("search-box");
  var container = document.getElementById("apps-container");

  function render() {
    container.replaceChildren();
    var sVal = storeFilter.value;
    var sortVal = sortBy.value;
    var q = (searchBox.value || "").toLowerCase().trim();

    var list = comps.filter(function (c) {
      if (sVal !== "all" && c.store !== sVal) return false;
      if (q && (c.title + " " + c.developer + " " + c.category).toLowerCase().indexOf(q) === -1) return false;
      return true;
    });
    list.sort(function (a, b) {
      if (sortVal === "evidence") return ((b.signals && b.signals.evidence_score) || 0) - ((a.signals && a.signals.evidence_score) || 0);
      if (sortVal === "rating") return (b.rating || 0) - (a.rating || 0);
      return ((b.signals && b.signals.popularity_score) || 0) - ((a.signals && a.signals.popularity_score) || 0);
    });

    list.forEach(function (comp) {
      var sig = comp.signals || {};
      var card = el("article", { class: "app-card" });
      var head = el("div", { class: "app-head" });
      var ident = el("div", { class: "app-ident" });
      var iconRel = comp.icon_asset && comp.icon_asset.local_path
        ? safeRelUrl("apps/" + comp.folder_name + "/" + comp.icon_asset.local_path)
        : "";
      if (iconRel) {
        var iconImg = el("img", { src: iconRel, alt: comp.title, loading: "lazy" });
        iconImg.addEventListener("click", function () { openLightbox(iconRel, comp.title); });
        ident.appendChild(iconImg);
      }
      var info = el("div");
      info.appendChild(el("h3", { class: "app-title" }, comp.title));
      info.appendChild(el("div", { class: "app-sub" },
        (comp.store === "apple_app_store" ? "App Store" : "Google Play") + " · " +
        (sig.monetization_model || "-") + " · " + (comp.rating || 0) + " ★"
      ));
      ident.appendChild(info);
      head.appendChild(ident);
      head.appendChild(el("div", { class: "app-score" }, String(sig.evidence_score || 0)));
      card.appendChild(head);

      (comp.youtube_videos || []).forEach(function (vid) {
        var vrow = el("div", { class: "video-row" });
        if (vid.downloaded && vid.local_path) {
          var vRel = safeRelUrl("apps/" + comp.folder_name + "/" + vid.local_path);
          if (vRel) vrow.appendChild(el("video", { controls: "controls", preload: "metadata", src: vRel }));
        }
        (vid.storyboard_paths || []).forEach(function (sb) {
          var sbRel = safeRelUrl("apps/" + comp.folder_name + "/" + sb);
          if (sbRel) {
            var sbImg = el("img", { class: "storyboard", src: sbRel, alt: "Storyboard", loading: "lazy" });
            sbImg.addEventListener("click", function () { openLightbox(sbRel, comp.title + " Storyboard"); });
            vrow.appendChild(sbImg);
          }
        });
        if (vrow.childNodes.length > 0) card.appendChild(vrow);

        var frames = vid.frames || [];
        if (frames.length > 0) {
          var strip = el("div", { class: "filmstrip" });
          frames.forEach(function (kf) {
            var fRel = safeRelUrl("apps/" + comp.folder_name + "/" + kf.local_path);
            if (!fRel) return;
            var tile = el("div", { class: "frame-tile" });
            var fimg = el("img", { src: fRel, alt: "Frame " + kf.index, loading: "lazy" });
            fimg.addEventListener("click", function () { openLightbox(fRel, comp.title + " @" + kf.timestamp_label); });
            tile.appendChild(fimg);
            var fmeta = el("div", { class: "frame-meta" });
            fmeta.appendChild(el("span", null, kf.timestamp_label));
            fmeta.appendChild(el("span", null, kf.source === "scene_change" ? "SCN" : "TIM"));
            tile.appendChild(fmeta);
            strip.appendChild(tile);
          });
          card.appendChild(strip);
        }
      });

      var shots = (comp.screenshots || []).filter(function (s) { return s.downloaded && s.local_path; });
      if (shots.length > 0) {
        var gal = el("div", { class: "gallery" });
        shots.forEach(function (s, idx) {
          var sRel = safeRelUrl("apps/" + comp.folder_name + "/" + s.local_path);
          if (!sRel) return;
          var simg = el("img", { src: sRel, alt: comp.title + " #" + (idx + 1), loading: "lazy" });
          simg.addEventListener("click", function () { openLightbox(sRel, comp.title + " #" + (idx + 1)); });
          gal.appendChild(simg);
        });
        card.appendChild(gal);
      }

      var links = el("div", { class: "links-row" });
      links.appendChild(el("a", { href: safeRelUrl("apps/" + comp.folder_name + "/teardown_report.md") }, "teardown_report.md"));
      links.appendChild(el("a", { href: safeRelUrl("apps/" + comp.folder_name + "/evidence.json") }, "evidence.json"));
      links.appendChild(el("a", { href: safeRelUrl("apps/" + comp.folder_name + "/web_research.md") }, "web_research.md"));
      var storeExt = safeExternalUrl(comp.store_url);
      if (storeExt) links.appendChild(el("a", { href: storeExt, target: "_blank", rel: "noopener noreferrer" }, "Store ↗"));
      card.appendChild(links);

      container.appendChild(card);
    });
  }

  storeFilter.addEventListener("change", render);
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
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; media-src 'self'; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none';">
  <title>App Teardown Workbench</title>
  <link rel="stylesheet" href="dashboard.css">
</head>
<body>
  <div class="shell">
    <aside class="rail">
      <div class="brand">
        <div class="brand-mark">AT</div>
        <div class="brand-name">App Teardown</div>
      </div>

      <div>
        <div class="rail-label">Workspace</div>
        <ul class="rail-nav">
          <li><a class="rail-link active" href="#overview"><span>Overview</span></a></li>
          <li><a class="rail-link" href="#matrix-panel"><span>Competitors</span><span class="rail-cnt" id="nav-count-comps">0</span></a></li>
          <li><a class="rail-link" href="#domain-refs-panel"><span>Subject Refs</span><span class="rail-cnt" id="nav-count-refs">0</span></a></li>
          <li><a class="rail-link" href="#kits-panel"><span>Free Kits</span><span class="rail-cnt" id="nav-count-kits">0</span></a></li>
          <li><a class="rail-link" href="#competitors-section"><span>Keyframes</span></a></li>
        </ul>
      </div>

      <div>
        <div class="rail-label">Reports</div>
        <ul class="rail-nav">
          <li><a class="rail-link" href="GENEL_TEARDOWN_RAPORU.md"><span>Teardown</span></a></li>
          <li><a class="rail-link" href="TASARIM_BLUEPRINT.md"><span>Blueprint</span></a></li>
          <li><a class="rail-link" href="PROTOTIP_VE_TAM_SURUM_PLANI.md"><span>Prototype Plan</span></a></li>
        </ul>
      </div>

      <div class="rail-foot">
        <span class="status-dot"></span>
        <span id="rail-status">Local MCP ready</span>
      </div>
    </aside>

    <div class="workspace">
      <header class="topbar">
        <div class="top-left">
          <h1 id="hero-title">Teardown</h1>
          <span class="top-meta" id="top-meta">US/EN</span>
        </div>
        <div class="top-actions">
          <button type="button" class="btn" id="theme-toggle">Light</button>
          <a class="btn btn-primary" href="PROTOTIP_VE_TAM_SURUM_PLANI.md">Prototype Gate</a>
        </div>
      </header>

      <main class="canvas" id="overview">
        <section class="kpi-grid" id="kpi-grid"></section>

        <section class="panel hidden" id="idea-panel">
          <div class="panel-hd">
            <h2>Deliverables</h2>
            <span class="panel-meta">Local Markdown</span>
          </div>
          <div class="links-row" id="idea-links"></div>
        </section>

        <section class="panel hidden" id="matrix-panel">
          <div class="panel-hd">
            <h2>Competitors</h2>
            <span class="panel-meta">Evidence score</span>
          </div>
          <div class="rows" id="matrix-rows"></div>
        </section>

        <section class="panel hidden" id="domain-refs-panel">
          <div class="panel-hd">
            <h2>Subject References</h2>
            <div class="controls">
              <select id="ref-cat-filter" aria-label="Category">
                <option value="all">All</option>
                <option value="anatomy_layers">Anatomy</option>
                <option value="how_its_made">Process</option>
                <option value="real_world_equivalent">Real-world</option>
                <option value="famous_brand">Brands</option>
              </select>
            </div>
          </div>
          <div class="ref-overview" id="domain-refs-overview"></div>
          <div class="ref-grid" id="domain-refs-grid"></div>
        </section>

        <section class="panel hidden" id="domain-panel">
          <div class="panel-hd">
            <h2>Subject Sources</h2>
            <span class="panel-meta">Wikipedia &amp; Web</span>
          </div>
          <ul class="web-list" id="domain-list"></ul>
        </section>

        <section class="panel hidden" id="kits-panel">
          <div class="panel-hd">
            <h2>Free Asset Kits</h2>
            <div class="controls">
              <select id="kit-cat-filter" aria-label="Kit Category">
                <option value="all">All</option>
                <option value="ui_ux">UI / UX</option>
                <option value="models_sprites">3D / 2D</option>
                <option value="audio_sfx">Audio</option>
                <option value="fonts">Fonts</option>
                <option value="engine_sdk">SDK</option>
              </select>
            </div>
          </div>
          <div class="kits-grid" id="kits-grid"></div>
        </section>

        <section id="competitors-section">
          <div class="panel-hd">
            <h2>Gameplay Keyframes</h2>
            <div class="controls">
              <select id="store-filter" aria-label="Store">
                <option value="all">All stores</option>
                <option value="google_play">Google Play</option>
                <option value="apple_app_store">App Store</option>
              </select>
              <select id="sort-by" aria-label="Sort">
                <option value="popularity">Popularity</option>
                <option value="evidence">Evidence</option>
                <option value="rating">Rating</option>
              </select>
              <input id="search-box" type="search" placeholder="Filter...">
            </div>
          </div>
          <div id="apps-container"></div>
        </section>
      </main>
    </div>
  </div>

  <div class="lightbox" id="lightbox" role="dialog" aria-modal="true">
    <img id="lightbox-img" alt="Preview">
    <div class="lightbox-caption" id="lightbox-caption"></div>
  </div>

  <script id="teardown-data" type="application/json">{safe_payload}</script>
  <script src="dashboard.js"></script>
</body>
</html>
"""
    html_path.write_text(html_doc, encoding="utf-8")
    return html_path

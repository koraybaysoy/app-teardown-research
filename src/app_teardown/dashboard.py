"""Secure, zero-CDN, XSS-safe local HTML Teardown Dashboard inspired by shadcn/ui (Zinc), Tremor, and Tabler."""

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


_DASHBOARD_CSS = """/* App Teardown Dashboard - shadcn/ui Zinc + Tremor + Tabler inspired self-contained stylesheet */
:root {
  --background: #fafafa;
  --sidebar: #f4f4f5;
  --card: #ffffff;
  --card-hover: #fcfcfd;
  --foreground: #09090b;
  --muted-bg: #f4f4f5;
  --muted: #71717a;
  --border: #e4e4e7;
  --border-strong: #d4d4d8;
  --primary: #18181b;
  --primary-fg: #fafafa;
  --ring: #18181b;
  --emerald: #15803d;
  --emerald-bg: #f0fdf4;
  --emerald-bd: #bbf7d0;
  --amber: #b45309;
  --amber-bg: #fffbeb;
  --amber-bd: #fde68a;
  --rose: #be123c;
  --rose-bg: #fff1f2;
  --rose-bd: #fecdd3;
  --shadow-xs: 0 1px 2px rgba(9, 9, 11, 0.04);
  --radius: 10px;
}

body.dark {
  --background: #09090b;
  --sidebar: #111113;
  --card: #121215;
  --card-hover: #18181b;
  --foreground: #fafafa;
  --muted-bg: #1c1c20;
  --muted: #a1a1aa;
  --border: #27272a;
  --border-strong: #3f3f46;
  --primary: #fafafa;
  --primary-fg: #09090b;
  --ring: #d4d4d8;
  --emerald: #4ade80;
  --emerald-bg: rgba(34, 197, 94, 0.12);
  --emerald-bd: rgba(34, 197, 94, 0.28);
  --amber: #fbbf24;
  --amber-bg: rgba(245, 158, 11, 0.12);
  --amber-bd: rgba(245, 158, 11, 0.28);
  --rose: #fb7185;
  --rose-bg: rgba(244, 63, 94, 0.12);
  --rose-bd: rgba(244, 63, 94, 0.28);
  --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.25);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--background);
  color: var(--foreground);
  line-height: 1.5;
  font-size: 14px;
  -webkit-font-smoothing: antialiased;
}
.hidden { display: none !important; }

/* App Shell: Inset Sidebar + Main Column (shadcn/ui dashboard-01) */
.shell {
  display: grid;
  grid-template-columns: 244px minmax(0, 1fr);
  min-height: 100vh;
}
aside.sidebar {
  background: var(--sidebar);
  border-right: 1px solid var(--border);
  padding: 16px 12px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.brand-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
}
.brand-mark {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  background: var(--primary);
  color: var(--primary-fg);
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 13px;
  flex-shrink: 0;
}
.brand-title { font-size: 13.5px; font-weight: 700; letter-spacing: -0.01em; }
.brand-ver { font-size: 11px; color: var(--muted); }
.nav-group-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  padding: 0 10px 6px 10px;
  letter-spacing: 0.02em;
}
.nav-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 2px; }
.nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 10px;
  border-radius: 7px;
  color: var(--foreground);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: background 0.12s ease;
}
.nav-link:hover { background: var(--border); }
.nav-link.active { background: var(--card); border: 1px solid var(--border); box-shadow: var(--shadow-xs); }
.nav-count {
  font-size: 11px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}
.sidebar-footer {
  margin-top: auto;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 10px 12px;
  font-size: 12px;
}
.sidebar-footer .sf-title { font-weight: 600; margin-bottom: 4px; }
.sidebar-footer .sf-meta { color: var(--muted); font-size: 11.5px; }

/* Main Workspace */
.workspace {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
header.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  background: var(--card);
  border-bottom: 1px solid var(--border);
  height: 54px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  min-width: 0;
}
.breadcrumbs .crumb-muted { color: var(--muted); }
.breadcrumbs .crumb-sep { color: var(--border-strong); }
.breadcrumbs .crumb-active { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.topbar-actions { display: flex; align-items: center; gap: 10px; }

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--foreground);
  border-radius: 7px;
  padding: 6px 11px;
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  box-shadow: var(--shadow-xs);
}
.btn:hover { background: var(--muted-bg); }
.btn-primary {
  background: var(--primary);
  color: var(--primary-fg);
  border-color: var(--primary);
}
.btn-primary:hover { opacity: 0.9; background: var(--primary); }

.main-inner {
  max-width: 1360px;
  width: 100%;
  margin: 0 auto;
  padding: 22px 24px 48px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-end;
  gap: 12px;
}
.page-header h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.025em;
}
.page-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 4px;
  font-size: 12.5px;
  color: var(--muted);
}

/* Tremor-style KPI Metric Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
  gap: 14px;
}
.kpi-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 18px;
  box-shadow: var(--shadow-xs);
}
.kpi-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--muted);
}
.kpi-val {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.025em;
  margin-top: 6px;
  font-variant-numeric: tabular-nums;
  color: var(--foreground);
}
.kpi-sub {
  font-size: 11.5px;
  color: var(--muted);
  margin-top: 4px;
}

/* Cards & Panels (shadcn/ui Card) */
.panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  box-shadow: var(--shadow-xs);
}
.panel-compact { margin-bottom: 14px; }
.panel-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}
.panel-header-flat { margin-bottom: 0; }
.panel h2 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.015em;
}
.panel-desc {
  margin: 2px 0 0 0;
  font-size: 12.5px;
  color: var(--muted);
}

/* Restrained Semantic Badges (shadcn/ui Badge outline/secondary) */
.badges { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.badge {
  display: inline-flex;
  align-items: center;
  font-size: 11.5px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--muted-bg);
  color: var(--foreground);
  border: 1px solid var(--border);
}
.badge.gp, .badge.good { color: var(--emerald); background: var(--emerald-bg); border-color: var(--emerald-bd); }
.badge.ios, .badge.mode { color: var(--foreground); background: var(--card); border-color: var(--border-strong); }
.badge.warn { color: var(--amber); background: var(--amber-bg); border-color: var(--amber-bd); }
.badge.danger { color: var(--rose); background: var(--rose-bg); border-color: var(--rose-bd); }

/* TanStack-style Hairline Comparison Table */
.table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; }
table.data-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
table.data-table th {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--muted);
  background: var(--muted-bg);
  padding: 9px 12px;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
table.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}
table.data-table tr:last-child td { border-bottom: none; }
table.data-table tr:hover td { background: var(--muted-bg); }
.table-app-cell { display: flex; align-items: center; gap: 10px; font-weight: 600; }
.table-app-cell img { width: 32px; height: 32px; border-radius: 7px; object-fit: cover; border: 1px solid var(--border); cursor: pointer; }
.score-bar-wrap { display: flex; align-items: center; gap: 8px; font-variant-numeric: tabular-nums; font-weight: 600; font-size: 12px; }
.score-bar { width: 64px; height: 6px; border-radius: 999px; background: var(--muted-bg); overflow: hidden; border: 1px solid var(--border); }
.score-bar-fill { height: 100%; background: var(--primary); border-radius: 999px; }

/* Swatches */
.swatches { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }
.swatch {
  width: 15px;
  height: 15px;
  border-radius: 4px;
  border: 1px solid rgba(9, 9, 11, 0.18);
  display: inline-block;
}

/* Palette Wall */
.palette-wall { display: grid; grid-template-columns: repeat(auto-fill, minmax(156px, 1fr)); gap: 12px; }
.wall-tile {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}
.wall-tile img {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  object-fit: cover;
  border: 1px solid var(--border);
  display: block;
  margin: 0 auto 8px auto;
  cursor: pointer;
}
.wall-tile .name { font-size: 12.5px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.wall-tile .swatches { justify-content: center; margin-top: 8px; }

/* Domain Visual Reference Gallery */
.disclaimer-note { font-size: 12px; color: var(--muted); margin: 0 0 12px 0; }
.ref-overview { display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-start; margin-bottom: 14px; }
.ref-overview img {
  max-height: 230px;
  max-width: 100%;
  border-radius: 8px;
  border: 1px solid var(--border);
  cursor: pointer;
}
.ref-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 12px; }
.ref-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.ref-card img {
  width: 100%;
  height: 148px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--muted-bg);
  cursor: pointer;
}
.ref-card .ref-title { font-size: 12.5px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ref-card a { color: var(--muted); text-decoration: none; font-size: 11.5px; }
.ref-card a:hover { color: var(--foreground); text-decoration: underline; }

/* Free Kits Grid */
.kits-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.kit-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.kit-card a { color: var(--foreground); text-decoration: none; font-weight: 600; font-size: 13px; }
.kit-card a:hover { text-decoration: underline; }

/* Filters / Inputs (shadcn/ui Input & Select) */
.controls { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.controls select, .controls input {
  background: var(--card);
  color: var(--foreground);
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 7px 11px;
  font-size: 13px;
  box-shadow: var(--shadow-xs);
}
.controls input { min-width: 240px; }
.controls select:focus, .controls input:focus { outline: 2px solid var(--ring); outline-offset: 1px; }

/* Competitor Teardown Detail Cards */
.app-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 18px;
  box-shadow: var(--shadow-xs);
}
.app-head {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
  padding-bottom: 14px;
  margin-bottom: 16px;
}
.app-identity { display: flex; gap: 14px; align-items: center; flex: 1; min-width: 260px; }
.app-identity img { width: 58px; height: 58px; border-radius: 13px; object-fit: cover; border: 1px solid var(--border); cursor: pointer; }
.app-title { font-size: 16px; font-weight: 700; margin: 0; letter-spacing: -0.015em; }
.app-sub { color: var(--muted); font-size: 12.5px; margin: 2px 0 4px 0; }
.score-pill {
  padding: 8px 14px;
  border-radius: 8px;
  background: var(--muted-bg);
  border: 1px solid var(--border);
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.score-pill strong { display: block; font-size: 15px; }
.section-label {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 16px 0 8px 0;
}
.palette-card-img { max-width: 640px; width: 100%; border-radius: 8px; border: 1px solid var(--border); cursor: pointer; }
.video-row { display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-start; }
.video-row video { max-height: 290px; max-width: 480px; border-radius: 8px; border: 1px solid var(--border); background: #000; }
.video-row img.storyboard { max-height: 290px; border-radius: 8px; border: 1px solid var(--border); cursor: pointer; }
.filmstrip { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 8px; }
.frame-tile {
  background: var(--muted-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px;
  flex-shrink: 0;
  width: 158px;
}
.frame-tile img { width: 100%; height: 124px; object-fit: cover; border-radius: 5px; cursor: pointer; display: block; }
.frame-meta {
  font-size: 11px;
  color: var(--muted);
  margin-top: 5px;
  display: flex;
  justify-content: space-between;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.gallery { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 6px; }
.gallery img { height: 210px; width: auto; border-radius: 8px; border: 1px solid var(--border); cursor: pointer; flex-shrink: 0; }
.web-list { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
.web-item {
  background: var(--muted-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 13px;
}
.web-item a { color: var(--foreground); text-decoration: none; font-weight: 600; }
.web-item a:hover { text-decoration: underline; }
.web-snippet { color: var(--muted); font-size: 12px; margin-top: 4px; }
.links-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.links-row a {
  color: var(--foreground);
  text-decoration: none;
  font-size: 12px;
  font-weight: 500;
  padding: 5px 10px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--card);
}
.links-row a:hover { background: var(--muted-bg); }

/* Lightbox */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(9, 9, 11, 0.88);
  display: none;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 24px;
}
.lightbox.open { display: flex; }
.lightbox img { max-width: 94vw; max-height: 85vh; border-radius: 8px; background: #fff; }
.lightbox-caption { color: #f4f4f5; margin-top: 10px; font-size: 13px; }

@media (max-width: 960px) {
  .shell { grid-template-columns: 1fr; }
  aside.sidebar { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--border); }
}
"""

_DASHBOARD_JS = """/* App Teardown Dashboard - Safe DOM renderer using createElement and textContent only */
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

  // Theme toggle (Zinc Light / Zinc Dark)
  var themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      var isDark = document.body.classList.toggle("dark");
      themeToggle.textContent = isDark ? "Light Mode" : "Dark Mode";
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

  // Topbar & Hero
  var campaignLabel = runData.campaign_name || runData.query || "Teardown";
  document.getElementById("crumb-campaign").textContent = campaignLabel;
  document.getElementById("hero-title").textContent = campaignLabel;

  var heroMeta = document.getElementById("hero-meta");
  [
    "Mekanik: " + (runData.query || "Direct Targets"),
    "Teknoloji: " + (brief && brief.selected_tech ? brief.selected_tech.toUpperCase() : "Otomatik"),
    "Bölge: " + String(runData.country || "").toUpperCase() + "/" + (runData.lang || ""),
    "Mod: " + String(ca.dominant_mode || runData.product_mode || "auto").toUpperCase(),
    "Uyumluluk: " + (runData.official_only ? "OFFICIAL APIs ONLY" : "Lokal Araştırma")
  ].forEach(function (t) {
    heroMeta.appendChild(el("span", null, t));
  });

  // Sidebar counters & footer
  var cntComps = document.getElementById("nav-count-comps");
  var cntRefs = document.getElementById("nav-count-refs");
  var cntDom = document.getElementById("nav-count-domain");
  var cntKits = document.getElementById("nav-count-kits");
  if (cntComps) cntComps.textContent = String(comps.length);
  if (cntRefs) cntRefs.textContent = String(domainRefs.length);
  if (cntDom) cntDom.textContent = String(domainEv.length);
  if (cntKits) cntKits.textContent = String(freeKits.length);

  var sfMeta = document.getElementById("sidebar-run-meta");
  if (sfMeta) {
    sfMeta.textContent = (brief && brief.selected_tech ? brief.selected_tech.toUpperCase() + " · " : "") +
      (runData.official_only ? "Official APIs Only" : "Local Research Mode");
  }

  // KPI Grid (Tremor style: clean label, tabular-nums value, muted footnote)
  var kpiGrid = document.getElementById("kpi-grid");
  [
    ["Analiz Edilen Rakip", String(ca.total_competitors || comps.length), "App Store & Google Play"],
    ["Video Kare Kanıtı", String(ca.total_gameplay_frames || 0), "FFmpeg sahne + aralık"],
    ["Gerçek Hayat Görseli", String(domainRefs.length), String(domainEv.length) + " konu kaynağı"],
    ["Ücretsiz Asset Kiti", String(freeKits.length), "CC0 / MIT / SIL OFL"],
    ["Baskın Gelir Modeli", String(ca.dominant_monetization || "-"), "Mağaza + yorum sinyali"],
    ["Ort. Kanıt Skoru", String(ca.avg_evidence_score || 0) + "/100", "Kanıt izlenebilirliği"]
  ].forEach(function (item) {
    var c = el("div", { class: "kpi-card" });
    c.appendChild(el("div", { class: "kpi-label" }, item[0]));
    c.appendChild(el("div", { class: "kpi-val" }, item[1]));
    c.appendChild(el("div", { class: "kpi-sub" }, item[2]));
    kpiGrid.appendChild(c);
  });

  // Idea & Tech Brief Panel
  var ideaPanel = document.getElementById("idea-panel");
  var ideaBody = document.getElementById("idea-body");
  if (brief && (brief.raw_idea || brief.selected_tech || brief.core_subject)) {
    ideaPanel.classList.remove("hidden");
    if (brief.raw_idea) ideaBody.appendChild(el("div", { class: "app-sub" }, "Fikir: " + brief.raw_idea));
    var bRow = el("div", { class: "badges" });
    if (brief.selected_tech) bRow.appendChild(el("span", { class: "badge mode" }, "Teknoloji: " + brief.selected_tech.toUpperCase()));
    if (brief.mechanic_query) bRow.appendChild(el("span", { class: "badge good" }, "Mekanik: " + brief.mechanic_query));
    if (brief.core_subject) bRow.appendChild(el("span", { class: "badge" }, "Gerçek Hayat Konusu: " + brief.core_subject));
    if (brief.theme_label) bRow.appendChild(el("span", { class: "badge warn" }, "Tema: " + brief.theme_label));
    if (Array.isArray(brief.famous_brands) && brief.famous_brands.length > 0) {
      bRow.appendChild(el("span", { class: "badge" }, "Markalar: " + brief.famous_brands.join(", ")));
    }
    ideaBody.appendChild(bRow);
    var docLinks = el("div", { class: "links-row" });
    docLinks.appendChild(el("a", { href: "TASARIM_BLUEPRINT.md" }, "TASARIM_BLUEPRINT.md"));
    docLinks.appendChild(el("a", { href: "PROTOTIP_VE_TAM_SURUM_PLANI.md" }, "PROTOTIP_VE_TAM_SURUM_PLANI.md"));
    docLinks.appendChild(el("a", { href: "DOMAIN_ARASTIRMASI.md" }, "DOMAIN_ARASTIRMASI.md"));
    docLinks.appendChild(el("a", { href: "FREE_ASSET_VE_KIT_REHBERI.md" }, "FREE_ASSET_VE_KIT_REHBERI.md"));
    docLinks.appendChild(el("a", { href: "GENEL_TEARDOWN_RAPORU.md" }, "GENEL_TEARDOWN_RAPORU.md"));
    ideaBody.appendChild(docLinks);
  }

  // TanStack-style Competitor Summary Table
  var tablePanel = document.getElementById("matrix-panel");
  var tableBody = document.getElementById("matrix-tbody");
  if (comps.length > 0 && tablePanel && tableBody) {
    tablePanel.classList.remove("hidden");
    comps.forEach(function (comp) {
      var sig = comp.signals || {};
      var tr = el("tr");

      var tdApp = el("td");
      var appCell = el("div", { class: "table-app-cell" });
      var iconRel = comp.icon_asset && comp.icon_asset.local_path
        ? safeRelUrl("apps/" + comp.folder_name + "/" + comp.icon_asset.local_path)
        : "";
      if (iconRel) {
        var im = el("img", { src: iconRel, alt: comp.title, loading: "lazy" });
        im.addEventListener("click", function () { openLightbox(iconRel, comp.title); });
        appCell.appendChild(im);
      }
      var nameWrap = el("div");
      nameWrap.appendChild(el("div", null, comp.title));
      nameWrap.appendChild(el("div", { class: "app-sub", style: { margin: "0" } }, comp.developer || ""));
      appCell.appendChild(nameWrap);
      tdApp.appendChild(appCell);
      tr.appendChild(tdApp);

      var tdStore = el("td");
      tdStore.appendChild(el("span", { class: "badge " + (comp.store === "apple_app_store" ? "ios" : "gp") }, comp.store === "apple_app_store" ? "iOS" : "Android"));
      tr.appendChild(tdStore);

      tr.appendChild(el("td", null, sig.monetization_model || "-"));
      tr.appendChild(el("td", { style: { fontVariantNumeric: "tabular-nums" } }, String(comp.rating || 0) + " ★ (" + Number(comp.ratings_count || 0).toLocaleString() + ")"));

      var framesCnt = (comp.youtube_videos || []).reduce(function (acc, v) { return acc + (v.frames || []).length; }, 0);
      tr.appendChild(el("td", { style: { fontVariantNumeric: "tabular-nums" } }, String(framesCnt) + " kare"));

      var tdPal = el("td");
      var swRow = el("div", { class: "swatches" });
      (comp.combined_palette || []).slice(0, 5).forEach(function (sw) {
        if (sw && /^#[0-9A-Fa-f]{6}$/.test(sw.hex)) {
          swRow.appendChild(el("span", { class: "swatch", title: sw.hex, style: { backgroundColor: sw.hex } }));
        }
      });
      tdPal.appendChild(swRow);
      tr.appendChild(tdPal);

      var tdScore = el("td");
      var scoreVal = Number(sig.evidence_score || 0);
      var sbWrap = el("div", { class: "score-bar-wrap" });
      var bar = el("div", { class: "score-bar" });
      bar.appendChild(el("div", { class: "score-bar-fill", style: { width: Math.min(100, Math.max(0, scoreVal)) + "%" } }));
      sbWrap.appendChild(bar);
      sbWrap.appendChild(el("span", null, scoreVal + "/100"));
      tdScore.appendChild(sbWrap);
      tr.appendChild(tdScore);

      tableBody.appendChild(tr);
    });
  }

  // Real-World & Famous Brand Visual Reference Gallery Panel
  var domainRefsPanel = document.getElementById("domain-refs-panel");
  var domainRefsOverview = document.getElementById("domain-refs-overview");
  var domainRefsGrid = document.getElementById("domain-refs-grid");
  var refCatFilter = document.getElementById("ref-cat-filter");
  var refCatNames = {
    anatomy_layers: "Anatomi / Katman",
    how_its_made: "Nasıl Yapılır / Süreç",
    real_world_equivalent: "Gerçek Hayat",
    famous_brand: "Ünlü Marka"
  };
  var refCatBadgeClass = {
    anatomy_layers: "good",
    how_its_made: "warn",
    real_world_equivalent: "mode",
    famous_brand: ""
  };
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
      var cap = r.evidence_id + " · " + (r.subject_label || r.title || "") + " (" + (refCatNames[r.category] || r.category) + ")";
      img.addEventListener("click", function () { openLightbox(rel, cap); });
      card.appendChild(img);
      card.appendChild(el("div", { class: "ref-title", title: r.subject_label || r.title }, r.subject_label || r.title));
      var rb = el("div", { class: "badges" });
      rb.appendChild(el("span", { class: "badge " + (refCatBadgeClass[r.category] || "") }, refCatNames[r.category] || r.category));
      rb.appendChild(el("span", { class: "badge" }, r.evidence_id));
      if (r.width && r.height) rb.appendChild(el("span", { class: "badge" }, r.width + "x" + r.height));
      card.appendChild(rb);
      if (Array.isArray(r.dominant_colors) && r.dominant_colors.length > 0) {
        var swRow = el("div", { class: "swatches" });
        r.dominant_colors.slice(0, 4).forEach(function (hx) {
          if (/^#[0-9A-Fa-f]{6}$/.test(hx)) {
            swRow.appendChild(el("span", { class: "swatch", title: hx, style: { backgroundColor: hx } }));
          }
        });
        card.appendChild(swRow);
      }
      var ext = safeExternalUrl(r.page_url || r.source_url);
      if (ext) {
        card.appendChild(el("a", { href: ext, target: "_blank", rel: "noopener noreferrer" }, (r.domain || r.source_engine || "Kaynak") + " ↗"));
      }
      domainRefsGrid.appendChild(card);
    });
  }
  if (domainRefs.length > 0) {
    domainRefsPanel.classList.remove("hidden");
    var sheetRel = safeRelUrl(runData.domain_reference_sheet_path || "");
    if (sheetRel) {
      var shImg = el("img", { src: sheetRel, alt: "Real-World Reference Moodboard", loading: "lazy" });
      shImg.addEventListener("click", function () { openLightbox(sheetRel, "Gerçek Hayat & Ünlü Marka Moodboard Panosu"); });
      domainRefsOverview.appendChild(shImg);
    }
    var domPalRel = safeRelUrl(runData.domain_palette_card_path || "");
    if (domPalRel) {
      var dpImg = el("img", { src: domPalRel, alt: "Real-World Subject Color Palette", loading: "lazy" });
      dpImg.addEventListener("click", function () { openLightbox(domPalRel, "Gerçek Hayat Konu Renk Paleti"); });
      domainRefsOverview.appendChild(dpImg);
    }
    refCatFilter.addEventListener("change", renderDomainRefs);
    renderDomainRefs();
  }

  // Domain Research Text Evidence Panel
  var domainPanel = document.getElementById("domain-panel");
  var domainList = document.getElementById("domain-list");
  var domCatNames = {
    what_is_it: "Nedir",
    how_its_made: "Nasıl Yapılır",
    anatomy_layers: "Katman / Anatomi",
    famous_brands: "Ünlü Markalar",
    real_world_equivalent: "Gerçek Hayat",
    general: "Genel"
  };
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
      var metaLabel = " (" + (domCatNames[d.category] || d.category || "Konu") + " · " + (d.source_engine || d.domain || "") + ")";
      li.appendChild(el("span", { class: "app-sub" }, metaLabel));
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

  // Filters & Competitor Cards
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
      badges.appendChild(el("span", { class: "badge mode" }, String(comp.product_mode || "game").toUpperCase()));
      badges.appendChild(el("span", { class: "badge" }, sig.monetization_model || "-"));
      badges.appendChild(el("span", { class: "badge" }, String(comp.rating || 0) + " ★ (" + Number(comp.ratings_count || 0).toLocaleString() + ")"));
      if (comp.installs) badges.appendChild(el("span", { class: "badge" }, comp.installs));
      if (comp.iap_price_range) badges.appendChild(el("span", { class: "badge" }, "IAP: " + comp.iap_price_range));
      tcol.appendChild(badges);
      ident.appendChild(tcol);
      head.appendChild(ident);

      var scorePill = el("div", { class: "score-pill" });
      scorePill.appendChild(el("strong", null, "Kanıt " + String(sig.evidence_score || 0) + "/100"));
      scorePill.appendChild(el("span", { class: "app-sub", style: { margin: "0" } }, "Pop: " + String(sig.popularity_score || 0)));
      head.appendChild(scorePill);
      card.appendChild(head);

      var sigBadges = el("div", { class: "badges" });
      (sig.detected_ad_formats || []).forEach(function (a) { sigBadges.appendChild(el("span", { class: "badge warn" }, "Ad: " + a)); });
      (sig.retention_hooks || []).forEach(function (r) { sigBadges.appendChild(el("span", { class: "badge good" }, "Retention: " + r)); });
      Object.keys(sig.ux_friction_themes || {}).forEach(function (f) {
        sigBadges.appendChild(el("span", { class: "badge danger" }, "Friction: " + f + " (" + sig.ux_friction_themes[f] + ")"));
      });
      if (sigBadges.childNodes.length > 0) {
        card.appendChild(el("div", { class: "section-label" }, "Monetizasyon, Retention & Sürtünme Sinyalleri"));
        card.appendChild(sigBadges);
      }

      if (comp.palette_card_path) {
        var palRel = safeRelUrl("apps/" + comp.folder_name + "/" + comp.palette_card_path);
        if (palRel) {
          card.appendChild(el("div", { class: "section-label" }, "Çıkarılan Renk Paleti"));
          var palImg = el("img", { class: "palette-card-img", src: palRel, alt: "Color Palette Card", loading: "lazy" });
          palImg.addEventListener("click", function () { openLightbox(palRel, comp.title + " - Renk Paleti"); });
          card.appendChild(palImg);
        }
      }

      (comp.youtube_videos || []).forEach(function (vid, vIdx) {
        card.appendChild(el("div", { class: "section-label" }, "Video #" + (vIdx + 1) + ": " + (vid.title || "Gameplay") + " (" + (vid.frames || []).length + " kare)"));
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
          card.appendChild(el("div", { class: "section-label" }, "Kare Kare Zaman Çizelgesi"));
          var strip = el("div", { class: "filmstrip" });
          frames.forEach(function (kf) {
            var fRel = safeRelUrl("apps/" + comp.folder_name + "/" + kf.local_path);
            if (!fRel) return;
            var tile = el("div", { class: "frame-tile" });
            var fimg = el("img", { src: fRel, alt: "Frame " + kf.index, loading: "lazy" });
            var cap = comp.title + " - Frame #" + kf.index + " @" + kf.timestamp_label + " [" + kf.phase_hint + " | " + kf.source + "]";
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
        card.appendChild(el("div", { class: "section-label" }, "Mağaza Ekran Görüntüleri (" + shots.length + ")"));
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
        card.appendChild(el("div", { class: "section-label" }, "Web Araştırma Kanıtları (" + webEv.length + ")"));
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
      links.appendChild(el("a", { href: safeRelUrl("apps/" + comp.folder_name + "/teardown_report.md") }, "teardown_report.md"));
      links.appendChild(el("a", { href: safeRelUrl("apps/" + comp.folder_name + "/web_research.md") }, "web_research.md"));
      links.appendChild(el("a", { href: safeRelUrl("apps/" + comp.folder_name + "/store_metadata.md") }, "store_metadata.md"));
      links.appendChild(el("a", { href: safeRelUrl("apps/" + comp.folder_name + "/evidence.json") }, "evidence.json"));
      var storeExt = safeExternalUrl(comp.store_url);
      if (storeExt) links.appendChild(el("a", { href: storeExt, target: "_blank", rel: "noopener noreferrer" }, "Mağaza ↗"));
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
  <title>App Teardown Dashboard</title>
  <link rel="stylesheet" href="dashboard.css">
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand-box">
        <div class="brand-mark">AT</div>
        <div>
          <div class="brand-title">App Teardown</div>
          <div class="brand-ver">Research Workspace · v1.3</div>
        </div>
      </div>

      <div>
        <div class="nav-group-label">Araştırma</div>
        <ul class="nav-list">
          <li><a class="nav-link active" href="#overview"><span>Genel Bakış</span></a></li>
          <li><a class="nav-link" href="#matrix-panel"><span>Rakip Matrisi</span><span class="nav-count" id="nav-count-comps">0</span></a></li>
          <li><a class="nav-link" href="#domain-refs-panel"><span>Gerçek Hayat &amp; Markalar</span><span class="nav-count" id="nav-count-refs">0</span></a></li>
          <li><a class="nav-link" href="#domain-panel"><span>Konu Kaynakları</span><span class="nav-count" id="nav-count-domain">0</span></a></li>
          <li><a class="nav-link" href="#kits-panel"><span>Ücretsiz Kitler</span><span class="nav-count" id="nav-count-kits">0</span></a></li>
          <li><a class="nav-link" href="#competitors-section"><span>Kare Kare İnceleme</span></a></li>
        </ul>
      </div>

      <div>
        <div class="nav-group-label">Raporlar</div>
        <ul class="nav-list">
          <li><a class="nav-link" href="GENEL_TEARDOWN_RAPORU.md"><span>Genel Rapor</span></a></li>
          <li><a class="nav-link" href="DOMAIN_ARASTIRMASI.md"><span>Domain Araştırması</span></a></li>
          <li><a class="nav-link" href="FREE_ASSET_VE_KIT_REHBERI.md"><span>Ücretsiz Kitler</span></a></li>
          <li><a class="nav-link" href="TASARIM_BLUEPRINT.md"><span>Tasarım Blueprint</span></a></li>
          <li><a class="nav-link" href="PROTOTIP_VE_TAM_SURUM_PLANI.md"><span>Prototip &amp; Tam Sürüm</span></a></li>
        </ul>
      </div>

      <div class="sidebar-footer">
        <div class="sf-title">Lokal Çalışma Alanı</div>
        <div class="sf-meta" id="sidebar-run-meta">Local Research Mode</div>
      </div>
    </aside>

    <div class="workspace">
      <header class="topbar">
        <div class="breadcrumbs">
          <span class="crumb-muted">Campaigns</span>
          <span class="crumb-sep">/</span>
          <span class="crumb-active" id="crumb-campaign">Teardown</span>
        </div>
        <div class="topbar-actions">
          <button type="button" class="btn" id="theme-toggle">Dark Mode</button>
          <a class="btn btn-primary" href="PROTOTIP_VE_TAM_SURUM_PLANI.md">Prototip Planı</a>
        </div>
      </header>

      <div class="main-inner" id="overview">
        <div class="page-header">
          <div>
            <h1 id="hero-title">Ürün Teardown Raporu</h1>
            <div class="page-meta" id="hero-meta"></div>
          </div>
        </div>

        <section class="kpi-grid" id="kpi-grid"></section>

        <section class="panel hidden" id="idea-panel">
          <div class="panel-header">
            <div>
              <h2>Fikir Özeti, Mekanik / Konu Ayrımı ve Raporlar</h2>
              <p class="panel-desc">Seçilen teknoloji yığını, rakip mekanik sorgusu ve gerçek hayat araştırma ekseni.</p>
            </div>
          </div>
          <div id="idea-body"></div>
        </section>

        <section class="panel hidden" id="matrix-panel">
          <div class="panel-header">
            <div>
              <h2>Rakip Karşılaştırma Matrisi</h2>
              <p class="panel-desc">Popülerlik, gelir modeli, çıkarılan video kareleri, baskın renkler ve kanıt tamlık skoru.</p>
            </div>
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Uygulama / Oyun</th>
                  <th>Mağaza</th>
                  <th>Gelir Modeli</th>
                  <th>Puan</th>
                  <th>Kare</th>
                  <th>Baskın Palet</th>
                  <th>Kanıt Skoru</th>
                </tr>
              </thead>
              <tbody id="matrix-tbody"></tbody>
            </table>
          </div>
        </section>

        <section class="panel hidden" id="domain-refs-panel">
          <div class="panel-header">
            <div>
              <h2>Gerçek Hayat &amp; Ünlü Marka Görsel Referansları</h2>
              <p class="panel-desc">Anatomi, hazırlanma süreci ve marka silüeti incelemesi için indirilen referanslar.</p>
            </div>
            <div class="controls">
              <select id="ref-cat-filter" aria-label="Referans Kategorisi">
                <option value="all">Tüm Referanslar</option>
                <option value="anatomy_layers">Katman / Anatomi</option>
                <option value="how_its_made">Nasıl Yapılır / Süreç</option>
                <option value="real_world_equivalent">Gerçek Hayat Karşılığı</option>
                <option value="famous_brand">Ünlü Markalar</option>
              </select>
            </div>
          </div>
          <p class="disclaimer-note">Yalnızca görsel araştırma, katman/anatomi ve renk referansı içindir. Ünlü marka logolarını veya telifli fotoğrafları kopyalama; özgün stilize varlıklar üret.</p>
          <div class="ref-overview" id="domain-refs-overview"></div>
          <div class="ref-grid" id="domain-refs-grid"></div>
        </section>

        <section class="panel hidden" id="domain-panel">
          <div class="panel-header">
            <div>
              <h2>Gerçek Dünya Konu Kanıtları</h2>
              <p class="panel-desc">Nedir, nasıl yapılır, katman sırası ve ünlü gerçek hayat markaları.</p>
            </div>
          </div>
          <ul class="web-list" id="domain-list"></ul>
        </section>

        <section class="panel hidden" id="kits-panel">
          <div class="panel-header">
            <div>
              <h2>Ücretsiz UI/UX, 3D/2D Model, Ses &amp; SDK Kitleri</h2>
              <p class="panel-desc">Seçilen teknolojiye ve temaya uygun doğrulanmış açık lisanslı üretim paketleri.</p>
            </div>
            <div class="controls">
              <select id="kit-cat-filter" aria-label="Kit Kategorisi">
                <option value="all">Tüm Kitler</option>
                <option value="ui_ux">UI / UX Kitleri</option>
                <option value="models_sprites">3D / 2D Modeller</option>
                <option value="audio_sfx">Ses / SFX Kitleri</option>
                <option value="fonts">Fontlar</option>
                <option value="engine_sdk">Teknoloji SDK / Eklentiler</option>
              </select>
            </div>
          </div>
          <div class="kits-grid" id="kits-grid"></div>
        </section>

        <section class="panel">
          <div class="panel-header">
            <div>
              <h2>Rakip İkon &amp; Renk Paleti Duvarı</h2>
              <p class="panel-desc">Kategorideki görsel renk yoğunlaşmasını yan yana karşılaştır.</p>
            </div>
          </div>
          <div class="palette-wall" id="palette-wall"></div>
        </section>

        <section id="competitors-section">
          <div class="panel panel-compact">
            <div class="panel-header panel-header-flat">
              <div>
                <h2>Rakip Detayları &amp; Kare Kare Analiz</h2>
                <p class="panel-desc">Mağaza, mod, sıralama veya anahtar kelimeyle rakipleri filtrele.</p>
              </div>
              <div class="controls">
                <select id="store-filter" aria-label="Mağaza Filtresi">
                  <option value="all">Tüm Mağazalar</option>
                  <option value="google_play">Google Play</option>
                  <option value="apple_app_store">Apple App Store</option>
                </select>
                <select id="mode-filter" aria-label="Mod Filtresi">
                  <option value="all">Tüm Modlar</option>
                  <option value="game">Oyun (Game)</option>
                  <option value="app">Uygulama (App)</option>
                </select>
                <select id="sort-by" aria-label="Sıralama">
                  <option value="popularity">Popülerlik</option>
                  <option value="evidence">Kanıt Skoru</option>
                  <option value="rating">Puan</option>
                  <option value="frames">Kare Sayısı</option>
                </select>
                <input id="search-box" type="search" placeholder="Uygulama, geliştirici veya model ara...">
              </div>
            </div>
          </div>
          <main id="apps-container"></main>
        </section>
      </div>
    </div>
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

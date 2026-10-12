/* ==========================================================================
   AMAL — Sélecteur de langue (français · anglais · wolof)
   --------------------------------------------------------------------------
   Le français est la langue de référence : le contenu de index.html est en
   français. Les traductions vivent dans assets/js/i18n-data.js, généré par
   tools/i18n_build.py à partir de tools/i18n/translations-en.txt et
   translations-wo.txt.

   Au chargement, chaque texte affiché (nœuds de texte, attributs alt /
   placeholder / aria-label / title, titre et métadonnées) est mis en cache
   puis remplacé par sa traduction. Revenir au français restaure le texte
   d'origine au caractère près : aucune perte, aucune mutation du HTML.

   Langue choisie :
     1. paramètre d'URL  ?lang=en  (utile pour partager un lien)
     2. préférence mémorisée (localStorage)
     3. français par défaut (langue de référence du site)
   L'adresse est tenue à jour (?lang=en / ?lang=wo) pour que le lien partagé
   rouvre la même langue.
   ========================================================================== */
(function () {
  "use strict";

  var DATA = window.AMAL_I18N_DATA;
  if (!DATA || !DATA.fr || !DATA.fr.length) return;

  var LANGS = ["fr", "en", "wo"];
  var STORAGE_KEY = "amal-lang";
  var ATTRS = ["alt", "placeholder", "aria-label", "title"];
  var META_SELECTORS = [
    ['meta[name="description"]', "description"],
    ['meta[name="keywords"]', "keywords"],
    ['meta[property="og:title"]', "og:title"],
    ['meta[property="og:description"]', "og:description"],
    ['meta[property="og:image:alt"]', "og:image:alt"]
  ];

  /* ---------- 1. Outils ---------- */
  function normalize(value) {
    return String(value == null ? "" : value)
      .replace(/\u00a0/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function buildMap(code) {
    var dict = (DATA.translations || {})[code] || {};
    var map = Object.create(null);
    DATA.fr.forEach(function (source) {
      var translated = dict[source];
      if (typeof translated === "string" && translated.length) map[source] = translated;
    });
    return map;
  }

  var maps = { en: buildMap("en"), wo: buildMap("wo") };

  /* ---------- 2. Inventaire de la page (fait une seule fois) ---------- */
  var textNodes = [];
  var attrNodes = [];
  var metaNodes = [];
  var collected = false;

  function isSkipped(element) {
    if (!element || element.nodeType !== 1) return true;
    var tag = element.nodeName.toLowerCase();
    if (tag === "script" || tag === "style") return true;
    if (typeof element.closest === "function") {
      if (element.closest("svg")) return true;
      if (element.closest("[data-no-i18n]")) return true;
    }
    return false;
  }

  function collectTextNodes() {
    if (typeof document.createTreeWalker !== "function") return;
    var filter = {
      acceptNode: function (node) {
        if (!normalize(node.nodeValue)) return NodeFilter.FILTER_REJECT;
        return isSkipped(node.parentNode) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
      }
    };
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, filter, false);
    var current;
    while ((current = walker.nextNode())) {
      textNodes.push({ node: current, original: current.nodeValue });
    }
  }

  function collectAttributes() {
    var selector = ATTRS.map(function (name) { return "[" + name + "]"; }).join(",");
    Array.prototype.forEach.call(document.querySelectorAll(selector), function (element) {
      if (isSkipped(element)) return;
      ATTRS.forEach(function (name) {
        var value = element.getAttribute(name);
        if (value && normalize(value)) {
          attrNodes.push({ element: element, name: name, original: value });
        }
      });
    });
  }

  function collectMetadata() {
    metaNodes.push({ kind: "title", original: document.title });
    META_SELECTORS.forEach(function (pair) {
      var element = document.querySelector(pair[0]);
      if (element && element.getAttribute("content")) {
        metaNodes.push({ element: element, kind: pair[1], original: element.getAttribute("content") });
      }
    });
  }

  function collect() {
    if (collected) return;
    collectTextNodes();
    collectAttributes();
    collectMetadata();
    collected = true;
  }

  /* ---------- 3. Application d'une langue ---------- */
  function lookup(value, code) {
    if (code === "fr") return null;
    var map = maps[code];
    if (!map) return null;
    var found = map[normalize(value)];
    return typeof found === "string" ? found : null;
  }

  function applyLanguage(code) {
    var active = LANGS.indexOf(code) === -1 ? "fr" : code;
    collect();

    textNodes.forEach(function (entry) {
      var translated = lookup(entry.original, active);
      if (translated === null) {
        if (entry.node.nodeValue !== entry.original) entry.node.nodeValue = entry.original;
        return;
      }
      var lead = (/^\s*/.exec(entry.original) || [""])[0];
      var tail = (/\s*$/.exec(entry.original) || [""])[0];
      entry.node.nodeValue = lead + translated + tail;
    });

    attrNodes.forEach(function (entry) {
      var translated = lookup(entry.original, active);
      entry.element.setAttribute(entry.name, translated === null ? entry.original : translated);
    });

    metaNodes.forEach(function (entry) {
      var translated = lookup(entry.original, active);
      var value = translated === null ? entry.original : translated;
      if (entry.kind === "title") document.title = value;
      else entry.element.setAttribute("content", value);
    });

    document.documentElement.setAttribute("lang", active);
    current = active;

    try {
      window.localStorage.setItem(STORAGE_KEY, active);
    } catch (error) {
      /* navigation privée : on ignore */
    }

    syncSwitcher(active);
    renderVariantNote(active);
    syncUrl(active);
    window.AMAL_LANG = active;
    document.dispatchEvent(new CustomEvent("amal:language", { detail: { lang: active } }));
  }

  /* ---------- 4. Bandeau « variante de langue » ----------
     L'anglais et le wolof sont des versions secondaires : un bandeau discret le
     rappelle et permet de revenir au français, langue de référence.             */
  var VARIANT_NOTES = {
    en: {
      text: "English version — the French version is the reference.",
      back: "Read in French"
    },
    wo: {
      text: "Wersiyoŋ bu wolof — wersiyoŋ bu frãs bi moo gëna am solo.",
      back: "Jàng ci farañse"
    }
  };

  function renderVariantNote(code) {
    var existing = document.querySelector(".lang-note");
    var info = VARIANT_NOTES[code];
    if (!info) {
      if (existing) existing.parentNode.removeChild(existing);
      return;
    }
    if (existing && existing.getAttribute("data-lang") === code) return;
    if (existing) existing.parentNode.removeChild(existing);

    var note = document.createElement("div");
    note.className = "lang-note";
    note.setAttribute("data-lang", code);
    note.setAttribute("data-no-i18n", "");
    note.setAttribute("role", "note");

    var text = document.createElement("span");
    text.textContent = info.text;
    note.appendChild(text);

    var back = document.createElement("button");
    back.type = "button";
    back.className = "lang-note__back";
    back.textContent = info.back;
    note.appendChild(back);

    var main = document.querySelector("main");
    if (main && main.parentNode) main.parentNode.insertBefore(note, main);
    else document.body.appendChild(note);
  }

  /* ---------- 5. Sélecteur de langue ---------- */
  var current = "fr";

  /* L'adresse reflète la langue : ?lang=en / ?lang=wo restent partageables. */
  function syncUrl(code) {
    if (!window.history || typeof window.history.replaceState !== "function") return;
    try {
      var url = new URL(window.location.href);
      if (code === "fr") url.searchParams.delete("lang");
      else url.searchParams.set("lang", code);
      window.history.replaceState(null, "", url.toString());
    } catch (error) {
      /* ancien navigateur : on ignore, la langue reste active */
    }
  }

  function syncSwitcher(code) {
    Array.prototype.forEach.call(document.querySelectorAll(".lang__btn"), function (button) {
      var active = button.getAttribute("data-lang") === code;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    var label = document.getElementById("langCurrent");
    if (label) label.textContent = code.toUpperCase();
  }

  function bindSwitcher() {
    document.addEventListener("click", function (event) {
      var target = event.target;
      if (!target || typeof target.closest !== "function") return;
      var button = target.closest(".lang__btn") || target.closest(".lang-note__back");
      if (!button) return;
      event.preventDefault();
      applyLanguage(button.getAttribute("data-lang") || "fr");
    });
  }

  function initialLanguage() {
    var fromUrl = null;
    try {
      fromUrl = new URLSearchParams(window.location.search).get("lang");
    } catch (error) {
      fromUrl = null;
    }
    if (fromUrl && LANGS.indexOf(fromUrl) !== -1) return fromUrl;

    var stored = null;
    try {
      stored = window.localStorage.getItem(STORAGE_KEY);
    } catch (error) {
      stored = null;
    }
    if (stored && LANGS.indexOf(stored) !== -1) return stored;

    /* Le français reste la langue par défaut : le visiteur choisit explicitement
       l'anglais ou le wolof via le sélecteur (ou un lien ?lang=xx). */
    return "fr";
  }

  /* ---------- 5. Utilitaire exposé aux autres scripts ---------- */
  /* window.AMAL_T("texte français") renvoie la traduction courante. */
  window.AMAL_T = function (frenchText) {
    var translated = lookup(frenchText, current);
    return translated === null ? frenchText : translated;
  };

  /* ---------- 6. Démarrage ---------- */
  function start() {
    bindSwitcher();
    var code = initialLanguage();
    if (code === "fr") {
      syncSwitcher("fr");
      renderVariantNote("fr");
      window.AMAL_LANG = "fr";
    } else {
      applyLanguage(code);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();

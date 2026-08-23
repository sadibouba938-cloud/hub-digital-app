/**
 * hub-digital-site — Logique du site (menu, i18n, animations, formulaire)
 */
(function () {
  "use strict";

  var SUPPORTED = ["fr", "en", "ar"];
  var STORAGE_KEY = "hubDigitalLang";
  var DEFAULT_LANG = "fr";

  /* ---------- Détection de la langue ---------- */
  function detectLanguage() {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (saved && SUPPORTED.indexOf(saved) !== -1) return saved;
    } catch (e) {
      /* localStorage indisponible */
    }
    var nav = (navigator.language || "fr").toLowerCase().split("-")[0];
    return SUPPORTED.indexOf(nav) !== -1 ? nav : DEFAULT_LANG;
  }

  /* ---------- Application de la langue ---------- */
  function applyLanguage(lang) {
    if (SUPPORTED.indexOf(lang) === -1) lang = DEFAULT_LANG;
    var t = I18N[lang];
    if (!t) return;

    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    document.title = t["meta.title"];
    var metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) metaDesc.setAttribute("content", t["meta.desc"]);

    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      if (t[key] != null) el.textContent = t[key];
    });
    document.querySelectorAll("[data-i18n-ph]").forEach(function (el) {
      var key = el.getAttribute("data-i18n-ph");
      if (t[key] != null) el.placeholder = t[key];
    });
    document.querySelectorAll(".lang-btn").forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-lang") === lang);
    });

    var backToTop = document.getElementById("backToTop");
    if (backToTop) {
      backToTop.title = t.backToTop;
      backToTop.setAttribute("aria-label", t.backToTop);
    }

    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {
      /* ignore */
    }
  }

  /* ---------- Menu mobile ---------- */
  function initMenu() {
    var toggle = document.getElementById("menuToggle");
    var links = document.getElementById("navLinks");
    if (!toggle || !links) return;

    function closeMenu() {
      links.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.textContent = "☰";
    }

    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.textContent = open ? "✕" : "☰";
    });

    links.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", closeMenu);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeMenu();
    });
  }

  /* ---------- Sélecteur de langue ---------- */
  function initLangSwitch() {
    document.querySelectorAll(".lang-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyLanguage(btn.getAttribute("data-lang"));
      });
    });
  }

  /* ---------- FAQ (accordéon) ---------- */
  function initFaq() {
    document.querySelectorAll(".faq-item").forEach(function (item) {
      var btn = item.querySelector(".faq-q");
      if (!btn) return;
      btn.addEventListener("click", function () {
        var open = item.classList.toggle("open");
        btn.setAttribute("aria-expanded", String(open));
      });
    });
  }

  /* ---------- Apparition au scroll ---------- */
  function initReveal() {
    var els = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window)) {
      els.forEach(function (el) {
        el.classList.add("visible");
      });
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    els.forEach(function (el) {
      io.observe(el);
    });
  }

  /* ---------- Compteurs animés (stats) ---------- */
  function animateCounter(el) {
    var target = parseInt(el.getAttribute("data-count"), 10) || 0;
    var duration = 1200;
    var start = null;

    function tick(now) {
      if (start === null) start = now;
      var progress = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(target * eased);
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function initCounters() {
    var counters = document.querySelectorAll(".stat-value");
    if (!counters.length) return;
    if (!("IntersectionObserver" in window)) {
      counters.forEach(function (c) {
        c.textContent = c.getAttribute("data-count");
      });
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.4 }
    );
    counters.forEach(function (c) {
      io.observe(c);
    });
  }

  /* ---------- Surlignage du lien actif (scrollspy) ---------- */
  function initScrollspy() {
    var sections = document.querySelectorAll("main section[id]");
    if (!sections.length || !("IntersectionObserver" in window)) return;
    var links = document.querySelectorAll('.nav-links a[href^="#"]');
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var id = "#" + entry.target.id;
            links.forEach(function (link) {
              link.classList.toggle("active", link.getAttribute("href") === id);
            });
          }
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach(function (s) {
      io.observe(s);
    });
  }

  /* ---------- Header + bouton retour en haut ---------- */
  function initScrollUI() {
    var header = document.getElementById("siteHeader");
    var backToTop = document.getElementById("backToTop");
    if (!header && !backToTop) return;

    window.addEventListener(
      "scroll",
      function () {
        var y = window.scrollY;
        if (header) header.classList.toggle("scrolled", y > 10);
        if (backToTop) backToTop.classList.toggle("show", y > 500);
      },
      { passive: true }
    );

    if (backToTop) {
      backToTop.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }
  }

  /* ---------- Formulaire de contact ---------- */
  function initForm() {
    var form = document.getElementById("contactForm");
    var success = document.getElementById("formSuccess");
    if (!form) return;

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var name = data.get("name") || "";
      var email = data.get("email") || "";
      var subject = data.get("subject") || "";
      var message = data.get("message") || "";

      var mailto =
        "mailto:contact@hubdigital.com?subject=" +
        encodeURIComponent(subject) +
        "&body=" +
        encodeURIComponent("Nom / Name: " + name + "\nE-mail: " + email + "\n\n" + message);

      if (success) success.hidden = false;
      form.reset();
      window.location.href = mailto;
    });
  }

  /* ---------- Initialisation ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    initMenu();
    initLangSwitch();
    initFaq();
    initReveal();
    initCounters();
    initScrollspy();
    initScrollUI();
    initForm();
    applyLanguage(detectLanguage());

    var year = document.getElementById("year");
    if (year) year.textContent = new Date().getFullYear();
  });
})();

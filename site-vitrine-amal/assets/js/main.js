/* ==========================================================================
   AMAL — Détergents du Sénégal · Interactions du site vitrine
   Menu, filtres produits, FAQ, compteurs, animations, formulaire de devis
   ========================================================================== */
(function () {
  "use strict";

  /* ---------------------------------------------------------------------
     ⚙️ À PERSONNALISER : numéro WhatsApp de l'entreprise (format international,
     sans « + », sans espaces ni tirets)
     --------------------------------------------------------------------- */
  var WHATSAPP_NUMBER = "221771234567";
  var COMPANY_EMAIL = "contact@amal-detergents.sn";

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* ================= 1. Menu mobile ================= */
  function initMenu() {
    var burger = $("#burger");
    var nav = $("#nav");
    if (!burger || !nav) return;

    var close = function () {
      nav.classList.remove("is-open");
      burger.classList.remove("is-open");
      burger.setAttribute("aria-expanded", "false");
      burger.setAttribute("aria-label", "Ouvrir le menu");
    };

    burger.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      burger.classList.toggle("is-open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
      burger.setAttribute("aria-label", open ? "Fermer le menu" : "Ouvrir le menu");
    });

    $$(".nav a").forEach(function (link) { link.addEventListener("click", close); });

    window.addEventListener("keydown", function (e) {
      if (e.key === "Escape") close();
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 900) close();
    });
  }

  /* ================= 2. Header + navigation active ================= */
  function initScrollUi() {
    var header = $("#header");
    var toTop = $("#toTop");
    var sections = $$("main section[id]");
    var links = $$(".nav__link");

    var onScroll = function () {
      var y = window.scrollY || window.pageYOffset;

      if (header) header.classList.toggle("is-scrolled", y > 12);
      if (toTop) toTop.classList.toggle("is-visible", y > 620);

      var current = "";
      sections.forEach(function (sec) {
        if (y >= sec.offsetTop - 140) current = sec.id;
      });
      links.forEach(function (link) {
        link.classList.toggle("is-active",
          link.getAttribute("href") === "#" + current);
      });
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    if (toTop) {
      toTop.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }
  }

  /* ================= 3. Animations à l'apparition ================= */
  function initReveal() {
    var items = $$(".reveal");
    if (!items.length) return;

    if (!("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-in"); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var siblings = $$(".reveal").indexOf(el);
        el.style.transitionDelay = Math.min((siblings % 4) * 70, 210) + "ms";
        el.classList.add("is-in");
        observer.unobserve(el);
      });
    }, { threshold: 0.14, rootMargin: "0px 0px -40px 0px" });

    items.forEach(function (el) { observer.observe(el); });
  }

  /* ================= 4. Compteurs animés ================= */
  function initCounters() {
    var counters = $$("[data-count]");
    if (!counters.length) return;

    var run = function (el) {
      var target = parseFloat(el.getAttribute("data-count")) || 0;
      var duration = 1500;
      var start = null;

      var step = function (ts) {
        if (!start) start = ts;
        var progress = Math.min((ts - start) / duration, 1);
        var eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(target * eased).toLocaleString("fr-FR");
        if (progress < 1) window.requestAnimationFrame(step);
      };
      window.requestAnimationFrame(step);
    };

    if (!("IntersectionObserver" in window)) {
      counters.forEach(run);
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        run(entry.target);
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.5 });

    counters.forEach(function (el) { observer.observe(el); });
  }

  /* ================= 5. Filtres produits ================= */
  function initFilters() {
    var buttons = $$(".filter");
    var products = $$(".product");
    if (!buttons.length) return;

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var filter = btn.getAttribute("data-filter");

        buttons.forEach(function (b) { b.classList.toggle("is-active", b === btn); });

        products.forEach(function (product) {
          var match = filter === "all" || product.getAttribute("data-cat") === filter;
          product.classList.toggle("is-hidden", !match);
        });
      });
    });
  }

  /* ================= 6. Accordéon FAQ ================= */
  function initFaq() {
    var items = $$(".faq__item");
    if (!items.length) return;

    items.forEach(function (item) {
      var button = $(".faq__q", item);
      var answer = $(".faq__a", item);
      if (!button || !answer) return;

      button.addEventListener("click", function () {
        var isOpen = item.classList.contains("is-open");

        // Fermer les autres items (comportement accordéon)
        items.forEach(function (other) {
          other.classList.remove("is-open");
          var otherBtn = $(".faq__q", other);
          var otherAnswer = $(".faq__a", other);
          if (otherBtn) otherBtn.setAttribute("aria-expanded", "false");
          if (otherAnswer) otherAnswer.style.maxHeight = "0px";
        });

        if (!isOpen) {
          item.classList.add("is-open");
          button.setAttribute("aria-expanded", "true");
          answer.style.maxHeight = answer.scrollHeight + 40 + "px";
        }
      });
    });

    window.addEventListener("resize", function () {
      items.forEach(function (item) {
        if (!item.classList.contains("is-open")) return;
        var answer = $(".faq__a", item);
        if (answer) answer.style.maxHeight = answer.scrollHeight + 40 + "px";
      });
    });
  }

  /* ================= 7. Formulaire de devis ================= */
  function renderSuccessMessage(target, waUrl, mailUrl) {
    // Construit le message en DOM (pas d'innerHTML) : aucune donnée saisie
    // par l'utilisateur n'est interprétée comme du HTML.
    target.textContent = "";

    var linkStyle = "color:var(--green-800);font-weight:700";

    target.appendChild(document.createTextNode(
      "Nous ouvrons WhatsApp avec le récapitulatif de votre demande "
    ));

    var wa = document.createElement("a");
    wa.href = waUrl;
    wa.target = "_blank";
    wa.rel = "noopener";
    wa.setAttribute("style", linkStyle);
    wa.textContent = "(cliquez ici si rien ne s'ouvre)";
    target.appendChild(wa);

    target.appendChild(document.createTextNode("."));
    target.appendChild(document.createElement("br"));
    target.appendChild(document.createTextNode("Vous préférez l'e-mail ? "));

    var mail = document.createElement("a");
    mail.href = mailUrl;
    mail.setAttribute("style", linkStyle);
    mail.textContent = "Envoyez votre demande par e-mail";
    target.appendChild(mail);
    target.appendChild(document.createTextNode("."));
  }

  function initForm() {
    var form = $("#devisForm");
    if (!form) return;

    var success = $("#formSuccess");
    var successText = $("#successText");

    var setError = function (field, hasError) {
      if (!field) return;
      var wrapper = field.closest ? field.closest(".field") : null;
      if (wrapper) wrapper.classList.toggle("has-error", hasError);
    };

    var validate = function () {
      var ok = true;

      var required = [
        { el: $("#nom"), test: function (v) { return v.trim().length >= 2; } },
        { el: $("#telephone"), test: function (v) { return v.replace(/[^0-9]/g, "").length >= 9; } },
        { el: $("#ville"), test: function (v) { return v !== ""; } },
        { el: $("#besoin"), test: function (v) { return v !== ""; } },
        { el: $("#consent"), test: function (v, el) { return el.checked; } }
      ];

      required.forEach(function (rule) {
        if (!rule.el) return;
        var valid = rule.test(rule.el.value || "", rule.el);
        setError(rule.el, !valid);
        if (!valid) ok = false;
      });

      var email = $("#email");
      if (email && email.value.trim() !== "") {
        var validEmail = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(email.value.trim());
        setError(email, !validEmail);
        if (!validEmail) ok = false;
      } else if (email) {
        setError(email, false);
      }

      return ok;
    };

    // Nettoyage de l'erreur à la saisie
    $$("input, select, textarea", form).forEach(function (el) {
      var evt = el.type === "checkbox" || el.tagName === "SELECT" ? "change" : "input";
      el.addEventListener(evt, function () { setError(el, false); });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      if (!validate()) {
        var firstError = $(".field.has-error", form);
        if (firstError) {
          firstError.scrollIntoView({ behavior: "smooth", block: "center" });
          var input = $("input, select, textarea", firstError);
          if (input && input.focus) input.focus({ preventScroll: true });
        }
        return;
      }

      var nom = ($("#nom") || {}).value || "";
      var tel = ($("#telephone") || {}).value || "";
      var email = ($("#email") || {}).value || "";
      var ville = ($("#ville") || {}).value || "";
      var besoin = ($("#besoin") || {}).value || "";
      var volume = ($("#volume") || {}).value || "";
      var message = ($("#message") || {}).value || "";

      var lines = [
        "Bonjour AMAL — Détergents du Sénégal,",
        "",
        "Je souhaite recevoir un devis :",
        "• Nom : " + nom,
        "• Téléphone : " + tel,
        email ? "• E-mail : " + email : null,
        "• Zone de livraison : " + ville,
        "• Type de demande : " + besoin,
        volume ? "• Volume estimé : " + volume : null,
        message ? "• Précisions : " + message : null,
        "",
        "Merci de me recontacter."
      ].filter(Boolean);

      var waUrl = "https://wa.me/" + WHATSAPP_NUMBER + "?text=" + encodeURIComponent(lines.join("\n"));
      var mailUrl = "mailto:" + COMPANY_EMAIL +
        "?subject=" + encodeURIComponent("Demande de devis — " + nom + " (" + ville + ")") +
        "&body=" + encodeURIComponent(lines.join("\n"));

      if (success && successText) {
        renderSuccessMessage(successText, waUrl, mailUrl);
        success.classList.add("is-visible");
        success.scrollIntoView({ behavior: "smooth", block: "center" });
      }

      window.open(waUrl, "_blank", "noopener");

      // Réinitialisation après envoi
      form.reset();
      window.setTimeout(function () {
        if (success) success.classList.remove("is-visible");
      }, 20000);
    });
  }

  /* ================= 8. Divers ================= */
  function initMisc() {
    var year = $("#year");
    if (year) year.textContent = new Date().getFullYear();

    // Liens sociaux/placeholder : évite les sauts de page sur les « # »
    $$('a[href="#"]').forEach(function (link) {
      link.addEventListener("click", function (e) { e.preventDefault(); });
    });
  }

  /* ================= Init ================= */
  document.addEventListener("DOMContentLoaded", function () {
    initMenu();
    initScrollUi();
    initReveal();
    initCounters();
    initFilters();
    initFaq();
    initForm();
    initMisc();
  });
})();

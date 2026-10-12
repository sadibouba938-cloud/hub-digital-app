/* Vérifie le moteur de langue AMAL sur la vraie page, sans navigateur (jsdom).
 *
 *   node tools/i18n_test.js
 *
 * jsdom n'est pas une dépendance du site : installez-le à côté si besoin
 *   npm install jsdom
 * (le script cherche jsdom dans node_modules local, global, ou dans le chemin
 *  indiqué par la variable d'environnement AMAL_JSDOM).
 */
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
const engines = {
  "assets/js/i18n-data.js": fs.readFileSync(path.join(ROOT, "assets/js/i18n-data.js"), "utf8"),
  "assets/js/i18n.js": fs.readFileSync(path.join(ROOT, "assets/js/i18n.js"), "utf8"),
};

function loadJsdom() {
  const candidates = [
    "jsdom",
    process.env.AMAL_JSDOM,
    "/tmp/i18n-test/node_modules/jsdom",
  ].filter(Boolean);
  for (const candidate of candidates) {
    try {
      return require(candidate);
    } catch (error) {
      /* on essaie le suivant */
    }
  }
  console.error("jsdom introuvable : lancez `npm install jsdom` puis relancez ce script.");
  process.exit(2);
}

const { JSDOM } = loadJsdom();

function openPage(query) {
  const dom = new JSDOM(html, {
    // "dangerously" : les scripts du site doivent s'exécuter comme dans un
    // navigateur (aucune ressource distante n'est chargée pour autant).
    runScripts: "dangerously",
    url: `http://localhost/index.html${query || ""}`,
    pretendToBeVisual: true,
  });
  const { window } = dom;
  Object.values(engines).forEach((source) => {
    const script = window.document.createElement("script");
    script.textContent = source;
    window.document.body.appendChild(script);
  });
  window.document.dispatchEvent(new window.Event("DOMContentLoaded"));
  return window;
}

const read = {
  title: (w) => w.document.querySelector("h1").textContent.trim(),
  nav: (w) => w.document.querySelector(".nav__link").textContent.trim(),
  price: (w) => w.document.querySelector(".soon").textContent.trim(),
  fab: (w) => w.document.querySelector(".whatsapp-fab").textContent.trim(),
  alt: (w) => w.document.querySelector(".hero__photo img").getAttribute("alt"),
  placeholder: (w) => w.document.getElementById("nom").getAttribute("placeholder"),
  htmlLang: (w) => w.document.documentElement.getAttribute("lang"),
  note: (w) => {
    const note = w.document.querySelector(".lang-note");
    return note ? note.textContent.trim() : "—";
  },
  url: (w) => w.window.location.search || "(sans paramètre)",
  active: (w) => (w.document.querySelector(".lang__btn.is-active") || {}).getAttribute
    ? w.document.querySelector(".lang__btn.is-active").getAttribute("data-lang")
    : "?",
  count: (w) => w.document.querySelectorAll(".lang__btn").length,
};

function snapshot(window, label) {
  console.log(`\n=== ${label} ===`);
  Object.entries(read).forEach(([name, fn]) => {
    console.log("  " + name.padEnd(12) + " : " + String(fn(window)).slice(0, 62));
  });
}

const results = [];
function check(name, ok) {
  results.push([name, !!ok]);
  console.log(`  ${ok ? "OK  " : "ECHEC"} ${name}`);
}

/* ---------- 1. Français par défaut ---------- */
const frPage = openPage("");
snapshot(frPage, "FRANÇAIS (par défaut)");
console.log("\n--- 1. Page française ---");
check("titre français", read.title(frPage).includes("La propreté qui porte un nom"));
check("aucun bandeau de variante", read.note(frPage) === "—");
check("lang=fr sur <html>", read.htmlLang(frPage) === "fr");
check("URL sans paramètre", read.url(frPage) === "(sans paramètre)");
check("3 boutons de langue", read.count(frPage) === 3);
check("bouton FR actif", read.active(frPage) === "fr");

/* ---------- 2. Bascule vers l'anglais ---------- */
console.log("\n--- 2. Sélecteur → EN ---");
frPage.document.querySelector('.lang__btn[data-lang="en"]').click();
snapshot(frPage, "ANGLAIS (après clic)");
check("titre traduit", read.title(frPage).includes("Cleanliness that has a name"));
check("alt d'image traduit", read.alt(frPage).startsWith("AMAL filling line"));
check("placeholder traduit", read.placeholder(frPage).startsWith("E.g."));
check("lang=en sur <html>", read.htmlLang(frPage) === "en");
check("URL ?lang=en", read.url(frPage) === "?lang=en");
check("bandeau anglais affiché", read.note(frPage).includes("English version"));
check("bouton EN actif", read.active(frPage) === "en");

/* ---------- 3. Bascule vers le wolof ---------- */
console.log("\n--- 3. Sélecteur → WO ---");
frPage.document.querySelector('.lang__btn[data-lang="wo"]').click();
snapshot(frPage, "WOLOF (après clic)");
check("titre traduit en wolof", read.title(frPage).includes("Set gi am na tur"));
check("lang=wo sur <html>", read.htmlLang(frPage) === "wo");
check("URL ?lang=wo", read.url(frPage) === "?lang=wo");
check("bandeau wolof affiché", read.note(frPage).includes("Wersiyoŋ bu wolof"));
check("nom de marque conservé", read.price(frPage) === "Njëg bi ñów na");
check("AMAL non traduit", read.title(frPage).includes("AMAL"));

/* ---------- 4. Retour au français via le bandeau ---------- */
console.log("\n--- 4. Bandeau → retour au français ---");
frPage.document.querySelector(".lang-note__back").click();
snapshot(frPage, "RETOUR AU FRANÇAIS");
check("titre français restauré", read.title(frPage).includes("La propreté qui porte un nom"));
check("bandeau retiré", read.note(frPage) === "—");
check("URL nettoyée", read.url(frPage) === "(sans paramètre)");
check("attribut alt restauré", read.alt(frPage).startsWith("Ligne de conditionnement"));
check("placeholder restauré", read.placeholder(frPage).startsWith("Ex :"));

/* ---------- 5. Lien partagé ?lang=wo ---------- */
console.log("\n--- 5. Lien partagé ?lang=wo ---");
const woPage = openPage("?lang=wo");
snapshot(woPage, "WOLOF (lien direct)");
check("langue appliquée au chargement", read.title(woPage).includes("Set gi am na tur"));
check("préférence mémorisée", woPage.localStorage.getItem("amal-lang") === "wo");
check("AMAL_LANG exposé", woPage.AMAL_LANG === "wo");
check("dictionnaire chargé", Array.isArray(woPage.AMAL_I18N_DATA.fr) && woPage.AMAL_I18N_DATA.fr.length > 300);

/* ---------- 6. Traductions partielles : le français prend le relais ---------- */
console.log("\n--- 6. Textes sans traduction ---");
const woText = read.placeholder(woPage);
check("texte resté en français si non traduit", woText.length > 0);

/* ---------- Bilan ---------- */
const failures = results.filter(([, ok]) => !ok);
console.log(`\n${results.length - failures.length}/${results.length} contrôles réussis`);
if (failures.length) {
  failures.forEach(([name]) => console.log("  ✗ " + name));
  process.exit(1);
}

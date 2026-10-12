# 🧼 AMAL — Détergents du Sénégal · Site vitrine

Site vitrine **complet, responsive et 100 % statique** (HTML / CSS / JavaScript, aucune
dépendance) pour une entreprise sénégalaise spécialisée dans la **production de détergents
et de produits d'hygiène**, commercialisés sous la marque **AMAL** (أمل, « l'espoir ») :
liquide vaisselle, lessive, nettoyant multi-usage, javel, savon liquide et dégraissants pro.

> ℹ️ **Catalogue en cours de lancement** : les **prix, fiches techniques et photos définitives**
> sont volontairement affichés « à venir » sur le site. Chaque produit porte un bouton
> **« Demander la fiche »** qui renvoie vers le formulaire de devis, et un bandeau dédié
> explique la situation aux visiteurs.

---

## 🎨 Charte graphique AMAL

| Élément | Choix | Pourquoi |
|---|---|---|
| Bleu profond `#1b4fd8` → `#061c47` | Couleur principale | Confiance, propreté de l'eau — reprend la couleur des étiquettes AMAL |
| Vert émeraude `#12945a` → `#085c33` | Couleur secondaire | Nature, savoir-faire local, gamme vaisselle |
| Or `#f2b233` | Accent | Exigence de qualité, mise en avant des CTA |
| Crème `#fffaf1` / sable `#fdf6ea` | Fonds | Douceur, rappel de la mousse et du linge |
| **Plus Jakarta Sans** | Titres | Géométrique, moderne, très lisible en gras |
| **Inter** | Texte courant | Excellence de lecture sur mobile |
| **Amiri** | Signature arabe **أمل** | Cohérence culturelle du nom de marque (héro & pied de page) |

Le bandeau « La marque AMAL » explique le code couleur par famille : **vert = vaisselle,
bleu = lessive, ambre = dégraissant**.

---

## 🖼️ L'assemblage : rendus 3D AMAL + photos d'usine

Les visuels du site sont le **fruit d'un assemblage** entre les photos réelles de la
production et les rendus 3D des packagings AMAL. Les quatre scènes obtenues habillent
tout le parcours du visiteur :

| Visuel assemblé | Composition | Où il apparaît |
|---|---|---|
| `hero-atelier.jpg` | Ligne de conditionnement + gamme AMAL au premier plan | Accueil (héro) |
| `showcase-gamme-usine.jpg` | Gamme AMAL posée dans l'atelier, ligne en arrière-plan | Bandeau « La marque AMAL » |
| `palette-livraison.jpg` | Équipe en train d'emballer + palette de cartons siglés AMAL | Section « Notre histoire » + fond du bandeau revendeur |
| `labo-amal.jpg` | Technicienne au laboratoire + flacon AMAL Vaisselle Citron | Section « Qualité & process » |

Chaque photo d'atelier reçoit une **légende discrète** en surimpression
(« Notre ligne de conditionnement — Diamniadio », « Contrôle d'un lot en laboratoire »,
« Palettes prêtes à partir pour Dakar et les régions ») qui renforce le sérieux du site.

Les fichiers d'origine sont conservés dans `assets/img/sources/` : ils servent de
matière première (nouvelles compositions, presse, réseaux sociaux) et ne sont pas
appelés par la page.

---

## ✨ Les produits en rendu 3D, étiquetés AMAL

Les 8 références de la gamme sont présentées sous forme de **rendus 3D publicitaires**,
chacun portant l'**étiquette de marque AMAL** sur le packaging :

| # | Référence | Visuel |
|---|---|---|
| 1 | AMAL Vaisselle Citron | `produit-vaisselle.jpg` |
| 2 | AMAL Multi-Usage Fraîcheur (5 L) | `produit-multi-usage.jpg` |
| 3 | AMAL Lessive Poudre Éclat (best-seller) | `produit-lessive-poudre.jpg` |
| 4 | AMAL Lessive Liquide Bleu Océan | `produit-lessive-liquide.jpg` |
| 5 | AMAL Javel Assainissante 12° | `produit-javel.jpg` |
| 6 | AMAL Savon Mains Douceur | `produit-savon-mains.jpg` |
| 7 | AMAL Dégraissant Pro Cuisine | `produit-degraissant.jpg` |
| 8 | AMAL Vaisselle Concentré 20 L (vrac B2B) | `produit-bidon-pro.jpg` |

Plus le visuel de gamme complet `gamme-amal.jpg`, affiché dans le bandeau « La marque ».

**Effet 3D en CSS** : chaque visuel est posé sur une scène (dégradé crème + halo coloré
propre au produit, socle d'ombre au sol) et au survol la bouteille **se soulève, grossit
légèrement et pivote**, avec une pastille « Rendu 3D » dans le coin.

---

## 👀 Structure du site

| Section | Contenu |
|---|---|
| Bandeau supérieur | Téléphone, e-mail, horaires, statut « usine ouverte » |
| En-tête collant | Logo AMAL, navigation, appel direct, menu burger sur mobile |
| Accueil (hero) | Accroche, signature **أمل**, photo de l'usine, chiffres clés animés, encart « catalogue en cours de lancement » |
| Bandeau confiance | Usine locale, prix de gros, livraison, moyens de paiement |
| **La gamme AMAL** | 8 produits 3D filtrables (maison, lessive, hygiène, pro), badges « Rendu 3D », pilules **« Prix à venir »** + encart explicatif |
| La marque | Charte, code couleur par famille, potentiel marque blanche + visuel de gamme |
| Services | Production à façon, vrac B2B, livraison nationale, formulation sur mesure + CTA revendeur |
| L'entreprise | Histoire, origine du nom AMAL, équipe (28 emplois) |
| Qualité & process | 5 étapes de fabrication, laboratoire interne, indicateurs |
| Livraison | Zones du Sénégal avec délais + carte Google Maps (Diamniadio) |
| Témoignages / FAQ | 3 avis clients, 6 questions en accordéon (dont « quand les prix seront-ils disponibles ? ») |
| Devis | Formulaire validé en JS → récapitulatif envoyé via **WhatsApp** ou e-mail, avec l'option « être informé du lancement » |
| Pied de page + flottants | Coordonnées, NINEA, réseaux sociaux, bouton WhatsApp permanent, retour en haut |

---

## 📁 Structure des fichiers

```
site-vitrine-amal/
├── index.html                  # page unique complète (contenu français de référence)
├── en/index.html               # entrée « version anglaise » → index.html?lang=en
├── wo/index.html               # entrée « version wolof » → index.html?lang=wo
├── serve_preview.py            # serveur local de prévisualisation (Python standard)
├── tools/
│   ├── i18n_build.py           # génère i18n-data.js + la table de référence
│   ├── i18n_test.js            # tests du moteur de langue (jsdom, optionnel)
│   └── i18n/                   # traductions à saisir + table de relecture
└── assets/
    ├── css/style.css           # charte AMAL complète + scènes 3D + responsive
    ├── js/main.js              # menu, filtres, FAQ, compteurs, formulaire de devis
    ├── js/i18n-data.js         # dictionnaire FR → EN / WO (généré, ne pas éditer)
    ├── js/i18n.js              # moteur de langue + sélecteur FR / EN / WO
    └── img/
        ├── hero-atelier.jpg            # assemblage : usine + gamme AMAL (héro)
        ├── showcase-gamme-usine.jpg     # gamme AMAL dans l'atelier
        ├── palette-livraison.jpg        # équipe, cartons et palette siglés AMAL
        ├── labo-amal.jpg                # laboratoire + flacon AMAL
        ├── produit-*.jpg                # 8 rendus 3D étiquetés AMAL
        └── sources/                     # photos et rendus d'origine (non appelés)
```

---

## 🚀 Lancer le site

```bash
cd site-vitrine-amal
python3 serve_preview.py          # → http://localhost:8000
python3 serve_preview.py 8080     # autre port
```

Un double-clic sur `index.html` fonctionne également.

### Intégré au backend FastAPI de ce dépôt

| Route | Contenu |
|---|---|
| `/amal` | redirection (307) vers `/amal/` |
| `/amal/` | page d'accueil du site vitrine AMAL (français) |
| `/amal/en/` | version anglaise (même page, langue pré-sélectionnée) |
| `/amal/wo/` | version wolof (même page, langue pré-sélectionnée) |
| `/amal/assets/…` | styles, scripts et images |

### Mise en ligne définitive

Déposez le dossier `site-vitrine-amal/` tel quel chez un hébergeur statique
(**Netlify, Vercel, GitHub Pages, Cloudflare Pages, Hostinger, o2switch, cPanel**…).
Aucune base de données ni serveur applicatif n'est nécessaire.

---

## 🌍 Versions anglaise et wolof

Le **français est la langue de référence** : le texte vit dans `index.html`, et les
versions EN / WO sont produites à partir de celui-ci. Aucune page n'est dupliquée —
le visiteur change de langue sans recharger, depuis le sélecteur **FR · EN · WO** du
bandeau supérieur.

| Adresse | Résultat |
|---|---|
| `index.html` | site en français |
| `index.html?lang=en` | site en anglais (lien partageable) |
| `index.html?lang=wo` | site en wolof (lien partageable) |
| `en/` · `wo/` | pages d'entrée rapides vers les liens ci-dessus |

Le choix est mémorisé dans le navigateur (`localStorage`), l'attribut `lang` de la
page et les métadonnées (`title`, `description`) suivent la langue, et un bandeau
discret rappelle que la version française fait foi.

### Corriger ou compléter une traduction

1. Ouvrir `tools/i18n/translations-en.txt` ou `tools/i18n/translations-wo.txt` :
   une ligne = un texte, sous la forme `numéro|traduction` (le numéro correspond à
   la ligne du même numéro dans `tools/i18n/reference.md`, la table FR / EN / WO).
2. Laisser la ligne **vide** pour un nom propre, un numéro de téléphone ou une
   unité (le français s'affiche alors tel quel) — `-` signifie « identique au français ».
3. Régénérer le dictionnaire :

```bash
cd site-vitrine-amal
python3 tools/i18n_build.py            # régénère assets/js/i18n-data.js
python3 tools/i18n_build.py --check    # contrôle : renvoie 1 si le fichier n'est pas à jour
python3 tools/i18n_build.py --dump     # affiche la liste française numérotée
node tools/i18n_test.js                # tests du sélecteur (nécessite jsdom)
```

Si un texte est ajouté ou déplacé dans `index.html`, la numérotation change :
le script **s'arrête** et indique les index concernés plutôt que d'associer une
traduction au mauvais texte. On réaligne alors les fichiers de traduction, puis on
relance avec `--accept`.

---

## ✏️ Personnalisation

| À changer | Où |
|---|---|
| **Numéro WhatsApp** (boutons + formulaire) | `assets/js/main.js` → `WHATSAPP_NUMBER` (`221771234567`) **et** les liens `wa.me/…` dans `index.html` |
| E-mail de contact | `assets/js/main.js` → `COMPANY_EMAIL`, plus les `mailto:` de `index.html` |
| Téléphone, adresse, horaires | bandeau supérieur, section `#devis`, pied de page |
| Couleurs de la marque | `assets/css/style.css` → variables `--navy*`, `--blue*`, `--green*`, `--gold` |
| Polices | `index.html` (lien Google Fonts) + variables `--font-title`, `--font-body`, `--font-arabic` |
| Produits, formats, descriptions | section `#produits` — un `<article class="product">` par référence |
| **Ajouter les prix** (quand ils seront prêts) | remplacez le bloc `<span class="soon">…Prix à venir</span>` par `<p class="price">…</p>` (classe déjà stylée) et retirez l'encart `.soon-note` |
| Visuels 3D des produits | remplacez `assets/img/produit-*.jpg` en gardant les mêmes noms |
| Carte de localisation | section `#livraison`, attribut `src` de l'iframe Google Maps |

### Comment activer les prix plus tard

1. Dans chaque produit, remplacer :

   ```html
   <span class="soon">…Prix à venir</span>
   ```
   par :
   ```html
   <p class="price">2 500 FCFA<small>à partir de · 1 L</small></p>
   ```
2. Supprimer le bloc `<div class="soon-note">…</div>` sous la grille.
3. Mettre à jour la FAQ « Quand les prix seront-ils disponibles ? » et l'encart du héro.

---

## ⚠️ Informations à confirmer avant publication

Le site est une **maquette complète et fonctionnelle** : les coordonnées, chiffres,
témoignages et rendus 3D sont des exemples à valider avec l'entreprise.

- [ ] Raison sociale exacte, forme juridique et **NINEA** (pied de page)
- [ ] **Logo AMAL officiel** (fichiers vectoriels) → remplacer le logotype texte et le favicon
- [ ] Validation de la charte : nuances de bleu / vert / or et polices définitives
- [ ] Numéros de téléphone / WhatsApp réels et adresse e-mail professionnelle
- [ ] Adresse réelle de l'usine et nom de domaine
- [ ] **Rendus 3D et assemblages validés par le client** (formes d'emballage et étiquettes définitives)
- [ ] Prix, formats et quantités minimum — à publier quand ils seront fixés
- [ ] Témoignages clients (à recueillir, avec accord écrit, ou à retirer)
- [ ] Zones et délais de livraison réellement assurés
- [ ] Mentions légales / politique de confidentialité si collecte de données

---

## ✅ Contrôles techniques

- HTML sans erreur de structure et CSS équilibré (vérifiés automatiquement).
- 14 références d'assets : toutes présentes, aucune image orpheline.
- Aucune mention de l'ancienne marque, aucun prix fictif résiduel.
- Formulaire validé en direct (nom, téléphone ≥ 9 chiffres, ville, type de demande, e-mail, consentement).
- Rendu servi en HTTP 200 par le serveur de prévisualisation **et** par FastAPI (`/amal/`, `/amal/en/`, `/amal/wo/`, `/amal/assets/…`).
- Multilingue : `node tools/i18n_test.js` → 29 contrôles (bascule FR → EN → WO → FR, bandeau, lien partagé, restauration exacte du français).
- Accessibilité : navigation clavier, `aria-*` sur le menu et la FAQ, contrastes respectés.
- `prefers-reduced-motion` : animations désactivées si le visiteur le demande.

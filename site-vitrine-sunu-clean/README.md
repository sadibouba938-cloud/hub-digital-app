# 🧼 Sunu Clean Sénégal — Site vitrine

Site vitrine **complet, responsive et 100 % statique** (HTML / CSS / JavaScript, aucune
dépendance) pour une entreprise sénégalaise spécialisée dans la **production de détergents
et de produits d'hygiène** : liquide vaisselle, lessive, nettoyant multi-usage, javel,
savon liquide et dégraissants professionnels.

---

## 👀 Aperçu

| Section | Contenu |
|---|---|
| Bandeau supérieur | Téléphone, e-mail, horaires, statut « usine ouverte » |
| En-tête collant | Logo, navigation, appel direct, menu burger sur mobile |
| Accueil (hero) | Accroche, photo de l'usine, boutons d'action, 3 chiffres clés animés |
| Bandeau confiance | Usine locale, prix de gros, livraison, moyens de paiement |
| Produits | 9 produits filtrables par catégorie (maison, lessive, hygiène, pro) avec prix en FCFA |
| Services | Production à façon (marque blanche), vrac B2B, livraison, formulation sur mesure |
| L'entreprise | Histoire, chiffres, photographie de l'équipe |
| Qualité & process | 5 étapes de fabrication + 4 indicateurs qualité |
| Livraison | Zones du Sénégal avec délais + carte Google Maps de Diamniadio |
| Témoignages | 3 avis clients (revendeuse, hôtel, marque partenaire) |
| FAQ | 6 questions en accordéon (minimum de commande, marque blanche, paiement…) |
| Devis | Formulaire validé en JavaScript → envoi du récapitulatif via **WhatsApp** ou e-mail |
| Pied de page | Coordonnées, liens, réseaux sociaux, NINEA |
| Flottants | Bouton WhatsApp permanent + retour en haut |

Fonctions techniques : menu mobile accessible, animation des compteurs, apparition
progressive au défilement, filtres produits, accordéon FAQ, validation de formulaire,
balisage SEO (meta, Open Graph, données structurées `LocalBusiness`).

---

## 📁 Structure

```
site-vitrine-sunu-clean/
├── index.html                  # page unique complète (toutes les sections)
├── serve_preview.py            # serveur local de prévisualisation (Python standard)
├── README.md                   # ce fichier
└── assets/
    ├── css/style.css           # design system complet (variables, composants, responsive)
    ├── js/main.js              # menu, filtres, FAQ, compteurs, formulaire de devis
    └── img/                    # 4 visuels (usine, gamme, laboratoire, équipe)
```

---

## 🚀 Lancer le site

### En local (prévisualisation)

```bash
cd site-vitrine-sunu-clean
python3 serve_preview.py        # → http://localhost:8000
# ou avec un autre port : python3 serve_preview.py 8080
```

Un simple double-clic sur `index.html` fonctionne aussi.

### Déjà intégré au backend FastAPI de ce dépôt

Le site est servi par `main.py` sur ces routes (uniquement si le dossier est présent) :

| Route | Contenu |
|---|---|
| `/sunu-clean` | redirection vers `/sunu-clean/` |
| `/sunu-clean/` | page d'accueil du site vitrine |
| `/sunu-clean/assets/…` | styles, scripts et images |

### Mise en ligne définitive (hébergement statique)

Déposez le dossier `site-vitrine-sunu-clean/` tel quel chez n'importe quel hébergeur
statique : **Netlify, Vercel, GitHub Pages, Cloudflare Pages, Hostinger, o2switch, cPanel**…
Aucune base de données ni serveur applicatif n'est nécessaire — le site pèse moins de 1 Mo.

---

## ✏️ Personnalisation (5 minutes)

| Ce que vous voulez changer | Où |
|---|---|
| **Numéro WhatsApp** (boutons, formulaire) | `assets/js/main.js` → `WHATSAPP_NUMBER` (format `221771234567`) **et** les liens `wa.me/…` dans `index.html` |
| E-mail de contact | `assets/js/main.js` → `COMPANY_EMAIL`, plus les `mailto:` dans `index.html` |
| Téléphone, adresse, horaires | `index.html` : bandeau supérieur, section `#devis`, pied de page |
| Nom de l'entreprise, logo, slogan | `index.html` (bloc `.logo`) + balise `<title>` + favicon |
| Couleurs de la marque | `assets/css/style.css` → variables `--green*`, `--gold*` (début du fichier) |
| Produits, formats, prix | `index.html` → section `#produits` (chaque `<article class="product">`) |
| Photos | remplacez les fichiers de `assets/img/` en gardant les mêmes noms |
| Carte de localisation | `index.html` → section `#livraison` (attribut `src` de l'iframe Google Maps) |
| Réseaux sociaux | `index.html` → bloc `.socials` du pied de page (remplacez les `href="#"`) |
| SEO / partage Facebook-WhatsApp | `index.html` → `<meta name="description">` et balises `og:*` |

### Ajouter ou retirer un produit

1. Copiez un `<article class="product" data-cat="…">` entier.
2. `data-cat` doit valoir `maison`, `lessive`, `hygiene` ou `pro` (les filtres s'y adaptent).
3. `style="--product-color:#0e8c53"` définit la couleur du flacon illustré.
4. Pour une pastille « Best-seller »/« Pro », ajoutez `<span class="product__tag">…</span>`.

---

## ⚠️ Informations à confirmer avant publication

Ce site est une **maquette complète et fonctionnelle** : tous les contenus de marque sont
fictifs et doivent être remplacés par les informations réelles de l'entreprise avant
sa mise en ligne publique.

À vérifier avec le client :

- [ ] Raison sociale exacte, forme juridique et **NINEA** (pied de page)
- [ ] Adresse réelle de l'usine et de l'entrepôt (carte, itinéraire)
- [ ] Numéros de téléphone / WhatsApp réellement utilisés
- [ ] Adresse e-mail professionnelle et nom de domaine
- [ ] Prix réels, formats conditionnés et quantités minimum de commande
- [ ] Zones et délais de livraison réellement assurés
- [ ] Témoignages clients (à recueillir, avec accord écrit, ou à retirer)
- [ ] Logos des réseaux sociaux (Facebook, Instagram, TikTok)
- [ ] Mentions légales / politique de confidentialité si le site collecte des données
- [ ] Photos de l'usine et des produits réels (remplacer les visuels générés)

---

## 🔎 Contrôle qualité automatique

Le formulaire de devis valide en direct : nom, téléphone (au moins 9 chiffres),
ville, type de demande, e-mail au bon format et case de consentement.
En cas d'erreur, le premier champ fautif est mis en évidence et le focus y est placé.

Le site respecte aussi `prefers-reduced-motion` (animations désactivées pour les
personnes sensibles au mouvement) et reste lisible sans JavaScript.

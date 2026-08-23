# 🚀 Déployer Hub Digital (site + API) pour obtenir un lien permanent

Le site actuel tourne dans un **aperçu temporaire** Arena : il disparaît à la fin de la session.
Pour partager un **lien permanent** sur les réseaux sociaux, déployez ce dossier sur un hébergeur gratuit.

---

## 📁 Contenu à déployer

```
backend/
├── main.py              # FastAPI : vitrine + tableau de bord + API + chat + boutique
├── database.py          # SQLite
├── data.db              # base de données
├── requirements.txt     # dépendances Python
├── Procfile             # commande de démarrage (Railway / Render / Heroku)
└── static/
    ├── index.html       # site vitrine Hub Digital
    ├── taches.html      # tableau de bord
    ├── chat.css / chat.js
    └── assets/          # css + js + i18n
```

---

## Option A — Railway (recommandé, le plus simple)

1. Créez un compte sur **railway.app** (gratuit).
2. Poussez ce dossier `backend/` sur GitHub (nouveau dépôt ou sous-dossier).
3. Dans Railway : **New Project → Deploy from GitHub repo**.
4. Railway détecte `requirements.txt` + `Procfile` automatiquement.
5. Cliquez **Deploy**, puis **Settings → Networking → Generate Domain**.
6. ✅ Vous obtenez un lien du type : `https://hubdigital.up.railway.app`

👉 Ce lien est **permanent** et partageable partout.

---

## Option B — Render

1. Créez un compte sur **render.com** (gratuit).
2. **New → Web Service**, connectez le dépôt GitHub.
3. Build command : `pip install -r requirements.txt`
4. Start command : `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. ✅ Lien permanent du type : `https://hubdigital.onrender.com`

---

## Option C — Votre GitHub Pages existant (site statique uniquement)

Votre dépôt publie déjà `https://sadibouba938-cloud.github.io/hub-digital-site/`.
⚠️ Attention : GitHub Pages est **statique** — la vitrine et la section Boutique
(si les produits sont chargés via l'API) y fonctionneront, mais le **tableau de bord
(/taches)**, le **chat IA (/api/chat)** et le **proxy boutique (/boutique/produits)**
ont besoin du backend Python (Options A ou B).

---

## 🌐 Routes disponibles après déploiement

| Route | Contenu |
|---|---|
| `/` | Site vitrine Hub Digital |
| `/taches` | Tableau de bord (tâches + base SQLite) |
| `/boutique/produits` | Produits Chariow (proxy API) |
| `/api/chat` | Chat « Hub Digital IA » |
| `/health` | État du serveur |
| `/docs` | Documentation API (Swagger) |

---

## ⚠️ Note sur la base de données

- `data.db` est un simple fichier SQLite : il se déploie avec le code.
- Sur les hébergeurs gratuits, le disque peut être **éphémère** (réinitialisé à chaque redéploiement).
- Pour une persistance fiable en production, passez à **PostgreSQL** (Railway/Render en proposent un gratuitement).

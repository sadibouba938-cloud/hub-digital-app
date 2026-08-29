# Pack vidéo prêt à publier — Hub Digital · « Le Kit Ultime »

Pub pour le **Kit Ultime de création & vente de produits digitaux — du concept aux ventes**.
**Prix intégré : 2 500 FCFA (~~5 000 FCFA~~ barré), révélé à 30,5 s avec un « ding » — urgence « cette semaine ».**
**Engagement : plan dédié à 42,7 s (commente « KIT », partage, sauvegarde) avec bulles de commentaires animées.**
Quatre fichiers encodés aux specs Instagram Reels / TikTok / Facebook, avec les textes à copier.

## 📦 Les 4 exports

| Fichier | Format | Durée | Poids | À publier sur |
|---|---|---|---|---|
| `reel_kit_ultime_1080x1920.mp4` | 1080×1920 (9:16) | 57 s | 29 Mo | **Reels, TikTok, Shorts** (le principal) |
| `reel_kit_ultime_court_1080x1920.mp4` | 1080×1920 (9:16) | 36 s | 16 Mo | A/B test : hook + promesse + prix + CTA + engagement |
| `reel_kit_ultime_feed_1080x1350.mp4` | 1080×1350 (4:5) | 57 s | 25 Mo | Post feed Instagram / Facebook |
| `reel_kit_ultime_feed_1080x1080.mp4` | 1080×1080 (1:1) | 57 s | 23 Mo | Post feed carré, LinkedIn |

Tous : H.264 High / yuv420p · 30 fps · AAC 48 kHz 160 kb/s · **faststart** · sous-titres incrustés.

## 👀 Aperçu dans le navigateur

```bash
cd marketing/reel-kit-ultime
python3 serve_preview.py          # http://localhost:8000
```
La page `index.html` affiche le lecteur (4 formats), la légende et les hashtags à copier en un clic.

## ✅ Contrôle technique

```bash
python3 verify.py      # -> "TOUT EST PRET A PUBLIER"
```

## 🔁 Régénérer / personnaliser

```bash
python3 -m venv ../../.venv && ../../.venv/bin/pip install pillow numpy imageio-ffmpeg
python3 build_reel.py                                   # reel 9:16 complet
SCENES_SEL=0,2,6,7,8,9 python3 build_reel.py            # montage court (hook, kit, prix, CTA, engagement, fin)
RATIO=4x5 OUT_NAME=ma_video.mp4 python3 build_reel.py   # autre format (9x16 / 4x5 / 1x1)
MUSIC_VOL=0 python3 build_reel.py                       # sans musique
CRF=20 PRESET=fast python3 build_reel.py                # encodage plus leger
```

| Je veux changer… | Où ? |
|---|---|
| Textes à l'écran, tailles, couleurs | `SCENES` dans `build_reel.py` |
| Images / ordre des plans | `SCENES[i]["img"]` + dossier `assets/` |
| Voix off | fichiers de `audio/` (une phrase = un fichier) |
| Blancs entre phrases | `LEAD`, `GAP`, `TAIL` |
| Accroches alternatives | `script.md` (3 variantes à A/B tester) |

Couleurs de marque : orange `#ff7a00`, violet `#6c5ce7`, fond `#0d1117`.

## 🧩 Ce que fait le générateur

1. **Voix off** : assemble `audio/` avec des blancs, normalise.
2. **Musique** : instru synthétisée (124 BPM) + *ducking* automatique sous la voix.
3. **Images** : recadrage au ratio demandé + Ken Burns, voile dégradé + vignette.
4. **Sous-titres** : gros titres contourés, surlignage mot à mot, punch sur l'accroche.
5. **Habillage** : badge « HUB DIGITAL », barre de progression, pastille CTA, carte de fin.
6. **Encodage** : H.264 High CRF 17, GOP 2 s, `+faststart`, AAC 160 kb/s.

Le texte reste entre 260 px et 1600 px de haut : hors des zones masquées par l'interface Reels.

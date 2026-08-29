# Reel pub — Hub Digital · « Le Kit Ultime » (9:16)

Fichier livré : **`reel_kit_ultime_1080x1920.mp4`** — 1080 × 1920, 30 fps, 42 s, ~13 Mo.

```
marketing/reel-kit-ultime/
├── reel_kit_ultime_1080x1920.mp4   ← la vidéo finale
├── build_reel.py                   ← générateur complet (relance-le après modification)
├── script.md                       ← script, accroches, légende, hashtags
├── assets/                         ← 7 visuels 9:16 (IA)
└── audio/                          ← voix off, une piste par phrase
```

## 🔁 Régénérer la vidéo

```bash
cd marketing/reel-kit-ultime
python3 -m venv ../../.venv && ../../.venv/bin/pip install pillow numpy imageio-ffmpeg
../../.venv/bin/python build_reel.py
```

Sortie : `reel_kit_ultime_1080x1920.mp4` (durée ~1 min 45 de rendu).

## ✏️ Personnaliser

| Je veux changer… | Où ? |
|---|---|
| Les textes à l'écran / tailles / couleurs | `SCENES` dans `build_reel.py` (clés `lines`) |
| L'ordre ou les images | `SCENES[i]["img"]` dans `assets/` |
| La voix off | remplacer les fichiers de `audio/` (une phrase = un fichier, même ordre) |
| Le volume de la musique | `MUSIC_VOL=0.06 python3 build_reel.py` (`0` = sans musique) |
| Les blancs entre phrases | `LEAD`, `GAP`, `TAIL` en haut de `build_reel.py` |

Couleurs de marque utilisées : orange `#ff7a00`, violet `#6c5ce7`, fond `#0d1117`.

## 🧩 Ce que fait le générateur

1. **Voix off** : assemble les pistes de `audio/` avec des blancs, normalise.
2. **Musique** : instru synthétisée (124 BPM, kick/clap/hats/basse/nappe) + *ducking* automatique sous la voix.
3. **Images** : recadrage 9:16 + Ken Burns (zoom avant/arrière alterné), voile dégradé + vignette pour la lisibilité.
4. **Sous-titres** : gros titres contourés, surlignage mot à mot synchronisé, pop-in/punch à l'arrivée.
5. **Habillage** : badge « HUB DIGITAL », barre de progression, pastille CTA, carte de fin.
6. Encodage H.264 (CRF 18) + AAC 192 kbps, `faststart` activé.

Le script évite les zones masquées par l'interface Reels (texte entre 260 px et 1600 px de haut).

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the 9:16 Reels ad for  « Hub Digital — Le Kit Ultime »
(Création & vente de produits digitaux : du concept aux ventes)

Sortie : reel_kit_ultime_1080x1920.mp4  (1080x1920, 30 fps, H.264 + AAC)

Tout est reproductible : modifie SCENES / les textes puis relance
    python3 build_reel.py
"""

import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ------------------------------------------------------------------ config
ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
AUDIO = os.path.join(ROOT, "audio")
WORK = os.path.join(ROOT, "_work")
OUT_NAME = os.environ.get("OUT_NAME", "reel_kit_ultime_1080x1920.mp4")
OUT_MP4 = os.path.join(ROOT, OUT_NAME)
PRESET = os.environ.get("PRESET", "medium")     # encodage
CRF = os.environ.get("CRF", "17")               # qualite (plus bas = meilleur)

FFMPEG = "/home/user/.venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
if not os.path.exists(FFMPEG):
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

W, H, FPS = 1080, 1920, 30
V_SCALE = 1.0            # echelle verticale des elements (1.0 = 1080x1920)
SR = 48000

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

WHITE = (255, 255, 255)
ORANGE = (255, 122, 0)
PURPLE = (108, 92, 231)
BLACK = (0, 0, 0)

MUSIC_VOL = float(os.environ.get("MUSIC_VOL", 0.115))   # 0 = sans musique
LEAD = 0.35      # silence avant la 1re phrase
GAP = 0.12       # blanc entre deux phrases
TAIL = 1.10      # tenue de la carte de fin
XF = 0.35        # duree du fondu entre deux plans
TEXT_MAX_W = 940

# ------------------------------------------------------------- le script
# hi = surlignage mot a mot (karaoke), anchor = centre vertical du bloc texte
SCENES = [
    dict(
        audio="v01_l1.mp3", img="01_hook_scroll.jpg", hi=False, anchor=1120, punch=True,
        lines=[
            {"t": "ARRÊTE DE", "c": "white", "size": 118},
            {"t": "SCROLLER", "c": "orange", "size": 118},
            {"t": "TON IDÉE VAUT PLUS QUE ÇA", "c": "white", "size": 54},
        ],
    ),
    dict(
        audio="v01_l2.mp3", img="03_idee_concept.jpg", hi=True, anchor=1150,
        lines=[
            {"t": "TU VEUX VENDRE UN", "c": "white", "size": 88},
            {"t": "PRODUIT DIGITAL", "c": "white", "size": 88},
            {"t": "… MAIS TU BLOQUES", "c": "orange", "size": 76},
        ],
    ),
    dict(
        audio="v01_l3.mp3", img="04_kit_3d.jpg", hi=True, anchor=1140,
        lines=[
            {"t": "LE KIT ULTIME", "c": "orange", "size": 104},
            {"t": "DU CONCEPT AUX VENTES", "c": "white", "size": 76},
        ],
    ),
    dict(
        audio="v01_l4.mp3", img="02_creation_produit.jpg", hi=True, anchor=1160,
        lines=[
            {"t": "IDÉE · CRÉATION ·", "c": "white", "size": 86},
            {"t": "PACKAGING · VENTE", "c": "orange", "size": 86},
        ],
    ),
    dict(
        audio="v01_l5.mp3", img="06_page_de_vente.jpg", hi=True, anchor=1140,
        lines=[
            {"t": "TEMPLATES · PAGES DE VENTE ·", "c": "white", "size": 66},
            {"t": "SCRIPTS · EMAILS", "c": "white", "size": 66},
            {"t": "TOUT EST PRÊT", "c": "orange", "size": 84},
        ],
    ),
    dict(
        audio="v01_l6.mp3", img="07_liberte.jpg", hi=True, anchor=1140,
        lines=[
            {"t": "MÊME AVEC", "c": "white", "size": 96},
            {"t": "0 EXPÉRIENCE", "c": "orange", "size": 96},
            {"t": "0 AUDIENCE", "c": "white", "size": 96},
        ],
    ),
    dict(
        audio="v01_prix.mp3", img="04_kit_3d.jpg", hi=True, anchor=1140, sfx="ding",
        lines=[
            {"t": "SEULEMENT", "c": "white", "size": 58},
            {"t": "CETTE SEMAINE", "c": "white", "size": 58},
            {"t": "2 500 FCFA", "c": "orange", "size": 150},
            {"t": "AU LIEU DE 5 000 FCFA", "c": "white", "size": 62, "strike": True},
        ],
    ),
    dict(
        audio="v01_l7.mp3", img="05_vente_confirmee.jpg", hi=True, anchor=1080,
        lines=[
            {"t": "TON PREMIER PRODUIT", "c": "white", "size": 82},
            {"t": "COMMENCE AUJOURD'HUI", "c": "orange", "size": 82},
        ],
        pill="VOIR LE KIT",
    ),
    dict(
        audio="v01_interaction.mp3", img="08_interaction.jpg", hi=True, anchor=1160,
        bubbles=True, sfx="pop",
        lines=[
            {"t": "COMMENTE", "c": "white", "size": 76},
            {"t": "« KIT »", "c": "orange", "size": 150},
            {"t": "PARTAGE À UN AMI · SAUVEGARDE", "c": "white", "size": 48},
        ],
    ),
    dict(
        audio="v01_l8.mp3", img="04_kit_3d.jpg", endcard=True, hi=False, anchor=960,
        lines=[
            {"t": "HUB DIGITAL", "c": "white", "size": 92},
            {"t": "LE KIT ULTIME", "c": "orange", "size": 74},
            {"t": "2 500 FCFA", "c": "white", "size": 112},
            {"t": "5 000 FCFA", "c": "muted", "size": 54, "strike": True},
            {"t": "Offre valable cette semaine", "c": "muted", "size": 42, "font": FONT_REG},
        ],
        pill="COMMENTE « KIT »",
    ),
]

ACTIVE = list(SCENES)          # scenes retenues pour le montage en cours

COLOR_MAP = {"white": WHITE, "orange": ORANGE, "muted": (170, 180, 190), "purple": PURPLE}

# ------------------------------------------------------------------ audio
def decode_mp3(path):
    out = subprocess.run(
        [FFMPEG, "-v", "error", "-i", path, "-f", "s16le",
         "-acodec", "pcm_s16le", "-ar", str(SR), "-ac", "1", "-"],
        capture_output=True,
    )
    a = np.frombuffer(out.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    if a.size == 0:
        raise RuntimeError("audio vide: " + path)
    peak = float(np.max(np.abs(a)))
    if peak > 0:
        a *= 0.88 / peak
    return a


def build_vo_timeline():
    clips = [decode_mp3(os.path.join(AUDIO, s["audio"])) for s in ACTIVE]
    starts, pos = [], LEAD
    for c in clips:
        starts.append(pos)
        pos += len(c) / SR + GAP
    total = pos + TAIL
    vo = np.zeros(int(total * SR) + SR, dtype=np.float32)
    for c, st in zip(clips, starts):
        i0 = int(st * SR)
        vo[i0:i0 + len(c)] += c
    return vo, starts, [len(c) / SR for c in clips], total


def synth_music(total, sr=SR):
    """Petite instru : kick, clap, hats, basse, nappe. Volontairement discrete."""
    n = int(total * sr)
    t = np.arange(n) / sr
    out = np.zeros(n, dtype=np.float32)

    bpm, beat = 124.0, 60 / 124.0
    rng = np.random.default_rng(7)

    def env(i0, dur, tau):
        m = int(dur * sr)
        idx = np.arange(m)
        e = np.exp(-idx / (tau * sr))
        sl = slice(i0, min(n, i0 + m))
        e = e[: sl.stop - sl.start]
        return sl, e

    # --- kick (4 temps) + clap (2 & 4) + hats + basse + nappe
    nbeats = int(total / beat) + 2
    noise = rng.normal(0, 1, n).astype(np.float32)

    for b in range(nbeats):
        i0 = int(b * beat * sr)
        # kick
        sl, e = env(i0, 0.34, 0.075)
        if sl.stop > sl.start:
            ph = 2 * np.pi * np.cumsum(np.linspace(150, 46, sl.stop - sl.start)) / sr
            out[sl] += 1.0 * e * np.sin(ph)
        # clap sur 2 et 4
        if b % 4 in (1, 3):
            sl, e = env(i0, 0.20, 0.035)
            if sl.stop > sl.start:
                out[sl] += 0.30 * e * noise[sl.start:sl.stop]
        # hats (croches)
        for off, amp in ((0.0, 0.16), (0.5, 0.10)):
            i1 = int((b + off) * beat * sr)
            sl, e = env(i1, 0.055, 0.012)
            if sl.stop > sl.start:
                seg = noise[sl.start:sl.stop] * e
                # passe-haut rudimentaire
                seg = np.diff(seg, prepend=0.0)
                out[sl] += amp * seg

    # --- basse : progression Am - F - C - G (2 temps chaque)
    roots = [110.0, 87.31, 130.81, 98.0]
    for b in range(nbeats):
        note = roots[(b // 2) % 4]
        i0 = int(b * beat * sr)
        sl, e = env(i0, beat * 1.9, 0.30)
        if sl.stop > sl.start:
            tt = np.arange(sl.stop - sl.start) / sr
            out[sl] += 0.28 * e * np.sin(2 * np.pi * note * tt)

    # --- nappe : accord mineur tout doux
    for b in range(0, nbeats, 8):
        note = roots[(b // 2) % 4] * 4
        i0 = int(b * beat * sr)
        dur = beat * 8
        sl, e = env(i0, dur, dur * 0.55)
        if sl.stop > sl.start:
            tt = np.arange(sl.stop - sl.start) / sr
            chord = sum(np.sin(2 * np.pi * note * r * tt) for r in (1.0, 1.19, 1.5))
            out[sl] += 0.055 * e * chord / 3.0

    # --- impact de debut (sub boom)
    sl, e = env(int(0.02 * sr), 0.9, 0.30)
    if sl.stop > sl.start:
        ph = 2 * np.pi * np.cumsum(np.linspace(90, 38, sl.stop - sl.start)) / sr
        out[sl] += 0.85 * e * np.sin(ph)

    out /= max(1e-6, float(np.max(np.abs(out))))
    out *= 0.92
    return out


def moving_avg(x, w):
    w = max(1, int(w))
    if w >= len(x):
        return np.full(len(x), float(np.mean(x)), dtype=np.float32)
    cs = np.cumsum(np.insert(x.astype(np.float64), 0, 0.0))
    out = (cs[w:] - cs[:-w]) / w
    pad_l = (len(x) - len(out)) // 2
    return np.pad(out, (pad_l, len(x) - len(out) - pad_l), mode="edge").astype(np.float32)


def add_sfx(base, t0, kind="ding", sr=SR):
    """Petit son de revelation du prix."""
    i0 = int(t0 * sr)
    if kind == "pop":
        segs = []
        for f0, off in ((760.0, 0.0), (1140.0, 0.20)):
            m = int(0.22 * sr)
            tt = np.arange(m) / sr
            segs.append((off, np.exp(-tt / 0.07) * np.sin(2 * np.pi * f0 * tt)))
        for off, seg in segs:
            j0 = i0 + int(off * sr)
            j1 = min(len(base), j0 + len(seg))
            if j1 > j0:
                base[j0:j1] += seg[: j1 - j0] * 0.22
        return base
    if kind == "ding":
        dur = 0.85
        m = int(dur * sr)
        tt = np.arange(m) / sr
        e = np.exp(-tt / 0.26)
        wave = 0.55 * np.sin(2 * np.pi * 1320 * tt) + 0.35 * np.sin(2 * np.pi * 1980 * tt) \
            + 0.18 * np.sin(2 * np.pi * 2640 * tt)
        seg = e * wave
    else:
        return base
    i1 = min(len(base), i0 + len(seg))
    base[i0:i1] += seg[: i1 - i0] * 0.30
    return base


def duck(music, vo, sr=SR):
    """Baisse la musique sous la voix."""
    speech = (np.abs(vo) > 0.02).astype(np.float32)
    c = moving_avg(speech, 0.35 * sr)
    target = np.where(c > 0.02, 0.42, 1.0).astype(np.float32)
    level = moving_avg(target, 0.08 * sr)
    n = min(len(music), len(level))
    return music[:n] * level[:n]


# ------------------------------------------------------------------ texte
_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def gap_for(size):
    return max(9, int(size * 0.22))


def wrap_words(draw, words, f, max_w, gap):
    lines, cur, cur_w = [], [], 0
    for w in words:
        ww = draw.textbbox((0, 0), w, font=f)[2]
        if cur and cur_w + ww + gap > max_w:
            lines.append(cur)
            cur, cur_w = [w], ww
        else:
            cur.append(w)
            cur_w += ww + gap
    if cur:
        lines.append(cur)
    return lines


def layout(scene):
    """Calcule la position de chaque mot (fixe pour toute la scene)."""
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    laid, words_all = [], []
    for li, spec in enumerate(scene["lines"]):
        size = spec.get("size", 84)
        fpath = spec.get("font", FONT_BOLD)
        words = spec["t"].split()
        # 1) on essaie de tenir sur une seule ligne (plus propre a l'ecran)
        while True:
            f = font(fpath, size)
            gap = gap_for(size)
            widths = [tmp.textbbox((0, 0), w, font=f)[2] for w in words]
            total = sum(widths) + gap * (len(words) - 1)
            if total <= TEXT_MAX_W or size <= 44:
                break
            size -= 2
        if total <= TEXT_MAX_W:
            groups = [(words, widths)]
        else:  # vraiment trop long : on passe a la ligne
            groups = []
            for g in wrap_words(tmp, words, f, TEXT_MAX_W, gap):
                groups.append((g, [tmp.textbbox((0, 0), w, font=f)[2] for w in g]))
        for group, widths in groups:
            total = sum(widths) + gap * (len(group) - 1)
            laid.append(dict(font=f, size=size, color=spec.get("c", "white"),
                             words=group, widths=widths, total=total,
                             gap=gap, line=li, strike=bool(spec.get("strike"))))
            words_all.extend(group)
    lh = [max(l["size"] * 1.24, 40) for l in laid]
    block_h = int(sum(lh) + 18 * (len(laid) - 1))
    return dict(lines=laid, heights=lh, block_h=block_h, words=words_all,
                anchor=scene.get("anchor", 1150))


def render_text_layer(sc, lay, hi_index):
    """Rendu du bloc texte (transparent) avec surlignage du mot courant."""
    pad = 60
    img = Image.new("RGBA", (W, pad * 2 + lay["block_h"]), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = pad
    wi = 0
    for li, (l, hh) in enumerate(zip(lay["lines"], lay["heights"])):
        x = (W - l["total"]) // 2
        base = COLOR_MAP.get(l["color"], WHITE)
        for w, ww in zip(l["words"], l["widths"]):
            if sc.get("hi"):
                if wi < hi_index:
                    fill = base
                elif wi == hi_index:
                    fill = ORANGE
                else:
                    fill = tuple(int(c * 0.55) for c in base)
            else:
                fill = base
            sw = max(2, l["size"] // 20)
            # ombre portee
            d.text((x + 6, y + 8), w, font=l["font"], fill=(0, 0, 0, 160),
                   stroke_width=sw + 2, stroke_fill=(0, 0, 0, 160))
            # texte + contour
            d.text((x, y), w, font=l["font"], fill=fill,
                   stroke_width=sw, stroke_fill=(0, 0, 0, 235))
            x += ww + l["gap"]
            wi += 1
        if l.get("strike"):
            x0 = (W - l["total"]) // 2
            bar = max(6, l["size"] // 11)
            d.rectangle([x0 - 8, y + l["size"] * 0.52 - bar // 2,
                         x0 - 8 + l["total"] + 16, y + l["size"] * 0.52 + bar // 2],
                        fill=(231, 76, 60, 235))
        y += hh + 18
    return img.crop((0, 0, W, y + pad))


def draw_pill(img, text, y, alpha=255):
    d = ImageDraw.Draw(img, "RGBA")
    f = font(FONT_BOLD, 44)
    tw = d.textbbox((0, 0), text, font=f)[2]
    bw, bh = tw + 150, 104
    x = (W - bw) // 2
    # fleche vers le bas
    d.rounded_rectangle([x, y, x + bw, y + bh], radius=bh // 2,
                        fill=ORANGE + (alpha,))
    d.text(((W - tw) // 2, y + (bh - 44) // 2 - 6), text, font=f, fill=(255, 255, 255, alpha))
    ax, ay = W // 2, y + bh + 16
    d.polygon([(ax - 22, ay), (ax + 22, ay), (ax, ay + 30)], fill=ORANGE + (alpha,))
    return img


def draw_bubbles(img, age, vs=1.0):
    """Bulles de commentaires « KIT » qui apparaissent en cascade."""
    d = ImageDraw.Draw(img, "RGBA")
    f = font(FONT_BOLD, 40)
    tw = d.textbbox((0, 0), "KIT", font=f)[2]
    spots = [(120, 470), (700, 380), (330, 660), (640, 760)]
    for k, (x, y) in enumerate(spots):
        a = int(255 * min(1.0, max(0.0, (age - 0.25 - k * 0.28) / 0.25)))
        if a <= 4:
            continue
        y = int(y * vs) + int(10 * np.sin(age * 2.2 + k))
        bw, bh = tw + 74, 98
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=28, fill=(255, 255, 255, a))
        d.polygon([(x + 34, y + bh - 2), (x + 78, y + bh - 2), (x + 46, y + bh + 30)],
                  fill=(255, 255, 255, a))
        d.text((x + 37, y + 24), "KIT", font=f, fill=(255, 122, 0, a))
    return img


def draw_badge(img, t, alpha, vs=1.0):
    d = ImageDraw.Draw(img, "RGBA")
    f = font(FONT_BOLD, int(38 * min(1.0, vs) if vs < 1 else 38))
    top = int(118 * vs)
    d.ellipse([62, top, 62 + 30, top + 30], fill=ORANGE + (alpha,))
    d.text((106, top), "HUB DIGITAL", font=f, fill=(255, 255, 255, alpha),
           stroke_width=3, stroke_fill=(0, 0, 0, alpha))
    return img


# ------------------------------------------------------------- background
def make_scrim():
    """Degrade + vignette, calcules une seule fois."""
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    a = np.zeros((H, W), dtype=np.float32)
    a += np.clip((yy - 0.42) / 0.58, 0, 1) ** 1.25 * 0.82          # bas assombri
    a += np.clip((0.30 - yy) / 0.30, 0, 1) ** 1.4 * 0.55           # haut assombri
    r = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2) / 0.72
    a += np.clip(r, 0, 1) ** 2 * 0.45                               # vignette
    a = np.clip(a, 0, 0.94)
    arr = np.zeros((H, W, 4), dtype=np.uint8)
    arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


SCRIM = make_scrim()


def scene_frame(i, t_local, dur):
    sc = ACTIVE[i]
    src = Image.open(os.path.join(ASSETS, sc["img"])).convert("RGB")
    if sc.get("endcard"):
        src = src.filter(ImageFilter.GaussianBlur(28))
    # canvas : debordement pour le Ken Burns
    zoom_max = 1.14
    cw, ch = int(W * zoom_max), int(H * zoom_max)
    sc_ratio, src_ratio = cw / ch, src.width / src.height
    if src_ratio > sc_ratio:
        nw = int(src.height * sc_ratio)
        src = src.crop(((src.width - nw) // 2, 0, (src.width - nw) // 2 + nw, src.height))
    else:
        nh = int(src.width / sc_ratio)
        src = src.crop((0, (src.height - nh) // 2, src.width, (src.height - nh) // 2 + nh))
    canvas = src.resize((cw, ch), Image.BILINEAR)

    p = 0.0 if dur <= 0 else min(1.0, max(0.0, t_local / dur))
    if i % 2 == 0:
        s = 1.0 + (zoom_max - 1.0) * p          # zoom avant
        dx, dy = 0.02 * p, -0.015 * p
    else:
        s = zoom_max - (zoom_max - 1.0) * p     # zoom arriere
        dx, dy = 0.02 * (1 - p), 0.015 * p

    cwp, chp = W / s, H / s
    cx = (cw - cwp) * (0.5 + dx)
    cy = (ch - chp) * (0.5 + dy)
    box = (int(cx), int(cy), int(cx + cwp), int(cy + chp))
    frame = canvas.crop(box).resize((W, H), Image.BILINEAR).convert("RGBA")
    frame.alpha_composite(SCRIM)
    return frame


def caption_layer(i, t_local, dur, cache, lay_cache):
    sc = ACTIVE[i]
    if lay_cache.get(i) is None:
        lay_cache[i] = layout(sc)
    lay = lay_cache[i]
    nw = max(1, len(lay["words"]))
    if sc.get("hi"):
        # progression lineaire ponderee par la longueur des mots
        lens = np.array([max(1, len(w)) for w in lay["words"]], dtype=np.float32)
        cum = np.cumsum(lens) / lens.sum()
        hi = int(np.searchsorted(cum, min(0.999, t_local / max(0.001, dur))))
        hi = min(hi, nw - 1)
    else:
        hi = nw
    key = (i, hi)
    if cache.get(key) is None:
        cache[key] = render_text_layer(sc, lay, hi)
    layer = cache[key]
    # pop-in (la 1re scene arrive en "punch" pour casser le scroll)
    age = t_local
    punch = sc.get("punch", False)
    if age < 0.26:
        k = max(0.0, age / 0.26)
        e = 1 - (1 - k) ** 3
        s = (1.22 - 0.22 * e) if punch else (0.90 + 0.10 * e)
        nwpx, nhpx = int(layer.width * s), int(layer.height * s)
        layer = layer.resize((nwpx, nhpx), Image.LANCZOS)
        a = layer.split()[3].point(lambda v: int(v * min(1.0, age / 0.12)))
        layer.putalpha(a)
    return layer, lay


# ------------------------------------------------------------------ rendu
RATIOS = {"9x16": (1080, 1920), "4x5": (1080, 1350), "1x1": (1080, 1080)}


def main():
    global W, H, V_SCALE, SCRIM, ACTIVE
    os.makedirs(WORK, exist_ok=True)

    r = os.environ.get("RATIO", "9x16")
    W, H = RATIOS.get(r, (1080, 1920))
    V_SCALE = H / 1920
    SCRIM = make_scrim()

    sel = os.environ.get("SCENES_SEL")           # ex. "0,2,6,7" pour la version courte
    ACTIVE = [SCENES[int(i)] for i in sel.split(",")] if sel else list(SCENES)

    vo, starts, durs, _ = build_vo_timeline()
    total = len(vo) / SR
    ends = [starts[k + 1] if k + 1 < len(starts) else starts[k] + durs[k] + TAIL
            for k in range(len(starts))]
    print(f"Duree totale : {total:.2f}s")

    # --- musique + mixage
    music = synth_music(total)
    if len(music) < len(vo):
        music = np.pad(music, (0, len(vo) - len(music)))
    else:
        music = music[:len(vo)]
    music = duck(music, vo)
    mix = vo * 0.95 + music * MUSIC_VOL
    for i, sc in enumerate(ACTIVE):           # effets ponctuels
        if sc.get("sfx"):
            mix = add_sfx(mix, starts[i], sc["sfx"])
    mix /= max(1e-6, float(np.max(np.abs(mix))))
    mix *= 0.92
    fo = int(0.9 * SR)                      # fondu de sortie
    mix[-fo:] *= np.linspace(1, 0, fo)
    wav = os.path.join(WORK, "mix.wav")
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with open(wav, "wb") as fh:
        import wave
        w = wave.open(fh, "wb")
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
        w.close()

    # --- video
    nframes = int(total * FPS)
    cmd = [FFMPEG, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", PRESET, "-crf", CRF,
           "-profile:v", "high", "-level", "4.1",
           "-g", str(FPS * 2), "-keyint_min", str(FPS), "-sc_threshold", "0",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           os.path.join(WORK, "video.mp4")]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    cache, lay_cache = {}, {}
    for f in range(nframes):
        t = f / FPS
        # scene courante
        i = 0
        for k in range(len(starts)):
            if t >= starts[k]:
                i = k
        tl = t - starts[i]
        dur = ends[i] - starts[i]

        frame = scene_frame(i, tl, dur)
        if tl < XF and i > 0:
            prev = scene_frame(i - 1, ends[i - 1] - starts[i - 1] + tl,
                               ends[i - 1] - starts[i - 1])
            frame = Image.blend(prev.convert("RGB"), frame.convert("RGB"),
                                min(1.0, tl / XF)).convert("RGBA")

        layer, lay = caption_layer(i, tl, dur, cache, lay_cache)
        y = int(lay["anchor"] * V_SCALE) - layer.height // 2
        frame.alpha_composite(layer, (0, max(0, y)))

        if ACTIVE[i].get("pill"):
            alpha = int(255 * min(1.0, max(0.0, (tl - 0.55) / 0.3)))
            draw_pill(frame, ACTIVE[i]["pill"], int(1420 * V_SCALE), alpha)

        if ACTIVE[i].get("bubbles"):
            draw_bubbles(frame, tl, V_SCALE)

        if t > 1.0:
            draw_badge(frame, t, int(255 * min(1.0, (t - 1.0) / 0.4)), V_SCALE)

        # barre de progression (haut de l'ecran)
        d = ImageDraw.Draw(frame, "RGBA")
        bw = int(W * min(1.0, t / total))
        d.rectangle([0, 0, bw, 9], fill=ORANGE + (210,))
        d.rectangle([bw, 0, W, 9], fill=(255, 255, 255, 45))

        proc.stdin.write(frame.convert("RGB").tobytes())
        if f % 60 == 0:
            print(f"  frame {f}/{nframes}  ({100*f//nframes}%)", flush=True)

    proc.stdin.close()
    proc.wait()

    subprocess.run([FFMPEG, "-y", "-v", "error",
                    "-i", os.path.join(WORK, "video.mp4"), "-i", wav,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                    "-shortest", "-movflags", "+faststart", OUT_MP4], check=True)

    size = os.path.getsize(OUT_MP4) / 1e6
    print(f"\nOK -> {OUT_MP4}  {W}x{H}  ({size:.1f} Mo, {total:.1f}s)")


if __name__ == "__main__":
    main()

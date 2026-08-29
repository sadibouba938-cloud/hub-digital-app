#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Controle technique des exports : specs Instagram Reels / TikTok / Facebook."""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_reel as B  # noqa: E402

FF = B.FFMPEG
FILES = [
    "reel_kit_ultime_1080x1920.mp4",
    "reel_kit_ultime_court_1080x1920.mp4",
    "reel_kit_ultime_feed_1080x1350.mp4",
    "reel_kit_ultime_feed_1080x1080.mp4",
]
ROOT = os.path.dirname(os.path.abspath(__file__))


def probe(path):
    r = subprocess.run([FF, "-i", path, "-hide_banner"], capture_output=True, text=True)
    info = r.stderr
    out = {}
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
    out["duration"] = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0
    m = re.search(r"Video: (\w+)", info)
    if m:
        out["vcodec"] = m.group(1)
    m = re.search(r"Video: .*?, (\d{3,5}x\d{3,5})", info)
    if m:
        out["size"] = m.group(1)
    m = re.search(r"([\d.]+) fps", info)
    if m:
        out["fps"] = round(float(m.group(1)))
    m = re.search(r"Video: .*?, ([\d.]+) kb/s", info)
    if m:
        out["vbitrate"] = int(float(m.group(1)))
    m = re.search(r"Video: .*?(yuv\w+p)", info)
    out["pix_fmt"] = m.group(1) if m else "?"
    m = re.search(r"Audio: (\w+).*?(\d+) Hz.*?([\d.]+) kb/s", info)
    if m:
        out.update(acodec=m.group(1), ar=int(m.group(2)), abitrate=int(float(m.group(3))))
    with open(path, "rb") as fh:
        head = fh.read(200000)
    out["faststart"] = head.find(b"moov") != -1 and head.find(b"moov") < head.find(b"mdat")
    out["mo"] = os.path.getsize(path) / 1e6
    return out


ok_all = True
print(f"{'fichier':42} {'format':11} {'duree':>7} {'fps':>4} {'video':>14} {'audio':>16} {'Mo':>6}  conformite")
print("-" * 130)
for f in FILES:
    p = os.path.join(ROOT, f)
    if not os.path.exists(p):
        print(f"{f:42} ABSENT")
        ok_all = False
        continue
    i = probe(p)
    checks = []
    checks.append(("H.264", i.get("vcodec") == "h264"))
    checks.append(("yuv420p", i.get("pix_fmt") == "yuv420p"))
    checks.append(("30fps", i.get("fps") == 30))
    checks.append(("AAC", i.get("acodec") == "aac"))
    checks.append(("debit 3-9Mb/s", 3000 <= i.get("vbitrate", 0) <= 9000))
    checks.append(("<=90s", i.get("duration", 999) <= 90))
    checks.append(("faststart", i.get("faststart")))
    checks.append(("<500Mo", i.get("mo", 999) < 500))
    bad = [n for n, v in checks if not v]
    ok_all &= not bad
    print(f"{f:42} {i.get('size','?'):11} {i.get('duration',0):7.1f} {i.get('fps','?'):>4} "
          f"{i.get('vcodec','?')} {i.get('vbitrate',0):5}kb/s {i.get('acodec','?')} "
          f"{i.get('ar','?')}Hz {i.get('abitrate',0):3}kb/s {i.get('mo',0):6.1f}  "
          + ("OK" if not bad else "KO: " + ", ".join(bad)))

print("\nRESULTAT :", "TOUT EST PRET A PUBLIER" if ok_all else "CORRECTIONS NECESSAIRES")

"""Builds optimized WebP versions of the images used by the site."""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402  (game list lives in build.py)

MEDIA = ROOT / "assets" / "media"
OUT = MEDIA / "opt"

ICON_LIMIT = 200
POSTER_LIMIT = 1200
SHOT_LIMIT = 1000
UI_LIMIT = 96
HERO_LIMIT = 1600

icons = {g["icon"] for g in build.GAMES}
posters = {g["poster"] for g in build.GAMES}
shots = {s for g in build.GAMES for s in g["shots"]}
ui = {"android.png", "apple.png"}
hero = {"nbanner1.jpg"}

limits = {}
limits.update({name: ICON_LIMIT for name in icons})
limits.update({name: POSTER_LIMIT for name in posters})
limits.update({name: SHOT_LIMIT for name in shots})
limits.update({name: UI_LIMIT for name in ui})
limits.update({name: HERO_LIMIT for name in hero})


def to_webp(name, limit):
    src = MEDIA / name
    if not src.exists():
        print(f"missing: {name}")
        return None, 0, 0
    out = OUT / (src.stem + ".webp")
    img = Image.open(src)
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    img = img.convert("RGBA" if has_alpha else "RGB")
    if max(img.size) > limit:
        img.thumbnail((limit, limit), Image.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(out, "WEBP", quality=82, method=6)
    return out, src.stat().st_size, out.stat().st_size


def main():
    before = after = 0
    count = 0
    for name, limit in sorted(limits.items()):
        out, b, a = to_webp(name, limit)
        if not out:
            continue
        before += b
        after += a
        count += 1
        print(f"{b/1024:8.1f} KB -> {a/1024:7.1f} KB  {out.name}")
    saved = before - after
    pct = (saved / before * 100) if before else 0
    print(f"\n{count} images: {before/1048576:.2f} MB -> {after/1048576:.2f} MB "
          f"(saved {saved/1048576:.2f} MB, {pct:.0f}%)")


if __name__ == "__main__":
    main()

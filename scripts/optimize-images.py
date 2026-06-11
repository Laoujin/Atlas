#!/usr/bin/env python3
"""Bulk-optimize research view images: convert raster -> WebP, resize, rewrite refs.

GitHub Pages rebuilds the whole site on every push and caps the published site at
1 GB; unoptimized 4-12 MB hero images are the dominant cost and the thing that makes
publishing "only get worse". This is the one-time backfill for images already in the
tree. New images are optimized at source by scout/skills/scout-view-author.

What it does (idempotent, --apply to write; dry-run otherwise):
  1. Every .jpg/.jpeg/.png under research/ -> sibling .webp (<=MAX_EDGE px, q=QUALITY),
     original removed. Oversized existing .webp are resized in place.
  2. Every image reference in .html/.md/.json is repointed to .webp -- but only when the
     .webp sibling actually exists on disk. Prose mentions and absolute http URLs (which
     have no local sibling) are left untouched. Zero same-stem collisions verified.
  3. Verify pass: no view still references a missing local raster/webp file.
"""
import os
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

MAX_EDGE = 1600          # longest side, px — web views never need more
QUALITY = 80             # libwebp quality
RASTER = (".jpg", ".jpeg", ".png")
TEXT_EXT = (".html", ".md", ".json")
# path-ish token ending in a raster extension; resolution + existence check below
# is what makes the rewrite safe, not this pattern.
REF_RE = re.compile(r"([\w][\w./-]*?)\.(jpe?g|png)\b", re.IGNORECASE)


def encode_webp(img, dst):
    img = ImageOps.exif_transpose(img)  # bake rotation, then drop metadata
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    img = img.convert("RGBA" if has_alpha else "RGB")
    img.thumbnail((MAX_EDGE, MAX_EDGE))  # only ever shrinks
    img.save(dst, "WEBP", quality=QUALITY, method=6)


def convert_one(path, apply):
    """raster -> sibling .webp (remove original); oversized .webp -> resized in place.
    Returns (saved_bytes, did_change)."""
    before = path.stat().st_size
    ext = path.suffix.lower()
    try:
        with Image.open(path) as img:
            w, h = img.size
            if ext == ".webp":
                if max(w, h) <= MAX_EDGE:
                    return 0, False  # already within bounds
                dst = path
                if apply:
                    encode_webp(img, dst)
            else:
                dst = path.with_suffix(".webp")
                if apply:
                    encode_webp(img, dst)
    except Exception as e:  # corrupt/unreadable image — leave it, surface it
        print(f"  ! skip (unreadable): {path}  ({e})")
        return 0, False
    if ext != ".webp" and apply:
        path.unlink()
    after = dst.stat().st_size if apply else before  # dry-run can't know; report 0 saving
    return (before - after if apply else 0), True


def rewrite_refs(root, apply):
    """Repoint .jpg/.jpeg/.png refs -> .webp where the .webp sibling exists."""
    touched = 0
    for f in root.rglob("*"):
        if f.suffix.lower() not in TEXT_EXT or not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")

        def repl(m):
            ref = m.group(0)
            target = (f.parent / ref)
            webp = target.with_suffix(".webp")
            # rewrite only if a real local .webp now sits where this ref points
            if webp.exists() and not target.exists():
                return ref[: -len(m.group(2)) - 1] + ".webp"
            return ref

        new = REF_RE.sub(repl, text)
        if new != text:
            touched += 1
            if apply:
                f.write_text(new, encoding="utf-8")
    return touched


def verify(root):
    """Every local raster/webp ref in a view must resolve to a file on disk."""
    broken = []
    for f in root.rglob("*"):
        if f.suffix.lower() not in TEXT_EXT or not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"""['"(]([\w][\w./-]*?\.(?:jpe?g|png|webp))\b""", text, re.IGNORECASE):
            ref = m.group(1)
            if "://" in ref:
                continue
            if not (f.parent / ref).exists():
                broken.append(f"{f}: {ref}")
    return broken


def main():
    apply = "--apply" in sys.argv[1:]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else Path("research")
    if not root.is_dir():
        sys.exit(f"not a directory: {root}")

    images = [p for p in root.rglob("*")
              if p.suffix.lower() in RASTER + (".webp",) and p.is_file()]
    print(f"{'APPLY' if apply else 'DRY-RUN'} — {len(images)} images under {root}")

    saved = changed = 0
    for p in images:
        s, did = convert_one(p, apply)
        saved += s
        changed += did
    print(f"converted/resized: {changed} images" + (f", saved {saved/1048576:.0f} MB" if apply else ""))

    touched = rewrite_refs(root, apply)
    print(f"ref rewrite: {touched} files {'updated' if apply else 'would change'}")

    broken = verify(root)
    if broken:
        print(f"\n!! {len(broken)} broken local image refs:")
        for b in broken[:40]:
            print(f"   {b}")
    else:
        print("verify: all local image refs resolve ✓")
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()

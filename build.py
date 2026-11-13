#!/usr/bin/env python3
"""Build the Clara Guzman portfolio site.

Reads content/site.yaml and content/works.yaml, makes web-sized copies of the
images in images/src/, and writes the HTML pages. Run it after every change:

    python3 build.py

Needs: pip install pyyaml jinja2 pillow
"""
import datetime
import hashlib
import json
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "images" / "src"
WEB = ROOT / "images" / "web"
SIZES = {"l": 2000, "m": 900}   # long edge in pixels
QUALITY = {"l": 82, "m": 80}

MANIFEST_FILE = WEB / "manifest.json"
MANIFEST = json.loads(MANIFEST_FILE.read_text()) if MANIFEST_FILE.exists() else {}

errors = []


def load_yaml(name):
    with open(ROOT / "content" / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_src(stem):
    for ext in (".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG"):
        p = SRC / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def make_image(stem):
    """Create images/web/<stem>-l.jpg and -m.jpg. Returns info dict or None."""
    src = find_src(stem)
    if src is None:
        errors.append(f"missing image: images/src/{stem}.jpg")
        return None
    info = {"stem": stem}
    im = None
    digest = hashlib.sha1(src.read_bytes()).hexdigest()
    changed = MANIFEST.get(stem) != digest
    MANIFEST[stem] = digest
    for key, edge in SIZES.items():
        out = WEB / f"{stem}-{key}.jpg"
        if changed or not out.exists():
            if im is None:
                im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
            copy = im.copy()
            copy.thumbnail((edge, edge), Image.LANCZOS)
            copy.save(out, "JPEG", quality=QUALITY[key], optimize=True, progressive=True)
        with Image.open(out) as o:
            info[key] = {"src": f"images/web/{out.name}", "w": o.width, "h": o.height}
    return info


def paragraphs(text):
    if not text:
        return []
    return [" ".join(p.split()) for p in str(text).strip().split("\n\n") if p.strip()]


def main():
    site = load_yaml("site.yaml")
    works = load_yaml("works.yaml") or []
    WEB.mkdir(parents=True, exist_ok=True)

    collections = {c["slug"]: dict(c, works=[]) for c in site["collections"]}
    seen = set()
    for w in works:
        slug = w.get("slug")
        if not slug or slug in seen:
            errors.append(f"missing or duplicate slug: {slug!r}")
            continue
        seen.add(slug)
        if w.get("collection") not in collections:
            errors.append(f"{slug}: unknown collection {w.get('collection')!r}")
            continue
        w["image"] = make_image(slug)
        if w["image"] is None:
            continue
        w["details_img"] = [i for i in (make_image(f"{slug}-detail-{n}") for n in range(1, int(w.get("details") or 0) + 1)) if i]
        w["process_img"] = [i for i in (make_image(f"{slug}-process-{n}") for n in range(1, int(w.get("process") or 0) + 1)) if i]
        w["paras"] = paragraphs(w.get("statement"))
        w["year"] = str(w["year"]) if w.get("year") else ""
        w["url"] = f"works/{slug}.html"
        collections[w["collection"]]["works"].append(w)

    # Previous / next within each collection
    for c in collections.values():
        ws = c["works"]
        for i, w in enumerate(ws):
            w["prev"] = ws[i - 1] if i > 0 else None
            w["next"] = ws[i + 1] if i < len(ws) - 1 else None
            w["coll"] = c
        c["cover"] = next((w for w in ws if w.get("featured")), ws[0] if ws else None)

    all_works = [w for c in collections.values() for w in c["works"]]
    featured = [w for w in all_works if w.get("featured")]
    portrait = make_image(Path(site["portrait"]).stem) if site.get("portrait") else None

    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    common = dict(site=site, collections=list(collections.values()),
                  year=datetime.date.today().year, bio=paragraphs(site.get("bio")))

    def render(template, out, depth=0, **kw):
        html = env.get_template(template).render(root="../" * depth, out=out, **common, **kw)
        path = ROOT / out
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        return out

    pages = [render("home.html", "index.html", featured=featured)]
    pages.append(render("about.html", "about.html", portrait=portrait))
    pages.append(render("contact.html", "contact.html"))
    for c in collections.values():
        pages.append(render("collection.html", f"collection/{c['slug']}.html", 1, c=c))

    # Remove pages for works that were deleted from works.yaml
    if (ROOT / "works").exists():
        for old in (ROOT / "works").glob("*.html"):
            if old.stem not in seen:
                old.unlink()
    for w in all_works:
        pages.append(render("work.html", w["url"], 1, w=w))

    # Old 2022 site addresses -> new pages
    redirects = {"portraits.html": "collection/pastel.html", "figures.html": "collection/drawing.html",
                 "other.html": "collection/watercolor.html", "magazine.html": "index.html",
                 "extra.html": "index.html"}
    for old, new in redirects.items():
        render("redirect.html", old, target=new)

    # Remove web images no longer used by any work
    used = {f"{s}-{k}.jpg" for s in [p.stem for p in SRC.iterdir()] for k in SIZES}
    for f in WEB.glob("*.jpg"):
        if f.name not in used:
            f.unlink()
    stems = {p.stem for p in SRC.iterdir()}
    MANIFEST_FILE.write_text(json.dumps({k: v for k, v in sorted(MANIFEST.items()) if k in stems}, indent=0))

    base = site["url"].rstrip("/")
    sitemap = "\n".join(f"  <url><loc>{base}/{'' if p == 'index.html' else p}</loc></url>" for p in pages)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap}\n</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    (ROOT / ".nojekyll").touch()

    print(f"Built {len(pages)} pages, {len(all_works)} works.")
    if errors:
        print("\nProblems to fix:")
        for e in errors:
            print("  -", e)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Clara Guzman portfolio — instructions for Claude

This repository is Clara Guzman's art portfolio, published with GitHub Pages at
https://guzmanart.github.io. Clara is an artist, not a developer: keep explanations
short and non-technical, and make changes for her rather than telling her how.

## How the site works

- `content/site.yaml` holds site-wide text: intro, bio, email, Instagram, collections.
- `content/works.yaml` lists every artwork, in display order within each collection.
- `images/src/` holds the original photos. The main image for a work is
  `images/src/<slug>.jpg`; close-ups are `<slug>-detail-1.jpg`, `-detail-2.jpg`, ...;
  in-progress photos are `<slug>-process-1.jpg`, ...
- `build.py` makes web-sized images in `images/web/` and writes all HTML pages
  (`index.html`, `about.html`, `contact.html`, `collection/*.html`, `works/*.html`).
  Never edit the generated HTML by hand: edit content or `templates/`, then build.
- `templates/` (Jinja2) and `assets/style.css` control the design.
- A GitHub Action (`.github/workflows/build.yml`) reruns `build.py` on every push that
  touches content, images or templates, and commits the result. So the site also
  updates if Clara edits files directly on github.com.

## Adding a new artwork

1. Choose a short slug from the title (lowercase, dashes): `annunciation-study`.
2. Save the photo as `images/src/<slug>.jpg` (convert HEIC/PNG to JPG; keep the full
   resolution; crop away easel, wall or table edges if she asks or if they're obvious).
3. Add an entry to `content/works.yaml` in the right collection section:
   ```yaml
   - slug: annunciation-study
     title: Annunciation Study
     collection: oil          # oil, pastel, watercolor or drawing
     medium: Oil on panel
     size: 40 × 50 cm
     year: 2026
     featured: false          # true = also shown on the home page
     status: available        # optional: available, sold, private, commission
     statement: |
       Optional words about the piece, in Clara's voice.
   ```
   Only include facts Clara gave you. Ask for title, medium, size and year if missing,
   but don't block on them: anything left out is simply not shown.
4. Run `python3 build.py` (install once with `pip install pyyaml jinja2 pillow`).
   It must finish without "Problems to fix".
5. Commit with a plain message ("Add Annunciation Study") and push to `master`.
   The live site updates within a minute or two.

## Other common requests

- Reorder works: move entries within `works.yaml`. The first `featured: true` work is
  the large image on the home page.
- Remove a work: delete its entry and its files in `images/src/`, then build.
- Edit bio, intro, email, Instagram: `content/site.yaml`.
- New collection: add it under `collections` in `site.yaml`, then use its slug.
- Custom domain: add a `CNAME` file with the domain, update `url` in `site.yaml`, and
  have Clara set the DNS records at her registrar per GitHub Pages docs.

## Rules

- Keep the classical look: Cormorant Garamond / EB Garamond, warm paper tones,
  artwork in white mats, generous space. Don't add frameworks or build tools.
- Images are stripped of metadata (including GPS location) by `build.py`; keep it that way.
- Show Clara the result (a screenshot or the live link) after each change.

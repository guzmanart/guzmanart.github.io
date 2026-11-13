# Clara Guzman — portfolio

Live at **https://guzmanart.github.io**

## Updating the site with Claude

Connect this GitHub account to Claude (Settings → Connectors → GitHub), then just ask,
for example: *"Add this painting to my oil collection: Annunciation Study, oil on panel,
40 × 50 cm, 2026."* Claude follows the instructions in `CLAUDE.md`.

## Updating the site by hand on github.com (works on the free Claude plan)

1. **Add the photo:** open the `images/src` folder → **Add file → Upload files**.
   Name it with a short id, like `annunciation-study.jpg`.
2. **Describe it:** open `content/works.yaml` → pencil icon → add an entry like the
   others (you can ask Claude to write it for you), using the same id as `slug`.
3. **Commit changes.** GitHub rebuilds the site automatically; it's live in a minute
   or two. (See the progress under the **Actions** tab.)

To change your bio, email or Instagram, edit `content/site.yaml` the same way.

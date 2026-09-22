# Baby Prep — local-first dashboard

A calm, visual planner for everything the baby needs — without overspending.
**No accounts, no server, no tracking: everything stays on your device.**

Static app (HTML + Alpine.js + Tailwind): item data lives in `static/app-data.js`,
your progress, links, brands, colors, theme and baby details live in this
browser's storage, and a backup file can be downloaded anytime.

The account-based multi-user version is preserved on the `main` branch.

## Run locally

```bash
python serve.py
```

Open http://localhost:8123 (or http://<your-ip>:8123 from a phone on the same Wi-Fi).
Any static file server works; there is nothing to install.

## Data

- Edit items/brands/tips in `static/app-data.js` (`window.APP_DATA = {...}`), then
  validate with `python check_data.py`.
- All user state is in `localStorage` under `babyPrepState`. "Baby details →
  Download backup" exports it as JSON; "Restore from file" imports it (e.g. when
  switching phones or clearing the browser).

## What is interactive

- Overview: season capsule, "Baby now" size card and countdown (from the due date),
  per-category progress cards, outfit recipes, brand strategy, tips
- Categories: Baby clothing (role + size filters, per-size targets and counters),
  Sleep (Essentials/Optional tabs — tap a badge to re-classify for yourself),
  Diapering & bath & care, Baby gear, Leisure, Mom, Tips & tricks
- Every item: multiple brand chips, color chips, a product link, owned counters
- Themes: peach (default), dusty blue, dusty burgundy, soft prune — in Baby details
- EU ↔ US size labels (50/56/62 ↔ NB/0–3M/3–6M)

## Deploying (GitHub Pages)

Push this branch to GitHub, then in the repo: Settings → Pages → deploy from the
branch. The manifest and service worker use relative paths, so the project
subpath (`user.github.io/repo/`) works. The app is a PWA: on iPhone, open in
Safari → Share → Add to Home Screen.

## Planning notes

The wardrobe deliberately separates daytime layering from sleep. The winter layer
guidance follows NHS advice to use roughly one extra layer in winter, while
keeping sleep clothing simple to avoid overheating. Per-size guidance keeps size
50 small (the stage lasts only weeks) and carries the working wardrobe in 56/62.

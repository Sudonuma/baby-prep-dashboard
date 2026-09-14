# Baby Winter Wardrobe Dashboard

A small FastAPI + Jinja2 + Tailwind + Alpine.js MVP for planning a winter newborn wardrobe.

## Run

```bash
conda create -n baby-dashboard python=3.12 -y
conda activate baby-dashboard
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000

## Accounts & personalization

- Register at `/register` (or log in at `/login`). Accounts and profiles live in a local SQLite database at `data/app.db` — auto-created on first start, gitignored.
- After signing up you're asked for your baby's name and due date (both optional). The dashboard personalizes from these: the baby name appears in the overview, and the due date sets the arrival season ("Winter arrival", the season capsule chip) plus a due-day countdown.
- Item quantities, links, brand picks, laundry cadence, size system and theme live in the database **per account** — new accounts start fresh, and your dashboard follows your login across devices (saved with a short debounce as you click).

## What is interactive

- Filter clothing by role (base, sleep, day, layer, cute, accessory, outdoor)
- Size selector (All / 50 / 56 / 62): each clothing item carries per-size target quantities, per-size owned counters, and per-size progress. EU sizes are the baby's max height in cm (50 ≈ 0–1 mo, 56 ≈ 1–3 mo, 62 ≈ 3–6 mo)
- EU/US size label toggle (NB / 0–3M / 3–6M); data and saved counts always stay on the canonical EU sizes
- Dedicated sleep section with All / Essentials / Optional tabs; essentials covers sleepwear (swaddle, sleepsack) and the sleep setup, each item with its own counter
- Diapering & bath & care section with All / Diapering / Bath / Care tabs, each item with its own counter
- Baby gear section for the big-ticket basics (stroller, car seat, carrier, bouncer, playard, swing)
- Leisure section for awake time (activity gym, books, plush toys, toys)
- Mom section with All / Nursing / Health & care tabs — nursing essentials and postpartum care
- Increment/decrement owned quantities (clothing counters adjust the selected size)
- Progress toward the starter capsule for the selected size
- Adjust laundry cadence
- Click outfit recipes to see the layer stack
- Add, edit or remove a product link on any item (saved in this browser) — park things you plan to buy when they go on sale; a data-provided link acts as the default
- Interactive shopping strategy: curated brand pools (high-quality basics / cute outfits for a good price) — pick brands, add your own, and set or change the brand on any item card (all saved in this browser). Clothing cards suggest from the strategy pools; sleep, care, gear and leisure cards each have their own brand suggestions
- Quantities persist in browser localStorage

## Design direction

Soft dusty-peach pink, warm off-white, dark brown text, rounded cards, minimal dashboard density.

## Roadmap

Planned next steps live in [ROADMAP.md](ROADMAP.md): due-date-driven wardrobe suggestions, an EU/US size toggle, weather-based dressing guidance, price/sale watching, brand and strategy options, and a paperwork tracker.

## Planning notes

The dashboard deliberately separates daytime layering from sleep. The winter layer guidance follows NHS advice to use roughly one extra layer in winter, while keeping sleep clothing simple to avoid overheating. Sanetta's current size guide uses 50/56/62/68/74/80 with 50 listed at 0 months, 56 at 1 month and 62 at 3 months.

The starter numbers are editable planning defaults rather than a prescriptive shopping list. Per-size guidance follows the common recommendation to keep size 50 small (the stage lasts only a few weeks and babies may skip it) and carry the working wardrobe in 56/62, with enough pieces for roughly a week between laundry loads.

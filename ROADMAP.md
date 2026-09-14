# Roadmap

Ideas for growing the winter-wardrobe MVP into a general baby-prep dashboard.
Work top-to-bottom: each phase builds on the one before it.

## Phase 1 — Due-date-driven planning (core)

- [ ] Due-date input on the dashboard
- [ ] Derive the birth season and the seasons the first ~6 months will cover
- [ ] Suggest the right capsule (items + target quantities) for those seasons, replacing the fixed winter list
- [ ] Quantity guidance per size band — "buy X for newborn, Y for 0–3 months, Z for 3–6 months" — with a nudge not to overstock sizes babies outgrow quickly
- [ ] Size label toggle: EU (50/56/62/68) ↔ US (NB, 0–3M, 3–6M), backed by one canonical size scale in the data model

## Phase 2 — Daily dressing guidance

- [ ] Weather-based advice: current temperature or forecast → recommended layer recipe from the existing OUTFITS data
- [ ] "Is baby too cold / too warm?" helper — how to check (nape of the neck / chest, not hands and feet), overheating signs, and TOG-style sleep guidance
- [ ] Keep the day-vs-sleep separation: sleep overheating guidance stays its own section

## Phase 3 — Shopping intelligence

- [ ] Price watch: user adds product URLs from the shops they actually buy from; dashboard checks prices on a schedule
- [ ] Sale alerts: notify (email, push, or browser notification) when a watched item drops in price
- [ ] Brand options per item — quality notes, price range, sizing quirks — so the user can pick what matters to them
- [ ] Buying strategy tips per item: buy now vs wait-and-see, new vs used, how many to start with; user-customizable
- [ ] Item comparison: when the same item type exists across brands/shops, compare on reviews plus fit for the user's own case (climate, laundry cadence, budget)
- [ ] Cost estimate: editable estimated prices per essential with a running total per category and overall, so the full prep can be budgeted before buying

## Phase 4 — Readiness admin

- [ ] Papers tracker: checklist for paperwork readiness — pre-birth (hospital pre-registration, parental leave, insurance) and post-birth (birth registration, passport, etc.) with configurable categories

## Phase 5 — Guides & community content

- [ ] Tips & tricks: curated community tips (e.g., from Reddit parenting communities) organized by topic — layering, sleep, diapering hacks, budget buys — with sources
- [ ] How to take care of your baby: visual step-by-step guides (video or picture series) — how to layer for weather, how to dress a newborn, how to change a diaper, first bath, swaddling, and similar basics

## Phase 6 — Other category

- [ ] Catch-all "Other" category for everything outside baby prep proper: nursery furniture and home decorations, welcome-baby party supplies, and misc household purchases

## Before sharing publicly

- [ ] Neutral default item list: the public version shouldn't default to one person's chosen brands and purchase links
- [ ] Data safety: export/import (or server-side storage) so clearing browser storage doesn't wipe progress

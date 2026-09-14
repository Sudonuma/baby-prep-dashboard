"""One-off check: render the dashboard template and confirm all category sections come out complete."""
from jinja2 import Environment, FileSystemLoader

import app as dashboard_app

env = Environment(loader=FileSystemLoader("templates"))
html = env.get_template("index.html").render(
    wardrobe=dashboard_app.WARDROBE,
    sleep=dashboard_app.SLEEP,
    care=dashboard_app.CARE,
    gear=dashboard_app.GEAR,
    leisure=dashboard_app.LEISURE,
    mom=dashboard_app.MOM,
    tips=dashboard_app.TIPS,
    brand_tiers=dashboard_app.BRAND_TIERS,
    category_brands=dashboard_app.CATEGORY_BRANDS,
    outfits=dashboard_app.OUTFITS,
    # multi-user personalization defaults
    baby_name=None, due_date=None, season_label="Winter", days_to_due=None,
    baby_display="your little one", username="tester", server_theme=None,
    baby_now=None,
)

# Sleep section: sleepwear moved out of clothing, essentials and optional groups present.
wardrobe_ids = {item["id"] for item in dashboard_app.WARDROBE}
sleep_items = dashboard_app.SLEEP
sleep_ids = {item["id"] for item in sleep_items}
assert "swaddle" not in wardrobe_ids and "sleevesack" not in wardrobe_ids, "sleepwear still in clothing list"
essentials_ids = {item["id"] for item in sleep_items if item["group"] == "Essentials"}
assert {"swaddle", "sleevesack", "crib", "bassinet", "cribmattress", "cribsheets"} <= essentials_ids, "essentials group wrong"
for expected in ("Crib", "Bassinet or bedside sleeper", "Crib mattress", "Crib sheets", "Baby monitor"):
    assert expected in html, f"sleep item missing from rendered page: {expected}"
assert "sleepFilter" in html, "sleep sub-filter tabs missing"

# Care section: diapering, bath and care groups with their tabs.
for expected in ("Changing pad", "Diaper bag", "Bathtub", "Bath thermometer",
                 "Baby thermometer", "Brush & comb"):
    assert expected in html, f"care item missing from rendered page: {expected}"
for group in ("Diapering", "Bath", "Care"):
    assert html.count(f">{group}<") >= 1 or group in html, f"care group missing: {group}"
assert "careFilter" in html, "care sub-filter tabs missing"
assert "babyItemLinks" in html and "+ link" in html, "per-item link editor missing"

# Gear section: big-ticket items present.
for expected in ("Stroller", "Infant car seat", "Structured carrier or wrap carrier",
                 "Bouncer", "Playard / travel crib", "Swing"):
    assert expected in html, f"gear item missing from rendered page: {expected}"
assert "GearSetup" in html, "gear nav wiring missing"

# Leisure section: awake-time items present.
for expected in ("Activity gym / mat", "Books", "Soft plush toys", "Toys"):
    assert expected in html, f"leisure item missing from rendered page: {expected}"
assert "LeisureSetup" in html, "leisure nav wiring missing"

# Mom section: nursing and health & care groups with tabs.
for expected in ("Nursing pads", "Silver cups", "Milk pumps", "Nursing bras",
                 "Nursing pillow", "Nipple creams", "Maternity pads",
                 "Maternity underwear", "Comfortable pyjamas"):
    assert expected in html, f"mom item missing from rendered page: {expected}"
assert "momFilter" in html, "mom sub-filter tabs missing"

# Multi-user personalization renders with defaults.
assert "WINTER CAPSULE" in html, "season capsule chip missing"
assert "Baby • Winter arrival" in html, "season header missing"
assert "your little one" in html, "neutral baby-name fallback missing"
assert "Your little one is on the way" in html, "baby-now fallback card missing"

# Tips section: advice moved out of the hero lives here now.
assert "Planning principle" not in html, "old planning card still present"
for expected in ("One extra layer", "Zips beat buttons", "Keep sleep separate from cute layering"):
    assert expected in html, f"tip missing: {expected}"
assert "tipsFilter" in html, "tips tabs missing"

def json_escaped(s: str) -> str:
    """Approximate Jinja's htmlsafe tojson: & <> ' and non-ASCII become \\uXXXX."""
    out = []
    for ch in s:
        o = ord(ch)
        if ch in "&<>'":
            out.append("\\u%04x" % o)
        elif o < 128:
            out.append(ch)
        else:
            out.append("\\u%04x" % o)
    return "".join(out)

# Shopping strategy: brand pools with picker + custom brands.
# Brand chips render client-side from the JSON blob, so match either raw or escaped.
assert "babyBrands" in html, "brand picker/datalist missing"
for tier in dashboard_app.BRAND_TIERS:
    assert tier["name"] in html, f"brand tier missing: {tier['name']}"
    for b in tier["brands"]:
        if b not in html and json_escaped(b) not in html:
            raise AssertionError(f"brand missing from pool: {b}")
# Per-category brand pools exist and feed the per-item brand menus.
assert "brandMenu" in html and "filteredBrandOptions" in html, "custom brand dropdown missing"
for cat, brands in dashboard_app.CATEGORY_BRANDS.items():
    assert cat in html, f"category brand pool missing: {cat}"
    for b in brands:
        if b not in html and json_escaped(b) not in html:
            raise AssertionError(f"brand missing from {cat} pool: {b}")

# Size planning: every clothing item needs per-size targets consistent with its size list.
for item in dashboard_app.WARDROBE:
    assert "size_targets" in item, f"{item['id']} missing size_targets"
    assert set(item["size_targets"]) <= set(item["sizes"]), f"{item['id']} size_targets/sizes mismatch"
assert "sizeFilter" in html, "size selector missing"

cards = html.count("visibleForFilter(")
print(
    f"Rendered OK: {len(html)} chars, {cards} clothing cards, "
    f"{len(dashboard_app.WARDROBE)} clothing items, {len(dashboard_app.SLEEP)} sleep items, "
    f"{len(dashboard_app.CARE)} care items, {len(dashboard_app.GEAR)} gear items, "
    f"{len(dashboard_app.LEISURE)} leisure items, {len(dashboard_app.MOM)} mom items"
)

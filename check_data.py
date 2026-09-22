"""Validate static/app-data.js: parses and every item is well-formed."""
import json

raw = open("static/app-data.js").read()
prefix = "window.APP_DATA ="
assert raw.startswith(prefix), "app-data.js must start with 'window.APP_DATA ='"
data = json.loads(raw[len(prefix):].rstrip().rstrip(";"))

for cat in ("wardrobe", "sleep", "care", "gear", "leisure", "mom", "tips"):
    assert isinstance(data.get(cat), list) and data[cat], f"missing category: {cat}"
assert data["outfits"], "missing outfits"
assert data["brandTiers"] and data["categoryBrands"], "missing brand pools"

ids = []
for cat in ("wardrobe", "sleep", "care", "gear", "leisure", "mom"):
    for item in data[cat]:
        for field in ("id", "name", "icon", "unit"):
            assert field in item, f"{item.get('id')} missing {field}"
        assert "target" in item or "size_targets" in item, f"{item['id']} needs target or size_targets"
        ids.append(item["id"])
        if item.get("size_targets"):
            assert set(item["size_targets"]) <= set(item["sizes"]), f"{item['id']} size_targets/sizes mismatch"
assert len(ids) == len(set(ids)), "duplicate item ids"

print(f"Data OK: {len(ids)} items across 6 categories, "
      f"{len(data['tips'])} tips, {len(data['outfits'])} outfits")

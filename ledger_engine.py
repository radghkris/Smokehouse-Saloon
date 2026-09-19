import json
import math
import re
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "ledger_data.json"

SEED = {
    "ingredients": {
        "tea-leaf": {"name": "Tea Leaf", "unit": "ea"},
        "orange": {"name": "Orange", "unit": "ea"},
        "sugar": {"name": "Sugar", "unit": "ea"},
        "water": {"name": "Water", "unit": "ea"},
        "coca-leaf": {"name": "Coca Leaf", "unit": "ea"},
        "lime": {"name": "Lime", "unit": "ea"},
        "prepared-meat-cut": {"name": "Prepared Meat Cut", "unit": "ea"},
        "beans": {"name": "Beans", "unit": "ea"},
        "pimenta": {"name": "Pimenta", "unit": "ea"},
        "tomato": {"name": "Tomato", "unit": "ea"},
        "whisky": {"name": "Whisky", "unit": "ea"},
        "barley": {"name": "Barley", "unit": "ea"},
        "cherry": {"name": "Cherry", "unit": "ea"},
        "potato": {"name": "Potato", "unit": "ea"},
        "corn": {"name": "Corn", "unit": "ea"},
        "wheat": {"name": "Wheat", "unit": "ea"},
        "onion": {"name": "Onion", "unit": "ea"},
        "milk": {"name": "Milk", "unit": "ea"},
        "carrot": {"name": "Carrot", "unit": "ea"},
        "creeping-thyme": {"name": "Creeping Thyme", "unit": "ea"},
        "coffee-beans": {"name": "Coffee Beans", "unit": "ea"},
        "sugarcane": {"name": "Sugarcane", "unit": "ea"},
    },
    "conversions": [
        {"id": "sugarcane-to-sugar", "inputId": "sugarcane", "inputQty": 1, "outputId": "sugar",
         "outputQty": 5, "cost": 0, "note": "20 Sugarcane → 100 Sugar"},
    ],
    "vendors": [
        {"id": "armadillo-tea-leaf", "ingredientId": "tea-leaf", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-tea-leaf", "ingredientId": "tea-leaf", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-orange", "ingredientId": "orange", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-orange", "ingredientId": "orange", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-sugarcane", "ingredientId": "sugarcane", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-sugarcane", "ingredientId": "sugarcane", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-lime", "ingredientId": "lime", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-lime", "ingredientId": "lime", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-beans", "ingredientId": "beans", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-beans", "ingredientId": "beans", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-pimenta", "ingredientId": "pimenta", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-pimenta", "ingredientId": "pimenta", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-tomato", "ingredientId": "tomato", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-tomato", "ingredientId": "tomato", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-barley", "ingredientId": "barley", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-barley", "ingredientId": "barley", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-cherry", "ingredientId": "cherry", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-cherry", "ingredientId": "cherry", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-potato", "ingredientId": "potato", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-potato", "ingredientId": "potato", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-corn", "ingredientId": "corn", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-corn", "ingredientId": "corn", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-wheat", "ingredientId": "wheat", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-wheat", "ingredientId": "wheat", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-onion", "ingredientId": "onion", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-onion", "ingredientId": "onion", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-carrot", "ingredientId": "carrot", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-carrot", "ingredientId": "carrot", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-creeping-thyme", "ingredientId": "creeping-thyme", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-creeping-thyme", "ingredientId": "creeping-thyme", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-coffee-beans", "ingredientId": "coffee-beans", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.10, "stock": "unknown"},
        {"id": "valentine-coffee-beans", "ingredientId": "coffee-beans", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.10, "stock": "unknown", "note": "regulated — matches Armadillo now"},
        {"id": "armadillo-milk", "ingredientId": "milk", "vendorName": "Armadillo Market", "town": "Armadillo", "price": 0.25, "stock": "unknown"},
        {"id": "valentine-milk", "ingredientId": "milk", "vendorName": "Valentine Market", "town": "Valentine", "price": 0.20, "stock": "out", "note": "No stock yet — watching for restock"},
        {"id": "milk-crate-note", "ingredientId": "milk", "vendorName": "Milk Crate (30 ea)", "town": "", "price": None, "stock": "unknown", "note": "Bulk pack of 30 Milk — crate price not set yet"},
        {"id": "general-store-whisky", "ingredientId": "whisky", "vendorName": "General Store", "town": "", "price": 0.06, "stock": "available"},
        {"id": "general-store-water", "ingredientId": "water", "vendorName": "General Store", "town": "Saint Denis", "price": 0.02, "stock": "available"},
        {"id": "coca-leaf-dealer", "ingredientId": "coca-leaf", "vendorName": "Coca Leaf Dealer", "town": "", "price": None, "stock": "out", "note": "Dealer on vacation — returning soon. Legal item."},
    ],
    "recipes": {
        "sun-brewed-sweet-tea": {"name": "Sun-Brewed Sweet Tea", "category": "drink", "yieldQty": 1, "salePrice": 0.45, "active": True,
                                  "ingredients": [{"ingredientId": "tea-leaf", "qty": 2}, {"ingredientId": "orange", "qty": 1}, {"ingredientId": "sugar", "qty": 1}, {"ingredientId": "water", "qty": 1}]},
        "blackwater-coca-tonic": {"name": "Blackwater Coca Tonic", "category": "drink", "yieldQty": 1, "salePrice": 0.45, "active": False,
                                   "ingredients": [{"ingredientId": "coca-leaf", "qty": 1}, {"ingredientId": "sugar", "qty": 1}, {"ingredientId": "lime", "qty": 1}, {"ingredientId": "water", "qty": 1}]},
        "buck-country-chili": {"name": "Buck Country Chili", "category": "food", "yieldQty": 1, "salePrice": 0.45, "active": True,
                                "ingredients": [{"ingredientId": "prepared-meat-cut", "qty": 2}, {"ingredientId": "beans", "qty": 2}, {"ingredientId": "pimenta", "qty": 1}, {"ingredientId": "tomato", "qty": 1}]},
        "irishmans-dram": {"name": "Irishman’s Dram", "category": "drink", "yieldQty": 1, "salePrice": 0.45, "active": True,
                            "ingredients": [{"ingredientId": "whisky", "qty": 2}, {"ingredientId": "barley", "qty": 1}]},
        "blackwater-old-fashioned": {"name": "Blackwater Old Fashioned", "category": "drink", "yieldQty": 1, "salePrice": 0.45, "active": True,
                                      "ingredients": [{"ingredientId": "whisky", "qty": 1}, {"ingredientId": "orange", "qty": 1}, {"ingredientId": "cherry", "qty": 1}, {"ingredientId": "sugar", "qty": 1}]},
        "brunswick-stew": {"name": "Brunswick Stew", "category": "food", "yieldQty": 1, "salePrice": 0.45, "active": True,
                            "ingredients": [{"ingredientId": "prepared-meat-cut", "qty": 2}, {"ingredientId": "potato", "qty": 1}, {"ingredientId": "corn", "qty": 1}, {"ingredientId": "tomato", "qty": 1}]},
        "cattlemans-ruin": {"name": "Cattleman’s Ruin", "category": "food", "yieldQty": 3, "salePrice": 0.45, "active": True,
                             "ingredients": [{"ingredientId": "prepared-meat-cut", "qty": 3}, {"ingredientId": "wheat", "qty": 2}, {"ingredientId": "onion", "qty": 1}, {"ingredientId": "sugar", "qty": 1}]},
        "mamas-chicken-dumplings": {"name": "Mama’s Chicken & Dumplings", "category": "food", "yieldQty": 1, "salePrice": 0.45, "active": True,
                                     "ingredients": [{"ingredientId": "prepared-meat-cut", "qty": 2}, {"ingredientId": "wheat", "qty": 2}, {"ingredientId": "milk", "qty": 1}, {"ingredientId": "carrot", "qty": 1}]},
        "dirty-weenies": {"name": "Dirty Weenies", "category": "food", "yieldQty": 1, "salePrice": 0.45, "active": True,
                           "ingredients": [{"ingredientId": "prepared-meat-cut", "qty": 2}, {"ingredientId": "beans", "qty": 2}, {"ingredientId": "onion", "qty": 1}, {"ingredientId": "sugar", "qty": 1}]},
        "backcountry-cottontail-stew": {"name": "Backcountry Cottontail Stew", "category": "food", "yieldQty": 1, "salePrice": 0.45, "active": True,
                                         "ingredients": [{"ingredientId": "prepared-meat-cut", "qty": 2}, {"ingredientId": "potato", "qty": 1}, {"ingredientId": "carrot", "qty": 1}, {"ingredientId": "creeping-thyme", "qty": 1}]},
        "drovers-onion-crock": {"name": "Drover’s Onion Crock", "category": "food", "yieldQty": 1, "salePrice": 0.45, "active": True,
                                 "ingredients": [{"ingredientId": "onion", "qty": 3}, {"ingredientId": "wheat", "qty": 2}, {"ingredientId": "milk", "qty": 1}]},
        "frontier-sarsaparilla": {"name": "Frontier Sarsaparilla", "category": "drink", "yieldQty": 1, "salePrice": 0.45, "active": True,
                                   "ingredients": [{"ingredientId": "barley", "qty": 1}, {"ingredientId": "sugar", "qty": 1}, {"ingredientId": "water", "qty": 1}]},
        "pappys-cane-coffee": {"name": "Pappy’s Cane Coffee", "category": "drink", "yieldQty": 1, "salePrice": 0.45, "active": True,
                                "ingredients": [{"ingredientId": "coffee-beans", "qty": 2}, {"ingredientId": "sugar", "qty": 4}, {"ingredientId": "water", "qty": 1}]},
    },
    "inventory": {ing_id: {"qty": 0, "preferredVendorId": None} for ing_id in [
        "tea-leaf", "orange", "sugar", "water", "coca-leaf", "lime", "prepared-meat-cut", "beans", "pimenta",
        "tomato", "whisky", "barley", "cherry", "potato", "corn", "wheat", "onion", "milk", "carrot",
        "creeping-thyme", "coffee-beans", "sugarcane",
    ]},
    "plan": {"targets": {rid: {"enabled": r["active"], "qty": 100} for rid, r in {
        "sun-brewed-sweet-tea": {"active": True}, "blackwater-coca-tonic": {"active": False},
        "buck-country-chili": {"active": True}, "irishmans-dram": {"active": True},
        "blackwater-old-fashioned": {"active": True}, "brunswick-stew": {"active": True},
        "cattlemans-ruin": {"active": True}, "mamas-chicken-dumplings": {"active": True},
        "dirty-weenies": {"active": True}, "backcountry-cottontail-stew": {"active": True},
        "drovers-onion-crock": {"active": True}, "frontier-sarsaparilla": {"active": True},
        "pappys-cane-coffee": {"active": True},
    }.items()}},
    "settings": {
        "priceCap": 0.45, "thresholdHealthy": 0.20, "thresholdTight": 0.30,
        "meatIngredientId": "prepared-meat-cut", "meatMode": "override",
        "meatRawCost": 0, "meatProcessingFee": 0.03, "meatOverrideCost": 0.08,
        "laborRatePer30Min": 1.50, "processTimeMinutes": 3.0, "taxRatePercent": 0.0,
    },
}

# Settings keys that may be missing from a data file saved before a given
# feature existed (e.g. labor costing). load_data() backfills only the
# missing keys onto an existing file -- it never touches what's already there.
SETTINGS_DEFAULTS = SEED["settings"]


def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        changed = False
        for key, default in SETTINGS_DEFAULTS.items():
            if key not in data.setdefault("settings", {}):
                data["settings"][key] = default
                changed = True
        if changed:
            save_data(data)
        return data
    save_data(SEED)
    return json.loads(json.dumps(SEED))


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower().strip()).strip("-")
    return s or "item"


def unique_id(base, existing):
    if base not in existing:
        return base
    n = 2
    while f"{base}-{n}" in existing:
        n += 1
    return f"{base}-{n}"


def fmt_money(n):
    if n is None or (isinstance(n, float) and math.isnan(n)):
        return "—"
    return f"${n:.2f}"


def ing_name(data, ing_id):
    ing = data["ingredients"].get(ing_id)
    return ing["name"] if ing else ing_id


def cheapest_vendor(data, ing_id):
    pool = [v for v in data["vendors"] if v["ingredientId"] == ing_id and v.get("price") is not None]
    return min(pool, key=lambda v: v["price"]) if pool else None


def ing_cost(data, ing_id, visiting=None):
    visiting = visiting or frozenset()
    if ing_id in visiting:
        return {"cost": 0.0, "warn": True, "reason": "circular"}
    s = data["settings"]
    if ing_id == s.get("meatIngredientId"):
        if s.get("meatMode") == "override":
            return {"cost": s.get("meatOverrideCost") or 0.0, "warn": False, "reason": "override"}
        return {"cost": (s.get("meatRawCost") or 0.0) + (s.get("meatProcessingFee") or 0.0), "warn": False, "reason": "calculated"}
    conv = next((c for c in data["conversions"] if c["outputId"] == ing_id), None)
    if conv:
        sub = ing_cost(data, conv["inputId"], visiting | {ing_id})
        out_qty = conv.get("outputQty") or 1
        cost = (sub["cost"] * (conv.get("inputQty") or 1) + (conv.get("cost") or 0)) / out_qty
        return {"cost": cost, "warn": sub["warn"], "reason": "conversion", "via": conv["inputId"]}
    inv = data["inventory"].get(ing_id, {})
    vendor = None
    pref_id = inv.get("preferredVendorId")
    if pref_id:
        vendor = next((v for v in data["vendors"] if v["id"] == pref_id and v.get("price") is not None), None)
    if not vendor:
        vendor = cheapest_vendor(data, ing_id)
    if vendor:
        return {"cost": vendor["price"], "warn": False, "reason": "vendor", "vendorId": vendor["id"]}
    return {"cost": 0.0, "warn": True, "reason": "no-price"}


def labor_cost_per_craft(data):
    """Overhead cost of the time a single craft/batch-slot takes to process,
    using the shared Process Time x Labor Rate settings (same for every
    recipe -- see Settings)."""
    s = data["settings"]
    minutes = s.get("processTimeMinutes") or 0.0
    rate_per_30 = s.get("laborRatePer30Min") or 0.0
    return minutes * (rate_per_30 / 30.0)


def net_of_tax(data, amount):
    """What's actually kept from a sale after the (still-unconfirmed) tax rate."""
    rate = (data["settings"].get("taxRatePercent") or 0.0) / 100.0
    return amount * (1 - rate)


def recipe_craft_cost(data, recipe):
    total, warn, lines = 0.0, False, []
    for ri in recipe.get("ingredients", []):
        res = ing_cost(data, ri["ingredientId"])
        warn = warn or res["warn"]
        line_cost = res["cost"] * ri["qty"]
        total += line_cost
        lines.append({**ri, "unitCost": res["cost"], "lineCost": line_cost, "warn": res["warn"]})
    labor = labor_cost_per_craft(data)
    total += labor
    return {"total": total, "lines": lines, "warn": warn, "ingredientCost": total - labor, "laborCost": labor}


def recipe_metrics(data, recipe):
    craft = recipe_craft_cost(data, recipe)
    yield_qty = recipe["yieldQty"] if recipe.get("yieldQty", 0) > 0 else 1
    cost_per_item = craft["total"] / yield_qty
    sale = recipe.get("salePrice") or 0.0
    net_sale = net_of_tax(data, sale)
    profit = net_sale - cost_per_item
    margin = (profit / net_sale) if net_sale > 0 else None
    s = data["settings"]
    tier = "good"
    if cost_per_item > s["thresholdTight"]:
        tier = "bad"
    elif cost_per_item > s["thresholdHealthy"]:
        tier = "warn"
    return {"craft": craft, "costPerItem": cost_per_item, "profit": profit, "margin": margin,
            "tier": tier, "overCap": sale > s["priceCap"], "netSale": net_sale}


def compute_plan(data):
    rows, totals = [], {}
    for rid, r in data["recipes"].items():
        t = data["plan"]["targets"].get(rid)
        if not t or not t.get("enabled") or not (t.get("qty", 0) > 0):
            continue
        yield_qty = r["yieldQty"] if r.get("yieldQty", 0) > 0 else 1
        crafts = math.ceil(t["qty"] / yield_qty)
        craft = recipe_craft_cost(data, r)
        rows.append({"recipe": r, "recipeId": rid, "target": t["qty"], "crafts": crafts,
                     "craftCost": craft["total"], "runCost": crafts * craft["total"], "warn": craft["warn"]})
        for ri in r.get("ingredients", []):
            need = crafts * ri["qty"]
            bucket = totals.setdefault(ri["ingredientId"], {"required": 0, "recipeIds": set()})
            bucket["required"] += need
            bucket["recipeIds"].add(rid)
    shortages = []
    for ing_id, d in totals.items():
        on_hand = data["inventory"].get(ing_id, {}).get("qty", 0)
        shortage = max(0, d["required"] - on_hand)
        shortages.append({"id": ing_id, "required": d["required"], "onHand": on_hand,
                          "shortage": shortage, "numRecipes": len(d["recipeIds"]),
                          "score": shortage * len(d["recipeIds"])})
    shortages.sort(key=lambda x: -x["shortage"])
    grow_next = sorted([s for s in shortages if s["shortage"] > 0], key=lambda x: -x["score"])[:5]
    return {"rows": rows, "shortages": shortages, "growNext": grow_next}


def used_in_recipes(data, ing_id):
    return [r for r in data["recipes"].values() if any(ri["ingredientId"] == ing_id for ri in r.get("ingredients", []))]


def used_in_conversions(data, ing_id):
    return [c for c in data["conversions"] if c["inputId"] == ing_id or c["outputId"] == ing_id]


def resolve_purchase_steps(data, ing_id, qty):
    steps, visiting, cur_id, cur_qty = [], set(), ing_id, qty
    for _ in range(20):
        if cur_id in visiting:
            steps.append({"type": "circular", "ingredientId": cur_id, "qty": cur_qty})
            break
        visiting.add(cur_id)
        if cur_id == data["settings"].get("meatIngredientId"):
            steps.append({"type": "hunt", "ingredientId": cur_id, "qty": cur_qty})
            break
        conv = next((c for c in data["conversions"] if c["outputId"] == cur_id), None)
        if conv:
            input_qty_needed = math.ceil(cur_qty / (conv.get("outputQty") or 1)) * (conv.get("inputQty") or 1)
            steps.append({"type": "convert", "fromId": conv["inputId"], "fromQty": input_qty_needed,
                          "outputId": cur_id, "outputQty": cur_qty})
            cur_id, cur_qty = conv["inputId"], input_qty_needed
            continue
        inv = data["inventory"].get(cur_id, {})
        vendor = None
        pref_id = inv.get("preferredVendorId")
        if pref_id:
            vendor = next((v for v in data["vendors"] if v["id"] == pref_id and v.get("price") is not None), None)
        if not vendor:
            vendor = cheapest_vendor(data, cur_id)
        if vendor:
            steps.append({"type": "buy", "ingredientId": cur_id, "qty": cur_qty, "vendor": vendor})
        else:
            steps.append({"type": "no-source", "ingredientId": cur_id, "qty": cur_qty})
        break
    return steps


def apply_made(data, recipe_id, crafts):
    """Deduct ingredients for `crafts` batches of recipe_id from inventory, and
    reduce its remaining plan target by the items produced. Returns a list of
    human-readable ingredient shortfalls (inventory is clamped to 0, never negative)."""
    r = data["recipes"][recipe_id]
    yield_qty = r["yieldQty"] if r.get("yieldQty", 0) > 0 else 1
    shortfalls = []
    for li in r.get("ingredients", []):
        need = crafts * li["qty"]
        inv = data["inventory"].setdefault(li["ingredientId"], {"qty": 0, "preferredVendorId": None})
        have = inv.get("qty", 0) or 0
        if need > have:
            shortfalls.append(f"{ing_name(data, li['ingredientId'])} (had {have:g}, used {need:g})")
        inv["qty"] = max(0.0, have - need)
    t = data["plan"]["targets"].get(recipe_id, {"enabled": False, "qty": 0})
    t["qty"] = max(0.0, (t.get("qty", 0) or 0) - crafts * yield_qty)
    data["plan"]["targets"][recipe_id] = t
    return shortfalls


def order_line_text(data, top_id, shortage_qty):
    steps = resolve_purchase_steps(data, top_id, shortage_qty)
    last = steps[-1]
    if last["type"] == "hunt":
        main = "Go Hunting — Valentine for processing"
    elif last["type"] == "buy":
        v = last["vendor"]
        town = f" ({v['town']})" if v.get("town") else ""
        main = f"Buy {last['qty']:g} {ing_name(data, last['ingredientId'])} — {v['vendorName']}{town} @ {fmt_money(v['price'])}/ea = {fmt_money(v['price'] * last['qty'])}"
    elif last["type"] == "no-source":
        main = f"No price set for {ing_name(data, last['ingredientId'])} — add a vendor"
    else:
        main = f"Circular conversion on {ing_name(data, last['ingredientId'])}"
    if len(steps) > 1:
        via = ", ".join(f"{s['outputQty']:g} {ing_name(data, s['outputId'])} ← {s['fromQty']:g} {ing_name(data, s['fromId'])}" for s in steps[:-1])
        main += f"  (via {via})"
    return main

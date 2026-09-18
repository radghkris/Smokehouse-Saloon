import uuid

import pandas as pd
import streamlit as st

from ledger_engine import (
    load_data, save_data, slugify, unique_id, fmt_money, ing_name, cheapest_vendor,
    ing_cost, recipe_craft_cost, recipe_metrics, compute_plan, used_in_recipes,
    used_in_conversions, resolve_purchase_steps, order_line_text,
)

st.set_page_config(page_title="Blackwater Ledger", page_icon="\U0001F356", layout="wide")
st.title("\U0001F356 Blackwater Ledger")
st.caption("The Smokehouse at Blackwater Saloon — costing & production planner. Data saves to ledger_data.json next to this script.")

data = load_data()

tab_dash, tab_recipes, tab_ing, tab_vendors, tab_inv, tab_planner, tab_settings = st.tabs(
    ["Dashboard", "Recipes", "Ingredients", "Vendors", "Inventory", "Planner", "Settings"]
)

with tab_dash:
    recipes = list(data["recipes"].items())
    metrics = {rid: recipe_metrics(data, r) for rid, r in recipes}
    active_n = sum(1 for _, r in recipes if r["active"])
    over_cap = sum(1 for rid, _ in recipes if metrics[rid]["overCap"])
    problematic = sum(1 for rid, _ in recipes if metrics[rid]["tier"] == "bad")
    plan = compute_plan(data)
    short_lines = sum(1 for s in plan["shortages"] if s["shortage"] > 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Recipes", f"{active_n} / {len(recipes)}")
    c2.metric("Ingredients Short (planned run)", short_lines)
    c3.metric("Over Price Cap", over_cap)
    c4.metric("Problematic Cost Tier", problematic)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Acquire Next")
        st.caption("Top shortages, weighted by how many planned recipes need them.")
        if plan["growNext"]:
            df = pd.DataFrame([{
                "Ingredient": ing_name(data, g["id"]), "Shortage": g["shortage"],
                "Recipes Using": g["numRecipes"], "Score": g["score"],
            } for g in plan["growNext"]])
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info("No shortages against the current plan — you're stocked.")
    with col_b:
        st.subheader("Pricing Watch")
        s = data["settings"]
        # st.caption renders markdown, where a pair of literal "$" is read as LaTeX math — escape them.
        md_money = lambda n: fmt_money(n).replace("$", "\\$")
        st.caption(f"Cap: {md_money(s['priceCap'])} · Tight: over {md_money(s['thresholdHealthy'])} · Problematic: over {md_money(s['thresholdTight'])}")
        watch = [(rid, r) for rid, r in recipes if metrics[rid]["tier"] != "good" or metrics[rid]["overCap"]]
        if watch:
            df = pd.DataFrame([{
                "Recipe": r["name"], "Cost/Item": fmt_money(metrics[rid]["costPerItem"]),
                "Sale Price": fmt_money(r["salePrice"]),
                "Flag": ("OVER CAP, " if metrics[rid]["overCap"] else "") + ("problematic" if metrics[rid]["tier"] == "bad" else "tight"),
            } for rid, r in watch])
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.success("Every recipe is under the tight-cost threshold and within the price cap.")

with tab_recipes:
    st.subheader("Recipes")
    st.caption("Tick/untick Active below, then Save — that's what the Dashboard and Planner use by default.")
    recipe_ids_sorted = sorted(data["recipes"], key=lambda i: data["recipes"][i]["name"])
    rows = []
    for rid in recipe_ids_sorted:
        r = data["recipes"][rid]
        m = recipe_metrics(data, r)
        rows.append({
            "id": rid,
            "Name": r["name"] + (" ⚠️" if m["craft"]["warn"] else ""),
            "Category": r["category"], "Yield": r["yieldQty"],
            "Craft Cost": fmt_money(m["craft"]["total"]), "Cost/Item": fmt_money(m["costPerItem"]),
            "Sale Price": fmt_money(r["salePrice"]) + (" (over cap)" if m["overCap"] else ""),
            "Profit": fmt_money(m["profit"]),
            "Margin": "—" if m["margin"] is None else f"{m['margin']*100:.1f}%",
            "Tier": {"good": "healthy", "warn": "tight", "bad": "problematic"}[m["tier"]],
            "Active": r["active"],
        })
    recipes_df = pd.DataFrame(rows)
    edited_recipes = st.data_editor(
        recipes_df, hide_index=True, use_container_width=True, key="recipes_active_editor",
        disabled=[c for c in recipes_df.columns if c not in ("id", "Active")],
        column_config={"id": None},
    )
    if st.button("Save active flags"):
        for _, row in edited_recipes.iterrows():
            data["recipes"][row["id"]]["active"] = bool(row["Active"])
        save_data(data)
        st.success("Saved.")
        st.rerun()

    ing_ids_sorted = sorted(data["ingredients"], key=lambda i: data["ingredients"][i]["name"])
    ing_names_sorted = [data["ingredients"][i]["name"] for i in ing_ids_sorted]
    name_to_id = {data["ingredients"][i]["name"]: i for i in ing_ids_sorted}

    with st.expander("Add / edit a recipe"):
        mode = st.radio("Mode", ["Add new", "Edit existing"], horizontal=True, key="recipe_mode")
        editing_id = None
        if mode == "Edit existing" and data["recipes"]:
            editing_id = st.selectbox(
                "Recipe", options=sorted(data["recipes"], key=lambda i: data["recipes"][i]["name"]),
                format_func=lambda i: data["recipes"][i]["name"], key="recipe_edit_pick",
            )
        existing = data["recipes"].get(editing_id) if editing_id else None

        with st.form("recipe_form"):
            name = st.text_input("Name", value=existing["name"] if existing else "")
            c1, c2, c3 = st.columns(3)
            category = c1.selectbox("Category", ["food", "drink"], index=0 if not existing or existing["category"] == "food" else 1)
            yield_qty = c2.number_input("Yield per craft", min_value=1, step=1, value=int(existing["yieldQty"]) if existing else 1)
            sale_price = c3.number_input("Sale price", min_value=0.0, step=0.01, format="%.2f",
                                          value=float(existing["salePrice"]) if existing else float(data["settings"]["priceCap"]))
            active = st.checkbox("Active (included in planner by default)", value=existing["active"] if existing else True)

            if existing and existing["ingredients"]:
                rows_df = pd.DataFrame([{"Ingredient": ing_name(data, l["ingredientId"]), "Qty": l["qty"]} for l in existing["ingredients"]])
            else:
                rows_df = pd.DataFrame([{"Ingredient": ing_names_sorted[0] if ing_names_sorted else "", "Qty": 1.0}])
            edited = st.data_editor(
                rows_df, num_rows="dynamic", use_container_width=True, key="recipe_ing_editor",
                column_config={
                    "Ingredient": st.column_config.SelectboxColumn(options=ing_names_sorted, required=True),
                    "Qty": st.column_config.NumberColumn(min_value=0.0, step=1.0, required=True),
                },
            )
            submitted = st.form_submit_button("Save recipe")
            if submitted:
                if not name.strip():
                    st.error("Name is required.")
                else:
                    lines = []
                    for _, row in edited.iterrows():
                        ing_id = name_to_id.get(row["Ingredient"])
                        qty = row["Qty"]
                        if ing_id and qty and qty > 0:
                            lines.append({"ingredientId": ing_id, "qty": float(qty)})
                    if not lines:
                        st.error("Add at least one ingredient.")
                    else:
                        payload = {"name": name.strip(), "category": category, "yieldQty": int(yield_qty),
                                   "salePrice": float(sale_price), "active": active, "ingredients": lines}
                        if existing:
                            data["recipes"][editing_id] = payload
                        else:
                            new_id = unique_id(slugify(name), set(data["recipes"]))
                            data["recipes"][new_id] = payload
                            data["plan"]["targets"][new_id] = {"enabled": active, "qty": 100}
                        save_data(data)
                        st.success("Saved.")
                        st.rerun()

    with st.expander("Delete a recipe"):
        if data["recipes"]:
            del_id = st.selectbox("Recipe to delete", options=sorted(data["recipes"], key=lambda i: data["recipes"][i]["name"]),
                                   format_func=lambda i: data["recipes"][i]["name"], key="recipe_del_pick")
            if st.button("Delete recipe", type="primary"):
                del data["recipes"][del_id]
                save_data(data)
                st.success("Deleted.")
                st.rerun()

with tab_ing:
    st.subheader("Ingredients")
    ing_rows = []
    for iid in sorted(data["ingredients"], key=lambda i: data["ingredients"][i]["name"]):
        ing = data["ingredients"][iid]
        res = ing_cost(data, iid)
        reason_map = {"conversion": "via conversion", "vendor": "vendor", "override": "meat override",
                      "calculated": "meat calc.", "no-price": "no data", "circular": "circular!"}
        ing_rows.append({"Name": ing["name"], "Unit": ing["unit"],
                          "Resolved Cost": "NO PRICE" if res["warn"] else fmt_money(res["cost"]),
                          "Source": reason_map.get(res["reason"], res["reason"])})
    st.dataframe(pd.DataFrame(ing_rows), hide_index=True, use_container_width=True)

    st.subheader("Conversions")
    st.caption("Turns a raw input into finished units of another ingredient — e.g. Sugarcane into Sugar — with an optional processing cost added before dividing across the output.")
    conv_rows = [{"Conversion": f"{c['inputQty']:g}× {ing_name(data, c['inputId'])} → {c['outputQty']:g}× {ing_name(data, c['outputId'])}",
                  "Processing Cost": fmt_money(c.get("cost") or 0)} for c in data["conversions"]]
    st.dataframe(pd.DataFrame(conv_rows), hide_index=True, use_container_width=True) if conv_rows else st.info("No conversions yet.")

    ing_ids_sorted = sorted(data["ingredients"], key=lambda i: data["ingredients"][i]["name"])
    ing_names_sorted = [data["ingredients"][i]["name"] for i in ing_ids_sorted]
    name_to_id = {data["ingredients"][i]["name"]: i for i in ing_ids_sorted}

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("Add an ingredient"):
            with st.form("ing_form"):
                new_name = st.text_input("Name")
                new_unit = st.text_input("Unit", value="ea")
                if st.form_submit_button("Add ingredient"):
                    if not new_name.strip():
                        st.error("Name is required.")
                    else:
                        new_id = unique_id(slugify(new_name), set(data["ingredients"]))
                        data["ingredients"][new_id] = {"name": new_name.strip(), "unit": new_unit.strip() or "ea"}
                        data["inventory"][new_id] = {"qty": 0, "preferredVendorId": None}
                        save_data(data)
                        st.success("Added.")
                        st.rerun()
        with st.expander("Delete an ingredient"):
            if ing_ids_sorted:
                del_iid = st.selectbox("Ingredient", options=ing_ids_sorted, format_func=lambda i: data["ingredients"][i]["name"], key="ing_del_pick")
                if st.button("Delete ingredient", type="primary"):
                    blockers = used_in_recipes(data, del_iid) + used_in_conversions(data, del_iid)
                    if blockers:
                        st.error(f"Can't delete — still used by {len(blockers)} recipe(s)/conversion(s). Remove those references first.")
                    else:
                        data["vendors"] = [v for v in data["vendors"] if v["ingredientId"] != del_iid]
                        data["inventory"].pop(del_iid, None)
                        del data["ingredients"][del_iid]
                        save_data(data)
                        st.success("Deleted.")
                        st.rerun()
    with col2:
        with st.expander("Add a conversion"):
            with st.form("conv_form"):
                in_name = st.selectbox("Input", options=ing_names_sorted, key="conv_in")
                in_qty = st.number_input("Input Qty", min_value=0.0, step=1.0, value=1.0, key="conv_in_qty")
                out_name = st.selectbox("Output", options=ing_names_sorted, key="conv_out")
                out_qty = st.number_input("Output Qty", min_value=0.0, step=1.0, value=1.0, key="conv_out_qty")
                cost = st.number_input("Processing Cost (total, optional)", min_value=0.0, step=0.01, value=0.0, key="conv_cost")
                if st.form_submit_button("Add conversion"):
                    in_id, out_id = name_to_id[in_name], name_to_id[out_name]
                    if in_id == out_id:
                        st.error("Input and output must be different ingredients.")
                    elif not in_qty or not out_qty:
                        st.error("Quantities must be greater than zero.")
                    else:
                        new_cid = "conv-" + uuid.uuid4().hex[:10]
                        data["conversions"].append({"id": new_cid, "inputId": in_id, "inputQty": in_qty,
                                                     "outputId": out_id, "outputQty": out_qty, "cost": cost})
                        save_data(data)
                        st.success("Added.")
                        st.rerun()
        with st.expander("Delete a conversion"):
            if data["conversions"]:
                labels = {c["id"]: f"{c['inputQty']:g}× {ing_name(data, c['inputId'])} → {c['outputQty']:g}× {ing_name(data, c['outputId'])}" for c in data["conversions"]}
                del_cid = st.selectbox("Conversion", options=list(labels), format_func=lambda i: labels[i], key="conv_del_pick")
                if st.button("Delete conversion", type="primary"):
                    data["conversions"] = [c for c in data["conversions"] if c["id"] != del_cid]
                    save_data(data)
                    st.success("Deleted.")
                    st.rerun()

with tab_vendors:
    st.subheader("Vendors")
    st.caption("Cheapest known price is marked automatically. Set a preferred supplier per ingredient on the Inventory tab — it won't be overwritten even if a cheaper one shows up.")
    v_rows = []
    for iid in sorted(data["ingredients"], key=lambda i: data["ingredients"][i]["name"]):
        cheap = cheapest_vendor(data, iid)
        for v in sorted([v for v in data["vendors"] if v["ingredientId"] == iid], key=lambda v: (v["price"] is None, v.get("price") or 0)):
            v_rows.append({
                "Ingredient": data["ingredients"][iid]["name"], "Vendor": v["vendorName"], "Town": v.get("town") or "—",
                "Price": "TBD" if v.get("price") is None else fmt_money(v["price"]) + (" ★ cheapest" if cheap and v["id"] == cheap["id"] else ""),
                "Stock": v.get("stock", "unknown"), "Note": v.get("note", ""),
            })
    st.dataframe(pd.DataFrame(v_rows), hide_index=True, use_container_width=True)

    ing_ids_sorted = sorted(data["ingredients"], key=lambda i: data["ingredients"][i]["name"])
    ing_names_sorted = [data["ingredients"][i]["name"] for i in ing_ids_sorted]
    name_to_id = {data["ingredients"][i]["name"]: i for i in ing_ids_sorted}

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("Add a vendor price"):
            with st.form("vendor_form"):
                v_ing = st.selectbox("Ingredient", options=ing_names_sorted, key="v_ing")
                v_name = st.text_input("Vendor Name", placeholder="Armadillo Market")
                v_town = st.text_input("Town", placeholder="Armadillo")
                v_price_raw = st.text_input("Price (blank = TBD)", placeholder="0.10")
                v_stock = st.selectbox("Stock", ["unknown", "available", "out"])
                if st.form_submit_button("Add vendor price"):
                    if not v_name.strip():
                        st.error("Vendor name is required.")
                    else:
                        try:
                            price = None if not v_price_raw.strip() else max(0.0, float(v_price_raw))
                        except ValueError:
                            price = None
                        new_vid = "v-" + uuid.uuid4().hex[:10]
                        data["vendors"].append({"id": new_vid, "ingredientId": name_to_id[v_ing], "vendorName": v_name.strip(),
                                                 "town": v_town.strip(), "price": price, "stock": v_stock})
                        save_data(data)
                        st.success("Added.")
                        st.rerun()
    with col2:
        with st.expander("Delete a vendor price"):
            if data["vendors"]:
                labels = {v["id"]: f"{ing_name(data, v['ingredientId'])} — {v['vendorName']} ({v.get('town') or 'n/a'})" for v in data["vendors"]}
                del_vid = st.selectbox("Vendor row", options=list(labels), format_func=lambda i: labels[i], key="vendor_del_pick")
                if st.button("Delete vendor price", type="primary"):
                    data["vendors"] = [v for v in data["vendors"] if v["id"] != del_vid]
                    for inv in data["inventory"].values():
                        if inv.get("preferredVendorId") == del_vid:
                            inv["preferredVendorId"] = None
                    save_data(data)
                    st.success("Deleted.")
                    st.rerun()

with tab_inv:
    st.subheader("Inventory")
    st.caption("Enter what you actually have on hand, then click Save.")
    inv_ids = sorted(data["ingredients"], key=lambda i: data["ingredients"][i]["name"])
    inv_df = pd.DataFrame([{
        "id": iid, "Ingredient": data["ingredients"][iid]["name"], "Unit": data["ingredients"][iid]["unit"],
        "On Hand": data["inventory"].get(iid, {}).get("qty", 0),
    } for iid in inv_ids])
    edited_inv = st.data_editor(
        inv_df, hide_index=True, use_container_width=True, disabled=["id", "Ingredient", "Unit"], key="inv_editor",
        column_config={"id": None, "On Hand": st.column_config.NumberColumn(min_value=0.0, step=1.0)},
    )
    if st.button("Save inventory quantities"):
        for _, row in edited_inv.iterrows():
            data["inventory"].setdefault(row["id"], {"preferredVendorId": None})["qty"] = float(row["On Hand"])
        save_data(data)
        st.success("Saved.")
        st.rerun()

    total_value = sum((data["inventory"].get(iid, {}).get("qty", 0) or 0) * ing_cost(data, iid)["cost"] for iid in inv_ids)
    st.metric("Total inventory value", fmt_money(total_value))

    with st.expander("Preferred suppliers (optional — overrides cheapest-wins)"):
        for iid in inv_ids:
            vendors_here = [v for v in data["vendors"] if v["ingredientId"] == iid]
            if not vendors_here:
                continue
            options = [""] + [v["id"] for v in vendors_here]
            labels = {"": "cheapest available"}
            labels.update({v["id"]: f"{v['vendorName']}" + (f" ({fmt_money(v['price'])})" if v.get("price") is not None else " (TBD)") for v in vendors_here})
            current = data["inventory"].get(iid, {}).get("preferredVendorId") or ""
            choice = st.selectbox(data["ingredients"][iid]["name"], options=options, index=options.index(current) if current in options else 0,
                                   format_func=lambda i: labels[i], key=f"pref_{iid}")
            if choice != current:
                data["inventory"].setdefault(iid, {"qty": 0})["preferredVendorId"] = choice or None
                save_data(data)
                st.rerun()

with tab_planner:
    st.subheader("Production Planner")
    st.caption("Check the recipes you're running and set how many of each you want, then What To Order fills in below.")

    bcol1, bcol2 = st.columns([1, 2])
    bulk_qty = bcol1.number_input("Set target for every enabled recipe", min_value=0, step=1, value=100, key="bulk_qty")
    if bcol2.button("Apply to enabled recipes", key="bulk_apply"):
        for rid, t in data["plan"]["targets"].items():
            if t.get("enabled"):
                t["qty"] = int(bulk_qty)
        save_data(data)
        st.rerun()

    plan_ids = sorted(data["recipes"], key=lambda i: data["recipes"][i]["name"])
    plan_df = pd.DataFrame([{
        "id": rid, "Recipe": data["recipes"][rid]["name"],
        "Enabled": data["plan"]["targets"].get(rid, {}).get("enabled", False),
        "Target Qty": data["plan"]["targets"].get(rid, {}).get("qty", 0),
    } for rid in plan_ids])
    edited_plan = st.data_editor(
        plan_df, hide_index=True, use_container_width=True, disabled=["id", "Recipe"], key="plan_editor",
        column_config={"id": None, "Target Qty": st.column_config.NumberColumn(min_value=0, step=1)},
    )
    if st.button("Save plan"):
        for _, row in edited_plan.iterrows():
            data["plan"]["targets"][row["id"]] = {"enabled": bool(row["Enabled"]), "qty": float(row["Target Qty"])}
        save_data(data)
        st.success("Saved.")
        st.rerun()

    plan = compute_plan(data)
    if plan["rows"]:
        run_df = pd.DataFrame([{
            "Recipe": row["recipe"]["name"], "Crafts Needed": row["crafts"], "Run Cost": fmt_money(row["runCost"]),
        } for row in plan["rows"]])
        st.dataframe(run_df, hide_index=True, use_container_width=True)

    st.subheader("What To Order")
    shortages = [s for s in plan["shortages"] if s["shortage"] > 0]
    order_total = 0.0
    for s in shortages:
        last = resolve_purchase_steps(data, s["id"], s["shortage"])[-1]
        if last["type"] == "buy":
            order_total += last["vendor"]["price"] * last["qty"]
    st.caption(f"Estimated spend: {fmt_money(order_total)}. Conversions (like Sugarcane → Sugar) are already worked out for you.")
    if shortages:
        order_df = pd.DataFrame([{
            "Ingredient": ing_name(data, s["id"]), "Short": s["shortage"],
            "Do This": order_line_text(data, s["id"], s["shortage"]),
        } for s in shortages])
        st.dataframe(order_df, hide_index=True, use_container_width=True)
    else:
        st.success("Nothing to order — you're covered for everything checked above.")

    with st.expander("Ingredient detail (required vs. on-hand, before conversions)"):
        detail_df = pd.DataFrame([{
            "Ingredient": ing_name(data, s["id"]), "Required": s["required"], "On Hand": s["onHand"],
            "Still Needed": s["shortage"],
        } for s in plan["shortages"]])
        if not detail_df.empty:
            st.dataframe(detail_df, hide_index=True, use_container_width=True)
        else:
            st.info("Enable at least one recipe above to see requirements.")

with tab_settings:
    st.subheader("Pricing Rules")
    with st.form("settings_pricing"):
        s = data["settings"]
        cap = st.number_input("Server Price Cap", min_value=0.0, step=0.01, value=float(s["priceCap"]), format="%.2f")
        healthy = st.number_input("Healthy Threshold (cost below)", min_value=0.0, step=0.01, value=float(s["thresholdHealthy"]), format="%.2f")
        tight = st.number_input("Problematic Threshold (cost above)", min_value=0.0, step=0.01, value=float(s["thresholdTight"]), format="%.2f")
        if st.form_submit_button("Save pricing rules"):
            s["priceCap"], s["thresholdHealthy"], s["thresholdTight"] = cap, healthy, tight
            save_data(data)
            st.success("Saved.")
            st.rerun()

    st.subheader("Meat Processing")
    st.caption("Prepared Meat Cut is priced specially instead of through the vendor list. Choose calculated (raw cost + butcher fee) or a flat manual override.")
    with st.form("settings_meat"):
        s = data["settings"]
        mode = st.radio("Meat mode", ["override", "calculated"], index=0 if s["meatMode"] == "override" else 1,
                         format_func=lambda m: "Manual override" if m == "override" else "Calculated (raw + processing fee)")
        c1, c2, c3 = st.columns(3)
        raw_cost = c1.number_input("Raw meat cost / unit", min_value=0.0, step=0.01, value=float(s["meatRawCost"]), format="%.2f")
        fee = c2.number_input("Processing fee / unit", min_value=0.0, step=0.01, value=float(s["meatProcessingFee"]), format="%.2f")
        override_cost = c3.number_input("Override cost / unit", min_value=0.0, step=0.01, value=float(s["meatOverrideCost"]), format="%.2f")
        if st.form_submit_button("Save meat settings"):
            s["meatMode"], s["meatRawCost"], s["meatProcessingFee"], s["meatOverrideCost"] = mode, raw_cost, fee, override_cost
            save_data(data)
            st.success("Saved.")
            st.rerun()
    st.caption("Special first batch (594 cuts for a flat $10 processing fee) was a one-off and isn't used as the ongoing basis — set your normal-arrangement numbers above.")

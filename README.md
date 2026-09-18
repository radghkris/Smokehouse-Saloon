# Blackwater Ledger (Python)

Recipe costing and production planner for the Smokehouse at Blackwater Saloon. A Streamlit port of the browser version, for running locally.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

This opens the app in your browser at `http://localhost:8501`.

## Data

Everything you enter (recipes, vendors, inventory, settings) is saved to `ledger_data.json`, created next to `app.py` the first time you run it. That file is your data — back it up or copy it between machines as needed; it's excluded from this repo (`.gitignore`) so nobody's local edits overwrite anyone else's.

## What it does

- **Dashboard** — shortages weighted by how many active recipes need them ("Grow Next"), and recipes flagged as tight/problematic cost or over the server's price cap.
- **Recipes** — ingredients, craft yield, sale price; cost, profit and margin computed automatically.
- **Ingredients & Conversions** — unit costs, plus raw-to-finished conversions (e.g. Sugarcane → Sugar) that resolve automatically through the cost engine.
- **Vendors** — multiple vendor prices per ingredient across towns; cheapest is flagged automatically.
- **Inventory** — quantities on hand, and an optional preferred supplier per ingredient.
- **Planner** — set target quantities per recipe, then **What To Order** tells you exactly what to buy (and from where) or that it's time to go hunting, walking through any conversions along the way.
- **Settings** — price cap, cost-tier thresholds, and Prepared Meat Cut pricing (calculated vs. flat override).

There's also a browser-hosted version of this tool at the Claude artifact link, which stays live and synced without needing Python installed.

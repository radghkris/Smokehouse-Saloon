# Blackwater Ledger (Python)

Recipe costing and production planner for the Smokehouse at Blackwater Saloon. Two local Python versions, sharing the same logic (`ledger_engine.py`) and the same data file:

- **`desktop_app.py`** — a standalone desktop window (Tkinter). No browser, no extra installs — just Python itself.
- **`app.py`** — a Streamlit version that runs in your browser at `http://localhost:8501`, if you'd rather have that.

## Run the desktop app (recommended if you don't want a browser tab)

Double-click **`run_desktop.bat`**, or from a terminal:

```bash
python desktop_app.py
```

That's it — no `pip install` needed, since it only uses what Python already includes.

## Run the browser (Streamlit) version instead

Double-click **`run.bat`** (sets itself up automatically), or from a terminal:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data

Everything you enter (recipes, vendors, inventory, settings) is saved to `ledger_data.json`, created next to the scripts the first time you run either version — both read and write the same file, so you can switch between them freely. That file is your data — back it up or copy it between machines as needed; it's excluded from this repo (`.gitignore`) so nobody's local edits overwrite anyone else's.

## What it does

- **Dashboard** — shortages weighted by how many active recipes need them ("Grow Next"), and recipes flagged as tight/problematic cost or over the server's price cap.
- **Recipes** — ingredients, craft yield, sale price; cost, profit and margin computed automatically. Toggle a recipe active/inactive right from the list.
- **Ingredients & Conversions** — unit costs, plus raw-to-finished conversions (e.g. Sugarcane → Sugar) that resolve automatically through the cost engine.
- **Vendors** — multiple vendor prices per ingredient across towns; cheapest is flagged automatically.
- **Inventory** — quantities on hand, and an optional preferred supplier per ingredient.
- **Planner** — set target quantities per recipe, then **What To Order** tells you exactly what to buy (and from where) or that it's time to go hunting, walking through any conversions along the way.
- **Settings** — price cap, cost-tier thresholds, and Prepared Meat Cut pricing (calculated vs. flat override).

There's also a browser-hosted version of this tool at the Claude artifact link, which stays live and synced without needing Python installed at all.

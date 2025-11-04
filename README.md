# India Trade Analysis — Flask delivery

This project serves the analytics from your earlier assignment via a Flask app backed by an SQLite DB (SQLAlchemy ORM).  
Use the included installation script to set up a Python virtual environment, install dependencies and populate the DB.

---

## Prerequisites (Windows)
- Python 3.8+ installed and on PATH
- Git (optional)
- A working internet connection to pip-install packages

---

## Quick install (one-time)

Open PowerShell in the project root (`c:\Users\Arghyadeep Dhar\OneDrive\Desktop\Assignmrnt8`) and run:

1. Create & activate venv and install requirements (script provided)
   - Run the setup script:
     powershell -ExecutionPolicy Bypass -File .\scripts\setup_env.ps1

   The script will:
   - create `venv`
   - activate it
   - pip install from `requirements.txt`
   - attempt to populate the DB by running `database_setup.py` (or `scripts/repopulate.py` if present)

If you prefer manual steps:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# populate DB (one of these depending which exists)
python database_setup.py
# or
python .\scripts\repopulate.py
```

---

## Run the app

With the venv activated:

```powershell
python app.py
```

Open a browser and visit http://127.0.0.1:5000

---

## Important files / folders
- `app.py` — Flask application routes and logic
- `models.py` — SQLAlchemy ORM models (imports / exports tables)
- `database_setup.py` or `scripts/repopulate.py` — populates SQLite DB from source files
- `instance/trade_data.db` — SQLite DB (created by populate script)
- `templates/` — Jinja2 templates (one per question)
- `static/charts/` — generated charts (PNG)
- `scripts/setup_env.ps1` — installation helper script
- `requirements.txt` — Python dependencies

---

## URLs to try and expected outcome

- `/`  
  - Home page / index. Links to each question (a)–(g).

- `/top_countries` (a)  
  - Shows Top 5 import destinations table and Top 5 export destinations table (or dedicated UI).

- `/top_commodities` (b)  
  - Shows Top 5 import and export commodities tables.

- `/trade_summary` (c)  
  - Single combined table for every country with columns:
    - Country, Imports, Exports, Export/Import Ratio, Trade Deficit  
  - This is the combined pd.concat output (no plot on this page).

- `/export_over_10000` (d)  
  - Countries with Exports > 10,000 Cr (uses `DataFrame.query()`).
  - Shows a formatted table (Exports, Imports, Ratio, Deficit). CSV download button available.

- `/export_over_10000/download` (download endpoint)  
  - Downloads the saved filtered table as CSV (`export_over_10000` DB table).

- `/saved_table` (e)  
  - Shows the saved/renamed table (if created) with columns `Country`, `Exports`, `Imports`.

- `/top_transactions` (f)  
  - Uses the saved table from (e) (if present) and `melt()`s into:
    - Country | Transaction | Value  
  - Shows the top 10 transactions (mix of Imports & Exports), sorted by Value.

- `/common_commodities` (g)  
  - Table of commodities that appear in both imports and exports (commodity intersection).

- `/_health`  
  - A small JSON response indicating DB connection and list of DB tables present (useful for quick checks).

---

## Notes & troubleshooting

- If pages look stale after edits, hard-refresh the browser (Ctrl+F5) to clear cached templates/CSS.
- If tables are empty, ensure the DB was populated successfully:
  - Check `instance/trade_data.db` exists
  - Run `python database_setup.py` (or the repopulate script) and watch console output for errors
- Charts are generated with matplotlib's non-interactive backend (`Agg`) so running on a server should not require an X display.

---

## Dependencies (included in repository)

See `requirements.txt`. Example minimal content:

- Flask
- pandas
- SQLAlchemy
- matplotlib
- openpyxl (if Excel -> DB population script reads .xlsx)

---

## Support

If any route returns HTTP 500, paste the terminal traceback here and I will patch the route or DB population step.

from models import db, ImportRecord, ExportRecord
import pandas as pd
import os


def populate_db(app, drop_first=False):
    """Create tables and populate the database from the Excel data files.

    - app: Flask app instance
    - drop_first: if True, drops all tables before creating (use with caution)
    """
    imports_path = os.path.join('data', 'India_Imports_2011-12_And_2012-13_aa605ad1f304803ce7963a2828dbd232.xlsx')
    exports_path = os.path.join('data', 'India_Exports_2011-12_And_2012-13_c6b919acfdfdeeb51af0f4db0dfe84cb.xlsx')

    with app.app_context():
        if drop_first:
            db.drop_all()
        db.create_all()

        # If there's already data, skip population
        if ImportRecord.query.first() is not None or ExportRecord.query.first() is not None:
            print('Database already populated; skipping population step.')
            return

        # Ensure files exist before trying to read
        if not os.path.exists(imports_path) or not os.path.exists(exports_path):
            raise FileNotFoundError(f"Expected data files not found: {imports_path} or {exports_path}")

        imports = pd.read_excel(imports_path, sheet_name='im0313gc')
        exports = pd.read_excel(exports_path, sheet_name='Country-wise India Exports')

        # Normalize column names
        imports.columns = imports.columns.str.strip().str.replace('\n', ' ')
        exports.columns = exports.columns.str.strip().str.replace('\n', ' ')

        # Find the 2011-12 value columns (best-effort)
        import_col_candidates = [c for c in imports.columns if '2011' in str(c) and 'Value' in str(c)]
        export_col_candidates = [c for c in exports.columns if '2011' in str(c) and 'Value' in str(c)]

        if not import_col_candidates or not export_col_candidates:
            raise RuntimeError('Could not find the 2011 value columns in the provided excel files.')

        import_col = import_col_candidates[0]
        export_col = export_col_candidates[0]

        # Try to detect commodity-like columns (case-insensitive substring match)
        def find_commodity_col(df):
            candidates = [c for c in df.columns if 'commodity' in str(c).lower() or 'commod' in str(c).lower()]
            return candidates[0] if candidates else None

        import_commodity_col = find_commodity_col(imports)
        export_commodity_col = find_commodity_col(exports)

        for _, row in imports.iterrows():
            try:
                val = float(row.get(import_col, 0) or 0)
            except Exception:
                val = 0.0
            commodity_val = None
            if import_commodity_col:
                commodity_val = row.get(import_commodity_col)
            db.session.add(ImportRecord(country=row.get('Country'), commodity=commodity_val, year='2011-12', value=val))

        for _, row in exports.iterrows():
            try:
                val = float(row.get(export_col, 0) or 0)
            except Exception:
                val = 0.0
            commodity_val = None
            if export_commodity_col:
                commodity_val = row.get(export_commodity_col)
            db.session.add(ExportRecord(country=row.get('Country'), commodity=commodity_val, year='2011-12', value=val))

        db.session.commit()
        print("Database populated successfully!")

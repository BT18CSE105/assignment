from flask import Flask, render_template, jsonify, Response
from models import db, ImportRecord, ExportRecord
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, inspect
import numpy as np
import os

app = Flask(__name__)
os.makedirs(app.instance_path, exist_ok=True)
db_path = os.path.join(app.instance_path, 'trade_data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
db.init_app(app)

engine = create_engine(f"sqlite:///{db_path}")

try:
    from database_setup import populate_db
    try:
        populate_db(app)
    except FileNotFoundError as e:
        print(f"populate_db skipped: {e}")
    except Exception as e:
        print(f"populate_db error: {e}")
except Exception:
    pass
os.makedirs('static/charts', exist_ok=True)


@app.route('/')
def home():
    return render_template('index.html')


# (a) Top 5 import/export destinations
@app.route('/top_countries')
def top_countries():
    imports_df = pd.read_sql("SELECT * FROM imports", engine)
    exports_df = pd.read_sql("SELECT * FROM exports", engine)

    top_imports = imports_df.groupby('country')['value'].sum().sort_values(ascending=False).head(5)
    top_exports = exports_df.groupby('country')['value'].sum().sort_values(ascending=False).head(5)

    top_imports_df = top_imports.reset_index().rename(columns={'value': 'Imports', 'country': 'Country'})
    top_exports_df = top_exports.reset_index().rename(columns={'value': 'Exports', 'country': 'Country'})

    plt.figure(figsize=(8, 4))
    top_imports.plot(kind='bar', color='tab:red')
    plt.title('Top 5 Import Destinations (2011–12)')
    plt.tight_layout()
    plt.savefig('static/charts/top_imports.png')
    plt.close()

    plt.figure(figsize=(8, 4))
    top_exports.plot(kind='bar', color='tab:green')
    plt.title('Top 5 Export Destinations (2011–12)')
    plt.tight_layout()
    plt.savefig('static/charts/top_exports.png')
    plt.close()

    return render_template(
        'top_countries.html',
        title="(a) Top 5 Import & Export Destinations",
        table=top_imports_df.to_html(classes='table table-striped', index=False, justify='center'),
        table2=top_exports_df.to_html(classes='table table-striped', index=False, justify='center'),
        image='charts/top_imports.png',
        image2='charts/top_exports.png'
    )


# (b) Top 5 import/export commodities
@app.route('/top_commodities')
def top_commodities():
    imports_df = pd.read_sql("SELECT * FROM imports", engine)
    exports_df = pd.read_sql("SELECT * FROM exports", engine)

    if 'commodity' not in imports_df.columns or 'commodity' not in exports_df.columns:
        return render_template('error.html', message="Commodity column missing in data!")

    top_imports = imports_df.groupby('commodity')['value'].sum().sort_values(ascending=False).head(10)
    top_exports = exports_df.groupby('commodity')['value'].sum().sort_values(ascending=False).head(10)

    top_imports_df = top_imports.reset_index().rename(columns={'commodity': 'Commodity', 'value': 'Imports'})
    top_exports_df = top_exports.reset_index().rename(columns={'commodity': 'Commodity', 'value': 'Exports'})

    plt.figure(figsize=(8, 4))
    top_imports.plot(kind='bar', color='orange')
    plt.title('Top Import Commodities (2011-12)')
    plt.tight_layout()
    plt.savefig('static/charts/top_import_commodities.png')
    plt.close()

    plt.figure(figsize=(8, 4))
    top_exports.plot(kind='bar', color='blue')
    plt.title('Top Export Commodities (2011-12)')
    plt.tight_layout()
    plt.savefig('static/charts/top_export_commodities.png')
    plt.close()

    return render_template(
        'top_commodities.html',
        title="(b) Top 5 Import & Export Commodities",
        table=top_imports_df.to_html(classes='table table-striped', index=False, justify='center'),
        table2=top_exports_df.to_html(classes='table table-striped', index=False, justify='center'),
        image='charts/top_import_commodities.png',
        image2='charts/top_export_commodities.png'
    )


# (c) Trade summary
@app.route('/trade_summary')
def trade_summary():
    imports_series = pd.read_sql("SELECT country, value FROM imports", engine).groupby('country')['value'].sum()
    exports_series = pd.read_sql("SELECT country, value FROM exports", engine).groupby('country')['value'].sum()

    combined = pd.concat([imports_series, exports_series], axis=1)
    combined.columns = ['Imports', 'Exports']
    combined = combined.fillna(0)
    combined['Export/Import Ratio'] = (combined['Exports'] / combined['Imports']).replace([float('inf'), -float('inf')], 0)
    combined['Trade Deficit'] = combined['Exports'] - combined['Imports']

    combined_df = combined.reset_index().rename(columns={'country': 'Country'})

    return render_template(
        'trade_summary.html',
        title="(c) Trade Summary Table",
        table_html=combined_df.to_html(classes='table table-striped table-bordered', index=False, justify='center')
    )


# (d) Countries with Exports > 10,000 Cr
@app.route('/export_over_10000')
def export_over_10000():
    import numpy as np

    # Aggregate exports and imports
    exports_df = pd.read_sql("SELECT country, value FROM exports", engine).groupby('country', as_index=False)['value'].sum()
    imports_df = pd.read_sql("SELECT country, value FROM imports", engine).groupby('country', as_index=False)['value'].sum()

    # Threshold = 10,000 crore = 1e12 rupees
    threshold = 1e12
    high_exports = exports_df.query('value > @threshold').rename(columns={'country': 'Country', 'value': 'Exports'})

    # Merge imports for reference
    imports_df = imports_df.rename(columns={'country': 'Country', 'value': 'Imports'})
    result = pd.merge(high_exports, imports_df, on='Country', how='left').fillna(0)

    result.to_sql('export_over_10000', engine, if_exists='replace', index=False)

    display = result.copy()
    display['Exports (₹ Cr)'] = (display['Exports'] / 1e7).round(2)
    display['Imports (₹ Cr)'] = (display['Imports'] / 1e7).round(2)
    display['Export/Import Ratio'] = np.where(display['Imports'] == 0, 0, (display['Exports'] / display['Imports']).round(2))
    display['Trade Surplus/Deficit (₹ Cr)'] = ((display['Exports'] - display['Imports']) / 1e7).round(2)

    display = display[['Country', 'Exports (₹ Cr)', 'Imports (₹ Cr)', 'Export/Import Ratio', 'Trade Surplus/Deficit (₹ Cr)']]

    image = None
    if not display.empty:
        plt.figure(figsize=(8, 4))
        display.set_index('Country')['Exports (₹ Cr)'].plot(kind='bar', color='tab:purple')
        plt.title('Countries with Exports > 10,000 Cr (in ₹ Crore)')
        plt.ylabel('Exports (₹ Cr)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('static/charts/exports_over_10000.png')
        plt.close()
        image = 'charts/exports_over_10000.png'

    return render_template(
        'export_over_10000.html',
        title="(d) Countries with Exports > 10,000 Cr",
        table=display.to_html(classes='table table-striped', index=False, justify='center', float_format='{:,.2f}'.format),
        image=image
    )


@app.route('/export_over_10000/download')
def export_over_10000_download():
    try:
        df = pd.read_sql('export_over_10000', engine)
    except Exception:
        return jsonify({'error': 'export_over_10000 table not found'}), 404
    csv = df.to_csv(index=False)
    return Response(csv, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=export_over_10000.csv'})


# (e) Save renamed table (FIXED version)
@app.route('/saved_table')
def saved_table():
    exports_df = pd.read_sql("SELECT country, value FROM exports", engine)
    imports_df = pd.read_sql("SELECT country, value FROM imports", engine)

    exp_total = exports_df.groupby('country', as_index=False)['value'].sum()
    imp_total = imports_df.groupby('country', as_index=False)['value'].sum()

    df = pd.merge(exp_total, imp_total, on='country', how='outer', suffixes=('_Exports', '_Imports')).fillna(0)

    df.rename(columns={'country': 'Country', 'value_Exports': 'Exports', 'value_Imports': 'Imports'}, inplace=True)
    df[['Exports', 'Imports']] = (df[['Exports', 'Imports']] / 1e12).round(3)

    df.to_sql('saved_table', engine, if_exists='replace', index=False)

    df_top = df.sort_values('Exports', ascending=False).head(10)
    plt.figure(figsize=(8, 4))
    df_top.set_index('Country')['Exports'].plot(kind='bar', color='tab:green')
    plt.title('Top 10 Exports (Saved Table)')
    plt.tight_layout()
    plt.savefig('static/charts/saved_top_exports.png')
    plt.close()

    return render_template(
        'saved_table.html',
        title="(e) Saved Table (Renamed Columns)",
        table=df.sort_values('Exports', ascending=False).head(15).to_html(classes='table table-striped', index=False, justify='center'),
        image='charts/saved_top_exports.png'
    )


# (f) Melt the table from step (e) and list top 10 transactions
@app.route('/top_transactions')
def top_transactions():
    inspector = inspect(engine)

    if 'export_over_10000' in inspector.get_table_names():
        df = pd.read_sql('export_over_10000', engine)
    elif 'saved_table' in inspector.get_table_names():
        df = pd.read_sql('saved_table', engine)
    else:
        exports_df = pd.read_sql("SELECT country, value FROM exports", engine).groupby('country', as_index=False)['value'].sum().rename(columns={'country': 'Country', 'value': 'Exports'})
        imports_df = pd.read_sql("SELECT country, value FROM imports", engine).groupby('country', as_index=False)['value'].sum().rename(columns={'country': 'Country', 'value': 'Imports'})
        df = pd.merge(exports_df, imports_df, on='Country', how='outer').fillna(0)

    df_cols = {c: c for c in df.columns}
    if 'country' in df.columns and 'Country' not in df.columns:
        df = df.rename(columns={'country': 'Country'})
    if 'exports' in df.columns and 'Exports' not in df.columns:
        df = df.rename(columns={'exports': 'Exports'})
    if 'imports' in df.columns and 'Imports' not in df.columns:
        df = df.rename(columns={'imports': 'Imports'})

    for col in ('Exports', 'Imports'):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0

    melted = pd.melt(df, id_vars=['Country'], value_vars=['Exports', 'Imports'], var_name='Transaction', value_name='Value')
    top10 = melted.sort_values(by='Value', ascending=False).head(10).reset_index(drop=True)

    return render_template(
        'top_transactions.html',
        title="(f) Top 10 Transactions (Country / Transaction / Value)",
        table=top10.to_html(classes='table table-striped', index=False, justify='center')
    )


# (g) Common commodities
@app.route('/common_commodities')
def common_commodities():
    imports_df = pd.read_sql("SELECT * FROM imports", engine)
    exports_df = pd.read_sql("SELECT * FROM exports", engine)
    if 'commodity' not in imports_df.columns or 'commodity' not in exports_df.columns:
        return render_template('error.html', message="Commodity column missing in data!")

    common = set(imports_df['commodity']).intersection(set(exports_df['commodity']))
    df = pd.DataFrame(sorted(list(common)), columns=['Common Commodities'])

    return render_template(
        'common_commodities.html',
        title="(g) Commodities Both Imported & Exported",
        table=df.to_html(classes='table table-striped', index=False, justify='center')
    )


@app.route('/_health')
def _health():
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        info = {'tables': tables}
        for t in ('imports', 'exports', 'saved_table'):
            info[f'{t}_columns'] = [c['name'] for c in inspector.get_columns(t)] if t in tables else None
        return jsonify({'status': 'ok', 'db': info})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False)

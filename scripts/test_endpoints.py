import importlib
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
app_module = importlib.import_module('app')
app = app_module.app

def short(s, n=200):
    return s.replace('\n',' ')[:n]

endpoints = ['/', '/top_countries', '/top_commodities', '/trade_summary', '/export_over_10000', '/saved_table', '/top_transactions', '/common_commodities', '/_health']

with app.app_context():
    client = app.test_client()
    results = []
    for ep in endpoints:
        try:
            r = client.get(ep)
            text = r.get_data(as_text=True)
            results.append((ep, r.status_code, short(text)))
        except Exception as e:
            results.append((ep, 'EXCEPTION', str(e)))

    for ep, status, snippet in results:
        print(f"{ep} -> {status}\n{snippet}\n{'-'*60}")

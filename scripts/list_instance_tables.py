from sqlalchemy import create_engine, inspect
import os
inst_db = os.path.join('instance','trade_data.db')
print('instance db exists:', os.path.exists(inst_db))
engine = create_engine(f"sqlite:///{inst_db}")
print('tables (instance):', inspect(engine).get_table_names())
# show a sample row from imports/exports if present
from sqlalchemy import text
if os.path.exists(inst_db):
    conn = engine.connect()
    for t in ('imports','exports'):
        try:
            r = conn.execute(text(f"SELECT * FROM {t} LIMIT 1")).fetchall()
            print(t, 'sample rows:', r)
        except Exception as e:
            print(t, 'error:', e)
    conn.close()

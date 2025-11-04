from sqlalchemy import create_engine, inspect
engine = create_engine('sqlite:///trade_data.db')
insp = inspect(engine)
print('tables (sqlalchemy):', insp.get_table_names())

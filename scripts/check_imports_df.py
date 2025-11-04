import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('sqlite:///instance/trade_data.db')
df = pd.read_sql('SELECT * FROM imports', engine)
print('columns:', df.columns.tolist())
print(df.head(5))

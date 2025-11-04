import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
	sys.path.insert(0, project_root)

from app import app
from database_setup import populate_db

print('Calling populate_db with drop_first=True')
populate_db(app, drop_first=True)
print('populate_db finished')

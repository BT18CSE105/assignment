import sys, os, json
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import importlib
app_module = importlib.import_module('app')
with app_module.app.app_context():
    resp = app_module._health()
# resp is a Flask response (werkzeug.wrappers.Response) or tuple
try:
    data = resp.get_json()
except Exception:
    if isinstance(resp, tuple):
        body = resp[0]
        try:
            data = body.get_json()
        except Exception:
            data = str(body)
    else:
        data = str(resp)
print(json.dumps(data, indent=2))

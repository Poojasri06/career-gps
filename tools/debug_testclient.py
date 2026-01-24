import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from app_api import app
import json

client = TestClient(app)

dummy_career = {"role_name": "Software Engineer", "role_id": "se_dummy"}
resp = client.post("/simulate/learn", json={"skills": ["Python"], "career": dummy_career, "new_skills": ["Django"]})
print('Status:', resp.status_code)
try:
    print(json.dumps(resp.json(), indent=2))
except Exception:
    print(resp.text)

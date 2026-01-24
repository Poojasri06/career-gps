import requests, json
BASE='http://127.0.0.1:8000'
dummy_career={"role_name": "Software Engineer", "role_id": "se_dummy"}
try:
    r=requests.post(BASE + '/simulate/learn', json={"skills":["Python"], "career": dummy_career, "new_skills":["Django"]}, timeout=10)
    print('Status:', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
except Exception as e:
    print('Request failed:', e)

import urllib.request
import urllib.error
import json
import time

API_BASE = "http://127.0.0.1:8000"


def get_health():
    url = API_BASE + "/health"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode())


def post_readiness(skills):
    url = API_BASE + "/readiness"
    data = json.dumps({"skills": skills}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


if __name__ == '__main__':
    print('Checking API health...')
    for i in range(15):
        try:
            h = get_health()
            print('Health OK:', h)
            break
        except Exception as e:
            print(f'Health check failed (attempt {i+1}):', e)
            time.sleep(1)
    else:
        print('API did not become healthy; aborting smoke test.')
        raise SystemExit(1)

    print('\nPosting readiness request...')
    try:
        skills = ['Python', 'SQL', 'Git']
        res = post_readiness(skills)
        print('Readiness response keys:', list(res.keys()))
        rd = res.get('readiness') or res.get('readiness')
        if rd:
            print('Overall score:', rd.get('overall_score'))
            print('Interpretation:', rd.get('interpretation'))
            print('Explanation:', rd.get('explanation'))
        else:
            print('No readiness object returned; full response:')
            print(json.dumps(res, indent=2))
    except Exception as e:
        print('Readiness request failed:', e)
        raise

    print('\nSmoke test complete.')

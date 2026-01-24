import requests
import json

BASE = "http://127.0.0.1:8000"

scenarios = [
    {"skills": ["Python", "SQL"], "name": "basic_skills"},
    {"skills": ["React", "JavaScript", "CSS"], "name": "frontend"},
    {"skills": ["AWS", "Docker"], "name": "cloud"},
]


def post_readiness(skills):
    r = requests.post(BASE + "/readiness", json={"skills": skills}, timeout=10)
    return r.json()


def post_simulate(skills, career, new_skills):
    r = requests.post(BASE + "/simulate/learn", json={"skills": skills, "career": career, "new_skills": new_skills}, timeout=10)
    return r.json()


if __name__ == '__main__':
    print('Running API scenarios...')
    for s in scenarios:
        print('\n--- Scenario:', s['name'], '---')
        try:
            res = post_readiness(s['skills'])
            print('Readiness overall:', res['readiness']['overall_score'])
            print('Explanation:', res['readiness'].get('explanation'))
        except Exception as e:
            print('Readiness failed:', e)

    # Simulate learning a new skill for frontend scenario
    # Get a career by calling readiness and extracting career from gap_analysis if provided
    try:
        r = post_readiness(scenarios[1]['skills'])
        career = None
        if r.get('gap_analysis') and isinstance(r['gap_analysis'], dict) and r['gap_analysis'].get('career'):
            career = r['gap_analysis']['career']
    except Exception:
        career = None

    # If no career provided, use a match via the chat endpoint
    if not career:
        print('\nAttempting to call /chat to derive career context...')
        try:
            rc = requests.post(BASE + '/chat', json={"prompt": "What career fits Python, SQL?", "skills": scenarios[0]['skills']}, timeout=10)
            job = rc.json()
            if job.get('type') == 'readiness' and job.get('gap'):
                career = job['gap'].get('career')
        except Exception as e:
            print('Chat failed:', e)

    if career:
        print('\nSimulating adding "TypeScript" to frontend scenario')
        try:
            sim = post_simulate(scenarios[1]['skills'], career, ["TypeScript"])
            print('Sim result readiness:', sim['simulation']['readiness_score']['overall_score'])
            print('What-if summary:', sim['simulation'].get('what_if_summary'))
        except Exception as e:
            print('Simulate failed:', e)
    else:
        print('No career context found; skipping simulate test')

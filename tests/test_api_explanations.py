import pytest
from fastapi.testclient import TestClient
from app_api import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'


@pytest.mark.parametrize("skills", [["Python", "SQL"], ["React", "CSS"]])
def test_readiness_has_explanation(skills):
    r = client.post("/readiness", json={"skills": skills})
    assert r.status_code == 200
    body = r.json()
    assert 'readiness' in body
    readiness = body['readiness']
    assert 'overall_score' in readiness
    # explanation should be present and non-empty
    assert 'explanation' in readiness
    assert isinstance(readiness['explanation'], str)
    assert len(readiness['explanation'].strip()) > 0


def test_simulate_add_skills_produces_what_if():
    # Basic readiness to get a career
    r = client.post("/readiness", json={"skills": ["Python"]})
    assert r.status_code == 200
    body = r.json()

    # For the purpose of the test, call simulate with a dummy career structure
    dummy_career = {"role_name": "Software Engineer", "role_id": "se_dummy"}
    sim = client.post("/simulate/learn", json={"skills": ["Python"], "career": dummy_career, "new_skills": ["Django"]})
    assert sim.status_code == 200
    s = sim.json()
    assert 'simulation' in s
    sim_obj = s['simulation']
    assert 'readiness_score' in sim_obj
    # what_if_summary should exist
    assert 'what_if_summary' in sim_obj
    assert isinstance(sim_obj['what_if_summary'], str)
    assert len(sim_obj['what_if_summary'].strip()) > 0

import copy
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def restore_activities():
    """Restore the in-memory activities dict after each test to keep tests isolated."""
    orig = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(orig)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Some known activities from the initial dataset
    assert "Soccer Team" in data
    assert "Basketball Team" in data


def test_signup_and_unregister_flow():
    activity = "Soccer Team"
    email = f"test+{uuid4().hex}@mergington.edu"

    # Signup
    signup = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Unregister
    unregister = client.post(f"/activities/{activity}/unregister?email={email}")
    assert unregister.status_code == 200
    assert email not in app_module.activities[activity]["participants"]


def test_signup_duplicate():
    activity = "Soccer Team"
    existing = app_module.activities[activity]["participants"][0]
    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_nonexistent():
    activity = "Basketball Team"
    fake_email = f"noone+{uuid4().hex}@mergington.edu"
    resp = client.post(f"/activities/{activity}/unregister?email={fake_email}")
    assert resp.status_code == 400


def test_activity_not_found():
    fake_activity = "Nonexistent Club"
    email = f"test+{uuid4().hex}@mergington.edu"

    r1 = client.post(f"/activities/{fake_activity}/signup?email={email}")
    assert r1.status_code == 404

    r2 = client.post(f"/activities/{fake_activity}/unregister?email={email}")
    assert r2.status_code == 404

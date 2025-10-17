import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister():
    test_activity = "Chess Club"
    test_email = "pytestuser@mergington.edu"

    # Ensure not registered
    if test_email in activities[test_activity]["participants"]:
        client.post(f"/activities/{test_activity}/unregister?email={test_email}")

    # Signup
    signup = client.post(f"/activities/{test_activity}/signup?email={test_email}")
    print("Signup response text:", signup.text)
    assert signup.status_code == 200
    assert signup.json() is not None
    assert "message" in signup.json()
    assert signup.json()["message"].startswith("Signed up")
    assert test_email in activities[test_activity]["participants"]

    # Duplicate signup
    duplicate = client.post(f"/activities/{test_activity}/signup?email={test_email}")
    assert duplicate.status_code == 400
    assert "already signed up" in duplicate.json()["detail"]

    # Unregister
    unregister = client.post(f"/activities/{test_activity}/unregister?email={test_email}")
    assert unregister.status_code == 200
    assert unregister.json()["message"].startswith("Unregistered")
    assert test_email not in activities[test_activity]["participants"]

    # Unregister again (should fail)
    unregister_again = client.post(f"/activities/{test_activity}/unregister?email={test_email}")
    assert unregister_again.status_code == 400
    assert "not registered" in unregister_again.json()["detail"]


def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup?email=pytestuser@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_nonexistent_activity():
    response = client.post("/activities/Nonexistent/unregister?email=pytestuser@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

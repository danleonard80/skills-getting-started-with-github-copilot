import pytest
from fastapi.testclient import TestClient
import httpx
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_data():
    """Setup test data before each test"""
    # Store original activities
    original = activities.copy()
    yield
    # Restore original activities after test
    activities.clear()
    activities.update(original)

def test_root_redirect():
    """Test that the root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    # Test structure of an activity
    activity = next(iter(data.values()))
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity

def test_signup_for_activity():
    """Test signing up for an activity"""
    test_activity = "Chess Club"
    test_email = "test@mergington.edu"

    # First make sure the user is not registered
    activities_response = client.get("/activities")
    current_activities = activities_response.json()
    if test_email in current_activities[test_activity]["participants"]:
        client.post(f"/activities/{test_activity}/unregister?email={test_email}")

    # Test successful signup
    response = client.post(f"/activities/{test_activity}/signup?email={test_email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Registered {test_email} for {test_activity}"

    # Test duplicate signup
    response = client.post(f"/activities/{test_activity}/signup?email={test_email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already registered for this activity"

    # Test signing up for non-existent activity
    response = client.post(f"/activities/NonexistentClub/signup?email={test_email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

    # Cleanup - unregister the test user
    client.post(f"/activities/{test_activity}/unregister?email={test_email}")

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    test_activity = "Chess Club"
    test_email = "unregister_test@mergington.edu"

    # First make sure the user is not registered
    activities_response = client.get("/activities")
    current_activities = activities_response.json()
    if test_email in current_activities[test_activity]["participants"]:
        client.post(f"/activities/{test_activity}/unregister?email={test_email}")

    # Now register the test user
    signup_response = client.post(f"/activities/{test_activity}/signup?email={test_email}")
    assert signup_response.status_code == 200

    # Test successful unregistration
    response = client.post(f"/activities/{test_activity}/unregister?email={test_email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {test_email} from {test_activity}"

    # Verify participant is no longer in activity
    activities_response = client.get("/activities")
    updated_activities = activities_response.json()
    assert test_email not in updated_activities[test_activity]["participants"]

    # Test unregistering from non-existent activity
    response = client.post(f"/activities/NonexistentClub/unregister?email={test_email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

    # Test unregistering when not registered
    response = client.post(f"/activities/{test_activity}/unregister?email={test_email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"
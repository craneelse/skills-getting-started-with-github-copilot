"""
Tests for the High School Management System API
Using the AAA (Arrange-Act-Assert) pattern
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


# store original activities for resetting
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture

def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture

def client():
    return TestClient(app)


def test_get_activities_returns_initial_activities(client, reset_activities):
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_successfully_adds_participant(client, reset_activities):
    # Arrange
    # Act
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]


def test_signup_twice_returns_400_duplicate_error(client, reset_activities):
    email = "duplicate@mergington.edu"
    response1 = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response1.status_code == 200
    response2 = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response2.status_code == 400
    data = response2.json()
    assert "already signed up" in data["detail"]


def test_signup_to_nonexistent_activity_returns_404(client, reset_activities):
    response = client.post("/activities/Nonexistent Club/signup?email=student@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_remove_participant_successfully(client, reset_activities):
    email = "michael@mergington.edu"
    activities_response = client.get("/activities")
    assert email in activities_response.json()["Chess Club"]["participants"]
    response = client.delete(f"/activities/Chess Club/participants?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Removed {email} from Chess Club"
    activities_response = client.get("/activities")
    assert email not in activities_response.json()["Chess Club"]["participants"]


def test_remove_participant_not_signed_returns_404(client, reset_activities):
    response = client.delete("/activities/Chess Club/participants?email=nothere@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]


def test_remove_from_nonexistent_activity_returns_404(client, reset_activities):
    response = client.delete("/activities/Nonexistent Club/participants?email=student@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


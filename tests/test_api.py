"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities data before each test"""
    from src.app import activities

    # Clear all participants from activities
    for activity in activities.values():
        activity["participants"] = []


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        # The redirect response should serve the HTML file


class TestActivitiesEndpoint:
    """Test the activities endpoints"""

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

        # Check that each activity has the required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        activity_name = "Basketball Team"
        email = "test@mergington.edu"

        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistentActivity/signup",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_already_signed_up(self, client):
        """Test signup when student is already signed up"""
        activity_name = "Soccer Club"
        email = "test@mergington.edu"

        # First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Second signup should fail
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_unregister_successful(self, client):
        """Test successful unregister from an activity"""
        activity_name = "Art Club"
        email = "test@mergington.edu"

        # First sign up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Then unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/NonExistentActivity/unregister",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_not_signed_up(self, client):
        """Test unregister when student is not signed up"""
        activity_name = "Debate Team"
        email = "test@mergington.edu"

        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]
"""Tests for the activities endpoints."""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that GET /activities returns status code 200."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that GET /activities returns a dictionary."""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_known_activities(self, client, reset_activities):
        """Test that response contains expected activities."""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Swimming Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing {field} in {activity_name}"

    def test_get_activities_participants_is_list(self, client, reset_activities):
        """Test that participants field is a list."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"Participants for {activity_name} is not a list"


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_returns_200_on_success(self, client, reset_activities):
        """Test that signup returns 200 on successful signup."""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client, reset_activities):
        """Test that signup returns a success message."""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant."""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Basketball%20Team/signup?email={email}")
        
        activities = client.get("/activities").json()
        assert email in activities["Basketball Team"]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signup for nonexistent activity returns 404."""
        response = client.post(
            "/activities/NonExistent/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_returns_400(self, client, reset_activities):
        """Test that signing up twice returns 400."""
        email = "test@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Basketball%20Team/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/Basketball%20Team/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()

    def test_signup_full_activity_returns_400(self, client, reset_activities):
        """Test that signup to full activity returns 400."""
        # Fill up Basketball Team (max 15 participants)
        for i in range(15):
            email = f"student{i}@mergington.edu"
            client.post(f"/activities/Basketball%20Team/signup?email={email}")
        
        # Try to add one more
        response = client.post(
            "/activities/Basketball%20Team/signup?email=overflow@mergington.edu"
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_signup_with_existing_participants(self, client, reset_activities):
        """Test that signup works when activity already has participants."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newplayer@mergington.edu"
        )
        assert response.status_code == 200
        
        activities = client.get("/activities").json()
        assert "newplayer@mergington.edu" in activities["Chess Club"]["participants"]


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_returns_200_on_success(self, client, reset_activities):
        """Test that unregister returns 200 on successful unregister."""
        email = "michael@mergington.edu"
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self, client, reset_activities):
        """Test that unregister returns a success message."""
        email = "michael@mergington.edu"
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant."""
        email = "michael@mergington.edu"
        
        # Verify email is in the list
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        
        # Unregister
        client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        
        # Verify email is no longer in the list
        activities = client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that unregister from nonexistent activity returns 404."""
        response = client.delete(
            "/activities/NonExistent/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_not_registered_returns_400(self, client, reset_activities):
        """Test that unregistering non-participant returns 400."""
        response = client.delete(
            "/activities/Basketball%20Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that user can sign up again after unregistering."""
        email = "michael@mergington.edu"
        
        # Unregister
        response1 = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify they're registered
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]

    def test_unregister_with_multiple_participants(self, client, reset_activities):
        """Test that unregister only removes the specified participant."""
        chess_email = "michael@mergington.edu"
        prog_email = "emma@mergington.edu"
        
        # Both are in Chess Club and Programming Class
        activities = client.get("/activities").json()
        assert chess_email in activities["Chess Club"]["participants"]
        assert prog_email in activities["Programming Class"]["participants"]
        
        # Unregister chess_email from Chess Club
        client.delete(f"/activities/Chess%20Club/unregister?email={chess_email}")
        
        # Verify only chess_email is removed from Chess Club
        activities = client.get("/activities").json()
        assert chess_email not in activities["Chess Club"]["participants"]
        assert prog_email in activities["Programming Class"]["participants"]


class TestRoot:
    """Tests for the root endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "static/index.html" in response.headers["location"]

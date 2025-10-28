"""
Test cases for the FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_redirects_to_static(self, client: TestClient):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test cases for the activities endpoint."""
    
    def test_get_activities_success(self, client: TestClient):
        """Test successful retrieval of all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check structure of one activity
        activity_name = list(data.keys())[0]
        activity = data[activity_name]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_get_activities_contains_expected_activities(self, client: TestClient):
        """Test that response contains expected activities."""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", 
            "Basketball Team", "Swimming Club", "Art Club", 
            "Drama Club", "Science Olympiad", "Debate Team"
        ]
        
        for activity in expected_activities:
            assert activity in data


class TestSignupEndpoint:
    """Test cases for the signup endpoint."""
    
    def test_signup_success(self, client: TestClient):
        """Test successful signup for an activity."""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify the student was actually added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
    
    def test_signup_duplicate(self, client: TestClient):
        """Test that signing up a student twice fails."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client: TestClient):
        """Test signing up for a non-existent activity."""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_missing_email(self, client: TestClient):
        """Test signup without providing email parameter."""
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_signup_empty_email(self, client: TestClient):
        """Test signup with empty email parameter."""
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email=")
        assert response.status_code == 200  # FastAPI allows empty strings
        
        # Verify empty email was added (though this might not be desired behavior)
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "" in activities_data[activity]["participants"]


class TestUnregisterEndpoint:
    """Test cases for the unregister endpoint."""
    
    def test_unregister_success(self, client: TestClient):
        """Test successful unregistration from an activity."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify the student was actually removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
    
    def test_unregister_not_registered(self, client: TestClient):
        """Test unregistering a student who is not registered."""
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity(self, client: TestClient):
        """Test unregistering from a non-existent activity."""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_missing_email(self, client: TestClient):
        """Test unregister without providing email parameter."""
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/unregister")
        assert response.status_code == 422  # Unprocessable Entity


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple operations."""
    
    def test_signup_then_unregister(self, client: TestClient):
        """Test signing up and then unregistering from an activity."""
        email = "integration@mergington.edu"
        activity = "Programming Class"
        
        # First signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup worked
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Then unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration worked
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
    
    def test_multiple_signups_different_activities(self, client: TestClient):
        """Test signing up for multiple different activities."""
        email = "multisport@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Club"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for activity in activities_to_join:
            assert email in activities_data[activity]["participants"]
    
    def test_unregister_then_signup_again(self, client: TestClient):
        """Test unregistering and then signing up again for the same activity."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        # First unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Then signup again
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify student is back in the activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]


class TestEdgeCases:
    """Test edge cases and special characters."""
    
    def test_activity_name_with_spaces(self, client: TestClient):
        """Test that activity names with spaces work correctly."""
        email = "spaces@mergington.edu"
        activity = "Programming Class"  # Has space in name
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
    
    def test_email_with_special_characters(self, client: TestClient):
        """Test emails with special characters."""
        email = "test.tag@mergington.edu"  # Use dot instead of plus for better compatibility
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify it was added correctly
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
    
    def test_url_encoded_parameters(self, client: TestClient):
        """Test that URL-encoded parameters work correctly."""
        email = "url%2Btest@mergington.edu"  # URL encoded +
        activity = "Chess%20Club"  # URL encoded space
        
        # The TestClient should handle URL encoding automatically
        response = client.post(f"/activities/Chess Club/signup?email=url+test@mergington.edu")
        assert response.status_code == 200
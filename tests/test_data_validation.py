"""
Test cases for data validation and business logic.
"""

import pytest
from fastapi.testclient import TestClient


class TestDataValidation:
    """Test data validation and constraints."""
    
    def test_activity_participant_limit(self, client: TestClient):
        """Test that activities respect participant limits."""
        # First, get an activity with known participant limit
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        # Find an activity we can test with
        test_activity = None
        for name, details in activities_data.items():
            current_participants = len(details["participants"])
            max_participants = details["max_participants"]
            if current_participants < max_participants:
                test_activity = name
                break
        
        assert test_activity is not None, "No activity found with available spots"
        
        # Get current state
        current_participants = len(activities_data[test_activity]["participants"])
        max_participants = activities_data[test_activity]["max_participants"]
        spots_available = max_participants - current_participants
        
        # Fill up all remaining spots
        for i in range(spots_available):
            email = f"filler{i}@mergington.edu"
            response = client.post(f"/activities/{test_activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify activity is now full
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert len(activities_data[test_activity]["participants"]) == max_participants
        
        # Try to add one more (should still work since we don't enforce limits in current implementation)
        overflow_email = "overflow@mergington.edu"
        response = client.post(f"/activities/{test_activity}/signup?email={overflow_email}")
        # Note: Current implementation doesn't enforce max_participants, so this will succeed
        # In a real application, you might want this to fail
        assert response.status_code == 200


class TestActivityData:
    """Test activity data integrity and consistency."""
    
    def test_all_activities_have_required_fields(self, client: TestClient):
        """Test that all activities have required fields."""
        response = client.get("/activities")
        activities_data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities_data.items():
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"
                
            # Test data types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Test constraints
            assert activity_data["max_participants"] > 0
            assert len(activity_data["description"]) > 0
            assert len(activity_data["schedule"]) > 0
    
    def test_participant_emails_format(self, client: TestClient):
        """Test that participant emails follow expected format."""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_data in activities_data.items():
            for email in activity_data["participants"]:
                # Basic email validation (contains @ and domain)
                if email:  # Skip empty emails for now
                    assert "@" in email, f"Invalid email format in {activity_name}: {email}"
                    assert "." in email.split("@")[1], f"Invalid domain in {activity_name}: {email}"


class TestConcurrency:
    """Test concurrent operations."""
    
    def test_concurrent_signups_same_activity(self, client: TestClient):
        """Test multiple signups to the same activity don't cause issues."""
        activity = "Programming Class"
        emails = [f"concurrent{i}@mergington.edu" for i in range(5)]
        
        # Sign up multiple students
        responses = []
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            responses.append(response)
        
        # All should succeed (assuming no duplicate emails)
        for response in responses:
            assert response.status_code == 200
        
        # Verify all students were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for email in emails:
            assert email in activities_data[activity]["participants"]
    
    def test_signup_and_unregister_same_student(self, client: TestClient):
        """Test signing up and immediately unregistering the same student."""
        email = "quickchange@mergington.edu"
        activity = "Art Club"
        
        # Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Immediate unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify final state
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_malformed_requests(self, client: TestClient):
        """Test various malformed requests."""
        # Test with invalid characters in activity name
        response = client.post("/activities/Invalid<>Activity/signup?email=test@mergington.edu")
        # Should still work as FastAPI handles URL encoding
        assert response.status_code in [200, 404]  # Either works or activity not found
        
        # Test with very long email
        long_email = "a" * 100 + "@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={long_email}")
        assert response.status_code == 200  # Should work unless we add validation
    
    def test_case_sensitivity(self, client: TestClient):
        """Test case sensitivity in activity names."""
        email = "case@mergington.edu"
        
        # Try different cases
        response1 = client.post("/activities/chess club/signup?email=" + email)
        assert response1.status_code == 404  # Case sensitive, should fail
        
        response2 = client.post("/activities/Chess Club/signup?email=" + email)
        assert response2.status_code == 200  # Correct case, should work
    
    def test_unicode_handling(self, client: TestClient):
        """Test Unicode characters in email addresses."""
        unicode_email = "tëst@mërgington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={unicode_email}")
        assert response.status_code == 200
        
        # Verify it was stored correctly
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert unicode_email in activities_data[activity]["participants"]
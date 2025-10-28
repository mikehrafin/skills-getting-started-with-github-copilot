"""
Performance and load testing for the FastAPI application.
"""

import pytest
import time
from fastapi.testclient import TestClient


class TestPerformance:
    """Basic performance tests."""
    
    def test_get_activities_response_time(self, client: TestClient):
        """Test that getting activities is reasonably fast."""
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0, f"Response took {response_time:.3f}s, should be under 1s"
    
    def test_signup_response_time(self, client: TestClient):
        """Test that signup operations are reasonably fast."""
        email = "performance@mergington.edu"
        activity = "Chess Club"
        
        start_time = time.time()
        response = client.post(f"/activities/{activity}/signup?email={email}")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0, f"Signup took {response_time:.3f}s, should be under 1s"
    
    def test_multiple_rapid_requests(self, client: TestClient):
        """Test handling multiple rapid requests."""
        responses = []
        start_time = time.time()
        
        # Make 10 rapid requests
        for i in range(10):
            response = client.get("/activities")
            responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Average response time should be reasonable
        avg_time = total_time / 10
        assert avg_time < 0.5, f"Average response time {avg_time:.3f}s too slow"


class TestLoad:
    """Load testing with multiple operations."""
    
    def test_bulk_signups(self, client: TestClient):
        """Test signing up many students at once."""
        activity = "Programming Class"
        num_signups = 20
        
        start_time = time.time()
        
        for i in range(num_signups):
            email = f"bulk{i}@mergington.edu"
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete in reasonable time
        assert total_time < 10.0, f"Bulk signups took {total_time:.3f}s, too slow"
        
        # Verify all students were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for i in range(num_signups):
            email = f"bulk{i}@mergington.edu"
            assert email in activities_data[activity]["participants"]
    
    def test_bulk_unregistrations(self, client: TestClient):
        """Test unregistering many students at once."""
        activity = "Swimming Club"
        num_students = 15
        
        # First, sign up the students
        for i in range(num_students):
            email = f"bulkremove{i}@mergington.edu"
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Then unregister them all
        start_time = time.time()
        
        for i in range(num_students):
            email = f"bulkremove{i}@mergington.edu"
            response = client.delete(f"/activities/{activity}/unregister?email={email}")
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete in reasonable time
        assert total_time < 10.0, f"Bulk unregistrations took {total_time:.3f}s, too slow"
        
        # Verify all students were removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for i in range(num_students):
            email = f"bulkremove{i}@mergington.edu"
            assert email not in activities_data[activity]["participants"]


class TestMemoryUsage:
    """Basic memory usage testing."""
    
    def test_large_participant_lists(self, client: TestClient):
        """Test handling activities with large participant lists."""
        activity = "Drama Club"
        num_participants = 100
        
        # Add many participants
        for i in range(num_participants):
            email = f"memory{i}@mergington.edu"
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Getting activities should still work efficiently
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 2.0, f"Large data response took {response_time:.3f}s"
        
        # Verify data integrity
        data = response.json()
        assert len(data[activity]["participants"]) >= num_participants
    
    def test_repeated_operations_memory_stability(self, client: TestClient):
        """Test that repeated operations don't cause memory issues."""
        activity = "Science Olympiad"
        email = "memory_test@mergington.edu"
        
        # Perform many signup/unregister cycles
        for cycle in range(20):
            # Signup
            signup_response = client.post(f"/activities/{activity}/signup?email={email}")
            assert signup_response.status_code == 200
            
            # Unregister
            unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
            assert unregister_response.status_code == 200
        
        # Final state should be clean
        final_response = client.get("/activities")
        final_data = final_response.json()
        assert email not in final_data[activity]["participants"]
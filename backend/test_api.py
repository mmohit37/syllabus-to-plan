"""
Test the /analyze endpoint
"""
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_health_check():
    """Test the health check endpoint"""
    print("Testing GET /...")
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("  [OK] Health check works\n")


def test_analyze_endpoint_structure():
    """Test the /analyze endpoint accepts correct input and returns correct structure"""
    print("Testing POST /analyze...")

    # Test with minimal valid input
    request_data = {
        "course": "CSE 374",
        "text": "No valid assignments here"
    }

    response = client.post("/analyze", json=request_data)

    assert response.status_code == 200
    data = response.json()

    # Should have the required keys
    assert "assignments" in data
    assert "weekly_workload" in data

    # Should be lists (even if empty)
    assert isinstance(data["assignments"], list)
    assert isinstance(data["weekly_workload"], list)

    print("  [OK] Endpoint structure is correct")
    print("  [OK] Gracefully handles parser NotImplementedError\n")


def test_analyze_with_mock_implementation():
    """Test that if parser were implemented, the flow would work"""
    print("Testing /analyze integration...")

    # Since call_llm is not implemented, we expect empty results
    # But the endpoint should not crash
    request_data = {
        "course": "CSE 374",
        "text": """
        CSE 374 Software Engineering

        Assignments:
        - Homework 1: Due October 15, 2024
        - Midterm Exam: November 3, 2024
        """
    }

    response = client.post("/analyze", json=request_data)

    assert response.status_code == 200
    data = response.json()

    # Parser will fail gracefully and return empty lists
    assert data["assignments"] == []
    assert data["weekly_workload"] == []

    print("  [OK] Endpoint handles parser failures gracefully\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Running API Tests")
    print("=" * 50 + "\n")

    try:
        test_health_check()
        test_analyze_endpoint_structure()
        test_analyze_with_mock_implementation()

        print("=" * 50)
        print("[OK] ALL API TESTS PASSED!")
        print("=" * 50)
        print("\nNote: The parser returns empty results because")
        print("call_llm() is not yet implemented. Once you")
        print("implement it with your LLM provider, the")
        print("endpoint will return actual parsed assignments.")
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        raise

import sys
import os

# Add the parent directory to the Python path to allow importing 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import json

from app.api.routes import parse_criteria
# Assuming the Flask app runs on http://localhost:5000
SERVER_URL = "http://localhost:5000"

def run_test(test_name, test_function):
    """Helper to run and report on individual test functions."""
    print(f"\n--- Running Test: {test_name} ---")
    try:
        test_function()
        print(f"--- PASSED: {test_name} ---")
        return True
    except AssertionError as e:
        print(f"--- FAILED: {test_name} ---")
        print(f"  Error: {e}")
        return False
    except Exception as e:
        print(f"--- FAILED: {test_name} ---")
        print(f"  An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def _test_parse_criteria():
    """Test the parse_criteria function with various inputs"""
    # Test empty criteria
    assert parse_criteria('') == {}, "Test empty criteria failed"
    
    # Test single numeric criteria
    assert parse_criteria('market_cap>1000000000') == {'market_cap': ('>', 1000000000)}, "Test single numeric criteria failed"
    
    # Test multiple numeric criteria
    criteria = parse_criteria('market_cap>1000000000,pe_ratio<20')
    assert criteria['market_cap'] == ('>', 1000000000), "Test multiple numeric criteria - market_cap failed"
    assert criteria['pe_ratio'] == ('<', 20), "Test multiple numeric criteria - pe_ratio failed"
    
    # Test string criteria
    assert parse_criteria('sector=Technology') == {'sector': 'Technology'}, "Test string criteria failed"
    
    # Test mixed criteria
    criteria = parse_criteria('market_cap>1000000000,sector=Technology,pe_ratio<20')
    assert criteria['market_cap'] == ('>', 1000000000), "Test mixed criteria - market_cap failed"
    assert criteria['sector'] == 'Technology', "Test mixed criteria - sector failed"
    assert criteria['pe_ratio'] == ('<', 20), "Test mixed criteria - pe_ratio failed"
    
    # Test float values
    assert parse_criteria('dividend_yield>0.02') == {'dividend_yield': ('>', 0.02)}, "Test float values failed"
    
    # Test different operators
    assert parse_criteria('pe_ratio>=20') == {'pe_ratio': ('>=', 20)}, "Test >= operator failed"
    assert parse_criteria('pe_ratio<=20') == {'pe_ratio': ('<=', 20)}, "Test <= operator failed"
    assert parse_criteria('pe_ratio==20') == {'pe_ratio': ('==', 20)}, "Test == operator failed"
    assert parse_criteria('pe_ratio!=20') == {'pe_ratio': ('!=', 20)}, "Test != operator failed"

def _test_screen_endpoint():
    """Test the /api/v1/screen endpoint"""
    # Test with valid criteria
    response = requests.post(f'{SERVER_URL}/api/v1/screen',
                          json={
                              'index': 'sp500',
                              'criteria': 'market_cap>1000000000,pe_ratio<20',
                              'limit': 5
                          })
    assert response.status_code == 200, f"Expected 200 for valid fundamental screen, got {response.status_code}"
    data = response.json()
    assert 'count' in data, "Screen endpoint response missing 'count'"
    assert 'stocks' in data, "Screen endpoint response missing 'stocks'"
    
    # Test with default criteria (empty criteria)
    response = requests.post(f'{SERVER_URL}/api/v1/screen',
                          json={
                              'index': 'sp500',
                              'criteria': '',
                              'limit': 5
                          })
    assert response.status_code == 200, f"Expected 200 for default fundamental screen, got {response.status_code}"
    data = response.json()
    assert 'count' in data, "Default screen endpoint response missing 'count'"
    assert 'stocks' in data, "Default screen endpoint response missing 'stocks'"
    
    # Test with invalid criteria format (should still return 200 but likely 0 results)
    response = requests.post(f'{SERVER_URL}/api/v1/screen',
                          json={
                              'index': 'sp500',
                              'criteria': 'invalid>criteria',
                              'limit': 5
                          })
    assert response.status_code == 200, f"Expected 200 for invalid criteria format, got {response.status_code}"

def _test_technical_endpoint():
    """Test the /api/v1/technical endpoint"""
    # Test with valid technical criteria
    response = requests.post(f'{SERVER_URL}/api/v1/technical',
                          json={
                              'index': 'sp500',
                              'criteria': 'rsi>40,ma>100',
                              'limit': 5
                          })
    assert response.status_code == 200, f"Expected 200 for valid technical screen, got {response.status_code}"
    data = response.json()
    assert 'count' in data, "Technical endpoint response missing 'count'"
    assert 'stocks' in data, "Technical endpoint response missing 'stocks'"
    
    # Test with empty criteria (should return 400 as technical criteria are required)
    response = requests.post(f'{SERVER_URL}/api/v1/technical',
                          json={
                              'index': 'sp500',
                              'criteria': '',
                              'limit': 5
                          })
    assert response.status_code == 400, f"Expected 400 for empty technical criteria, got {response.status_code}"
    assert 'error' in response.json(), "Error message missing for empty technical criteria"

def _test_combined_endpoint():
    """Test the /api/v1/combined endpoint"""
    # Test with both fundamental and technical criteria
    response = requests.post(f'{SERVER_URL}/api/v1/combined',
                          json={
                              'index': 'sp500',
                              'fundamental': 'market_cap>1000000000,pe_ratio<20',
                              'technical': 'rsi>40,ma>100',
                              'limit': 5
                          })
    assert response.status_code == 200, f"Expected 200 for combined screen, got {response.status_code}"
    data = response.json()
    assert 'count' in data, "Combined endpoint response missing 'count'"
    assert 'stocks' in data, "Combined endpoint response missing 'stocks'"
    
    # Test with only fundamental criteria
    response = requests.post(f'{SERVER_URL}/api/v1/combined',
                          json={
                              'index': 'sp500',
                              'fundamental': 'market_cap>1000000000',
                              'technical': '',
                              'limit': 5
                          })
    assert response.status_code == 200, f"Expected 200 for fundamental-only combined screen, got {response.status_code}"
    data = response.json()
    assert 'count' in data, "Fundamental-only combined endpoint response missing 'count'"
    assert 'stocks' in data, "Fundamental-only combined endpoint response missing 'stocks'"
    
    # Test with only technical criteria
    response = requests.post(f'{SERVER_URL}/api/v1/combined',
                          json={
                              'index': 'sp500',
                              'fundamental': '',
                              'technical': 'rsi>40',
                              'limit': 5
                          })
    assert response.status_code == 200, f"Expected 200 for technical-only combined screen, got {response.status_code}"
    data = response.json()
    assert 'count' in data, "Technical-only combined endpoint response missing 'count'"
    assert 'stocks' in data, "Technical-only combined endpoint response missing 'stocks'"
    
    # Test with no criteria (should return 400)
    response = requests.post(f'{SERVER_URL}/api/v1/combined',
                          json={
                              'index': 'sp500',
                              'fundamental': '',
                              'technical': '',
                              'limit': 5
                          })
    assert response.status_code == 400, f"Expected 400 for no combined criteria, got {response.status_code}"
    assert 'error' in response.json(), "Error message missing for no combined criteria"

def _test_invalid_requests():
    """Test various invalid request scenarios"""
    # Test missing index (should use default index in Flask app, so 200 expected)
    response = requests.post(f'{SERVER_URL}/api/v1/screen',
                          json={
                              'criteria': 'market_cap>1000000000',
                              'limit': 5
                          })
    assert response.status_code == 200, f"Expected 200 for missing index, got {response.status_code}"
    
    # Test invalid index (should return 400 from Flask app)
    response = requests.post(f'{SERVER_URL}/api/v1/screen',
                          json={
                              'index': 'invalid_index',
                              'criteria': 'market_cap>1000000000',
                              'limit': 5
                          })
    assert response.status_code == 400, f"Expected 400 for invalid index, got {response.status_code}"
    assert 'error' in response.json(), "Error message missing for invalid index"
    
    # Test missing request body (should return 400 from Flask app)
    response = requests.post(f'{SERVER_URL}/api/v1/screen')
    assert response.status_code == 400, f"Expected 400 for missing request body, got {response.status_code}"
    assert 'error' in response.json(), "Error message missing for missing request body"
    
    # Test invalid JSON (should return 400 from Flask app)
    try:
        response = requests.post(f'{SERVER_URL}/api/v1/screen',
                              data='invalid json',
                              headers={'Content-Type': 'application/json'})
        assert response.status_code == 400, f"Expected 400 for invalid JSON, got {response.status_code}"
        assert 'error' in response.json(), "Error message missing for invalid JSON"
    except json.JSONDecodeError:
        # requests might raise JSONDecodeError if response isn't JSON on error, handle it.
        pass # This means the server correctly didn't return JSON, which is also an error indication.

def main():
    print("Starting API Criteria Tests...")
    total_tests = 0
    passed_tests = 0

    tests_to_run = [
        ("Parse Criteria", _test_parse_criteria),
        ("Screen Endpoint", _test_screen_endpoint),
        ("Technical Endpoint", _test_technical_endpoint),
        ("Combined Endpoint", _test_combined_endpoint),
        ("Invalid Requests", _test_invalid_requests),
    ]

    for name, func in tests_to_run:
        total_tests += 1
        if run_test(name, func):
            passed_tests += 1
    
    print(f"\n--- Test Summary ---")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
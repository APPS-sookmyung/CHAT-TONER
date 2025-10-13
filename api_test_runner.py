
import requests
import json

BASE_URL = "https://chattoner-back-3yj2y7svbq-du.a.run.app"
USER_ID = "test-user-gemini-123"
TENANT_ID = "test-tenant-gemini-456"

def run_test(test_case_id, description, method, endpoint, expected_status, json_body=None):
    """Generic function to run a test case."""
    print(f"--- Running {test_case_id}: {description} ---")
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == 'POST':
            response = requests.post(url, json=json_body, timeout=30)
        else:
            print(f"Unsupported method: {method}")
            return

        print(f"Status Code: {response.status_code} (Expected: {expected_status})")
        
        if response.status_code == expected_status:
            print(f"PASSED: {test_case_id}")
        else:
            print(f"FAILED: {test_case_id}")
            try:
                print("Response Body:", response.json())
            except json.JSONDecodeError:
                print("Response Body:", response.text)
        
        print("\n")

    except requests.exceptions.RequestException as e:
        print(f"FAILED: {test_case_id} with exception: {e}")
        print("\n")

if __name__ == "__main__":
    # --- Onboarding Survey Tests ---
    
    # TC-004: Valid survey submission
    valid_survey_answers = {
        "primary_function": "engineering",
        "communication_style": "formal",
        "team_size": "1-10",
        "primary_channel": "chat",
        "primary_audience": ["peers_internal", "cross_team"]
    }
    run_test("TC-004", "Valid onboarding survey submission", "POST", "/api/v1/surveys/onboarding-intake/responses", 200, 
             json_body={"tenant_id": TENANT_ID, "user_id": USER_ID, "answers": valid_survey_answers})

    # TC-005: Incomplete survey submission (Note: server might not validate required questions at this level)
    incomplete_survey_answers = {
        "primary_function": "sales",
        "communication_style": "casual"
    }
    # The test case expects 400, but the endpoint might not validate this. Let's check for non-500.
    # Based on the code, it passes this to a pipeline, so it might return 200 but have different internal results.
    # We will stick to the user's expectation for the test.
    run_test("TC-005", "Incomplete onboarding survey", "POST", "/api/v1/surveys/onboarding-intake/responses", 400, 
             json_body={"tenant_id": TENANT_ID, "user_id": USER_ID, "answers": incomplete_survey_answers})

    # TC-006: Malformed survey submission (answers is not a dict)
    run_test("TC-006", "Malformed survey (answers is a list)", "POST", "/api/v1/surveys/onboarding-intake/responses", 422, 
             json_body={"tenant_id": TENANT_ID, "user_id": USER_ID, "answers": ["wrong", "format"]})

    # --- Personal Profile Tests ---

    # TC-009: Valid profile save
    valid_profile = {
        "userId": USER_ID,
        "baseFormalityLevel": 5,
        "baseFriendlinessLevel": 5,
        "baseEmotionLevel": 5,
        "baseDirectnessLevel": 5
    }
    run_test("TC-009", "Save valid personal profile", "POST", "/api/v1/profile", 200, json_body=valid_profile)

    # TC-010: Out-of-range profile save
    invalid_profile = {
        "userId": USER_ID,
        "baseFormalityLevel": 11, # Out of range
        "baseFriendlinessLevel": 5,
        "baseEmotionLevel": 5,
        "baseDirectnessLevel": 5
    }
    run_test("TC-010", "Save profile with out-of-range level", "POST", "/api/v1/profile", 422, json_body=invalid_profile)


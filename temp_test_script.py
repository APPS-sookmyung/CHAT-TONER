import httpx
import json

url = "http://127.0.0.1:5005/api/v1/conversion/convert"
payload = {
    "text": "회의 자료 검토 부탁드립니다",
    "user_profile": {
        "baseFormalityLevel": 3,
        "baseFriendlinessLevel": 4,
        "baseEmotionLevel": 2,
        "baseDirectnessLevel": 3
    },
    "context": "business",
    "negative_preferences": {
        "avoidFloweryLanguage": "strict",
        "avoidSlang": True
    }
}

try:
    with httpx.Client() as client:
        response = client.post(url, json=payload)
        print(response.status_code)
        print(response.text)
except httpx.ConnectError as e:
    print(f"Connection error: {e}")
    print("Is the python_backend server running on port 5001?")